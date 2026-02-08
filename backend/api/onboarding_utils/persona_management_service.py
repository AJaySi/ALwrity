"""
Persona Management Service
Handles persona generation and management for onboarding.
"""

from typing import Dict, Any
from fastapi import HTTPException
from loguru import logger

class PersonaManagementService:
    """Service for handling persona management operations."""
    
    def __init__(self):
        pass
    
    async def check_persona_generation_readiness(self, user_id: str) -> Dict[str, Any]:
        """Check if user has sufficient data for persona generation."""
        try:
            from api.persona import validate_persona_generation_readiness
            return await validate_persona_generation_readiness(user_id)
        except Exception as e:
            logger.error(f"Error checking persona readiness: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def generate_persona_preview(self, user_id: str) -> Dict[str, Any]:
        """Generate a preview of the writing persona without saving."""
        try:
            from api.persona import generate_persona_preview
            return await generate_persona_preview(user_id)
        except Exception as e:
            logger.error(f"Error generating persona preview: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def generate_writing_persona(self, user_id: str) -> Dict[str, Any]:
        """Generate and save a writing persona from onboarding data."""
        try:
            from api.persona import generate_persona, PersonaGenerationRequest
            request = PersonaGenerationRequest(force_regenerate=False)
            return await generate_persona(user_id, request)
        except Exception as e:
            logger.error(f"Error generating writing persona: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def get_user_writing_personas(self, user_id: str) -> Dict[str, Any]:
        """Get all writing personas for the user."""
        try:
            from api.persona import get_user_personas
            return await get_user_personas(user_id)
        except Exception as e:
            logger.error(f"Error getting user personas: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
