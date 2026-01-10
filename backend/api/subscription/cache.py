"""
Cache management for subscription API endpoints.
"""

from typing import Dict, Any
import time
import os


# Simple in-process cache for dashboard responses to smooth bursts
# Cache key: (user_id). TTL-like behavior implemented via timestamp check
_dashboard_cache: Dict[str, Dict[str, Any]] = {}
_dashboard_cache_ts: Dict[str, float] = {}
_DASHBOARD_CACHE_TTL_SEC = 600.0


def get_cached_dashboard(user_id: str) -> Dict[str, Any] | None:
    """
    Get cached dashboard data if available and not expired.
    
    Args:
        user_id: User ID to get cached data for
        
    Returns:
        Cached dashboard data or None if not cached/expired
    """
    # Check if caching is disabled via environment variable
    nocache = False
    try:
        nocache = os.getenv('SUBSCRIPTION_DASHBOARD_NOCACHE', 'false').lower() in {'1', 'true', 'yes', 'on'}
    except Exception:
        nocache = False
    
    if nocache:
        return None
    
    now = time.time()
    if user_id in _dashboard_cache and (now - _dashboard_cache_ts.get(user_id, 0)) < _DASHBOARD_CACHE_TTL_SEC:
        return _dashboard_cache[user_id]
    
    return None


def set_cached_dashboard(user_id: str, data: Dict[str, Any]) -> None:
    """
    Cache dashboard data for a user.
    
    Args:
        user_id: User ID to cache data for
        data: Dashboard data to cache
    """
    _dashboard_cache[user_id] = data
    _dashboard_cache_ts[user_id] = time.time()


def clear_dashboard_cache(user_id: str | None = None) -> None:
    """
    Clear dashboard cache for a specific user or all users.
    
    Args:
        user_id: User ID to clear cache for, or None to clear all
    """
    if user_id:
        _dashboard_cache.pop(user_id, None)
        _dashboard_cache_ts.pop(user_id, None)
    else:
        _dashboard_cache.clear()
        _dashboard_cache_ts.clear()
