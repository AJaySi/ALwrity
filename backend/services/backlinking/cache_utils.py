"""
Caching utilities for the AI Backlinking service.

Provides in-memory caching with TTL support for expensive operations
and API response caching to improve performance.
"""

import asyncio
import time
from typing import Any, Dict, Optional, Callable, Awaitable
from dataclasses import dataclass
from contextlib import asynccontextmanager
import hashlib
import json

from .config import get_config
from .logging_utils import backlinking_logger


@dataclass
class CacheEntry:
    """Cache entry with TTL support."""
    data: Any
    timestamp: float
    ttl: int

    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        return time.time() - self.timestamp > self.ttl

    def get_age(self) -> float:
        """Get the age of the cache entry in seconds."""
        return time.time() - self.timestamp


class MemoryCache:
    """
    In-memory cache with TTL support.

    Provides thread-safe caching for expensive operations.
    In production, this should be replaced with Redis or similar.
    """

    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        async with self._lock:
            entry = self.cache.get(key)
            if entry and not entry.is_expired():
                backlinking_logger.debug(f"Cache hit for key: {key}")
                return entry.data
            elif entry and entry.is_expired():
                # Remove expired entry
                del self.cache[key]
                backlinking_logger.debug(f"Cache expired for key: {key}")

        return None

    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """
        Set a value in the cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: 5 minutes)
        """
        async with self._lock:
            # Implement LRU eviction if cache is full
            if len(self.cache) >= self.max_size:
                # Remove oldest entries (simple implementation)
                oldest_key = min(self.cache.keys(),
                               key=lambda k: self.cache[k].timestamp)
                del self.cache[oldest_key]
                backlinking_logger.debug(f"Cache eviction: removed {oldest_key}")

            self.cache[key] = CacheEntry(
                data=value,
                timestamp=time.time(),
                ttl=ttl
            )

            backlinking_logger.debug(f"Cache set for key: {key}, TTL: {ttl}s")

    async def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.

        Args:
            key: Cache key

        Returns:
            True if key existed and was deleted, False otherwise
        """
        async with self._lock:
            if key in self.cache:
                del self.cache[key]
                backlinking_logger.debug(f"Cache deleted for key: {key}")
                return True
        return False

    async def clear(self) -> None:
        """Clear all cache entries."""
        async with self._lock:
            self.cache.clear()
            backlinking_logger.info("Cache cleared")

    async def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        async with self._lock:
            total_entries = len(self.cache)
            expired_entries = sum(1 for entry in self.cache.values() if entry.is_expired())
            valid_entries = total_entries - expired_entries

            return {
                "total_entries": total_entries,
                "valid_entries": valid_entries,
                "expired_entries": expired_entries,
                "hit_rate": 0.0,  # Would need to track hits/misses for this
                "max_size": self.max_size
            }


class CacheManager:
    """
    Cache manager for different types of cached data.

    Provides specialized caching for different use cases.
    """

    def __init__(self):
        self.config = get_config()
        self.cache = MemoryCache(max_size=1000)

        # Cache TTL configurations
        self.ttl_configs = {
            "scraping_result": 3600,      # 1 hour for scraping results
            "opportunity_search": 1800,   # 30 minutes for search results
            "email_generation": 7200,     # 2 hours for generated emails
            "analytics": 300,             # 5 minutes for analytics
            "config": 600,                # 10 minutes for config data
        }

    async def get_scraping_result(self, url: str) -> Optional[Dict[str, Any]]:
        """Get cached scraping result for a URL."""
        cache_key = f"scraping:{self._hash_url(url)}"
        return await self.cache.get(cache_key)

    async def set_scraping_result(self, url: str, data: Dict[str, Any]) -> None:
        """Cache scraping result for a URL."""
        cache_key = f"scraping:{self._hash_url(url)}"
        ttl = self.ttl_configs["scraping_result"]
        await self.cache.set(cache_key, data, ttl)

    async def get_search_results(self, keywords: str, search_type: str = "opportunities") -> Optional[List[Dict[str, Any]]]:
        """Get cached search results."""
        cache_key = f"search:{search_type}:{self._hash_keywords(keywords)}"
        return await self.cache.get(cache_key)

    async def set_search_results(self, keywords: str, results: List[Dict[str, Any]], search_type: str = "opportunities") -> None:
        """Cache search results."""
        cache_key = f"search:{search_type}:{self._hash_keywords(keywords)}"
        ttl = self.ttl_configs["opportunity_search"]
        await self.cache.set(cache_key, results, ttl)

    async def get_generated_email(self, campaign_id: str, opportunity_url: str) -> Optional[str]:
        """Get cached generated email."""
        cache_key = f"email:{campaign_id}:{self._hash_url(opportunity_url)}"
        return await self.cache.get(cache_key)

    async def set_generated_email(self, campaign_id: str, opportunity_url: str, email_content: str) -> None:
        """Cache generated email."""
        cache_key = f"email:{campaign_id}:{self._hash_url(opportunity_url)}"
        ttl = self.ttl_configs["email_generation"]
        await self.cache.set(cache_key, email_content, ttl)

    async def get_campaign_analytics(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get cached campaign analytics."""
        cache_key = f"analytics:{campaign_id}"
        return await self.cache.get(cache_key)

    async def set_campaign_analytics(self, campaign_id: str, analytics: Dict[str, Any]) -> None:
        """Cache campaign analytics."""
        cache_key = f"analytics:{campaign_id}"
        ttl = self.ttl_configs["analytics"]
        await self.cache.set(cache_key, analytics, ttl)

    async def invalidate_campaign_cache(self, campaign_id: str) -> None:
        """Invalidate all cache entries for a campaign."""
        # This is a simplified implementation
        # In production, we'd need to track all keys for a campaign
        backlinking_logger.info(f"Invalidating cache for campaign: {campaign_id}")

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        return await self.cache.stats()

    def _hash_url(self, url: str) -> str:
        """Create a hash for URL-based cache keys."""
        return hashlib.md5(url.encode()).hexdigest()[:16]

    def _hash_keywords(self, keywords: str) -> str:
        """Create a hash for keyword-based cache keys."""
        # Sort keywords to ensure consistent hashing
        sorted_keywords = ','.join(sorted(keywords.split(',')))
        return hashlib.md5(sorted_keywords.encode()).hexdigest()[:16]


