"""
Stock data fetching and analysis service
Uses yfinance to fetch stock data and compute indicators
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from models import StockSnapshot, StockSummary
from indicators import calculate_all_indicators, get_latest_analysis
import logging

logger = logging.getLogger(__name__)


class StockService:
    """Service for fetching and analyzing stock data"""

    @staticmethod
    def fetch_stock_data(symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """
        Fetch stock data from Yahoo Finance
        Periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        """
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)

            if df.empty:
                logger.warning(f"No data found for symbol: {symbol}")
                return None

            # Reset index to make Date a column
            df.reset_index(inplace=True)

            return df

        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None

    @staticmethod
    def get_stock_info(symbol: str) -> Optional[dict]:
        """Get stock info (company name, sector, etc.)"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 0),
                'currency': info.get('currency', 'USD')
            }
        except Exception as e:
            logger.error(f"Error fetching info for {symbol}: {str(e)}")
            return None

    @staticmethod
    def analyze_stock(symbol: str, period: str = "1y", db: Session = None) -> Optional[dict]:
        """
        Fetch stock data, calculate indicators, and return analysis
        Optionally stores data in database
        """
        # Fetch data
        df = StockService.fetch_stock_data(symbol, period)
        if df is None or df.empty:
            return None

        # Calculate indicators
        df = calculate_all_indicators(df)

        # Get latest analysis
        analysis = get_latest_analysis(df)
        analysis['symbol'] = symbol.upper()

        # Get stock info
        info = StockService.get_stock_info(symbol)
        if info:
            analysis['company_name'] = info.get('name', symbol)
            analysis['sector'] = info.get('sector', 'N/A')

        # Store in database if session provided
        if db:
            try:
                StockService.store_snapshots(symbol, df, db)
                StockService.update_summary(symbol, analysis, db)
            except Exception as e:
                logger.error(f"Error storing data for {symbol}: {str(e)}")

        return analysis

    @staticmethod
    def store_snapshots(symbol: str, df: pd.DataFrame, db: Session):
        """Store historical snapshots in database"""
        try:
            # Get the last 90 days of data to store
            recent_df = df.tail(90)

            for _, row in recent_df.iterrows():
                # Check if snapshot already exists
                existing = db.query(StockSnapshot).filter(
                    StockSnapshot.symbol == symbol.upper(),
                    StockSnapshot.date == row['Date']
                ).first()

                if not existing:
                    snapshot = StockSnapshot(
                        symbol=symbol.upper(),
                        date=row['Date'],
                        open=float(row['Open']),
                        high=float(row['High']),
                        low=float(row['Low']),
                        close=float(row['Close']),
                        volume=int(row['Volume']),
                        rsi=float(row['RSI']) if not pd.isna(row['RSI']) else None,
                        ema_short=float(row['EMA_12']) if not pd.isna(row['EMA_12']) else None,
                        ema_long=float(row['EMA_50']) if not pd.isna(row['EMA_50']) else None,
                        macd=float(row['MACD']) if not pd.isna(row['MACD']) else None,
                        macd_signal=float(row['MACD_Signal']) if not pd.isna(row['MACD_Signal']) else None,
                        macd_histogram=float(row['MACD_Histogram']) if not pd.isna(row['MACD_Histogram']) else None,
                        bb_upper=float(row['BB_Upper']) if not pd.isna(row['BB_Upper']) else None,
                        bb_middle=float(row['BB_Middle']) if not pd.isna(row['BB_Middle']) else None,
                        bb_lower=float(row['BB_Lower']) if not pd.isna(row['BB_Lower']) else None
                    )
                    db.add(snapshot)

            db.commit()
            logger.info(f"Stored snapshots for {symbol}")

        except Exception as e:
            db.rollback()
            logger.error(f"Error storing snapshots: {str(e)}")
            raise

    @staticmethod
    def update_summary(symbol: str, analysis: dict, db: Session):
        """Update or create stock summary"""
        try:
            summary = db.query(StockSummary).filter(
                StockSummary.symbol == symbol.upper()
            ).first()

            if summary:
                summary.last_price = analysis.get('close')
                summary.price_change = analysis.get('price_change')
                summary.price_change_percent = analysis.get('price_change_percent')
                summary.current_trend = analysis.get('trend')
                summary.current_rsi = analysis.get('rsi')
                summary.current_macd = analysis.get('macd')
                summary.recommendation = analysis.get('recommendation')
                summary.updated_at = datetime.utcnow()
            else:
                summary = StockSummary(
                    symbol=symbol.upper(),
                    last_price=analysis.get('close'),
                    price_change=analysis.get('price_change'),
                    price_change_percent=analysis.get('price_change_percent'),
                    current_trend=analysis.get('trend'),
                    current_rsi=analysis.get('rsi'),
                    current_macd=analysis.get('macd'),
                    recommendation=analysis.get('recommendation')
                )
                db.add(summary)

            db.commit()
            logger.info(f"Updated summary for {symbol}")

        except Exception as e:
            db.rollback()
            logger.error(f"Error updating summary: {str(e)}")
            raise

    @staticmethod
    def get_historical_data(symbol: str, period: str, db: Session) -> List[dict]:
        """Get historical data from database"""
        try:
            # Calculate date range based on period
            end_date = datetime.utcnow()
            if period == "1d":
                start_date = end_date - timedelta(days=1)
            elif period == "1w":
                start_date = end_date - timedelta(weeks=1)
            elif period == "1mo":
                start_date = end_date - timedelta(days=30)
            elif period == "3mo":
                start_date = end_date - timedelta(days=90)
            elif period == "6mo":
                start_date = end_date - timedelta(days=180)
            elif period == "1y":
                start_date = end_date - timedelta(days=365)
            else:
                start_date = end_date - timedelta(days=365)

            snapshots = db.query(StockSnapshot).filter(
                StockSnapshot.symbol == symbol.upper(),
                StockSnapshot.date >= start_date
            ).order_by(StockSnapshot.date.asc()).all()

            return [
                {
                    'date': s.date.isoformat(),
                    'open': float(s.open) if s.open else None,
                    'high': float(s.high) if s.high else None,
                    'low': float(s.low) if s.low else None,
                    'close': float(s.close) if s.close else None,
                    'volume': int(s.volume) if s.volume else None,
                    'rsi': float(s.rsi) if s.rsi else None,
                    'macd': float(s.macd) if s.macd else None,
                    'ema_short': float(s.ema_short) if s.ema_short else None,
                    'ema_long': float(s.ema_long) if s.ema_long else None
                }
                for s in snapshots
            ]

        except Exception as e:
            logger.error(f"Error getting historical data: {str(e)}")
            return []
