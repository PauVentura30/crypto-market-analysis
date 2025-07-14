"""
Correlations API routes - endpoints for correlation analysis
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
import structlog
import numpy as np

from models.asset import AssetResponse, TimeframeEnum
from services.data_collector import DataCollector, get_asset_type_from_symbol
from services.analyzer import CorrelationAnalyzer
from core.config import get_settings

logger = structlog.get_logger()
router = APIRouter()


class CorrelationRequest(BaseModel):
    """Request model for correlation analysis"""
    symbols: List[str] = Field(..., min_items=2, max_items=20, description="Asset symbols for correlation analysis")
    timeframe: TimeframeEnum = Field(default=TimeframeEnum.THIRTY_DAYS, description="Analysis timeframe")
    correlation_window: Optional[int] = Field(default=30, ge=10, le=100, description="Rolling correlation window")


class PairwiseCorrelationRequest(BaseModel):
    """Request for pairwise correlation analysis"""
    symbol1: str = Field(..., description="First asset symbol")
    symbol2: str = Field(..., description="Second asset symbol")
    timeframe: TimeframeEnum = Field(default=TimeframeEnum.THIRTY_DAYS)
    include_rolling: bool = Field(default=True, description="Include rolling correlation analysis")


@router.post(
    "/matrix",
    response_model=AssetResponse,
    summary="Correlation Matrix",
    description="Calculate correlation matrix for multiple assets"
)
async def calculate_correlation_matrix(request: CorrelationRequest):
    """Calculate correlation matrix for multiple assets"""
    try:
        symbols = [s.upper() for s in request.symbols]
        asset_types = {symbol: get_asset_type_from_symbol(symbol) for symbol in symbols}
        
        async with DataCollector() as collector:
            # Get historical data for all symbols
            price_data = {}
            historical_data = {}
            
            for symbol in symbols:
                asset_type = asset_types[symbol]
                hist_data = await collector.get_historical_data(symbol, asset_type, request.timeframe)
                
                if hist_data and hist_data.data:
                    prices = [float(point.close) for point in hist_data.data]
                    price_data[symbol] = prices
                    historical_data[symbol] = hist_data
            
            if len(price_data) < 2:
                raise HTTPException(
                    status_code=404,
                    detail="Insufficient data for correlation analysis. Need at least 2 assets with historical data."
                )
            
            # Calculate correlation matrix
            analyzer = CorrelationAnalyzer()
            correlation_result = analyzer.calculate_correlation_matrix(price_data)
            
            if not correlation_result:
                raise HTTPException(
                    status_code=400,
                    detail="Unable to calculate correlation matrix"
                )
            
            # Add metadata
            correlation_result["metadata"] = {
                "timeframe": request.timeframe.value,
                "symbols": symbols,
                "data_points": {symbol: len(prices) for symbol, prices in price_data.items()},
                "analysis_period": {
                    "start": min(hist_data.start_date for hist_data in historical_data.values()).isoformat(),
                    "end": max(hist_data.end_date for hist_data in historical_data.values()).isoformat()
                }
            }
            
            return AssetResponse(
                data=correlation_result,
                message=f"Correlation matrix calculated for {len(symbols)} assets"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating correlation matrix: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/pairwise",
    response_model=AssetResponse,
    summary="Pairwise Correlation",
    description="Detailed correlation analysis between two specific assets"
)
async def pairwise_correlation(request: PairwiseCorrelationRequest):
    """Calculate detailed correlation between two assets"""
    try:
        symbol1 = request.symbol1.upper()
        symbol2 = request.symbol2.upper()
        
        if symbol1 == symbol2:
            raise HTTPException(
                status_code=400,
                detail="Cannot calculate correlation between the same asset"
            )
        
        asset_type1 = get_asset_type_from_symbol(symbol1)
        asset_type2 = get_asset_type_from_symbol(symbol2)
        
        async with DataCollector() as collector:
            # Get historical data for both assets
            hist_data1 = await collector.get_historical_data(symbol1, asset_type1, request.timeframe)
            hist_data2 = await collector.get_historical_data(symbol2, asset_type2, request.timeframe)
            
            if not hist_data1 or not hist_data1.data:
                raise HTTPException(
                    status_code=404,
                    detail=f"Historical data not found for {symbol1}"
                )
            
            if not hist_data2 or not hist_data2.data:
                raise HTTPException(
                    status_code=404,
                    detail=f"Historical data not found for {symbol2}"
                )
            
            # Extract price data
            prices1 = [float(point.close) for point in hist_data1.data]
            prices2 = [float(point.close) for point in hist_data2.data]
            
            # Ensure both series have the same length
            min_length = min(len(prices1), len(prices2))
            prices1 = prices1[:min_length]
            prices2 = prices2[:min_length]
            
            if min_length < 10:
                raise HTTPException(
                    status_code=400,
                    detail="Insufficient overlapping data points for correlation analysis"
                )
            
            analyzer = CorrelationAnalyzer()
            
            # Calculate static correlation
            import pandas as pd
            df = pd.DataFrame({'asset1': prices1, 'asset2': prices2})
            returns_df = df.pct_change().dropna()
            static_correlation = returns_df['asset1'].corr(returns_df['asset2'])
            
            # Calculate rolling correlation if requested
            rolling_correlation = []
            if request.include_rolling:
                rolling_correlation = analyzer.calculate_rolling_correlation(prices1, prices2, window=30)
            
            # Analyze correlation stability
            stability_analysis = analyzer.analyze_correlation_stability(prices1, prices2)
            
            # Determine correlation strength and interpretation
            abs_corr = abs(static_correlation)
            if abs_corr >= 0.8:
                strength = "very_strong"
            elif abs_corr >= 0.6:
                strength = "strong"
            elif abs_corr >= 0.4:
                strength = "moderate"
            elif abs_corr >= 0.2:
                strength = "weak"
            else:
                strength = "very_weak"
            
            direction = "positive" if static_correlation > 0 else "negative" if static_correlation < 0 else "neutral"
            
            result = {
                "symbol1": symbol1,
                "symbol2": symbol2,
                "static_correlation": static_correlation,
                "correlation_strength": strength,
                "correlation_direction": direction,
                "rolling_correlation": rolling_correlation,
                "stability_analysis": stability_analysis,
                "interpretation": {
                    "relationship": f"{strength} {direction} correlation",
                    "explanation": get_correlation_explanation(static_correlation),
                    "investment_implication": get_investment_implication(static_correlation)
                },
                "statistics": {
                    "data_points": min_length,
                    "rolling_correlation_std": np.std(rolling_correlation) if rolling_correlation else None,
                    "rolling_correlation_mean": np.mean(rolling_correlation) if rolling_correlation else None
                }
            }
            
            return AssetResponse(
                data=result,
                message=f"Pairwise correlation analysis for {symbol1} and {symbol2}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in pairwise correlation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/heatmap",
    response_model=AssetResponse,
    summary="Correlation Heatmap Data",
    description="Get correlation data formatted for heatmap visualization"
)
async def correlation_heatmap(
    symbols: List[str] = Query(..., description="Asset symbols for heatmap"),
    timeframe: TimeframeEnum = Query(default=TimeframeEnum.THIRTY_DAYS, description="Analysis timeframe")
):
    """Get correlation data formatted for heatmap visualization"""
    try:
        if len(symbols) > 15:
            raise HTTPException(
                status_code=400,
                detail="Maximum 15 symbols allowed for heatmap"
            )
        
        symbols = [s.upper() for s in symbols]
        asset_types = {symbol: get_asset_type_from_symbol(symbol) for symbol in symbols}
        
        async with DataCollector() as collector:
            price_data = {}
            
            for symbol in symbols:
                asset_type = asset_types[symbol]
                hist_data = await collector.get_historical_data(symbol, asset_type, timeframe)
                
                if hist_data and hist_data.data:
                    prices = [float(point.close) for point in hist_data.data]
                    price_data[symbol] = prices
            
            if len(price_data) < 2:
                raise HTTPException(
                    status_code=404,
                    detail="Insufficient data for heatmap generation"
                )
            
            analyzer = CorrelationAnalyzer()
            correlation_result = analyzer.calculate_correlation_matrix(price_data)
            
            # Format for heatmap
            heatmap_data = []
            correlation_matrix = correlation_result.get("correlation_matrix", {})
            
            for i, symbol1 in enumerate(symbols):
                if symbol1 in correlation_matrix:
                    row_data = []
                    for j, symbol2 in enumerate(symbols):
                        if symbol2 in correlation_matrix[symbol1]:
                            correlation_value = correlation_matrix[symbol1][symbol2]
                            row_data.append({
                                "x": j,
                                "y": i,
                                "value": correlation_value,
                                "symbol1": symbol1,
                                "symbol2": symbol2
                            })
                    heatmap_data.extend(row_data)
            
            return AssetResponse(
                data={
                    "heatmap_data": heatmap_data,
                    "symbols": symbols,
                    "correlation_matrix": correlation_matrix,
                    "color_scale": {
                        "min": -1,
                        "max": 1,
                        "center": 0,
                        "colors": ["#d32f2f", "#ffffff", "#388e3c"]  # Red, White, Green
                    }
                },
                message=f"Heatmap data for {len(symbols)} assets"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating heatmap data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/rolling/{symbol1}/{symbol2}",
    response_model=AssetResponse,
    summary="Rolling Correlation",
    description="Get rolling correlation between two assets over time"
)
async def rolling_correlation(
    symbol1: str,
    symbol2: str,
    timeframe: TimeframeEnum = Query(default=TimeframeEnum.NINETY_DAYS),
    window: int = Query(default=30, ge=10, le=60, description="Rolling window size")
):
    """Get rolling correlation between two assets"""
    try:
        symbol1 = symbol1.upper()
        symbol2 = symbol2.upper()
        
        if symbol1 == symbol2:
            raise HTTPException(
                status_code=400,
                detail="Cannot calculate rolling correlation for the same asset"
            )
        
        asset_type1 = get_asset_type_from_symbol(symbol1)
        asset_type2 = get_asset_type_from_symbol(symbol2)
        
        async with DataCollector() as collector:
            hist_data1 = await collector.get_historical_data(symbol1, asset_type1, timeframe)
            hist_data2 = await collector.get_historical_data(symbol2, asset_type2, timeframe)
            
            if not hist_data1 or not hist_data2:
                raise HTTPException(
                    status_code=404,
                    detail="Historical data not found for one or both assets"
                )
            
            prices1 = [float(point.close) for point in hist_data1.data]
            prices2 = [float(point.close) for point in hist_data2.data]
            timestamps = [point.timestamp for point in hist_data1.data]
            
            min_length = min(len(prices1), len(prices2))
            prices1 = prices1[:min_length]
            prices2 = prices2[:min_length]
            timestamps = timestamps[:min_length]
            
            analyzer = CorrelationAnalyzer()
            rolling_corr = analyzer.calculate_rolling_correlation(prices1, prices2, window)
            
            if not rolling_corr:
                raise HTTPException(
                    status_code=400,
                    detail="Unable to calculate rolling correlation"
                )
            
            # Create time series data
            rolling_timestamps = timestamps[window:]  # Adjust for rolling window
            rolling_data = [
                {
                    "timestamp": ts.isoformat(),
                    "correlation": corr,
                    "abs_correlation": abs(corr)
                }
                for ts, corr in zip(rolling_timestamps, rolling_corr)
            ]
            
            # Calculate statistics
            corr_stats = {
                "mean": np.mean(rolling_corr),
                "std": np.std(rolling_corr),
                "min": np.min(rolling_corr),
                "max": np.max(rolling_corr),
                "latest": rolling_corr[-1] if rolling_corr else None
            }
            
            return AssetResponse(
                data={
                    "symbol1": symbol1,
                    "symbol2": symbol2,
                    "rolling_correlation": rolling_data,
                    "statistics": corr_stats,
                    "parameters": {
                        "window": window,
                        "timeframe": timeframe.value,
                        "data_points": len(rolling_corr)
                    }
                },
                message=f"Rolling correlation for {symbol1} and {symbol2}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating rolling correlation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


def get_correlation_explanation(correlation: float) -> str:
    """Get human-readable explanation of correlation value"""
    abs_corr = abs(correlation)
    
    if abs_corr >= 0.8:
        strength = "very strong"
    elif abs_corr >= 0.6:
        strength = "strong"
    elif abs_corr >= 0.4:
        strength = "moderate"
    elif abs_corr >= 0.2:
        strength = "weak"
    else:
        strength = "very weak"
    
    direction = "positive" if correlation > 0 else "negative" if correlation < 0 else "no"
    
    if correlation > 0:
        explanation = f"The assets show a {strength} positive relationship - they tend to move in the same direction."
    elif correlation < 0:
        explanation = f"The assets show a {strength} negative relationship - they tend to move in opposite directions."
    else:
        explanation = "The assets show no linear relationship."
    
    return explanation


def get_investment_implication(correlation: float) -> str:
    """Get investment implications of correlation"""
    abs_corr = abs(correlation)
    
    if abs_corr >= 0.8:
        if correlation > 0:
            return "High positive correlation suggests limited diversification benefits. Consider reducing allocation to one asset."
        else:
            return "High negative correlation provides excellent hedging opportunities and diversification benefits."
    elif abs_corr >= 0.6:
        if correlation > 0:
            return "Strong positive correlation offers some diversification but assets may move together during market stress."
        else:
            return "Strong negative correlation provides good hedging potential and portfolio balance."
    elif abs_corr >= 0.4:
        if correlation > 0:
            return "Moderate positive correlation allows for reasonable diversification while maintaining some directional exposure."
        else:
            return "Moderate negative correlation offers good diversification benefits for portfolio stability."
    elif abs_corr >= 0.2:
        return "Weak correlation provides good diversification benefits with independent price movements."
    else:
        return "Very weak correlation offers excellent diversification - asset prices move independently."