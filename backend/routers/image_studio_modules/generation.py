"""Generation-related API endpoints for Image Studio."""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query

from routers.image_studio_modules.models import CreateImageRequest, CostEstimationRequest
from routers.image_studio_modules.utils import _require_user_id
from routers.image_studio_modules.dependencies import get_studio_manager

from services.image_studio import ImageStudioManager, CreateStudioRequest
from middleware.auth_middleware import get_current_user
from utils.logger_utils import get_service_logger

logger = get_service_logger("api.image_studio.generation")
router = APIRouter()


@router.post("/create", summary="Generate Image")
async def create_image(
    request: CreateImageRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager)
):
    """Generate image(s) using Create Studio.

    This endpoint supports:
    - Multiple AI providers (Stability AI, WaveSpeed, HuggingFace, Gemini)
    - Template-based generation
    - Custom dimensions and aspect ratios
    - Style presets and quality levels
    - Multiple variations
    - Prompt enhancement

    Returns:
        Dictionary with generation results including image data
    """
    try:
        user_id = _require_user_id(current_user, "image generation")
        logger.info(f"[Create Image] Request from user {user_id}: {request.prompt[:100]}")

        # Convert request to CreateStudioRequest
        studio_request = CreateStudioRequest(
            prompt=request.prompt,
            template_id=request.template_id,
            provider=request.provider,
            model=request.model,
            width=request.width,
            height=request.height,
            aspect_ratio=request.aspect_ratio,
            style_preset=request.style_preset,
            quality=request.quality,
            negative_prompt=request.negative_prompt,
            guidance_scale=request.guidance_scale,
            steps=request.steps,
            seed=request.seed,
            num_variations=request.num_variations,
            enhance_prompt=request.enhance_prompt,
            use_persona=request.use_persona,
            persona_id=request.persona_id,
        )

        result = await studio_manager.create_image(studio_request, user_id=user_id)
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Create Image] ❌ Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Image generation failed: {e}")


@router.get("/providers", summary="Get Providers")
async def get_providers(
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Get available AI providers and their capabilities."""
    try:
        providers = studio_manager.get_providers()
        return {"providers": providers}
    except Exception as e:
        logger.error(f"[Get Providers] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to load providers")


@router.post("/estimate-cost", summary="Estimate Cost")
async def estimate_cost(
    request: CostEstimationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Estimate the cost of an image generation operation."""
    try:
        user_id = _require_user_id(current_user, "cost estimation")
        logger.info(f"[Cost Estimation] Request from user {user_id}: provider={request.provider}")

        cost_estimate = studio_manager.estimate_cost(
            provider=request.provider,
            model=request.model,
            operation=request.operation,
            num_images=request.num_images,
            width=request.width,
            height=request.height,
        )

        return cost_estimate

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Cost Estimation] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Cost estimation failed: {e}")


@router.get("/templates", summary="Get Templates")
async def get_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    limit: int = Query(50, ge=1, le=100, description="Number of templates to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Get available image generation templates."""
    try:
        templates = studio_manager.get_templates(
            category=category,
            platform=platform,
            limit=limit,
            offset=offset
        )
        return {"templates": templates}
    except Exception as e:
        logger.error(f"[Get Templates] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to load templates")


@router.get("/templates/search", summary="Search Templates")
async def search_templates(
    query: str = Query(..., description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    limit: int = Query(20, ge=1, le=50, description="Number of results to return"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Search for templates by name, description, or tags."""
    try:
        results = studio_manager.search_templates(
            query=query,
            category=category,
            platform=platform,
            limit=limit
        )
        return {"results": results}
    except Exception as e:
        logger.error(f"[Search Templates] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Template search failed")


@router.get("/templates/recommend", summary="Recommend Templates")
async def recommend_templates(
    prompt: str = Query(..., description="Image generation prompt"),
    limit: int = Query(5, ge=1, le=10, description="Number of recommendations"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Get template recommendations based on the user's prompt."""
    try:
        recommendations = studio_manager.recommend_templates(
            prompt=prompt,
            limit=limit
        )
        return {"recommendations": recommendations}
    except Exception as e:
        logger.error(f"[Recommend Templates] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Template recommendation failed")