"""
WordPress.com Analytics Handler

Handles WordPress.com analytics data retrieval and processing.
"""

import requests
from typing import Dict, Any
from datetime import datetime
from loguru import logger

from services.integrations.wordpress_oauth import WordPressOAuthService
from ..models.analytics_data import AnalyticsData
from ..models.platform_types import PlatformType
from .base_handler import BaseAnalyticsHandler


class WordPressAnalyticsHandler(BaseAnalyticsHandler):
    """Handler for WordPress.com analytics"""
    
    def __init__(self):
        super().__init__(PlatformType.WORDPRESS)
        self.wordpress_service = WordPressOAuthService()
    
    async def get_analytics(self, user_id: str, start_date: str = None, end_date: str = None, **kwargs) -> AnalyticsData:
        """
        Get WordPress analytics data using WordPress.com REST API
        
        Note: WordPress.com has limited analytics API access
        We'll try to get basic site stats and post data
        """
        self.log_analytics_request(user_id, "get_analytics")
        
        try:
            # Get user's WordPress tokens
            connection_status = self.wordpress_service.get_connection_status(user_id)
            
            if not connection_status.get('connected'):
                return self.create_error_response('WordPress not connected')
            
            # Get the first connected site
            sites = connection_status.get('sites', [])
            if not sites:
                return self.create_error_response('No WordPress sites found')
            
            site = sites[0]
            access_token = site.get('access_token')
            blog_id = site.get('blog_id')
            
            if not access_token or not blog_id:
                return self.create_error_response('WordPress access token not available')
            
            # Try to get basic site stats from WordPress.com API
            headers = {
                'Authorization': f'Bearer {access_token}',
                'User-Agent': 'ALwrity/1.0'
            }
            
            # Get site info and basic stats
            site_info_url = f"https://public-api.wordpress.com/rest/v1.1/sites/{blog_id}"
            response = requests.get(site_info_url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"WordPress API call failed: {response.status_code}")
                # Return basic connection info instead of full analytics
                return self.create_partial_response(
                    metrics={
                        'site_name': site.get('blog_url', 'Unknown'),
                        'connection_status': 'connected',
                        'blog_id': blog_id,
                        'connected_since': site.get('created_at', ''),
                        'note': 'WordPress.com API has limited analytics access'
                    },
                    error_message='WordPress.com API has limited analytics access'
                )
            
            site_data = response.json()
            
            # Extract basic site information
            metrics = {
                'site_name': site_data.get('name', 'Unknown'),
                'site_url': site_data.get('URL', ''),
                'blog_id': blog_id,
                'language': site_data.get('lang', ''),
                'timezone': site_data.get('timezone', ''),
                'is_private': site_data.get('is_private', False),
                'is_coming_soon': site_data.get('is_coming_soon', False),
                'connected_since': site.get('created_at', ''),
                'connection_status': 'connected',
                'connected_sites': len(sites),
                'note': 'WordPress.com API has limited analytics access. For detailed analytics, consider integrating with Google Analytics or Jetpack Stats.'
            }
            
            return self.create_success_response(metrics=metrics)
            
        except Exception as e:
            self.log_analytics_error(user_id, "get_analytics", e)
            return self.create_error_response(str(e))
    
    def get_connection_status(self, user_id: str) -> Dict[str, Any]:
        """Get WordPress.com connection status"""
        self.log_analytics_request(user_id, "get_connection_status")
        
        try:
            wp_connection = self.wordpress_service.get_connection_status(user_id)
            return {
                'connected': wp_connection.get('connected', False),
                'sites_count': wp_connection.get('total_sites', 0),
                'sites': wp_connection.get('sites', []),
                'error': None
            }
        except Exception as e:
            self.log_analytics_error(user_id, "get_connection_status", e)
            return {
                'connected': False,
                'sites_count': 0,
                'sites': [],
                'error': str(e)
            }
