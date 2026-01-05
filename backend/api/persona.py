"""
Persona API endpoints for ALwrity.
Handles writing persona generation, management, and platform-specific adaptations.
"""

from fastapi import HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger
from sqlalchemy.orm import Session

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

        # SUBSCRIPTION PRE-FLIGHT CHECK - Required before AI calls
        try:
            from services.database import get_db
            from services.subscription import UsageTrackingService, PricingService
            from models.subscription_models import UsageSummary
            from models.enums import APIProvider
            from datetime import datetime

            db = next(get_db())
            try:
                usage_service = UsageTrackingService(db)
                pricing_service = PricingService(db)

                # Estimate tokens for persona generation (comprehensive analysis)
                estimated_total_tokens = 8000

                # Check limits using sync method from pricing service
                provider_enum = APIProvider.GEMINI  # Use Gemini as default for persona generation
                can_proceed, message, usage_info = pricing_service.check_usage_limits(
                    user_id=str(user_id),
                    provider=provider_enum,
                    tokens_requested=estimated_total_tokens,
                    actual_provider_name="gemini"
                )

                if not can_proceed:
                    logger.warning(f"[generate_persona] Subscription limit exceeded for user {user_id}: {message}")
                    return PersonaGenerationResponse(
                        success=False,
                        message=f"Subscription limit exceeded: {message}",
                        usage_info=usage_info if usage_info else {},
                        timestamp=datetime.now().isoformat()
                    )

            finally:
                db.close()
        except Exception as sub_error:
            logger.error(f"[generate_persona] Subscription check failed for user {user_id}: {sub_error}")
            return PersonaGenerationResponse(
                success=False,
                message=f"Subscription check failed: {str(sub_error)}",
                timestamp=datetime.now().isoformat()
            )

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

async def get_user_personas(user_id: str):
    """Get all personas for a user using PersonaData."""
    try:
        from services.persona_data_service import PersonaDataService
        
        persona_service = PersonaDataService()
        all_personas = persona_service.get_all_platform_personas(user_id)
        
        return {
            "personas": all_personas,
            "total_count": len(all_personas),
            "platforms": list(all_personas.keys())
        }
        
    except Exception as e:
        logger.error(f"Error getting user personas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get personas: {str(e)}")

