"""
Portfolio API routes - endpoints for portfolio management and analysis
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field, validator
from decimal import Decimal
from datetime import datetime
import structlog
import numpy as np

from models.asset import AssetResponse, TimeframeEnum
from services.data_collector import DataCollector, get_asset_type_from_symbol
from services.analyzer import PerformanceAnalyzer, RiskAnalyzer
from core.config import get_settings

logger = structlog.get_logger()
router = APIRouter()


class PortfolioPosition(BaseModel):
    """Portfolio position model"""
    symbol: str = Field(..., description="Asset symbol")
    quantity: Decimal = Field(..., gt=0, description="Quantity held")
    avg_cost: Decimal = Field(..., gt=0, description="Average cost per unit")
    current_price: Optional[Decimal] = Field(None, description="Current market price")
    
    @validator('symbol')
    def symbol_uppercase(cls, v):
        return v.upper()


class Portfolio(BaseModel):
    """Portfolio model"""
    name: str = Field(..., description="Portfolio name")
    positions: List[PortfolioPosition] = Field(default_factory=list, description="Portfolio positions")
    cash: Decimal = Field(default=Decimal('0'), ge=0, description="Cash balance")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PortfolioAnalysisRequest(BaseModel):
    """Request for portfolio analysis"""
    positions: List[PortfolioPosition] = Field(..., min_items=1, description="Portfolio positions")
    benchmark_symbol: Optional[str] = Field(default="SPY", description="Benchmark for comparison")
    timeframe: TimeframeEnum = Field(default=TimeframeEnum.THIRTY_DAYS, description="Analysis timeframe")
    include_risk_metrics: bool = Field(default=True, description="Include risk analysis")


class OptimizationRequest(BaseModel):
    """Request for portfolio optimization"""
    symbols: List[str] = Field(..., min_items=2, max_items=20, description="Assets to include")
    total_value: Decimal = Field(..., gt=0, description="Total portfolio value")
    risk_tolerance: str = Field(default="moderate", description="Risk tolerance: conservative, moderate, aggressive")
    timeframe: TimeframeEnum = Field(default=TimefraneEnum.ONE_YEAR, description="Optimization timeframe")


class RebalancingRequest(BaseModel):
    """Request for portfolio rebalancing"""
    current_positions: List[PortfolioPosition] = Field(..., description="Current portfolio positions")
    target_allocations: Dict[str, float] = Field(..., description="Target allocations (symbol: percentage)")
    
    @validator('target_allocations')
    def allocations_sum_to_100(cls, v):
        total = sum(v.values())
        if not (99.0 <= total <= 101.0):  # Allow small rounding errors
            raise ValueError('Target allocations must sum to approximately 100%')
        return v


@router.post(
    "/analyze",
    response_model=AssetResponse,
    summary="Portfolio Analysis",
    description="Comprehensive analysis of portfolio performance, risk metrics, and allocation"
)
async def analyze_portfolio(request: PortfolioAnalysisRequest):
    """Analyze portfolio performance and risk metrics"""
    try:
        symbols = [pos.symbol for pos in request.positions]
        asset_types = {symbol: get_asset_type_from_symbol(symbol) for symbol in symbols}
        
        async with DataCollector() as collector:
            # Get current prices for all positions
            current_prices = await collector.get_multiple_prices(symbols, asset_types)
            
            # Get historical data for performance analysis
            historical_data = {}
            for symbol in symbols:
                asset_type = asset_types[symbol]
                hist_data = await collector.get_historical_data(symbol, asset_type, request.timeframe)
                if hist_data and hist_data.data:
                    historical_data[symbol] = hist_data
            
            # Get benchmark data if specified
            benchmark_data = None
            if request.benchmark_symbol:
                benchmark_type = get_asset_type_from_symbol(request.benchmark_symbol)
                benchmark_data = await collector.get_historical_data(
                    request.benchmark_symbol, benchmark_type, request.timeframe
                )
            
            # Calculate portfolio metrics
            portfolio_analysis = calculate_portfolio_metrics(
                request.positions, current_prices, historical_data, benchmark_data
            )
            
            # Add risk analysis if requested
            if request.include_risk_metrics:
                risk_analysis = calculate_portfolio_risk(
                    request.positions, historical_data, current_prices
                )
                portfolio_analysis["risk_analysis"] = risk_analysis
            
            return AssetResponse(
                data=portfolio_analysis,
                message=f"Portfolio analysis completed for {len(symbols)} positions"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing portfolio: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/optimize",
    response_model=AssetResponse,
    summary="Portfolio Optimization",
    description="Optimize portfolio allocation based on modern portfolio theory"
)
async def optimize_portfolio(request: OptimizationRequest):
    """Optimize portfolio allocation using modern portfolio theory"""
    try:
        symbols = [s.upper() for s in request.symbols]
        asset_types = {symbol: get_asset_type_from_symbol(symbol) for symbol in symbols}
        
        async with DataCollector() as collector:
            # Get historical data for all assets
            historical_data = {}
            for symbol in symbols:
                asset_type = asset_types[symbol]
                hist_data = await collector.get_historical_data(symbol, asset_type, request.timeframe)
                if hist_data and hist_data.data:
                    historical_data[symbol] = hist_data
            
            if len(historical_data) < 2:
                raise HTTPException(
                    status_code=404,
                    detail="Insufficient historical data for optimization"
                )
            
            # Calculate optimization
            optimization_result = calculate_portfolio_optimization(
                historical_data, request.risk_tolerance, float(request.total_value)
            )
            
            return AssetResponse(
                data=optimization_result,
                message=f"Portfolio optimization completed for {len(symbols)} assets"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error optimizing portfolio: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/rebalance",
    response_model=AssetResponse,
    summary="Portfolio Rebalancing",
    description="Calculate trades needed to rebalance portfolio to target allocations"
)
async def rebalance_portfolio(request: RebalancingRequest):
    """Calculate rebalancing trades for portfolio"""
    try:
        symbols = [pos.symbol for pos in request.current_positions]
        asset_types = {symbol: get_asset_type_from_symbol(symbol) for symbol in symbols}
        
        async with DataCollector() as collector:
            # Get current prices
            current_prices = await collector.get_multiple_prices(symbols, asset_types)
            
            # Calculate current portfolio value and allocations
            current_values = {}
            total_value = Decimal('0')
            
            for position in request.current_positions:
                symbol = position.symbol
                if symbol in current_prices and current_prices[symbol]:
                    current_price = Decimal(str(current_prices[symbol].price))
                    value = position.quantity * current_price
                    current_values[symbol] = value
                    total_value += value
                else:
                    # Use average cost if current price not available
                    value = position.quantity * position.avg_cost
                    current_values[symbol] = value
                    total_value += value
            
            # Calculate current allocations
            current_allocations = {
                symbol: float(value / total_value * 100) if total_value > 0 else 0
                for symbol, value in current_values.items()
            }
            
            # Calculate target values
            target_values = {
                symbol: total_value * Decimal(str(allocation / 100))
                for symbol, allocation in request.target_allocations.items()
            }
            
            # Calculate rebalancing trades
            rebalancing_trades = []
            for symbol in set(list(current_values.keys()) + list(target_values.keys())):
                current_value = current_values.get(symbol, Decimal('0'))
                target_value = target_values.get(symbol, Decimal('0'))
                difference = target_value - current_value
                
                if abs(difference) > total_value * Decimal('0.01'):  # 1% threshold
                    current_price = None
                    if symbol in current_prices and current_prices[symbol]:
                        current_price = Decimal(str(current_prices[symbol].price))
                    
                    if current_price and current_price > 0:
                        quantity_change = difference / current_price
                        
                        rebalancing_trades.append({
                            "symbol": symbol,
                            "action": "buy" if difference > 0 else "sell",
                            "quantity": abs(float(quantity_change)),
                            "value": float(abs(difference)),
                            "current_allocation": current_allocations.get(symbol, 0),
                            "target_allocation": request.target_allocations.get(symbol, 0),
                            "price": float(current_price)
                        })
            
            # Calculate rebalancing summary
            total_trades_value = sum(trade["value"] for trade in rebalancing_trades)
            turnover_rate = (total_trades_value / float(total_value)) * 100 if total_value > 0 else 0
            
            rebalancing_summary = {
                "current_allocations": current_allocations,
                "target_allocations": request.target_allocations,
                "required_trades": rebalancing_trades,
                "total_portfolio_value": float(total_value),
                "total_trades_value": total_trades_value,
                "turnover_rate": turnover_rate,
                "number_of_trades": len(rebalancing_trades)
            }
            
            return AssetResponse(
                data=rebalancing_summary,
                message=f"Rebalancing analysis completed - {len(rebalancing_trades)} trades required"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating rebalancing: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/performance/{symbol}",
    response_model=AssetResponse,
    summary="Asset Performance",
    description="Get detailed performance metrics for a single asset position"
)
async def asset_performance(
    symbol: str,
    quantity: Decimal = Query(..., gt=0, description="Quantity held"),
    avg_cost: Decimal = Query(..., gt=0, description="Average cost per unit"),
    timeframe: TimeframeEnum = Query(default=TimeframeEnum.THIRTY_DAYS)
):
    """Get performance metrics for a single asset position"""
    try:
        symbol = symbol.upper()
        asset_type = get_asset_type_from_symbol(symbol)
        
        async with DataCollector() as collector:
            # Get current price
            current_price_data = await collector.get_current_price(symbol, asset_type)
            if not current_price_data:
                raise HTTPException(
                    status_code=404,
                    detail=f"Current price not found for {symbol}"
                )
            
            # Get historical data
            hist_data = await collector.get_historical_data(symbol, asset_type, timeframe)
            if not hist_data or not hist_data.data:
                raise HTTPException(
                    status_code=404,
                    detail=f"Historical data not found for {symbol}"
                )
            
            current_price = Decimal(str(current_price_data.price))
            
            # Calculate position metrics
            position_value = quantity * current_price
            total_cost = quantity * avg_cost
            unrealized_pnl = position_value - total_cost
            unrealized_pnl_percent = (unrealized_pnl / total_cost * 100) if total_cost > 0 else Decimal('0')
            
            # Calculate performance metrics from historical data
            prices = [float(point.close) for point in hist_data.data]
            analyzer = PerformanceAnalyzer()
            returns = analyzer.calculate_returns(prices)
            
            performance_metrics = {
                "symbol": symbol,
                "position_details": {
                    "quantity": float(quantity),
                    "avg_cost": float(avg_cost),
                    "current_price": float(current_price),
                    "position_value": float(position_value),
                    "total_cost": float(total_cost),
                    "unrealized_pnl": float(unrealized_pnl),
                    "unrealized_pnl_percent": float(unrealized_pnl_percent)
                },
                "performance_metrics": {
                    "total_return": analyzer.calculate_total_return(prices),
                    "volatility": analyzer.calculate_volatility(returns),
                    "sharpe_ratio": analyzer.calculate_sharpe_ratio(returns),
                    "max_drawdown": analyzer.calculate_max_drawdown(prices),
                    "calmar_ratio": analyzer.calculate_calmar_ratio(returns, prices)
                },
                "market_data": {
                    "price_change_24h": float(current_price_data.price_change_24h or 0),
                    "price_change_percentage_24h": float(current_price_data.price_change_percentage_24h or 0),
                    "volume_24h": float(current_price_data.volume_24h or 0),
                    "market_cap": float(current_price_data.market_cap or 0)
                }
            }
            
            return AssetResponse(
                data=performance_metrics,
                message=f"Performance analysis for {symbol} position"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing asset performance: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


def calculate_portfolio_metrics(
    positions: List[PortfolioPosition],
    current_prices: Dict[str, Any],
    historical_data: Dict[str, Any],
    benchmark_data: Optional[Any] = None
) -> Dict[str, Any]:
    """Calculate comprehensive portfolio metrics"""
    
    # Calculate current portfolio value and allocations
    total_value = Decimal('0')
    position_values = {}
    
    for position in positions:
        symbol = position.symbol
        if symbol in current_prices and current_prices[symbol]:
            current_price = Decimal(str(current_prices[symbol].price))
            value = position.quantity * current_price
        else:
            value = position.quantity * position.avg_cost
        
        position_values[symbol] = value
        total_value += value
    
    # Calculate allocations
    allocations = {
        symbol: float(value / total_value * 100) if total_value > 0 else 0
        for symbol, value in position_values.items()
    }
    
    # Calculate total cost and P&L
    total_cost = sum(pos.quantity * pos.avg_cost for pos in positions)
    unrealized_pnl = total_value - total_cost
    unrealized_pnl_percent = (unrealized_pnl / total_cost * 100) if total_cost > 0 else Decimal('0')
    
    # Portfolio performance analysis
    portfolio_performance = {}
    if historical_data:
        # Calculate portfolio returns
        portfolio_returns = calculate_portfolio_returns(positions, historical_data)
        
        if portfolio_returns:
            analyzer = PerformanceAnalyzer()
            portfolio_performance = {
                "total_return": analyzer.calculate_total_return(portfolio_returns),
                "annualized_return": analyzer.calculate_annualized_return(
                    analyzer.calculate_returns(portfolio_returns)
                ),
                "volatility": analyzer.calculate_volatility(
                    analyzer.calculate_returns(portfolio_returns)
                ),
                "sharpe_ratio": analyzer.calculate_sharpe_ratio(
                    analyzer.calculate_returns(portfolio_returns)
                ),
                "max_drawdown": analyzer.calculate_max_drawdown(portfolio_returns)
            }
    
    # Benchmark comparison
    benchmark_comparison = {}
    if benchmark_data and benchmark_data.data:
        benchmark_prices = [float(point.close) for point in benchmark_data.data]
        benchmark_returns = PerformanceAnalyzer().calculate_returns(benchmark_prices)
        
        if portfolio_returns and benchmark_returns:
            portfolio_ret = PerformanceAnalyzer().calculate_returns(portfolio_returns)
            
            # Calculate beta and alpha
            if len(portfolio_ret) == len(benchmark_returns):
                risk_analyzer = RiskAnalyzer()
                beta = risk_analyzer.calculate_beta(portfolio_ret, benchmark_returns)
                
                portfolio_total_return = PerformanceAnalyzer().calculate_total_return(portfolio_returns)
                benchmark_total_return = PerformanceAnalyzer().calculate_total_return(benchmark_prices)
                alpha = portfolio_total_return - (beta * benchmark_total_return)
                
                benchmark_comparison = {
                    "benchmark_symbol": "SPY",  # or the actual benchmark used
                    "portfolio_return": portfolio_total_return,
                    "benchmark_return": benchmark_total_return,
                    "outperformance": portfolio_total_return - benchmark_total_return,
                    "beta": beta,
                    "alpha": alpha
                }
    
    return {
        "portfolio_value": float(total_value),
        "total_cost": float(total_cost),
        "unrealized_pnl": float(unrealized_pnl),
        "unrealized_pnl_percent": float(unrealized_pnl_percent),
        "allocations": allocations,
        "position_values": {k: float(v) for k, v in position_values.items()},
        "performance": portfolio_performance,
        "benchmark_comparison": benchmark_comparison,
        "portfolio_statistics": {
            "number_of_positions": len(positions),
            "largest_position": max(allocations, key=allocations.get) if allocations else None,
            "largest_allocation": max(allocations.values()) if allocations else 0,
            "concentration_risk": sum(1 for alloc in allocations.values() if alloc > 20)  # Positions > 20%
        }
    }


def calculate_portfolio_risk(
    positions: List[PortfolioPosition],
    historical_data: Dict[str, Any],
    current_prices: Dict[str, Any]
) -> Dict[str, Any]:
    """Calculate portfolio risk metrics"""
    
    risk_analyzer = RiskAnalyzer()
    
    # Calculate individual asset risks
    asset_risks = {}
    for position in positions:
        symbol = position.symbol
        if symbol in historical_data:
            prices = [float(point.close) for point in historical_data[symbol].data]
            returns = PerformanceAnalyzer().calculate_returns(prices)
            asset_risks[symbol] = risk_analyzer.assess_risk_profile(returns)
    
    # Portfolio-level risk (simplified)
    portfolio_returns = calculate_portfolio_returns(positions, historical_data)
    portfolio_risk = {}
    
    if portfolio_returns:
        portfolio_ret = PerformanceAnalyzer().calculate_returns(portfolio_returns)
        portfolio_risk = risk_analyzer.assess_risk_profile(portfolio_ret)
    
    return {
        "portfolio_risk": portfolio_risk,
        "asset_risks": asset_risks,
        "risk_summary": {
            "high_risk_assets": len([r for r in asset_risks.values() if r.get("risk_level") in ["high", "very_high"]]),
            "medium_risk_assets": len([r for r in asset_risks.values() if r.get("risk_level") == "medium"]),
            "low_risk_assets": len([r for r in asset_risks.values() if r.get("risk_level") in ["low", "very_low"]])
        }
    }


def calculate_portfolio_returns(
    positions: List[PortfolioPosition],
    historical_data: Dict[str, Any]
) -> List[float]:
    """Calculate historical portfolio returns"""
    
    # Get the shortest time series length
    min_length = min(len(historical_data[pos.symbol].data) 
                    for pos in positions 
                    if pos.symbol in historical_data)
    
    if min_length == 0:
        return []
    
    # Calculate weights based on initial positions
    total_initial_value = sum(pos.quantity * pos.avg_cost for pos in positions)
    weights = {
        pos.symbol: float(pos.quantity * pos.avg_cost / total_initial_value)
        for pos in positions
        if total_initial_value > 0
    }
    
    # Calculate portfolio value for each time point
    portfolio_values = []
    for i in range(min_length):
        portfolio_value = 0
        for position in positions:
            if position.symbol in historical_data:
                price = float(historical_data[position.symbol].data[i].close)
                portfolio_value += weights.get(position.symbol, 0) * price
        portfolio_values.append(portfolio_value)
    
    return portfolio_values


def calculate_portfolio_optimization(
    historical_data: Dict[str, Any],
    risk_tolerance: str,
    total_value: float
) -> Dict[str, Any]:
    """Calculate optimal portfolio allocation"""
    
    # This is a simplified optimization - in production, you'd use more sophisticated methods
    # like mean-variance optimization with libraries like scipy.optimize
    
    symbols = list(historical_data.keys())
    
    # Calculate returns and covariance matrix
    returns_data = {}
    for symbol, hist_data in historical_data.items():
        prices = [float(point.close) for point in hist_data.data]
        returns = PerformanceAnalyzer().calculate_returns(prices)
        returns_data[symbol] = returns
    
    import pandas as pd
    returns_df = pd.DataFrame(returns_data)
    
    if returns_df.empty:
        return {"error": "Insufficient data for optimization"}
    
    # Calculate expected returns and volatilities
    expected_returns = returns_df.mean() * 252  # Annualize
    volatilities = returns_df.std() * np.sqrt(252)  # Annualize
    
    # Simple optimization based on risk tolerance
    if risk_tolerance == "conservative":
        # Weight by inverse volatility
        inv_vol = 1 / volatilities
        weights = inv_vol / inv_vol.sum()
    elif risk_tolerance == "aggressive":
        # Weight by expected returns
        weights = expected_returns / expected_returns.sum()
    else:  # moderate
        # Equal weight with slight adjustment for risk-return
        base_weight = 1 / len(symbols)
        risk_adj = (expected_returns / volatilities).fillna(1)
        weights = (base_weight + risk_adj / risk_adj.sum() * 0.2)
        weights = weights / weights.sum()
    
    # Convert to allocation dictionary
    allocations = {}
    position_values = {}
    
    for symbol in symbols:
        allocation_percent = float(weights[symbol] * 100)
        allocation_value = total_value * weights[symbol]
        
        allocations[symbol] = allocation_percent
        position_values[symbol] = allocation_value
    
    # Calculate portfolio metrics
    portfolio_expected_return = float((weights * expected_returns).sum())
    portfolio_volatility = float(np.sqrt(np.dot(weights, np.dot(returns_df.cov() * 252, weights))))
    sharpe_ratio = portfolio_expected_return / portfolio_volatility if portfolio_volatility > 0 else 0
    
    return {
        "optimal_allocations": allocations,
        "position_values": position_values,
        "portfolio_metrics": {
            "expected_annual_return": portfolio_expected_return * 100,
            "annual_volatility": portfolio_volatility * 100,
            "sharpe_ratio": sharpe_ratio
        },
        "individual_metrics": {
            symbol: {
                "expected_return": float(expected_returns[symbol] * 100),
                "volatility": float(volatilities[symbol] * 100),
                "allocation": allocations[symbol]
            }
            for symbol in symbols
        },
        "optimization_parameters": {
            "risk_tolerance": risk_tolerance,
            "total_value": total_value,
            "number_of_assets": len(symbols)
        }
    }