"""
Analytics Cache Manager

Provides a unified interface for caching analytics data with platform-specific configurations.
"""

from typing import Dict, Any, Optional
from utils.logging import get_logger
logger = get_logger("analytics_cache_manager", migration_mode=True)

from ..analytics_cache_service import analytics_cache
from .models.platform_types import PlatformType


class AnalyticsCacheManager:
    """Manages caching for analytics data with platform-specific TTL configurations"""
    
    def __init__(self):
        # Platform-specific cache TTL configurations (in seconds)
        self.cache_ttl = {
            PlatformType.GSC: 3600,        # 1 hour
            PlatformType.BING: 3600,       # 1 hour (expensive operation)
            PlatformType.WORDPRESS: 1800,  # 30 minutes
            PlatformType.WIX: 1800,        # 30 minutes
            'platform_status': 1800,       # 30 minutes
            'analytics_summary': 900,      # 15 minutes
        }
    
    def get_cached_analytics(self, platform: PlatformType, user_id: str) -> Optional[Dict[str, Any]]:
        """Get cached analytics data for a platform"""
        cache_key = f"{platform.value}_analytics"
        cached_data = analytics_cache.get(cache_key, user_id)
        
        if cached_data:
            logger.info(f"Cache HIT: {platform.value} analytics for user {user_id}")
            return cached_data
        
        logger.info(f"Cache MISS: {platform.value} analytics for user {user_id}")
        return None
    
    def set_cached_analytics(self, platform: PlatformType, user_id: str, data: Dict[str, Any], ttl_override: Optional[int] = None):
        """Cache analytics data for a platform"""
        cache_key = f"{platform.value}_analytics"
        ttl = ttl_override or self.cache_ttl.get(platform, 1800)  # Default 30 minutes
        
        analytics_cache.set(cache_key, user_id, data, ttl_override=ttl)
        logger.info(f"Cached {platform.value} analytics for user {user_id} (TTL: {ttl}s)")
    
    def get_cached_platform_status(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get cached platform connection status"""
        cached_data = analytics_cache.get('platform_status', user_id)
        
        if cached_data:
            logger.info(f"Cache HIT: platform status for user {user_id}")
            return cached_data
        
        logger.info(f"Cache MISS: platform status for user {user_id}")
        return None
    
    def set_cached_platform_status(self, user_id: str, status_data: Dict[str, Any]):
        """Cache platform connection status"""
        ttl = self.cache_ttl['platform_status']
        analytics_cache.set('platform_status', user_id, status_data, ttl_override=ttl)
        logger.info(f"Cached platform status for user {user_id} (TTL: {ttl}s)")
    
    def get_cached_summary(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get cached analytics summary"""
        cached_data = analytics_cache.get('analytics_summary', user_id)
        
        if cached_data:
            logger.info(f"Cache HIT: analytics summary for user {user_id}")
            return cached_data
        
        logger.info(f"Cache MISS: analytics summary for user {user_id}")
        return None
    
    def set_cached_summary(self, user_id: str, summary_data: Dict[str, Any]):
        """Cache analytics summary"""
        ttl = self.cache_ttl['analytics_summary']
        analytics_cache.set('analytics_summary', user_id, summary_data, ttl_override=ttl)
        logger.info(f"Cached analytics summary for user {user_id} (TTL: {ttl}s)")
    
    def invalidate_platform_cache(self, platform: PlatformType, user_id: str):
        """Invalidate cache for a specific platform"""
        cache_key = f"{platform.value}_analytics"
        analytics_cache.invalidate(cache_key, user_id)
        logger.info(f"Invalidated {platform.value} analytics cache for user {user_id}")
    
    def invalidate_user_cache(self, user_id: str):
        """Invalidate all cache entries for a user"""
        analytics_cache.invalidate_user(user_id)
        logger.info(f"Invalidated all analytics cache for user {user_id}")
    
    def invalidate_platform_status_cache(self, user_id: str):
        """Invalidate platform status cache for a user"""
        analytics_cache.invalidate('platform_status', user_id)
        logger.info(f"Invalidated platform status cache for user {user_id}")
    
    def invalidate_summary_cache(self, user_id: str):
        """Invalidate analytics summary cache for a user"""
        analytics_cache.invalidate('analytics_summary', user_id)
        logger.info(f"Invalidated analytics summary cache for user {user_id}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return analytics_cache.get_stats()
    
    def clear_all_cache(self):
        """Clear all analytics cache"""
        analytics_cache.clear_all()
        logger.info("Cleared all analytics cache")
