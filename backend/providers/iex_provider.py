"""
IEX Cloud data provider
Free tier available with API key
"""
import requests
from typing import Optional, Dict, Any
import pandas as pd
import logging
from datetime import datetime
from config import settings

logger = logging.getLogger(__name__)


class IEXCloudProvider:
    """IEX Cloud data provider - Free tier available"""

    def __init__(self):
        self.name = "IEX Cloud"
        self.api_key = settings.IEX_CLOUD_API_KEY
        self.base_url = "https://cloud.iexapis.com/stable"
        self.sandbox_url = "https://sandbox.iexapis.com/stable"

        # Use sandbox for testing if no key
        self.use_sandbox = not bool(self.api_key)
        if self.use_sandbox:
            self.api_url = self.sandbox_url
        else:
            self.api_url = self.base_url

    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make request to IEX Cloud API"""
        if not self.api_key:
            logger.warning("IEX Cloud API key not configured")
            return None

        try:
            params = params or {}
            params['token'] = self.api_key

            response = requests.get(f"{self.api_url}/{endpoint}", params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"IEX Cloud API error: {str(e)}")
            return None

    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get real-time quote from IEX"""
        data = self._make_request(f"stock/{symbol}/quote")
        if not data:
            return None

        return {
            'symbol': symbol,
            'price': data.get('latestPrice'),
            'change': data.get('change'),
            'change_percent': data.get('changePercent'),
            'volume': data.get('latestVolume'),
            'market_cap': data.get('marketCap'),
            'pe_ratio': data.get('peRatio'),
            'timestamp': data.get('latestUpdate'),
            'provider': 'iex'
        }

    def get_stock_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get company information"""
        company = self._make_request(f"stock/{symbol}/company")
        quote = self.get_quote(symbol)

        if not company or not quote:
            return None

        return {
            'symbol': symbol,
            'name': company.get('companyName'),
            'sector': company.get('sector'),
            'industry': company.get('industry'),
            'description': company.get('description'),
            'ceo': company.get('CEO'),
            'website': company.get('website'),
            'exchange': company.get('exchange'),
            'current_price': quote.get('price'),
            'market_cap': quote.get('market_cap'),
            'pe_ratio': quote.get('pe_ratio'),
            'provider': 'iex'
        }

    def get_historical_data(self, symbol: str, range_period: str = "1y") -> Optional[pd.DataFrame]:
        """Get historical price data"""
        # IEX range: 1m, 3m, 6m, 1y, 2y, 5y
        data = self._make_request(f"stock/{symbol}/chart/{range_period}")
        if not data:
            return None

        try:
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.rename(columns={
                'date': 'Date',
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            })
            return df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
        except Exception as e:
            logger.error(f"IEX historical data parsing error: {str(e)}")
            return None

    def search_symbols(self, query: str) -> Optional[list]:
        """Search for symbols"""
        data = self._make_request(f"search/{query}")
        if not data:
            return None

        return [{
            'symbol': item.get('symbol'),
            'name': item.get('securityName'),
            'type': item.get('securityType'),
            'exchange': item.get('exchange')
        } for item in data[:10]]  # Limit to 10 results

    def get_market_movers(self) -> Optional[Dict[str, Any]]:
        """Get market gainers and losers"""
        try:
            gainers = self._make_request("stock/market/list/gainers")
            losers = self._make_request("stock/market/list/losers")
            most_active = self._make_request("stock/market/list/mostactive")

            return {
                'gainers': gainers[:10] if gainers else [],
                'losers': losers[:10] if losers else [],
                'most_active': most_active[:10] if most_active else [],
                'provider': 'iex'
            }
        except Exception as e:
            logger.error(f"IEX market movers error: {str(e)}")
            return None
