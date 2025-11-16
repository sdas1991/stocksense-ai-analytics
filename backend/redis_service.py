"""
Redis caching service for StockSense AI
Provides caching for stock data, indicators, and API responses
"""
import redis
import json
import logging
from typing import Optional, Any
from config import settings

logger = logging.getLogger(__name__)


class RedisService:
    """Redis caching service"""

    def __init__(self):
        self.redis_client = None
        self.enabled = False
        try:
            # Parse Redis URL
            redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0')
            self.redis_client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            self.enabled = True
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.warning(f"Redis not available: {str(e)}. Caching disabled.")
            self.enabled = False

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled:
            return None

        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis GET error: {str(e)}")
            return None

    def set(self, key: str, value: Any, expire: int = 300) -> bool:
        """
        Set value in cache
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            expire: Expiration time in seconds (default 5 minutes)
        """
        if not self.enabled:
            return False

        try:
            serialized = json.dumps(value, default=str)
            self.redis_client.setex(key, expire, serialized)
            return True
        except Exception as e:
            logger.error(f"Redis SET error: {str(e)}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.enabled:
            return False

        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis DELETE error: {str(e)}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.enabled:
            return False

        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Redis EXISTS error: {str(e)}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern
        Args:
            pattern: Redis pattern (e.g., "stock:*")
        Returns:
            Number of keys deleted
        """
        if not self.enabled:
            return 0

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Redis CLEAR_PATTERN error: {str(e)}")
            return 0

    def get_ttl(self, key: str) -> int:
        """Get remaining TTL for a key in seconds"""
        if not self.enabled:
            return -1

        try:
            return self.redis_client.ttl(key)
        except Exception as e:
            logger.error(f"Redis TTL error: {str(e)}")
            return -1

    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment a counter"""
        if not self.enabled:
            return None

        try:
            return self.redis_client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Redis INCREMENT error: {str(e)}")
            return None

    def cache_stock_data(self, symbol: str, period: str, data: dict, expire: int = 900):
        """Cache stock analysis data (15 min default)"""
        key = f"stock:analysis:{symbol}:{period}"
        return self.set(key, data, expire)

    def get_cached_stock_data(self, symbol: str, period: str) -> Optional[dict]:
        """Get cached stock analysis data"""
        key = f"stock:analysis:{symbol}:{period}"
        return self.get(key)

    def cache_stock_history(self, symbol: str, period: str, data: list, expire: int = 1800):
        """Cache stock historical data (30 min default)"""
        key = f"stock:history:{symbol}:{period}"
        return self.set(key, data, expire)

    def get_cached_stock_history(self, symbol: str, period: str) -> Optional[list]:
        """Get cached stock historical data"""
        key = f"stock:history:{symbol}:{period}"
        return self.get(key)

    def invalidate_stock_cache(self, symbol: str):
        """Invalidate all cache entries for a stock"""
        return self.clear_pattern(f"stock:*:{symbol}:*")

    def get_stats(self) -> dict:
        """Get Redis statistics"""
        if not self.enabled:
            return {"enabled": False}

        try:
            info = self.redis_client.info()
            return {
                "enabled": True,
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "0"),
                "total_keys": self.redis_client.dbsize(),
                "uptime_days": info.get("uptime_in_days", 0)
            }
        except Exception as e:
            logger.error(f"Redis STATS error: {str(e)}")
            return {"enabled": False, "error": str(e)}


# Global Redis instance
redis_service = RedisService()
