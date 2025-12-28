"""
Simple caching layer for Control Center backend

Provides TTL-based caching to improve performance for expensive operations
like file scanning, agent loading, and KB file enumeration.
"""

import time
from typing import Any, Callable, Optional
from functools import wraps


class SimpleCache:
    """
    Simple time-based cache with TTL (Time To Live)

    Usage:
        cache = SimpleCache(ttl=300)  # 5 minutes
        cache.set("key", value)
        result = cache.get("key")  # Returns value if not expired, None otherwise
    """

    def __init__(self, ttl: int = 300):
        """
        Initialize cache

        Args:
            ttl: Time to live in seconds (default: 300 = 5 minutes)
        """
        self._cache = {}
        self._timestamps = {}
        self.ttl = ttl

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache if not expired

        Args:
            key: Cache key

        Returns:
            Cached value if exists and not expired, None otherwise
        """
        if key in self._cache:
            if time.time() - self._timestamps[key] < self.ttl:
                return self._cache[key]
            else:
                # Cache expired, remove it
                del self._cache[key]
                del self._timestamps[key]
        return None

    def set(self, key: str, value: Any):
        """
        Set value in cache with current timestamp

        Args:
            key: Cache key
            value: Value to cache
        """
        self._cache[key] = value
        self._timestamps[key] = time.time()

    def invalidate(self, key: str):
        """
        Invalidate a specific cache entry

        Args:
            key: Cache key to invalidate
        """
        if key in self._cache:
            del self._cache[key]
            del self._timestamps[key]

    def clear(self):
        """Clear all cache entries"""
        self._cache.clear()
        self._timestamps.clear()

    def get_stats(self) -> dict:
        """
        Get cache statistics

        Returns:
            Dictionary with cache stats (size, entries, etc.)
        """
        current_time = time.time()
        expired_count = sum(
            1 for key, timestamp in self._timestamps.items()
            if current_time - timestamp >= self.ttl
        )

        return {
            "total_entries": len(self._cache),
            "expired_entries": expired_count,
            "active_entries": len(self._cache) - expired_count,
            "ttl_seconds": self.ttl
        }


def cached(ttl: int = 300):
    """
    Decorator for caching function results with TTL

    Usage:
        @cached(ttl=300)
        def expensive_function(arg1, arg2):
            # ... expensive computation
            return result

    The cache key is automatically generated from the function name and arguments.
    The cache instance is exposed as function_name.cache for manual operations.

    Args:
        ttl: Time to live in seconds (default: 300 = 5 minutes)
    """
    cache = SimpleCache(ttl)

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            # Convert args and kwargs to a hashable key
            cache_key = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"

            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result

            # Cache miss - compute result
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            return result

        # Expose cache for manual invalidation
        wrapper.cache = cache
        wrapper.invalidate = lambda: cache.clear()

        return wrapper

    return decorator
