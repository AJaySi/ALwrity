"""
Bing Webmaster Tools Analytics Handler

Handles Bing Webmaster Tools analytics data retrieval and processing.
"""

import requests
from typing import Dict, Any
from datetime import datetime, timedelta
from loguru import logger

from services.integrations.bing_oauth import BingOAuthService
from ...analytics_cache_service import analytics_cache
from ..models.analytics_data import AnalyticsData
from ..models.platform_types import PlatformType
from .base_handler import BaseAnalyticsHandler
from ..insights.bing_insights_service import BingInsightsService
from services.bing_analytics_storage_service import BingAnalyticsStorageService
import os


class BingAnalyticsHandler(BaseAnalyticsHandler):
    """Handler for Bing Webmaster Tools analytics"""
    
    def __init__(self):
        super().__init__(PlatformType.BING)
        self.bing_service = BingOAuthService()
        # Initialize insights service
        database_url = os.getenv('DATABASE_URL', 'sqlite:///./bing_analytics.db')
        self.insights_service = BingInsightsService(database_url)
        # Storage service used in onboarding step 5
        self.storage_service = BingAnalyticsStorageService(os.getenv('DATABASE_URL', 'sqlite:///alwrity.db'))
    
    async def get_analytics(self, user_id: str) -> AnalyticsData:
        """
        Get Bing Webmaster analytics data using Bing Webmaster API
        
        Note: Bing Webmaster provides SEO insights and search performance data
        """
        self.log_analytics_request(user_id, "get_analytics")
        
        # Check cache first - this is an expensive operation
        cached_data = analytics_cache.get('bing_analytics', user_id)
        if cached_data:
            logger.info("Using cached Bing analytics for user {user_id}", user_id=user_id)
            return AnalyticsData(**cached_data)
        
        logger.info("Fetching fresh Bing analytics for user {user_id} (expensive operation)", user_id=user_id)
        try:
            # Get user's Bing connection status with detailed token info
            token_status = self.bing_service.get_user_token_status(user_id)
            
            if not token_status.get('has_active_tokens'):
                if token_status.get('has_expired_tokens'):
                    return self.create_error_response('Bing Webmaster tokens expired - please reconnect')
                else:
                    return self.create_error_response('Bing Webmaster not connected')
            
            # Try once to fetch sites (may return empty if tokens are valid but no verified sites); do not block
            sites = self.bing_service.get_user_sites(user_id)
            
            # Get active tokens for access token
            active_tokens = token_status.get('active_tokens', [])
            if not active_tokens:
                return self.create_error_response('No active Bing Webmaster tokens available')
            
            # Get the first active token's access token
            token_info = active_tokens[0]
            access_token = token_info.get('access_token')
            
            # Cache the sites for future use (even if empty)
            analytics_cache.set('bing_sites', user_id, sites or [], ttl_override=2*60*60)
            logger.info(f"Cached Bing sites for analytics for user {user_id} (TTL: 2 hours)")
            
            if not access_token:
                return self.create_error_response('Bing Webmaster access token not available')
            
            # Do NOT call live Bing APIs here; use stored analytics like step 5
            query_stats = {}
            try:
                # If sites available, use first; otherwise ask storage for any stored summary
                site_url_for_storage = sites[0].get('Url', '') if (sites and isinstance(sites[0], dict)) else None
                stored = self.storage_service.get_analytics_summary(user_id, site_url_for_storage, days=30)
                if stored and isinstance(stored, dict):
                    query_stats = {
                        'total_clicks': stored.get('summary', {}).get('total_clicks', 0),
                        'total_impressions': stored.get('summary', {}).get('total_impressions', 0),
                        'total_queries': stored.get('summary', {}).get('total_queries', 0),
                        'avg_ctr': stored.get('summary', {}).get('total_ctr', 0),
                        'avg_position': stored.get('summary', {}).get('avg_position', 0),
                    }
            except Exception as e:
                logger.warning(f"Bing analytics: Failed to read stored analytics summary: {e}")
            
            # Get enhanced insights from database
            insights = self._get_enhanced_insights(user_id, sites[0].get('Url', '') if sites else '')
            
            # Extract comprehensive site information with actual metrics
            metrics = {
                'connection_status': 'connected',
                'connected_sites': len(sites),
                'sites': sites[:5] if sites else [],
                'connected_since': token_info.get('created_at', ''),
                'scope': token_info.get('scope', ''),
                'total_clicks': query_stats.get('total_clicks', 0),
                'total_impressions': query_stats.get('total_impressions', 0),
                'total_queries': query_stats.get('total_queries', 0),
                'avg_ctr': query_stats.get('avg_ctr', 0),
                'avg_position': query_stats.get('avg_position', 0),
                'insights': insights,
                'note': 'Bing Webmaster API provides SEO insights, search performance, and index status data'
            }
            
            # If no stored data or no sites, return partial like step 5, else success
            if (not sites) or (metrics.get('total_impressions', 0) == 0 and metrics.get('total_clicks', 0) == 0):
                result = self.create_partial_response(metrics=metrics, error_message='Connected to Bing; waiting for stored analytics or site verification')
            else:
                result = self.create_success_response(metrics=metrics)
            
            # Cache the result to avoid expensive API calls
            analytics_cache.set('bing_analytics', user_id, result.__dict__)
            logger.info("Cached Bing analytics data for user {user_id}", user_id=user_id)
            
            return result
            
        except Exception as e:
            self.log_analytics_error(user_id, "get_analytics", e)
            error_result = self.create_error_response(str(e))
            
            # Cache error result for shorter time to retry sooner
            analytics_cache.set('bing_analytics', user_id, error_result.__dict__, ttl_override=300)  # 5 minutes
            return error_result
    
    def get_connection_status(self, user_id: str) -> Dict[str, Any]:
        """Get Bing Webmaster connection status"""
        self.log_analytics_request(user_id, "get_connection_status")
        
        try:
            bing_connection = self.bing_service.get_connection_status(user_id)
            return {
                'connected': bing_connection.get('connected', False),
                'sites_count': bing_connection.get('total_sites', 0),
                'sites': bing_connection.get('sites', []),
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
    
    def _extract_user_sites(self, sites_data: Any) -> list:
        """Extract user sites from Bing API response"""
        if isinstance(sites_data, dict):
            if 'd' in sites_data:
                d_data = sites_data['d']
                if isinstance(d_data, dict) and 'results' in d_data:
                    return d_data['results']
                elif isinstance(d_data, list):
                    return d_data
                else:
                    return []
            else:
                return []
        elif isinstance(sites_data, list):
            return sites_data
        else:
            return []
    
    async def _get_query_stats(self, user_id: str, sites: list) -> Dict[str, Any]:
        """Get query statistics for Bing sites"""
        query_stats = {}
        logger.info(f"Bing sites found: {len(sites)} sites")
        
        if sites:
            first_site = sites[0]
            logger.info(f"First Bing site: {first_site}")
            # Bing API returns URL in 'Url' field (capital U)
            site_url = first_site.get('Url', '') if isinstance(first_site, dict) else str(first_site)
            logger.info(f"Extracted site URL: {site_url}")
            
            if site_url:
                try:
                    # Use the Bing service method to get query stats
                    logger.info(f"Getting Bing query stats for site: {site_url}")
                    query_data = self.bing_service.get_query_stats(
                        user_id=user_id,
                        site_url=site_url,
                        start_date=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                        end_date=datetime.now().strftime('%Y-%m-%d'),
                        page=0
                    )
                    
                    if "error" not in query_data:
                        logger.info(f"Bing query stats response structure: {type(query_data)}, keys: {list(query_data.keys()) if isinstance(query_data, dict) else 'Not a dict'}")
                        logger.info(f"Bing query stats raw response: {query_data}")
                        
                        # Handle different response structures from Bing API
                        queries = self._extract_queries(query_data)
                        
                        logger.info(f"Bing queries extracted: {len(queries)} queries")
                        if queries and len(queries) > 0:
                            logger.info(f"First query sample: {queries[0] if isinstance(queries[0], dict) else queries[0]}")
                        
                        # Calculate summary metrics
                        total_clicks = sum(query.get('Clicks', 0) for query in queries if isinstance(query, dict))
                        total_impressions = sum(query.get('Impressions', 0) for query in queries if isinstance(query, dict))
                        total_queries = len(queries)
                        avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
                        avg_position = sum(query.get('AvgClickPosition', 0) for query in queries if isinstance(query, dict)) / total_queries if total_queries > 0 else 0
                        
                        query_stats = {
                            'total_clicks': total_clicks,
                            'total_impressions': total_impressions,
                            'total_queries': total_queries,
                            'avg_ctr': round(avg_ctr, 2),
                            'avg_position': round(avg_position, 2)
                        }
                        
                        logger.info(f"Bing query stats calculated: {query_stats}")
                    else:
                        logger.warning(f"Bing query stats error: {query_data['error']}")
                    
                except Exception as e:
                    logger.warning(f"Error getting Bing query stats: {e}")
        
        return query_stats
    
    def _extract_queries(self, query_data: Any) -> list:
        """Extract queries from Bing API response"""
        if isinstance(query_data, dict):
            if 'd' in query_data:
                d_data = query_data['d']
                logger.info(f"Bing 'd' data structure: {type(d_data)}, keys: {list(d_data.keys()) if isinstance(d_data, dict) else 'Not a dict'}")
                if isinstance(d_data, dict) and 'results' in d_data:
                    return d_data['results']
                elif isinstance(d_data, list):
                    return d_data
                else:
                    return []
            else:
                return []
        elif isinstance(query_data, list):
            return query_data
        else:
            return []
    
    def _get_enhanced_insights(self, user_id: str, site_url: str) -> Dict[str, Any]:
        """Get enhanced insights from stored Bing analytics data"""
        try:
            if not site_url:
                return {'status': 'no_site_url', 'message': 'No site URL available for insights'}
            
            # Get performance insights
            performance_insights = self.insights_service.get_performance_insights(user_id, site_url, days=30)
            
            # Get SEO insights
            seo_insights = self.insights_service.get_seo_insights(user_id, site_url, days=30)
            
            # Get actionable recommendations
            recommendations = self.insights_service.get_actionable_recommendations(user_id, site_url, days=30)
            
            return {
                'performance': performance_insights,
                'seo': seo_insights,
                'recommendations': recommendations,
                'last_analyzed': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"Error getting enhanced insights: {e}")
            return {
                'status': 'error',
                'message': f'Unable to generate insights: {str(e)}',
                'fallback': True
            }
