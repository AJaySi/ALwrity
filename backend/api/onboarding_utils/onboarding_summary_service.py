"""
Onboarding Summary Service
Handles the complex logic for generating comprehensive onboarding summaries.
"""

from typing import Dict, Any, Optional
from fastapi import HTTPException
from loguru import logger

from services.onboarding.api_key_manager import get_api_key_manager
from services.database import get_db
from services.onboarding.database_service import OnboardingDatabaseService
from services.website_analysis_service import WebsiteAnalysisService
from services.research_preferences_service import ResearchPreferencesService
from services.persona_analysis_service import PersonaAnalysisService
from services.user_website_service import user_website_service

class OnboardingSummaryService:
    """Service for handling onboarding summary generation with user isolation."""
    
    def __init__(self, user_id: str):
        """
        Initialize service with user-specific context.
        
        Args:
            user_id: Clerk user ID from authenticated request
        """
        self.user_id = user_id  # Store Clerk user ID (string)
        self.db_service = OnboardingDatabaseService()
        
        logger.info(f"OnboardingSummaryService initialized for user {user_id} (database mode)")
    
    async def get_onboarding_summary(self) -> Dict[str, Any]:
        """Get comprehensive onboarding summary for FinalStep."""
        try:
            # Get API keys
            api_keys = self._get_api_keys()
            
            # Get website analysis data
            website_analysis = self._get_website_analysis()
            
            # Get research preferences
            research_preferences = self._get_research_preferences()
            
            # Get personalization settings
            personalization_settings = self._get_personalization_settings(research_preferences)
            
            # Check persona generation readiness
            persona_readiness = self._check_persona_readiness(website_analysis)
            
            # Determine capabilities
            capabilities = self._determine_capabilities(api_keys, website_analysis, research_preferences, personalization_settings, persona_readiness)
            
            user_website = user_website_service.get_user_website_by_user(self.user_id) if self.user_id else None

            return {
                "api_keys": api_keys,
                "website_url": website_analysis.get('website_url') if website_analysis else None,
                "preview_url": user_website.preview_url if user_website else None,
                "live_url": user_website.netlify_site_url if user_website else None,
                "style_analysis": website_analysis.get('style_analysis') if website_analysis else None,
                "research_preferences": research_preferences,
                "personalization_settings": personalization_settings,
                "persona_readiness": persona_readiness,
                "integrations": {},  # TODO: Implement integrations data
                "capabilities": capabilities
            }
            
        except Exception as e:
            logger.error(f"Error getting onboarding summary: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    def _get_api_keys(self) -> Dict[str, Any]:
        """Get configured API keys from database."""
        try:
            db = next(get_db())
            api_keys = self.db_service.get_api_keys(self.user_id, db)
            db.close()
            
            if not api_keys:
                return {
                    "openai": {"configured": False, "value": None},
                    "anthropic": {"configured": False, "value": None},
                    "google": {"configured": False, "value": None}
                }
            
            return {
                "openai": {
                    "configured": bool(api_keys.get('openai_api_key')),
                    "value": api_keys.get('openai_api_key')[:8] + "..." if api_keys.get('openai_api_key') else None
                },
                "anthropic": {
                    "configured": bool(api_keys.get('anthropic_api_key')),
                    "value": api_keys.get('anthropic_api_key')[:8] + "..." if api_keys.get('anthropic_api_key') else None
                },
                "google": {
                    "configured": bool(api_keys.get('google_api_key')),
                    "value": api_keys.get('google_api_key')[:8] + "..." if api_keys.get('google_api_key') else None
                }
            }
        except Exception as e:
            logger.error(f"Error getting API keys: {str(e)}")
            return {
                "openai": {"configured": False, "value": None},
                "anthropic": {"configured": False, "value": None},
                "google": {"configured": False, "value": None}
            }
    
    def _get_website_analysis(self) -> Optional[Dict[str, Any]]:
        """Get website analysis data from database."""
        try:
            db = next(get_db())
            website_data = self.db_service.get_website_analysis(self.user_id, db)
            db.close()
            return website_data
        except Exception as e:
            logger.error(f"Error getting website analysis: {str(e)}")
            return None
    
    async def get_website_analysis_data(self) -> Dict[str, Any]:
        """Get website analysis data for API endpoint."""
        try:
            website_analysis = self._get_website_analysis()
            return {
                "website_analysis": website_analysis,
                "status": "success" if website_analysis else "no_data"
            }
        except Exception as e:
            logger.error(f"Error in get_website_analysis_data: {str(e)}")
            raise e
    
    def _get_research_preferences(self) -> Optional[Dict[str, Any]]:
        """Get research preferences from database."""
        try:
            db = next(get_db())
            preferences = self.db_service.get_research_preferences(self.user_id, db)
            db.close()
            return preferences
        except Exception as e:
            logger.error(f"Error getting research preferences: {str(e)}")
            return None
    
    def _get_personalization_settings(self, research_preferences: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Get personalization settings based on research preferences."""
        if not research_preferences:
            return {
                "writing_style": "professional",
                "target_audience": "general",
                "content_focus": "informative"
            }
        
        return {
            "writing_style": research_preferences.get('writing_style', 'professional'),
            "target_audience": research_preferences.get('target_audience', 'general'),
            "content_focus": research_preferences.get('content_focus', 'informative')
        }
    
    def _check_persona_readiness(self, website_analysis: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Check if persona generation is ready based on available data."""
        if not website_analysis:
            return {
                "ready": False,
                "reason": "Website analysis not completed",
                "missing_data": ["website_url", "style_analysis"]
            }
        
        required_fields = ['website_url', 'writing_style', 'target_audience']
        missing_fields = [field for field in required_fields if not website_analysis.get(field)]
        
        return {
            "ready": len(missing_fields) == 0,
            "reason": "All required data available" if len(missing_fields) == 0 else f"Missing: {', '.join(missing_fields)}",
            "missing_data": missing_fields
        }
    
    def _determine_capabilities(self, api_keys: Dict[str, Any], website_analysis: Optional[Dict[str, Any]], 
                              research_preferences: Optional[Dict[str, Any]], 
                              personalization_settings: Dict[str, Any], 
                              persona_readiness: Dict[str, Any]) -> Dict[str, Any]:
        """Determine available capabilities based on configured data."""
        capabilities = {
            "ai_content_generation": any(key.get("configured") for key in api_keys.values()),
            "website_analysis": website_analysis is not None,
            "research_capabilities": research_preferences is not None,
            "persona_generation": persona_readiness.get("ready", False),
            "content_optimization": website_analysis is not None and research_preferences is not None
        }
        
        return capabilities
    
    async def get_research_preferences_data(self) -> Dict[str, Any]:
        """Get research preferences data for the user."""
        try:
            db = next(get_db())
            research_prefs_service = ResearchPreferencesService(db)
            # Use the new method that accepts user_id directly
            result = research_prefs_service.get_research_preferences_by_user_id(self.user_id)
            db.close()
            return result
        except Exception as e:
            logger.error(f"Error getting research preferences data: {e}")
            raise
