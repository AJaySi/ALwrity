"""
Google Search Console Analytics Handler

Handles GSC analytics data retrieval and processing.
"""

from typing import Dict, Any
from datetime import datetime, timedelta
from loguru import logger

from services.gsc_service import GSCService
from ...analytics_cache_service import analytics_cache
from ..models.analytics_data import AnalyticsData
from ..models.platform_types import PlatformType
from .base_handler import BaseAnalyticsHandler


class GSCAnalyticsHandler(BaseAnalyticsHandler):
    """Handler for Google Search Console analytics"""
    
    def __init__(self):
        super().__init__(PlatformType.GSC)
        self.gsc_service = GSCService()
    
    async def get_analytics(self, user_id: str, target_url: str = None, **kwargs) -> AnalyticsData:
        """
        Get Google Search Console analytics data with caching
        
        Args:
            user_id: User ID to get analytics for
            target_url: Optional URL to prefer when selecting GSC site
            
        Returns comprehensive SEO metrics including clicks, impressions, CTR, and position data.
        """
        self.log_analytics_request(user_id, "get_analytics")
        
        # Check cache first - GSC API calls can be expensive
        # Include target_url in cache key if provided
        cache_key = f"{user_id}_{target_url}" if target_url else user_id
        cached_data = analytics_cache.get('gsc_analytics', cache_key)
        if cached_data:
            logger.info("Using cached GSC analytics for user {user_id}", user_id=user_id)
            return AnalyticsData(**cached_data)
        
        logger.info("Fetching fresh GSC analytics for user {user_id}", user_id=user_id)
        try:
            # Get user's sites
            sites = self.gsc_service.get_site_list(user_id)
            logger.info(f"GSC Sites found for user {user_id}: {sites}")
            if not sites:
                logger.warning(f"No GSC sites found for user {user_id}")
                return self.create_error_response('No GSC sites found')
            
            # Select site: Prefer target_url match, otherwise first site
            selected_site = sites[0]
            if target_url:
                logger.info(f"Attempting to match target URL: {target_url}")
                # Normalize target URL (remove protocol, trailing slash)
                normalized_target = target_url.replace('https://', '').replace('http://', '').rstrip('/')
                
                for site in sites:
                    site_url = site['siteUrl']
                    normalized_site = site_url.replace('https://', '').replace('http://', '').rstrip('/')
                    
                    if normalized_target in normalized_site or normalized_site in normalized_target:
                        selected_site = site
                        logger.info(f"Found matching GSC site: {site_url}")
                        break
            
            site_url = selected_site['siteUrl']
            logger.info(f"Using GSC site URL: {site_url}")
            
            # Get search analytics for last 30 days
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            logger.info(f"GSC Date range: {start_date} to {end_date}")
            
            search_analytics = self.gsc_service.get_search_analytics(
                user_id=user_id,
                site_url=site_url,
                start_date=start_date,
                end_date=end_date
            )
            logger.info(f"GSC Search analytics retrieved for user {user_id}")
            
            # Process GSC data into standardized format
            processed_metrics = self._process_gsc_metrics(search_analytics)
            
            result = self.create_success_response(
                metrics=processed_metrics,
                date_range={'start': start_date, 'end': end_date}
            )
            
            # Cache the result to avoid expensive API calls
            analytics_cache.set('gsc_analytics', cache_key, result.__dict__)
            logger.info("Cached GSC analytics data for user {user_id}", user_id=user_id)
            
            return result
            
        except Exception as e:
            self.log_analytics_error(user_id, "get_analytics", e)
            error_result = self.create_error_response(str(e))
            
            # Cache error result for shorter time to retry sooner
            analytics_cache.set('gsc_analytics', cache_key, error_result.__dict__, ttl_override=300)  # 5 minutes
            return error_result
    
    def get_connection_status(self, user_id: str) -> Dict[str, Any]:
        """Get GSC connection status"""
        self.log_analytics_request(user_id, "get_connection_status")
        
        try:
            sites = self.gsc_service.get_site_list(user_id)
            return {
                'connected': len(sites) > 0,
                'sites_count': len(sites),
                'sites': sites[:3] if sites else [],  # Show first 3 sites
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
    
    def _process_gsc_metrics(self, search_analytics: Dict[str, Any]) -> Dict[str, Any]:
        """Process GSC raw data into standardized metrics"""
        try:
            # Debug: Log the raw search analytics data structure
            logger.info(f"GSC Raw search analytics structure: {search_analytics}")
            logger.info(f"GSC Raw search analytics keys: {list(search_analytics.keys())}")
            
            # Handle new data structure with overall_metrics and query_data
            if 'overall_metrics' in search_analytics:
                # New structure from updated GSC service
                overall_rows = search_analytics.get('overall_metrics', {}).get('rows', [])
                query_rows = search_analytics.get('query_data', {}).get('rows', [])
                
                # Calculate totals from overall_rows (most accurate as it includes anonymized queries)
                total_clicks = 0
                total_impressions = 0
                total_position = 0
                valid_position_rows = 0
                
                # Use overall_rows for totals if available, otherwise fallback to query_rows
                calc_rows = overall_rows if overall_rows else query_rows
                
                for row in calc_rows:
                    clicks = row.get('clicks', 0)
                    impressions = row.get('impressions', 0)
                    position = row.get('position', 0)
                    
                    total_clicks += clicks
                    total_impressions += impressions
                    
                    if position and position > 0:
                        total_position += position * impressions  # Weighted average
                
                # Calculate weighted average position
                avg_position = total_position / total_impressions if total_impressions > 0 else 0
                avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
                
                # Use query_rows for top queries list
                top_queries_source = query_rows
                
            else:
                # Legacy structure
                rows = search_analytics.get('rows', [])
                # ... existing legacy logic ...
                calc_rows = rows
                top_queries_source = rows
                
                total_clicks = 0
                total_impressions = 0
                total_position = 0
                valid_position_rows = 0
                
                for row in calc_rows:
                    clicks = row.get('clicks', 0)
                    impressions = row.get('impressions', 0)
                    position = row.get('position', 0)
                    
                    total_clicks += clicks
                    total_impressions += impressions
                    
                    if position and position > 0:
                         # Simple average for legacy/unknown structure if we can't do weighted
                        total_position += position
                        valid_position_rows += 1
                
                avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
                avg_position = total_position / valid_position_rows if valid_position_rows > 0 else 0

            
            # Get top performing queries
            top_queries = []
            if top_queries_source:
                # Sort by clicks
                sorted_queries = sorted(top_queries_source, key=lambda x: x.get('clicks', 0), reverse=True)[:10]
                
                for row in sorted_queries:
                    top_queries.append({
                        'query': self._extract_query_from_row(row),
                        'clicks': row.get('clicks', 0),
                        'impressions': row.get('impressions', 0),
                        'ctr': round(row.get('ctr', 0) * 100, 2),
                        'position': round(row.get('position', 0), 2)
                    })

            # Prepare Top Pages (requires page dimension, but we only requested query dimension in gsc_service step 3)
            # To get top pages, we would need another API call with dimension=['page']
            # For now, we'll return empty top_pages or infer from what we have if possible (we can't from query data)
            top_pages = [] 
            
            return {
                'connection_status': 'connected',
                'connected_sites': 1,
                'total_clicks': total_clicks,
                'total_impressions': total_impressions,
                'avg_ctr': round(avg_ctr, 2),
                'avg_position': round(avg_position, 2),
                'total_queries': len(top_queries_source) if top_queries_source else 0,
                'top_queries': top_queries,
                'top_pages': top_pages
            }
            
        except Exception as e:
            logger.error(f"Error processing GSC metrics: {e}")
            return {
                'connection_status': 'error',
                'connected_sites': 0,
                'total_clicks': 0,
                'total_impressions': 0,
                'avg_ctr': 0,
                'avg_position': 0,
                'total_queries': 0,
                'top_queries': [],
                'top_pages': [],
                'error': str(e)
            }
    
    def _extract_query_from_row(self, row: Dict[str, Any]) -> str:
        """Extract query text from GSC API row data"""
        try:
            keys = row.get('keys', [])
            if keys and len(keys) > 0:
                first_key = keys[0]
                if isinstance(first_key, dict):
                    return first_key.get('keys', ['Unknown'])[0]
                else:
                    return str(first_key)
            return 'Unknown'
        except Exception as e:
            logger.error(f"Error extracting query from row: {e}")
            return 'Unknown'
