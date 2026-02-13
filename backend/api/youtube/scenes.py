"""YouTube Scenes Router

Handles scene building and management endpoints.
Provides AI-powered scene creation from video plans and individual scene updates.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException

from middleware.auth_middleware import get_current_user
from services.database import get_db
from sqlalchemy.orm import Session

from .models import SceneBuildRequest, SceneBuildResponse, SceneUpdateRequest, SceneUpdateResponse
from .utils import require_authenticated_user
from .dependencies import get_youtube_scene_builder_service

from utils.logger_utils import get_service_logger

logger = get_service_logger("api.youtube.scenes")

router = APIRouter(prefix="/scenes", tags=["youtube-scenes"])


@router.post("", response_model=SceneBuildResponse)
async def build_scenes(
    request: SceneBuildRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> SceneBuildResponse:
    """
    Build structured scenes from a video plan.

    Converts the video plan into detailed scenes with:
    - Narration text for each scene
    - Visual descriptions and prompts
    - Timing estimates
    - Visual cues and emphasis tags
    """
    try:
        user_id = require_authenticated_user(current_user)

        duration_type = request.video_plan.get('duration_type', 'medium')
        has_existing_scenes = bool(request.video_plan.get("scenes")) and request.video_plan.get("_scenes_included")

        logger.info(
            f"[YouTubeScenes] Building scenes: duration={duration_type}, "
            f"custom_script={bool(request.custom_script)}, "
            f"has_existing_scenes={has_existing_scenes}, "
            f"user={user_id}"
        )

        # Build scenes (optimized to reuse existing scenes if available)
        scene_builder = get_youtube_scene_builder_service()
        scenes = scene_builder.build_scenes_from_plan(
            video_plan=request.video_plan,
            user_id=user_id,
            custom_script=request.custom_script,
        )

        return SceneBuildResponse(
            success=True,
            scenes=scenes,
            message=f"Built {len(scenes)} scenes successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[YouTubeScenes] Error building scenes: {e}", exc_info=True)
        return SceneBuildResponse(
            success=False,
            message=f"Failed to build scenes: {str(e)}"
        )


@router.post("/{scene_id}/update", response_model=SceneUpdateResponse)
async def update_scene(
    scene_id: int,
    request: SceneUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> SceneUpdateResponse:
    """
    Update a single scene's narration, visual description, or duration.

    This allows users to fine-tune individual scenes before rendering.
    """
    try:
        require_authenticated_user(current_user)

        logger.info(f"[YouTubeScenes] Updating scene {scene_id}")

        # In a full implementation, this would update a stored scene
        # For now, return the updated scene data
        updated_scene = {
            "scene_number": scene_id,
            "narration": request.narration,
            "visual_description": request.visual_description,
            "duration_estimate": request.duration_estimate,
            "enabled": request.enabled if request.enabled is not None else True,
        }

        return SceneUpdateResponse(
            success=True,
            scene=updated_scene,
            message="Scene updated successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[YouTubeScenes] Error updating scene: {e}", exc_info=True)
        return SceneUpdateResponse(
            success=False,
            message=f"Failed to update scene: {str(e)}"
        )