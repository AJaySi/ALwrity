"""Image Studio Generation Router - Core image generation and related functionality."""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException

from ...services.image_studio import ImageStudioManager
from ...services.image_studio.templates import Platform, TemplateCategory
from middleware.auth_middleware import get_current_user
from utils.logger_utils import get_service_logger

from .models.generation import CreateImageRequest, CostEstimationRequest
from .utils import _require_user_id
from .dependencies import get_studio_manager

import base64

logger = get_service_logger("api.image_studio.generation")
router = APIRouter()


# ====================
# CREATE STUDIO ENDPOINTS
# ====================

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
        from services.image_studio import CreateStudioRequest
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

        # Generate images
        result = await studio_manager.create_image(studio_request, user_id=user_id)

        # Convert image bytes to base64 for JSON response
        for idx, img_result in enumerate(result["results"]):
            if "image_bytes" in img_result:
                img_result["image_base64"] = base64.b64encode(img_result["image_bytes"]).decode("utf-8")
                # Remove bytes from response
                del img_result["image_bytes"]

        logger.info(f"[Create Image] ✅ Success: {result['total_generated']} images generated")
        return result

    except ValueError as e:
        logger.error(f"[Create Image] ❌ Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        logger.error(f"[Create Image] ❌ Generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")
    except Exception as e:
        logger.error(f"[Create Image] ❌ Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ====================
# TEMPLATE ENDPOINTS
# ====================

@router.get("/templates", summary="Get Templates")
async def get_templates(
    platform: Optional[Platform] = None,
    category: Optional[TemplateCategory] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager)
):
    """Get available image templates.

    Templates provide pre-configured settings for common use cases:
    - Platform-specific dimensions and formats
    - Recommended providers and models
    - Style presets and quality settings

    Args:
        platform: Filter by platform (instagram, facebook, twitter, etc.)
        category: Filter by category (social_media, blog_content, ad_creative, etc.)

    Returns:
        List of templates
    """
    try:
        templates = studio_manager.get_templates(platform=platform, category=category)

        # Convert to dict for JSON response
        templates_dict = [
            {
                "id": t.id,
                "name": t.name,
                "category": t.category.value,
                "platform": t.platform.value if t.platform else None,
                "aspect_ratio": {
                    "ratio": t.aspect_ratio.ratio,
                    "width": t.aspect_ratio.width,
                    "height": t.aspect_ratio.height,
                    "label": t.aspect_ratio.label,
                },
                "description": t.description,
                "recommended_provider": t.recommended_provider,
                "style_preset": t.style_preset,
                "quality": t.quality,
                "use_cases": t.use_cases or [],
            }
            for t in templates
        ]

        return {"templates": templates_dict, "total": len(templates_dict)}

    except Exception as e:
        logger.error(f"[Get Templates] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates/search", summary="Search Templates")
async def search_templates(
    query: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager)
):
    """Search templates by query.

    Searches in template names, descriptions, and use cases.

    Args:
        query: Search query

    Returns:
        List of matching templates
    """
    try:
        templates = studio_manager.search_templates(query)

        templates_dict = [
            {
                "id": t.id,
                "name": t.name,
                "category": t.category.value,
                "platform": t.platform.value if t.platform else None,
                "aspect_ratio": {
                    "ratio": t.aspect_ratio.ratio,
                    "width": t.aspect_ratio.width,
                    "height": t.aspect_ratio.height,
                    "label": t.aspect_ratio.label,
                },
                "description": t.description,
                "recommended_provider": t.recommended_provider,
                "style_preset": t.style_preset,
                "quality": t.quality,
                "use_cases": t.use_cases or [],
            }
            for t in templates
        ]

        return {"templates": templates_dict, "total": len(templates_dict), "query": query}

    except Exception as e:
        logger.error(f"[Search Templates] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates/recommend", summary="Recommend Templates")
async def recommend_templates(
    use_case: str,
    platform: Optional[Platform] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager)
):
    """Recommend templates based on use case.

    Args:
        use_case: Description of use case (e.g., "product showcase", "blog header")
        platform: Optional platform filter

    Returns:
        List of recommended templates
    """
    try:
        templates = studio_manager.recommend_templates(use_case, platform=platform)

        templates_dict = [
            {
                "id": t.id,
                "name": t.name,
                "category": t.category.value,
                "platform": t.platform.value if t.platform else None,
                "aspect_ratio": {
                    "ratio": t.aspect_ratio.ratio,
                    "width": t.aspect_ratio.width,
                    "height": t.aspect_ratio.height,
                    "label": t.aspect_ratio.label,
                },
                "description": t.description,
                "recommended_provider": t.recommended_provider,
                "style_preset": t.style_preset,
                "quality": t.quality,
                "use_cases": t.use_cases or [],
            }
            for t in templates
        ]

        return {"templates": templates_dict, "total": len(templates_dict), "use_case": use_case}

    except Exception as e:
        logger.error(f"[Recommend Templates] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ====================
# PROVIDER ENDPOINTS
# ====================

@router.get("/providers", summary="Get Providers")
async def get_providers(
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager)
):
    """Get available AI providers and their capabilities.

    Returns information about:
    - Available models
    - Capabilities
    - Maximum resolution
    - Cost estimates

    Returns:
        Dictionary of providers
    """
    try:
        providers = studio_manager.get_providers()
        return {"providers": providers}

    except Exception as e:
        logger.error(f"[Get Providers] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ====================
# COST ESTIMATION ENDPOINTS
# ====================

@router.post("/estimate-cost", summary="Estimate Cost")
async def estimate_cost(
    request: CostEstimationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager)
):
    """Estimate cost for image generation operations.

    Provides cost estimates before generation to help users make informed decisions.

    Args:
        request: Cost estimation request

    Returns:
        Cost estimation details
    """
    try:
        resolution = None
        if request.width and request.height:
            resolution = (request.width, request.height)

        estimate = studio_manager.estimate_cost(
            provider=request.provider,
            model=request.model,
            operation=request.operation,
            num_images=request.num_images,
            resolution=resolution
        )

        return estimate

    except Exception as e:
        logger.error(f"[Estimate Cost] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))