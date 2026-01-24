"""Editing and enhancement API endpoints for Image Studio."""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException

from routers.image_studio_modules.models import (
    EditImageRequest, EditModelsResponse, EditModelRecommendationRequest,
    EditModelRecommendationResponse, EditImageResponse, EditOperationsResponse,
    UpscaleImageRequest, UpscaleImageResponse,
    ControlImageRequest, ControlImageResponse, ControlOperationsResponse
)
from routers.image_studio_modules.utils import _require_user_id
from routers.image_studio_modules.dependencies import get_studio_manager

from services.image_studio import ImageStudioManager, EditStudioRequest
from services.image_studio.upscale_service import UpscaleStudioRequest
from middleware.auth_middleware import get_current_user
from utils.logger_utils import get_service_logger

logger = get_service_logger("api.image_studio.editing")
router = APIRouter()


# ====================
# EDIT STUDIO ENDPOINTS
# ====================

@router.post("/edit/process", response_model=EditImageResponse, summary="Process Edit Studio request")
async def process_edit_image(
    request: EditImageRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Perform Edit Studio operations such as remove background, inpaint, or recolor."""
    try:
        user_id = _require_user_id(current_user, "image editing")
        logger.info(f"[Edit Image] Request from user {user_id}: operation={request.operation}")

        edit_request = EditStudioRequest(
            image_base64=request.image_base64,
            operation=request.operation,
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            mask_base64=request.mask_base64,
            search_prompt=request.search_prompt,
            select_prompt=request.select_prompt,
            background_image_base64=request.background_image_base64,
            lighting_image_base64=request.lighting_image_base64,
            expand_left=request.expand_left,
            expand_right=request.expand_right,
            expand_up=request.expand_up,
            expand_down=request.expand_down,
            provider=request.provider,
            model=request.model,
            style_preset=request.style_preset,
            guidance_scale=request.guidance_scale,
            steps=request.steps,
            seed=request.seed,
            output_format=request.output_format,
            options=request.options or {},
        )

        result = await studio_manager.edit_image(edit_request, user_id=user_id)
        return EditImageResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Edit Image] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Image editing failed: {e}")


@router.get("/edit/operations", response_model=EditOperationsResponse, summary="List Edit Studio operations")
async def get_edit_operations(
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Return metadata for supported Edit Studio operations."""
    try:
        operations = studio_manager.get_edit_operations()
        return EditOperationsResponse(operations=operations)
    except Exception as e:
        logger.error(f"[Edit Operations] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to load edit operations")


@router.get("/edit/models", response_model=EditModelsResponse, summary="List available editing models")
async def get_edit_models(
    tier: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Get available models for Edit Studio operations."""
    try:
        models = studio_manager.get_edit_models(tier=tier)
        return EditModelsResponse(models=models, total=len(models))
    except Exception as e:
        logger.error(f"[Edit Models] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to load edit models")


@router.post("/edit/recommend", response_model=EditModelRecommendationResponse, summary="Get model recommendation")
async def recommend_edit_model(
    request: EditModelRecommendationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Get recommended model for Edit Studio based on operation and image properties."""
    try:
        # Get user tier from current_user if available
        user_tier = request.user_tier
        if not user_tier and current_user:
            user_tier = current_user.get("tier") or current_user.get("subscription_tier")

        result = studio_manager.recommend_edit_model(
            operation=request.operation,
            image_resolution=request.image_resolution,
            user_tier=user_tier,
            preferences=request.preferences,
        )
        return EditModelRecommendationResponse(**result)
    except Exception as e:
        logger.error(f"[Edit Recommend] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get recommendation: {e}")


# ====================
# UPSCALE STUDIO ENDPOINTS
# ====================

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
        logger.error(f"[Upscale Image] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Image upscaling failed: {e}")


# ====================
# CONTROL STUDIO ENDPOINTS
# ====================

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

        control_request = studio_manager._create_control_request(
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