"""
Persona API endpoints for ALwrity.
Handles writing persona generation, management, and platform-specific adaptations.
"""

from fastapi import HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger

from services.persona_analysis_service import PersonaAnalysisService
from services.database import get_db

class PersonaGenerationRequest(BaseModel):
    """Request model for persona generation."""
    onboarding_session_id: Optional[int] = Field(None, description="Specific onboarding session ID to use")
    force_regenerate: bool = Field(False, description="Force regeneration even if persona exists")

class PersonaResponse(BaseModel):
    """Response model for persona data."""
    persona_id: int
    persona_name: str
    archetype: str
    core_belief: str
    confidence_score: float
    platforms: List[str]
    created_at: str

class PlatformPersonaResponse(BaseModel):
    """Response model for platform-specific persona."""
    platform_type: str
    sentence_metrics: Dict[str, Any]
    lexical_features: Dict[str, Any]
    content_format_rules: Dict[str, Any]
    engagement_patterns: Dict[str, Any]
    platform_best_practices: Dict[str, Any]

class PersonaGenerationResponse(BaseModel):
    """Response model for persona generation result."""
    success: bool
    persona_id: Optional[int] = None
    message: str
    confidence_score: Optional[float] = None
    data_sufficiency: Optional[float] = None
    platforms_generated: List[str] = []

class LinkedInPersonaValidationRequest(BaseModel):
    """Request model for LinkedIn persona validation."""
    persona_data: Dict[str, Any]

class LinkedInPersonaValidationResponse(BaseModel):
    """Response model for LinkedIn persona validation."""
    is_valid: bool
    quality_score: float
    completeness_score: float
    professional_context_score: float
    linkedin_optimization_score: float
    missing_fields: List[str]
    incomplete_fields: List[str]
    recommendations: List[str]
    quality_issues: List[str]
    strengths: List[str]
    validation_details: Dict[str, Any]

# Dependency to get persona service
def get_persona_service() -> PersonaAnalysisService:
    """Get the persona analysis service instance."""
    return PersonaAnalysisService()

async def generate_persona(user_id: int, request: PersonaGenerationRequest):
    """Generate a new writing persona from onboarding data."""
    try:
        logger.info(f"Generating persona for user {user_id}")
        
        persona_service = get_persona_service()
        
        # Check if persona already exists and force_regenerate is False
        if not request.force_regenerate:
            existing_personas = persona_service.get_user_personas(user_id)
            if existing_personas:
                return PersonaGenerationResponse(
                    success=False,
                    message="Persona already exists. Use force_regenerate=true to create a new one.",
                    persona_id=existing_personas[0]["id"]
                )
        
        # Generate new persona
        result = persona_service.generate_persona_from_onboarding(
            user_id=user_id,
            onboarding_session_id=request.onboarding_session_id
        )
        
        if "error" in result:
            return PersonaGenerationResponse(
                success=False,
                message=result["error"]
            )
        
        return PersonaGenerationResponse(
            success=True,
            persona_id=result["persona_id"],
            message="Persona generated successfully",
            confidence_score=result["analysis_metadata"]["confidence_score"],
            data_sufficiency=result["analysis_metadata"].get("data_sufficiency", 0.0),
            platforms_generated=list(result["platform_personas"].keys())
        )
        
    except Exception as e:
        logger.error(f"Error generating persona: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate persona: {str(e)}")

async def get_user_personas(user_id: int):
    """Get all personas for a user."""
    try:
        persona_service = get_persona_service()
        personas = persona_service.get_user_personas(user_id)
        
        return {
            "personas": personas,
            "total_count": len(personas)
        }
        
    except Exception as e:
        logger.error(f"Error getting user personas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get personas: {str(e)}")

