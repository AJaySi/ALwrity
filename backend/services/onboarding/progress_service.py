"""
Database-only Onboarding Progress Service
Replaces file-based progress tracking with database-only implementation.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from services.database import SessionLocal
from .database_service import OnboardingDatabaseService


class OnboardingProgressService:
    """Database-only onboarding progress management."""
    
    def __init__(self):
        self.db_service = OnboardingDatabaseService()
    
    def get_onboarding_status(self, user_id: str) -> Dict[str, Any]:
        """Get current onboarding status from database only."""
        try:
            db = SessionLocal()
            try:
                # Get session data
                session = self.db_service.get_session_by_user(user_id, db)
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
                # This guards against partial writes where one field persisted but the other didn't.
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
            db = SessionLocal()
            try:
                success = self.db_service.update_step(user_id, step_number, db)
                if success:
                    logger.info(f"Updated user {user_id} to step {step_number}")
                return success
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error updating step: {e}")
            return False
    
    def update_progress(self, user_id: str, progress_percentage: float) -> bool:
        """Update progress percentage in database."""
        try:
            db = SessionLocal()
            try:
                success = self.db_service.update_progress(user_id, progress_percentage, db)
                if success:
                    logger.info(f"Updated user {user_id} progress to {progress_percentage}%")
                return success
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error updating progress: {e}")
            return False
    
    def complete_onboarding(self, user_id: str) -> bool:
        """Mark onboarding as complete in database."""
        try:
            db = SessionLocal()
            try:
                success = self.db_service.mark_onboarding_complete(user_id, db)
                if success:
                    logger.info(f"Marked onboarding complete for user {user_id}")
                return success
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error completing onboarding: {e}")
            return False
    
    def reset_onboarding(self, user_id: str) -> bool:
        """Reset onboarding progress in database."""
        try:
            db = SessionLocal()
            try:
                # Reset to step 1, 0% progress
                success = self.db_service.update_step(user_id, 1, db)
                if success:
                    self.db_service.update_progress(user_id, 0.0, db)
                    logger.info(f"Reset onboarding for user {user_id}")
                return success
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error resetting onboarding: {e}")
            return False
    
    def get_completion_data(self, user_id: str) -> Dict[str, Any]:
        """Get completion data for validation."""
        try:
            db = SessionLocal()
            try:
                # Get all relevant data for completion validation
                session = self.db_service.get_session_by_user(user_id, db)
                api_keys = self.db_service.get_api_keys(user_id, db)
                website_analysis = self.db_service.get_website_analysis(user_id, db)
                research_preferences = self.db_service.get_research_preferences(user_id, db)
                persona_data = self.db_service.get_persona_data(user_id, db)

                return {
                    "session": session,
                    "api_keys": api_keys or {},  # Convert None to empty dict
                    "website_analysis": website_analysis or {},  # Convert None to empty dict
                    "research_preferences": research_preferences or {},  # Convert None to empty dict
                    "persona_data": persona_data or {}  # Convert None to empty dict
                }
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error getting completion data: {e}")
            return {}


# Global instance
_onboarding_progress_service = None

def get_onboarding_progress_service() -> OnboardingProgressService:
    """Get the global onboarding progress service instance."""
    global _onboarding_progress_service
    if _onboarding_progress_service is None:
        _onboarding_progress_service = OnboardingProgressService()
    return _onboarding_progress_service
