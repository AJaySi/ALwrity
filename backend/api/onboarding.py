"""Onboarding API endpoints for ALwrity."""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import os
from loguru import logger
import time

# Import the existing progress tracking system
from services.api_key_manager import (
    OnboardingProgress, 
    get_onboarding_progress, 
    StepStatus, 
    StepData,
    APIKeyManager
)
from services.validation import check_all_api_keys

# Pydantic models for API requests/responses
class StepDataModel(BaseModel):
    step_number: int
    title: str
    description: str
    status: str
    completed_at: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    validation_errors: List[str] = []

class OnboardingProgressModel(BaseModel):
    steps: List[StepDataModel]
    current_step: int
    started_at: str
    last_updated: str
    is_completed: bool
    completed_at: Optional[str] = None

class StepCompletionRequest(BaseModel):
    data: Optional[Dict[str, Any]] = None
    validation_errors: List[str] = []

class APIKeyRequest(BaseModel):
    provider: str = Field(..., description="API provider name (e.g., 'openai', 'gemini')")
    api_key: str = Field(..., description="API key value")
    description: Optional[str] = Field(None, description="Optional description")

class OnboardingStatusResponse(BaseModel):
    is_completed: bool
    current_step: int
    completion_percentage: float
    next_step: Optional[int]
    started_at: str
    completed_at: Optional[str] = None
    can_proceed_to_final: bool

class StepValidationResponse(BaseModel):
    can_proceed: bool
    validation_errors: List[str]
    step_status: str

# Dependency to get progress instance
def get_progress() -> OnboardingProgress:
    """Get the current onboarding progress instance."""
    return get_onboarding_progress()

# Dependency to get API key manager
def get_api_key_manager() -> APIKeyManager:
    """Get the API key manager instance."""
    return APIKeyManager()

