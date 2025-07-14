"""
Analysis API routes - endpoints for market analysis and metrics
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import structlog

from models.asset import AssetResponse, TimeframeEnum, AssetType
from services.data_collector import DataCollector, get_asset_type_from_symbol
from services.analyzer import TechnicalAnalyzer, PerformanceAnalyzer
from core.config import get_settings

logger = structlog.get_logger()
router = APIRouter()


class AnalysisRequest(BaseModel):
    """Request model for analysis endpoints"""
    symbols: List[str] = Field(..., min_items=1, max_items=20, description="Asset symbols to analyze")
    timeframe: TimeframeEnum = Field(default=TimeframeEnum.THIRTY_DAYS, description="Analysis timeframe")
    metrics: Optional[List[str]] = Field(default=None, description="Specific metrics to calculate")


class VolatilityAnalysisRequest(BaseModel):
    """Request for volatility analysis"""
    symbols: List[str] = Field(..., min_items=1, max_items=10)
    timeframe: TimeframeEnum = Field(default=TimeframeEnum.THIRTY_DAYS)
    window: int = Field(default=20, ge=5, le=100, description="Rolling window for volatility calculation")


class TechnicalAnalysisRequest(BaseModel):
    """Request for technical analysis"""
    symbol: str = Field(..., description="Asset symbol")
    timeframe: TimeframeEnum = Field(default=TimeframeEnum.THIRTY_DAYS)
    indicators: List[str] = Field(
        default=["sma", "ema", "rsi", "macd"],
        description="Technical indicators to calculate"
    )


@router.post(
    "/performance",
    response_model=AssetResponse,
    summary="Performance Analysis",
    description="Analyze performance metrics for multiple assets including returns, volatility, and risk metrics"
)
async def analyze_performance(request: AnalysisRequest):
    """Analyze performance metrics for multiple assets"""
    try:
        symbols = [s.upper() for s in request.symbols]
        asset_types = {symbol: get_asset_type_from_symbol(symbol) for symbol in symbols}
        
        async with DataCollector() as collector:
            # Get historical data for all symbols
            historical_data = {}
            for symbol in symbols:
                asset_type = asset_types[symbol]
                hist_data = await collector.get_historical_data(symbol, asset_type, request.timeframe)
                if hist_data and hist_data.data:
                    historical_data[symbol] = hist_data
            
            if not historical_data:
                raise HTTPException(
                    status_code=404,
                    detail="No historical data found for the specified assets"
                )
            
            # Initialize performance analyzer
            analyzer = PerformanceAnalyzer()
            
            # Calculate performance metrics for each asset
            performance_results = {}
            for symbol, hist_data in historical_data.items():
                prices = [float(point.close) for point in hist_data.data]
                volumes = [float(point.volume) if point.volume else 0 for point in hist_data.data]
                timestamps = [point.timestamp for point in hist_data.data]
                
                # Calculate returns
                returns = analyzer.calculate_returns(prices)
                
                # Performance metrics
                metrics = {
                    "symbol": symbol,
                    "timeframe": request.timeframe.value,
                    "total_return": analyzer.calculate_total_return(prices),
                    "annualized_return": analyzer.calculate_annualized_return(returns, len(prices)),
                    "volatility": analyzer.calculate_volatility(returns),
                    "sharpe_ratio": analyzer.calculate_sharpe_ratio(returns),
                    "max_drawdown": analyzer.calculate_max_drawdown(prices),
                    "calmar_ratio": analyzer.calculate_calmar_ratio(returns, prices),
                    "avg_volume": np.mean(volumes) if volumes else 0,
                    "price_range": {
                        "min": min(prices),
                        "max": max(prices),
                        "current": prices[-1]
                    },
                    "data_points": len(prices),
                    "period_start": timestamps[0].isoformat(),
                    "period_end": timestamps[-1].isoformat()
                }
                
                performance_results[symbol] = metrics
            
            # Calculate comparative metrics
            all_returns = []
            all_volatilities = []
            for symbol, metrics in performance_results.items():
                all_returns.append(metrics["total_return"])
                all_volatilities.append(metrics["volatility"])
            
            comparative_analysis = {
                "best_performer": max(performance_results.items(), key=lambda x: x[1]["total_return"]),
                "worst_performer": min(performance_results.items(), key=lambda x: x[1]["total_return"]),
                "highest_sharpe": max(performance_results.items(), key=lambda x: x[1]["sharpe_ratio"]),
                "lowest_volatility": min(performance_results.items(), key=lambda x: x[1]["volatility"]),
                "average_return": np.mean(all_returns),
                "average_volatility": np.mean(all_volatilities)
            }
            
            return AssetResponse(
                data={
                    "individual_performance": performance_results,
                    "comparative_analysis": comparative_analysis,
                    "analysis_metadata": {
                        "timeframe": request.timeframe.value,
                        "assets_analyzed": len(symbols),
                        "analysis_date": datetime.utcnow().isoformat()
                    }
                },
                message=f"Performance analysis completed for {len(symbols)} assets"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in performance analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/volatility",
    response_model=AssetResponse,
    summary="Volatility Analysis",
    description="Analyze volatility patterns and risk metrics for assets"
)
async def analyze_volatility(request: VolatilityAnalysisRequest):
    """Analyze volatility for multiple assets"""
    try:
        symbols = [s.upper() for s in request.symbols]
        asset_types = {symbol: get_asset_type_from_symbol(symbol) for symbol in symbols}
        
        async with DataCollector() as collector:
            historical_data = {}
            for symbol in symbols:
                asset_type = asset_types[symbol]
                hist_data = await collector.get_historical_data(symbol, asset_type, request.timeframe)
                if hist_data and hist_data.data:
                    historical_data[symbol] = hist_data
            
            if not historical_data:
                raise HTTPException(
                    status_code=404,
                    detail="No historical data found for volatility analysis"
                )
            
            analyzer = PerformanceAnalyzer()
            volatility_results = {}
            
            for symbol, hist_data in historical_data.items():
                prices = [float(point.close) for point in hist_data.data]
                returns = analyzer.calculate_returns(prices)
                
                # Calculate different volatility measures
                volatility_metrics = {
                    "symbol": symbol,
                    "historical_volatility": analyzer.calculate_volatility(returns),
                    "rolling_volatility": analyzer.calculate_rolling_volatility(returns, request.window),
                    "garch_volatility": analyzer.calculate_garch_volatility(returns),
                    "var_95": analyzer.calculate_var(returns, confidence_level=0.95),
                    "var_99": analyzer.calculate_var(returns, confidence_level=0.99),
                    "conditional_var": analyzer.calculate_cvar(returns),
                    "volatility_clustering": analyzer.detect_volatility_clustering(returns),
                    "volatility_regime": analyzer.identify_volatility_regime(returns)
                }
                
                volatility_results[symbol] = volatility_metrics
            
            # Volatility ranking
            volatility_ranking = sorted(
                volatility_results.items(),
                key=lambda x: x[1]["historical_volatility"],
                reverse=True
            )
            
            return AssetResponse(
                data={
                    "volatility_analysis": volatility_results,
                    "volatility_ranking": volatility_ranking,
                    "market_regime": analyzer.assess_market_regime(volatility_results),
                    "analysis_parameters": {
                        "timeframe": request.timeframe.value,
                        "rolling_window": request.window,
                        "assets_count": len(symbols)
                    }
                },
                message=f"Volatility analysis completed for {len(symbols)} assets"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in volatility analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/technical",
    response_model=AssetResponse,
    summary="Technical Analysis",
    description="Calculate technical indicators and signals for an asset"
)
async def technical_analysis(request: TechnicalAnalysisRequest):
    """Perform technical analysis on an asset"""
    try:
        symbol = request.symbol.upper()
        asset_type = get_asset_type_from_symbol(symbol)
        
        async with DataCollector() as collector:
            hist_data = await collector.get_historical_data(symbol, asset_type, request.timeframe)
            
            if not hist_data or not hist_data.data:
                raise HTTPException(
                    status_code=404,
                    detail=f"No historical data found for {symbol}"
                )
            
            # Prepare data for technical analysis
            df = pd.DataFrame([
                {
                    "timestamp": point.timestamp,
                    "open": float(point.open) if point.open else float(point.close),
                    "high": float(point.high) if point.high else float(point.close),
                    "low": float(point.low) if point.low else float(point.close),
                    "close": float(point.close),
                    "volume": float(point.volume) if point.volume else 0
                }
                for point in hist_data.data
            ])
            
            # Initialize technical analyzer
            tech_analyzer = TechnicalAnalyzer(df)
            
            # Calculate requested indicators
            indicators = {}
            for indicator in request.indicators:
                if hasattr(tech_analyzer, f"calculate_{indicator}"):
                    indicators[indicator] = getattr(tech_analyzer, f"calculate_{indicator}")()
            
            # Generate trading signals
            signals = tech_analyzer.generate_signals(request.indicators)
            
            # Support and resistance levels
            support_resistance = tech_analyzer.find_support_resistance()
            
            # Current market sentiment
            sentiment = tech_analyzer.assess_sentiment()
            
            return AssetResponse(
                data={
                    "symbol": symbol,
                    "timeframe": request.timeframe.value,
                    "indicators": indicators,
                    "signals": signals,
                    "support_resistance": support_resistance,
                    "sentiment": sentiment,
                    "analysis_date": datetime.utcnow().isoformat(),
                    "data_points": len(df)
                },
                message=f"Technical analysis completed for {symbol}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in technical analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/market-overview",
    response_model=AssetResponse,
    summary="Market Overview",
    description="Get overall market analysis and trends"
)
async def market_overview(
    timeframe: TimeframeEnum = Query(default=TimeframeEnum.THIRTY_DAYS),
    include_crypto: bool = Query(default=True, description="Include cryptocurrency metrics"),
    include_traditional: bool = Query(default=True, description="Include traditional market metrics")
):
    """Get comprehensive market overview"""
    try:
        from core.config import ASSET_MAPPINGS
        
        symbols = []
        if include_crypto:
            symbols.extend(list(ASSET_MAPPINGS["cryptocurrencies"].keys())[:5])  # Top 5 crypto
        if include_traditional:
            symbols.extend(["SPY", "QQQ", "GLD"])  # Key traditional assets
        
        asset_types = {symbol: get_asset_type_from_symbol(symbol) for symbol in symbols}
        
        async with DataCollector() as collector:
            # Get current prices
            current_prices = await collector.get_multiple_prices(symbols, asset_types)
            
            # Get historical data for trend analysis
            historical_data = {}
            for symbol in symbols:
                asset_type = asset_types[symbol]
                hist_data = await collector.get_historical_data(symbol, asset_type, timeframe)
                if hist_data:
                    historical_data[symbol] = hist_data
            
            analyzer = PerformanceAnalyzer()
            
            # Market sentiment analysis
            market_sentiment = {
                "overall_trend": "neutral",
                "crypto_sentiment": "neutral",
                "traditional_sentiment": "neutral",
                "volatility_level": "normal",
                "market_fear_greed": 50  # Simulated value
            }
            
            # Performance summary
            performance_summary = {}
            for symbol, hist_data in historical_data.items():
                if hist_data.data:
                    prices = [float(point.close) for point in hist_data.data]
                    returns = analyzer.calculate_returns(prices)
                    
                    performance_summary[symbol] = {
                        "return": analyzer.calculate_total_return(prices),
                        "volatility": analyzer.calculate_volatility(returns),
                        "trend": "up" if prices[-1] > prices[0] else "down"
                    }
            
            # Market statistics
            if performance_summary:
                all_returns = [p["return"] for p in performance_summary.values()]
                all_volatilities = [p["volatility"] for p in performance_summary.values()]
                
                market_stats = {
                    "average_return": np.mean(all_returns),
                    "median_return": np.median(all_returns),
                    "average_volatility": np.mean(all_volatilities),
                    "assets_positive": sum(1 for r in all_returns if r > 0),
                    "assets_negative": sum(1 for r in all_returns if r < 0),
                    "total_assets": len(all_returns)
                }
            else:
                market_stats = {}
            
            return AssetResponse(
                data={
                    "market_sentiment": market_sentiment,
                    "performance_summary": performance_summary,
                    "market_statistics": market_stats,
                    "current_prices": current_prices,
                    "analysis_metadata": {
                        "timeframe": timeframe.value,
                        "assets_analyzed": len(symbols),
                        "include_crypto": include_crypto,
                        "include_traditional": include_traditional,
                        "analysis_time": datetime.utcnow().isoformat()
                    }
                },
                message="Market overview analysis completed"
            )
            
    except Exception as e:
        logger.error(f"Error in market overview: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/trends",
    response_model=AssetResponse,
    summary="Market Trends",
    description="Identify and analyze current market trends"
)
async def analyze_trends(
    symbols: List[str] = Query(..., description="Asset symbols to analyze"),
    timeframe: TimeframeEnum = Query(default=TimeframeEnum.THIRTY_DAYS),
    trend_periods: List[int] = Query(default=[10, 20, 50], description="Periods for trend analysis")
):
    """Analyze market trends for multiple assets"""
    try:
        symbols = [s.upper() for s in symbols]
        
        if len(symbols) > 20:
            raise HTTPException(
                status_code=400,
                detail="Maximum 20 symbols allowed for trend analysis"
            )
        
        asset_types = {symbol: get_asset_type_from_symbol(symbol) for symbol in symbols}
        
        async with DataCollector() as collector:
            historical_data = {}
            for symbol in symbols:
                asset_type = asset_types[symbol]
                hist_data = await collector.get_historical_data(symbol, asset_type, timeframe)
                if hist_data and hist_data.data:
                    historical_data[symbol] = hist_data
            
            if not historical_data:
                raise HTTPException(
                    status_code=404,
                    detail="No historical data found for trend analysis"
                )
            
            trend_analysis = {}
            for symbol, hist_data in historical_data.items():
                prices = [float(point.close) for point in hist_data.data]
                
                # Calculate moving averages for different periods
                moving_averages = {}
                trend_signals = {}
                
                for period in trend_periods:
                    if len(prices) >= period:
                        ma = pd.Series(prices).rolling(window=period).mean().tolist()
                        moving_averages[f"ma_{period}"] = ma[-1] if ma else None
                        
                        # Trend signal based on price vs MA
                        current_price = prices[-1]
                        if ma and ma[-1]:
                            if current_price > ma[-1]:
                                trend_signals[f"ma_{period}_signal"] = "bullish"
                            else:
                                trend_signals[f"ma_{period}_signal"] = "bearish"
                
                # Overall trend determination
                bullish_signals = sum(1 for signal in trend_signals.values() if signal == "bullish")
                total_signals = len(trend_signals)
                
                if total_signals > 0:
                    trend_strength = bullish_signals / total_signals
                    if trend_strength >= 0.7:
                        overall_trend = "strong_bullish"
                    elif trend_strength >= 0.5:
                        overall_trend = "bullish"
                    elif trend_strength >= 0.3:
                        overall_trend = "bearish"
                    else:
                        overall_trend = "strong_bearish"
                else:
                    overall_trend = "neutral"
                
                trend_analysis[symbol] = {
                    "moving_averages": moving_averages,
                    "trend_signals": trend_signals,
                    "overall_trend": overall_trend,
                    "trend_strength": trend_strength if total_signals > 0 else 0.5,
                    "current_price": prices[-1],
                    "price_change": ((prices[-1] - prices[0]) / prices[0] * 100) if prices[0] != 0 else 0
                }
            
            return AssetResponse(
                data={
                    "trend_analysis": trend_analysis,
                    "analysis_parameters": {
                        "timeframe": timeframe.value,
                        "trend_periods": trend_periods,
                        "assets_count": len(symbols)
                    }
                },
                message=f"Trend analysis completed for {len(symbols)} assets"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in trend analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")