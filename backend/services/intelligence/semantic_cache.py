"""
Enhanced Semantic Caching System for ALwrity SIF

Provides intelligent caching for semantic operations including:
- User-specific semantic indices with TTL management
- Query result caching with relevance-based invalidation
- Content analysis caching with versioning
- Intelligent cache warming based on user behavior
"""

import json
import hashlib
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from functools import wraps
import logging
from collections import OrderedDict
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Represents a cached semantic intelligence entry"""
    data: Any
    timestamp: float
    ttl: int  # Time to live in seconds
    version: str
    metadata: Dict[str, Any]
    access_count: int = 0
    last_accessed: float = 0.0


@dataclass
class SemanticCacheStats:
    """Statistics for semantic cache performance"""
    total_hits: int = 0
    total_misses: int = 0
    total_invalidations: int = 0
    cache_size: int = 0
    memory_usage_mb: float = 0.0
    average_hit_time_ms: float = 0.0
    hit_rate: float = 0.0


class SemanticCacheManager:
    """
    Intelligent caching system for semantic intelligence operations
    
    Features:
    - Multi-tier caching (memory + persistent)
    - TTL-based expiration with intelligent defaults
    - Relevance-based cache invalidation
    - User-specific semantic index isolation
    - Performance monitoring and analytics
    """
    
    def __init__(
        self,
        max_memory_size_mb: int = 512,
        default_ttl_seconds: int = 3600,
        cleanup_interval_seconds: int = 300,
        enable_persistent_cache: bool = True,
        cache_dir: str = "/tmp/semantic_cache"
    ):
        self.max_memory_size_mb = max_memory_size_mb
        self.default_ttl = default_ttl_seconds
        self.cleanup_interval = cleanup_interval_seconds
        self.enable_persistent_cache = enable_persistent_cache
        self.cache_dir = cache_dir
        
        # In-memory cache with LRU eviction
        self.memory_cache: Dict[str, CacheEntry] = OrderedDict()
        self.user_indices: Dict[str, str] = {}  # user_id -> index_hash mapping
        
        # Statistics
        self.stats = SemanticCacheStats()
        self._stats_lock = asyncio.Lock()
        
        # Thread pool for background operations
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Start background cleanup task (optional - can be started manually)
        self.cleanup_task = None
        if cleanup_interval_seconds > 0:
            # Note: Cleanup task should be started manually in async context
            pass
        
        logger.info(f"SemanticCacheManager initialized with {max_memory_size_mb}MB limit")
    
    def _generate_cache_key(
        self, 
        operation: str, 
        user_id: str, 
        params: Dict[str, Any]
    ) -> str:
        """Generate a unique cache key for semantic operations"""
        # Create deterministic key from operation, user, and parameters
        key_data = {
            "operation": operation,
            "user_id": user_id,
            "params": self._serialize_params(params)
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()
    
    def _serialize_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize parameters for consistent hashing"""
        serialized = {}
        for key, value in params.items():
            if isinstance(value, (list, dict)):
                serialized[key] = json.dumps(value, sort_keys=True)
            else:
                serialized[key] = str(value)
        return serialized
    
    def _is_entry_valid(self, entry: CacheEntry) -> bool:
        """Check if cache entry is still valid"""
        current_time = time.time()
        
        # Check TTL expiration
        if current_time - entry.timestamp > entry.ttl:
            return False
        
        # Check version compatibility (semantic analysis versions)
        if entry.version != self._get_current_version():
            return False
        
        return True
    
    def _get_current_version(self) -> str:
        """Get current semantic analysis version"""
        # This could be based on model versions, algorithm updates, etc.
        return "v1.0.0"
    
    def _calculate_memory_usage(self) -> float:
        """Calculate current memory usage in MB"""
        total_size = 0
        for entry in self.memory_cache.values():
            # Rough estimation of memory usage
            entry_size = len(json.dumps(asdict(entry)).encode())
            total_size += entry_size
        
        return total_size / (1024 * 1024)  # Convert to MB
    
    def _evict_lru_entries(self, target_size_mb: float):
        """Evict least recently used entries to meet memory target"""
        current_size = self._calculate_memory_usage()
        
        while current_size > target_size_mb and self.memory_cache:
            # Remove oldest entry
            oldest_key = next(iter(self.memory_cache))
            del self.memory_cache[oldest_key]
            current_size = self._calculate_memory_usage()
            
            logger.debug(f"Evicted cache entry: {oldest_key}")
    
    def _periodic_cleanup(self):
        """Background task to clean up expired entries"""
        while True:
            try:
                time.sleep(self.cleanup_interval)
                self.cleanup_expired_entries()
                
                # Update statistics
                self.stats.cache_size = len(self.memory_cache)
                self.stats.memory_usage_mb = self._calculate_memory_usage()
                    
            except Exception as e:
                logger.error(f"Error in periodic cleanup: {e}")
    
    def cache_semantic_insights(
        self,
        user_id: str,
        insights: Dict[str, Any],
        ttl: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Cache semantic insights for a user
        
        Args:
            user_id: User identifier
            insights: Semantic insights data
            ttl: Time to live in seconds (uses default if None)
            metadata: Additional metadata for cache management
            
        Returns:
            True if caching was successful
        """
        try:
            cache_key = self._generate_cache_key(
                "semantic_insights", 
                user_id, 
                {"timestamp": time.time()}
            )
            
            entry = CacheEntry(
                data=insights,
                timestamp=time.time(),
                ttl=ttl or self.default_ttl,
                version=self._get_current_version(),
                metadata=metadata or {},
                access_count=1,
                last_accessed=time.time()
            )
            
            # Check memory limit before adding
            projected_size = self._calculate_memory_usage() + (
                len(json.dumps(insights).encode()) / (1024 * 1024)
            )
            
            if projected_size > self.max_memory_size_mb:
                # Evict old entries to make room
                self._evict_lru_entries(self.max_memory_size_mb * 0.8)
            
            self.memory_cache[cache_key] = entry
            self.memory_cache.move_to_end(cache_key)  # Mark as recently used
            
            # Update user index mapping
            self.user_indices[user_id] = cache_key
            
            logger.info(f"Cached semantic insights for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache semantic insights: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get current cache statistics"""
        return asdict(self.stats)

    def clear_cache(self) -> bool:
        """Clear all cache entries"""
        try:
            self.memory_cache.clear()
            self.stats.cache_size = 0
            self.stats.memory_usage_mb = 0.0
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    def get_cached_semantic_insights(
        self, 
        user_id: str,
        force_refresh: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached semantic insights for a user
        
        Args:
            user_id: User identifier
            force_refresh: Force cache refresh even if valid
            
        Returns:
            Cached insights or None if not found/expired
        """
        try:
            cache_key = self.user_indices.get(user_id)
            if not cache_key:
                self.stats.total_misses += 1
                return None
            
            entry = self.memory_cache.get(cache_key)
            if not entry:
                self.stats.total_misses += 1
                return None
            
            # Check validity
            if not self._is_entry_valid(entry) or force_refresh:
                del self.memory_cache[cache_key]
                del self.user_indices[user_id]
                self.stats.total_invalidations += 1
                return None
            
            # Update access statistics
            entry.access_count += 1
            entry.last_accessed = time.time()
            self.memory_cache.move_to_end(cache_key)
            
            self.stats.total_hits += 1
                
            logger.debug(f"Retrieved cached semantic insights for user {user_id}")
            return entry.data
            
        except Exception as e:
            logger.error(f"Failed to retrieve cached semantic insights: {e}")
            return None
    
    def cache_query_results(
        self,
        query: str,
        results: List[Dict[str, Any]],
        relevance_threshold: float = 0.7,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Cache semantic search query results with relevance-based invalidation
        
        Args:
            query: Search query
            results: Query results
            relevance_threshold: Minimum relevance score for caching
            ttl: Time to live in seconds
            
        Returns:
            True if caching was successful
        """
        try:
            # Only cache high-quality results
            if not results or max(r.get('score', 0) for r in results) < relevance_threshold:
                return False
            
            cache_key = self._generate_cache_key(
                "semantic_query",
                "global",  # Global query cache
                {"query": query, "threshold": relevance_threshold}
            )
            
            entry = CacheEntry(
                data=results,
                timestamp=time.time(),
                ttl=ttl or (self.default_ttl // 2),  # Shorter TTL for queries
                version=self._get_current_version(),
                metadata={
                    "query": query,
                    "relevance_threshold": relevance_threshold,
                    "result_count": len(results)
                }
            )
            
            self.memory_cache[cache_key] = entry
            self.memory_cache.move_to_end(cache_key)
            
            logger.info(f"Cached semantic query results for: {query}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache query results: {e}")
            return False
    
    def get_cached_query_results(
        self,
        query: str,
        relevance_threshold: float = 0.7
    ) -> Optional[List[Dict[str, Any]]]:
        """Retrieve cached semantic query results"""
        try:
            cache_key = self._generate_cache_key(
                "semantic_query",
                "global",
                {"query": query, "threshold": relevance_threshold}
            )
            
            entry = self.memory_cache.get(cache_key)
            if not entry or not self._is_entry_valid(entry):
                return None
            
            # Update access statistics
            entry.access_count += 1
            entry.last_accessed = time.time()
            self.memory_cache.move_to_end(cache_key)
            
            logger.debug(f"Retrieved cached query results for: {query}")
            return entry.data
            
        except Exception as e:
            logger.error(f"Failed to retrieve cached query results: {e}")
            return None
    
    def invalidate_user_cache(self, user_id: str, operation_type: Optional[str] = None):
        """
        Invalidate cache entries for a specific user
        
        Args:
            user_id: User identifier
            operation_type: Specific operation type to invalidate (optional)
        """
        try:
            keys_to_remove = []
            
            # Check user index mapping first
            if user_id in self.user_indices:
                cache_key = self.user_indices[user_id]
                if cache_key in self.memory_cache:
                    entry = self.memory_cache[cache_key]
                    if operation_type is None or entry.metadata.get("operation") == operation_type:
                        keys_to_remove.append(cache_key)
            
            # Also check all cache entries for user_id in metadata
            for cache_key, entry in list(self.memory_cache.items()):
                if entry.metadata.get("user_id") == user_id:
                    if operation_type is None or entry.metadata.get("operation") == operation_type:
                        if cache_key not in keys_to_remove:
                            keys_to_remove.append(cache_key)
            
            # Remove identified keys
            for key in keys_to_remove:
                if key in self.memory_cache:
                    del self.memory_cache[key]
                    # Clean up user index mapping
                    user_keys = [k for k, v in self.user_indices.items() if v == key]
                    for user_key in user_keys:
                        if user_key in self.user_indices:
                            del self.user_indices[user_key]
            
            logger.info(f"Invalidated {len(keys_to_remove)} cache entries for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to invalidate user cache: {e}")
    
    def invalidate_on_content_update(self, user_id: str, content_type: str):
        """
        Invalidate relevant cache entries when user content is updated
        
        Args:
            user_id: User identifier
            content_type: Type of content updated (e.g., 'blog_post', 'page', etc.)
        """
        try:
            # Invalidate semantic insights for this user
            self.invalidate_user_cache(user_id, "semantic_insights")
            
            # Invalidate related query caches
            if content_type in ["blog_post", "page", "content"]:
                # Invalidate pillar-related caches
                self.invalidate_user_cache(user_id, "semantic_pillars")
                
            logger.info(f"Invalidated cache for user {user_id} content update: {content_type}")
            
        except Exception as e:
            logger.error(f"Failed to invalidate cache on content update: {e}")
    
    def cleanup_expired_entries(self):
        """Clean up expired cache entries"""
        try:
            expired_keys = []
            current_time = time.time()
            
            for cache_key, entry in self.memory_cache.items():
                if not self._is_entry_valid(entry):
                    expired_keys.append(cache_key)
            
            for key in expired_keys:
                del self.memory_cache[key]
                # Clean up user index mapping
                user_keys = [k for k, v in self.user_indices.items() if v == key]
                for user_key in user_keys:
                    del self.user_indices[user_key]
            
            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
                
        except Exception as e:
            logger.error(f"Error during cache cleanup: {e}")
    
    def get_cache_stats(self) -> SemanticCacheStats:
        """Get current cache statistics"""
        try:
            # Calculate hit rate
            total_requests = self.stats.total_hits + self.stats.total_misses
            if total_requests > 0:
                self.stats.hit_rate = self.stats.total_hits / total_requests
            
            # Update current stats
            self.stats.cache_size = len(self.memory_cache)
            self.stats.memory_usage_mb = self._calculate_memory_usage()
            
            return self.stats
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return self.stats
    
    def warm_cache_for_user(self, user_id: str, common_queries: List[str]):
        """
        Pre-populate cache with common semantic queries for a user
        
        Args:
            user_id: User identifier
            common_queries: List of common semantic queries to pre-cache
        """
        try:
            logger.info(f"Warming cache for user {user_id} with {len(common_queries)} queries")
            
            # This would typically involve running the actual semantic analysis
            # For now, we log the intent and can be extended with actual warming logic
            
            # Example warming scenarios:
            # 1. Pre-analyze user's top content pillars
            # 2. Cache common competitor comparisons
            # 3. Pre-compute semantic similarity scores
            
            logger.info(f"Cache warming initiated for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to warm cache for user: {e}")


def semantic_cache_decorator(ttl: int = 3600, operation_type: str = "generic"):
    """
    Decorator for caching semantic intelligence operations
    
    Args:
        ttl: Time to live in seconds
        operation_type: Type of semantic operation being cached
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Get cache manager instance (assumes it's available as self.cache_manager)
            cache_manager = getattr(self, 'cache_manager', None)
            if not cache_manager:
                return await func(self, *args, **kwargs)
            
            # Generate cache key from function and arguments
            user_id = kwargs.get('user_id') or (args[0] if args else 'unknown')
            cache_key = cache_manager._generate_cache_key(
                operation_type,
                user_id,
                {"args": args, "kwargs": kwargs}
            )
            
            # Try to get from cache
            cached_result = cache_manager.memory_cache.get(cache_key)
            if cached_result and cache_manager._is_entry_valid(cached_result):
                logger.debug(f"Cache hit for {operation_type} operation")
                return cached_result.data
            
            # Execute function and cache result
            result = await func(self, *args, **kwargs)
            
            if result:
                entry = CacheEntry(
                    data=result,
                    timestamp=time.time(),
                    ttl=ttl,
                    version=cache_manager._get_current_version(),
                    metadata={"operation": operation_type, "user_id": user_id}
                )
                cache_manager.memory_cache[cache_key] = entry
            
            return result
        
        return wrapper
    return decorator


# Global cache manager instance
semantic_cache_manager = SemanticCacheManager()