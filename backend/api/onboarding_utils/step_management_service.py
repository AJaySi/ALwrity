"""
Step Management Service
Handles onboarding step operations and progress tracking.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import HTTPException
from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from api.content_planning.services.content_strategy.onboarding import OnboardingDataIntegrationService
from services.database import get_db
from models.onboarding import OnboardingSession, APIKey, WebsiteAnalysis, ResearchPreferences, PersonaData, CompetitorAnalysis

class StepManagementService:
    """Service for handling onboarding step management."""
    
    def __init__(self):
        self.integration_service = OnboardingDataIntegrationService()

    def _get_or_create_session(self, user_id: str, db: Session) -> OnboardingSession:
        """Get or create onboarding session."""
        session = db.query(OnboardingSession).filter(
            OnboardingSession.user_id == user_id
        ).first()
        
        if not session:
            session = OnboardingSession(
                user_id=user_id,
                current_step=1,
                progress=0.0,
                started_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(session)
            db.commit()
            db.refresh(session)
            
        return session

    def _save_api_key(self, user_id: str, provider: str, api_key: str, db: Session) -> bool:
        """Save API key directly to database."""
        try:
            session = self._get_or_create_session(user_id, db)
            
            existing_key = db.query(APIKey).filter(
                APIKey.session_id == session.id,
                APIKey.provider == provider
            ).first()
            
            if existing_key:
                existing_key.key = api_key
                existing_key.updated_at = datetime.utcnow()
            else:
                new_key = APIKey(
                    session_id=session.id,
                    provider=provider,
                    key=api_key
                )
                db.add(new_key)
            
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving API key for user {user_id}: {e}")
            db.rollback()
            raise e

    def _save_website_analysis(self, user_id: str, analysis_data: Dict[str, Any], db: Session) -> bool:
        """Save website analysis directly to database."""
        try:
            session = self._get_or_create_session(user_id, db)
            
            # Normalize payload
            incoming = analysis_data or {}
            nested = incoming.get('analysis') if isinstance(incoming.get('analysis'), dict) else None
            
            # Extract extra fields
            brand_analysis = (nested or incoming).get('brand_analysis')
            content_strategy_insights = (nested or incoming).get('content_strategy_insights')
            meta_info = (nested or incoming).get('meta_info')
            
            # Fix: Check both nested and incoming for social_media_presence
            social_media_presence = (nested or {}).get('social_media_presence') or incoming.get('social_media_presence')
            
            seo_audit = (nested or incoming).get('seo_audit')
            style_patterns = (nested or incoming).get('style_patterns')
            style_guidelines = (nested or incoming).get('guidelines')
            sitemap_analysis = (nested or incoming).get('sitemap_analysis')
            
            # Prepare crawl_result
            crawl_result = incoming.get('crawl_result') or {}
            if not isinstance(crawl_result, dict):
                crawl_result = {"raw": crawl_result}
                
            # Meta info still goes to crawl_result as we didn't add a column for it
            if meta_info:
                crawl_result['meta_info'] = meta_info
                
            # Store sitemap_analysis in crawl_result as we don't have a dedicated column yet
            if sitemap_analysis:
                crawl_result['sitemap_analysis'] = sitemap_analysis

            normalized = {
                'website_url': incoming.get('website') or incoming.get('website_url') or '',
                'writing_style': (nested or incoming).get('writing_style'),
                'content_characteristics': (nested or incoming).get('content_characteristics'),
                'target_audience': (nested or incoming).get('target_audience'),
                'content_type': (nested or incoming).get('content_type'),
                'recommended_settings': (nested or incoming).get('recommended_settings'),
                'brand_analysis': brand_analysis,
                'content_strategy_insights': content_strategy_insights,
                'social_media_presence': social_media_presence,
                'crawl_result': crawl_result,
                'seo_audit': seo_audit,
                'style_patterns': style_patterns,
                'style_guidelines': style_guidelines
            }
            
            # Filter only valid columns to prevent TypeError
            valid_columns = [c.name for c in WebsiteAnalysis.__table__.columns if c.name not in ['id', 'session_id', 'created_at', 'updated_at']]
            filtered_data = {k: v for k, v in normalized.items() if k in valid_columns and v is not None}

            existing_analysis = db.query(WebsiteAnalysis).filter(
                WebsiteAnalysis.session_id == session.id
            ).first()
            
            if existing_analysis:
                for key, value in filtered_data.items():
                    setattr(existing_analysis, key, value)
                existing_analysis.updated_at = datetime.utcnow()
            else:
                new_analysis = WebsiteAnalysis(
                    session_id=session.id,
                    **filtered_data
                )
                db.add(new_analysis)
            
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving website analysis for user {user_id}: {e}")
            db.rollback()
            raise e

    def _save_research_preferences(self, user_id: str, research_data: Dict[str, Any], db: Session) -> bool:
        """Save research preferences directly to database."""
        try:
            session = self._get_or_create_session(user_id, db)
            
            # Add defaults for required fields if missing to prevent 500 errors
            # The frontend Step 3 (Competitor Analysis) might not send these
            if 'research_depth' not in research_data:
                research_data['research_depth'] = 'Comprehensive'
            if 'content_types' not in research_data:
                research_data['content_types'] = ["Blog Posts", "Social Media", "Newsletters"]
            if 'auto_research' not in research_data:
                research_data['auto_research'] = True
            if 'factual_content' not in research_data:
                research_data['factual_content'] = True
            
            existing_prefs = db.query(ResearchPreferences).filter(
                ResearchPreferences.session_id == session.id
            ).first()
            
            if existing_prefs:
                # Fix for SQLite DateTime issue: Ensure created_at is a datetime object
                if hasattr(existing_prefs, 'created_at') and isinstance(existing_prefs.created_at, str):
                    try:
                        existing_prefs.created_at = datetime.fromisoformat(existing_prefs.created_at)
                    except (ValueError, TypeError):
                        pass

                for key, value in research_data.items():
                    # Skip metadata fields and id
                    if key in ['id', 'session_id', 'created_at', 'updated_at']:
                        continue
                        
                    if hasattr(existing_prefs, key) and value is not None:
                        setattr(existing_prefs, key, value)
                existing_prefs.updated_at = datetime.utcnow()
            else:
                # Filter valid columns only to avoid errors
                valid_columns = [c.name for c in ResearchPreferences.__table__.columns if c.name not in ['id', 'session_id', 'created_at', 'updated_at']]
                filtered_data = {k: v for k, v in research_data.items() if k in valid_columns}
                
                new_prefs = ResearchPreferences(
                    session_id=session.id,
                    **filtered_data
                )
                db.add(new_prefs)
            
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving research preferences for user {user_id}: {e}")
            db.rollback()
            raise e

    def _save_competitor_analysis(self, user_id: str, competitors: List[Dict[str, Any]], industry_context: Optional[str], db: Session) -> bool:
        """Save competitor analysis results to database."""
        try:
            session = self._get_or_create_session(user_id, db)
            
            logger.info(f"🔍 COMPETITOR SAVE: Starting to save {len(competitors)} competitors for session {session.id}")
            
            saved_count = 0
            failed_count = 0
            
            for idx, competitor in enumerate(competitors):
                try:
                    if not competitor or not isinstance(competitor, dict):
                        logger.warning(f"  ⚠️ Skipping invalid competitor entry at index {idx}: {competitor}")
                        continue

                    # Use full URL (Text column supports it) and clean it
                    raw_url = competitor.get("url", "")
                    competitor_url = raw_url.strip().strip('`').strip() if raw_url else ""

                    # Prepare analysis data
                    analysis_data = {
                        "title": competitor.get("title", ""),
                        "summary": competitor.get("summary", ""),
                        "relevance_score": competitor.get("relevance_score", 0.5),
                        "highlights": competitor.get("highlights", []),
                        "subpages": competitor.get("subpages", []),
                        "favicon": competitor.get("favicon"),
                        "image": competitor.get("image"),
                        "published_date": competitor.get("published_date"),
                        "author": competitor.get("author"),
                        "competitive_analysis": competitor.get("competitive_analysis") or competitor.get("competitive_insights", {}),
                        "content_insights": competitor.get("content_insights", {}),
                        "industry_context": industry_context,
                        "completed_at": datetime.utcnow().isoformat()
                    }
                    
                    # Check if competitor already exists for this session
                    existing_competitor = db.query(CompetitorAnalysis).filter(
                        CompetitorAnalysis.session_id == session.id,
                        CompetitorAnalysis.competitor_url == competitor.get("url", "")
                    ).first()

                    has_details = bool(analysis_data.get("summary") or analysis_data.get("highlights"))
                    detail_msg = "with rich details" if has_details else "basic info only"

                    if existing_competitor:
                        existing_competitor.analysis_data = analysis_data
                        existing_competitor.updated_at = datetime.utcnow()
                        logger.info(f"  Updated existing competitor {idx + 1} ({detail_msg})")
                    else:
                        competitor_record = CompetitorAnalysis(
                            session_id=session.id,
                            competitor_url=competitor_url,
                            competitor_domain=competitor.get("domain", ""),
                            analysis_data=analysis_data,
                            status="completed"
                        )
                        db.add(competitor_record)
                        logger.info(f"  Added new competitor {idx + 1} ({detail_msg})")
                    
                    saved_count += 1
                    
                except Exception as e:
                    failed_count += 1
                    logger.error(f"  ❌ Failed to save competitor {idx + 1}: {str(e)}")
            
            db.commit()
            logger.info(f"✅ Saved {saved_count} competitors ({failed_count} failed)")
            return True
        except Exception as e:
            logger.error(f"Error saving competitor analysis for user {user_id}: {e}")
            db.rollback()
            raise e


    def _save_persona_data(self, user_id: str, persona_data: Dict[str, Any], db: Session) -> bool:
        """Save persona data directly to database."""
        try:
            session = self._get_or_create_session(user_id, db)
            
            existing = db.query(PersonaData).filter(
                PersonaData.session_id == session.id
            ).first()
            
            if existing:
                existing.core_persona = persona_data.get('corePersona')
                existing.platform_personas = persona_data.get('platformPersonas')
                existing.quality_metrics = persona_data.get('qualityMetrics')
                existing.selected_platforms = persona_data.get('selectedPlatforms', [])
                existing.updated_at = datetime.utcnow()
            else:
                persona = PersonaData(
                    session_id=session.id,
                    core_persona=persona_data.get('corePersona'),
                    platform_personas=persona_data.get('platformPersonas'),
                    quality_metrics=persona_data.get('qualityMetrics'),
                    selected_platforms=persona_data.get('selectedPlatforms', [])
                )
                db.add(persona)
            
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving persona data for user {user_id}: {e}")
            db.rollback()
            raise e
    
    async def get_onboarding_status(self, current_user: Dict[str, Any]) -> Dict[str, Any]:
        """Get the current onboarding status (per user)."""
        try:
            from services.onboarding.progress_service import OnboardingProgressService
            user_id = str(current_user.get('id'))
            status = OnboardingProgressService().get_onboarding_status(user_id)
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
            from services.onboarding.progress_service import OnboardingProgressService
            user_id = str(current_user.get('id'))
            progress_service = OnboardingProgressService()
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
            db = next(get_db(current_user))
            
            # Use SSOT for reading step data
            integrated_data = self.integration_service.get_integrated_data_sync(user_id, db)

            if step_number == 2:
                website = integrated_data.get('website_analysis', {})
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
                research = integrated_data.get('research_preferences', {})
                competitors = integrated_data.get('competitor_analysis', [])
                website = integrated_data.get('website_analysis', {})
                social_media = website.get('social_media_presence') or website.get('social_media_accounts', {})
                
                # Merge competitors into the data
                step_data = research.copy() if research else {}
                step_data['competitors'] = competitors
                step_data['social_media_accounts'] = social_media
                
                return {
                    "step_number": 3,
                    "title": "Research",
                    "description": "Discover competitors",
                    "status": 'completed' if (research.get('research_depth') or research.get('content_types') or competitors) else 'pending',
                    "completed_at": None,
                    "data": step_data,
                    "validation_errors": []
                }
            if step_number == 4:
                persona = integrated_data.get('persona_data', {})
                return {
                    "step_number": 4,
                    "title": "Personalization",
                    "description": "Customize your experience",
                    "status": 'completed' if (persona.get('corePersona') or persona.get('platformPersonas')) else 'pending',
                    "completed_at": None,
                    "data": persona,
                    "validation_errors": []
                }

            from services.onboarding.progress_service import OnboardingProgressService
            status = OnboardingProgressService().get_onboarding_status(user_id)
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

            db = next(get_db(current_user))
            
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
                                saved = self._save_api_key(user_id, provider, key, db)
                                if saved:
                                    logger.info(f"✅ Saved API key for provider {provider}")
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
                if website_data:
                    try:
                        saved = self._save_website_analysis(user_id, website_data, db)
                        if saved:
                            logger.info(f"✅ Saved website analysis for user {user_id}")
                            
                            # Trigger Advertools persona augmentation (Phase 1)
                            try:
                                from services.scheduler import get_scheduler
                                
                                website_url = website_data.get('website') or website_data.get('website_url')
                                if website_url:
                                    scheduler = get_scheduler()
                                    # Schedule content audit for persona augmentation
                                    scheduler.schedule_one_time_task(
                                        func=scheduler.execute_task_by_type,
                                        run_date=datetime.utcnow() + timedelta(seconds=10), # Start in 10s
                                        job_id=f"advertools_persona_augmentation_{user_id}",
                                        kwargs={
                                            "task_type": "advertools_intelligence",
                                            "user_id": user_id,
                                            "payload": {
                                                "type": "content_audit",
                                                "website_url": website_url
                                            }
                                        }
                                    )
                                    logger.info(f"🚀 Triggered Advertools persona augmentation for {website_url}")
                            except Exception as sched_err:
                                logger.error(f"Failed to trigger Advertools augmentation: {sched_err}")
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
                    try:
                        saved = self._save_research_preferences(user_id, research_data, db)
                        if saved:
                            logger.info(f"✅ Saved research preferences for user {user_id}")
                            
                        # Also save competitors if present
                        competitors = research_data.get('competitors')
                        if competitors:
                            industry_context = research_data.get('industryContext') or research_data.get('industry_context')
                            logger.info(f"🔍 Step 3: Found {len(competitors)} competitors to save")
                            self._save_competitor_analysis(user_id, competitors, industry_context, db)
                            
                        # Save social media presence if available (Update WebsiteAnalysis)
                        social_media = research_data.get('social_media_accounts')
                        if social_media:
                            logger.info(f"🔍 Step 3: Found social media accounts to save")
                            try:
                                session = self._get_or_create_session(user_id, db)
                                existing_analysis = db.query(WebsiteAnalysis).filter(
                                    WebsiteAnalysis.session_id == session.id
                                ).first()
                                if existing_analysis:
                                    existing_analysis.social_media_presence = social_media
                                    existing_analysis.updated_at = datetime.utcnow()
                                    db.commit()
                                    logger.info(f"✅ Updated social media presence for user {user_id}")
                                else:
                                    logger.warning(f"⚠️ Could not save social media: WebsiteAnalysis not found for user {user_id}")
                            except Exception as e:
                                logger.error(f"❌ Failed to save social media presence: {str(e)}")
                                # Don't block completion for this, as it's secondary data
                    
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
                        saved = self._save_persona_data(user_id, persona_data, db)
                        if saved:
                            logger.info(f"✅ Saved persona data for user {user_id}")
                    except Exception as e:
                        logger.error(f"❌ BLOCKING ERROR: Failed to save persona data: {str(e)}")
                        raise HTTPException(
                            status_code=500,
                            detail="Failed to save persona data. Onboarding cannot proceed until this is resolved."
                        ) from e

            # Persist current step and progress in DB
            from services.onboarding.progress_service import OnboardingProgressService
            progress_service = OnboardingProgressService()
            progress_service.update_step(user_id, step_number)
            try:
                progress_pct = min(100.0, round((step_number / 6) * 100))
                progress_service.update_progress(user_id, float(progress_pct))
            except Exception as e:
                logger.warning(f"Failed to update progress: {e}")

            # Log save errors but don't block step completion (non-blocking)
            if save_errors:
                logger.warning(f"⚠️ Step {step_number} completed but some data save operations failed: {save_errors}")
            
            # Refresh SSOT (Canonical Profile) - non-blocking try/except inside method
            if not save_errors:
                await self.integration_service.refresh_integrated_data(user_id, db)
            
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
            from services.onboarding.api_key_manager import get_onboarding_progress_for_user
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
