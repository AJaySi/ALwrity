"""
Onboarding Summary Service
Handles the complex logic for generating comprehensive onboarding summaries.
"""

from typing import Dict, Any, Optional
from fastapi import HTTPException
from loguru import logger

from services.api_key_manager import get_api_key_manager
from services.database import get_db
from services.onboarding_database_service import OnboardingDatabaseService
from services.website_analysis_service import WebsiteAnalysisService
from services.research_preferences_service import ResearchPreferencesService
from services.persona_analysis_service import PersonaAnalysisService

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
            
            return {
                "api_keys": api_keys,
                "website_url": website_analysis.get('website_url') if website_analysis else None,
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
            logger.info(f"Retrieved {len(api_keys)} API keys from database for user {self.user_id}")
            return api_keys
        except Exception as e:
            logger.error(f"Error getting API keys from database: {e}")
            return {}
    
    def _get_website_analysis(self) -> Optional[Dict[str, Any]]:
        """Get website analysis data from database (Step 2)."""
        try:
            db = next(get_db())
            website_data = self.db_service.get_website_analysis(self.user_id, db)
            if website_data:
                logger.info(f"Retrieved website analysis from database for user {self.user_id}")
            else:
                logger.warning(f"No website analysis found in database for user {self.user_id}")
            return website_data
        except Exception as e:
            logger.error(f"Error getting website analysis from database: {e}")
            return None
    
    def _get_research_preferences(self) -> Optional[Dict[str, Any]]:
        """Get research preferences data from database (Step 3)."""
        try:
            db = next(get_db())
            research_data = self.db_service.get_research_preferences(self.user_id, db)
            if research_data:
                logger.info(f"Retrieved research preferences from database for user {self.user_id}")
            else:
                logger.warning(f"No research preferences found in database for user {self.user_id}")
            return research_data
        except Exception as e:
            logger.error(f"Error getting research preferences from database: {e}")
            return None
    
    def _get_personalization_settings(self, research_preferences: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Get personalization settings from Step 4 (Persona) database."""
        try:
            # Try to get from Step 4 (Persona) in database
            db = next(get_db())
            persona_data = self.db_service.get_persona_data(self.user_id, db)
            
            if persona_data:
                logger.info(f"Retrieved persona data from database for user {self.user_id}")
                # Extract personalization settings from persona data
                if 'corePersona' in persona_data:
                    core_persona = persona_data.get('corePersona', {})
                    return {
                        'writing_style': core_persona.get('linguistic_fingerprint', {}).get('tone', 'Professional'),
                        'tone': core_persona.get('tonal_range', {}).get('primary_tone', 'Formal'),
                        'brand_voice': core_persona.get('identity', {}).get('voice', 'Trustworthy and Expert')
                    }
            
            # Fallback to research preferences if persona data not available
            if research_preferences:
                logger.info(f"Using research preferences as fallback for personalization")
                return {
                    'writing_style': research_preferences.get('writing_style', {}).get('tone', 'Professional'),
                    'tone': research_preferences.get('writing_style', {}).get('voice', 'Formal'),
                    'brand_voice': research_preferences.get('writing_style', {}).get('complexity', 'Trustworthy and Expert')
                }
            
            return None
        except Exception as e:
            logger.error(f"Error getting personalization settings from database: {e}")
            return None
    
    def _check_persona_readiness(self, website_analysis: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Check if persona can be generated."""
        try:
            persona_service = PersonaAnalysisService()
            
            # Check if persona can be generated
            onboarding_data = persona_service._collect_onboarding_data(self.user_id)
            if onboarding_data:
                data_sufficiency = persona_service._calculate_data_sufficiency(onboarding_data)
                return {
                    "ready": data_sufficiency >= 50.0,
                    "data_sufficiency": data_sufficiency,
                    "can_generate": website_analysis is not None
                }
            return {"ready": False, "data_sufficiency": 0.0, "can_generate": False}
        except Exception as e:
            logger.warning(f"Could not check persona readiness: {str(e)}")
            return {"ready": False, "error": str(e)}
    
    def _determine_capabilities(self, api_keys: Dict[str, Any], website_analysis: Optional[Dict[str, Any]], 
                              research_preferences: Optional[Dict[str, Any]], 
                              personalization_settings: Optional[Dict[str, Any]], 
                              persona_readiness: Optional[Dict[str, Any]]) -> Dict[str, bool]:
        """Determine user capabilities based on onboarding data."""
        return {
            "ai_content": len(api_keys) > 0,
            "style_analysis": website_analysis is not None,
            "research_tools": research_preferences is not None,
            "personalization": personalization_settings is not None,
            "persona_generation": persona_readiness.get("ready", False) if persona_readiness else False,
            "integrations": False  # TODO: Implement
        }
    
    async def get_website_analysis_data(self) -> Optional[Dict[str, Any]]:
        """Get website analysis data for FinalStep."""
        try:
            analysis = self._get_website_analysis()
            
            if analysis:
                return {
                    "website_url": analysis.get('website_url'),
                    "style_analysis": analysis.get('style_analysis'),
                    "style_patterns": analysis.get('style_patterns'),
                    "style_guidelines": analysis.get('style_guidelines'),
                    "status": analysis.get('status'),
                    "completed_at": analysis.get('created_at')
                }
            else:
                return None
        except Exception as e:
            logger.error(f"Error getting website analysis data: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def get_research_preferences_data(self) -> Optional[Dict[str, Any]]:
        """Get research preferences data for FinalStep."""
        try:
            return self._get_research_preferences()
        except Exception as e:
            logger.error(f"Error getting research preferences data: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
