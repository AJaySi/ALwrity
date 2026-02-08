"""
User Data Service
Handles fetching user data from the onboarding database.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from loguru import logger

from models.onboarding import OnboardingSession, WebsiteAnalysis, APIKey, ResearchPreferences
from api.content_planning.services.content_strategy.onboarding import OnboardingDataIntegrationService

class UserDataService:
    """Service for managing user data from onboarding."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.integration_service = OnboardingDataIntegrationService()
    
    def get_user_website_url(self, user_id: int = 1) -> Optional[str]:
        """
        Get the website URL for a user from their onboarding data.
        
        Args:
            user_id: The user ID (defaults to 1 for single-user setup)
            
        Returns:
            Website URL or None if not found
        """
        try:
            # Use SSOT integration service
            integrated_data = self.integration_service.get_integrated_data_sync(str(user_id), self.db)
            website_analysis = integrated_data.get('website_analysis', {})
            
            if not website_analysis:
                logger.warning(f"No website analysis found for user {user_id}")
                return None
            
            url = website_analysis.get('website_url')
            if url:
                logger.info(f"Found website URL: {url}")
                return url
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user website URL: {str(e)}")
            return None
    
    def get_user_onboarding_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive onboarding data for a user.
        
        Args:
            user_id: The user ID (defaults to 1 for single-user setup)
            
        Returns:
            Dictionary with onboarding data or None if not found
        """
        try:
            # Use SSOT integration service
            integrated_data = self.integration_service.get_integrated_data_sync(user_id, self.db)
            
            if not integrated_data.get('onboarding_session'):
                return None
            
            # Map SSOT data to legacy format expected by consumers
            return {
                'session': integrated_data.get('onboarding_session'),
                'website_analysis': integrated_data.get('website_analysis'),
                'api_keys': integrated_data.get('api_keys_data', {}).get('api_keys', []),
                'research_preferences': integrated_data.get('research_preferences')
            }
            
        except Exception as e:
            logger.error(f"Error getting user onboarding data: {str(e)}")
            return None
    
    def get_user_website_analysis(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get website analysis data for a user.
        
        Args:
            user_id: The user ID (defaults to 1 for single-user setup)
            
        Returns:
            Website analysis data or None if not found
        """
        try:
            # Use SSOT integration service
            integrated_data = self.integration_service.get_integrated_data_sync(user_id, self.db)
            return integrated_data.get('website_analysis')
            
        except Exception as e:
            logger.error(f"Error getting user website analysis: {str(e)}")
            return None 
