"""
Caching service for scraped content
Uses TTL-based in-memory cache, extensible to Redis in the future
"""

import hashlib
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from cachetools import TTLCache
from scraper_config import ScraperConfig


class ContentCache:
    """
    TTL-based cache for scraped content
    Extensible to Redis or other backends in the future
    """

    def __init__(
        self,
        ttl: int = ScraperConfig.CACHE_TTL_SECONDS,
        maxsize: int = ScraperConfig.CACHE_MAX_SIZE
    ):
        """
        Initialize cache

        Args:
            ttl: Time-to-live in seconds
            maxsize: Maximum number of items in cache
        """
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl)
        self.ttl = ttl
        self.logger = logging.getLogger(__name__)

    def _make_key(self, url: str) -> str:
        """
        Generate cache key from URL

        Args:
            url: The URL to cache

        Returns:
            MD5 hash of the URL
        """
        return hashlib.md5(url.encode('utf-8')).hexdigest()

    def get(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached content for a URL

        Args:
            url: The URL to look up

        Returns:
            Cached data dict or None if not found/expired
        """
        key = self._make_key(url)
        data = self.cache.get(key)

        if data:
            self.logger.info(f"Cache HIT for URL: {url[:50]}...")
            # Add cache metadata
            data['cached'] = True
            data['cache_timestamp'] = data.get('cache_timestamp', datetime.utcnow().isoformat())
            return data
        else:
            self.logger.info(f"Cache MISS for URL: {url[:50]}...")
            return None

    def set(self, url: str, data: Dict[str, Any]) -> None:
        """
        Store content in cache

        Args:
            url: The URL key
            data: The data to cache
        """
        key = self._make_key(url)
        # Add timestamp
        data['cache_timestamp'] = datetime.utcnow().isoformat()
        data['cached'] = False  # Will be True when retrieved

        self.cache[key] = data
        self.logger.info(f"Cached content for URL: {url[:50]}... (TTL: {self.ttl}s)")

    def invalidate(self, url: str) -> bool:
        """
        Invalidate/remove cached content for a URL

        Args:
            url: The URL to invalidate

        Returns:
            True if item was in cache, False otherwise
        """
        key = self._make_key(url)
        if key in self.cache:
            del self.cache[key]
            self.logger.info(f"Invalidated cache for URL: {url[:50]}...")
            return True
        return False

    def clear(self) -> None:
        """Clear all cached content"""
        self.cache.clear()
        self.logger.info("Cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics

        Returns:
            Dict with cache stats
        """
        return {
            'size': len(self.cache),
            'maxsize': self.cache.maxsize,
            'ttl_seconds': self.ttl,
            'currsize': self.cache.currsize
        }


# Global cache instance (singleton pattern)
_cache_instance = None


def get_cache() -> ContentCache:
    """
    Get global cache instance (singleton)

    Returns:
        ContentCache instance
    """
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = ContentCache()
    return _cache_instance


# For future extension to Redis:
# class RedisContentCache(ContentCache):
#     def __init__(self, redis_client, ttl=3600):
#         self.redis = redis_client
#         self.ttl = ttl
#
#     def get(self, url: str) -> Optional[Dict[str, Any]]:
#         key = self._make_key(url)
#         data = self.redis.get(key)
#         if data:
#             return json.loads(data)
#         return None
#
#     def set(self, url: str, data: Dict[str, Any]) -> None:
#         key = self._make_key(url)
#         self.redis.setex(key, self.ttl, json.dumps(data))
