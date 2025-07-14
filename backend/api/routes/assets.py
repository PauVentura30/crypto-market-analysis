"""
Assets API routes - endpoints for asset data operations
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Path, Depends
from fastapi.responses import JSONResponse
import structlog

from models.asset import (
    AssetInfo, PriceData, HistoricalData, MarketSummary, AssetListItem,
    AssetSearchRequest, AssetComparisonRequest, AssetResponse, PaginatedAssetResponse,
    AssetType, TimeframeEnum
)
from services.data_collector import DataCollector, get_asset_type_from_symbol
from core.config import get_settings, ASSET_MAPPINGS
from api.deps import get_current_user_optional

logger = structlog.get_logger()
router = APIRouter()


@router.get(
    "/",
    response_model=PaginatedAssetResponse,
    summary="List all supported assets",
    description="Get a paginated list of all supported assets with basic information"
)
async def list_assets(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    asset_type: Optional[AssetType] = Query(None, description="Filter by asset type"),
    search: Optional[str] = Query(None, description="Search in asset name or symbol")
):
    """List all supported assets with pagination and filtering"""
    try:
        settings = get_settings()
        all_assets = []
        
        # Add cryptocurrencies
        for symbol, coin_id in ASSET_MAPPINGS["cryptocurrencies"].items():
            all_assets.append(AssetListItem(
                symbol=symbol,
                name=coin_id.replace("-", " ").title(),
                asset_type=AssetType.CRYPTOCURRENCY
            ))
        
        # Add traditional assets
        for symbol, ticker in ASSET_MAPPINGS["traditional"].items():
            asset_type = AssetType.INDEX if ticker.startswith("^") else AssetType.ETF
            all_assets.append(AssetListItem(
                symbol=symbol,
                name=symbol,  # Could be enhanced with real names
                asset_type=asset_type
            ))
        
        # Apply filters
        filtered_assets = all_assets
        
        if asset_type:
            filtered_assets = [a for a in filtered_assets if a.asset_type == asset_type]
        
        if search:
            search_lower = search.lower()
            filtered_assets = [
                a for a in filtered_assets 
                if search_lower in a.symbol.lower() or search_lower in a.name.lower()
            ]
        
        # Pagination
        total = len(filtered_assets)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_assets = filtered_assets[start_idx:end_idx]
        
        total_pages = (total + per_page - 1) // per_page
        
        return PaginatedAssetResponse(
            data=paginated_assets,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
        
    except Exception as e:
        logger.error(f"Error listing assets: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/{symbol}/price",
    response_model=AssetResponse,
    summary="Get current price",
    description="Get the current price and basic market data for a specific asset"
)
async def get_asset_price(
    symbol: str = Path(..., description="Asset symbol (e.g., BTC, ETH, SPY)")
):
    """Get current price for a specific asset"""
    try:
        symbol = symbol.upper()
        asset_type = get_asset_type_from_symbol(symbol)
        
        async with DataCollector() as collector:
            price_data = await collector.get_current_price(symbol, asset_type)
            
            if not price_data:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Price data not found for asset: {symbol}"
                )
            
            return AssetResponse(
                data=price_data,
                message=f"Current price for {symbol}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching price for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/{symbol}/historical",
    response_model=AssetResponse,
    summary="Get historical data",
    description="Get historical price data for a specific asset and timeframe"
)
async def get_asset_historical(
    symbol: str = Path(..., description="Asset symbol"),
    timeframe: TimeframeEnum = Query(
        TimeframeEnum.THIRTY_DAYS, 
        description="Timeframe for historical data"
    )
):
    """Get historical data for a specific asset"""
    try:
        symbol = symbol.upper()
        asset_type = get_asset_type_from_symbol(symbol)
        
        async with DataCollector() as collector:
            historical_data = await collector.get_historical_data(symbol, asset_type, timeframe)
            
            if not historical_data:
                raise HTTPException(
                    status_code=404,
                    detail=f"Historical data not found for asset: {symbol}"
                )
            
            return AssetResponse(
                data=historical_data,
                message=f"Historical data for {symbol} ({timeframe.value})"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/{symbol}/summary",
    response_model=AssetResponse,
    summary="Get market summary",
    description="Get comprehensive market summary including price, volume, market cap, and performance metrics"
)
async def get_asset_summary(
    symbol: str = Path(..., description="Asset symbol")
):
    """Get comprehensive market summary for an asset"""
    try:
        symbol = symbol.upper()
        asset_type = get_asset_type_from_symbol(symbol)
        
        async with DataCollector() as collector:
            summary = await collector.get_market_summary(symbol, asset_type)
            
            if not summary:
                raise HTTPException(
                    status_code=404,
                    detail=f"Market summary not found for asset: {symbol}"
                )
            
            return AssetResponse(
                data=summary,
                message=f"Market summary for {symbol}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching summary for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/prices",
    response_model=AssetResponse,
    summary="Get multiple asset prices",
    description="Get current prices for multiple assets in a single request"
)
async def get_multiple_prices(
    symbols: List[str] = Query(..., description="List of asset symbols"),
    include_summary: bool = Query(False, description="Include market summary data")
):
    """Get current prices for multiple assets"""
    try:
        if len(symbols) > 50:
            raise HTTPException(
                status_code=400,
                detail="Maximum 50 symbols allowed per request"
            )
        
        symbols = [s.upper() for s in symbols]
        asset_types = {symbol: get_asset_type_from_symbol(symbol) for symbol in symbols}
        
        async with DataCollector() as collector:
            prices = await collector.get_multiple_prices(symbols, asset_types)
            
            result = {}
            for symbol in symbols:
                if symbol in prices:
                    result[symbol] = prices[symbol]
                else:
                    result[symbol] = None
            
            return AssetResponse(
                data=result,
                message=f"Prices for {len(symbols)} assets"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching multiple prices: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/compare",
    response_model=AssetResponse,
    summary="Compare multiple assets",
    description="Compare performance and metrics of multiple assets over a specified timeframe"
)
async def compare_assets(request: AssetComparisonRequest):
    """Compare multiple assets performance"""
    try:
        symbols = [s.upper() for s in request.symbols]
        asset_types = {symbol: get_asset_type_from_symbol(symbol) for symbol in symbols}
        
        async with DataCollector() as collector:
            # Get current prices
            prices = await collector.get_multiple_prices(symbols, asset_types)
            
            # Get historical data for comparison
            historical_data = {}
            for symbol in symbols:
                asset_type = asset_types[symbol]
                hist_data = await collector.get_historical_data(symbol, asset_type, request.timeframe)
                if hist_data:
                    historical_data[symbol] = hist_data
            
            # Calculate comparison metrics
            comparison_result = {
                "timeframe": request.timeframe.value,
                "vs_currency": request.vs_currency,
                "assets": {},
                "summary": {
                    "best_performer": None,
                    "worst_performer": None,
                    "most_volatile": None,
                    "least_volatile": None
                }
            }
            
            performance_data = []
            
            for symbol in symbols:
                asset_data = {
                    "symbol": symbol,
                    "current_price": prices.get(symbol),
                    "historical_data": historical_data.get(symbol),
                    "performance": None,
                    "volatility": None
                }
                
                # Calculate performance if historical data available
                if symbol in historical_data and historical_data[symbol].data:
                    hist_points = historical_data[symbol].data
                    if len(hist_points) > 1:
                        start_price = float(hist_points[0].close)
                        end_price = float(hist_points[-1].close)
                        performance = ((end_price - start_price) / start_price) * 100
                        asset_data["performance"] = performance
                        
                        # Calculate volatility (standard deviation of returns)
                        prices_list = [float(point.close) for point in hist_points]
                        returns = [(prices_list[i] - prices_list[i-1]) / prices_list[i-1] 
                                 for i in range(1, len(prices_list))]
                        volatility = np.std(returns) * 100 if returns else 0
                        asset_data["volatility"] = volatility
                        
                        performance_data.append({
                            "symbol": symbol,
                            "performance": performance,
                            "volatility": volatility
                        })
                
                comparison_result["assets"][symbol] = asset_data
            
            # Find best/worst performers
            if performance_data:
                best_performer = max(performance_data, key=lambda x: x["performance"])
                worst_performer = min(performance_data, key=lambda x: x["performance"])
                most_volatile = max(performance_data, key=lambda x: x["volatility"])
                least_volatile = min(performance_data, key=lambda x: x["volatility"])
                
                comparison_result["summary"] = {
                    "best_performer": best_performer,
                    "worst_performer": worst_performer,
                    "most_volatile": most_volatile,
                    "least_volatile": least_volatile
                }
            
            return AssetResponse(
                data=comparison_result,
                message=f"Comparison of {len(symbols)} assets over {request.timeframe.value}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing assets: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/search",
    response_model=AssetResponse,
    summary="Search assets",
    description="Search for assets by name or symbol"
)
async def search_assets(
    query: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    asset_type: Optional[AssetType] = Query(None, description="Filter by asset type")
):
    """Search for assets by name or symbol"""
    try:
        query_lower = query.lower()
        all_assets = []
        
        # Search in cryptocurrencies
        for symbol, coin_id in ASSET_MAPPINGS["cryptocurrencies"].items():
            name = coin_id.replace("-", " ").title()
            if (query_lower in symbol.lower() or query_lower in name.lower()):
                if not asset_type or asset_type == AssetType.CRYPTOCURRENCY:
                    all_assets.append(AssetListItem(
                        symbol=symbol,
                        name=name,
                        asset_type=AssetType.CRYPTOCURRENCY
                    ))
        
        # Search in traditional assets
        for symbol, ticker in ASSET_MAPPINGS["traditional"].items():
            if query_lower in symbol.lower():
                asset_type_detected = AssetType.INDEX if ticker.startswith("^") else AssetType.ETF
                if not asset_type or asset_type == asset_type_detected:
                    all_assets.append(AssetListItem(
                        symbol=symbol,
                        name=symbol,
                        asset_type=asset_type_detected
                    ))
        
        # Limit results
        results = all_assets[:limit]
        
        return AssetResponse(
            data={
                "query": query,
                "results": results,
                "total_found": len(results)
            },
            message=f"Found {len(results)} assets matching '{query}'"
        )
        
    except Exception as e:
        logger.error(f"Error searching assets: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/categories",
    response_model=AssetResponse,
    summary="Get asset categories",
    description="Get available asset categories and their counts"
)
async def get_asset_categories():
    """Get available asset categories"""
    try:
        categories = {
            "cryptocurrency": len(ASSET_MAPPINGS["cryptocurrencies"]),
            "traditional": len(ASSET_MAPPINGS["traditional"]),
            "total": len(ASSET_MAPPINGS["cryptocurrencies"]) + len(ASSET_MAPPINGS["traditional"])
        }
        
        return AssetResponse(
            data=categories,
            message="Asset categories overview"
        )
        
    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")