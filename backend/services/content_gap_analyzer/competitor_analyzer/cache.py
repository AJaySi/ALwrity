"""
Caching utilities for competitor analyzer results.
"""

import hashlib
import json
import time
from typing import Dict, Any, Optional, Union
from functools import lru_cache
from datetime import datetime, timedelta
from loguru import logger

class AnalysisCache:
    """
    Smart caching system for competitor analysis results.
    
    Features:
    - TTL-based cache expiration
    - Content-aware cache keys
    - Memory-efficient storage
    - Cache hit/miss statistics
    """
    
    def __init__(self, 
                 default_ttl: int = 3600,  # 1 hour
                 max_cache_size: int = 1000):
        self.default_ttl = default_ttl
        self.max_cache_size = max_cache_size
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
        
        logger.info(f"✅ AnalysisCache initialized - TTL: {default_ttl}s, Max size: {max_cache_size}")
    
    def _generate_cache_key(self, 
                          url: str, 
                          industry: str, 
                          keywords: Optional[list] = None,
                          analysis_depth: str = "comprehensive") -> str:
        """
        Generate a consistent cache key based on analysis parameters.
        """
        # Create normalized input data
        cache_data = {
            'url': url.lower().strip(),
            'industry': industry.lower().strip(),
            'keywords': sorted(keywords or []),
            'analysis_depth': analysis_depth
        }
        
        # Generate hash
        content = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, 
            url: str, 
            industry: str, 
            keywords: Optional[list] = None,
            analysis_depth: str = "comprehensive") -> Optional[Dict[str, Any]]:
        """
        Get cached analysis result.
        """
        cache_key = self._generate_cache_key(url, industry, keywords, analysis_depth)
        
        if cache_key not in self._cache:
            self._stats['misses'] += 1
            return None
        
        cache_entry = self._cache[cache_key]
        
        # Check TTL
        if time.time() > cache_entry['expires_at']:
            del self._cache[cache_key]
            self._stats['misses'] += 1
            logger.debug(f"Cache expired for {cache_key}")
            return None
        
        self._stats['hits'] += 1
        logger.debug(f"Cache hit for {cache_key}")
        return cache_entry['data']
    
    def set(self, 
            url: str, 
            industry: str, 
            data: Dict[str, Any],
            keywords: Optional[list] = None,
            analysis_depth: str = "comprehensive",
            ttl: Optional[int] = None) -> None:
        """
        Cache analysis result with TTL.
        """
        cache_key = self._generate_cache_key(url, industry, keywords, analysis_depth)
        
        # Evict oldest entries if cache is full
        if len(self._cache) >= self.max_cache_size:
            self._evict_oldest()
        
        ttl = ttl or self.default_ttl
        cache_entry = {
            'data': data,
            'created_at': time.time(),
            'expires_at': time.time() + ttl,
            'ttl': ttl,
            'cache_key': cache_key
        }
        
        self._cache[cache_key] = cache_entry
        logger.debug(f"Cached analysis for {cache_key} (TTL: {ttl}s)")
    
    def _evict_oldest(self) -> None:
        """Evict the oldest cache entry."""
        if not self._cache:
            return
        
        oldest_key = min(self._cache.keys(), 
                        key=lambda k: self._cache[k]['created_at'])
        del self._cache[oldest_key]
        self._stats['evictions'] += 1
        logger.debug(f"Evicted cache entry: {oldest_key}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        total_requests = self._stats['hits'] + self._stats['misses']
        hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_size': len(self._cache),
            'max_cache_size': self.max_cache_size,
            'hits': self._stats['hits'],
            'misses': self._stats['misses'],
            'evictions': self._stats['evictions'],
            'hit_rate_percent': round(hit_rate, 2),
            'total_requests': total_requests
        }
    
    def cleanup_expired(self) -> int:
        """Remove all expired entries."""
        current_time = time.time()
        keys_to_remove = []
        
        for cache_key, cache_entry in self._cache.items():
            if current_time > cache_entry['expires_at']:
                keys_to_remove.append(cache_key)
        
        for key in keys_to_remove:
            del self._cache[key]
        
        logger.info(f"Cleaned up {len(keys_to_remove)} expired cache entries")
        return len(keys_to_remove)


# Global cache instance
_analysis_cache = AnalysisCache()

def get_analysis_cache() -> AnalysisCache:
    """Get the global analysis cache instance."""
    return _analysis_cache


# Decorator for caching analysis methods
def cached_analysis(ttl: int = 3600):
    """
    Decorator to cache analysis method results.
    
    Args:
        ttl: Time to live in seconds
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract cacheable parameters
            url = kwargs.get('url') or (args[1] if len(args) > 1 else None)
            industry = kwargs.get('industry') or (args[2] if len(args) > 2 else None)
            keywords = kwargs.get('target_keywords')
            analysis_depth = kwargs.get('analysis_depth', 'comprehensive')
            
            if not url or not industry:
                # Skip caching if required parameters missing
                return await func(*args, **kwargs)
            
            # Try to get from cache
            cache = get_analysis_cache()
            cached_result = cache.get(url, industry, keywords, analysis_depth)
            
            if cached_result is not None:
                return cached_result
            
            # Execute analysis and cache result
            result = await func(*args, **kwargs)
            
            if result:  # Only cache successful results
                cache.set(url, industry, result, keywords, analysis_depth, ttl)
            
            return result
        
        return wrapper
    return decorator


# LRU Cache for frequently accessed data
@lru_cache(maxsize=128)
def get_industry_benchmarks(industry: str) -> Dict[str, Any]:
    """
    Get industry benchmarks (cached with LRU).
    
    Args:
        industry: Industry category
        
    Returns:
        Industry benchmark data
    """
    # This would typically fetch from database or external API
    benchmarks = {
        'ecommerce': {
            'avg_content_quality': 7.5,
            'avg_domain_authority': 45,
            'avg_content_frequency': 'weekly'
        },
        'saas': {
            'avg_content_quality': 8.2,
            'avg_domain_authority': 52,
            'avg_content_frequency': 'bi-weekly'
        },
        'blog': {
            'avg_content_quality': 6.8,
            'avg_domain_authority': 38,
            'avg_content_frequency': 'daily'
        }
    }
    
    return benchmarks.get(industry.lower(), {
        'avg_content_quality': 7.0,
        'avg_domain_authority': 40,
        'avg_content_frequency': 'weekly'
    })

