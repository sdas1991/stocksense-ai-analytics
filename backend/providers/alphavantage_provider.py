"""
Alpha Vantage data provider
Free tier: 5 API calls per minute, 500 per day
"""
import requests
from typing import Optional, Dict, Any, List
import pandas as pd
import logging
from config import settings

logger = logging.getLogger(__name__)


class AlphaVantageProvider:
    """Alpha Vantage provider - Free tier: 5 calls/minute"""

    def __init__(self):
        self.name = "Alpha Vantage"
        self.api_key = settings.ALPHA_VANTAGE_API_KEY
        self.base_url = "https://www.alphavantage.co/query"

    def is_available(self) -> bool:
        """Check if Alpha Vantage is available"""
        return bool(self.api_key)

    def _make_request(self, params: Dict) -> Optional[Dict]:
        """Make request to Alpha Vantage API"""
        if not self.is_available():
            return None

        try:
            params['apikey'] = self.api_key
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Check for error messages
            if 'Error Message' in data:
                logger.error(f"Alpha Vantage error: {data['Error Message']}")
                return None

            if 'Note' in data:
                logger.warning(f"Alpha Vantage rate limit: {data['Note']}")
                return None

            return data
        except Exception as e:
            logger.error(f"Alpha Vantage API error: {str(e)}")
            return None

    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get real-time quote"""
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol
        }

        data = self._make_request(params)
        if not data or 'Global Quote' not in data:
            return None

        quote = data['Global Quote']

        return {
            'symbol': symbol,
            'price': float(quote.get('05. price', 0)),
            'high': float(quote.get('03. high', 0)),
            'low': float(quote.get('04. low', 0)),
            'open': float(quote.get('02. open', 0)),
            'volume': int(quote.get('06. volume', 0)),
            'previous_close': float(quote.get('08. previous close', 0)),
            'change': float(quote.get('09. change', 0)),
            'change_percent': quote.get('10. change percent', '0%').rstrip('%'),
            'latest_trading_day': quote.get('07. latest trading day'),
            'provider': 'alphavantage'
        }

    def get_daily_data(self, symbol: str, outputsize: str = 'compact') -> Optional[pd.DataFrame]:
        """Get daily time series (compact = last 100 days, full = 20+ years)"""
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'outputsize': outputsize
        }

        data = self._make_request(params)
        if not data or 'Time Series (Daily)' not in data:
            return None

        try:
            ts_data = data['Time Series (Daily)']
            df = pd.DataFrame.from_dict(ts_data, orient='index')

            df.index = pd.to_datetime(df.index)
            df = df.sort_index()

            df = df.rename(columns={
                '1. open': 'Open',
                '2. high': 'High',
                '3. low': 'Low',
                '4. close': 'Close',
                '5. volume': 'Volume'
            })

            df = df.astype(float)
            df = df.reset_index()
            df = df.rename(columns={'index': 'Date'})

            return df
        except Exception as e:
            logger.error(f"Alpha Vantage daily data parsing error: {str(e)}")
            return None

    def get_company_overview(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get company overview/fundamentals"""
        params = {
            'function': 'OVERVIEW',
            'symbol': symbol
        }

        data = self._make_request(params)
        if not data or 'Symbol' not in data:
            return None

        return {
            'symbol': symbol,
            'name': data.get('Name'),
            'description': data.get('Description'),
            'sector': data.get('Sector'),
            'industry': data.get('Industry'),
            'exchange': data.get('Exchange'),
            'currency': data.get('Currency'),
            'country': data.get('Country'),
            'market_cap': data.get('MarketCapitalization'),
            'pe_ratio': data.get('PERatio'),
            'peg_ratio': data.get('PEGRatio'),
            'book_value': data.get('BookValue'),
            'dividend_per_share': data.get('DividendPerShare'),
            'dividend_yield': data.get('DividendYield'),
            'eps': data.get('EPS'),
            'revenue_per_share': data.get('RevenuePerShareTTM'),
            'profit_margin': data.get('ProfitMargin'),
            'operating_margin': data.get('OperatingMarginTTM'),
            '52_week_high': data.get('52WeekHigh'),
            '52_week_low': data.get('52WeekLow'),
            '50_day_ma': data.get('50DayMovingAverage'),
            '200_day_ma': data.get('200DayMovingAverage'),
            'analyst_target_price': data.get('AnalystTargetPrice'),
            'provider': 'alphavantage'
        }

    def search_symbols(self, query: str) -> Optional[List[Dict]]:
        """Search for symbols"""
        params = {
            'function': 'SYMBOL_SEARCH',
            'keywords': query
        }

        data = self._make_request(params)
        if not data or 'bestMatches' not in data:
            return None

        return [{
            'symbol': match.get('1. symbol'),
            'name': match.get('2. name'),
            'type': match.get('3. type'),
            'region': match.get('4. region'),
            'market_open': match.get('5. marketOpen'),
            'market_close': match.get('6. marketClose'),
            'timezone': match.get('7. timezone'),
            'currency': match.get('8. currency'),
            'match_score': match.get('9. matchScore'),
            'provider': 'alphavantage'
        } for match in data['bestMatches'][:10]]

    def get_technical_indicator(self, symbol: str, indicator: str, interval: str = 'daily', **kwargs) -> Optional[Dict]:
        """Get technical indicator"""
        function_map = {
            'rsi': 'RSI',
            'macd': 'MACD',
            'ema': 'EMA',
            'sma': 'SMA',
            'bbands': 'BBANDS'
        }

        if indicator.lower() not in function_map:
            return None

        params = {
            'function': function_map[indicator.lower()],
            'symbol': symbol,
            'interval': interval,
            **kwargs
        }

        data = self._make_request(params)

        if data:
            return {
                'symbol': symbol,
                'indicator': indicator,
                'data': data,
                'provider': 'alphavantage'
            }

        return None
