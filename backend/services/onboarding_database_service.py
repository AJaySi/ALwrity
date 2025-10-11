"""
Onboarding Database Service
Provides database-backed storage for onboarding progress with user isolation.
This replaces the JSON file-based storage with proper database persistence.
"""

from typing import Dict, Any, Optional, List
import os
import json
from datetime import datetime
from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

from models.onboarding import OnboardingSession, APIKey, WebsiteAnalysis, ResearchPreferences, PersonaData
from services.database import get_db


class OnboardingDatabaseService:
    """Database service for onboarding with user isolation."""
    
    def __init__(self, db: Session = None):
        """Initialize with optional database session."""
        self.db = db
        # Cache for schema feature detection
        self._brand_cols_checked: bool = False
        self._brand_cols_available: bool = False

    # --- Feature flags and schema detection helpers ---
    def _brand_feature_enabled(self) -> bool:
        """Check if writing brand-related columns is enabled via env flag."""
        return os.getenv('ENABLE_WEBSITE_BRAND_COLUMNS', 'true').lower() in {'1', 'true', 'yes', 'on'}

    def _ensure_brand_column_detection(self, session_db: Session) -> None:
        """Detect at runtime whether brand columns exist and cache the result."""
        if self._brand_cols_checked:
            return
        try:
            # This works across SQLite/Postgres; LIMIT 0 avoids scanning
            session_db.execute(text('SELECT brand_analysis, content_strategy_insights FROM website_analyses LIMIT 0'))
            self._brand_cols_available = True
        except Exception:
            self._brand_cols_available = False
        finally:
            self._brand_cols_checked = True

    def _maybe_update_brand_columns(self, session_db: Session, session_id: int, brand_analysis: Any, content_strategy_insights: Any) -> None:
        """Safely update brand columns using raw SQL if feature enabled and columns exist."""
        if not self._brand_feature_enabled():
            return
        self._ensure_brand_column_detection(session_db)
        if not self._brand_cols_available:
            return
        try:
            session_db.execute(
                text('''
                    UPDATE website_analyses
                    SET brand_analysis = :brand_analysis,
                        content_strategy_insights = :content_strategy_insights
                    WHERE session_id = :session_id
                '''),
                {
                    'brand_analysis': json.dumps(brand_analysis) if brand_analysis is not None else None,
                    'content_strategy_insights': json.dumps(content_strategy_insights) if content_strategy_insights is not None else None,
                    'session_id': session_id,
                }
            )
        except Exception as e:
            logger.warning(f"Skipped updating brand columns (not critical): {e}")

    def _maybe_attach_brand_columns(self, session_db: Session, session_id: int, result: Dict[str, Any]) -> None:
        """Optionally read brand columns and attach to result if available."""
        if not self._brand_feature_enabled():
            return
        self._ensure_brand_column_detection(session_db)
        if not self._brand_cols_available:
            return
        try:
            row = session_db.execute(
                text('''
                    SELECT brand_analysis, content_strategy_insights
                    FROM website_analyses WHERE session_id = :session_id LIMIT 1
                '''),
                {'session_id': session_id}
            ).mappings().first()
            if row:
                brand = row.get('brand_analysis')
                insights = row.get('content_strategy_insights')
                # If stored as TEXT in SQLite, try to parse JSON
                if isinstance(brand, str):
                    try:
                        brand = json.loads(brand)
                    except Exception:
                        pass
                if isinstance(insights, str):
                    try:
                        insights = json.loads(insights)
                    except Exception:
                        pass
                result['brand_analysis'] = brand
                result['content_strategy_insights'] = insights
        except Exception as e:
            logger.warning(f"Skipped reading brand columns (not critical): {e}")
    
    def get_or_create_session(self, user_id: str, db: Session = None) -> OnboardingSession:
        """Get existing onboarding session or create new one for user."""
        session_db = db or self.db
        if not session_db:
            raise ValueError("Database session required")
        
        try:
            # Try to get existing session for this user
            session = session_db.query(OnboardingSession).filter(
                OnboardingSession.user_id == user_id
            ).first()
            
            if session:
                logger.info(f"Found existing onboarding session for user {user_id}")
                return session
            
            # Create new session
            session = OnboardingSession(
                user_id=user_id,
                current_step=1,
                progress=0.0,
                started_at=datetime.now()
            )
            session_db.add(session)
            session_db.commit()
            session_db.refresh(session)
            
            logger.info(f"Created new onboarding session for user {user_id}")
            return session
            
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_or_create_session: {e}")
            session_db.rollback()
            raise
    
    def get_session_by_user(self, user_id: str, db: Session = None) -> Optional[OnboardingSession]:
        """Get onboarding session for user."""
        session_db = db or self.db
        if not session_db:
            raise ValueError("Database session required")
        
        try:
            return session_db.query(OnboardingSession).filter(
                OnboardingSession.user_id == user_id
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting session: {e}")
            return None
    
    def update_step(self, user_id: str, step_number: int, db: Session = None) -> bool:
        """Update current step for user."""
        session_db = db or self.db
        if not session_db:
            raise ValueError("Database session required")
        
        try:
            session = self.get_or_create_session(user_id, session_db)
            session.current_step = step_number
            session.updated_at = datetime.now()
            session_db.commit()
            
            logger.info(f"Updated user {user_id} to step {step_number}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error updating step: {e}")
            session_db.rollback()
            return False
    
    def update_progress(self, user_id: str, progress: float, db: Session = None) -> bool:
        """Update progress percentage for user."""
        session_db = db or self.db
        if not session_db:
            raise ValueError("Database session required")
        
        try:
            session = self.get_or_create_session(user_id, session_db)
            session.progress = progress
            session.updated_at = datetime.now()
            session_db.commit()
            
            logger.info(f"Updated user {user_id} progress to {progress}%")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error updating progress: {e}")
            session_db.rollback()
            return False
    
    def save_api_key(self, user_id: str, provider: str, api_key: str, db: Session = None) -> bool:
        """Save API key for user with isolation."""
        session_db = db or self.db
        if not session_db:
            raise ValueError("Database session required")
        
        try:
            # Get user's onboarding session
            session = self.get_or_create_session(user_id, session_db)
            
            # Check if key already exists for this provider and session
            existing_key = session_db.query(APIKey).filter(
                APIKey.session_id == session.id,
                APIKey.provider == provider
            ).first()
            
            if existing_key:
                # Update existing key
                existing_key.key = api_key
                existing_key.updated_at = datetime.now()
                logger.info(f"Updated {provider} API key for user {user_id}")
            else:
                # Create new key
                new_key = APIKey(
                    session_id=session.id,
                    provider=provider,
                    key=api_key
                )
                session_db.add(new_key)
                logger.info(f"Created new {provider} API key for user {user_id}")
            
            session_db.commit()
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error saving API key: {e}")
            session_db.rollback()
            return False
    
    def get_api_keys(self, user_id: str, db: Session = None) -> Dict[str, str]:
        """Get all API keys for user."""
        session_db = db or self.db
        if not session_db:
            raise ValueError("Database session required")
        
        try:
            session = self.get_session_by_user(user_id, session_db)
            if not session:
                return {}
            
            keys = session_db.query(APIKey).filter(
                APIKey.session_id == session.id
            ).all()
            
            return {key.provider: key.key for key in keys}
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting API keys: {e}")
            return {}
    
    def save_website_analysis(self, user_id: str, analysis_data: Dict[str, Any], db: Session = None) -> bool:
        """Save website analysis for user."""
        session_db = db or self.db
        if not session_db:
            raise ValueError("Database session required")
        
        try:
            session = self.get_or_create_session(user_id, session_db)
            # Normalize payload. Step 2 sometimes sends { website, analysis: {...} }
            # while DB expects flattened fields. Support both shapes.
            incoming = analysis_data or {}
            nested = incoming.get('analysis') if isinstance(incoming.get('analysis'), dict) else None
            normalized = {
                'website_url': incoming.get('website') or incoming.get('website_url') or '',
                'writing_style': (nested or incoming).get('writing_style'),
                'content_characteristics': (nested or incoming).get('content_characteristics'),
                'target_audience': (nested or incoming).get('target_audience'),
                'content_type': (nested or incoming).get('content_type'),
                'recommended_settings': (nested or incoming).get('recommended_settings'),
                'brand_analysis': (nested or incoming).get('brand_analysis'),
                'content_strategy_insights': (nested or incoming).get('content_strategy_insights'),
                'crawl_result': (nested or incoming).get('crawl_result'),
                'style_patterns': (nested or incoming).get('style_patterns'),
                'style_guidelines': (nested or incoming).get('style_guidelines'),
                'status': (nested or incoming).get('status', incoming.get('status', 'completed')),
            }
            
            # Check if analysis already exists
            existing = session_db.query(WebsiteAnalysis).filter(
                WebsiteAnalysis.session_id == session.id
            ).first()
            
            if existing:
                # Update existing
                existing.website_url = normalized.get('website_url', existing.website_url)
                existing.writing_style = normalized.get('writing_style')
                existing.content_characteristics = normalized.get('content_characteristics')
                existing.target_audience = normalized.get('target_audience')
                existing.content_type = normalized.get('content_type')
                existing.recommended_settings = normalized.get('recommended_settings')
                existing.crawl_result = normalized.get('crawl_result')
                existing.style_patterns = normalized.get('style_patterns')
                existing.style_guidelines = normalized.get('style_guidelines')
                existing.status = normalized.get('status', 'completed')
                existing.updated_at = datetime.now()
                logger.info(f"Updated website analysis for user {user_id}")
            else:
                # Create new
                analysis = WebsiteAnalysis(
                    session_id=session.id,
                    website_url=normalized.get('website_url', ''),
                    writing_style=normalized.get('writing_style'),
                    content_characteristics=normalized.get('content_characteristics'),
                    target_audience=normalized.get('target_audience'),
                    content_type=normalized.get('content_type'),
                    recommended_settings=normalized.get('recommended_settings'),
                    crawl_result=normalized.get('crawl_result'),
                    style_patterns=normalized.get('style_patterns'),
                    style_guidelines=normalized.get('style_guidelines'),
                    status=normalized.get('status', 'completed')
                )
                session_db.add(analysis)
                logger.info(f"Created website analysis for user {user_id}")
            
            session_db.commit()

            # Optional brand column update via raw SQL (feature-flagged)
            self._maybe_update_brand_columns(
                session_db=session_db,
                session_id=session.id,
                brand_analysis=normalized.get('brand_analysis'),
                content_strategy_insights=normalized.get('content_strategy_insights')
            )
            session_db.commit()
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error saving website analysis: {e}")
            session_db.rollback()
            return False
    
    def get_website_analysis(self, user_id: str, db: Session = None) -> Optional[Dict[str, Any]]:
        """Get website analysis for user."""
        session_db = db or self.db
        if not session_db:
            raise ValueError("Database session required")
        
        try:
            session = self.get_session_by_user(user_id, session_db)
            if not session:
                return None
            
            analysis = session_db.query(WebsiteAnalysis).filter(
                WebsiteAnalysis.session_id == session.id
            ).first()
            
            result = analysis.to_dict() if analysis else None
            if result:
                # Optionally include brand fields without touching ORM mapping
                self._maybe_attach_brand_columns(session_db, session.id, result)
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting website analysis: {e}")
            return None
    
    def save_research_preferences(self, user_id: str, preferences: Dict[str, Any], db: Session = None) -> bool:
        """Save research preferences for user."""
        session_db = db or self.db
        if not session_db:
            raise ValueError("Database session required")
        
        try:
            session = self.get_or_create_session(user_id, session_db)
            
            # Check if preferences already exist
            existing = session_db.query(ResearchPreferences).filter(
                ResearchPreferences.session_id == session.id
            ).first()
            
            if existing:
                # Update existing
                existing.research_depth = preferences.get('research_depth', existing.research_depth)
                existing.content_types = preferences.get('content_types', existing.content_types)
                existing.auto_research = preferences.get('auto_research', existing.auto_research)
                existing.factual_content = preferences.get('factual_content', existing.factual_content)
                existing.writing_style = preferences.get('writing_style')
                existing.content_characteristics = preferences.get('content_characteristics')
                existing.target_audience = preferences.get('target_audience')
                existing.recommended_settings = preferences.get('recommended_settings')
                existing.updated_at = datetime.now()
                logger.info(f"Updated research preferences for user {user_id}")
            else:
                # Create new
                prefs = ResearchPreferences(
                    session_id=session.id,
                    research_depth=preferences.get('research_depth', 'standard'),
                    content_types=preferences.get('content_types', []),
                    auto_research=preferences.get('auto_research', True),
                    factual_content=preferences.get('factual_content', True),
                    writing_style=preferences.get('writing_style'),
                    content_characteristics=preferences.get('content_characteristics'),
                    target_audience=preferences.get('target_audience'),
                    recommended_settings=preferences.get('recommended_settings')
                )
                session_db.add(prefs)
                logger.info(f"Created research preferences for user {user_id}")
            
            session_db.commit()
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error saving research preferences: {e}")
            session_db.rollback()
            return False
    
    def save_persona_data(self, user_id: str, persona_data: Dict[str, Any], db: Session = None) -> bool:
        """Save persona data for user."""
        session_db = db or self.db
        if not session_db:
            raise ValueError("Database session required")
        
        try:
            session = self.get_or_create_session(user_id, session_db)
            
            # Check if persona data already exists for this user
            existing = session_db.query(PersonaData).filter(
                PersonaData.session_id == session.id
            ).first()
            
            if existing:
                # Update existing persona data
                existing.core_persona = persona_data.get('corePersona')
                existing.platform_personas = persona_data.get('platformPersonas')
                existing.quality_metrics = persona_data.get('qualityMetrics')
                existing.selected_platforms = persona_data.get('selectedPlatforms', [])
                existing.updated_at = datetime.utcnow()
                logger.info(f"Updated persona data for user {user_id}")
            else:
                # Create new persona data record
                persona = PersonaData(
                    session_id=session.id,
                    core_persona=persona_data.get('corePersona'),
                    platform_personas=persona_data.get('platformPersonas'),
                    quality_metrics=persona_data.get('qualityMetrics'),
                    selected_platforms=persona_data.get('selectedPlatforms', [])
                )
                session_db.add(persona)
                logger.info(f"Created persona data for user {user_id}")
            
            session_db.commit()
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error saving persona data: {e}")
            session_db.rollback()
            return False
    
    def get_research_preferences(self, user_id: str, db: Session = None) -> Optional[Dict[str, Any]]:
        """Get research preferences for user."""
        session_db = db or self.db
        if not session_db:
            raise ValueError("Database session required")
        
        try:
            session = self.get_session_by_user(user_id, session_db)
            if not session:
                return None
            
            prefs = session_db.query(ResearchPreferences).filter(
                ResearchPreferences.session_id == session.id
            ).first()
            
            return prefs.to_dict() if prefs else None
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting research preferences: {e}")
            return None
    
    def get_persona_data(self, user_id: str, db: Session = None) -> Optional[Dict[str, Any]]:
        """Get persona data for user."""
        session_db = db or self.db
        if not session_db:
            raise ValueError("Database session required")
        
        try:
            session = self.get_session_by_user(user_id, session_db)
            if not session:
                return None
            
            persona = session_db.query(PersonaData).filter(
                PersonaData.session_id == session.id
            ).first()
            
            if not persona:
                return None
            
            # Return persona data in the expected format
            return {
                'corePersona': persona.core_persona,
                'platformPersonas': persona.platform_personas,
                'qualityMetrics': persona.quality_metrics,
                'selectedPlatforms': persona.selected_platforms
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting persona data: {e}")
            return None
    
    def mark_onboarding_complete(self, user_id: str, db: Session = None) -> bool:
        """Mark onboarding as complete for user."""
        session_db = db or self.db
        if not session_db:
            raise ValueError("Database session required")
        
        try:
            session = self.get_or_create_session(user_id, session_db)
            session.current_step = 6  # Final step
            session.progress = 100.0
            session.updated_at = datetime.now()
            session_db.commit()
            
            logger.info(f"Marked onboarding complete for user {user_id}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Error marking onboarding complete: {e}")
            session_db.rollback()
            return False
    
    def get_onboarding_status(self, user_id: str, db: Session = None) -> Dict[str, Any]:
        """Get comprehensive onboarding status for user."""
        session_db = db or self.db
        if not session_db:
            raise ValueError("Database session required")
        
        try:
            session = self.get_session_by_user(user_id, session_db)
            
            if not session:
                # User hasn't started onboarding yet
                return {
                    "is_completed": False,
                    "current_step": 1,
                    "progress": 0.0,
                    "started_at": None,
                    "updated_at": None
                }
            
            return {
                "is_completed": session.current_step >= 6 and session.progress >= 100.0,
                "current_step": session.current_step,
                "progress": session.progress,
                "started_at": session.started_at.isoformat() if session.started_at else None,
                "updated_at": session.updated_at.isoformat() if session.updated_at else None
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting onboarding status: {e}")
            return {
                "is_completed": False,
                "current_step": 1,
                "progress": 0.0,
                "started_at": None,
                "updated_at": None
            }

