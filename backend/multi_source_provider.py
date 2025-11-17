"""
Multi-source data provider
Aggregates data from multiple providers with intelligent fallback and caching
"""
import logging
from typing import Optional, Dict, Any, List
import pandas as pd
from datetime import datetime

from providers.yahoo_provider import YahooFinanceProvider
from providers.iex_provider import IEXCloudProvider
from providers.finnhub_provider import FinnhubProvider
from providers.polygon_provider import PolygonProvider
from providers.twelvedata_provider import TwelveDataProvider
from providers.alphavantage_provider import AlphaVantageProvider
from data_provider_config import data_provider_service, DataProviderConfig
from redis_service import redis_service

logger = logging.getLogger(__name__)


class MultiSourceProvider:
    """Aggregates data from multiple providers with intelligent fallback"""

    def __init__(self):
        # Initialize all providers
        self.providers = {
            'yahoo': YahooFinanceProvider(),
            'iex': IEXCloudProvider(),
            'finnhub': FinnhubProvider(),
            'polygon': PolygonProvider(),
            'twelvedata': TwelveDataProvider(),
            'alphavantage': AlphaVantageProvider()
        }

        self.available_providers = data_provider_service.available_providers
        logger.info(f"Multi-source provider initialized with: {', '.join(self.available_providers)}")

    def _get_cached_data(self, cache_key: str) -> Optional[Any]:
        """Get data from cache"""
        return redis_service.get(cache_key)

    def _cache_data(self, cache_key: str, data: Any, ttl: int = 900):
        """Cache data with TTL"""
        redis_service.set(cache_key, data, expire=ttl)

    def get_stock_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get stock quote from any available provider
        Uses caching and fallback
        """
        cache_key = f"quote:{symbol}"

        # Check cache first
        cached = self._get_cached_data(cache_key)
        if cached:
            logger.info(f"Quote cache hit for {symbol}")
            return cached

        # Try providers in priority order
        for provider_name in self.available_providers:
            if not DataProviderConfig.can_make_request(provider_name):
                continue

            provider = self.providers.get(provider_name)
            if not provider:
                continue

            try:
                logger.info(f"Trying to get quote for {symbol} from {provider_name}")

                quote = None
                if provider_name == 'yahoo':
                    quote = provider.get_quote(symbol)
                elif provider_name == 'iex':
                    quote = provider.get_quote(symbol)
                elif provider_name == 'finnhub':
                    quote = provider.get_quote(symbol)
                elif provider_name == 'polygon':
                    quote = provider.get_quote(symbol)
                elif provider_name == 'twelvedata':
                    quote = provider.get_quote(symbol)
                elif provider_name == 'alphavantage':
                    quote = provider.get_quote(symbol)

                if quote:
                    DataProviderConfig.record_request(provider_name)
                    self._cache_data(cache_key, quote, ttl=300)  # 5 minutes
                    logger.info(f"Successfully got quote for {symbol} from {provider_name}")
                    return quote

            except Exception as e:
                logger.error(f"Error getting quote from {provider_name}: {str(e)}")
                continue

        logger.warning(f"Could not get quote for {symbol} from any provider")
        return None

    def get_stock_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get detailed stock information with fallback"""
        cache_key = f"info:{symbol}"

        # Check cache
        cached = self._get_cached_data(cache_key)
        if cached:
            return cached

        # Try providers
        for provider_name in self.available_providers:
            if not DataProviderConfig.can_make_request(provider_name):
                continue

            provider = self.providers.get(provider_name)
            if not provider:
                continue

            try:
                info = None
                if provider_name == 'yahoo':
                    info = provider.get_stock_info(symbol)
                elif provider_name == 'iex':
                    info = provider.get_stock_info(symbol)
                elif provider_name == 'finnhub':
                    profile = provider.get_company_profile(symbol)
                    quote = provider.get_quote(symbol)
                    if profile and quote:
                        info = {**profile, **quote}
                elif provider_name == 'polygon':
                    info = provider.get_ticker_details(symbol)
                elif provider_name == 'alphavantage':
                    info = provider.get_company_overview(symbol)

                if info:
                    DataProviderConfig.record_request(provider_name)
                    self._cache_data(cache_key, info, ttl=3600)  # 1 hour
                    return info

            except Exception as e:
                logger.error(f"Error getting info from {provider_name}: {str(e)}")
                continue

        return None

    def get_historical_data(self, symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """Get historical data with fallback"""
        cache_key = f"historical:{symbol}:{period}"

        # Check cache
        cached = self._get_cached_data(cache_key)
        if cached and isinstance(cached, list):
            try:
                df = pd.DataFrame(cached)
                return df
            except:
                pass

        # Try providers
        for provider_name in self.available_providers:
            if not DataProviderConfig.can_make_request(provider_name):
                continue

            provider = self.providers.get(provider_name)
            if not provider:
                continue

            try:
                df = None
                if provider_name == 'yahoo':
                    df = provider.get_stock_data(symbol, period)
                elif provider_name == 'iex':
                    df = provider.get_historical_data(symbol, period)
                elif provider_name == 'twelvedata':
                    # Convert period to outputsize
                    outputsize_map = {'1mo': 30, '3mo': 90, '6mo': 180, '1y': 365}
                    outputsize = outputsize_map.get(period, 365)
                    df = provider.get_time_series(symbol, '1day', outputsize)
                elif provider_name == 'alphavantage':
                    df = provider.get_daily_data(symbol)

                if df is not None and not df.empty:
                    DataProviderConfig.record_request(provider_name)
                    # Cache as dict for JSON serialization
                    self._cache_data(cache_key, df.to_dict('records'), ttl=1800)  # 30 min
                    return df

            except Exception as e:
                logger.error(f"Error getting historical data from {provider_name}: {str(e)}")
                continue

        return None

    def get_company_news(self, symbol: str, days: int = 7) -> Optional[List[Dict]]:
        """Get company news from available providers"""
        cache_key = f"news:{symbol}:{days}"

        # Check cache
        cached = self._get_cached_data(cache_key)
        if cached:
            return cached

        # Finnhub has best news coverage
        if 'finnhub' in self.available_providers:
            if DataProviderConfig.can_make_request('finnhub'):
                provider = self.providers['finnhub']
                try:
                    news = provider.get_company_news(symbol, days)
                    if news:
                        DataProviderConfig.record_request('finnhub')
                        self._cache_data(cache_key, news, ttl=600)  # 10 min
                        return news
                except Exception as e:
                    logger.error(f"Error getting news from Finnhub: {str(e)}")

        return None

    def get_market_movers(self) -> Optional[Dict[str, Any]]:
        """Get market gainers, losers, and most active"""
        cache_key = "market:movers"

        # Check cache
        cached = self._get_cached_data(cache_key)
        if cached:
            return cached

        # IEX has good market movers data
        if 'iex' in self.available_providers:
            if DataProviderConfig.can_make_request('iex'):
                provider = self.providers['iex']
                try:
                    movers = provider.get_market_movers()
                    if movers:
                        DataProviderConfig.record_request('iex')
                        self._cache_data(cache_key, movers, ttl=300)  # 5 min
                        return movers
                except Exception as e:
                    logger.error(f"Error getting market movers from IEX: {str(e)}")

        return None

    def search_symbols(self, query: str) -> Optional[List[Dict]]:
        """Search for stock symbols across providers"""
        cache_key = f"search:{query}"

        # Check cache
        cached = self._get_cached_data(cache_key)
        if cached:
            return cached

        results = []
        used_symbols = set()

        # Try multiple providers to get comprehensive results
        for provider_name in self.available_providers:
            if not DataProviderConfig.can_make_request(provider_name):
                continue

            provider = self.providers.get(provider_name)
            if not provider:
                continue

            try:
                search_results = None
                if provider_name == 'iex':
                    search_results = provider.search_symbols(query)
                elif provider_name == 'finnhub':
                    search_results = provider.search_symbols(query)
                elif provider_name == 'twelvedata':
                    search_results = provider.search_symbols(query)
                elif provider_name == 'alphavantage':
                    search_results = provider.search_symbols(query)
                elif provider_name == 'polygon':
                    search_results = provider.search_tickers(query)

                if search_results:
                    DataProviderConfig.record_request(provider_name)
                    for result in search_results:
                        symbol = result.get('symbol')
                        if symbol and symbol not in used_symbols:
                            results.append(result)
                            used_symbols.add(symbol)

                # Break after first successful provider or if we have enough results
                if len(results) >= 10:
                    break

            except Exception as e:
                logger.error(f"Error searching from {provider_name}: {str(e)}")
                continue

        if results:
            self._cache_data(cache_key, results, ttl=3600)  # 1 hour

        return results if results else None

    def get_provider_stats(self) -> Dict[str, Any]:
        """Get statistics about all providers"""
        return data_provider_service.get_provider_stats()


# Global instance
multi_source_provider = MultiSourceProvider()
