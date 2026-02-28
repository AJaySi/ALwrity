"""
Onboarding Completion Service
Handles the complex logic for completing the onboarding process.
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import os
from fastapi import HTTPException
from loguru import logger

from api.content_planning.services.content_strategy.onboarding import OnboardingDataIntegrationService
from services.database import get_session_for_user
from services.persona_analysis_service import PersonaAnalysisService
from services.research.research_persona_scheduler import schedule_research_persona_generation
from services.persona.facebook.facebook_persona_scheduler import schedule_facebook_persona_generation

class OnboardingCompletionService:
    """Service for handling onboarding completion logic."""
    
    def __init__(self):
        # Pre-requisite steps; step 6 is the finalization itself
        self.required_steps = [1, 2, 3, 4, 5]
    
    async def complete_onboarding(self, current_user: Dict[str, Any]) -> Dict[str, Any]:
        """Complete the onboarding process with full validation."""
        try:
            from services.onboarding.progress_service import OnboardingProgressService
            user_id = str(current_user.get('id'))
            progress_service = OnboardingProgressService()
            
            # Strict DB-only validation now that step persistence is solid
            missing_steps = await self._validate_required_steps_database(user_id)
            if missing_steps:
                missing_steps_str = ", ".join(missing_steps)
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot complete onboarding. The following steps must be completed first: {missing_steps_str}"
                )

            # Require API keys in DB for completion
            await self._validate_api_keys(user_id)
            
            # Generate writing persona from onboarding data only if not already present
            persona_generated = await self._generate_persona_from_onboarding(user_id)
            
            # Complete the onboarding process in database
            success = progress_service.complete_onboarding(user_id)
            if not success:
                raise HTTPException(status_code=500, detail="Failed to mark onboarding as complete")
            
            # Schedule research persona generation 20 minutes after onboarding completion
            try:
                schedule_research_persona_generation(user_id, delay_minutes=20)
                logger.info(f"Scheduled research persona generation for user {user_id} (20 minutes after onboarding)")
            except Exception as e:
                # Non-critical: log but don't fail onboarding completion
                logger.warning(f"Failed to schedule research persona generation for user {user_id}: {e}")
            
            # Schedule Facebook persona generation 20 minutes after onboarding completion
            try:
                schedule_facebook_persona_generation(user_id, delay_minutes=20)
                logger.info(f"Scheduled Facebook persona generation for user {user_id} (20 minutes after onboarding)")
            except Exception as e:
                # Non-critical: log but don't fail onboarding completion
                logger.warning(f"Failed to schedule Facebook persona generation for user {user_id}: {e}")
            
            # Create OAuth token monitoring tasks for connected platforms
            try:
                from services.progressive_setup_service import ProgressiveSetupService
                
                db = get_session_for_user(user_id)
                try:
                    # Initialize user environment (create workspace, setup features)
                    try:
                        setup_service = ProgressiveSetupService(db)
                        setup_service.initialize_user_environment(user_id)
                        logger.info(f"Initialized user environment for {user_id} on onboarding completion")
                    except Exception as e:
                        logger.warning(f"Failed to initialize user environment for {user_id}: {e}")

                    monitoring_tasks = create_oauth_monitoring_tasks(user_id, db)
                    logger.info(
                        f"Created {len(monitoring_tasks)} OAuth token monitoring tasks for user {user_id} "
                        f"on onboarding completion"
                    )
                finally:
                    db.close()
            except Exception as e:
                # Non-critical: log but don't fail onboarding completion
                logger.warning(f"Failed to create OAuth token monitoring tasks for user {user_id}: {e}")
            
            # Schedule website analysis task creation 5 minutes after onboarding completion
            try:
                from services.website_analysis_monitoring_service import schedule_website_analysis_task_creation
                schedule_website_analysis_task_creation(user_id=user_id, delay_minutes=5)
                logger.info(
                    f"Scheduled website analysis task creation for user {user_id} "
                    f"(5 minutes after onboarding completion)"
                )
            except Exception as e:
                logger.warning(f"Failed to schedule website analysis task creation for user {user_id}: {e}")



            # Schedule onboarding full-site SEO audit (non-blocking) ~10 minutes after completion
            try:
                from services.database import SessionLocal
                from models.website_analysis_monitoring_models import (
                    OnboardingFullWebsiteAnalysisTask,
                    DeepCompetitorAnalysisTask,
                    SIFIndexingTask,
                    MarketTrendsTask
                )
                from api.content_planning.services.content_strategy.onboarding import OnboardingDataIntegrationService

                db = SessionLocal()
                try:
                    integration_service = OnboardingDataIntegrationService()
                    integrated_data = integration_service.get_integrated_data_sync(user_id, db)
                    website_analysis = integrated_data.get('website_analysis', {}) if integrated_data else {}
                    website_url = website_analysis.get('website_url')

                    if not website_url:
                        try:
                            from services.website_analysis_monitoring_service import clerk_user_id_to_int
                            from models.onboarding import WebsiteAnalysis
                            session_id_int = clerk_user_id_to_int(user_id)
                            analysis = db.query(WebsiteAnalysis).filter(
                                WebsiteAnalysis.session_id == session_id_int
                            ).order_by(WebsiteAnalysis.created_at.desc()).first()
                            if analysis and analysis.website_url:
                                website_url = analysis.website_url
                        except Exception:
                            website_url = None

                    if website_url:
                        # 1. Schedule Full Site SEO Audit
                        next_execution = datetime.utcnow() + timedelta(minutes=5)
                        existing = db.query(OnboardingFullWebsiteAnalysisTask).filter(
                            OnboardingFullWebsiteAnalysisTask.user_id == user_id,
                            OnboardingFullWebsiteAnalysisTask.website_url == website_url
                        ).first()

                        payload = {
                            'website_url': website_url,
                            'max_urls': 500,
                            'created_from': 'onboarding_completion'
                        }

                        if existing:
                            existing.status = 'active'
                            existing.next_execution = next_execution
                            existing.payload = payload
                            db.add(existing)
                        else:
                            db.add(OnboardingFullWebsiteAnalysisTask(
                                user_id=user_id,
                                website_url=website_url,
                                status='active',
                                next_execution=next_execution,
                                payload=payload
                            ))

                        # 2. Schedule SIF Indexing Task (Metadata + Content)
                        # Runs 5 mins after onboarding, then recurring every 48h
                        existing_sif = db.query(SIFIndexingTask).filter(
                            SIFIndexingTask.user_id == user_id,
                            SIFIndexingTask.website_url == website_url
                        ).first()
                        
                        payload_sif = {
                            'website_url': website_url,
                            'mode': 'initial_indexing',
                            'created_from': 'onboarding_completion'
                        }
                        
                        if existing_sif:
                            existing_sif.status = 'active'
                            existing_sif.next_execution = next_execution
                            existing_sif.frequency_hours = 48
                            existing_sif.payload = payload_sif
                            db.add(existing_sif)
                        else:
                            db.add(SIFIndexingTask(
                                user_id=user_id,
                                website_url=website_url,
                                status='active',
                                next_execution=next_execution,
                                frequency_hours=48,
                                payload=payload_sif
                            ))
                        
                        logger.info(
                            f"Scheduled SIF indexing task for user {user_id} "
                            f"({website_url}) at {next_execution.isoformat()}"
                        )

                        # 3. Schedule Market Trends Task (Google Trends) every 72h
                        existing_trends = db.query(MarketTrendsTask).filter(
                            MarketTrendsTask.user_id == user_id,
                            MarketTrendsTask.website_url == website_url
                        ).first()

                        payload_trends = {
                            "website_url": website_url,
                            "geo": "US",
                            "timeframe": "today 12-m",
                            "created_from": "onboarding_completion"
                        }

                        if existing_trends:
                            existing_trends.status = "active"
                            existing_trends.next_execution = next_execution
                            existing_trends.frequency_hours = 72
                            existing_trends.payload = payload_trends
                            db.add(existing_trends)
                        else:
                            db.add(MarketTrendsTask(
                                user_id=user_id,
                                website_url=website_url,
                                status="active",
                                next_execution=next_execution,
                                frequency_hours=72,
                                payload=payload_trends
                            ))

                        db.commit()
                        logger.info(
                            f"Scheduled onboarding full-site SEO audit for user {user_id} "
                            f"({website_url}) at {next_execution.isoformat()}"
                        )

                        try:
                            research_prefs = integrated_data.get("research_preferences", {}) if isinstance(integrated_data, dict) else {}
                            competitors = research_prefs.get("competitors") if isinstance(research_prefs, dict) else None

                            if isinstance(competitors, list) and len(competitors) > 0:
                                existing_deep = db.query(DeepCompetitorAnalysisTask).filter(
                                    DeepCompetitorAnalysisTask.user_id == user_id,
                                    DeepCompetitorAnalysisTask.website_url == website_url
                                ).first()

                                payload_deep = {
                                    "website_url": website_url,
                                    "competitors": competitors,
                                    "max_competitors": 25,
                                    "crawl_concurrency": 4,
                                    "mode": "strategic_insights",  # Enable recurring weekly strategic insights
                                    "baseline_updated_at": website_analysis.get("updated_at") if isinstance(website_analysis, dict) else None,
                                    "created_from": "onboarding_completion"
                                }

                                if existing_deep:
                                    existing_deep.status = "active"
                                    existing_deep.next_execution = next_execution
                                    existing_deep.payload = payload_deep
                                    db.add(existing_deep)
                                else:
                                    db.add(DeepCompetitorAnalysisTask(
                                        user_id=user_id,
                                        website_url=website_url,
                                        status="active",
                                        next_execution=next_execution,
                                        payload=payload_deep
                                    ))

                                db.commit()
                                logger.info(
                                    f"Scheduled deep competitor analysis for user {user_id} "
                                    f"({website_url}) at {next_execution.isoformat()} with {len(competitors)} competitors"
                                )
                            else:
                                logger.warning(
                                    f"Deep competitor analysis not scheduled for user {user_id}: "
                                    f"no Step 3 competitors available"
                                )
                        except Exception as e:
                            logger.warning(f"Failed to schedule deep competitor analysis for user {user_id}: {e}")
                    else:
                        logger.warning(
                            f"Could not schedule onboarding full-site SEO audit for user {user_id}: "
                            f"website_url missing"
                        )
                finally:
                    db.close()
            except Exception as e:
                logger.warning(f"Failed to schedule onboarding full-site SEO audit for user {user_id}: {e}")
            
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
    
    async def _validate_required_steps_database(self, user_id: str) -> List[str]:
        """Validate that all required steps are completed using SSOT integration service."""
        missing_steps = []
        try:
            db = get_session_for_user(user_id)
            integration_service = OnboardingDataIntegrationService()
            
            logger.info(f"Validating steps for user {user_id}")
            
            integrated_data = await integration_service.process_onboarding_data(user_id, db)
            db.close()

            from services.onboarding.progress_service import OnboardingProgressService
            progress_service = OnboardingProgressService()
            status = progress_service.get_onboarding_status(user_id)
            current_step = status.get("current_step", 1)
            
            for step_num in self.required_steps:
                step_completed = False
                
                if step_num == 1:
                    api_keys_data = integrated_data.get('api_keys_data', {})
                    logger.info(f"Step 1 - API Keys: {api_keys_data}")
                    step_completed = bool(
                        api_keys_data.get('openai_api_key') or 
                        api_keys_data.get('anthropic_api_key') or 
                        api_keys_data.get('google_api_key')
                    )
                    if not step_completed:
                        has_global_providers = bool(
                            os.getenv("EXA_API_KEY") or
                            os.getenv("GEMINI_API_KEY") or
                            os.getenv("OPENAI_API_KEY") or
                            os.getenv("ANTHROPIC_API_KEY") or
                            os.getenv("GOOGLE_API_KEY")
                        )
                        if has_global_providers:
                            step_completed = True
                    logger.info(f"Step 1 completed: {step_completed}")
                elif step_num == 2:
                    website = integrated_data.get('website_analysis', {})
                    logger.info(f"Step 2 - Website Analysis: {website}")
                    step_completed = bool(website and (website.get('website_url') or website.get('writing_style')))
                    logger.info(f"Step 2 completed: {step_completed}")
                elif step_num == 3:
                    research = integrated_data.get('research_preferences', {})
                    logger.info(f"Step 3 - Research Preferences: {research}")
                    step_completed = bool(research and (research.get('research_depth') or research.get('content_types')))
                    logger.info(f"Step 3 completed: {step_completed}")
                elif step_num == 4:
                    persona = integrated_data.get('persona_data', {})
                    logger.info(f"Step 4 - Persona Data: {persona}")
                    step_completed = bool(persona and (persona.get('corePersona') or persona.get('platformPersonas')))
                    if not step_completed:
                        website = integrated_data.get('website_analysis', {})
                        research = integrated_data.get('research_preferences', {})
                        basic_ready = bool(
                            website and (website.get('website_url') or website.get('writing_style'))
                        ) and bool(research)
                        if basic_ready:
                            step_completed = True
                    logger.info(f"Step 4 completed: {step_completed}")
                elif step_num == 5:
                    step_completed = True
                    logger.info(f"Step 5 completed: {step_completed}")

                if not step_completed and current_step >= step_num:
                    step_completed = True
                    logger.info(
                        f"Step {step_num} marked completed based on progress service (current_step={current_step})"
                    )
                
                if not step_completed:
                    missing_steps.append(f"Step {step_num}")
            
            logger.info(f"Missing steps: {missing_steps}")
            return missing_steps
            
        except Exception as e:
            logger.error(f"Error validating required steps: {e}")
            return ["Validation error"]
    
    async def _validate_api_keys(self, user_id: str):
        """Validate that API keys are configured for the current user (SSOT or environment)."""
        try:
            db = get_session_for_user(user_id)
            try:
                integration_service = OnboardingDataIntegrationService()
                integrated_data = await integration_service.process_onboarding_data(user_id, db)
            finally:
                db.close()
            
            api_keys_data = integrated_data.get('api_keys_data', {}) if integrated_data else {}
            
            has_user_keys = bool(
                api_keys_data.get('openai_api_key') or 
                api_keys_data.get('anthropic_api_key') or 
                api_keys_data.get('google_api_key') or
                api_keys_data.get('exa_api_key') or
                api_keys_data.get('gemini_api_key')
            )

            has_env_keys = bool(
                os.getenv("OPENAI_API_KEY") or
                os.getenv("ANTHROPIC_API_KEY") or
                os.getenv("GOOGLE_API_KEY") or
                os.getenv("EXA_API_KEY") or
                os.getenv("GEMINI_API_KEY")
            )

            has_keys = has_user_keys or has_env_keys
            
            if not has_keys:
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
            
            try:
                existing = persona_service.get_user_personas(user_id)
                if existing and len(existing) > 0:
                    logger.info("Persona already exists for user %s; skipping regeneration during completion", user_id)
                    return False
            except Exception:
                # Non-fatal; proceed to attempt generation
                pass

            persona_result = persona_service.generate_persona_from_onboarding(user_id)
            
            if "error" not in persona_result:
                logger.info(f"✅ Writing persona generated during onboarding completion: {persona_result.get('persona_id')}")
                return True
            else:
                logger.warning(f"⚠️ Persona generation failed during onboarding: {persona_result['error']}")
                return False
        except Exception as e:
            logger.warning(f"⚠️ Non-critical error generating persona during onboarding: {str(e)}")
            return False
