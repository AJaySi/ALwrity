"""
Onboarding Completion Service
Handles the complex logic for completing the onboarding process.
"""

from typing import Dict, Any, List
from datetime import datetime
from fastapi import HTTPException
from loguru import logger

from services.onboarding_progress_service import get_onboarding_progress_service
from services.onboarding_database_service import OnboardingDatabaseService
from services.database import get_db
from services.persona_analysis_service import PersonaAnalysisService

class OnboardingCompletionService:
    """Service for handling onboarding completion logic."""
    
    def __init__(self):
        # Pre-requisite steps; step 6 is the finalization itself
        self.required_steps = [1, 2, 3, 4, 5]
    
    async def complete_onboarding(self, current_user: Dict[str, Any]) -> Dict[str, Any]:
        """Complete the onboarding process with full validation."""
        try:
            user_id = str(current_user.get('id'))
            progress_service = get_onboarding_progress_service()
            
            # Strict DB-only validation now that step persistence is solid
            missing_steps = self._validate_required_steps_database(user_id)
            if missing_steps:
                missing_steps_str = ", ".join(missing_steps)
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot complete onboarding. The following steps must be completed first: {missing_steps_str}"
                )

            # Require API keys in DB for completion
            self._validate_api_keys(user_id)
            
            # Generate writing persona from onboarding data only if not already present
            persona_generated = await self._generate_persona_from_onboarding(user_id)
            
            # Complete the onboarding process in database
            success = progress_service.complete_onboarding(user_id)
            if not success:
                raise HTTPException(status_code=500, detail="Failed to mark onboarding as complete")
            
            return {
                "message": "Onboarding completed successfully",
                "completed_at": datetime.now().isoformat(),
                "completion_percentage": 100.0,
                "persona_generated": persona_generated
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error completing onboarding: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    def _validate_required_steps_database(self, user_id: str) -> List[str]:
        """Validate that all required steps are completed using database only."""
        missing_steps = []
        try:
            db = next(get_db())
            db_service = OnboardingDatabaseService()
            
            # Debug logging
            logger.info(f"Validating steps for user {user_id}")
            
            # Check each required step
            for step_num in self.required_steps:
                step_completed = False
                
                if step_num == 1:  # API Keys
                    api_keys = db_service.get_api_keys(user_id, db)
                    logger.info(f"Step 1 - API Keys: {api_keys}")
                    step_completed = any(v for v in api_keys.values() if v)
                    logger.info(f"Step 1 completed: {step_completed}")
                elif step_num == 2:  # Website Analysis
                    website = db_service.get_website_analysis(user_id, db)
                    logger.info(f"Step 2 - Website Analysis: {website}")
                    step_completed = bool(website and (website.get('website_url') or website.get('writing_style')))
                    logger.info(f"Step 2 completed: {step_completed}")
                elif step_num == 3:  # Research Preferences
                    research = db_service.get_research_preferences(user_id, db)
                    logger.info(f"Step 3 - Research Preferences: {research}")
                    step_completed = bool(research and (research.get('research_depth') or research.get('content_types')))
                    logger.info(f"Step 3 completed: {step_completed}")
                elif step_num == 4:  # Persona Generation
                    persona = db_service.get_persona_data(user_id, db)
                    logger.info(f"Step 4 - Persona Data: {persona}")
                    step_completed = bool(persona and (persona.get('corePersona') or persona.get('platformPersonas')))
                    logger.info(f"Step 4 completed: {step_completed}")
                elif step_num == 5:  # Integrations
                    # For now, consider this always completed if we reach this point
                    step_completed = True
                    logger.info(f"Step 5 completed: {step_completed}")
                
                if not step_completed:
                    missing_steps.append(f"Step {step_num}")
            
            logger.info(f"Missing steps: {missing_steps}")
            return missing_steps
            
        except Exception as e:
            logger.error(f"Error validating required steps: {e}")
            return ["Validation error"]
    
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

        logger.info(f"OnboardingCompletionService: Validating steps for user {user_id}")
        logger.info(f"OnboardingCompletionService: Current step: {progress.current_step}")
        logger.info(f"OnboardingCompletionService: Required steps: {self.required_steps}")

        for step_num in self.required_steps:
            step = progress.get_step_data(step_num)
            logger.info(f"OnboardingCompletionService: Step {step_num} - status: {step.status if step else 'None'}")
            if step and step.status in [StepStatus.COMPLETED, StepStatus.SKIPPED]:
                logger.info(f"OnboardingCompletionService: Step {step_num} already completed/skipped")
                continue

            # DB-aware fallbacks for migration period
            try:
                if db_service:
                    if step_num == 1:
                        # Treat as completed if user has any API key in DB
                        keys = db_service.get_api_keys(user_id, db)
                        if keys and any(v for v in keys.values()):
                            try:
                                progress.mark_step_completed(1, {'source': 'db-fallback'})
                            except Exception:
                                pass
                            continue
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
                    if step_num == 4:
                        # Treat as completed if persona data exists in DB
                        persona = None
                        try:
                            persona = db_service.get_persona_data(user_id, db)
                        except Exception:
                            persona = None
                        if persona and persona.get('corePersona'):
                            try:
                                progress.mark_step_completed(4, {'source': 'db-fallback'})
                            except Exception:
                                pass
                            continue
                    if step_num == 5:
                        # Treat as completed if integrations data exists in DB
                        # For now, we'll consider step 5 completed if the user has reached the final step
                        # This is a simplified approach - in the future, we could check for specific integration data
                        try:
                            # Check if user has completed previous steps and is on final step
                            if progress.current_step >= 6:  # FinalStep is step 6
                                progress.mark_step_completed(5, {'source': 'final-step-fallback'})
                                continue
                        except Exception:
                            pass
            except Exception:
                # If DB check fails, fall back to progress status only
                pass

            if step:
                missing_steps.append(step.title)
        
        return missing_steps
    
    def _validate_api_keys(self, user_id: str):
        """Validate that API keys are configured for the current user (DB-only)."""
        try:
            db = next(get_db())
            db_service = OnboardingDatabaseService()
            user_keys = db_service.get_api_keys(user_id, db)
            if not user_keys or not any(v for v in user_keys.values()):
                raise HTTPException(
                    status_code=400,
                    detail="Cannot complete onboarding. At least one AI provider API key must be configured in your account."
                )
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Cannot complete onboarding. API key validation failed."
            )
    
    async def _generate_persona_from_onboarding(self, user_id: str) -> bool:
        """Generate writing persona from onboarding data."""
        try:
            persona_service = PersonaAnalysisService()
            
            # If a persona already exists for this user, skip regeneration
            try:
                existing = persona_service.get_user_personas(int(user_id))
                if existing and len(existing) > 0:
                    logger.info("Persona already exists for user %s; skipping regeneration during completion", user_id)
                    return False
            except Exception:
                # Non-fatal; proceed to attempt generation
                pass

            # Generate persona for this user
            persona_result = persona_service.generate_persona_from_onboarding(int(user_id))
            
            if "error" not in persona_result:
                logger.info(f"✅ Writing persona generated during onboarding completion: {persona_result.get('persona_id')}")
                return True
            else:
                logger.warning(f"⚠️ Persona generation failed during onboarding: {persona_result['error']}")
                return False
        except Exception as e:
            logger.warning(f"⚠️ Non-critical error generating persona during onboarding: {str(e)}")
            return False
