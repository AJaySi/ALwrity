"""
Collection of modular routers for Story Writer endpoints.
Each module focuses on a related set of routes to keep the primary
`router.py` concise and easier to maintain.
"""

from . import cache_routes
from . import media_generation
from . import scene_animation
from . import story_content
from . import story_setup
from . import story_tasks
from . import video_generation

__all__ = [
    "cache_routes",
    "media_generation",
    "scene_animation",
    "story_content",
    "story_setup",
    "story_tasks",
    "video_generation",
]
