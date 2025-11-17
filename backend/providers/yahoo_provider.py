"""
Yahoo Finance data provider
Free, no API key required
"""
import yfinance as yf
import pandas as pd
from typing import Optional, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class YahooFinanceProvider:
    """Yahoo Finance data provider - Free, no API key"""

    def __init__(self):
        self.name = "Yahoo Finance"

    def get_stock_data(self, symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """Fetch stock data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)

            if df.empty:
                return None

            df.reset_index(inplace=True)
            return df
        except Exception as e:
            logger.error(f"Yahoo Finance error for {symbol}: {str(e)}")
            return None

    def get_stock_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get stock info from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            return {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 0),
                'currency': info.get('currency', 'USD'),
                'exchange': info.get('exchange', 'N/A'),
                'current_price': info.get('currentPrice'),
                'previous_close': info.get('previousClose'),
                'day_high': info.get('dayHigh'),
                'day_low': info.get('dayLow'),
                'volume': info.get('volume'),
                'avg_volume': info.get('averageVolume'),
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'dividend_yield': info.get('dividendYield'),
                '52_week_high': info.get('fiftyTwoWeekHigh'),
                '52_week_low': info.get('fiftyTwoWeekLow'),
                'provider': 'yahoo'
            }
        except Exception as e:
            logger.error(f"Yahoo Finance info error for {symbol}: {str(e)}")
            return None

    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get real-time quote"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            return {
                'symbol': symbol,
                'price': info.get('currentPrice') or info.get('regularMarketPrice'),
                'change': info.get('regularMarketChange'),
                'change_percent': info.get('regularMarketChangePercent'),
                'volume': info.get('volume'),
                'timestamp': datetime.utcnow().isoformat(),
                'provider': 'yahoo'
            }
        except Exception as e:
            logger.error(f"Yahoo Finance quote error for {symbol}: {str(e)}")
            return None

    def search_symbols(self, query: str) -> Optional[list]:
        """Search for stock symbols (limited in yfinance)"""
        # Yahoo Finance API doesn't have good search, but we can validate
        try:
            ticker = yf.Ticker(query.upper())
            info = ticker.info
            if info.get('symbol'):
                return [{
                    'symbol': info.get('symbol'),
                    'name': info.get('longName', ''),
                    'type': info.get('quoteType', 'equity'),
                    'exchange': info.get('exchange', '')
                }]
        except:
            pass
        return None
