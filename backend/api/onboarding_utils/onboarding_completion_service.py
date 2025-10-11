"""
Onboarding Completion Service
Handles the complex logic for completing the onboarding process.
"""

from typing import Dict, Any, List
from fastapi import HTTPException
from loguru import logger

from services.api_key_manager import get_onboarding_progress_for_user, get_api_key_manager, StepStatus
from services.onboarding_database_service import OnboardingDatabaseService
from services.database import get_db
from services.persona_analysis_service import PersonaAnalysisService

class OnboardingCompletionService:
    """Service for handling onboarding completion logic."""
    
    def __init__(self):
        # Only pre-requisite steps; step 6 is the finalization itself
        self.required_steps = [1, 2, 3]
    
    async def complete_onboarding(self, current_user: Dict[str, Any]) -> Dict[str, Any]:
        """Complete the onboarding process with full validation."""
        try:
            user_id = str(current_user.get('id'))
            progress = get_onboarding_progress_for_user(user_id)
            
            # Validate required steps are completed (with DB-aware fallbacks)
            missing_steps = self._validate_required_steps(user_id, progress)
            if missing_steps:
                missing_steps_str = ", ".join(missing_steps)
                raise HTTPException(
                    status_code=400, 
                    detail=f"Cannot complete onboarding. The following steps must be completed first: {missing_steps_str}"
                )
            
            # Validate API keys are configured
            self._validate_api_keys()
            
            # Generate writing persona from onboarding data
            persona_generated = await self._generate_persona_from_onboarding(user_id)
            
            # Complete the onboarding process
            progress.complete_onboarding()
            
            return {
                "message": "Onboarding completed successfully",
                "completed_at": progress.completed_at,
                "completion_percentage": 100.0,
                "persona_generated": persona_generated
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error completing onboarding: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    def _validate_required_steps(self, user_id: str, progress) -> List[str]:
        """Validate that all required steps are completed.

        This method trusts the progress tracker, but also falls back to
        database presence for Steps 2 and 3 so migration from file→DB
        does not block completion.
        """
        missing_steps = []
        db = None
        db_service = None
        try:
            db = next(get_db())
            db_service = OnboardingDatabaseService(db)
        except Exception:
            db = None
            db_service = None

        for step_num in self.required_steps:
            step = progress.get_step_data(step_num)
            if step and step.status in [StepStatus.COMPLETED, StepStatus.SKIPPED]:
                continue

            # DB-aware fallbacks for migration period
            try:
                if db_service:
                    if step_num == 2:
                        # Treat as completed if website analysis exists in DB
                        website = db_service.get_website_analysis(user_id, db)
                        if website and (website.get('website_url') or website.get('writing_style')):
                            # Optionally mark as completed in progress to keep state consistent
                            try:
                                progress.mark_step_completed(2, {'source': 'db-fallback'})
                            except Exception:
                                pass
                            continue
                        # Secondary fallback: research preferences captured style data
                        prefs = db_service.get_research_preferences(user_id, db)
                        if prefs and (prefs.get('writing_style') or prefs.get('content_characteristics')):
                            try:
                                progress.mark_step_completed(2, {'source': 'research-prefs-fallback'})
                            except Exception:
                                pass
                            continue
                        # Tertiary fallback: persona data created implies earlier steps done
                        persona = None
                        try:
                            persona = db_service.get_persona_data(user_id, db)
                        except Exception:
                            persona = None
                        if persona and persona.get('corePersona'):
                            try:
                                progress.mark_step_completed(2, {'source': 'persona-fallback'})
                            except Exception:
                                pass
                            continue
                    if step_num == 3:
                        # Treat as completed if research preferences exist in DB
                        prefs = db_service.get_research_preferences(user_id, db)
                        if prefs and prefs.get('research_depth'):
                            try:
                                progress.mark_step_completed(3, {'source': 'db-fallback'})
                            except Exception:
                                pass
                            continue
            except Exception:
                # If DB check fails, fall back to progress status only
                pass

            if step:
                missing_steps.append(step.title)
        
        return missing_steps
    
    def _validate_api_keys(self):
        """Validate that API keys are configured."""
        api_manager = get_api_key_manager()
        api_keys = api_manager.get_all_keys()
        if not api_keys:
            raise HTTPException(
                status_code=400,
                detail="Cannot complete onboarding. At least one AI provider API key must be configured."
            )
    
    async def _generate_persona_from_onboarding(self, user_id: str) -> bool:
        """Generate writing persona from onboarding data."""
        try:
            persona_service = PersonaAnalysisService()
            
            # Use user_id = 1 for now (assuming single user system)
            persona_user_id = 1
            persona_result = persona_service.generate_persona_from_onboarding(persona_user_id)
            
            if "error" not in persona_result:
                logger.info(f"✅ Writing persona generated during onboarding completion: {persona_result.get('persona_id')}")
                return True
            else:
                logger.warning(f"⚠️ Persona generation failed during onboarding: {persona_result['error']}")
                return False
        except Exception as e:
            logger.warning(f"⚠️ Non-critical error generating persona during onboarding: {str(e)}")
            return False
