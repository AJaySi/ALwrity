"""
SEO Dashboard Service

Main orchestration service that coordinates data fetching from GSC, Bing,
and other analytics sources for the SEO dashboard. Leverages existing
OAuth connections from onboarding step 5.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from loguru import logger


def _raise_postgresql_required():
    """Raise error if PostgreSQL not configured."""
    raise ValueError(
        """
 POSTGRESQL REQUIRED - Clean Architecture
        
    ALwrity requires PostgreSQL environment variables to be set:
    - DATABASE_URL=postgresql://user:pass@host:port/database_name
    - PLATFORM_DATABASE_URL=postgresql://user:pass@host:port/database_name
    - USER_DATA_DATABASE_URL=postgresql://user:pass@host:port/database_name

    This is intentional - we no longer support SQLite or single database setups.
    """
    )

from utils.logger_utils import get_service_logger
from services.gsc_service import GSCService
from services.integrations.bing_oauth import BingOAuthService
from services.bing_analytics_storage_service import BingAnalyticsStorageService
from services.analytics_cache_service import AnalyticsCacheService
from services.onboarding.data_service import OnboardingDataService
from .analytics_aggregator import AnalyticsAggregator
from .competitive_analyzer import CompetitiveAnalyzer


def _raise_postgresql_required():
    """Raise error if PostgreSQL not configured."""
    raise ValueError(
        """
 POSTGRESQL REQUIRED - Clean Architecture
        
    ALwrity requires PostgreSQL environment variables to be set:
    - DATABASE_URL=postgresql://user:pass@host:port/database_name
    - PLATFORM_DATABASE_URL=postgresql://user:pass@host:port/database_name
    - USER_DATA_DATABASE_URL=postgresql://user:pass@host:port/database_name

    This is intentional - we no longer support SQLite or single database setups.
    """
    )

logger = get_service_logger("seo_dashboard")

class SEODashboardService:
    """Main service for SEO dashboard data orchestration."""
    
    def __init__(self, db: Session):
        """Initialize the SEO dashboard service."""
        self.db = db
        self.gsc_service = GSCService()
        self.bing_oauth = BingOAuthService()
        self.bing_storage = BingAnalyticsStorageService(_raise_postgresql_required())
        self.analytics_cache = AnalyticsCacheService()
        self.user_data_service = OnboardingDataService(db)
        self.analytics_aggregator = AnalyticsAggregator()
        self.competitive_analyzer = CompetitiveAnalyzer(db)
        
    async def get_platform_status(self, user_id: str) -> Dict[str, Any]:
        """Get connection status for GSC and Bing platforms."""
        try:
            # Check GSC connection
            gsc_credentials = self.gsc_service.load_user_credentials(user_id)
            gsc_connected = gsc_credentials is not None
            
            # Check Bing connection with detailed status
            bing_token_status = self.bing_oauth.get_user_token_status(user_id)
            bing_connected = bing_token_status.get('has_active_tokens', False)
            
            # Get cached data for last sync info
            gsc_data = self.analytics_cache.get('gsc_analytics', user_id)
            bing_data = self.analytics_cache.get('bing_analytics', user_id)
            
            return {
                "gsc": {
                    "connected": gsc_connected,
                    "sites": self._get_gsc_sites(user_id) if gsc_connected else [],
                    "last_sync": gsc_data.get('last_updated') if gsc_data else None,
                    "status": "connected" if gsc_connected else "disconnected"
                },
                "bing": {
                    "connected": bing_connected,
                    "sites": self._get_bing_sites(user_id) if bing_connected else [],
                    "last_sync": bing_data.get('last_updated') if bing_data else None,
                    "status": "connected" if bing_connected else ("expired" if bing_token_status.get('has_expired_tokens') else "disconnected"),
                    "has_expired_tokens": bing_token_status.get('has_expired_tokens', False),
                    "last_token_date": bing_token_status.get('last_token_date'),
                    "total_tokens": bing_token_status.get('total_tokens', 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting platform status for user {user_id}: {e}")
            return {
                "gsc": {"connected": False, "sites": [], "last_sync": None, "status": "error"},
                "bing": {"connected": False, "sites": [], "last_sync": None, "status": "error"}
            }
    
    async def get_dashboard_overview(self, user_id: str, site_url: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive dashboard overview with real GSC/Bing data."""
        try:
            # Get user's website URL if not provided
            if not site_url:
                # Try to get from website analysis first
                website_analysis = self.user_data_service.get_user_website_analysis(int(user_id))
                if website_analysis and website_analysis.get('website_url'):
                    site_url = website_analysis['website_url']
                else:
                    # Fallback: try to get from Bing sites
                    bing_sites = self._get_bing_sites(user_id)
                    if bing_sites:
                        site_url = bing_sites[0]  # Use first Bing site
                    else:
                        site_url = 'https://alwrity.com'  # Default fallback
            
            # Get platform status
            platform_status = await self.get_platform_status(user_id)
            
            # Get analytics data
            gsc_data = await self.get_gsc_data(user_id, site_url)
            bing_data = await self.get_bing_data(user_id, site_url)
            
            # Aggregate metrics
            summary = self.analytics_aggregator.combine_metrics(gsc_data, bing_data)
            timeseries = self.analytics_aggregator.normalize_timeseries(
                gsc_data.get("timeseries", []), 
                bing_data.get("timeseries", [])
            )
            
            # Get competitive insights
            competitor_insights = await self.competitive_analyzer.get_competitive_insights(user_id)
            
            # Calculate health score
            health_score = self._calculate_health_score(summary, platform_status)
            
            # Generate AI insights
            ai_insights = await self._generate_ai_insights(summary, timeseries, competitor_insights)
            
            return {
                "website_url": site_url,
                "platforms": platform_status,
                "summary": summary,
                "timeseries": timeseries,
                "competitor_insights": competitor_insights,
                "health_score": health_score,
                "ai_insights": ai_insights,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard overview for user {user_id}: {e}")
            raise
    
    async def get_gsc_data(self, user_id: str, site_url: Optional[str] = None) -> Dict[str, Any]:
        """Get GSC data for the specified site."""
        try:
            # Check if user has GSC credentials
            credentials = self.gsc_service.load_user_credentials(user_id)
            if not credentials:
                return {"error": "GSC not connected", "data": [], "status": "disconnected"}
            
            # Try to get from cache first
            cache_key = f"gsc_analytics:{user_id}:{site_url or 'default'}"
            cached_data = self.analytics_cache.get('gsc_analytics', user_id, site_url=site_url or 'default')
            if cached_data:
                return cached_data
            
            # Fetch fresh data from GSC API
            if site_url:
                gsc_data = self.gsc_service.get_search_analytics(user_id, site_url)
            else:
                # Get all sites for user
                sites = self._get_gsc_sites(user_id)
                if sites:
                    gsc_data = self.gsc_service.get_search_analytics(user_id, sites[0])
                else:
                    return {"error": "No GSC sites found", "data": [], "status": "disconnected"}
            
            # Cache the data
            self.analytics_cache.set('gsc_analytics', user_id, gsc_data, ttl_override=3600, site_url=site_url or 'default')  # 1 hour cache
            
            return gsc_data
            
        except Exception as e:
            logger.error(f"Error getting GSC data for user {user_id}: {e}")
            return {"error": str(e), "data": [], "status": "error"}
    
    async def get_bing_data(self, user_id: str, site_url: Optional[str] = None) -> Dict[str, Any]:
        """Get Bing Webmaster Tools data for the specified site."""
        try:
            # Check if user has Bing tokens
            tokens = self.bing_oauth.get_user_tokens(user_id)
            if not tokens:
                return {"error": "Bing not connected", "data": [], "status": "disconnected"}
            
            # Try to get from cache first
            cache_key = f"bing_analytics:{user_id}:{site_url or 'default'}"
            cached_data = self.analytics_cache.get('bing_analytics', user_id, site_url=site_url or 'default')
            if cached_data:
                return cached_data
            
            # Get data from Bing storage service
            if site_url:
                bing_data = self.bing_storage.get_analytics_summary(user_id, site_url, days=30)
            else:
                # Get all sites for user
                sites = self._get_bing_sites(user_id)
                if sites:
                    logger.info(f"Using first Bing site for analysis: {sites[0]}")
                    bing_data = self.bing_storage.get_analytics_summary(user_id, sites[0], days=30)
                else:
                    logger.warning(f"No Bing sites found for user {user_id}")
                    return {"error": "No Bing sites found", "data": [], "status": "disconnected"}
            
            # Cache the data
            self.analytics_cache.set('bing_analytics', user_id, bing_data, ttl_override=3600, site_url=site_url or 'default')  # 1 hour cache
            
            return bing_data
            
        except Exception as e:
            logger.error(f"Error getting Bing data for user {user_id}: {e}")
            return {"error": str(e), "data": [], "status": "error"}
    
    async def get_competitive_insights(self, user_id: str) -> Dict[str, Any]:
        """Get competitive insights from onboarding step 3 data."""
        try:
            return await self.competitive_analyzer.get_competitive_insights(user_id)
        except Exception as e:
            logger.error(f"Error getting competitive insights for user {user_id}: {e}")
            return {
                "competitor_keywords": [],
                "content_gaps": [],
                "opportunity_score": 0
            }
    
    async def refresh_analytics_data(self, user_id: str, site_url: Optional[str] = None) -> Dict[str, Any]:
        """Refresh analytics data by invalidating cache and fetching fresh data."""
        try:
            # Invalidate cache
            cache_keys = [
                f"gsc_analytics:{user_id}",
                f"bing_analytics:{user_id}",
                f"gsc_analytics:{user_id}:{site_url or 'default'}",
                f"bing_analytics:{user_id}:{site_url or 'default'}"
            ]
            
            for key in cache_keys:
                self.analytics_cache.delete(key)
            
            # Fetch fresh data
            gsc_result = await self.get_gsc_data(user_id, site_url)
            bing_result = await self.get_bing_data(user_id, site_url)
            
            return {
                "status": "success",
                "message": "Analytics data refreshed successfully",
                "last_updated": datetime.now().isoformat(),
                "platforms": {
                    "gsc": {"status": "success" if "error" not in gsc_result else "error"},
                    "bing": {"status": "success" if "error" not in bing_result else "error"}
                }
            }
            
        except Exception as e:
            logger.error(f"Error refreshing analytics data for user {user_id}: {e}")
            return {
                "status": "error",
                "message": f"Failed to refresh analytics data: {str(e)}",
                "last_updated": datetime.now().isoformat()
            }
    
    def _get_gsc_sites(self, user_id: str) -> List[str]:
        """Get GSC sites for user."""
        try:
            credentials = self.gsc_service.load_user_credentials(user_id)
            if not credentials:
                return []
            
            # This would need to be implemented in GSCService
            # For now, return empty list
            return []
        except Exception as e:
            logger.error(f"Error getting GSC sites for user {user_id}: {e}")
            return []
    
    def _get_bing_sites(self, user_id: str) -> List[str]:
        """Get Bing sites for user."""
        try:
            # Use the existing get_user_sites method from BingOAuthService
            sites = self.bing_oauth.get_user_sites(user_id)
            if not sites:
                logger.warning(f"No Bing sites found for user {user_id}")
                return []
            
            # Extract site URLs from the sites data
            site_urls = []
            for site in sites:
                if isinstance(site, dict) and site.get('url'):
                    site_urls.append(site['url'])
                elif isinstance(site, str):
                    site_urls.append(site)
            
            logger.info(f"Found {len(site_urls)} Bing sites for user {user_id}: {site_urls}")
            return site_urls
            
        except Exception as e:
            logger.error(f"Error getting Bing sites for user {user_id}: {e}")
            return []
    
    def _calculate_health_score(self, summary: Dict[str, Any], platform_status: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall SEO health score."""
        try:
            score = 0
            max_score = 100
            
            # Base score for connected platforms
            if platform_status.get("gsc", {}).get("connected"):
                score += 30
            if platform_status.get("bing", {}).get("connected"):
                score += 20
            
            # Traffic score (0-30)
            clicks = summary.get("clicks", 0)
            if clicks > 1000:
                score += 30
            elif clicks > 500:
                score += 20
            elif clicks > 100:
                score += 10
            
            # CTR score (0-20)
            ctr = summary.get("ctr", 0)
            if ctr > 0.05:  # 5%
                score += 20
            elif ctr > 0.03:  # 3%
                score += 15
            elif ctr > 0.01:  # 1%
                score += 10
            
            # Determine trend and color
            if score >= 80:
                trend = "up"
                label = "EXCELLENT"
                color = "#4CAF50"
            elif score >= 60:
                trend = "stable"
                label = "GOOD"
                color = "#2196F3"
            elif score >= 40:
                trend = "down"
                label = "NEEDS IMPROVEMENT"
                color = "#FF9800"
            else:
                trend = "down"
                label = "POOR"
                color = "#F44336"
            
            return {
                "score": score,
                "change": 0,  # Would need historical data to calculate
                "trend": trend,
                "label": label,
                "color": color
            }
            
        except Exception as e:
            logger.error(f"Error calculating health score: {e}")
            return {
                "score": 0,
                "change": 0,
                "trend": "unknown",
                "label": "UNKNOWN",
                "color": "#9E9E9E"
            }
    
    async def _generate_ai_insights(self, summary: Dict[str, Any], timeseries: List[Dict[str, Any]], competitor_insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate AI insights from analytics data."""
        try:
            insights = []
            
            # Traffic insights
            clicks = summary.get("clicks", 0)
            ctr = summary.get("ctr", 0)
            
            if clicks > 0 and ctr < 0.02:  # Low CTR
                insights.append({
                    "type": "opportunity",
                    "priority": "high",
                    "text": f"Your CTR is {ctr:.1%}, which is below average. Consider optimizing your meta descriptions and titles.",
                    "category": "performance"
                })
            
            # Competitive insights
            opportunity_score = competitor_insights.get("opportunity_score", 0)
            if opportunity_score > 70:
                insights.append({
                    "type": "opportunity",
                    "priority": "high",
                    "text": f"High opportunity score of {opportunity_score}% - competitors are ranking for keywords you're not targeting.",
                    "category": "competitive"
                })
            
            # Content gaps
            content_gaps = competitor_insights.get("content_gaps", [])
            if content_gaps:
                insights.append({
                    "type": "action",
                    "priority": "medium",
                    "text": f"Found {len(content_gaps)} content gaps. Consider creating content for these topics.",
                    "category": "content"
                })
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating AI insights: {e}")
            return []