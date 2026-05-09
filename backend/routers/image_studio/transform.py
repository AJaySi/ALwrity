"""Transform Studio endpoints — image-to-video, talking avatar, and video serving."""

from pathlib import Path
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse

from .models import (
    TransformImageToVideoRequestModel, TalkingAvatarRequestModel,
    TransformVideoResponse, TransformCostEstimateRequest, TransformCostEstimateResponse,
)
from .deps import get_studio_manager, _require_user_id
from services.image_studio import ImageStudioManager, TransformImageToVideoRequest, TalkingAvatarRequest
from middleware.auth_middleware import get_current_user, get_current_user_with_query_token
from utils.logger_utils import get_service_logger

logger = get_service_logger("api.image_studio")
router = APIRouter(tags=["image-studio"])


@router.post("/transform/image-to-video", response_model=TransformVideoResponse, summary="Transform Image to Video")
async def transform_image_to_video(
    request: TransformImageToVideoRequestModel,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Transform an image into a video using WAN 2.5."""
    try:
        user_id = _require_user_id(current_user, "image-to-video transformation")
        logger.info(f"[Transform Studio] Image-to-video request from user {user_id}: resolution={request.resolution}, duration={request.duration}s")

        transform_request = TransformImageToVideoRequest(
            image_base64=request.image_base64,
            prompt=request.prompt,
            audio_base64=request.audio_base64,
            resolution=request.resolution,
            duration=request.duration,
            negative_prompt=request.negative_prompt,
            seed=request.seed,
            enable_prompt_expansion=request.enable_prompt_expansion,
        )

        result = await studio_manager.transform_image_to_video(transform_request, user_id=user_id)

        logger.info(f"[Transform Studio] ✅ Image-to-video completed: cost=${result['cost']:.2f}")
        return TransformVideoResponse(**result)

    except ValueError as e:
        logger.error(f"[Transform Studio] ❌ Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Transform Studio] ❌ Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")


@router.post("/transform/talking-avatar", response_model=TransformVideoResponse, summary="Create Talking Avatar")
async def create_talking_avatar(
    request: TalkingAvatarRequestModel,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Create a talking avatar video using InfiniteTalk."""
    try:
        user_id = _require_user_id(current_user, "talking avatar generation")
        logger.info(f"[Transform Studio] Talking avatar request from user {user_id}: resolution={request.resolution}")

        avatar_request = TalkingAvatarRequest(
            image_base64=request.image_base64,
            audio_base64=request.audio_base64,
            resolution=request.resolution,
            prompt=request.prompt,
            mask_image_base64=request.mask_image_base64,
            seed=request.seed,
        )

        result = await studio_manager.create_talking_avatar(avatar_request, user_id=user_id)

        logger.info(f"[Transform Studio] ✅ Talking avatar completed: cost=${result['cost']:.2f}")
        return TransformVideoResponse(**result)

    except ValueError as e:
        logger.error(f"[Transform Studio] ❌ Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Transform Studio] ❌ Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Talking avatar generation failed: {str(e)}")


@router.post("/transform/estimate-cost", response_model=TransformCostEstimateResponse, summary="Estimate Transform Cost")
async def estimate_transform_cost(
    request: TransformCostEstimateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Estimate cost for transform operations."""
    try:
        estimate = studio_manager.estimate_transform_cost(
            operation=request.operation,
            resolution=request.resolution,
            duration=request.duration,
        )
        return TransformCostEstimateResponse(**estimate)

    except ValueError as e:
        logger.error(f"[Transform Studio] ❌ Cost estimation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[Transform Studio] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/videos/{user_id}/{video_filename:path}", summary="Serve Transform Studio Video")
async def serve_transform_video(
    user_id: str,
    video_filename: str,
    current_user: Dict[str, Any] = Depends(get_current_user_with_query_token),
):
    """Serve a generated Transform Studio video file."""
    try:
        authenticated_user_id = _require_user_id(current_user, "video access")
        if authenticated_user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Access denied: You can only access your own videos"
            )

        base_dir = Path(__file__).parent.parent.parent
        transform_videos_dir = base_dir / "transform_videos"
        video_path = transform_videos_dir / user_id / video_filename

        try:
            resolved_video_path = video_path.resolve()
            resolved_base = transform_videos_dir.resolve()
            resolved_video_path.relative_to(resolved_base)
        except ValueError:
            raise HTTPException(
                status_code=403,
                detail="Invalid video path: path traversal detected"
            )

        if not video_path.exists():
            raise HTTPException(status_code=404, detail="Video not found")

        return FileResponse(
            path=str(video_path),
            media_type="video/mp4",
            filename=video_filename
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Transform Studio] Failed to serve video: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
