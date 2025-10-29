"""
Onboarding Control Service
Handles onboarding session control and management.
"""

from typing import Dict, Any
from fastapi import HTTPException
from loguru import logger

from services.onboarding.api_key_manager import get_onboarding_progress, get_onboarding_progress_for_user

class OnboardingControlService:
    """Service for handling onboarding control operations."""
    
    def __init__(self):
        pass
    
    async def start_onboarding(self, current_user: Dict[str, Any]) -> Dict[str, Any]:
        """Start a new onboarding session."""
        try:
            user_id = str(current_user.get('id'))
            progress = get_onboarding_progress_for_user(user_id)
            progress.reset_progress()
            
            return {
                "message": "Onboarding started successfully",
                "current_step": progress.current_step,
                "started_at": progress.started_at
            }
        except Exception as e:
            logger.error(f"Error starting onboarding: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def reset_onboarding(self) -> Dict[str, Any]:
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
    
    async def get_resume_info(self) -> Dict[str, Any]:
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
