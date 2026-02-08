"""
Database-only Onboarding Progress Service
Replaces file-based progress tracking with database-only implementation.
Refactored to use direct DB access and eliminate legacy OnboardingDatabaseService dependency.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from services.database import SessionLocal, get_session_for_user
from models.onboarding import OnboardingSession


class OnboardingProgressService:
    """Database-only onboarding progress management."""
    
    def __init__(self):
        from api.content_planning.services.content_strategy.onboarding import OnboardingDataIntegrationService
        self.integration_service = OnboardingDataIntegrationService()
    
    def get_completion_data(self, user_id: str) -> Dict[str, Any]:
        """Get full completion data for all steps using SSOT."""
        try:
            db = get_session_for_user(user_id)
            try:
                # Use SSOT integration service to get all data
                integrated_data = self.integration_service.get_integrated_data_sync(user_id, db)
                
                # Map to format expected by StepManagementService
                return {
                    "api_keys": integrated_data.get('api_keys_data', {}),
                    "website_analysis": integrated_data.get('website_analysis', {}),
                    "research_preferences": integrated_data.get('research_preferences', {}),
                    "persona_data": integrated_data.get('persona_data', {}),
                    "onboarding_session": integrated_data.get('onboarding_session', {})
                }
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error getting completion data: {e}")
            return {}

    def get_onboarding_status(self, user_id: str) -> Dict[str, Any]:
        """Get current onboarding status from database."""
        try:
            db = get_session_for_user(user_id)
            try:
                # Direct DB access to SSOT session
                session = db.query(OnboardingSession).filter(OnboardingSession.user_id == user_id).first()
                
                if not session:
                    return {
                        "is_completed": False,
                        "current_step": 1,
                        "completion_percentage": 0.0,
                        "started_at": None,
                        "last_updated": None,
                        "completed_at": None
                    }
                
                # Check if onboarding is complete
                # Consider complete if either the final step is reached OR progress hit 100%
                is_completed = (session.current_step >= 6) or (session.progress >= 100.0)
                
                return {
                    "is_completed": is_completed,
                    "current_step": session.current_step,
                    "completion_percentage": session.progress,
                    "started_at": session.started_at.isoformat() if session.started_at else None,
                    "last_updated": session.updated_at.isoformat() if session.updated_at else None,
                    "completed_at": session.updated_at.isoformat() if is_completed else None
                }
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error getting onboarding status: {e}")
            return {
                "is_completed": False,
                "current_step": 1,
                "completion_percentage": 0.0,
                "started_at": None,
                "last_updated": None,
                "completed_at": None
            }
    
    def update_step(self, user_id: str, step_number: int) -> bool:
        """Update current step in database."""
        try:
            db = get_session_for_user(user_id)
            try:
                session = db.query(OnboardingSession).filter(OnboardingSession.user_id == user_id).first()
                if not session:
                    # Create session if not exists
                    session = OnboardingSession(
                        user_id=user_id,
                        current_step=step_number,
                        progress=0.0,
                        started_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    db.add(session)
                else:
                    session.current_step = step_number
                    session.updated_at = datetime.utcnow()
                
                db.commit()
                logger.info(f"Updated user {user_id} to step {step_number}")
                return True
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error updating step: {e}")
            return False
    
    def update_progress(self, user_id: str, progress_percentage: float) -> bool:
        """Update progress percentage in database."""
        try:
            db = get_session_for_user(user_id)
            try:
                session = db.query(OnboardingSession).filter(OnboardingSession.user_id == user_id).first()
                if session:
                    session.progress = progress_percentage
                    session.updated_at = datetime.utcnow()
                    db.commit()
                    logger.info(f"Updated user {user_id} progress to {progress_percentage}%")
                    return True
                return False
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error updating progress: {e}")
            return False
    
    def complete_onboarding(self, user_id: str) -> bool:
        """Mark onboarding as complete in database."""
        try:
            db = get_session_for_user(user_id)
            try:
                session = db.query(OnboardingSession).filter(OnboardingSession.user_id == user_id).first()
                if session:
                    session.progress = 100.0
                    session.current_step = 6  # Assuming 6 is complete
                    session.updated_at = datetime.utcnow()
                    db.commit()
                    return True
                return False
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error completing onboarding: {e}")
            return False
