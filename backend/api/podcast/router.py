"""
Podcast Maker API Router

Main router that imports and registers all handler modules.
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any

from middleware.auth_middleware import get_current_user
from api.story_writer.utils.auth import require_authenticated_user
from api.story_writer.task_manager import task_manager

# Import all handler routers
from .handlers import projects, analysis, research, script, audio, images, video, avatar

# Create main router
router = APIRouter(prefix="/api/podcast", tags=["Podcast Maker"])

# Include all handler routers
router.include_router(projects.router)
router.include_router(analysis.router)
router.include_router(research.router)
router.include_router(script.router)
router.include_router(audio.router)
router.include_router(images.router)
router.include_router(video.router)
router.include_router(avatar.router)


@router.get("/task/{task_id}/status")
async def podcast_task_status(task_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Expose task status under podcast namespace (reuses shared task manager)."""
    require_authenticated_user(current_user)
    return task_manager.get_task_status(task_id)