async def get_persona_details(user_id: str, persona_id: int):
    """Get detailed information about a specific persona using PersonaData."""
    try:
        from services.persona_data_service import PersonaDataService
        
        persona_service = PersonaDataService()
        persona_data = persona_service.get_user_persona_data(user_id)
        
        if not persona_data:
            raise HTTPException(status_code=404, detail="Persona not found")
        
        # Return the complete persona data with all platforms
        return {
            "persona_id": persona_data.get('id'),
            "core_persona": persona_data.get('core_persona', {}),
            "platform_personas": persona_data.get('platform_personas', {}),
            "quality_metrics": persona_data.get('quality_metrics', {}),
            "selected_platforms": persona_data.get('selected_platforms', []),
            "created_at": persona_data.get('created_at'),
            "updated_at": persona_data.get('updated_at')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting persona details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get persona details: {str(e)}")

async def get_platform_persona(user_id: str, platform: str):
    """Get persona adaptation for a specific platform using PersonaData."""
    try:
        from services.persona_data_service import PersonaDataService
        
        persona_service = PersonaDataService()
        platform_persona = persona_service.get_platform_persona(user_id, platform)
        
        if not platform_persona:
            raise HTTPException(status_code=404, detail=f"No persona found for platform {platform}")
        
        return platform_persona
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting platform persona: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get platform persona: {str(e)}")

async def get_persona_summary(user_id: str):
    """Get persona summary for a user using PersonaData."""
    try:
        from services.persona_data_service import PersonaDataService
        
        persona_service = PersonaDataService()
        summary = persona_service.get_persona_summary(user_id)
        
        return summary
        
    except Exception as e:
        logger.error(f"Error getting persona summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get persona summary: {str(e)}")

async def update_persona(user_id: str, persona_id: int, update_data: Dict[str, Any]):
    """Update an existing persona using PersonaData."""
    try:
        from services.persona_data_service import PersonaDataService
        from models.onboarding import PersonaData
        
        persona_service = PersonaDataService()
        
        # For PersonaData, we update the core_persona field
        if 'core_persona' in update_data:
            # Get current persona data
            persona_data = persona_service.get_user_persona_data(user_id)
            if not persona_data:
                raise HTTPException(status_code=404, detail="Persona not found")
            
            # Update core persona with new data
            persona_service.db.query(PersonaData).filter(
                PersonaData.id == persona_data.get('id')
            ).update({
                'core_persona': update_data['core_persona'],
                'updated_at': datetime.utcnow()
            })
            persona_service.db.commit()
            persona_service.db.close()
            
            return {
                "message": "Persona updated successfully",
                "persona_id": persona_data.get('id'),
                "updated_at": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail="core_persona field is required for updates")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating persona: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update persona: {str(e)}")

async def delete_persona(user_id: str, persona_id: int):
    """Delete a persona using PersonaData (not recommended, personas are generated during onboarding)."""
    try:
        from services.persona_data_service import PersonaDataService
        from models.onboarding import PersonaData
        
        persona_service = PersonaDataService()
        
        # Get persona data
        persona_data = persona_service.get_user_persona_data(user_id)
        if not persona_data:
            raise HTTPException(status_code=404, detail="Persona not found")
        
        # For PersonaData, we mark it as deleted by setting a flag
        # Note: In production, you might want to add a deleted_at field or similar
        # For now, we'll just return a warning that deletion is not recommended
        logger.warning(f"Delete persona requested for user {user_id}. PersonaData deletion is not recommended.")
        
        return {
            "message": "Persona deletion requested. Note: Personas are generated during onboarding and deletion is not recommended.",
            "persona_id": persona_data.get('id'),
            "alternative": "Consider re-running onboarding to regenerate persona if needed."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting persona: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete persona: {str(e)}")

async def update_platform_persona(user_id: str, platform: str, update_data: Dict[str, Any]):
    """Update platform-specific persona fields using PersonaData."""
    try:
        from services.persona_data_service import PersonaDataService

        persona_service = PersonaDataService()
        
        # Update platform-specific persona data
        success = persona_service.update_platform_persona(user_id, platform, update_data)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"No platform persona found for platform {platform}")

        return {
            "message": "Platform persona updated successfully",
            "platform": platform,
            "user_id": user_id,
            "updated_at": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating platform persona: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update platform persona: {str(e)}")

async def generate_platform_persona(user_id: str, platform: str, db_session):
    """
    Generate a platform-specific persona from core persona and save it.
    
    Args:
        user_id: User ID from auth
        platform: Platform name (facebook, linkedin, etc.)
        db_session: Database session from FastAPI dependency injection
    
    Returns:
        Generated platform persona with validation results
    """
    try:
        logger.info(f"Generating {platform} persona for user {user_id}")
        
        # Import services
        from services.persona_data_service import PersonaDataService
        from services.onboarding.database_service import OnboardingDatabaseService
        
        persona_data_service = PersonaDataService(db_session=db_session)
        onboarding_service = OnboardingDatabaseService(db=db_session)
        
        # Get core persona data
        persona_data = persona_data_service.get_user_persona_data(user_id)
        if not persona_data:
            raise HTTPException(status_code=404, detail="Core persona not found")
        
        core_persona = persona_data.get('core_persona', {})
        if not core_persona:
            raise HTTPException(status_code=404, detail="Core persona data is empty")
        
        # Get onboarding data for context
        onboarding_session = onboarding_service.get_session_by_user(user_id)
        if not onboarding_session:
            raise HTTPException(status_code=404, detail="Onboarding session not found")
        
        # Get website analysis for context
        website_analysis = onboarding_service.get_website_analysis(user_id)
        research_prefs = onboarding_service.get_research_preferences(user_id)
        
        onboarding_data = {
            "website_url": website_analysis.get('website_url', '') if website_analysis else '',
            "writing_style": website_analysis.get('writing_style', {}) if website_analysis else {},
            "content_characteristics": website_analysis.get('content_characteristics', {}) if website_analysis else {},
            "target_audience": website_analysis.get('target_audience', '') if website_analysis else '',
            "research_preferences": research_prefs or {}
        }
        
        # Generate platform persona based on platform
        generated_persona = None
        platform_service = None
        
        if platform.lower() == 'facebook':
            from services.persona.facebook.facebook_persona_service import FacebookPersonaService
            platform_service = FacebookPersonaService()
            generated_persona = platform_service.generate_facebook_persona(
                core_persona, 
                onboarding_data
            )
        elif platform.lower() == 'linkedin':
            from services.persona.linkedin.linkedin_persona_service import LinkedInPersonaService
            platform_service = LinkedInPersonaService()
            generated_persona = platform_service.generate_linkedin_persona(
                core_persona,
                onboarding_data
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")
        
        # Check for errors in generation
        if "error" in generated_persona:
            raise HTTPException(status_code=500, detail=generated_persona["error"])
        
        # Save the generated platform persona to database
        success = persona_data_service.save_platform_persona(user_id, platform, generated_persona)
        
        if not success:
            raise HTTPException(status_code=500, detail=f"Failed to save {platform} persona")
        
        logger.info(f"✅ Successfully generated and saved {platform} persona for user {user_id}")
        
        return {
            "success": True,
            "platform": platform,
            "persona": generated_persona,
            "validation_results": generated_persona.get("validation_results", {}),
            "quality_score": generated_persona.get("validation_results", {}).get("quality_score", 0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating {platform} persona: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate {platform} persona: {str(e)}")

async def check_facebook_persona(user_id: str, db: Session):
    """Check if Facebook persona exists for user."""
    try:
        from services.persona_data_service import PersonaDataService
        
        persona_data_service = PersonaDataService(db_session=db)
        persona_data = persona_data_service.get_user_persona_data(user_id)
        
        if not persona_data:
            return {
                "has_persona": False,
                "has_core_persona": False,
                "message": "No persona data found",
                "onboarding_completed": False
            }
        
        platform_personas = persona_data.get('platform_personas', {})
        facebook_persona = platform_personas.get('facebook') if platform_personas else None
        
        # Check if core persona exists
        has_core_persona = bool(persona_data.get('core_persona'))
        
        # Assume onboarding is completed if persona data exists
        onboarding_completed = True
        
        return {
            "has_persona": bool(facebook_persona),
            "has_core_persona": has_core_persona,
            "persona": facebook_persona,
            "onboarding_completed": onboarding_completed
        }
    except Exception as e:
        logger.error(f"Error checking Facebook persona for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
        # SUBSCRIPTION PRE-FLIGHT CHECK - Required before AI calls
        try:
            from services.database import get_db
            from services.subscription import UsageTrackingService, PricingService
            from models.subscription_models import UsageSummary
            from models.enums import APIProvider
            from datetime import datetime

            db = next(get_db())
            try:
                usage_service = UsageTrackingService(db)
                pricing_service = PricingService(db)

                # Estimate tokens for persona preview (smaller analysis)
                estimated_total_tokens = 4000

                # Check limits using sync method from pricing service
                provider_enum = APIProvider.GEMINI  # Use Gemini as default for persona preview
                can_proceed, message, usage_info = pricing_service.check_usage_limits(
                    user_id=str(user_id),
                    provider=provider_enum,
                    tokens_requested=estimated_total_tokens,
                    actual_provider_name="gemini"
                )

                if not can_proceed:
                    logger.warning(f"[generate_persona_preview] Subscription limit exceeded for user {user_id}: {message}")
                    raise HTTPException(
                        status_code=429,
                        detail={
                            'error': message,
                            'message': message,
                            'usage_info': usage_info if usage_info else {}
                        }
                    )

            finally:
                db.close()
        except HTTPException:
            raise
        except Exception as sub_error:
            logger.error(f"[generate_persona_preview] Subscription check failed for user {user_id}: {sub_error}")
            raise HTTPException(
                status_code=500,
                detail=f"Subscription check failed: {str(sub_error)}"
            )

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