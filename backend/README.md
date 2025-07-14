# CryptoAnalyzer Backend API

Professional FastAPI backend for cryptocurrency and traditional market analysis with real-time data, correlations, and portfolio management.

## 🚀 Features

- **Real-time Market Data** from multiple sources (CoinGecko, Yahoo Finance)
- **Advanced Analysis** - Technical indicators, performance metrics, volatility analysis
- **Correlation Analysis** - Matrix calculations, rolling correlations, heatmaps
- **Portfolio Management** - Performance tracking, optimization, rebalancing
- **Professional Architecture** - Async/await, structured logging, error handling
- **Comprehensive API** - RESTful endpoints with OpenAPI documentation
- **High Performance** - Caching, rate limiting, concurrent data fetching

## 🛠️ Tech Stack

- **Framework**: FastAPI 0.104+
- **Data Processing**: pandas, numpy, scipy
- **Market Data**: yfinance, aiohttp for API calls
- **Analysis**: Custom financial calculations, TA-Lib integration
- **Async Support**: asyncio, aiohttp
- **Logging**: structlog with JSON formatting
- **Documentation**: Automatic OpenAPI/Swagger generation

## 📁 Project Structure

```
backend/
├── api/
│   ├── routes/
│   │   ├── assets.py        # Asset data endpoints
│   │   ├── analysis.py      # Market analysis endpoints
│   │   ├── correlations.py  # Correlation analysis
│   │   └── portfolio.py     # Portfolio management
│   └── deps.py              # API dependencies
├── core/
│   ├── config.py           # Application configuration
│   └── security.py         # Security utilities
├── models/
│   ├── asset.py            # Asset data models
│   ├── analysis.py         # Analysis models
│   └── portfolio.py        # Portfolio models
├── services/
│   ├── data_collector.py   # Market data collection
│   ├── analyzer.py         # Financial analysis
│   └── calculator.py       # Mathematical calculations
├── utils/
│   └── helpers.py          # Utility functions
├── main.py                 # Application entry point
├── requirements.txt        # Dependencies
└── README.md              # This file
```

## 🏃‍♂️ Quick Start

### Prerequisites

- Python 3.9+
- pip or poetry

### Installation

1. **Navigate to backend directory**:
   ```bash
   cd backend/
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables** (optional):
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start the server**:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Open API documentation**:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## 📊 API Endpoints

### Assets Endpoints (`/api/v1/assets`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all supported assets |
| GET | `/{symbol}/price` | Get current price |
| GET | `/{symbol}/historical` | Get historical data |
| GET | `/{symbol}/summary` | Get market summary |
| POST | `/prices` | Get multiple asset prices |
| POST | `/compare` | Compare multiple assets |
| GET | `/search` | Search assets |
| GET | `/categories` | Get asset categories |

### Analysis Endpoints (`/api/v1/analysis`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/performance` | Performance analysis |
| POST | `/volatility` | Volatility analysis |
| POST | `/technical` | Technical analysis |
| GET | `/market-overview` | Market overview |
| GET | `/trends` | Market trends analysis |

### Correlations Endpoints (`/api/v1/correlations`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/matrix` | Correlation matrix |
| POST | `/pairwise` | Pairwise correlation |
| GET | `/heatmap` | Heatmap data |
| GET | `/rolling/{symbol1}/{symbol2}` | Rolling correlation |

### Portfolio Endpoints (`/api/v1/portfolio`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/analyze` | Portfolio analysis |
| POST | `/optimize` | Portfolio optimization |
| POST | `/rebalance` | Rebalancing analysis |
| GET | `/performance/{symbol}` | Asset performance |

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Application
ENVIRONMENT=development
DEBUG=True
HOST=0.0.0.0
PORT=8000

# CORS
ALLOWED_HOSTS=["http://localhost:3000"]

# API Keys (optional)
ALPHA_VANTAGE_API_KEY=your_key_here
FINNHUB_API_KEY=your_key_here
POLYGON_API_KEY=your_key_here

# Cache
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=300

# Database (future)
DATABASE_URL=postgresql://user:password@localhost/cryptoanalyzer

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Supported Assets

The API supports:

**Cryptocurrencies:**
- Bitcoin (BTC), Ethereum (ETH), Cardano (ADA)
- Solana (SOL), Polkadot (DOT), Chainlink (LINK)
- And more...

**Traditional Markets:**
- ETFs: SPY, QQQ, VTI, VXUS, GLD, SLV
- Indices: S&P 500, NASDAQ, Dow Jones, FTSE, DAX, Nikkei
- Individual stocks via symbol

## 📈 Usage Examples

### Get Current Price

```bash
curl -X GET "http://localhost:8000/api/v1/assets/BTC/price"
```

### Historical Data

```bash
curl -X GET "http://localhost:8000/api/v1/assets/ETH/historical?timeframe=30d"
```

### Performance Analysis

```bash
curl -X POST "http://localhost:8000/api/v1/analysis/performance" \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["BTC", "ETH", "SPY"],
    "timeframe": "30d"
  }'
```

### Correlation Matrix

