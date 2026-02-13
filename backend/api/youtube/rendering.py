"""YouTube Rendering Router

Handles video rendering, processing, and task management endpoints.
Provides asynchronous video generation with progress tracking and task monitoring.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from middleware.auth_middleware import get_current_user
from services.database import get_db

from .models import (
    VideoRenderRequest, VideoRenderResponse,
    SceneVideoRenderRequest, SceneVideoRenderResponse,
    CombineVideosRequest, CombineVideosResponse,
)
from .utils import require_authenticated_user
from .dependencies import (
    get_youtube_renderer_service,
    get_pricing_service,
    get_scene_animation_validator,
)
from .task_utils import (
    _execute_video_render_task,
    _execute_scene_video_render_task,
    _execute_combine_video_task,
)
from .task_manager import task_manager

from utils.logger_utils import get_service_logger

logger = get_service_logger("api.youtube.rendering")

router = APIRouter(prefix="/render", tags=["youtube-rendering"])


@router.post("", response_model=VideoRenderResponse)
async def start_video_render(
    request: VideoRenderRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> VideoRenderResponse:
    """
    Start rendering a video from scenes asynchronously.

    This endpoint creates a background task that:
    1. Generates narration audio for each scene
    2. Renders each scene using WAN 2.5 text-to-video
    3. Combines scenes into final video (if requested)
    4. Saves to asset library

    Returns task_id for polling progress.
    """
    try:
        user_id = require_authenticated_user(current_user)

        # Validate subscription limits
        pricing_service = get_pricing_service()
        get_scene_animation_validator()(
            pricing_service=pricing_service,
            user_id=user_id
        )

        # Filter enabled scenes
        enabled_scenes = [s for s in request.scenes if s.get("enabled", True)]
        if not enabled_scenes:
            return VideoRenderResponse(
                success=False,
                message="No enabled scenes to render"
            )

        # VALIDATION: Pre-validate scenes before creating task to prevent wasted API calls
        validation_errors = []
        for scene in enabled_scenes:
            scene_num = scene.get("scene_number", 0)
            visual_prompt = (scene.get("enhanced_visual_prompt") or scene.get("visual_prompt", "")).strip()

            if not visual_prompt:
                validation_errors.append(f"Scene {scene_num}: Missing visual prompt")
            elif len(visual_prompt) < 5:
                validation_errors.append(f"Scene {scene_num}: Visual prompt too short ({len(visual_prompt)} chars, minimum 5)")

            # Validate duration
            duration = scene.get("duration_estimate", 5)
            if duration < 1 or duration > 10:
                validation_errors.append(f"Scene {scene_num}: Invalid duration ({duration}s, must be 1-10 seconds)")

        if validation_errors:
            return VideoRenderResponse(
                success=False,
                message=f"Validation failed: {', '.join(validation_errors)}"
            )

        # Create background task
        task_id = task_manager.create_task(
            task_type="video_render",
            user_id=user_id,
            metadata={
                "scene_count": len(enabled_scenes),
                "resolution": request.resolution,
                "combine_scenes": request.combine_scenes,
                "voice_id": request.voice_id
            }
        )

        # Start background task
        background_tasks.add_task(
            _execute_video_render_task,
            task_id=task_id,
            scenes=enabled_scenes,
            video_plan=request.video_plan,
            user_id=user_id,
            resolution=request.resolution,
            combine_scenes=request.combine_scenes,
            voice_id=request.voice_id,
        )

        logger.info(
            f"[YouTubeRendering] Video render task created: {task_id}, "
            f"scenes={len(enabled_scenes)}, user={user_id}"
        )

        return VideoRenderResponse(
            success=True,
            task_id=task_id,
            message=f"Video render started with {len(enabled_scenes)} scenes. Task ID: {task_id}"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[YouTubeRendering] Error starting video render: {e}", exc_info=True)
        return VideoRenderResponse(
            success=False,
            message=f"Failed to start video render: {str(e)}"
        )


@router.post("/scene", response_model=SceneVideoRenderResponse)
async def start_scene_video_render(
    request: SceneVideoRenderRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SceneVideoRenderResponse:
    """
    Start rendering a single scene video asynchronously.

    Returns task_id for polling progress.
    """
    try:
        user_id = require_authenticated_user(current_user)

        # Validate subscription limits
        pricing_service = get_pricing_service()
        get_scene_animation_validator()(
            pricing_service=pricing_service,
            user_id=user_id
        )

        # Create background task
        task_id = task_manager.create_task(
            task_type="scene_render",
            user_id=user_id,
            metadata={
                "scene_number": request.scene.get("scene_number"),
                "resolution": request.resolution,
                "generate_audio": request.generate_audio_enabled,
                "voice_id": request.voice_id
            }
        )

        # Start background task
        background_tasks.add_task(
            _execute_scene_video_render_task,
            task_id=task_id,
            scene=request.scene,
            video_plan=request.video_plan,
            user_id=user_id,
            resolution=request.resolution,
            voice_id=request.voice_id,
            generate_audio_enabled=request.generate_audio_enabled,
        )

        logger.info(
            f"[YouTubeRendering] Scene render task created: {task_id}, "
            f"scene={request.scene.get('scene_number')}, user={user_id}"
        )

        return SceneVideoRenderResponse(
            success=True,
            task_id=task_id,
            scene_number=request.scene.get("scene_number"),
            message=f"Scene render started. Task ID: {task_id}"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[YouTubeRendering] Error starting scene render: {e}", exc_info=True)
        return SceneVideoRenderResponse(
            success=False,
            message=f"Failed to start scene render: {str(e)}",
            scene_number=request.scene.get("scene_number")
        )


@router.get("/{task_id}")
async def get_render_status(
    task_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Get the status of a video rendering task."""
    try:
        user_id = require_authenticated_user(current_user)

        task_status = task_manager.get_task_status(task_id)
        if not task_status:
            raise HTTPException(status_code=404, detail="Task not found")

        # Verify task ownership (if user_id is stored in task metadata)
        if task_status.get("user_id") and task_status["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        return task_status

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[YouTubeRendering] Error getting render status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get render status: {str(e)}")


@router.post("/combine", response_model=CombineVideosResponse)
async def combine_videos(
    request: CombineVideosRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> CombineVideosResponse:
    """
    Combine multiple scene videos into a final video asynchronously.

    Returns task_id for polling progress.
    """
    try:
        user_id = require_authenticated_user(current_user)

        # Create background task
        task_id = task_manager.create_task(
            task_type="video_combine",
            user_id=user_id,
            metadata={
                "video_count": len(request.scene_video_urls),
                "resolution": request.resolution,
                "title": request.title
            }
        )

        # Start background task
        background_tasks.add_task(
            _execute_combine_video_task,
            task_id=task_id,
            scene_video_urls=request.scene_video_urls,
            user_id=user_id,
            resolution=request.resolution,
            title=request.title,
        )

        logger.info(
            f"[YouTubeRendering] Video combine task created: {task_id}, "
            f"videos={len(request.scene_video_urls)}, user={user_id}"
        )

        return CombineVideosResponse(
            success=True,
            task_id=task_id,
            message=f"Video combination started with {len(request.scene_video_urls)} scenes. Task ID: {task_id}"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[YouTubeRendering] Error starting video combine: {e}", exc_info=True)
        return CombineVideosResponse(
            success=False,
            message=f"Failed to start video combine: {str(e)}"
        )