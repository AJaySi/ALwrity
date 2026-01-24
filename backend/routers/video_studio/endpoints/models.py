"""
Model listing and cost estimation endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, Dict, Any

from ...services.video_studio import VideoStudioService
from ...utils.auth import get_current_user, require_authenticated_user
from utils.logger_utils import get_service_logger

logger = get_service_logger("video_studio.endpoints.models")

router = APIRouter()


@router.get("/models")
async def list_available_models(
    operation_type: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    List available AI models for video generation.

    Optionally filter by operation type (text-to-video, image-to-video, avatar, enhancement).
    """
    try:
        user_id = require_authenticated_user(current_user)

        video_service = VideoStudioService()

        models = video_service.get_available_models(operation_type)

        logger.info(f"[VideoStudio] Listed models for user={user_id}, operation={operation_type}")

        return {
            "success": True,
            "models": models,
            "operation_type": operation_type,
        }

    except Exception as e:
        logger.error(f"[VideoStudio] Error listing models: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")


@router.get("/cost-estimate")
async def estimate_cost(
    operation_type: str,
    duration: Optional[int] = None,
    resolution: Optional[str] = None,
    model: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Estimate cost for video generation operations.

    Provides real-time cost estimates before generation.
    """
    try:
        user_id = require_authenticated_user(current_user)

        video_service = VideoStudioService()

        estimate = video_service.estimate_cost(
            operation_type=operation_type,
            duration=duration,
            resolution=resolution,
            model=model,
        )

        logger.info(f"[VideoStudio] Cost estimate for user={user_id}: {estimate}")

        return {
            "success": True,
            "estimate": estimate,
            "operation_type": operation_type,
        }

    except Exception as e:
        logger.error(f"[VideoStudio] Error estimating cost: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to estimate cost: {str(e)}")
