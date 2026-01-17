"""
Step Management Service
Handles onboarding step operations and progress tracking.
"""

from typing import Dict, Any, List, Optional
from fastapi import HTTPException
from loguru import logger

from services.onboarding.progress_service import get_onboarding_progress_service
from services.onboarding.database_service import OnboardingDatabaseService
from services.database import get_db

class StepManagementService:
    """Service for handling onboarding step management."""
    
    def __init__(self):
        pass
    
    async def get_onboarding_status(self, current_user: Dict[str, Any]) -> Dict[str, Any]:
        """Get the current onboarding status (per user)."""
        try:
            user_id = str(current_user.get('id'))
            status = get_onboarding_progress_service().get_onboarding_status(user_id)
            return {
                "is_completed": status["is_completed"],
                "current_step": status["current_step"],
                "completion_percentage": status["completion_percentage"],
                "next_step": 6 if status["is_completed"] else max(1, status["current_step"]),
                "started_at": status["started_at"],
                "completed_at": status["completed_at"],
                "can_proceed_to_final": True if status["is_completed"] else status["current_step"] >= 5,
            }
        except Exception as e:
            logger.error(f"Error getting onboarding status: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def get_onboarding_progress_full(self, current_user: Dict[str, Any]) -> Dict[str, Any]:
        """Get the full onboarding progress data."""
        try:
            user_id = str(current_user.get('id'))
            progress_service = get_onboarding_progress_service()
            status = progress_service.get_onboarding_status(user_id)
            data = progress_service.get_completion_data(user_id)

            def completed(b: bool) -> str:
                return 'completed' if b else 'pending'

            api_keys = data.get('api_keys') or {}
            website = data.get('website_analysis') or {}
            research = data.get('research_preferences') or {}
            persona = data.get('persona_data') or {}

            steps = [
                {
                    "step_number": 1,
                    "title": "API Keys",
                    "description": "Connect your AI services",
                    "status": completed(any(v for v in api_keys.values() if v)),
                    "completed_at": None,
                    "data": None,
                    "validation_errors": []
                },
                {
                    "step_number": 2,
                    "title": "Website",
                    "description": "Set up your website",
                    "status": completed(bool(website.get('website_url') or website.get('writing_style'))),
                    "completed_at": None,
                    "data": website or None,
                    "validation_errors": []
                },
                {
                    "step_number": 3,
                    "title": "Research",
                    "description": "Discover competitors",
                    "status": completed(bool(research.get('research_depth') or research.get('content_types'))),
                    "completed_at": None,
                    "data": research or None,
                    "validation_errors": []
                },
                {
                    "step_number": 4,
                    "title": "Personalization",
                    "description": "Customize your experience",
                    "status": completed(bool(persona.get('corePersona') or persona.get('platformPersonas'))),
                    "completed_at": None,
                    "data": persona or None,
                    "validation_errors": []
                },
                {
                    "step_number": 5,
                    "title": "Integrations",
                    "description": "Connect additional services",
                    "status": completed(status['current_step'] >= 5),
                    "completed_at": None,
                    "data": None,
                    "validation_errors": []
                },
                {
                    "step_number": 6,
                    "title": "Finish",
                    "description": "Complete setup",
                    "status": completed(status['is_completed']),
                    "completed_at": status['completed_at'],
                    "data": None,
                    "validation_errors": []
                }
            ]

            return {
                "steps": steps,
                "current_step": 6 if status['is_completed'] else status['current_step'],
                "started_at": status['started_at'],
                "last_updated": status['last_updated'],
                "is_completed": status['is_completed'],
                "completed_at": status['completed_at'],
                "completion_percentage": status['completion_percentage']
            }
        except Exception as e:
            logger.error(f"Error getting onboarding progress: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def get_step_data(self, step_number: int, current_user: Dict[str, Any]) -> Dict[str, Any]:
        """Get data for a specific step."""
        try:
            user_id = str(current_user.get('id'))
            db = next(get_db())
            db_service = OnboardingDatabaseService()

            if step_number == 2:
                website = db_service.get_website_analysis(user_id, db) or {}
                return {
                    "step_number": 2,
                    "title": "Website",
                    "description": "Set up your website",
                    "status": 'completed' if (website.get('website_url') or website.get('writing_style')) else 'pending',
                    "completed_at": None,
                    "data": website,
                    "validation_errors": []
                }
            if step_number == 3:
                research = db_service.get_research_preferences(user_id, db) or {}
                return {
                    "step_number": 3,
                    "title": "Research",
                    "description": "Discover competitors",
                    "status": 'completed' if (research.get('research_depth') or research.get('content_types')) else 'pending',
                    "completed_at": None,
                    "data": research,
                    "validation_errors": []
                }
            if step_number == 4:
                persona = db_service.get_persona_data(user_id, db) or {}
                return {
                    "step_number": 4,
                    "title": "Personalization",
                    "description": "Customize your experience",
                    "status": 'completed' if (persona.get('corePersona') or persona.get('platformPersonas')) else 'pending',
                    "completed_at": None,
                    "data": persona,
                    "validation_errors": []
                }

            status = get_onboarding_progress_service().get_onboarding_status(user_id)
            mapping = {
                1: ('API Keys', 'Connect your AI services', status['current_step'] >= 1),
                5: ('Integrations', 'Connect additional services', status['current_step'] >= 5),
                6: ('Finish', 'Complete setup', status['is_completed'])
            }
            title, description, done = mapping.get(step_number, (f'Step {step_number}', 'Onboarding step', False))
            return {
                "step_number": step_number,
                "title": title,
                "description": description,
                "status": 'completed' if done else 'pending',
                "completed_at": status['completed_at'] if step_number == 6 and done else None,
                "data": None,
                "validation_errors": []
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting step data: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def complete_step(self, step_number: int, request_data: Dict[str, Any], current_user: Dict[str, Any]) -> Dict[str, Any]:
        """Mark a step as completed."""
        try:
            logger.info(f"[complete_step] Completing step {step_number}")
            user_id = str(current_user.get('id'))

            # Optional validation
            try:
                from services.validation import validate_step_data
                logger.info(f"[complete_step] Validating step {step_number} with data: {request_data}")
                validation_errors = validate_step_data(step_number, request_data)
                if validation_errors:
                    logger.warning(f"[complete_step] Step {step_number} validation failed: {validation_errors}")
                    raise HTTPException(status_code=400, detail=f"Step validation failed: {'; '.join(validation_errors)}")
            except ImportError:
                pass

            db = next(get_db())
            db_service = OnboardingDatabaseService()
            
            save_errors = []  # Track save failures

            # Step-specific side effects: save data to DB
            if step_number == 1 and request_data:
                # Step 1: Save API keys
                step_data = request_data.get('data') or request_data
                logger.info(f"🔍 Step 1: Raw request_data keys: {list(request_data.keys()) if request_data else 'None'}")
                logger.info(f"🔍 Step 1: Extracted step_data keys: {list(step_data.keys()) if step_data else 'None'}")
                api_keys = step_data.get('api_keys', {})
                logger.info(f"🔍 Step 1: API keys found: {list(api_keys.keys()) if api_keys else 'None'}")
                if api_keys:
                    for provider, key in api_keys.items():
                        if key:
                            try:
                                saved = db_service.save_api_key(user_id, provider, key, db)
                                if saved:
                                    logger.info(f"✅ Saved API key for provider {provider}")
                                else:
                                    # This should not happen anymore since save_api_key now raises exceptions
                                    raise Exception(f"API key save returned False for provider {provider}")
                            except Exception as e:
                                logger.error(f"❌ BLOCKING ERROR: Failed to save API key for provider {provider}: {str(e)}")
                                raise HTTPException(
                                    status_code=500,
                                    detail=f"Failed to save API key for {provider}. Onboarding cannot proceed until this is resolved."
                                ) from e

            # Step 2: Save website analysis data
            elif step_number == 2 and request_data:
                website_data = request_data.get('data') or request_data
                logger.info(f"🔍 Step 2: Raw request_data keys: {list(request_data.keys()) if request_data else 'None'}")
                logger.info(f"🔍 Step 2: Extracted website_data keys: {list(website_data.keys()) if website_data else 'None'}")
                logger.info(f"🔍 Step 2: website_data.website: {website_data.get('website') if website_data else 'None'}")
                logger.info(f"🔍 Step 2: website_data.analysis: {bool(website_data.get('analysis')) if website_data else 'None'}")
                if website_data.get('analysis'):
                    logger.info(f"🔍 Step 2: analysis keys: {list(website_data['analysis'].keys()) if isinstance(website_data.get('analysis'), dict) else 'Not dict'}")
                if website_data:
                    try:
                        saved = db_service.save_website_analysis(user_id, website_data, db)
                        if saved:
                            logger.info(f"✅ Saved website analysis for user {user_id}")
                        else:
                            # This should not happen anymore since save_website_analysis now raises exceptions
                            raise Exception("Website analysis save returned False")
                    except Exception as e:
                        logger.error(f"❌ BLOCKING ERROR: Failed to save website analysis: {str(e)}")
                        raise HTTPException(
                            status_code=500,
                            detail="Failed to save website analysis data. Onboarding cannot proceed until this is resolved."
                        ) from e

            # Step 3: Save research preferences data
            elif step_number == 3 and request_data:
                research_data = request_data.get('data') or request_data
                logger.info(f"🔍 Step 3: Raw request_data keys: {list(request_data.keys()) if request_data else 'None'}")
                logger.info(f"🔍 Step 3: Extracted research_data keys: {list(research_data.keys()) if research_data else 'None'}")
                if research_data:
                    # Note: Competitor data is saved separately via discover-competitors endpoint
                    # This saves research preferences (content_types, target_audience, etc.)
                    try:
                        saved = db_service.save_research_preferences(user_id, research_data, db)
                        if saved:
                            logger.info(f"✅ Saved research preferences for user {user_id}")
                        else:
                            # This should not happen anymore since save_research_preferences now raises exceptions
                            raise Exception("Research preferences save returned False")
                    except Exception as e:
                        logger.error(f"❌ BLOCKING ERROR: Failed to save research preferences: {str(e)}")
                        raise HTTPException(
                            status_code=500,
                            detail="Failed to save research preferences. Onboarding cannot proceed until this is resolved."
                        ) from e

            # Step 4: Save persona data
            elif step_number == 4 and request_data:
                persona_data = request_data.get('data') or request_data
                logger.info(f"🔍 Step 4: Raw request_data keys: {list(request_data.keys()) if request_data else 'None'}")
                logger.info(f"🔍 Step 4: Extracted persona_data keys: {list(persona_data.keys()) if persona_data else 'None'}")
                if persona_data:
                    try:
                        saved = db_service.save_persona_data(user_id, persona_data, db)
                        if saved:
                            logger.info(f"✅ Saved persona data for user {user_id}")
                        else:
                            # This should not happen anymore since save_persona_data now raises exceptions
                            raise Exception("Persona data save returned False")
                    except Exception as e:
                        logger.error(f"❌ BLOCKING ERROR: Failed to save persona data: {str(e)}")
                        raise HTTPException(
                            status_code=500,
                            detail="Failed to save persona data. Onboarding cannot proceed until this is resolved."
                        ) from e

            # Persist current step and progress in DB
            db_service.update_step(user_id, step_number, db)
            try:
                progress_pct = min(100.0, round((step_number / 6) * 100))
                db_service.update_progress(user_id, float(progress_pct), db)
            except Exception as e:
                logger.warning(f"Failed to update progress: {e}")

            # Log save errors but don't block step completion (non-blocking)
            if save_errors:
                logger.warning(f"⚠️ Step {step_number} completed but some data save operations failed: {save_errors}")
            
            logger.info(f"[complete_step] Step {step_number} persisted to DB for user {user_id}")
            return {
                "message": "Step completed successfully",
                "step_number": step_number,
                "data": request_data or {},
                "warnings": save_errors if save_errors else None  # Include warnings in response
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error completing step: {str(e)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def skip_step(self, step_number: int, current_user: Dict[str, Any]) -> Dict[str, Any]:
        """Skip a step (for optional steps)."""
        try:
            user_id = str(current_user.get('id'))
            progress = get_onboarding_progress_for_user(user_id)
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
    
    async def validate_step_access(self, step_number: int, current_user: Dict[str, Any]) -> Dict[str, Any]:
        """Validate if user can access a specific step."""
        try:
            user_id = str(current_user.get('id'))
            progress = get_onboarding_progress_for_user(user_id)
            
            if not progress.can_proceed_to_step(step_number):
                return {
                    "can_proceed": False,
                    "validation_errors": [f"Cannot proceed to step {step_number}. Complete previous steps first."],
                    "step_status": "locked"
                }
            
            return {
                "can_proceed": True,
                "validation_errors": [],
                "step_status": "available"
            }
        except Exception as e:
            logger.error(f"Error validating step access: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
