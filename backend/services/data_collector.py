"""
Data collection service for fetching market data from multiple sources
"""

import asyncio
import aiohttp
import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from decimal import Decimal
import structlog
from dataclasses import dataclass

from core.config import get_settings, ASSET_MAPPINGS, DATA_SOURCES, TIME_PERIODS
from models.asset import (
    PriceData, HistoricalData, HistoricalPricePoint, MarketSummary,
    AssetType, TimeframeEnum
)

logger = structlog.get_logger()


@dataclass
class DataSourceConfig:
    """Configuration for data sources"""
    name: str
    priority: int  # Lower number = higher priority
    rate_limit: int  # requests per minute
    timeout: int = 30


class DataCollector:
    """Main data collection service"""
    
    def __init__(self):
        self.settings = get_settings()
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limiters = {}
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"User-Agent": "CryptoAnalyzer/1.0"}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def get_current_price(self, symbol: str, asset_type: AssetType) -> Optional[PriceData]:
        """Get current price for an asset"""
        try:
            if asset_type == AssetType.CRYPTOCURRENCY:
                return await self._get_crypto_price(symbol)
            else:
                return await self._get_traditional_price(symbol)
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {str(e)}")
            return None
    
    async def get_historical_data(
        self, 
        symbol: str, 
        asset_type: AssetType,
        timeframe: TimeframeEnum
    ) -> Optional[HistoricalData]:
        """Get historical data for an asset"""
        try:
            if asset_type == AssetType.CRYPTOCURRENCY:
                return await self._get_crypto_historical(symbol, timeframe)
            else:
                return await self._get_traditional_historical(symbol, timeframe)
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
            return None
    
    async def get_multiple_prices(
        self, 
        symbols: List[str], 
        asset_types: Dict[str, AssetType]
    ) -> Dict[str, PriceData]:
        """Get current prices for multiple assets"""
        tasks = []
        for symbol in symbols:
            asset_type = asset_types.get(symbol, AssetType.CRYPTOCURRENCY)
            task = self.get_current_price(symbol, asset_type)
            tasks.append((symbol, task))
        
        results = {}
        for symbol, task in tasks:
            try:
                price_data = await task
                if price_data:
                    results[symbol] = price_data
            except Exception as e:
                logger.error(f"Error fetching price for {symbol}: {str(e)}")
        
        return results
    
    async def _get_crypto_price(self, symbol: str) -> Optional[PriceData]:
        """Get cryptocurrency price from CoinGecko"""
        try:
            coin_id = ASSET_MAPPINGS["cryptocurrencies"].get(symbol.upper())
            if not coin_id:
                return None
            
            url = f"{DATA_SOURCES['coingecko']['base_url']}/simple/price"
            params = {
                "ids": coin_id,
                "vs_currencies": "usd",
                "include_market_cap": "true",
                "include_24hr_vol": "true",
                "include_24hr_change": "true",
                "include_last_updated_at": "true"
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    coin_data = data.get(coin_id, {})
                    
                    return PriceData(
                        symbol=symbol.upper(),
                        price=Decimal(str(coin_data.get("usd", 0))),
                        price_change_24h=Decimal(str(coin_data.get("usd_24h_change", 0))),
                        price_change_percentage_24h=Decimal(str(coin_data.get("usd_24h_change", 0))),
                        market_cap=Decimal(str(coin_data.get("usd_market_cap", 0))),
                        volume_24h=Decimal(str(coin_data.get("usd_24h_vol", 0))),
                        last_updated=datetime.utcnow()
                    )
                    
        except Exception as e:
            logger.error(f"Error fetching crypto price for {symbol}: {str(e)}")
            return None
    
    async def _get_traditional_price(self, symbol: str) -> Optional[PriceData]:
        """Get traditional asset price from Yahoo Finance"""
        try:
            # Use yfinance for traditional assets
            ticker = yf.Ticker(symbol)
            info = ticker.info
            history = ticker.history(period="2d")
            
            if history.empty:
                return None
            
            current_price = history['Close'].iloc[-1]
            prev_price = history['Close'].iloc[-2] if len(history) > 1 else current_price
            price_change = current_price - prev_price
            price_change_pct = (price_change / prev_price * 100) if prev_price != 0 else 0
            
            return PriceData(
                symbol=symbol.upper(),
                price=Decimal(str(current_price)),
                price_change_24h=Decimal(str(price_change)),
                price_change_percentage_24h=Decimal(str(price_change_pct)),
                market_cap=Decimal(str(info.get("marketCap", 0))),
                volume_24h=Decimal(str(history['Volume'].iloc[-1])),
                last_updated=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error fetching traditional price for {symbol}: {str(e)}")
            return None
    
    async def _get_crypto_historical(
        self, 
        symbol: str, 
        timeframe: TimeframeEnum
    ) -> Optional[HistoricalData]:
        """Get historical cryptocurrency data"""
        try:
            coin_id = ASSET_MAPPINGS["cryptocurrencies"].get(symbol.upper())
            if not coin_id:
                return None
            
            period_config = TIME_PERIODS[timeframe.value]
            days = period_config["days"]
            
            url = f"{DATA_SOURCES['coingecko']['base_url']}/coins/{coin_id}/market_chart"
            params = {
                "vs_currency": "usd",
                "days": days,
                "interval": period_config["interval"]
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    prices = data.get("prices", [])
                    volumes = data.get("total_volumes", [])
                    
                    historical_points = []
                    for i, (timestamp, price) in enumerate(prices):
                        volume = volumes[i][1] if i < len(volumes) else 0
                        
                        historical_points.append(
                            HistoricalPricePoint(
                                timestamp=datetime.fromtimestamp(timestamp / 1000),
                                close=Decimal(str(price)),
                                volume=Decimal(str(volume))
                            )
                        )
                    
                    return HistoricalData(
                        symbol=symbol.upper(),
                        timeframe=timeframe,
                        data=historical_points,
                        total_points=len(historical_points),
                        start_date=historical_points[0].timestamp if historical_points else datetime.utcnow(),
                        end_date=historical_points[-1].timestamp if historical_points else datetime.utcnow()
                    )
                    
        except Exception as e:
            logger.error(f"Error fetching crypto historical data for {symbol}: {str(e)}")
            return None
    
    async def _get_traditional_historical(
        self,
        symbol: str,
        timeframe: TimeframeEnum
    ) -> Optional[HistoricalData]:
        """Get historical traditional asset data"""
        try:
            period_config = TIME_PERIODS[timeframe.value]
            
            # Calculate start date
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_config["days"])
            
            ticker = yf.Ticker(symbol)
            history = ticker.history(
                start=start_date,
                end=end_date,
                interval="1d"  # Daily data for traditional assets
            )
            
            if history.empty:
                return None
            
            historical_points = []
            for index, row in history.iterrows():
                historical_points.append(
                    HistoricalPricePoint(
                        timestamp=index.to_pydatetime(),
                        open=Decimal(str(row['Open'])),
                        high=Decimal(str(row['High'])),
                        low=Decimal(str(row['Low'])),
                        close=Decimal(str(row['Close'])),
                        volume=Decimal(str(row['Volume']))
                    )
                )
            
            return HistoricalData(
                symbol=symbol.upper(),
                timeframe=timeframe,
                data=historical_points,
                total_points=len(historical_points),
                start_date=historical_points[0].timestamp if historical_points else datetime.utcnow(),
                end_date=historical_points[-1].timestamp if historical_points else datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error fetching traditional historical data for {symbol}: {str(e)}")
            return None
    
    async def get_market_summary(self, symbol: str, asset_type: AssetType) -> Optional[MarketSummary]:
        """Get comprehensive market summary for an asset"""
        try:
            if asset_type == AssetType.CRYPTOCURRENCY:
                return await self._get_crypto_summary(symbol)
            else:
                return await self._get_traditional_summary(symbol)
        except Exception as e:
            logger.error(f"Error fetching market summary for {symbol}: {str(e)}")
            return None
    
    async def _get_crypto_summary(self, symbol: str) -> Optional[MarketSummary]:
        """Get crypto market summary from CoinGecko"""
        try:
            coin_id = ASSET_MAPPINGS["cryptocurrencies"].get(symbol.upper())
            if not coin_id:
                return None
            
            url = f"{DATA_SOURCES['coingecko']['base_url']}/coins/{coin_id}"
            params = {
                "localization": "false",
                "tickers": "false",
                "market_data": "true",
                "community_data": "false",
                "developer_data": "false"
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    market_data = data.get("market_data", {})
                    
                    return MarketSummary(
                        symbol=symbol.upper(),
                        current_price=Decimal(str(market_data.get("current_price", {}).get("usd", 0))),
                        market_cap=Decimal(str(market_data.get("market_cap", {}).get("usd", 0))),
                        market_cap_rank=market_data.get("market_cap_rank"),
                        volume_24h=Decimal(str(market_data.get("total_volume", {}).get("usd", 0))),
                        price_change_24h=Decimal(str(market_data.get("price_change_24h", 0))),
                        price_change_percentage_24h=Decimal(str(market_data.get("price_change_percentage_24h", 0))),
                        price_change_7d=Decimal(str(market_data.get("price_change_percentage_7d", 0))),
                        price_change_30d=Decimal(str(market_data.get("price_change_percentage_30d", 0))),
                        high_24h=Decimal(str(market_data.get("high_24h", {}).get("usd", 0))),
                        low_24h=Decimal(str(market_data.get("low_24h", {}).get("usd", 0))),
                        ath=Decimal(str(market_data.get("ath", {}).get("usd", 0))),
                        ath_date=datetime.fromisoformat(market_data.get("ath_date", {}).get("usd", "").replace("Z", "+00:00")) if market_data.get("ath_date", {}).get("usd") else None,
                        atl=Decimal(str(market_data.get("atl", {}).get("usd", 0))),
                        atl_date=datetime.fromisoformat(market_data.get("atl_date", {}).get("usd", "").replace("Z", "+00:00")) if market_data.get("atl_date", {}).get("usd") else None
                    )
                    
        except Exception as e:
            logger.error(f"Error fetching crypto summary for {symbol}: {str(e)}")
            return None
    
    async def _get_traditional_summary(self, symbol: str) -> Optional[MarketSummary]:
        """Get traditional asset summary from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            history = ticker.history(period="30d")
            
            if history.empty:
                return None
            
            current_price = history['Close'].iloc[-1]
            
            # Calculate percentage changes
            price_change_24h = 0
            price_change_7d = 0
            price_change_30d = 0
            
            if len(history) > 1:
                price_change_24h = ((current_price - history['Close'].iloc[-2]) / history['Close'].iloc[-2] * 100)
            if len(history) > 7:
                price_change_7d = ((current_price - history['Close'].iloc[-8]) / history['Close'].iloc[-8] * 100)
            if len(history) > 1:
                price_change_30d = ((current_price - history['Close'].iloc[0]) / history['Close'].iloc[0] * 100)
            
            return MarketSummary(
                symbol=symbol.upper(),
                current_price=Decimal(str(current_price)),
                market_cap=Decimal(str(info.get("marketCap", 0))),
                volume_24h=Decimal(str(history['Volume'].iloc[-1])),
                price_change_percentage_24h=Decimal(str(price_change_24h)),
                price_change_7d=Decimal(str(price_change_7d)),
                price_change_30d=Decimal(str(price_change_30d)),
                high_24h=Decimal(str(history['High'].iloc[-1])),
                low_24h=Decimal(str(history['Low'].iloc[-1]))
            )
            
        except Exception as e:
            logger.error(f"Error fetching traditional summary for {symbol}: {str(e)}")
            return None


# Helper functions
async def fetch_multiple_assets_data(
    symbols: List[str],
    asset_types: Dict[str, AssetType],
    data_type: str = "price"
) -> Dict[str, Any]:
    """Fetch data for multiple assets concurrently"""
    async with DataCollector() as collector:
        if data_type == "price":
            return await collector.get_multiple_prices(symbols, asset_types)
        # Add other data types as needed
    
    return {}


def get_asset_type_from_symbol(symbol: str) -> AssetType:
    """Determine asset type from symbol"""
    symbol = symbol.upper()
    
    if symbol in ASSET_MAPPINGS["cryptocurrencies"]:
        return AssetType.CRYPTOCURRENCY
    elif symbol in ASSET_MAPPINGS["traditional"]:
        if symbol.startswith("^"):
            return AssetType.INDEX
        elif symbol in ["GLD", "SLV"]:
            return AssetType.COMMODITY
        else:
            return AssetType.ETF
    else:
        # Default guess based on symbol patterns
        if len(symbol) <= 4 and symbol.isalpha():
            return AssetType.STOCK
        else:
            return AssetType.CRYPTOCURRENCY