async def get_persona_details(user_id: int, persona_id: int):
    """Get detailed information about a specific persona."""
    try:
        from services.database import get_db_session
        from models.persona_models import WritingPersona, PlatformPersona
        
        session = get_db_session()
        
        # Get persona
        persona = session.query(WritingPersona).filter(
            WritingPersona.id == persona_id,
            WritingPersona.user_id == user_id,
            WritingPersona.is_active == True
        ).first()
        
        if not persona:
            raise HTTPException(status_code=404, detail="Persona not found")
        
        # Get platform adaptations
        platform_personas = session.query(PlatformPersona).filter(
            PlatformPersona.writing_persona_id == persona_id,
            PlatformPersona.is_active == True
        ).all()
        
        result = persona.to_dict()
        result["platform_adaptations"] = [pp.to_dict() for pp in platform_personas]
        
        session.close()
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting persona details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get persona details: {str(e)}")

async def get_platform_persona(user_id: int, platform: str):
    """Get persona adaptation for a specific platform."""
    try:
        persona_service = get_persona_service()
        platform_persona = persona_service.get_persona_for_platform(user_id, platform)
        
        if not platform_persona:
            raise HTTPException(status_code=404, detail=f"No persona found for platform {platform}")
        
        return platform_persona
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting platform persona: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get platform persona: {str(e)}")

