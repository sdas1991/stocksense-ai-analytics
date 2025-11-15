# StockSense AI - AI-Powered Stock Analysis Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.3-green.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-teal.svg)](https://fastapi.tiangolo.com/)

A complete, dockerized stock analysis web application that connects to open-source trading APIs (Yahoo Finance), stores & visualizes historical trends, computes technical indicators, and uses AWS Bedrock AI to generate intelligent buy/sell/hold recommendations.

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

### User Interface
- **Interactive Dashboard**: Modern, responsive Vue.js interface
- **Real-time Charts**: Beautiful Chart.js visualizations with EMA overlays
- **Stock Search**: Quick search with instant analysis
- **Watchlist Management**: Save and track favorite stocks
- **Trend Analysis**: Visual indicators for bullish/bearish trends

## Architecture

```
stocksense-ai/
├── backend/          # FastAPI Python backend
│   ├── main.py              # API endpoints
│   ├── models.py            # Database models
│   ├── indicators.py        # Technical indicators calculation
│   ├── stock_service.py     # Stock data fetching
│   ├── ai_service.py        # AWS Bedrock integration
│   └── requirements.txt     # Python dependencies
├── frontend/         # Vue 3 frontend
│   ├── src/
│   │   ├── components/      # Reusable components
│   │   ├── views/           # Page views
│   │   └── services/        # API services
│   └── package.json         # Node dependencies
├── db/               # PostgreSQL setup
│   └── schema.sql           # Database schema
└── docker-compose.yml       # Docker orchestration
```

## Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy
- **Data Analysis**: Pandas, NumPy
- **Stock Data**: yfinance
- **AI/ML**: AWS Bedrock (Amazon Titan)

### Frontend
- **Framework**: Vue.js 3 (Composition API)
- **Styling**: Tailwind CSS
- **Charts**: Chart.js + vue-chartjs
- **HTTP Client**: Axios
- **Build Tool**: Vite

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Database**: PostgreSQL with persistent volumes
- **Networking**: Docker bridge network

## Quick Start

### Prerequisites
- Docker Desktop or Docker Engine + Docker Compose
- (Optional) AWS Account with Bedrock access for AI features

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd stocksense-ai-analytics
```

2. **(Optional) Configure AWS Bedrock**

If you want to use AI-powered recommendations, set up AWS credentials:

```bash
# Edit docker-compose.yml and uncomment AWS environment variables
# Or create backend/.env file:
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
```

3. **Start the application**
```bash
docker-compose up --build
```

Wait for all services to start (this may take a few minutes on first run).

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8080
- API Documentation: http://localhost:8080/docs

## Usage

### Analyzing a Stock

1. Navigate to http://localhost:3000
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

### Trends
```
GET /api/trends
```
Returns recently analyzed stocks with trends.

## Database Schema

### stock_snapshot
Stores historical stock data with computed indicators:
- OHLCV data (Open, High, Low, Close, Volume)
- Technical indicators (RSI, MACD, EMA, Bollinger Bands)
- Trend analysis
- Timestamps

### stock_summary
Caches latest analysis for each stock:
- Current price and changes
- Latest indicators
- AI recommendation and summary
- Confidence score

### watchlist
User's saved stocks:
- Symbol
- Notes
- Add date

## AWS Bedrock Configuration

### Setting up AWS Bedrock

1. **Create IAM User**
   - Go to AWS Console → IAM
   - Create new user: `stocksense-ai-user`
   - Attach policy: `AmazonBedrockFullAccess`
   - Generate access keys

2. **Enable Bedrock Models**
   - Go to AWS Console → Bedrock
   - Request access to Amazon Titan models
   - Wait for approval (usually instant)

3. **Configure Application**
   ```bash
   # In docker-compose.yml, uncomment and set:
   AWS_ACCESS_KEY_ID: your_access_key_here
   AWS_SECRET_ACCESS_KEY: your_secret_key_here
   AWS_REGION: us-east-1
   ```

4. **Restart Services**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

**Note**: The application works without AWS Bedrock using rule-based recommendations. AI features are optional.

## Development

### Running Locally (without Docker)

**Backend**:
```bash
cd backend
pip install -r requirements.txt
# Set up PostgreSQL database
# Update DATABASE_URL in config.py
uvicorn main:app --reload --port 8080
```

**Frontend**:
```bash
cd frontend
npm install
npm run dev
```

### Database Migrations

Connect to PostgreSQL:
```bash
docker exec -it stocksense-db psql -U postgres -d stocksense
```

View tables:
```sql
\dt
SELECT * FROM stock_summary;
```

## Troubleshooting

### Port Already in Use
```bash
# Change ports in docker-compose.yml
ports:
  - "3001:3000"  # Frontend
  - "8081:8080"  # Backend
  - "5433:5432"  # Database
```

### Database Connection Issues
```bash
# Reset database
docker-compose down -v
docker-compose up --build
```

### Frontend Not Loading
```bash
# Rebuild frontend
docker-compose up --build frontend
```

### API Errors
```bash
# View backend logs
docker-compose logs -f backend
```

## Performance Optimization

- **Caching**: Stock data is cached in PostgreSQL (60-minute expiry)
- **Rate Limiting**: Yahoo Finance has rate limits; data is stored locally
- **Async Operations**: FastAPI handles requests asynchronously
- **Database Indexing**: Optimized queries with proper indexes

## Security Considerations

- Never commit AWS credentials to git
- Use environment variables for sensitive data
- PostgreSQL password should be changed in production
- Enable HTTPS in production deployment
- Implement rate limiting for public APIs

## Future Enhancements

- [ ] Portfolio tracking with ROI calculation
- [ ] Email/SMS alerts for price thresholds
- [ ] News sentiment analysis integration
- [ ] Multi-timeframe analysis
- [ ] Export reports to PDF
- [ ] Backtesting strategies
- [ ] Social sentiment from Reddit/Twitter
- [ ] Sector comparison tools

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Disclaimer

This application is for educational purposes only. Stock market investments carry risk. Always do your own research and consult with financial advisors before making investment decisions. The AI recommendations are based on technical analysis only and should not be considered financial advice.

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review API docs at http://localhost:8080/docs

---

**Built with ❤️ using FastAPI, Vue.js, and AWS Bedrock**
