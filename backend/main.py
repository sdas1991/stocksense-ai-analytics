"""
StockSense AI - FastAPI Backend
Main application file with API endpoints
"""
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from config import settings
from database import get_db, engine, Base
from models import StockSummary, Watchlist, StockSnapshot
from stock_service import StockService
from ai_service import AIService
from multi_source_provider import multi_source_provider
from redis_service import redis_service
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Stock Analysis Platform"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI service
ai_service = AIService()

# Create tables
Base.metadata.create_all(bind=engine)


# Pydantic models for request/response
class StockAnalysisResponse(BaseModel):
    symbol: str
    company_name: Optional[str] = None
    sector: Optional[str] = None
    close: float
    price_change: float
    price_change_percent: float
    trend: str
    rsi: float
    macd: float
    macd_signal: float
    macd_histogram: float
    ema_12: float
    ema_50: float
    bb_upper: float
    bb_middle: float
    bb_lower: float
    recommendation: str
    ai_summary: str
    confidence_score: float


class WatchlistItem(BaseModel):
    symbol: str
    notes: Optional[str] = None


class HistoricalDataPoint(BaseModel):
    date: str
    open: Optional[float]
    high: Optional[float]
    low: Optional[float]
    close: Optional[float]
    volume: Optional[int]
    rsi: Optional[float]
    macd: Optional[float]
    ema_short: Optional[float]
    ema_long: Optional[float]


# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "bedrock_available": ai_service.bedrock_available
    }


