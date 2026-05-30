"""
Cache management for subscription API endpoints.

Delegates to the canonical implementation in services/subscription/cache.py.
All cache state lives there so service-layer code can invalidate without
importing from the API layer.
"""

from services.subscription.cache import (
    get_cached_dashboard,
    set_cached_dashboard,
    clear_dashboard_cache,
)

__all__ = [
    "get_cached_dashboard",
    "set_cached_dashboard",
    "clear_dashboard_cache",
]
