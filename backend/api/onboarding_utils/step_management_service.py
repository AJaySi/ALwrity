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

            # Step-specific side effects: save API keys to DB
            if step_number == 1 and request_data and 'api_keys' in request_data:
                api_keys = request_data['api_keys'] or {}
                for provider, key in api_keys.items():
                    if key:
                        db_service.save_api_key(user_id, provider, key, db)

            # Persist current step and progress in DB
            db_service.update_step(user_id, step_number, db)
            try:
                progress_pct = min(100.0, round((step_number / 6) * 100))
                db_service.update_progress(user_id, float(progress_pct), db)
            except Exception:
                pass

            logger.info(f"[complete_step] Step {step_number} persisted to DB for user {user_id}")
            return {
                "message": "Step completed successfully",
                "step_number": step_number,
                "data": request_data or {}
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error completing step: {str(e)}")
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
