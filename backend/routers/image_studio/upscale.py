"""Upscale Studio endpoint."""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException

from .models import UpscaleImageRequest, UpscaleImageResponse
from .deps import get_studio_manager, _require_user_id
from services.image_studio import ImageStudioManager
from services.image_studio.upscale_service import UpscaleStudioRequest
from middleware.auth_middleware import get_current_user
from utils.logger_utils import get_service_logger

logger = get_service_logger("api.image_studio")
router = APIRouter(tags=["image-studio"])


@router.post("/upscale", response_model=UpscaleImageResponse, summary="Upscale Image")
async def upscale_image(
    request: UpscaleImageRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Upscale an image using Stability AI pipelines."""
    try:
        user_id = _require_user_id(current_user, "image upscaling")
        upscale_request = UpscaleStudioRequest(
            image_base64=request.image_base64,
            mode=request.mode,
            target_width=request.target_width,
            target_height=request.target_height,
            preset=request.preset,
            prompt=request.prompt,
        )
        result = await studio_manager.upscale_image(upscale_request, user_id=user_id)
        return UpscaleImageResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Upscale Image] ❌ Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Image upscaling failed: {e}")
