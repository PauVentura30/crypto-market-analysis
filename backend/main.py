"""
CryptoAnalyzer Backend - FastAPI Application
Professional cryptocurrency and traditional market analysis API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import structlog
import uvicorn
from contextlib import asynccontextmanager

from core.config import get_settings
from api.routes import assets, analysis, correlations, portfolio

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting CryptoAnalyzer API...")
    
    # Startup logic
    settings = get_settings()
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    
    yield
    
    # Shutdown logic
    logger.info("🛑 Shutting down CryptoAnalyzer API...")


def create_application() -> FastAPI:
    """Create and configure FastAPI application"""
    settings = get_settings()
    
    app = FastAPI(
        title="CryptoAnalyzer API",
        description="""
        🚀 **Professional Cryptocurrency & Traditional Market Analysis API**
        
        A comprehensive platform for analyzing cryptocurrencies vs traditional markets with:
        
        - **Real-time market data** from multiple sources
        - **Advanced correlation analysis** between crypto and traditional assets  
        - **Portfolio management** with P&L tracking
        - **Technical indicators** and volatility metrics
        - **Multi-language support** (EN/ES)
        - **High-performance caching** for optimal response times
        
        Built with FastAPI, pandas, and modern async architecture.
        """,
        version="1.0.0",
        openapi_tags=[
            {
                "name": "assets",
                "description": "Asset data operations - prices, metadata, historical data"
            },
            {
                "name": "analysis", 
                "description": "Market analysis - technical indicators, performance metrics"
            },
            {
                "name": "correlations",
                "description": "Correlation analysis between different asset classes"
            },
            {
                "name": "portfolio",
                "description": "Portfolio management - positions, P&L, allocation"
            }
        ],
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan
    )
    
    # Middleware configuration
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Total-Count", "X-Page-Count"]
    )
    
    # Include routers
    app.include_router(
        assets.router,
        prefix="/api/v1/assets",
        tags=["assets"]
    )
    
    app.include_router(
        analysis.router,
        prefix="/api/v1/analysis",
        tags=["analysis"]
    )
    
    app.include_router(
        correlations.router,
        prefix="/api/v1/correlations", 
        tags=["correlations"]
    )
    
    app.include_router(
        portfolio.router,
        prefix="/api/v1/portfolio",
        tags=["portfolio"]
    )
    
    return app


# Create app instance
app = create_application()


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "🚀 CryptoAnalyzer API",
        "version": "1.0.0",
        "description": "Professional cryptocurrency and traditional market analysis",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "assets": "/api/v1/assets",
            "analysis": "/api/v1/analysis", 
            "correlations": "/api/v1/correlations",
            "portfolio": "/api/v1/portfolio"
        }
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2025-01-01T00:00:00Z",
        "version": "1.0.0"
    }


@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"The endpoint {request.url.path} was not found",
            "suggestion": "Check the API documentation at /docs"
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler"""
    logger.error(f"Internal server error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error", 
            "message": "An unexpected error occurred",
            "request_id": getattr(request.state, "request_id", "unknown")
        }
    )


if __name__ == "__main__":
    settings = get_settings()
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug",
        access_log=True,
        workers=1 if settings.debug else 4
    )