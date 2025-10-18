"""
Platform Analytics Service (Refactored)

Streamlined orchestrator service for platform analytics with modular architecture.
"""

from typing import Dict, Any, List, Optional
from loguru import logger

from .models.analytics_data import AnalyticsData
from .models.platform_types import PlatformType, DEFAULT_PLATFORMS
from .handlers import (
    GSCAnalyticsHandler,
    BingAnalyticsHandler,
    WordPressAnalyticsHandler,
    WixAnalyticsHandler
)
from .connection_manager import PlatformConnectionManager
from .summary_generator import AnalyticsSummaryGenerator
from .cache_manager import AnalyticsCacheManager


class PlatformAnalyticsService:
    """
    Streamlined service for retrieving analytics data from connected platforms.
    
    This service orchestrates platform handlers, manages caching, and provides
    comprehensive analytics summaries.
    """
    
    def __init__(self):
        # Initialize platform handlers
        self.handlers = {
            PlatformType.GSC: GSCAnalyticsHandler(),
            PlatformType.BING: BingAnalyticsHandler(),
            PlatformType.WORDPRESS: WordPressAnalyticsHandler(),
            PlatformType.WIX: WixAnalyticsHandler()
        }
        
        # Initialize managers
        self.connection_manager = PlatformConnectionManager()
        self.summary_generator = AnalyticsSummaryGenerator()
        self.cache_manager = AnalyticsCacheManager()
    
    async def get_comprehensive_analytics(self, user_id: str, platforms: List[str] = None) -> Dict[str, AnalyticsData]:
        """
        Get analytics data from all connected platforms
        
        Args:
            user_id: User ID to get analytics for
            platforms: List of platforms to get data from (None = all available)
            
        Returns:
            Dictionary of platform analytics data
        """
        if platforms is None:
            platforms = [p.value for p in DEFAULT_PLATFORMS]
        
        logger.info(f"Getting comprehensive analytics for user {user_id}, platforms: {platforms}")
        analytics_data = {}
        
        for platform_name in platforms:
            try:
                # Convert string to PlatformType enum
                platform_type = PlatformType(platform_name)
                handler = self.handlers.get(platform_type)
                
                if handler:
                    analytics_data[platform_name] = await handler.get_analytics(user_id)
                else:
                    logger.warning(f"Unknown platform: {platform_name}")
                    analytics_data[platform_name] = self._create_error_response(platform_name, f"Unknown platform: {platform_name}")
                    
            except ValueError:
                logger.warning(f"Invalid platform name: {platform_name}")
                analytics_data[platform_name] = self._create_error_response(platform_name, f"Invalid platform name: {platform_name}")
            except Exception as e:
                logger.error(f"Failed to get analytics for {platform_name}: {e}")
                analytics_data[platform_name] = self._create_error_response(platform_name, str(e))
        
        return analytics_data
    
    async def get_platform_connection_status(self, user_id: str) -> Dict[str, Dict[str, Any]]:
        """
        Check connection status for all platforms
        
        Returns:
            Dictionary with connection status for each platform
        """
        return await self.connection_manager.get_platform_connection_status(user_id)
    
    def get_analytics_summary(self, analytics_data: Dict[str, AnalyticsData]) -> Dict[str, Any]:
        """
        Generate a summary of analytics data across all platforms
        
        Args:
            analytics_data: Dictionary of platform analytics data
            
        Returns:
            Summary statistics and insights
        """
        return self.summary_generator.get_analytics_summary(analytics_data)
    
    def get_platform_comparison(self, analytics_data: Dict[str, AnalyticsData]) -> Dict[str, Any]:
        """Generate platform comparison metrics"""
        return self.summary_generator.get_platform_comparison(analytics_data)
    
    def get_trend_analysis(self, analytics_data: Dict[str, AnalyticsData]) -> Dict[str, Any]:
        """Generate trend analysis (placeholder for future implementation)"""
        return self.summary_generator.get_trend_analysis(analytics_data)
    
    def invalidate_platform_cache(self, user_id: str, platform: str = None):
        """
        Invalidate cache for platform connections and analytics
        
        Args:
            user_id: User ID to invalidate cache for
            platform: Specific platform to invalidate (optional, invalidates all if None)
        """
        if platform:
            try:
                platform_type = PlatformType(platform)
                self.cache_manager.invalidate_platform_cache(platform_type, user_id)
                logger.info(f"Invalidated {platform} cache for user {user_id}")
            except ValueError:
                logger.warning(f"Invalid platform name for cache invalidation: {platform}")
        else:
            self.cache_manager.invalidate_user_cache(user_id)
            logger.info(f"Invalidated all platform caches for user {user_id}")
    
    def invalidate_connection_cache(self, user_id: str):
        """Invalidate platform connection status cache"""
        self.cache_manager.invalidate_platform_status_cache(user_id)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self.cache_manager.get_cache_stats()
    
    def clear_all_cache(self):
        """Clear all analytics cache"""
        self.cache_manager.clear_all_cache()
    
    def get_supported_platforms(self) -> List[str]:
        """Get list of supported platforms"""
        return [p.value for p in PlatformType]
    
    def get_platform_handler(self, platform: str) -> Optional[Any]:
        """Get handler for a specific platform"""
        try:
            platform_type = PlatformType(platform)
            return self.handlers.get(platform_type)
        except ValueError:
            return None
    
    def _create_error_response(self, platform_name: str, error_message: str) -> AnalyticsData:
        """Create a standardized error response"""
        from datetime import datetime
        
        return AnalyticsData(
            platform=platform_name,
            metrics={},
            date_range={'start': '', 'end': ''},
            last_updated=datetime.now().isoformat(),
            status='error',
            error_message=error_message
        )
