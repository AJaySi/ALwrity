"""
Base Analytics Handler

Abstract base class for platform-specific analytics handlers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

from ..models.analytics_data import AnalyticsData
from ..models.platform_types import PlatformType


class BaseAnalyticsHandler(ABC):
    """Abstract base class for platform analytics handlers"""
    
    def __init__(self, platform_type: PlatformType):
        self.platform_type = platform_type
        self.platform_name = platform_type.value
    
    @abstractmethod
    async def get_analytics(self, user_id: str, **kwargs) -> AnalyticsData:
        """
        Get analytics data for the platform
        
        Args:
            user_id: User ID to get analytics for
            **kwargs: Additional arguments for specific handlers
            
        Returns:
            AnalyticsData object with platform metrics
        """
        pass
    
    @abstractmethod
    def get_connection_status(self, user_id: str) -> Dict[str, Any]:
        """
        Get connection status for the platform
        
        Args:
            user_id: User ID to check connection for
            
        Returns:
            Dictionary with connection status information
        """
        pass
    
    def create_error_response(self, error_message: str) -> AnalyticsData:
        """Create a standardized error response"""
        return AnalyticsData(
            platform=self.platform_name,
            metrics={},
            date_range={'start': '', 'end': ''},
            last_updated=datetime.now().isoformat(),
            status='error',
            error_message=error_message
        )
    
    def create_partial_response(self, metrics: Dict[str, Any], error_message: str = None) -> AnalyticsData:
        """Create a standardized partial response"""
        return AnalyticsData(
            platform=self.platform_name,
            metrics=metrics,
            date_range={'start': '', 'end': ''},
            last_updated=datetime.now().isoformat(),
            status='partial',
            error_message=error_message
        )
    
    def create_success_response(self, metrics: Dict[str, Any], date_range: Dict[str, str] = None) -> AnalyticsData:
        """Create a standardized success response"""
        return AnalyticsData(
            platform=self.platform_name,
            metrics=metrics,
            date_range=date_range or {'start': '', 'end': ''},
            last_updated=datetime.now().isoformat(),
            status='success'
        )
    
    def log_analytics_request(self, user_id: str, operation: str):
        """Log analytics request for monitoring"""
        from loguru import logger
        logger.info(f"{self.platform_name} analytics: {operation} for user {user_id}")
    
    def log_analytics_error(self, user_id: str, operation: str, error: Exception):
        """Log analytics error for monitoring"""
        from loguru import logger
        logger.error(f"{self.platform_name} analytics: {operation} failed for user {user_id}: {error}")
