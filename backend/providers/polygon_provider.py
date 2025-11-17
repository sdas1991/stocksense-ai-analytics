"""
Polygon.io data provider
Free tier: 5 API calls per minute
"""
from polygon import RESTClient
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime, timedelta
from config import settings

logger = logging.getLogger(__name__)


class PolygonProvider:
    """Polygon.io data provider - Free tier: 5 calls/minute"""

    def __init__(self):
        self.name = "Polygon.io"
        self.api_key = settings.POLYGON_API_KEY
        self.client = None

        if self.api_key:
            try:
                self.client = RESTClient(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Polygon client initialization error: {str(e)}")

    def is_available(self) -> bool:
        """Check if Polygon is available"""
        return bool(self.client)

    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get last quote for symbol"""
        if not self.is_available():
            return None

        try:
            quote = self.client.get_last_quote(symbol)

            return {
                'symbol': symbol,
                'price': quote.last.price if hasattr(quote, 'last') else None,
                'bid': quote.last.bid_price if hasattr(quote, 'last') else None,
                'ask': quote.last.ask_price if hasattr(quote, 'last') else None,
                'bid_size': quote.last.bid_size if hasattr(quote, 'last') else None,
                'ask_size': quote.last.ask_size if hasattr(quote, 'last') else None,
                'timestamp': quote.last.sip_timestamp if hasattr(quote, 'last') else None,
                'provider': 'polygon'
            }
        except Exception as e:
            logger.error(f"Polygon quote error for {symbol}: {str(e)}")
            return None

    def get_daily_open_close(self, symbol: str, date: str = None) -> Optional[Dict[str, Any]]:
        """Get daily OHLC for a specific date"""
        if not self.is_available():
            return None

        try:
            if not date:
                # Get yesterday's data
                date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

            data = self.client.get_daily_open_close(symbol, date)

            return {
                'symbol': symbol,
                'date': date,
                'open': data.open,
                'high': data.high,
                'low': data.low,
                'close': data.close,
                'volume': data.volume,
                'after_hours': data.afterHours if hasattr(data, 'afterHours') else None,
                'pre_market': data.preMarket if hasattr(data, 'preMarket') else None,
                'provider': 'polygon'
            }
        except Exception as e:
            logger.error(f"Polygon daily data error for {symbol}: {str(e)}")
            return None

    def get_ticker_details(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get ticker details"""
        if not self.is_available():
            return None

        try:
            details = self.client.get_ticker_details(symbol)

            return {
                'symbol': symbol,
                'name': details.name,
                'market': details.market if hasattr(details, 'market') else None,
                'locale': details.locale if hasattr(details, 'locale') else None,
                'primary_exchange': details.primary_exchange if hasattr(details, 'primary_exchange') else None,
                'type': details.type if hasattr(details, 'type') else None,
                'currency_name': details.currency_name if hasattr(details, 'currency_name') else None,
                'market_cap': details.market_cap if hasattr(details, 'market_cap') else None,
                'share_class_shares_outstanding': details.share_class_shares_outstanding if hasattr(details, 'share_class_shares_outstanding') else None,
                'description': details.description if hasattr(details, 'description') else None,
                'homepage_url': details.homepage_url if hasattr(details, 'homepage_url') else None,
                'total_employees': details.total_employees if hasattr(details, 'total_employees') else None,
                'list_date': details.list_date if hasattr(details, 'list_date') else None,
                'provider': 'polygon'
            }
        except Exception as e:
            logger.error(f"Polygon ticker details error for {symbol}: {str(e)}")
            return None

    def search_tickers(self, query: str) -> Optional[List[Dict]]:
        """Search for tickers"""
        if not self.is_available():
            return None

        try:
            results = self.client.list_tickers(search=query, limit=10)

            return [{
                'symbol': ticker.ticker,
                'name': ticker.name,
                'market': ticker.market if hasattr(ticker, 'market') else None,
                'type': ticker.type if hasattr(ticker, 'type') else None,
                'primary_exchange': ticker.primary_exchange if hasattr(ticker, 'primary_exchange') else None,
                'provider': 'polygon'
            } for ticker in results]
        except Exception as e:
            logger.error(f"Polygon search error: {str(e)}")
            return None

    def get_market_status(self) -> Optional[Dict[str, Any]]:
        """Get market status"""
        if not self.is_available():
            return None

        try:
            status = self.client.get_market_status()

            return {
                'market': status.market if hasattr(status, 'market') else None,
                'server_time': status.serverTime if hasattr(status, 'serverTime') else None,
                'exchanges': {
                    'nasdaq': status.exchanges.nasdaq if hasattr(status, 'exchanges') else None,
                    'nyse': status.exchanges.nyse if hasattr(status, 'exchanges') else None,
                    'otc': status.exchanges.otc if hasattr(status, 'exchanges') else None,
                },
                'provider': 'polygon'
            }
        except Exception as e:
            logger.error(f"Polygon market status error: {str(e)}")
            return None