```bash
curl -X POST "http://localhost:8000/api/v1/correlations/matrix" \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["BTC", "ETH", "SPY", "GLD"],
    "timeframe": "90d"
  }'
```

### Portfolio Analysis

```bash
curl -X POST "http://localhost:8000/api/v1/portfolio/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "positions": [
      {"symbol": "BTC", "quantity": 0.5, "avg_cost": 40000},
      {"symbol": "ETH", "quantity": 10, "avg_cost": 2500}
    ],
    "timeframe": "30d"
  }'
```

## 🧪 Testing

### Run Tests

```bash
pytest tests/ -v
```

### Test Coverage

```bash
pytest --cov=. tests/
```

### Manual Testing

Use the interactive API documentation at `/docs` to test endpoints manually.

## 🔍 Data Sources

### Primary Sources

1. **CoinGecko API** - Cryptocurrency data
   - Real-time prices, market caps, volumes
   - Historical data with various intervals
   - Market summaries and metadata

2. **Yahoo Finance** - Traditional market data
   - Stock prices, ETF data, indices
   - Historical OHLCV data
   - Company fundamentals

### Backup Sources

- Alpha Vantage (with API key)
- Finnhub (with API key)
- Polygon.io (with API key)

## 📊 Analysis Features

### Technical Analysis

- **Moving Averages**: SMA, EMA
- **Momentum**: RSI, MACD
- **Volatility**: Bollinger Bands, ATR
- **Support/Resistance**: Automatic level detection

### Performance Metrics

- **Returns**: Total, annualized, risk-adjusted
- **Risk**: Volatility, VaR, CVaR, max drawdown
- **Ratios**: Sharpe, Calmar, Sortino
- **Beta**: Systematic risk vs market

### Correlation Analysis

- **Static Correlation**: Pearson correlation coefficient
- **Rolling Correlation**: Time-varying relationships
- **Correlation Matrix**: Multi-asset analysis
- **Stability Analysis**: Correlation consistency

### Portfolio Analytics

- **Performance**: Returns, risk, benchmarking
- **Allocation**: Current vs target weights
- **Optimization**: Modern Portfolio Theory
- **Rebalancing**: Trade recommendations

## 🚀 Performance Optimization

### Caching Strategy

- **Redis**: Price data, analysis results
- **TTL**: 5 minutes for real-time data
- **Invalidation**: Smart cache updates

### Async Operations

- **Concurrent Requests**: Multiple data sources
- **Connection Pooling**: Efficient HTTP clients
- **Background Tasks**: Heavy computations

### Rate Limiting

- **Per-IP Limits**: Prevent abuse
- **API Key Tiers**: Premium access
- **Graceful Degradation**: Fallback strategies

## 🔒 Security

### Input Validation

- **Pydantic Models**: Request/response validation
- **Type Safety**: Strict type checking
- **Sanitization**: SQL injection prevention

### Error Handling

- **Structured Logging**: Detailed error tracking
- **Custom Exceptions**: Meaningful error messages
- **Graceful Failures**: Service continuity

## 📝 Logging

### Log Levels

- **INFO**: Normal operations
- **WARNING**: Non-critical issues
- **ERROR**: Error conditions
- **DEBUG**: Detailed debugging

### Log Format

```json
{
  "timestamp": "2025-01-01T12:00:00Z",
  "level": "INFO",
  "logger": "data_collector",
  "message": "Fetched BTC price",
  "symbol": "BTC",
  "price": 45000.00,
  "source": "coingecko"
}
```

## 🚢 Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
  
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

### Production Deployment

- **ASGI Server**: Gunicorn with Uvicorn workers
- **Reverse Proxy**: Nginx for static files and SSL
- **Load Balancing**: Multiple API instances
- **Monitoring**: Health checks and metrics

## 🔧 Development

### Code Style

```bash
# Format code
black .

# Sort imports
isort .

# Lint code
flake8 .
```

### Pre-commit Hooks

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Development Guidelines

- Write tests for new features
- Follow PEP 8 style guidelines
- Add docstrings to functions
- Update documentation

## 📄 API Reference

Complete API documentation is available at:
- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI JSON**: `/openapi.json`

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Check virtual environment activation
2. **API Timeouts**: Verify internet connection and data sources
3. **Memory Issues**: Reduce analysis timeframes for large datasets
4. **Rate Limits**: Implement proper caching and request throttling

### Debug Mode

```bash
export DEBUG=True
export LOG_LEVEL=DEBUG
uvicorn main:app --reload --log-level debug
```

## 📈 Future Enhancements

- **WebSocket Support**: Real-time data streaming
- **Machine Learning**: Predictive analytics
- **Advanced Indicators**: Custom technical indicators
- **Backtesting Engine**: Strategy validation
- **Multi-Exchange Data**: Broader market coverage
- **Database Integration**: Persistent data storage
- **User Authentication**: Personal portfolios
- **API Monetization**: Premium features

## 📞 Support

- **Issues**: GitHub Issues
- **Documentation**: This README + API docs
- **Community**: Discussion forum

---

Built with ❤️ using FastAPI + Python + Modern Financial Analysis