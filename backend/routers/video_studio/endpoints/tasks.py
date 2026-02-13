"""
Async task status endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

from ...utils.auth import get_current_user, require_authenticated_user
from utils.logger_utils import get_service_logger
from api.story_writer.task_manager import task_manager

logger = get_service_logger("video_studio.endpoints.tasks")

router = APIRouter()


@router.get("/task/{task_id}/status")
async def get_task_status(
    task_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Poll for video generation task status.
    
    Returns task status, progress, and result when complete.
    """
    try:
        require_authenticated_user(current_user)
        
        status = task_manager.get_task_status(task_id)
        if not status:
            raise HTTPException(status_code=404, detail="Task not found or expired")
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[VideoStudio] Failed to get task status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get task status: {str(e)}")
