"""
Collection of modular routers for Story Writer endpoints.
Each module focuses on a related set of routes to keep the primary
`router.py` concise and easier to maintain.
"""

from . import story_setup
from . import story_content
from . import story_tasks
from . import media_generation
from . import video_generation
from . import cache_routes

__all__ = [
    "story_setup",
    "story_content",
    "story_tasks",
    "media_generation",
    "video_generation",
    "cache_routes",
]