# Async operation utilities

@asynccontextmanager
async def timed_operation(operation_name: str):
    """
    Context manager for timing async operations.

    Usage:
        async with timed_operation("database_query"):
            result = await db.query(...)
    """
    start_time = time.time()
    backlinking_logger.debug(f"Starting operation: {operation_name}")

    try:
        yield
        duration = time.time() - start_time
        backlinking_logger.debug(
            f"Completed operation: {operation_name}",
            duration=f"{duration:.3f}s"
        )
    except Exception as e:
        duration = time.time() - start_time
        backlinking_logger.error(
            f"Failed operation: {operation_name}",
            error=str(e),
            duration=f"{duration:.3f}s"
        )
        raise


def cached_async(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator for caching async function results.

    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache keys

    Usage:
        @cached_async(ttl=600, key_prefix="api")
        async def api_call(param):
            return await expensive_operation(param)
    """
    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        cache = MemoryCache()

        async def wrapper(*args, **kwargs) -> Any:
            # Create cache key from function name and arguments
            key_parts = [key_prefix, func.__name__]
            key_parts.extend(str(arg) for arg in args if arg is not None)
            key_parts.extend(f"{k}:{v}" for k, v in kwargs.items() if v is not None)

            cache_key = ":".join(key_parts)
            cache_key = hashlib.md5(cache_key.encode()).hexdigest()

            # Try to get from cache first
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                backlinking_logger.debug(f"Cache hit for {func.__name__}")
                return cached_result

            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache.set(cache_key, result, ttl)

            backlinking_logger.debug(f"Cached result for {func.__name__}")
            return result

        return wrapper
    return decorator


class AsyncOperationManager:
    """
    Manager for optimizing async operations and resource usage.
    """

    def __init__(self):
        self.config = get_config()
        self.semaphore = asyncio.Semaphore(self.config.scraping.max_concurrent_requests)
        self.active_operations = 0

    async def execute_with_semaphore(self, coro: Awaitable[Any]) -> Any:
        """
        Execute an async operation with semaphore control.

        Args:
            coro: Coroutine to execute

        Returns:
            Result of the coroutine
        """
        async with self.semaphore:
            self.active_operations += 1
            try:
                result = await coro
                return result
            finally:
                self.active_operations -= 1

    async def execute_batch(self, coros: list, max_concurrent: Optional[int] = None) -> list:
        """
        Execute a batch of coroutines with controlled concurrency.

        Args:
            coros: List of coroutines to execute
            max_concurrent: Maximum concurrent operations

        Returns:
            List of results
        """
        if max_concurrent:
            semaphore = asyncio.Semaphore(max_concurrent)
        else:
            semaphore = self.semaphore

        async def execute_with_limit(coro):
            async with semaphore:
                return await coro

        tasks = [execute_with_limit(coro) for coro in coros]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Log any exceptions
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                backlinking_logger.error(
                    f"Batch operation {i} failed",
                    error=str(result)
                )

        return results

    def get_active_operations(self) -> int:
        """Get the number of currently active operations."""
        return self.active_operations


# Global instances
cache_manager = CacheManager()
async_manager = AsyncOperationManager()


def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    return cache_manager


def get_async_manager() -> AsyncOperationManager:
    """Get the global async operation manager instance."""
    return async_manager