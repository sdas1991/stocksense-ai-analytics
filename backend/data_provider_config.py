"""
Multi-source data provider service
Aggregates data from multiple APIs with intelligent fallback and caching
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from config import settings
from redis_service import redis_service

logger = logging.getLogger(__name__)


class DataProviderConfig:
    """Configuration for each data provider"""

    PROVIDERS = {
        "yahoo": {
            "name": "Yahoo Finance",
            "requires_key": False,
            "free": True,
            "rate_limit": None,  # No strict limit
            "delay_between_calls": 0.1  # 100ms between calls
        },
        "iex": {
            "name": "IEX Cloud",
            "requires_key": True,
            "free": True,  # Has free tier
            "rate_limit": 100,  # 100 requests per second (free tier)
            "delay_between_calls": 0.01
        },
        "polygon": {
            "name": "Polygon.io",
            "requires_key": True,
            "free": True,  # Has free tier
            "rate_limit": 5,  # 5 requests per minute (free tier)
            "delay_between_calls": 12  # 12 seconds between calls
        },
        "finnhub": {
            "name": "Finnhub",
            "requires_key": True,
            "free": True,  # Has free tier
            "rate_limit": 60,  # 60 calls per minute
            "delay_between_calls": 1
        },
        "twelvedata": {
            "name": "Twelve Data",
            "requires_key": True,
            "free": True,  # Has free tier
            "rate_limit": 8,  # 8 requests per minute (free tier)
            "delay_between_calls": 8
        },
        "alphavantage": {
            "name": "Alpha Vantage",
            "requires_key": True,
            "free": True,  # Free tier available
            "rate_limit": 5,  # 5 requests per minute
            "delay_between_calls": 12
        }
    }

    @classmethod
    def is_provider_available(cls, provider: str) -> bool:
        """Check if provider is available based on configuration"""
        if provider not in cls.PROVIDERS:
            return False

        config = cls.PROVIDERS[provider]

        # If provider doesn't require key, it's available
        if not config["requires_key"]:
            return True

        # Check if API key is configured
        key_mapping = {
            "iex": settings.IEX_CLOUD_API_KEY,
            "polygon": settings.POLYGON_API_KEY,
            "finnhub": settings.FINNHUB_API_KEY,
            "twelvedata": settings.TWELVE_DATA_API_KEY,
            "alphavantage": settings.ALPHA_VANTAGE_API_KEY
        }

        return bool(key_mapping.get(provider))

    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of available providers based on configuration"""
        available = []
        for provider in settings.DATA_PROVIDER_PRIORITY:
            if cls.is_provider_available(provider):
                available.append(provider)
        return available

    @classmethod
    def can_make_request(cls, provider: str) -> bool:
        """Check if we can make a request to provider (rate limiting)"""
        if not cls.is_provider_available(provider):
            return False

        config = cls.PROVIDERS.get(provider)
        if not config:
            return False

        # Check rate limit from Redis
        rate_limit_key = f"rate_limit:{provider}"

        if config["rate_limit"]:
            # Check current request count
            current_count = redis_service.get(rate_limit_key)
            if current_count and int(current_count) >= config["rate_limit"]:
                logger.warning(f"Rate limit reached for {provider}")
                return False

        # Check last request time
        last_request_key = f"last_request:{provider}"
        last_request = redis_service.get(last_request_key)

        if last_request:
            time_since_last = (datetime.utcnow() - datetime.fromisoformat(last_request)).total_seconds()
            if time_since_last < config["delay_between_calls"]:
                return False

        return True

    @classmethod
    def record_request(cls, provider: str):
        """Record that a request was made to provider"""
        config = cls.PROVIDERS.get(provider)
        if not config:
            return

        # Record request count (expires after 1 minute)
        rate_limit_key = f"rate_limit:{provider}"
        current = redis_service.increment(rate_limit_key)
        if current == 1:  # First request, set expiry
            redis_service.redis_client.expire(rate_limit_key, 60)

        # Record last request time
        last_request_key = f"last_request:{provider}"
        redis_service.set(last_request_key, datetime.utcnow().isoformat(), expire=300)

    @classmethod
    def get_provider_status(cls) -> Dict[str, Any]:
        """Get status of all providers"""
        status = {}
        for provider, config in cls.PROVIDERS.items():
            available = cls.is_provider_available(provider)
            can_request = cls.can_make_request(provider) if available else False

            rate_limit_key = f"rate_limit:{provider}"
            requests_made = redis_service.get(rate_limit_key) or 0

            status[provider] = {
                "name": config["name"],
                "available": available,
                "can_request": can_request,
                "requires_key": config["requires_key"],
                "free": config["free"],
                "rate_limit": config["rate_limit"],
                "requests_made_last_minute": int(requests_made)
            }

        return status


class DataProviderService:
    """Service to aggregate data from multiple providers"""

    def __init__(self):
        self.available_providers = DataProviderConfig.get_available_providers()
        logger.info(f"Available data providers: {', '.join(self.available_providers)}")

    def get_primary_provider(self) -> Optional[str]:
        """Get the primary (highest priority) available provider"""
        for provider in self.available_providers:
            if DataProviderConfig.can_make_request(provider):
                return provider
        return None

    def get_fallback_provider(self, exclude: List[str] = None) -> Optional[str]:
        """Get fallback provider excluding specified ones"""
        exclude = exclude or []
        for provider in self.available_providers:
            if provider not in exclude and DataProviderConfig.can_make_request(provider):
                return provider
        return None

    def record_provider_usage(self, provider: str):
        """Record that provider was used"""
        DataProviderConfig.record_request(provider)

    def get_provider_stats(self) -> Dict[str, Any]:
        """Get statistics about provider usage"""
        return DataProviderConfig.get_provider_status()


# Global instance
data_provider_service = DataProviderService()
