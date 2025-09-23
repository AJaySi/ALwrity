"""
Cache Management System for Blog Writer API

Handles research and outline cache operations including statistics,
clearing, invalidation, and entry retrieval.
"""

from typing import Any, Dict, List
from loguru import logger

from services.blog_writer.blog_service import BlogWriterService


class CacheManager:
    """Manages cache operations for research and outline data."""
    
    def __init__(self):
        self.service = BlogWriterService()
    
    def get_research_cache_stats(self) -> Dict[str, Any]:
        """Get research cache statistics."""
        try:
            from services.cache.research_cache import research_cache
            return research_cache.get_cache_stats()
        except Exception as e:
            logger.error(f"Failed to get research cache stats: {e}")
            raise
    
    def clear_research_cache(self) -> Dict[str, Any]:
        """Clear the research cache."""
        try:
            from services.cache.research_cache import research_cache
            research_cache.clear_cache()
            return {"status": "success", "message": "Research cache cleared"}
        except Exception as e:
            logger.error(f"Failed to clear research cache: {e}")
            raise
    
    def get_outline_cache_stats(self) -> Dict[str, Any]:
        """Get outline cache statistics."""
        try:
            stats = self.service.get_outline_cache_stats()
            return {"success": True, "stats": stats}
        except Exception as e:
            logger.error(f"Failed to get outline cache stats: {e}")
            raise
    
    def clear_outline_cache(self) -> Dict[str, Any]:
        """Clear all cached outline entries."""
        try:
            self.service.clear_outline_cache()
            return {"success": True, "message": "Outline cache cleared successfully"}
        except Exception as e:
            logger.error(f"Failed to clear outline cache: {e}")
            raise
    
    def invalidate_outline_cache_for_keywords(self, keywords: List[str]) -> Dict[str, Any]:
        """Invalidate outline cache entries for specific keywords."""
        try:
            self.service.invalidate_outline_cache_for_keywords(keywords)
            return {"success": True, "message": f"Invalidated cache for keywords: {keywords}"}
        except Exception as e:
            logger.error(f"Failed to invalidate outline cache for keywords {keywords}: {e}")
            raise
    
    def get_recent_outline_cache_entries(self, limit: int = 20) -> Dict[str, Any]:
        """Get recent outline cache entries for debugging."""
        try:
            entries = self.service.get_recent_outline_cache_entries(limit)
            return {"success": True, "entries": entries}
        except Exception as e:
            logger.error(f"Failed to get recent outline cache entries: {e}")
            raise


# Global cache manager instance
cache_manager = CacheManager()