# Health check endpoint
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Onboarding status endpoints
async def get_onboarding_status():
    """Get the current onboarding status."""
    try:
        progress = get_onboarding_progress()
        
        # Safety check: if all steps are completed, ensure is_completed is True
        all_steps_completed = all(s.status in [StepStatus.COMPLETED, StepStatus.SKIPPED] for s in progress.steps)
        if all_steps_completed and not progress.is_completed:
            logger.info(f"[get_onboarding_status] All steps completed but is_completed was False, fixing...")
            progress.is_completed = True
            progress.completed_at = datetime.now().isoformat()
            progress.current_step = len(progress.steps)  # Ensure current_step is valid
            progress.save_progress()
        
        logger.info(f"[get_onboarding_status] Current step: {progress.current_step}")
        logger.info(f"[get_onboarding_status] Is completed: {progress.is_completed}")
        logger.info(f"[get_onboarding_status] Steps status: {[f'{s.step_number}:{s.status.value}' for s in progress.steps]}")
        
        return OnboardingStatusResponse(
            is_completed=progress.is_completed,
            current_step=progress.current_step,
            completion_percentage=progress.get_completion_percentage(),
            next_step=progress.get_next_incomplete_step(),
            started_at=progress.started_at,
            completed_at=progress.completed_at,
            can_proceed_to_final=progress.can_complete_onboarding()
        )
    except Exception as e:
        logger.error(f"Error getting onboarding status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def get_onboarding_progress_full():
    """Get the full onboarding progress data."""
    try:
        progress = get_onboarding_progress()
        # Convert StepData objects to Pydantic models
        step_models = []
        for step in progress.steps:
            step_models.append(StepDataModel(
                step_number=step.step_number,
                title=step.title,
                description=step.description,
                status=step.status.value,
                completed_at=step.completed_at,
                data=step.data,
                validation_errors=step.validation_errors or []
            ))
        
        return OnboardingProgressModel(
            steps=step_models,
            current_step=progress.current_step,
            started_at=progress.started_at,
            last_updated=progress.last_updated,
            is_completed=progress.is_completed,
            completed_at=progress.completed_at
        )
    except Exception as e:
        logger.error(f"Error getting onboarding progress: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def get_step_data(step_number: int):
    """Get data for a specific step."""
    try:
        progress = get_onboarding_progress()
        step = progress.get_step_data(step_number)
        
        if not step:
            raise HTTPException(status_code=404, detail=f"Step {step_number} not found")
        
        return StepDataModel(
            step_number=step.step_number,
            title=step.title,
            description=step.description,
            status=step.status.value,
            completed_at=step.completed_at,
            data=step.data,
            validation_errors=step.validation_errors or []
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting step data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def complete_step(step_number: int, request: StepCompletionRequest):
    """Mark a step as completed."""
    try:
        logger.info(f"[complete_step] Completing step {step_number}")
        progress = get_onboarding_progress()
        step = progress.get_step_data(step_number)
        
        if not step:
            logger.error(f"[complete_step] Step {step_number} not found")
            raise HTTPException(status_code=404, detail=f"Step {step_number} not found")
        
        # Mark step as completed
        progress.mark_step_completed(step_number, request.data)
        logger.info(f"[complete_step] Step {step_number} completed successfully")
        
        return {
            "message": f"Step {step_number} completed successfully",
            "step_number": step_number,
            "data": request.data
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing step: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def skip_step(step_number: int):
    """Skip a step (for optional steps)."""
    try:
        progress = get_onboarding_progress()
        step = progress.get_step_data(step_number)
        
        if not step:
            raise HTTPException(status_code=404, detail=f"Step {step_number} not found")
        
        # Mark step as skipped
        progress.mark_step_skipped(step_number)
        
        return {
            "message": f"Step {step_number} skipped successfully",
            "step_number": step_number
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error skipping step: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def validate_step_access(step_number: int):
    """Validate if user can access a specific step."""
    try:
        progress = get_onboarding_progress()
        
        if not progress.can_proceed_to_step(step_number):
            return StepValidationResponse(
                can_proceed=False,
                validation_errors=[f"Cannot proceed to step {step_number}. Complete previous steps first."],
                step_status="locked"
            )
        
        return StepValidationResponse(
            can_proceed=True,
            validation_errors=[],
            step_status="available"
        )
    except Exception as e:
        logger.error(f"Error validating step access: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Simple cache for API keys
_api_keys_cache = None
_cache_timestamp = 0
CACHE_DURATION = 30  # Cache for 30 seconds

async def get_api_keys():
    """Get all configured API keys (masked)."""
    global _api_keys_cache, _cache_timestamp
    
    current_time = time.time()
    
    # Return cached result if still valid
    if _api_keys_cache and (current_time - _cache_timestamp) < CACHE_DURATION:
        logger.debug("Returning cached API keys")
        return _api_keys_cache
    
    try:
        api_manager = APIKeyManager()
        api_manager.load_api_keys()  # Load keys from environment
        api_keys = api_manager.api_keys  # Get the loaded keys
        
        # Mask the API keys for security
        masked_keys = {}
        for provider, key in api_keys.items():
            if key:
                masked_keys[provider] = "*" * (len(key) - 4) + key[-4:] if len(key) > 4 else "*" * len(key)
            else:
                masked_keys[provider] = None
        
        result = {
            "api_keys": masked_keys,
            "total_providers": len(api_keys),
            "configured_providers": [k for k, v in api_keys.items() if v]
        }
        
        # Cache the result
        _api_keys_cache = result
        _cache_timestamp = current_time
        
        return result
    except Exception as e:
        logger.error(f"Error getting API keys: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def save_api_key(request: APIKeyRequest):
    """Save an API key for a provider."""
    try:
        api_manager = APIKeyManager()
        success = api_manager.save_api_key(request.provider, request.api_key)
        
        if success:
            return {
                "message": f"API key for {request.provider} saved successfully",
                "provider": request.provider,
                "status": "saved"
            }
        else:
            raise HTTPException(status_code=400, detail=f"Failed to save API key for {request.provider}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving API key: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def validate_api_keys():
    """Validate all configured API keys."""
    try:
        api_manager = APIKeyManager()
        validation_results = check_all_api_keys(api_manager)
        
        return {
            "validation_results": validation_results.get('results', {}),
            "all_valid": validation_results.get('all_valid', False),
            "total_providers": len(validation_results.get('results', {}))
        }
    except Exception as e:
        logger.error(f"Error validating API keys: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def start_onboarding():
    """Start a new onboarding session."""
    try:
        progress = get_onboarding_progress()
        progress.reset_progress()
        
        return {
            "message": "Onboarding started successfully",
            "current_step": progress.current_step,
            "started_at": progress.started_at
        }
    except Exception as e:
        logger.error(f"Error starting onboarding: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def complete_onboarding():
    """Complete the onboarding process."""
    try:
        progress = get_onboarding_progress()
        
        # Check which required steps are missing
        required_steps = [1, 2, 3, 6]  # Steps 1, 2, 3, and 6 are required
        missing_steps = []
        
        for step_num in required_steps:
            step = progress.get_step_data(step_num)
            if step and step.status not in [StepStatus.COMPLETED, StepStatus.SKIPPED]:
                missing_steps.append(step.title)
        
        if missing_steps:
            missing_steps_str = ", ".join(missing_steps)
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot complete onboarding. The following steps must be completed first: {missing_steps_str}"
            )
        
        # Additional validation: Check if API keys are configured
        api_manager = get_api_key_manager()
        api_keys = api_manager.get_all_keys()
        if not api_keys:
            raise HTTPException(
                status_code=400,
                detail="Cannot complete onboarding. At least one AI provider API key must be configured."
            )
        
        # Generate writing persona from onboarding data
        try:
            from services.persona_analysis_service import PersonaAnalysisService
            persona_service = PersonaAnalysisService()
            
            # Use user_id = 1 for now (assuming single user system)
            user_id = 1
            persona_result = persona_service.generate_persona_from_onboarding(user_id)
            
            if "error" not in persona_result:
                logger.info(f"✅ Writing persona generated during onboarding completion: {persona_result.get('persona_id')}")
            else:
                logger.warning(f"⚠️ Persona generation failed during onboarding: {persona_result['error']}")
        except Exception as e:
            logger.warning(f"⚠️ Non-critical error generating persona during onboarding: {str(e)}")
        
        progress.complete_onboarding()
        
        return {
            "message": "Onboarding completed successfully",
            "completed_at": progress.completed_at,
            "completion_percentage": 100.0,
            "persona_generated": "error" not in persona_result if 'persona_result' in locals() else False
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing onboarding: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def reset_onboarding():
    """Reset the onboarding progress."""
    try:
        progress = get_onboarding_progress()
        progress.reset_progress()
        
        return {
            "message": "Onboarding progress reset successfully",
            "current_step": progress.current_step,
            "started_at": progress.started_at
        }
    except Exception as e:
        logger.error(f"Error resetting onboarding: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def get_resume_info():
    """Get information for resuming onboarding."""
    try:
        progress = get_onboarding_progress()
        
        if progress.is_completed:
            return {
                "can_resume": False,
                "message": "Onboarding is already completed",
                "completion_percentage": 100.0
            }
        
        resume_step = progress.get_resume_step()
        
        return {
            "can_resume": True,
            "resume_step": resume_step,
            "current_step": progress.current_step,
            "completion_percentage": progress.get_completion_percentage(),
            "started_at": progress.started_at,
            "last_updated": progress.last_updated
        }
    except Exception as e:
        logger.error(f"Error getting resume info: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

def get_onboarding_config():
    """Get onboarding configuration and requirements."""
    return {
        "total_steps": 6,
        "steps": [
            {
                "number": 1,
                "title": "AI LLM Providers",
                "description": "Configure AI language model providers",
                "required": True,
                "providers": ["openai", "gemini", "anthropic"]
            },
            {
                "number": 2,
                "title": "Website Analysis",
                "description": "Set up website analysis and crawling",
                "required": True
            },
            {
                "number": 3,
                "title": "AI Research",
                "description": "Configure AI research capabilities",
                "required": True
            },
            {
                "number": 4,
                "title": "Personalization",
                "description": "Set up personalization features",
                "required": False
            },
            {
                "number": 5,
                "title": "Integrations",
                "description": "Configure ALwrity integrations",
                "required": False
            },
            {
                "number": 6,
                "title": "Complete Setup",
                "description": "Finalize and complete onboarding",
                "required": True
            }
        ],
        "requirements": {
            "min_api_keys": 1,
            "required_providers": ["openai"],
            "optional_providers": ["gemini", "anthropic"]
        }
    } 

# Add new endpoints for enhanced functionality

async def get_provider_setup_info(provider: str):
    """Get setup information for a specific provider."""
    try:
        providers_info = get_all_providers_info()
        if provider in providers_info:
            return providers_info[provider]
        else:
            raise HTTPException(status_code=404, detail=f"Provider {provider} not found")
    except Exception as e:
        logger.error(f"Error getting provider setup info: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def get_all_providers_info():
    """Get setup information for all providers."""
    return {
        "openai": {
            "name": "OpenAI",
            "description": "GPT-4 and GPT-3.5 models for content generation",
            "setup_url": "https://platform.openai.com/api-keys",
            "required_fields": ["api_key"],
            "optional_fields": ["organization_id"]
        },
        "gemini": {
            "name": "Google Gemini",
            "description": "Google's advanced AI models for content creation",
            "setup_url": "https://makersuite.google.com/app/apikey",
            "required_fields": ["api_key"],
            "optional_fields": []
        },
        "anthropic": {
            "name": "Anthropic",
            "description": "Claude models for sophisticated content generation",
            "setup_url": "https://console.anthropic.com/",
            "required_fields": ["api_key"],
            "optional_fields": []
        }
    }

async def validate_provider_key(provider: str, request: APIKeyRequest):
    """Validate a specific provider's API key."""
    try:
        result = await validate_api_key(provider, request.api_key)
        return result
    except Exception as e:
        logger.error(f"Error validating provider key: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def get_enhanced_validation_status():
    """Get enhanced validation status for all configured services."""
    try:
        return await check_all_api_keys(get_api_key_manager())
    except Exception as e:
        logger.error(f"Error getting enhanced validation status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# New endpoints for FinalStep data loading
async def get_onboarding_summary():
    """Get comprehensive onboarding summary for FinalStep."""
    try:
        from services.database import get_db
        from services.website_analysis_service import WebsiteAnalysisService
        from services.research_preferences_service import ResearchPreferencesService
        from services.persona_analysis_service import PersonaAnalysisService
        
        # Get current session (assuming session ID 1 for now)
        session_id = 1
        user_id = 1  # Assuming single user system for now
        
        # Get API keys
        api_manager = get_api_key_manager()
        api_keys = api_manager.get_all_keys()
        
        # Get website analysis data
        db = next(get_db())
        website_service = WebsiteAnalysisService(db)
        website_analysis = website_service.get_analysis_by_session(session_id)
        
        # Get research preferences
        research_service = ResearchPreferencesService(db)
        research_preferences = research_service.get_research_preferences(session_id)
        
        # Get personalization settings (from research preferences)
        personalization_settings = None
        if research_preferences:
            personalization_settings = {
                'writing_style': research_preferences.get('writing_style', {}).get('tone', 'Professional'),
                'tone': research_preferences.get('writing_style', {}).get('voice', 'Formal'),
                'brand_voice': research_preferences.get('writing_style', {}).get('complexity', 'Trustworthy and Expert')
            }
        
        # Check persona generation readiness
        persona_service = PersonaAnalysisService()
        persona_readiness = None
        try:
            # Check if persona can be generated
            onboarding_data = persona_service._collect_onboarding_data(user_id)
            if onboarding_data:
                data_sufficiency = persona_service._calculate_data_sufficiency(onboarding_data)
                persona_readiness = {
                    "ready": data_sufficiency >= 50.0,
                    "data_sufficiency": data_sufficiency,
                    "can_generate": website_analysis is not None
                }
        except Exception as e:
            logger.warning(f"Could not check persona readiness: {str(e)}")
            persona_readiness = {"ready": False, "error": str(e)}
        
        return {
            "api_keys": api_keys,
            "website_url": website_analysis.get('website_url') if website_analysis else None,
            "style_analysis": website_analysis.get('style_analysis') if website_analysis else None,
            "research_preferences": research_preferences,
            "personalization_settings": personalization_settings,
            "persona_readiness": persona_readiness,
            "integrations": {},  # TODO: Implement integrations data
            "capabilities": {
                "ai_content": len(api_keys) > 0,
                "style_analysis": website_analysis is not None,
                "research_tools": research_preferences is not None,
                "personalization": personalization_settings is not None,
                "persona_generation": persona_readiness.get("ready", False) if persona_readiness else False,
                "integrations": False  # TODO: Implement
            }
        }
    except Exception as e:
        logger.error(f"Error getting onboarding summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def get_website_analysis_data():
    """Get website analysis data for FinalStep."""
    try:
        from services.database import get_db
        from services.website_analysis_service import WebsiteAnalysisService
        
        session_id = 1
        db = next(get_db())
        website_service = WebsiteAnalysisService(db)
        analysis = website_service.get_analysis_by_session(session_id)
        
        if analysis:
            return {
                "website_url": analysis.get('website_url'),
                "style_analysis": analysis.get('style_analysis'),
                "style_patterns": analysis.get('style_patterns'),
                "style_guidelines": analysis.get('style_guidelines'),
                "status": analysis.get('status'),
                "completed_at": analysis.get('created_at')
            }
        else:
            return None
    except Exception as e:
        logger.error(f"Error getting website analysis data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def get_research_preferences_data():
    """Get research preferences data for FinalStep."""
    try:
        from services.database import get_db
        from services.research_preferences_service import ResearchPreferencesService
        
        session_id = 1
        db = next(get_db())
        research_service = ResearchPreferencesService(db)
        preferences = research_service.get_research_preferences(session_id)
        
        return preferences
    except Exception as e:
        logger.error(f"Error getting research preferences data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# New persona-related endpoints

async def check_persona_generation_readiness(user_id: int = 1):
    """Check if user has sufficient data for persona generation."""
    try:
        from api.persona import validate_persona_generation_readiness
        return await validate_persona_generation_readiness(user_id)
    except Exception as e:
        logger.error(f"Error checking persona readiness: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def generate_persona_preview(user_id: int = 1):
    """Generate a preview of the writing persona without saving."""
    try:
        from api.persona import generate_persona_preview
        return await generate_persona_preview(user_id)
    except Exception as e:
        logger.error(f"Error generating persona preview: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def generate_writing_persona(user_id: int = 1):
    """Generate and save a writing persona from onboarding data."""
    try:
        from api.persona import generate_persona, PersonaGenerationRequest
        request = PersonaGenerationRequest(force_regenerate=False)
        return await generate_persona(user_id, request)
    except Exception as e:
        logger.error(f"Error generating writing persona: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def get_user_writing_personas(user_id: int = 1):
    """Get all writing personas for the user."""
    try:
        from api.persona import get_user_personas
        return await get_user_personas(user_id)
    except Exception as e:
        logger.error(f"Error getting user personas: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") 

# Business Information endpoints
async def save_business_info(business_info: 'BusinessInfoRequest'):
    """Save business information for users without websites."""
    try:
        from models.business_info_request import BusinessInfoRequest
        from services.business_info_service import business_info_service
        
        logger.info(f"🔄 Saving business info for user_id: {business_info.user_id}")
        result = business_info_service.save_business_info(business_info)
        logger.success(f"✅ Business info saved successfully for user_id: {business_info.user_id}")
        return result
    except Exception as e:
        logger.error(f"❌ Error saving business info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save business info: {str(e)}")

async def get_business_info(business_info_id: int):
    """Get business information by ID."""
    try:
        from services.business_info_service import business_info_service
        
        logger.info(f"🔄 Getting business info for ID: {business_info_id}")
        result = business_info_service.get_business_info(business_info_id)
        if result:
            logger.success(f"✅ Business info retrieved for ID: {business_info_id}")
            return result
        else:
            logger.warning(f"⚠️ No business info found for ID: {business_info_id}")
            raise HTTPException(status_code=404, detail="Business info not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting business info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get business info: {str(e)}")

async def get_business_info_by_user(user_id: int):
    """Get business information by user ID."""
    try:
        from services.business_info_service import business_info_service
        
        logger.info(f"🔄 Getting business info for user ID: {user_id}")
        result = business_info_service.get_business_info_by_user(user_id)
        if result:
            logger.success(f"✅ Business info retrieved for user ID: {user_id}")
            return result
        else:
            logger.warning(f"⚠️ No business info found for user ID: {user_id}")
            raise HTTPException(status_code=404, detail="Business info not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting business info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get business info: {str(e)}")

async def update_business_info(business_info_id: int, business_info: 'BusinessInfoRequest'):
    """Update business information."""
    try:
        from models.business_info_request import BusinessInfoRequest
        from services.business_info_service import business_info_service
        
        logger.info(f"🔄 Updating business info for ID: {business_info_id}")
        result = business_info_service.update_business_info(business_info_id, business_info)
        if result:
            logger.success(f"✅ Business info updated for ID: {business_info_id}")
            return result
        else:
            logger.warning(f"⚠️ No business info found to update for ID: {business_info_id}")
            raise HTTPException(status_code=404, detail="Business info not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error updating business info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update business info: {str(e)}")
