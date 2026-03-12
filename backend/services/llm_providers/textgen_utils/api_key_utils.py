"""
API Key Utilities Module

This module contains API key-related utility functions extracted from main_text_generation.py
to resolve merge conflicts and improve maintainability.
"""

from typing import Optional
from loguru import logger

from ..tenant_provider_config import tenant_provider_config_resolver


def get_api_key(gpt_provider: str, user_id: Optional[str] = None) -> Optional[str]:
    """Get API key for the specified provider."""
    try:
        provider_mapping = {
            "google": "gemini",
            "huggingface": "huggingface"
        }
        mapped_provider = provider_mapping.get(gpt_provider, gpt_provider)
        key, _source = tenant_provider_config_resolver.resolve_provider_key(mapped_provider, user_id=user_id)
        return key
    except Exception as e:
        logger.error(f"[get_api_key] Error getting API key for {gpt_provider}: {str(e)}")
        return None
