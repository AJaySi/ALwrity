"""
Cache Management System for Story Writer API

Handles story generation cache operations.
"""

from typing import Any, Dict, Optional
from loguru import logger


class CacheManager:
    """Manages cache operations for story generation data."""
    
    def __init__(self):
        """Initialize the cache manager."""
        self.cache: Dict[str, Dict[str, Any]] = {}
        logger.info("[StoryWriter] CacheManager initialized")
    
    def get_cache_key(self, request_data: Dict[str, Any]) -> str:
        """Generate a cache key from request data."""
        import hashlib
        import json
        
        # Create a normalized version of the request for caching
        cache_data = {
            "persona": request_data.get("persona", ""),
            "story_setting": request_data.get("story_setting", ""),
            "character_input": request_data.get("character_input", ""),
            "plot_elements": request_data.get("plot_elements", ""),
            "writing_style": request_data.get("writing_style", ""),
            "story_tone": request_data.get("story_tone", ""),
            "narrative_pov": request_data.get("narrative_pov", ""),
            "audience_age_group": request_data.get("audience_age_group", ""),
            "content_rating": request_data.get("content_rating", ""),
            "ending_preference": request_data.get("ending_preference", ""),
        }
        
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get a cached result if available."""
        if cache_key in self.cache:
            logger.debug(f"[StoryWriter] Cache hit for key: {cache_key}")
            return self.cache[cache_key]
        logger.debug(f"[StoryWriter] Cache miss for key: {cache_key}")
        return None
    
    def cache_result(self, cache_key: str, result: Dict[str, Any]):
        """Cache a result."""
        self.cache[cache_key] = result
        logger.debug(f"[StoryWriter] Cached result for key: {cache_key}")
    
    def clear_cache(self):
        """Clear all cached results."""
        count = len(self.cache)
        self.cache.clear()
        logger.info(f"[StoryWriter] Cleared {count} cached entries")
        return {"status": "success", "message": f"Cleared {count} cached entries"}
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "total_entries": len(self.cache),
            "cache_keys": list(self.cache.keys())
        }


# Global cache manager instance
cache_manager = CacheManager()
