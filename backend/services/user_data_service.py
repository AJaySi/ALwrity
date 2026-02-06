"""
User Data Service
Handles fetching user data from the onboarding database.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from utils.logging import get_logger
logger = get_logger("user_data_service", migration_mode=True)

from models.onboarding import OnboardingSession, WebsiteAnalysis, APIKey, ResearchPreferences

class UserDataService:
    """Service for managing user data from onboarding."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_user_website_url(self, user_id: int = 1) -> Optional[str]:
        """
        Get the website URL for a user from their onboarding data.
        
        Args:
            user_id: The user ID (defaults to 1 for single-user setup)
            
        Returns:
            Website URL or None if not found
        """
        try:
            # Get the latest onboarding session for the user
            session = self.db.query(OnboardingSession).filter(
                OnboardingSession.user_id == user_id
            ).order_by(OnboardingSession.updated_at.desc()).first()
            
            if not session:
                logger.warning(f"No onboarding session found for user {user_id}")
                return None
            
            # Get the latest website analysis for this session
            website_analysis = self.db.query(WebsiteAnalysis).filter(
                WebsiteAnalysis.session_id == session.id
            ).order_by(WebsiteAnalysis.updated_at.desc()).first()
            
            if not website_analysis:
                logger.warning(f"No website analysis found for session {session.id}")
                return None
            
            logger.info(f"Found website URL: {website_analysis.website_url}")
            return website_analysis.website_url
            
        except Exception as e:
            logger.error(f"Error getting user website URL: {str(e)}")
            return None
    
    def get_user_onboarding_data(self, user_id: int = 1) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive onboarding data for a user.
        
        Args:
            user_id: The user ID (defaults to 1 for single-user setup)
            
        Returns:
            Dictionary with onboarding data or None if not found
        """
        try:
            # Get the latest onboarding session
            session = self.db.query(OnboardingSession).filter(
                OnboardingSession.user_id == user_id
            ).order_by(OnboardingSession.updated_at.desc()).first()
            
            if not session:
                return None
            
            # Get website analysis
            website_analysis = self.db.query(WebsiteAnalysis).filter(
                WebsiteAnalysis.session_id == session.id
            ).order_by(WebsiteAnalysis.updated_at.desc()).first()
            
            # Get API keys
            api_keys = self.db.query(APIKey).filter(
                APIKey.session_id == session.id
            ).all()
            
            # Get research preferences
            research_preferences = self.db.query(ResearchPreferences).filter(
                ResearchPreferences.session_id == session.id
            ).first()
            
            return {
                'session': {
                    'id': session.id,
                    'current_step': session.current_step,
                    'progress': session.progress,
                    'started_at': session.started_at.isoformat() if session.started_at else None,
                    'updated_at': session.updated_at.isoformat() if session.updated_at else None
                },
                'website_analysis': website_analysis.to_dict() if website_analysis else None,
                'api_keys': [
                    {
                        'id': key.id,
                        'provider': key.provider,
                        'created_at': key.created_at.isoformat() if key.created_at else None
                    }
                    for key in api_keys
                ],
                'research_preferences': research_preferences.to_dict() if research_preferences else None
            }
            
        except Exception as e:
            logger.error(f"Error getting user onboarding data: {str(e)}")
            return None
    
    def get_user_website_analysis(self, user_id: int = 1) -> Optional[Dict[str, Any]]:
        """
        Get website analysis data for a user.
        
        Args:
            user_id: The user ID (defaults to 1 for single-user setup)
            
        Returns:
            Website analysis data or None if not found
        """
        try:
            # Get the latest onboarding session
            session = self.db.query(OnboardingSession).filter(
                OnboardingSession.user_id == user_id
            ).order_by(OnboardingSession.updated_at.desc()).first()
            
            if not session:
                return None
            
            # Get website analysis
            website_analysis = self.db.query(WebsiteAnalysis).filter(
                WebsiteAnalysis.session_id == session.id
            ).order_by(WebsiteAnalysis.updated_at.desc()).first()
            
            if not website_analysis:
                return None
            
            return website_analysis.to_dict()
            
        except Exception as e:
            logger.error(f"Error getting user website analysis: {str(e)}")
            return None 