@app.get("/api/stock/{symbol}/analyze", response_model=StockAnalysisResponse)
async def analyze_stock(
    symbol: str,
    period: str = Query("1y", regex="^(1d|5d|1mo|3mo|6mo|1y|2y|5y)$"),
    db: Session = Depends(get_db)
):
    """
    Analyze a stock with technical indicators and AI summary
    """
    try:
        # Get analysis
        analysis = StockService.analyze_stock(symbol.upper(), period, db)

        if not analysis:
            raise HTTPException(status_code=404, detail=f"Stock {symbol} not found or no data available")

        # Generate AI summary
        ai_summary = ai_service.generate_summary(symbol.upper(), analysis)
        confidence_score = ai_service.calculate_confidence_score(analysis)

        # Update summary in database with AI analysis
        summary = db.query(StockSummary).filter(
            StockSummary.symbol == symbol.upper()
        ).first()

        if summary:
            summary.ai_summary = ai_summary
            summary.confidence_score = confidence_score
            db.commit()

        # Return response
        return StockAnalysisResponse(
            symbol=analysis['symbol'],
            company_name=analysis.get('company_name', symbol),
            sector=analysis.get('sector', 'N/A'),
            close=analysis['close'],
            price_change=analysis['price_change'],
            price_change_percent=analysis['price_change_percent'],
            trend=analysis['trend'],
            rsi=analysis['rsi'],
            macd=analysis['macd'],
            macd_signal=analysis['macd_signal'],
            macd_histogram=analysis['macd_histogram'],
            ema_12=analysis['ema_12'],
            ema_50=analysis['ema_50'],
            bb_upper=analysis['bb_upper'],
            bb_middle=analysis['bb_middle'],
            bb_lower=analysis['bb_lower'],
            recommendation=analysis['recommendation'],
            ai_summary=ai_summary,
            confidence_score=confidence_score
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing stock {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stock/{symbol}/history")
async def get_stock_history(
    symbol: str,
    period: str = Query("1y", regex="^(1d|1w|1mo|3mo|6mo|1y)$"),
    db: Session = Depends(get_db)
):
    """
    Get historical stock data with indicators
    """
    try:
        # Try to get from database first
        historical_data = StockService.get_historical_data(symbol.upper(), period, db)

        # If no data in DB, fetch and analyze
        if not historical_data:
            StockService.analyze_stock(symbol.upper(), period, db)
            historical_data = StockService.get_historical_data(symbol.upper(), period, db)

        if not historical_data:
            raise HTTPException(status_code=404, detail=f"No historical data found for {symbol}")

        return {
            "symbol": symbol.upper(),
            "period": period,
            "data": historical_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting history for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stock/{symbol}/summary")
async def get_stock_summary(symbol: str, db: Session = Depends(get_db)):
    """
    Get cached stock summary
    """
    try:
        summary = db.query(StockSummary).filter(
            StockSummary.symbol == symbol.upper()
        ).first()

        if not summary:
            raise HTTPException(status_code=404, detail=f"No summary found for {symbol}. Try analyzing it first.")

        return {
            "symbol": summary.symbol,
            "last_price": float(summary.last_price) if summary.last_price else None,
            "price_change": float(summary.price_change) if summary.price_change else None,
            "price_change_percent": float(summary.price_change_percent) if summary.price_change_percent else None,
            "trend": summary.current_trend,
            "rsi": float(summary.current_rsi) if summary.current_rsi else None,
            "macd": float(summary.current_macd) if summary.current_macd else None,
            "recommendation": summary.recommendation,
            "ai_summary": summary.ai_summary,
            "confidence_score": float(summary.confidence_score) if summary.confidence_score else None,
            "updated_at": summary.updated_at.isoformat() if summary.updated_at else None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting summary for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/trends")
async def get_trends(db: Session = Depends(get_db)):
    """
    Get trending stocks based on recent analysis
    """
    try:
        summaries = db.query(StockSummary).order_by(
            StockSummary.updated_at.desc()
        ).limit(10).all()

        return {
            "trends": [
                {
                    "symbol": s.symbol,
                    "trend": s.current_trend,
                    "recommendation": s.recommendation,
                    "price_change_percent": float(s.price_change_percent) if s.price_change_percent else 0,
                    "updated_at": s.updated_at.isoformat() if s.updated_at else None
                }
                for s in summaries
            ]
        }

    except Exception as e:
        logger.error(f"Error getting trends: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/watchlist")
async def get_watchlist(db: Session = Depends(get_db)):
    """
    Get user's watchlist
    """
    try:
        items = db.query(Watchlist).order_by(Watchlist.added_at.desc()).all()

        watchlist_data = []
        for item in items:
            # Get latest summary if available
            summary = db.query(StockSummary).filter(
                StockSummary.symbol == item.symbol
            ).first()

            watchlist_data.append({
                "symbol": item.symbol,
                "notes": item.notes,
                "added_at": item.added_at.isoformat(),
                "last_price": float(summary.last_price) if summary and summary.last_price else None,
                "price_change_percent": float(summary.price_change_percent) if summary and summary.price_change_percent else None,
                "trend": summary.current_trend if summary else None,
                "recommendation": summary.recommendation if summary else None
            })

        return {"watchlist": watchlist_data}

    except Exception as e:
        logger.error(f"Error getting watchlist: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/watchlist")
async def add_to_watchlist(item: WatchlistItem, db: Session = Depends(get_db)):
    """
    Add stock to watchlist
    """
    try:
        # Check if already exists
        existing = db.query(Watchlist).filter(
            Watchlist.symbol == item.symbol.upper()
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="Stock already in watchlist")

        # Add to watchlist
        watchlist_item = Watchlist(
            symbol=item.symbol.upper(),
            notes=item.notes
        )
        db.add(watchlist_item)
        db.commit()
        db.refresh(watchlist_item)

        return {
            "message": "Added to watchlist",
            "symbol": watchlist_item.symbol
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding to watchlist: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/watchlist/{symbol}")
async def remove_from_watchlist(symbol: str, db: Session = Depends(get_db)):
    """
    Remove stock from watchlist
    """
    try:
        item = db.query(Watchlist).filter(
            Watchlist.symbol == symbol.upper()
        ).first()

        if not item:
            raise HTTPException(status_code=404, detail="Stock not in watchlist")

        db.delete(item)
        db.commit()

        return {"message": "Removed from watchlist", "symbol": symbol.upper()}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing from watchlist: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """
    Health check for monitoring
    """
    redis_stats = redis_service.get_stats()

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": "connected",
            "redis": "connected" if redis_stats.get("enabled") else "unavailable",
            "bedrock": "available" if ai_service.bedrock_available else "fallback"
        },
        "cache_stats": redis_stats
    }


# NEW ENDPOINTS - Multi-source data features


@app.get("/api/market/movers")
async def get_market_movers():
    """
    Get market gainers, losers, and most active stocks
    """
    try:
        movers = multi_source_provider.get_market_movers()

        if not movers:
            raise HTTPException(status_code=503, detail="Market movers data temporarily unavailable")

        return movers

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting market movers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/market/overview")
async def get_market_overview():
    """
    Get market overview with major indices and statistics
    """
    try:
        # Get quotes for major indices
        indices = ['SPY', 'QQQ', 'DIA', '^VIX']  # S&P 500, NASDAQ, Dow Jones, VIX
        overview = {
            'indices': {},
            'timestamp': datetime.utcnow().isoformat()
        }

        for symbol in indices:
            quote = multi_source_provider.get_stock_quote(symbol)
            if quote:
                overview['indices'][symbol] = {
                    'price': quote.get('price'),
                    'change': quote.get('change'),
                    'change_percent': quote.get('change_percent')
                }

        # Get market movers
        movers = multi_source_provider.get_market_movers()
        if movers:
            overview['movers'] = {
                'gainers_count': len(movers.get('gainers', [])),
                'losers_count': len(movers.get('losers', [])),
                'top_gainers': movers.get('gainers', [])[:5],
                'top_losers': movers.get('losers', [])[:5]
            }

        return overview

    except Exception as e:
        logger.error(f"Error getting market overview: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/search/{query}")
async def search_symbols(query: str):
    """
    Search for stock symbols across multiple providers
    """
    try:
        if len(query) < 1:
            raise HTTPException(status_code=400, detail="Query must be at least 1 character")

        results = multi_source_provider.search_symbols(query)

        if not results:
            return {"results": [], "count": 0}

        return {
            "results": results,
            "count": len(results),
            "query": query
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching symbols: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stock/{symbol}/news")
async def get_company_news(symbol: str, days: int = Query(7, ge=1, le=30)):
    """
    Get company news for a symbol
    """
    try:
        news = multi_source_provider.get_company_news(symbol, days)

        if not news:
            return {"news": [], "count": 0, "symbol": symbol}

        return {
            "news": news,
            "count": len(news),
            "symbol": symbol,
            "days": days
        }

    except Exception as e:
        logger.error(f"Error getting news for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/providers/status")
async def get_providers_status():
    """
    Get status of all data providers (rate limits, availability)
    """
    try:
        status = multi_source_provider.get_provider_stats()

        return {
            "providers": status,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting provider status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stock/{symbol}/quote")
async def get_stock_quote(symbol: str):
    """
    Get real-time quote for a symbol using multi-source provider
    """
    try:
        quote = multi_source_provider.get_stock_quote(symbol.upper())

        if not quote:
            raise HTTPException(status_code=404, detail=f"Could not fetch quote for {symbol}")

        return quote

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting quote for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
