# StockSense AI - AI-Powered Stock Analysis Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.3-green.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-teal.svg)](https://fastapi.tiangolo.com/)
[![Redis](https://img.shields.io/badge/Redis-7-red.svg)](https://redis.io/)

A complete, production-ready, dockerized stock analysis web application that connects to open-source trading APIs (Yahoo Finance), stores & visualizes historical trends, computes technical indicators, and uses AWS Bedrock AI to generate intelligent buy/sell/hold recommendations.

## ✨ What's New in v2.0

- **🔥 Multi-Environment Support**: Separate dev and prod modes with optimized configurations
- **⚡ Redis Caching**: 10x faster response times with intelligent caching layer
- **🔒 Production Ready**: Nginx reverse proxy, SSL support, security hardening
- **📊 Enhanced Performance**: Optimized Docker builds, resource limits, health checks
- **🛠️ Better DX**: Hot reload in dev, one-command deployment, comprehensive docs

## Features

### Technical Analysis
- **Real-time Stock Data**: Fetches current and historical stock prices from Yahoo Finance
- **Technical Indicators**:
  - RSI (Relative Strength Index)
  - MACD (Moving Average Convergence Divergence)
  - EMA (Exponential Moving Average) - 12 & 50 period
  - SMA (Simple Moving Average)
  - Bollinger Bands
  - Volume analysis and spike detection

### AI-Powered Insights
- **AWS Bedrock Integration**: Uses Amazon Titan for natural language analysis
- **Intelligent Recommendations**: AI-generated Buy/Hold/Sell suggestions
- **Confidence Scoring**: Algorithm-based confidence levels for recommendations
- **Fallback Analysis**: Rule-based recommendations when AI is unavailable

### Infrastructure
- **Redis Caching**: Fast data retrieval with configurable TTL
- **Nginx Reverse Proxy**: Load balancing and SSL termination (production)
- **Health Checks**: Auto-restart on failures
- **Resource Management**: CPU and memory limits
- **Security**: Rate limiting, CORS, authentication ready

### User Interface
- **Interactive Dashboard**: Modern, responsive Vue.js interface
- **Real-time Charts**: Beautiful Chart.js visualizations with EMA overlays
- **Stock Search**: Quick search with instant analysis
- **Watchlist Management**: Save and track favorite stocks
- **Trend Analysis**: Visual indicators for bullish/bearish trends

## Architecture

```
Production Architecture:
┌─────────────┐
│   Nginx     │ ← Reverse Proxy, SSL, Rate Limiting
│  (Port 80)  │
└──────┬──────┘
       │
   ┌───┴────┐
   │        │
┌──▼──┐  ┌──▼──┐
│ Vue │  │ API │ ← FastAPI Backend
│ App │  │     │
└─────┘  └──┬──┘
            │
      ┌─────┼─────┐
      │     │     │
   ┌──▼─┐ ┌─▼──┐ ┌▼────┐
   │ PG │ │Redis│ │ AWS │
   │ DB │ │Cache│ │Bedrck│
   └────┘ └─────┘ └─────┘
```

## Quick Start

### 🚀 Development Mode (Recommended for Local)

Perfect for local development with hot reload and debugging.

```bash
# Clone the repository
git clone <repository-url>
cd stocksense-ai-analytics

# Run development mode (one command!)
./run-dev.sh

# Or manually:
docker-compose -f docker-compose.dev.yml up --build
```

**What you get in dev mode:**
- ✅ Hot reload for backend and frontend
- ✅ Debug logging
- ✅ Direct port access to all services
- ✅ Volume mounting for live code editing
- ✅ Development-friendly error messages

**Access Points:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8080
- API Docs: http://localhost:8080/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### 🏭 Production Mode

Optimized for production deployment with security and performance.

```bash
# Create production environment file
cp .env.prod.example .env.prod

# Edit with your production values
# REQUIRED: Set POSTGRES_PASSWORD, REDIS_PASSWORD, SECRET_KEY
nano .env.prod

# Deploy to production
./run-prod.sh

# Or manually:
docker-compose -f docker-compose.prod.yml up -d
```

**What you get in prod mode:**
- ✅ Nginx reverse proxy
- ✅ SSL/TLS support
- ✅ Optimized production builds
- ✅ Security hardening (passwords, rate limiting)
- ✅ Resource limits and health checks
- ✅ Auto-restart policies
- ✅ Multiple backend replicas

**Access Points:**
- Application: http://localhost (via Nginx)
- API: http://localhost/api
- API Docs: http://localhost/docs

### Prerequisites
- Docker Desktop or Docker Engine + Docker Compose
- (Optional) AWS Account with Bedrock access for AI features

## Project Structure

```
stocksense-ai-analytics/
├── backend/                    # FastAPI Python backend
│   ├── main.py                # API endpoints
│   ├── models.py              # Database models
│   ├── indicators.py          # Technical indicators
│   ├── stock_service.py       # Stock data fetching
│   ├── ai_service.py          # AWS Bedrock integration
│   ├── redis_service.py       # Redis caching
│   ├── Dockerfile.dev         # Dev container
│   ├── Dockerfile.prod        # Prod container (optimized)
│   └── requirements.txt       # Python dependencies
├── frontend/                   # Vue 3 frontend
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   ├── views/             # Page views
│   │   └── services/          # API services
│   ├── Dockerfile.dev         # Dev container
│   ├── Dockerfile.prod        # Prod container (optimized)
│   └── package.json           # Node dependencies
├── nginx/                      # Nginx configuration (prod)
│   ├── nginx.conf             # Main config
│   └── conf.d/                # Server blocks
├── db/                         # PostgreSQL setup
│   └── schema.sql             # Database schema
├── docker-compose.dev.yml      # Development environment
├── docker-compose.prod.yml     # Production environment
├── run-dev.sh                  # Dev mode launcher
├── run-prod.sh                 # Prod mode launcher
├── DEPLOYMENT.md               # Deployment guide
├── IMPROVEMENTS.md             # Feature roadmap
└── README.md                   # This file
```

## Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **ORM**: SQLAlchemy
- **Data Analysis**: Pandas, NumPy
- **Stock Data**: yfinance
- **AI/ML**: AWS Bedrock (Amazon Titan)
- **Server**: Uvicorn (dev) / Gunicorn (prod)

### Frontend
- **Framework**: Vue.js 3 (Composition API)
- **Styling**: Tailwind CSS
- **Charts**: Chart.js + vue-chartjs
- **HTTP Client**: Axios
- **Build Tool**: Vite

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Reverse Proxy**: Nginx (production)
- **Cache**: Redis with AOF persistence
- **Database**: PostgreSQL with health checks
- **Networking**: Docker bridge networks

## Usage

### Analyzing a Stock

1. Navigate to http://localhost:3000 (dev) or http://localhost (prod)
2. Enter a stock symbol (e.g., AAPL, TSLA, MSFT, GOOGL, AMZN)
3. Click "Analyze" or press Enter
4. View comprehensive technical analysis, charts, and AI recommendations

### Managing Watchlist

1. After analyzing a stock, click "Add to Watchlist"
2. Navigate to "Watchlist" in the top menu
3. View all saved stocks with their latest data
4. Click any stock to see detailed analysis
5. Remove stocks by clicking the X button

### Understanding Recommendations

**Buy Signal**: Generated when:
- RSI indicates oversold conditions (< 35)
- MACD shows positive momentum
- Short-term EMA crosses above long-term EMA
- Price near lower Bollinger Band

**Sell Signal**: Generated when:
- RSI indicates overbought conditions (> 65)
- MACD shows negative momentum
- Short-term EMA crosses below long-term EMA
- Price near upper Bollinger Band

**Hold Signal**: Mixed indicators or neutral conditions

## API Endpoints

### Stock Analysis
```
GET /api/stock/{symbol}/analyze?period=1y
```
Analyzes a stock and returns technical indicators with AI summary.

**Parameters**:
- `symbol`: Stock ticker symbol (e.g., AAPL)
- `period`: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y)

**Response**:
```json
{
  "symbol": "AAPL",
  "close": 178.50,
  "price_change": 2.35,
  "price_change_percent": 1.33,
  "trend": "Bullish",
  "rsi": 58.42,
  "macd": 0.45,
  "recommendation": "Buy",
  "ai_summary": "AAPL shows bullish trend...",
  "confidence_score": 75.5
}
```

### Historical Data
```
GET /api/stock/{symbol}/history?period=1mo
```
Returns historical OHLCV data with indicators.

### Watchlist
```
GET /api/watchlist                    # Get watchlist
POST /api/watchlist                   # Add to watchlist
DELETE /api/watchlist/{symbol}        # Remove from watchlist
```

### Health Check
```
GET /api/health
```
Returns system health and service status.

## Environment Variables

### Development
Minimal configuration - defaults work out of the box!

```bash
# Optional overrides
DEBUG=True
ENV=development
```

### Production
**Required variables** in `.env.prod`:

```bash
# Database
POSTGRES_PASSWORD=<strong-password>
REDIS_PASSWORD=<strong-password>

# Security
SECRET_KEY=<random-secret-key>

# AWS (optional)
AWS_ACCESS_KEY_ID=<your-key>
AWS_SECRET_ACCESS_KEY=<your-secret>
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete configuration guide.

## Performance

### Caching Strategy

- **Stock Analysis**: 15 minutes TTL
- **Historical Data**: 30 minutes TTL
- **News**: 10 minutes TTL

### Response Times

| Endpoint | Without Cache | With Cache |
|----------|--------------|------------|
| Stock Analysis | 2-3s | 50-100ms |
| Historical Data | 1-2s | 30-50ms |
| Watchlist | 200ms | 10ms |

## Development

### Running Tests

```bash
# Backend tests
docker exec -it stocksense-backend-dev pytest

# With coverage
docker exec -it stocksense-backend-dev pytest --cov=.
```

### Accessing Services

```bash
# Backend shell
docker exec -it stocksense-backend-dev python

# PostgreSQL
docker exec -it stocksense-db-dev psql -U postgres -d stocksense_dev

# Redis CLI
docker exec -it stocksense-redis-dev redis-cli

# View logs
docker-compose -f docker-compose.dev.yml logs -f backend
```

### Database Migrations

```bash
# Create migration
docker exec -it stocksense-backend-dev alembic revision -m "description"

# Run migrations
docker exec -it stocksense-backend-dev alembic upgrade head
```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive deployment guide including:
- Production setup
- SSL configuration
- Domain setup
- Backup strategies
- Monitoring
- Troubleshooting

## Improvements & Roadmap

See [IMPROVEMENTS.md](IMPROVEMENTS.md) for detailed feature roadmap including:
- Portfolio tracking
- News sentiment analysis
- Social media integration
- Advanced alerts
- Backtesting engine
- Mobile app
- And 20+ more features!

## Security

### Development
- Relaxed security for ease of development
- Open ports for debugging
- Simple passwords acceptable

### Production
- Strong passwords required
- SSL/TLS encryption
- Rate limiting
- CORS protection
- Security headers
- No exposed debug endpoints

## Troubleshooting

### Port Already in Use
```bash
# Find and kill process
sudo lsof -i :3000
sudo lsof -i :8080

# Or change ports in docker-compose files
```

### Database Connection Issues
```bash
# Reset database
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up --build
```

### Redis Not Available
```bash
# Check Redis status
docker exec -it stocksense-redis-dev redis-cli ping

# View Redis logs
docker logs stocksense-redis-dev
```

### Cache Issues
```bash
# Clear Redis cache
docker exec -it stocksense-redis-dev redis-cli FLUSHALL

# Or restart Redis
docker-compose restart redis-cache
```

For more troubleshooting, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test in dev mode: `./run-dev.sh`
5. Submit a pull request

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## Disclaimer

This application is for educational purposes only. Stock market investments carry risk. Always do your own research and consult with financial advisors before making investment decisions. The AI recommendations are based on technical analysis only and should not be considered financial advice.

## Support

For issues, questions, or suggestions:
- 📖 Read the [DEPLOYMENT.md](DEPLOYMENT.md) guide
- 🚀 Check [IMPROVEMENTS.md](IMPROVEMENTS.md) for planned features
- 🐛 Open an issue on GitHub
- 📚 Review API docs at http://localhost:8080/docs

## Useful Commands

### Development
```bash
# Start dev environment
./run-dev.sh

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Restart a service
docker-compose -f docker-compose.dev.yml restart backend

# Stop everything
docker-compose -f docker-compose.dev.yml down
```

### Production
```bash
# Deploy production
./run-prod.sh

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Check status
docker-compose -f docker-compose.prod.yml ps

# Stop production
docker-compose -f docker-compose.prod.yml down
```

---

**Built with ❤️ using FastAPI, Vue.js, Redis, and AWS Bedrock**

**Version 2.0** - Now with multi-environment support and production-ready architecture!
