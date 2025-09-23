"""
FastAPI routes for persona management.
Integrates persona generation and management into the main API.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional

from api.persona import (
    generate_persona,
    get_user_personas,
    get_persona_details,
    get_platform_persona,
    update_persona,
    delete_persona,
    validate_persona_generation_readiness,
    generate_persona_preview,
    get_supported_platforms,
    validate_linkedin_persona,
    optimize_linkedin_persona,
    validate_facebook_persona,
    optimize_facebook_persona,
    PersonaGenerationRequest,
    LinkedInPersonaValidationRequest,
    LinkedInPersonaValidationResponse,
    LinkedInOptimizationRequest,
    LinkedInOptimizationResponse,
    FacebookPersonaValidationRequest,
    FacebookPersonaValidationResponse,
    FacebookOptimizationRequest,
    FacebookOptimizationResponse
)

from services.persona_replication_engine import PersonaReplicationEngine
from api.persona import update_platform_persona

# Create router
router = APIRouter(prefix="/api/personas", tags=["personas"])

@router.post("/generate")
async def generate_persona_endpoint(
    request: PersonaGenerationRequest,
    user_id: int = Query(1, description="User ID")
):
    """Generate a new writing persona from onboarding data."""
    return await generate_persona(user_id, request)

@router.get("/user/{user_id}")
async def get_user_personas_endpoint(user_id: int):
    """Get all personas for a user."""
    # Beta testing: Force user_id=1 for all requests
    return await get_user_personas(1)

@router.get("/{persona_id}")
async def get_persona_details_endpoint(
    persona_id: int,
    user_id: int = Query(..., description="User ID")
):
    """Get detailed information about a specific persona."""
    # Beta testing: Force user_id=1 for all requests
    return await get_persona_details(1, persona_id)

@router.get("/platform/{platform}")
async def get_platform_persona_endpoint(
    platform: str,
    user_id: int = Query(1, description="User ID")
):
    """Get persona adaptation for a specific platform."""
    # Beta testing: Force user_id=1 for all requests
    return await get_platform_persona(1, platform)

@router.put("/{persona_id}")
async def update_persona_endpoint(
    persona_id: int,
    update_data: Dict[str, Any],
    user_id: int = Query(..., description="User ID")
):
    """Update an existing persona."""
    # Beta testing: Force user_id=1 for all requests
    return await update_persona(1, persona_id, update_data)

@router.delete("/{persona_id}")
async def delete_persona_endpoint(
    persona_id: int,
    user_id: int = Query(..., description="User ID")
):
    """Delete a persona."""
    # Beta testing: Force user_id=1 for all requests
    return await delete_persona(1, persona_id)

@router.get("/check/readiness")
async def check_persona_readiness_endpoint(
    user_id: int = Query(1, description="User ID")
):
    """Check if user has sufficient data for persona generation."""
    # Beta testing: Force user_id=1 for all requests
    return await validate_persona_generation_readiness(1)

@router.get("/preview/generate")
async def generate_preview_endpoint(
    user_id: int = Query(1, description="User ID")
):
    """Generate a preview of the writing persona without saving."""
    # Beta testing: Force user_id=1 for all requests
    return await generate_persona_preview(1)

@router.get("/platforms/supported")
async def get_supported_platforms_endpoint():
    """Get list of supported platforms for persona generation."""
    return await get_supported_platforms()

@router.post("/linkedin/validate", response_model=LinkedInPersonaValidationResponse)
async def validate_linkedin_persona_endpoint(
    request: LinkedInPersonaValidationRequest
):
    """Validate LinkedIn persona data for completeness and quality."""
    return await validate_linkedin_persona(request)

@router.post("/linkedin/optimize", response_model=LinkedInOptimizationResponse)
async def optimize_linkedin_persona_endpoint(
    request: LinkedInOptimizationRequest
):
    """Optimize LinkedIn persona data for maximum algorithm performance."""
    return await optimize_linkedin_persona(request)

@router.post("/facebook/validate", response_model=FacebookPersonaValidationResponse)
async def validate_facebook_persona_endpoint(
    request: FacebookPersonaValidationRequest
):
    """Validate Facebook persona data for completeness and quality."""
    return await validate_facebook_persona(request)

@router.post("/facebook/optimize", response_model=FacebookOptimizationResponse)
async def optimize_facebook_persona_endpoint(
    request: FacebookOptimizationRequest
):
    """Optimize Facebook persona data for maximum algorithm performance."""
    return await optimize_facebook_persona(request)

@router.post("/generate-content")
async def generate_content_with_persona_endpoint(
    request: Dict[str, Any]
):
    """Generate content using persona replication engine."""
    try:
        # Beta testing: Force user_id=1 for all requests
        user_id = 1
        platform = request.get("platform")
        content_request = request.get("content_request")
        content_type = request.get("content_type", "post")
        
        if not platform or not content_request:
            raise HTTPException(status_code=400, detail="Platform and content_request are required")
        
        engine = PersonaReplicationEngine()
        result = engine.generate_content_with_persona(
            user_id=user_id,
            platform=platform,
            content_request=content_request,
            content_type=content_type
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")

@router.get("/export/{platform}")
async def export_persona_prompt_endpoint(
    platform: str,
    user_id: int = Query(1, description="User ID")
):
    """Export hardened persona prompt for external use."""
    try:
        engine = PersonaReplicationEngine()
        # Beta testing: Force user_id=1 for all requests
        export_package = engine.export_persona_for_external_use(1, platform)
        
        if "error" in export_package:
            raise HTTPException(status_code=400, detail=export_package["error"])
        
        return export_package
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.post("/validate-content")
async def validate_content_endpoint(
    request: Dict[str, Any]
):
    """Validate content against persona constraints."""
    try:
        # Beta testing: Force user_id=1 for all requests
        user_id = 1
        platform = request.get("platform")
        content = request.get("content")
        
        if not platform or not content:
            raise HTTPException(status_code=400, detail="Platform and content are required")
        
        engine = PersonaReplicationEngine()
        persona_data = engine.persona_service.get_persona_for_platform(user_id, platform)
        
        if not persona_data:
            raise HTTPException(status_code=404, detail="No persona found for platform")
        
        validation_result = engine._validate_content_fidelity(content, persona_data, platform)
        
        return {
            "validation_result": validation_result,
            "persona_id": persona_data["core_persona"]["id"],
            "platform": platform
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

@router.put("/platform/{platform}")
async def update_platform_persona_endpoint(
    platform: str,
    update_data: Dict[str, Any],
    user_id: int = Query(1, description="User ID")
):
    """Update platform-specific persona fields for a user.

    Allows editing persona fields in the UI and saving them to the database.
    """
    # Beta testing: Force user_id=1 for all requests
    return await update_platform_persona(1, platform, update_data)