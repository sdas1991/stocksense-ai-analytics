"""
Twelve Data provider
Free tier: 8 API calls per minute, 800 per day
"""
from twelvedata import TDClient
from typing import Optional, Dict, Any, List
import logging
import pandas as pd
from config import settings

logger = logging.getLogger(__name__)


class TwelveDataProvider:
    """Twelve Data provider - Free tier: 8 calls/minute"""

    def __init__(self):
        self.name = "Twelve Data"
        self.api_key = settings.TWELVE_DATA_API_KEY
        self.client = None

        if self.api_key:
            try:
                self.client = TDClient(apikey=self.api_key)
            except Exception as e:
                logger.error(f"Twelve Data client initialization error: {str(e)}")

    def is_available(self) -> bool:
        """Check if Twelve Data is available"""
        return bool(self.client)

    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get real-time quote"""
        if not self.is_available():
            return None

        try:
            quote = self.client.quote(symbol=symbol).as_json()

            return {
                'symbol': symbol,
                'name': quote.get('name'),
                'exchange': quote.get('exchange'),
                'price': float(quote.get('close', 0)),
                'open': float(quote.get('open', 0)),
                'high': float(quote.get('high', 0)),
                'low': float(quote.get('low', 0)),
                'volume': int(quote.get('volume', 0)),
                'change': float(quote.get('change', 0)),
                'change_percent': float(quote.get('percent_change', 0)),
                'previous_close': float(quote.get('previous_close', 0)),
                'timestamp': quote.get('datetime'),
                'provider': 'twelvedata'
            }
        except Exception as e:
            logger.error(f"Twelve Data quote error for {symbol}: {str(e)}")
            return None

    def get_time_series(self, symbol: str, interval: str = "1day", outputsize: int = 365) -> Optional[pd.DataFrame]:
        """Get historical time series"""
        if not self.is_available():
            return None

        try:
            ts = self.client.time_series(
                symbol=symbol,
                interval=interval,
                outputsize=outputsize
            )

            df = ts.as_pandas()

            if df is not None and not df.empty:
                df = df.reset_index()
                df = df.rename(columns={
                    'datetime': 'Date',
                    'open': 'Open',
                    'high': 'High',
                    'low': 'Low',
                    'close': 'Close',
                    'volume': 'Volume'
                })
                return df

            return None
        except Exception as e:
            logger.error(f"Twelve Data time series error for {symbol}: {str(e)}")
            return None

    def get_technical_indicator(self, symbol: str, indicator: str, **kwargs) -> Optional[Dict]:
        """Get technical indicator (RSI, MACD, etc.)"""
        if not self.is_available():
            return None

        try:
            # Available indicators: rsi, macd, ema, sma, bbands, etc.
            result = None

            if indicator.lower() == 'rsi':
                result = self.client.rsi(symbol=symbol, **kwargs).as_json()
            elif indicator.lower() == 'macd':
                result = self.client.macd(symbol=symbol, **kwargs).as_json()
            elif indicator.lower() == 'ema':
                result = self.client.ema(symbol=symbol, **kwargs).as_json()
            elif indicator.lower() == 'sma':
                result = self.client.sma(symbol=symbol, **kwargs).as_json()
            elif indicator.lower() == 'bbands':
                result = self.client.bbands(symbol=symbol, **kwargs).as_json()

            if result:
                return {
                    'symbol': symbol,
                    'indicator': indicator,
                    'data': result,
                    'provider': 'twelvedata'
                }

            return None
        except Exception as e:
            logger.error(f"Twelve Data indicator error for {symbol}: {str(e)}")
            return None

    def search_symbols(self, query: str) -> Optional[List[Dict]]:
        """Search for symbols"""
        if not self.is_available():
            return None

        try:
            results = self.client.symbol_search(symbol=query).as_json()

            if not results or 'data' not in results:
                return None

            return [{
                'symbol': item.get('symbol'),
                'name': item.get('instrument_name'),
                'type': item.get('instrument_type'),
                'exchange': item.get('exchange'),
                'country': item.get('country'),
                'currency': item.get('currency'),
                'provider': 'twelvedata'
            } for item in results['data'][:10]]
        except Exception as e:
            logger.error(f"Twelve Data search error: {str(e)}")
            return None

    def get_earliest_timestamp(self, symbol: str) -> Optional[str]:
        """Get earliest available timestamp for symbol"""
        if not self.is_available():
            return None

        try:
            result = self.client.earliest_timestamp(symbol=symbol).as_json()
            return result.get('datetime')
        except Exception as e:
            logger.error(f"Twelve Data earliest timestamp error: {str(e)}")
            return None
