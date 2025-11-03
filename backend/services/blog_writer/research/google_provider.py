"""
Google Research Provider

Wrapper for Gemini native Google Search grounding to match base provider interface.
"""

from services.llm_providers.gemini_grounded_provider import GeminiGroundedProvider
from models.subscription_models import APIProvider
from .base_provider import ResearchProvider as BaseProvider
from loguru import logger


class GoogleResearchProvider(BaseProvider):
    """Google research provider using Gemini native grounding."""
    
    def __init__(self):
        self.gemini = GeminiGroundedProvider()
    
    async def search(self, prompt, topic, industry, target_audience, config, user_id):
        """Call Gemini grounding with pre-flight validation."""
        logger.info(f"[Google Research] Executing search for topic: {topic}")
        
        result = await self.gemini.generate_grounded_content(
            prompt=prompt,
            content_type="research",
            max_tokens=2000,
            user_id=user_id,
            validate_subsequent_operations=True
        )
        
        return result
    
    def get_provider_enum(self):
        """Return GEMINI provider enum for subscription tracking."""
        return APIProvider.GEMINI
    
    def estimate_tokens(self) -> int:
        """Estimate token usage for Google grounding."""
        return 1200  # Conservative estimate

