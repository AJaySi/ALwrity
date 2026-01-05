"""
Google Trends Service

Provides Google Trends data integration for the Research Engine.
Handles rate limiting, caching, error handling, and data serialization.

Author: ALwrity Team
Version: 1.0
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
import pandas as pd

try:
    from pytrends.request import TrendReq
    PYTrends_AVAILABLE = True
except ImportError:
    PYTrends_AVAILABLE = False
    logger.warning("pytrends not installed. Google Trends features will be unavailable.")

from .rate_limiter import RateLimiter


class GoogleTrendsService:
    """
    Service for fetching and analyzing Google Trends data.
    
    Features:
    - Interest over time
    - Interest by region
    - Related topics
    - Related queries
    - Rate limiting (1 req/sec)
    - Caching (24-hour TTL)
    - Async support
    - Error handling with retry logic
    """
    
    def __init__(self):
        """Initialize the Google Trends service."""
        if not PYTrends_AVAILABLE:
            raise RuntimeError("pytrends library is required. Install with: pip install pytrends")
        
        self.rate_limiter = RateLimiter(max_calls=1, period=1.0)  # 1 request per second
        self.cache: Dict[str, Dict[str, Any]] = {}  # Simple in-memory cache
        self.cache_ttl = timedelta(hours=24)  # 24-hour cache
        
        logger.info("GoogleTrendsService initialized")
    
    async def analyze_trends(
        self,
        keywords: List[str],
        timeframe: str = "today 12-m",
        geo: str = "US",
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Comprehensive trends analysis.
        
        Fetches all trends data in a single optimized call:
        - Interest over time
        - Interest by region
        - Related topics (top & rising)
        - Related queries (top & rising)
        
        Args:
            keywords: List of keywords to analyze (1-5 keywords recommended)
            timeframe: Timeframe string (e.g., "today 12-m", "today 1-y", "all")
            geo: Country code (e.g., "US", "GB", "IN")
            user_id: User ID for subscription checks (optional for now)
            
        Returns:
            Dict containing all trends data in serializable format
            
        Raises:
            ValueError: If keywords list is empty or too long
            RuntimeError: If pytrends is not available or API fails
        """
        if not keywords:
            raise ValueError("Keywords list cannot be empty")
        
        if len(keywords) > 5:
            logger.warning(f"Too many keywords ({len(keywords)}), using first 5")
            keywords = keywords[:5]
        
        # Check cache first
        cache_key = self._build_cache_key(keywords, timeframe, geo)
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            logger.info(f"Returning cached trends data for: {keywords}")
            return {**cached_data, "cached": True}
        
        # Rate limit
        await self.rate_limiter.acquire()
        
        try:
            logger.info(f"Fetching Google Trends data for: {keywords} (timeframe: {timeframe}, geo: {geo})")
            
            # Initialize pytrends (sync operation, run in thread)
            pytrends = await asyncio.to_thread(
                self._initialize_pytrends,
                keywords,
                timeframe,
                geo
            )
            
            # Fetch all data in parallel (pytrends methods are sync, so use to_thread)
            interest_over_time_task = asyncio.to_thread(
                lambda: self._safe_interest_over_time(pytrends)
            )
            interest_by_region_task = asyncio.to_thread(
                lambda: self._safe_interest_by_region(pytrends)
            )
            related_topics_task = asyncio.to_thread(
                lambda: self._safe_related_topics(pytrends, keywords)
            )
            related_queries_task = asyncio.to_thread(
                lambda: self._safe_related_queries(pytrends, keywords)
            )
            
            # Wait for all tasks
            interest_over_time, interest_by_region, related_topics, related_queries = await asyncio.gather(
                interest_over_time_task,
                interest_by_region_task,
                related_topics_task,
                related_queries_task,
                return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(interest_over_time, Exception):
                logger.error(f"Interest over time failed: {interest_over_time}")
                interest_over_time = []
            if isinstance(interest_by_region, Exception):
                logger.error(f"Interest by region failed: {interest_by_region}")
                interest_by_region = []
            if isinstance(related_topics, Exception):
                logger.error(f"Related topics failed: {related_topics}")
                related_topics = {"top": [], "rising": []}
            if isinstance(related_queries, Exception):
                logger.error(f"Related queries failed: {related_queries}")
                related_queries = {"top": [], "rising": []}
            
            # Build result
            result = {
                "interest_over_time": interest_over_time,
                "interest_by_region": interest_by_region,
                "related_topics": related_topics,
                "related_queries": related_queries,
                "timeframe": timeframe,
                "geo": geo,
                "keywords": keywords,
                "timestamp": datetime.utcnow().isoformat(),
                "cached": False
            }
            
            # Cache result
            self._save_to_cache(cache_key, result)
            
            logger.info(f"Google Trends data fetched successfully: {len(interest_over_time)} time points, {len(interest_by_region)} regions")
            
            return result
            
        except Exception as e:
            logger.error(f"Google Trends analysis failed: {e}")
            # Return fallback response
            return self._create_fallback_response(keywords, timeframe, geo, str(e))
    
    def _initialize_pytrends(
        self,
        keywords: List[str],
        timeframe: str,
        geo: str
    ) -> TrendReq:
        """Initialize pytrends and build payload (sync operation)."""
        pytrends = TrendReq(hl='en-US', tz=360)
        pytrends.build_payload(kw_list=keywords, timeframe=timeframe, geo=geo)
        return pytrends
    
    def _safe_interest_over_time(self, pytrends: TrendReq) -> List[Dict[str, Any]]:
        """Safely fetch interest over time data."""
        try:
            df = pytrends.interest_over_time()
            if df.empty:
                return []
            return self._format_dataframe(df.reset_index())
        except Exception as e:
            logger.error(f"Error fetching interest over time: {e}")
            return []
    
    def _safe_interest_by_region(self, pytrends: TrendReq) -> List[Dict[str, Any]]:
        """Safely fetch interest by region data."""
        try:
            df = pytrends.interest_by_region(resolution='COUNTRY', inc_low_vol=True, inc_geo_code=False)
            if df.empty:
                return []
            return self._format_dataframe(df.reset_index())
        except Exception as e:
            logger.error(f"Error fetching interest by region: {e}")
            return []
    
    def _safe_related_topics(
        self,
        pytrends: TrendReq,
        keywords: List[str]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Safely fetch related topics."""
        try:
            topics_data = pytrends.related_topics()
            result = {"top": [], "rising": []}
            
            for keyword in keywords:
                if keyword in topics_data and isinstance(topics_data[keyword], dict):
                    keyword_topics = topics_data[keyword]
                    
                    if "top" in keyword_topics and not keyword_topics["top"].empty:
                        top_df = keyword_topics["top"]
                        # Select relevant columns
                        if "topic_title" in top_df.columns and "value" in top_df.columns:
                            top_data = top_df[["topic_title", "value"]].to_dict('records')
                            result["top"].extend(top_data)
                    
                    if "rising" in keyword_topics and not keyword_topics["rising"].empty:
                        rising_df = keyword_topics["rising"]
                        if "topic_title" in rising_df.columns and "value" in rising_df.columns:
                            rising_data = rising_df[["topic_title", "value"]].to_dict('records')
                            result["rising"].extend(rising_data)
            
            return result
        except Exception as e:
            logger.error(f"Error fetching related topics: {e}")
            return {"top": [], "rising": []}
    
    def _safe_related_queries(
        self,
        pytrends: TrendReq,
        keywords: List[str]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Safely fetch related queries."""
        try:
            queries_data = pytrends.related_queries()
            result = {"top": [], "rising": []}
            
            for keyword in keywords:
                if keyword in queries_data and isinstance(queries_data[keyword], dict):
                    keyword_queries = queries_data[keyword]
                    
                    if "top" in keyword_queries and not keyword_queries["top"].empty:
                        top_df = keyword_queries["top"]
                        result["top"].extend(top_df.to_dict('records'))
                    
                    if "rising" in keyword_queries and not keyword_queries["rising"].empty:
                        rising_df = keyword_queries["rising"]
                        result["rising"].extend(rising_df.to_dict('records'))
            
            return result
        except Exception as e:
            logger.error(f"Error fetching related queries: {e}")
            return {"top": [], "rising": []}
    
    def _format_dataframe(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Convert DataFrame to list of dicts (serializable format)."""
        if df.empty:
            return []
        
        # Convert datetime columns to strings
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].astype(str)
        
        # Convert to dict records
        return df.to_dict('records')
    
    def _build_cache_key(self, keywords: List[str], timeframe: str, geo: str) -> str:
        """Build cache key from parameters."""
        keywords_str = ":".join(sorted(keywords))
        return f"google_trends:{keywords_str}:{timeframe}:{geo}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get data from cache if not expired."""
        if cache_key not in self.cache:
            return None
        
        cached_entry = self.cache[cache_key]
        cached_time = datetime.fromisoformat(cached_entry.get("timestamp", ""))
        
        if datetime.utcnow() - cached_time > self.cache_ttl:
            # Expired, remove from cache
            del self.cache[cache_key]
            return None
        
        # Return cached data (without cached flag)
        result = {**cached_entry}
        result.pop("cached", None)
        return result
    
    def _save_to_cache(self, cache_key: str, data: Dict[str, Any]):
        """Save data to cache."""
        # Store with timestamp
        cache_entry = {
            **data,
            "cached_at": datetime.utcnow().isoformat()
        }
        self.cache[cache_key] = cache_entry
        
        # Clean up old cache entries periodically
        if len(self.cache) > 100:  # Limit cache size
            self._cleanup_cache()
    
    def _cleanup_cache(self):
        """Remove expired cache entries."""
        now = datetime.utcnow()
        expired_keys = []
        
        for key, entry in self.cache.items():
            cached_time = datetime.fromisoformat(entry.get("cached_at", entry.get("timestamp", "")))
            if now - cached_time > self.cache_ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def _create_fallback_response(
        self,
        keywords: List[str],
        timeframe: str,
        geo: str,
        error_message: str
    ) -> Dict[str, Any]:
        """Create fallback response when trends analysis fails."""
        return {
            "interest_over_time": [],
            "interest_by_region": [],
            "related_topics": {"top": [], "rising": []},
            "related_queries": {"top": [], "rising": []},
            "timeframe": timeframe,
            "geo": geo,
            "keywords": keywords,
            "timestamp": datetime.utcnow().isoformat(),
            "cached": False,
            "error": error_message
        }
    
    async def get_trending_searches(
        self,
        country: str = "united_states",
        user_id: Optional[str] = None
    ) -> List[str]:
        """
        Get current trending searches for a country.
        
        Args:
            country: Country name (e.g., "united_states", "united_kingdom")
            user_id: User ID for subscription checks
            
        Returns:
            List of trending search terms
        """
        await self.rate_limiter.acquire()
        
        try:
            pytrends = TrendReq(hl='en-US', tz=360)
            trending_df = await asyncio.to_thread(
                lambda: pytrends.trending_searches(pn=country)
            )
            
            if trending_df.empty:
                return []
            
            # Return as list of strings
            return trending_df[0].tolist() if len(trending_df.columns) > 0 else []
            
        except Exception as e:
            logger.error(f"Error fetching trending searches: {e}")
            return []
