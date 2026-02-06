"""
Platform Connection Manager

Manages platform connection status checking and caching across all analytics platforms.
"""

from typing import Dict, Any, List
from utils.logging import get_logger
logger = get_logger("analytics_connection_manager", migration_mode=True)

from ..analytics_cache_service import analytics_cache
from .handlers import (
    GSCAnalyticsHandler,
    BingAnalyticsHandler, 
    WordPressAnalyticsHandler,
    WixAnalyticsHandler
)
from .models.platform_types import PlatformType


class PlatformConnectionManager:
    """Manages platform connection status across all analytics platforms"""
    
    def __init__(self):
        self.handlers = {
            PlatformType.GSC: GSCAnalyticsHandler(),
            PlatformType.BING: BingAnalyticsHandler(),
            PlatformType.WORDPRESS: WordPressAnalyticsHandler(),
            PlatformType.WIX: WixAnalyticsHandler()
        }
    
    async def get_platform_connection_status(self, user_id: str) -> Dict[str, Dict[str, Any]]:
        """
        Check connection status for all platforms
        
        Returns:
            Dictionary with connection status for each platform
        """
        # Check cache first - connection status doesn't change frequently
        cached_status = analytics_cache.get('platform_status', user_id)
        if cached_status:
            logger.info("Using cached platform connection status for user {user_id}", user_id=user_id)
            return cached_status
        
        logger.info("Fetching fresh platform connection status for user {user_id}", user_id=user_id)
        status = {}
        
        # Check each platform connection
        for platform_type, handler in self.handlers.items():
            platform_name = platform_type.value
            try:
                status[platform_name] = handler.get_connection_status(user_id)
            except Exception as e:
                logger.error(f"Error checking {platform_name} connection status: {e}")
                status[platform_name] = {
                    'connected': False,
                    'sites_count': 0,
                    'sites': [],
                    'error': str(e)
                }
        
        # Cache the connection status
        analytics_cache.set('platform_status', user_id, status)
        logger.info("Cached platform connection status for user {user_id}", user_id=user_id)
        
        return status
    
    def get_connected_platforms(self, user_id: str, status_data: Dict[str, Dict[str, Any]] = None) -> List[str]:
        """
        Get list of connected platform names
        
        Args:
            user_id: User ID
            status_data: Optional pre-fetched status data
            
        Returns:
            List of connected platform names
        """
        if status_data is None:
            # This would need to be async, but for now return empty list
            # In practice, this method should be called with pre-fetched status
            return []
        
        connected_platforms = []
        for platform_name, status in status_data.items():
            if status.get('connected', False):
                connected_platforms.append(platform_name)
        
        return connected_platforms
    
    def get_platform_sites_count(self, user_id: str, platform_name: str, status_data: Dict[str, Dict[str, Any]] = None) -> int:
        """
        Get sites count for a specific platform
        
        Args:
            user_id: User ID
            platform_name: Name of the platform
            status_data: Optional pre-fetched status data
            
        Returns:
            Number of connected sites for the platform
        """
        if status_data is None:
            return 0
        
        platform_status = status_data.get(platform_name, {})
        return platform_status.get('sites_count', 0)
    
    def is_platform_connected(self, user_id: str, platform_name: str, status_data: Dict[str, Dict[str, Any]] = None) -> bool:
        """
        Check if a specific platform is connected
        
        Args:
            user_id: User ID
            platform_name: Name of the platform
            status_data: Optional pre-fetched status data
            
        Returns:
            True if platform is connected, False otherwise
        """
        if status_data is None:
            return False
        
        platform_status = status_data.get(platform_name, {})
        return platform_status.get('connected', False)
    
    def get_platform_error(self, user_id: str, platform_name: str, status_data: Dict[str, Dict[str, Any]] = None) -> str:
        """
        Get error message for a specific platform
        
        Args:
            user_id: User ID
            platform_name: Name of the platform
            status_data: Optional pre-fetched status data
            
        Returns:
            Error message if any, None otherwise
        """
        if status_data is None:
            return None
        
        platform_status = status_data.get(platform_name, {})
        return platform_status.get('error')
    
    def invalidate_connection_cache(self, user_id: str):
        """
        Invalidate connection status cache for a user
        
        Args:
            user_id: User ID to invalidate cache for
        """
        analytics_cache.invalidate('platform_status', user_id)
        logger.info("Invalidated platform connection status cache for user {user_id}", user_id=user_id)
