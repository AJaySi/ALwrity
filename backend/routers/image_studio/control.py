"""Control Studio endpoints."""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException

from .models import ControlImageRequest, ControlImageResponse, ControlOperationsResponse
from .deps import get_studio_manager, _require_user_id
from services.image_studio import ImageStudioManager, ControlStudioRequest
from middleware.auth_middleware import get_current_user
from utils.logger_utils import get_service_logger

logger = get_service_logger("api.image_studio")
router = APIRouter(tags=["image-studio"])


@router.post("/control/process", response_model=ControlImageResponse, summary="Process Control Studio request")
async def process_control_image(
    request: ControlImageRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Perform Control Studio operations such as sketch-to-image, structure control, style control, and style transfer."""
    try:
        user_id = _require_user_id(current_user, "image control")
        logger.info(f"[Control Image] Request from user {user_id}: operation={request.operation}")

        control_request = ControlStudioRequest(
            operation=request.operation,
            prompt=request.prompt,
            control_image_base64=request.control_image_base64,
            style_image_base64=request.style_image_base64,
            negative_prompt=request.negative_prompt,
            control_strength=request.control_strength,
            fidelity=request.fidelity,
            style_strength=request.style_strength,
            composition_fidelity=request.composition_fidelity,
            change_strength=request.change_strength,
            aspect_ratio=request.aspect_ratio,
            style_preset=request.style_preset,
            seed=request.seed,
            output_format=request.output_format,
        )

        result = await studio_manager.control_image(control_request, user_id=user_id)
        return ControlImageResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Control Image] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Image control failed: {e}")


@router.get("/control/operations", response_model=ControlOperationsResponse, summary="List Control Studio operations")
async def get_control_operations(
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Return metadata for supported Control Studio operations."""
    try:
        operations = studio_manager.get_control_operations()
        return ControlOperationsResponse(operations=operations)
    except Exception as e:
        logger.error(f"[Control Operations] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to load control operations")
