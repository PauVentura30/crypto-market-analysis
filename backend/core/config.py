"""
Application configuration using Pydantic Settings
"""

from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # App settings
    app_name: str = "CryptoAnalyzer API"
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    
    # Server settings
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # CORS settings
    allowed_hosts: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173"],
        env="ALLOWED_HOSTS"
    )
    
    # API Keys (for external data sources)
    alpha_vantage_api_key: Optional[str] = Field(default=None, env="ALPHA_VANTAGE_API_KEY")
    finnhub_api_key: Optional[str] = Field(default=None, env="FINNHUB_API_KEY")
    polygon_api_key: Optional[str] = Field(default=None, env="POLYGON_API_KEY")
    
    # Cache settings
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    cache_ttl: int = Field(default=300, env="CACHE_TTL")  # 5 minutes
    
    # Database settings (for future use)
    database_url: str = Field(
        default="postgresql://user:password@localhost/cryptoanalyzer",
        env="DATABASE_URL"
    )
    
    # Rate limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")  # seconds
    
    # Data source settings
    default_vs_currency: str = Field(default="usd", env="DEFAULT_VS_CURRENCY")
    max_historical_days: int = Field(default=365, env="MAX_HISTORICAL_DAYS")
    
    # Analysis settings
    correlation_window: int = Field(default=30, env="CORRELATION_WINDOW")  # days
    volatility_window: int = Field(default=30, env="VOLATILITY_WINDOW")  # days
    
    # Supported assets
    supported_cryptocurrencies: List[str] = Field(
        default=[
            "bitcoin", "ethereum", "cardano", "solana", "polkadot",
            "chainlink", "litecoin", "bitcoin-cash", "stellar", "dogecoin"
        ],
        env="SUPPORTED_CRYPTOCURRENCIES"
    )
    
    supported_traditional_assets: List[str] = Field(
        default=[
            "SPY", "QQQ", "VTI", "VXUS", "GLD", "SLV", 
            "DJI", "^GSPC", "^IXIC", "^FTSE", "^GDAXI", "^N225"
        ],
        env="SUPPORTED_TRADITIONAL_ASSETS"
    )
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    # Security (for future auth implementation)
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Asset mappings for different data sources
ASSET_MAPPINGS = {
    "cryptocurrencies": {
        "BTC": "bitcoin",
        "ETH": "ethereum", 
        "ADA": "cardano",
        "SOL": "solana",
        "DOT": "polkadot",
        "LINK": "chainlink",
        "LTC": "litecoin",
        "BCH": "bitcoin-cash",
        "XLM": "stellar",
        "DOGE": "dogecoin"
    },
    "traditional": {
        "SPY": "SPY",  # S&P 500 ETF
        "QQQ": "QQQ",  # NASDAQ ETF
        "VTI": "VTI",  # Total Stock Market ETF
        "VXUS": "VXUS",  # International Stocks ETF
        "GLD": "GLD",  # Gold ETF
        "SLV": "SLV",  # Silver ETF
        "SP500": "^GSPC",  # S&P 500 Index
        "NASDAQ": "^IXIC",  # NASDAQ Index
        "DJI": "^DJI",  # Dow Jones Index
        "FTSE": "^FTSE",  # FTSE 100
        "DAX": "^GDAXI",  # DAX
        "NIKKEI": "^N225"  # Nikkei 225
    }
}

# API endpoints for different data sources
DATA_SOURCES = {
    "coingecko": {
        "base_url": "https://api.coingecko.com/api/v3",
        "endpoints": {
            "price": "/simple/price",
            "historical": "/coins/{id}/history",
            "market_data": "/coins/{id}/market_chart"
        }
    },
    "yahoo_finance": {
        "base_url": "https://query1.finance.yahoo.com/v8/finance",
        "endpoints": {
            "quote": "/quote",
            "historical": "/chart/{symbol}"
        }
    },
    "alpha_vantage": {
        "base_url": "https://www.alphavantage.co/query",
        "rate_limit": 5  # requests per minute
    }
}

# Time period mappings
TIME_PERIODS = {
    "1d": {"days": 1, "interval": "1h"},
    "7d": {"days": 7, "interval": "4h"}, 
    "30d": {"days": 30, "interval": "1d"},
    "90d": {"days": 90, "interval": "1d"},
    "365d": {"days": 365, "interval": "1d"},
    "max": {"days": 1000, "interval": "1d"}
}