async def update_persona(user_id: int, persona_id: int, update_data: Dict[str, Any]):
    """Update an existing persona."""
    try:
        from services.database import get_db_session
        from models.persona_models import WritingPersona
        
        session = get_db_session()
        
        persona = session.query(WritingPersona).filter(
            WritingPersona.id == persona_id,
            WritingPersona.user_id == user_id
        ).first()
        
        if not persona:
            raise HTTPException(status_code=404, detail="Persona not found")
        
        # Update allowed fields
        updatable_fields = [
            'persona_name', 'archetype', 'core_belief', 'brand_voice_description',
            'linguistic_fingerprint', 'platform_adaptations'
        ]
        
        for field in updatable_fields:
            if field in update_data:
                setattr(persona, field, update_data[field])
        
        persona.updated_at = datetime.utcnow()
        session.commit()
        session.close()
        
        return {
            "message": "Persona updated successfully",
            "persona_id": persona_id,
            "updated_at": persona.updated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating persona: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update persona: {str(e)}")

async def delete_persona(user_id: int, persona_id: int):
    """Delete a persona (soft delete by setting is_active=False)."""
    try:
        from services.database import get_db_session
        from models.persona_models import WritingPersona, PlatformPersona
        
        session = get_db_session()
        
        persona = session.query(WritingPersona).filter(
            WritingPersona.id == persona_id,
            WritingPersona.user_id == user_id
        ).first()
        
        if not persona:
            raise HTTPException(status_code=404, detail="Persona not found")
        
        # Soft delete persona and platform adaptations
        persona.is_active = False
        persona.updated_at = datetime.utcnow()
        
        platform_personas = session.query(PlatformPersona).filter(
            PlatformPersona.writing_persona_id == persona_id
        ).all()
        
        for pp in platform_personas:
            pp.is_active = False
            pp.updated_at = datetime.utcnow()
        
        session.commit()
        session.close()
        
        return {
            "message": "Persona deleted successfully",
            "persona_id": persona_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting persona: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete persona: {str(e)}")

async def update_platform_persona(user_id: int, platform: str, update_data: Dict[str, Any]):
    """Update platform-specific persona fields for a user's persona.

    This updates the underlying PlatformPersona row for the given platform.
    """
    try:
        from services.database import get_db_session
        from models.persona_models import WritingPersona, PlatformPersona

        session = get_db_session()

        # Find the user's active core persona id
        core_persona = session.query(WritingPersona).filter(
            WritingPersona.user_id == user_id,
            WritingPersona.is_active == True
        ).order_by(WritingPersona.created_at.desc()).first()

        if not core_persona:
            raise HTTPException(status_code=404, detail="No active persona found for user")

        # Find the platform persona for the requested platform
        platform_persona = session.query(PlatformPersona).filter(
            PlatformPersona.writing_persona_id == core_persona.id,
            PlatformPersona.platform_type.ilike(platform),
            PlatformPersona.is_active == True
        ).first()

        if not platform_persona:
            raise HTTPException(status_code=404, detail=f"No platform persona found for platform {platform}")

        # Update allowed platform fields
        updatable_fields = [
            'sentence_metrics', 'lexical_features', 'rhetorical_devices', 'tonal_range',
            'stylistic_constraints', 'content_format_rules', 'engagement_patterns',
            'posting_frequency', 'content_types', 'platform_best_practices', 'algorithm_considerations'
        ]

        updated_any = False
        for field in updatable_fields:
            if field in update_data:
                setattr(platform_persona, field, update_data[field])
                updated_any = True

        if not updated_any:
            # Nothing to update
            session.close()
            return {
                "message": "No updatable fields provided",
                "platform": platform_persona.platform_type,
                "persona_id": core_persona.id
            }

        platform_persona.updated_at = datetime.utcnow()
        session.commit()
        session.close()

        return {
            "message": "Platform persona updated successfully",
            "platform": platform,
            "persona_id": core_persona.id,
            "updated_at": platform_persona.updated_at.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating platform persona: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update platform persona: {str(e)}")

async def validate_persona_generation_readiness(user_id: int):
    """Check if user has sufficient onboarding data for persona generation."""
    try:
        persona_service = get_persona_service()
        
        # Get onboarding data
        onboarding_data = persona_service._collect_onboarding_data(user_id)
        
        if not onboarding_data:
            return {
                "ready": False,
                "message": "No onboarding data found. Please complete onboarding first.",
                "missing_steps": ["All onboarding steps"],
                "data_sufficiency": 0.0
            }
        
        data_sufficiency = persona_service._calculate_data_sufficiency(onboarding_data)
        
        missing_steps = []
        if not onboarding_data.get("website_analysis"):
            missing_steps.append("Website Analysis (Step 2)")
        if not onboarding_data.get("research_preferences"):
            missing_steps.append("Research Preferences (Step 3)")
        
        ready = data_sufficiency >= 50.0  # Require at least 50% data sufficiency
        
        return {
            "ready": ready,
            "message": "Ready for persona generation" if ready else "Insufficient data for reliable persona generation",
            "missing_steps": missing_steps,
            "data_sufficiency": data_sufficiency,
            "recommendations": [
                "Complete website analysis for better style detection",
                "Provide research preferences for content type optimization"
            ] if not ready else []
        }
        
    except Exception as e:
        logger.error(f"Error validating persona generation readiness: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to validate readiness: {str(e)}")

async def generate_persona_preview(user_id: int):
    """Generate a preview of what the persona would look like without saving."""
    try:
        persona_service = get_persona_service()
        
        # Get onboarding data
        onboarding_data = persona_service._collect_onboarding_data(user_id)
        
        if not onboarding_data:
            raise HTTPException(status_code=400, detail="No onboarding data available")
        
        # Generate core persona (without saving)
        core_persona = persona_service._generate_core_persona(onboarding_data)
        
        if "error" in core_persona:
            raise HTTPException(status_code=400, detail=core_persona["error"])
        
        # Generate sample platform adaptation (just one for preview)
        sample_platform = "linkedin"
        platform_preview = persona_service._generate_single_platform_persona(
            core_persona, sample_platform, onboarding_data
        )
        
        return {
            "preview": {
                "identity": core_persona.get("identity", {}),
                "linguistic_fingerprint": core_persona.get("linguistic_fingerprint", {}),
                "tonal_range": core_persona.get("tonal_range", {}),
                "sample_platform": {
                    "platform": sample_platform,
                    "adaptation": platform_preview
                }
            },
            "confidence_score": core_persona.get("confidence_score", 0.0),
            "data_sufficiency": persona_service._calculate_data_sufficiency(onboarding_data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating persona preview: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate preview: {str(e)}")

async def get_supported_platforms():
    """Get list of supported platforms for persona generation."""
    return {
        "platforms": [
            {
                "id": "twitter",
                "name": "Twitter/X",
                "description": "Microblogging platform optimized for short, engaging content",
                "character_limit": 280,
                "optimal_length": "120-150 characters"
            },
            {
                "id": "linkedin",
                "name": "LinkedIn",
                "description": "Professional networking platform for thought leadership content",
                "character_limit": 3000,
                "optimal_length": "150-300 words"
            },
            {
                "id": "instagram",
                "name": "Instagram",
                "description": "Visual-first platform with engaging captions",
                "character_limit": 2200,
                "optimal_length": "125-150 words"
            },
            {
                "id": "facebook",
                "name": "Facebook",
                "description": "Social networking platform for community engagement",
                "character_limit": 63206,
                "optimal_length": "40-80 words"
            },
            {
                "id": "blog",
                "name": "Blog Posts",
                "description": "Long-form content optimized for SEO and engagement",
                "word_count": "800-2000 words",
                "seo_optimized": True
            },
            {
                "id": "medium",
                "name": "Medium",
                "description": "Publishing platform for storytelling and thought leadership",
                "word_count": "1000-3000 words",
                "storytelling_focus": True
            },
            {
                "id": "substack",
                "name": "Substack",
                "description": "Newsletter platform for building subscriber relationships",
                "format": "email newsletter",
                "subscription_focus": True
                    }
    ]
}

class LinkedInOptimizationRequest(BaseModel):
    """Request model for LinkedIn algorithm optimization."""
    persona_data: Dict[str, Any]


class LinkedInOptimizationResponse(BaseModel):
    """Response model for LinkedIn algorithm optimization."""
    optimized_persona: Dict[str, Any]
    optimization_applied: bool
    optimization_details: Dict[str, Any]


async def validate_linkedin_persona(
    request: LinkedInPersonaValidationRequest,
    persona_service: PersonaAnalysisService = Depends(get_persona_service)
):
    """
    Validate LinkedIn persona data for completeness and quality.

    This endpoint provides comprehensive validation of LinkedIn persona data,
    including core fields, LinkedIn-specific optimizations, professional context,
    and content quality assessments.
    """
    try:
        logger.info("Validating LinkedIn persona data")

        # Get LinkedIn persona service
        from services.persona.linkedin.linkedin_persona_service import LinkedInPersonaService
        linkedin_service = LinkedInPersonaService()

        # Validate the persona data
        validation_results = linkedin_service.validate_linkedin_persona(request.persona_data)

        logger.info(f"LinkedIn persona validation completed: Quality Score: {validation_results['quality_score']:.1f}%")

        return LinkedInPersonaValidationResponse(**validation_results)

    except Exception as e:
        logger.error(f"Error validating LinkedIn persona: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to validate LinkedIn persona: {str(e)}"
        )


async def optimize_linkedin_persona(
    request: LinkedInOptimizationRequest,
    persona_service: PersonaAnalysisService = Depends(get_persona_service)
):
    """
    Optimize LinkedIn persona data for maximum algorithm performance.

    This endpoint applies comprehensive LinkedIn algorithm optimization to persona data,
    including content quality optimization, multimedia strategy, engagement optimization,
    timing optimization, and professional context optimization.
    """
    try:
        logger.info("Optimizing LinkedIn persona for algorithm performance")

        # Get LinkedIn persona service
        from services.persona.linkedin.linkedin_persona_service import LinkedInPersonaService
        linkedin_service = LinkedInPersonaService()

        # Apply algorithm optimization
        optimized_persona = linkedin_service.optimize_for_linkedin_algorithm(request.persona_data)

        # Extract optimization details
        optimization_details = optimized_persona.get("algorithm_optimization", {})
        
        logger.info("✅ LinkedIn persona algorithm optimization completed successfully")

        return LinkedInOptimizationResponse(
            optimized_persona=optimized_persona,
            optimization_applied=True,
            optimization_details={
                "optimization_categories": list(optimization_details.keys()),
                "total_optimization_strategies": sum(len(strategies) if isinstance(strategies, list) else 1 
                                                   for category in optimization_details.values() 
                                                   for strategies in category.values() if isinstance(category, dict)),
                "optimization_timestamp": datetime.utcnow().isoformat()
            }
        )

    except Exception as e:
        logger.error(f"Error optimizing LinkedIn persona: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to optimize LinkedIn persona: {str(e)}"
        )


class FacebookPersonaValidationRequest(BaseModel):
    """Request model for Facebook persona validation."""
    persona_data: Dict[str, Any]


class FacebookPersonaValidationResponse(BaseModel):
    """Response model for Facebook persona validation."""
    is_valid: bool
    quality_score: float
    completeness_score: float
    facebook_optimization_score: float
    engagement_strategy_score: float
    content_format_score: float
    audience_targeting_score: float
    community_building_score: float
    missing_fields: List[str]
    incomplete_fields: List[str]
    recommendations: List[str]
    quality_issues: List[str]
    strengths: List[str]
    validation_details: Dict[str, Any]


class FacebookOptimizationRequest(BaseModel):
    """Request model for Facebook algorithm optimization."""
    persona_data: Dict[str, Any]


class FacebookOptimizationResponse(BaseModel):
    """Response model for Facebook algorithm optimization."""
    optimized_persona: Dict[str, Any]
    optimization_applied: bool
    optimization_details: Dict[str, Any]


async def validate_facebook_persona(
    request: FacebookPersonaValidationRequest,
    persona_service: PersonaAnalysisService = Depends(get_persona_service)
):
    """
    Validate Facebook persona data for completeness and quality.

    This endpoint provides comprehensive validation of Facebook persona data,
    including core fields, Facebook-specific optimizations, engagement strategies,
    content formats, audience targeting, and community building assessments.
    """
    try:
        logger.info("Validating Facebook persona data")

        # Get Facebook persona service
        from services.persona.facebook.facebook_persona_service import FacebookPersonaService
        facebook_service = FacebookPersonaService()

        # Validate the persona data
        validation_results = facebook_service.validate_facebook_persona(request.persona_data)

        logger.info(f"Facebook persona validation completed: Quality Score: {validation_results['quality_score']:.1f}%")

        return FacebookPersonaValidationResponse(**validation_results)

    except Exception as e:
        logger.error(f"Error validating Facebook persona: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to validate Facebook persona: {str(e)}"
        )


async def optimize_facebook_persona(
    request: FacebookOptimizationRequest,
    persona_service: PersonaAnalysisService = Depends(get_persona_service)
):
    """
    Optimize Facebook persona data for maximum algorithm performance.

    This endpoint applies comprehensive Facebook algorithm optimization to persona data,
    including engagement optimization, content quality optimization, timing optimization,
    audience targeting optimization, and community building strategies.
    """
    try:
        logger.info("Optimizing Facebook persona for algorithm performance")

        # Get Facebook persona service
        from services.persona.facebook.facebook_persona_service import FacebookPersonaService
        facebook_service = FacebookPersonaService()

        # Apply algorithm optimization
        optimized_persona = facebook_service.optimize_for_facebook_algorithm(request.persona_data)

        # Extract optimization details
        optimization_details = optimized_persona.get("algorithm_optimization", {})
        
        logger.info("✅ Facebook persona algorithm optimization completed successfully")

        # Use the optimization metadata from the service
        optimization_metadata = optimized_persona.get("optimization_metadata", {})
        
        return FacebookOptimizationResponse(
            optimized_persona=optimized_persona,
            optimization_applied=True,
            optimization_details={
                "optimization_categories": optimization_metadata.get("optimization_categories", []),
                "total_optimization_strategies": optimization_metadata.get("total_optimization_strategies", 0),
                "optimization_timestamp": optimization_metadata.get("optimization_timestamp", datetime.utcnow().isoformat())
            }
        )

    except Exception as e:
        logger.error(f"Error optimizing Facebook persona: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to optimize Facebook persona: {str(e)}"
        )