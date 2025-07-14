"""
Pydantic models for asset data
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from decimal import Decimal
from enum import Enum


class AssetType(str, Enum):
    """Asset type enumeration"""
    CRYPTOCURRENCY = "cryptocurrency"
    STOCK = "stock" 
    ETF = "etf"
    INDEX = "index"
    COMMODITY = "commodity"
    FOREX = "forex"


class TimeframeEnum(str, Enum):
    """Available timeframes"""
    ONE_DAY = "1d"
    SEVEN_DAYS = "7d"
    THIRTY_DAYS = "30d"
    NINETY_DAYS = "90d"
    ONE_YEAR = "365d"
    MAX = "max"


class AssetInfo(BaseModel):
    """Basic asset information"""
    symbol: str = Field(..., description="Asset symbol (e.g., BTC, ETH, SPY)")
    name: str = Field(..., description="Asset full name")
    asset_type: AssetType = Field(..., description="Type of asset")
    category: Optional[str] = Field(None, description="Asset category")
    description: Optional[str] = Field(None, description="Asset description")
    website: Optional[str] = Field(None, description="Official website")
    logo_url: Optional[str] = Field(None, description="Asset logo URL")
    
    @validator('symbol')
    def symbol_uppercase(cls, v):
        return v.upper()


class PriceData(BaseModel):
    """Current price data for an asset"""
    symbol: str = Field(..., description="Asset symbol")
    price: Decimal = Field(..., description="Current price in USD")
    price_change_24h: Optional[Decimal] = Field(None, description="24h price change")
    price_change_percentage_24h: Optional[Decimal] = Field(None, description="24h price change %")
    market_cap: Optional[Decimal] = Field(None, description="Market capitalization")
    volume_24h: Optional[Decimal] = Field(None, description="24h trading volume")
    circulating_supply: Optional[Decimal] = Field(None, description="Circulating supply")
    total_supply: Optional[Decimal] = Field(None, description="Total supply")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v) if v else None
        }


class HistoricalPricePoint(BaseModel):
    """Single historical price point"""
    timestamp: datetime = Field(..., description="Price timestamp")
    open: Optional[Decimal] = Field(None, description="Opening price")
    high: Optional[Decimal] = Field(None, description="High price")
    low: Optional[Decimal] = Field(None, description="Low price")
    close: Decimal = Field(..., description="Closing price")
    volume: Optional[Decimal] = Field(None, description="Trading volume")
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v) if v else None
        }


class HistoricalData(BaseModel):
    """Historical price data for an asset"""
    symbol: str = Field(..., description="Asset symbol")
    timeframe: TimeframeEnum = Field(..., description="Data timeframe")
    data: List[HistoricalPricePoint] = Field(..., description="Historical price points")
    total_points: int = Field(..., description="Total number of data points")
    start_date: datetime = Field(..., description="Start date of data")
    end_date: datetime = Field(..., description="End date of data")


class MarketSummary(BaseModel):
    """Market summary statistics"""
    symbol: str = Field(..., description="Asset symbol")
    current_price: Decimal = Field(..., description="Current price")
    market_cap: Optional[Decimal] = Field(None, description="Market cap")
    market_cap_rank: Optional[int] = Field(None, description="Market cap rank")
    volume_24h: Optional[Decimal] = Field(None, description="24h volume")
    price_change_24h: Optional[Decimal] = Field(None, description="24h change")
    price_change_percentage_24h: Optional[Decimal] = Field(None, description="24h change %")
    price_change_7d: Optional[Decimal] = Field(None, description="7d change %")
    price_change_30d: Optional[Decimal] = Field(None, description="30d change %")
    high_24h: Optional[Decimal] = Field(None, description="24h high")
    low_24h: Optional[Decimal] = Field(None, description="24h low")
    ath: Optional[Decimal] = Field(None, description="All-time high")
    ath_date: Optional[datetime] = Field(None, description="ATH date")
    atl: Optional[Decimal] = Field(None, description="All-time low")
    atl_date: Optional[datetime] = Field(None, description="ATL date")
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v) if v else None
        }


class AssetListItem(BaseModel):
    """Asset list item for search/browse endpoints"""
    symbol: str = Field(..., description="Asset symbol")
    name: str = Field(..., description="Asset name")
    asset_type: AssetType = Field(..., description="Asset type")
    current_price: Optional[Decimal] = Field(None, description="Current price")
    market_cap: Optional[Decimal] = Field(None, description="Market cap")
    volume_24h: Optional[Decimal] = Field(None, description="24h volume")
    price_change_percentage_24h: Optional[Decimal] = Field(None, description="24h change %")
    logo_url: Optional[str] = Field(None, description="Asset logo")
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v) if v else None
        }


class AssetSearchRequest(BaseModel):
    """Asset search request"""
    query: str = Field(..., min_length=1, max_length=100, description="Search query")
    asset_types: Optional[List[AssetType]] = Field(None, description="Filter by asset types")
    limit: int = Field(default=20, ge=1, le=100, description="Number of results")
    
    @validator('query')
    def query_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()


class AssetComparisonRequest(BaseModel):
    """Request for comparing multiple assets"""
    symbols: List[str] = Field(..., min_items=2, max_items=10, description="Asset symbols to compare")
    timeframe: TimeframeEnum = Field(default=TimeframeEnum.THIRTY_DAYS, description="Comparison timeframe")
    vs_currency: str = Field(default="usd", description="Base currency for comparison")
    
    @validator('symbols')
    def symbols_uppercase(cls, v):
        return [symbol.upper() for symbol in v]


class AssetResponse(BaseModel):
    """Standard asset response wrapper"""
    success: bool = Field(default=True)
    data: Optional[Any] = Field(None)
    message: Optional[str] = Field(None)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = Field(None)


class PaginatedAssetResponse(BaseModel):
    """Paginated asset response"""
    success: bool = Field(default=True)
    data: List[AssetListItem] = Field(default_factory=list)
    total: int = Field(default=0)
    page: int = Field(default=1)
    per_page: int = Field(default=20)
    total_pages: int = Field(default=0)
    has_next: bool = Field(default=False)
    has_prev: bool = Field(default=False)
    timestamp: datetime = Field(default_factory=datetime.utcnow)