"""
Onboarding Summary Service
Handles the complex logic for generating comprehensive onboarding summaries.
"""

from typing import Dict, Any, Optional
from fastapi import HTTPException
from loguru import logger

from services.onboarding.api_key_manager import get_api_key_manager
from services.database import get_session_for_user
from services.website_analysis_service import WebsiteAnalysisService
from services.research_preferences_service import ResearchPreferencesService
from services.persona_analysis_service import PersonaAnalysisService
from api.content_planning.services.content_strategy.onboarding import OnboardingDataIntegrationService

class OnboardingSummaryService:
    """Service for handling onboarding summary generation with user isolation."""
    
    def __init__(self, user_id: str):
        """
        Initialize service with user-specific context.
        
        Args:
            user_id: Clerk user ID from authenticated request
        """
        self.user_id = user_id  # Store Clerk user ID (string)
        self.integration_service = OnboardingDataIntegrationService()
        
        logger.info(f"OnboardingSummaryService initialized for user {user_id} (SSOT mode)")
    
    async def get_onboarding_summary(self) -> Dict[str, Any]:
        """Get comprehensive onboarding summary for FinalStep."""
        try:
            db = get_session_for_user(self.user_id)
            if not db:
                raise HTTPException(status_code=500, detail="Database session could not be created")
            try:
                integrated_data = await self.integration_service.process_onboarding_data(self.user_id, db)
            finally:
                db.close()
            
            # Extract components from integrated data
            website_analysis = integrated_data.get('website_analysis', {})
            research_preferences = integrated_data.get('research_preferences', {})
            persona_data = integrated_data.get('persona_data', {})
            canonical_profile = integrated_data.get('canonical_profile', {})
            api_keys_data = integrated_data.get('api_keys_data', {})
            
            # Get API keys
            api_keys = self._get_api_keys(api_keys_data)
            
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
                "integrations": {},
                "capabilities": capabilities,
                "canonical_profile": canonical_profile
            }
            
        except Exception as e:
            logger.error(f"Error getting onboarding summary: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    def _get_api_keys(self, api_keys_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get configured API keys from integrated data."""
        try:
            if not api_keys_data:
                return {
                    "openai": {"configured": False, "value": None},
                    "anthropic": {"configured": False, "value": None},
                    "google": {"configured": False, "value": None}
                }
            
            return {
                "openai": {
                    "configured": bool(api_keys_data.get('openai_api_key')),
                    "value": api_keys_data.get('openai_api_key')[:8] + "..." if api_keys_data.get('openai_api_key') else None
                },
                "anthropic": {
                    "configured": bool(api_keys_data.get('anthropic_api_key')),
                    "value": api_keys_data.get('anthropic_api_key')[:8] + "..." if api_keys_data.get('anthropic_api_key') else None
                },
                "google": {
                    "configured": bool(api_keys_data.get('google_api_key')),
                    "value": api_keys_data.get('google_api_key')[:8] + "..." if api_keys_data.get('google_api_key') else None
                }
            }
        except Exception as e:
            logger.error(f"Error getting API keys: {str(e)}")
            return {
                "openai": {"configured": False, "value": None},
                "anthropic": {"configured": False, "value": None},
                "google": {"configured": False, "value": None}
            }
    
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
    
    async def get_website_analysis_data(self) -> Dict[str, Any]:
        """Get website analysis data for the user (Step 2 output)."""
        try:
            db = get_session_for_user(self.user_id)
            if not db:
                raise HTTPException(status_code=500, detail="Database session could not be created")
            try:
                integrated_data = await self.integration_service.process_onboarding_data(self.user_id, db)
                website_analysis = integrated_data.get("website_analysis") or {}
                return website_analysis
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error getting website analysis data: {e}")
            raise
    
    async def get_research_preferences_data(self) -> Dict[str, Any]:
        """Get research preferences data for the user."""
        try:
            db = get_session_for_user(self.user_id)
            if not db:
                raise HTTPException(status_code=500, detail="Database session could not be created")
            try:
                research_prefs_service = ResearchPreferencesService(db)
                result = research_prefs_service.get_research_preferences_by_user_id(self.user_id)
                return result
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error getting research preferences data: {e}")
            raise
