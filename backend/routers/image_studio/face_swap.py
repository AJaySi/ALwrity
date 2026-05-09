"""Face Swap Studio endpoints."""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException

from .models import (
    FaceSwapRequest, FaceSwapResponse, FaceSwapModelsResponse,
    FaceSwapModelRecommendationRequest, FaceSwapModelRecommendationResponse,
)
from .deps import get_studio_manager, _require_user_id
from services.image_studio import ImageStudioManager
from services.image_studio.face_swap_service import FaceSwapStudioRequest
from middleware.auth_middleware import get_current_user
from utils.logger_utils import get_service_logger

logger = get_service_logger("api.image_studio")
router = APIRouter(tags=["image-studio"])


@router.post("/face-swap/process", response_model=FaceSwapResponse, summary="Process Face Swap")
async def process_face_swap(
    request: FaceSwapRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Process face swap request with auto-detection and model selection."""
    try:
        user_id = _require_user_id(current_user, "face swap")
        face_swap_request = FaceSwapStudioRequest(
            base_image_base64=request.base_image_base64,
            face_image_base64=request.face_image_base64,
            model=request.model,
            target_face_index=request.target_face_index,
            target_gender=request.target_gender,
            options=request.options,
        )
        result = await studio_manager.face_swap(face_swap_request, user_id=user_id)
        return FaceSwapResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Face Swap] ❌ Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Face swap failed: {e}")


@router.get("/face-swap/models", response_model=FaceSwapModelsResponse, summary="List available face swap models")
async def get_face_swap_models(
    tier: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Get available WaveSpeed face swap models with metadata.

    Query Parameters:
    - tier: Filter by tier ("budget", "mid", "premium")
    """
    try:
        result = studio_manager.get_face_swap_models(tier=tier)
        return FaceSwapModelsResponse(**result)
    except Exception as e:
        logger.error(f"[Face Swap Models] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to load face swap models")


@router.post("/face-swap/recommend", response_model=FaceSwapModelRecommendationResponse, summary="Get face swap model recommendation")
async def recommend_face_swap_model(
    request: FaceSwapModelRecommendationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Get recommended face swap model based on image resolutions and user preferences.

    Auto-detects best model when user doesn't specify one.
    """
    try:
        user_tier = request.user_tier
        if not user_tier and current_user:
            user_tier = current_user.get("tier") or current_user.get("subscription_tier")

        result = studio_manager.recommend_face_swap_model(
            base_image_resolution=request.base_image_resolution,
            face_image_resolution=request.face_image_resolution,
            user_tier=user_tier,
            preferences=request.preferences,
        )
        return FaceSwapModelRecommendationResponse(**result)
    except Exception as e:
        logger.error(f"[Face Swap Recommend] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get recommendation: {e}")
