"""
Finnhub data provider
Free tier available with API key
"""
import finnhub
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime, timedelta
from config import settings

logger = logging.getLogger(__name__)


class FinnhubProvider:
    """Finnhub data provider - Free tier: 60 calls/minute"""

    def __init__(self):
        self.name = "Finnhub"
        self.api_key = settings.FINNHUB_API_KEY
        self.client = None

        if self.api_key:
            try:
                self.client = finnhub.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Finnhub client initialization error: {str(e)}")

    def is_available(self) -> bool:
        """Check if Finnhub is available"""
        return bool(self.client)

    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get real-time quote"""
        if not self.is_available():
            return None

        try:
            quote = self.client.quote(symbol)

            return {
                'symbol': symbol,
                'price': quote.get('c'),  # Current price
                'high': quote.get('h'),   # High of the day
                'low': quote.get('l'),    # Low of the day
                'open': quote.get('o'),   # Open price
                'previous_close': quote.get('pc'),
                'change': quote.get('d'),  # Change
                'change_percent': quote.get('dp'),  # Percent change
                'timestamp': quote.get('t'),
                'provider': 'finnhub'
            }
        except Exception as e:
            logger.error(f"Finnhub quote error for {symbol}: {str(e)}")
            return None

    def get_company_profile(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get company profile"""
        if not self.is_available():
            return None

        try:
            profile = self.client.company_profile2(symbol=symbol)

            return {
                'symbol': symbol,
                'name': profile.get('name'),
                'country': profile.get('country'),
                'currency': profile.get('currency'),
                'exchange': profile.get('exchange'),
                'ipo': profile.get('ipo'),
                'market_cap': profile.get('marketCapitalization'),
                'industry': profile.get('finnhubIndustry'),
                'logo': profile.get('logo'),
                'phone': profile.get('phone'),
                'share_outstanding': profile.get('shareOutstanding'),
                'weburl': profile.get('weburl'),
                'provider': 'finnhub'
            }
        except Exception as e:
            logger.error(f"Finnhub profile error for {symbol}: {str(e)}")
            return None

    def get_company_news(self, symbol: str, days: int = 7) -> Optional[List[Dict]]:
        """Get company news"""
        if not self.is_available():
            return None

        try:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

            news = self.client.company_news(symbol, _from=start_date, to=end_date)

            return [{
                'headline': article.get('headline'),
                'summary': article.get('summary'),
                'source': article.get('source'),
                'url': article.get('url'),
                'datetime': article.get('datetime'),
                'image': article.get('image'),
                'category': article.get('category'),
                'provider': 'finnhub'
            } for article in news[:20]]  # Limit to 20 articles
        except Exception as e:
            logger.error(f"Finnhub news error for {symbol}: {str(e)}")
            return None

    def get_market_news(self, category: str = "general") -> Optional[List[Dict]]:
        """Get general market news"""
        if not self.is_available():
            return None

        try:
            news = self.client.general_news(category, min_id=0)

            return [{
                'headline': article.get('headline'),
                'summary': article.get('summary'),
                'source': article.get('source'),
                'url': article.get('url'),
                'datetime': article.get('datetime'),
                'image': article.get('image'),
                'provider': 'finnhub'
            } for article in news[:15]]
        except Exception as e:
            logger.error(f"Finnhub market news error: {str(e)}")
            return None

    def search_symbols(self, query: str) -> Optional[List[Dict]]:
        """Search symbols"""
        if not self.is_available():
            return None

        try:
            results = self.client.symbol_lookup(query)

            if not results or 'result' not in results:
                return None

            return [{
                'symbol': item.get('symbol'),
                'name': item.get('description'),
                'type': item.get('type'),
                'exchange': item.get('displaySymbol'),
                'provider': 'finnhub'
            } for item in results['result'][:10]]
        except Exception as e:
            logger.error(f"Finnhub symbol search error: {str(e)}")
            return None

    def get_recommendation_trends(self, symbol: str) -> Optional[List[Dict]]:
        """Get analyst recommendations"""
        if not self.is_available():
            return None

        try:
            recommendations = self.client.recommendation_trends(symbol)

            return [{
                'period': rec.get('period'),
                'strong_buy': rec.get('strongBuy'),
                'buy': rec.get('buy'),
                'hold': rec.get('hold'),
                'sell': rec.get('sell'),
                'strong_sell': rec.get('strongSell'),
                'provider': 'finnhub'
            } for rec in recommendations]
        except Exception as e:
            logger.error(f"Finnhub recommendations error: {str(e)}")
            return None
