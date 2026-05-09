"""Edit Studio endpoints."""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException

from .models import (
    EditImageRequest, EditImageResponse, EditOperationsResponse,
    EditModelsResponse, EditModelRecommendationRequest, EditModelRecommendationResponse,
)
from .deps import get_studio_manager, _require_user_id
from services.image_studio import ImageStudioManager, EditStudioRequest
from middleware.auth_middleware import get_current_user
from utils.logger_utils import get_service_logger

logger = get_service_logger("api.image_studio")
router = APIRouter(tags=["image-studio"])


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
    operation: Optional[str] = None,
    tier: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Get available WaveSpeed editing models with metadata.

    Query Parameters:
    - operation: Filter by operation type (e.g., "general_edit")
    - tier: Filter by tier ("budget", "mid", "premium")
    """
    try:
        result = studio_manager.get_edit_models(operation=operation, tier=tier)
        return EditModelsResponse(**result)
    except Exception as e:
        logger.error(f"[Edit Models] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to load editing models")


@router.post("/edit/recommend", response_model=EditModelRecommendationResponse, summary="Get model recommendation")
async def recommend_edit_model(
    request: EditModelRecommendationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Get recommended editing model based on operation, image resolution, and user preferences.

    Auto-detects best model when user doesn't specify one.
    """
    try:
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
