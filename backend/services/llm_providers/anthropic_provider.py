"""Anthropic Provider Service for ALwrity Backend.

This service handles Anthropic API integrations,
migrated from the legacy lib/gpt_providers/text_generation/anthropic_text_gen.py
"""

import os
import json
import time
from typing import Dict, Any, Tuple
from loguru import logger
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)

# Import APIKeyManager
from ..onboarding.api_key_manager import APIKeyManager

try:
    import anthropic
except ImportError:
    anthropic = None
    logger.warning("Anthropic library not available. Install with: pip install anthropic")

async def test_anthropic_api_key(api_key: str) -> Tuple[bool, str]:
    """
    Test if the provided Anthropic API key is valid.
    
    Args:
        api_key (str): The Anthropic API key to test
        
    Returns:
        tuple[bool, str]: A tuple containing (is_valid, message)
    """
    if not anthropic:
        return False, "Anthropic library not available"
    
    try:
        # Create Anthropic client with the provided key
        client = anthropic.Anthropic(api_key=api_key)
        
        # Try to generate a simple response as a test
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=10,
            messages=[{"role": "user", "content": "Hello"}]
        )
        
        # If we get here, the key is valid
        return True, "Anthropic API key is valid"
        
    except anthropic.AuthenticationError:
        return False, "Invalid Anthropic API key"
    except anthropic.RateLimitError:
        return False, "Rate limit exceeded. Please try again later."
    except Exception as e:
        return False, f"Error testing Anthropic API key: {str(e)}"

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def anthropic_text_response(prompt: str, model: str = "claude-3-5-sonnet-20241022", 
                           temperature: float = 0.7, max_tokens: int = 4000, 
                           system_prompt: str = None) -> str:
    """Get response from Anthropic Claude."""
    if not anthropic:
        logger.error("Anthropic library not available")
        return "Anthropic library not available. Please install anthropic package."
    
    try:
        # Use APIKeyManager instead of direct environment variable access
        api_key_manager = APIKeyManager()
        api_key = api_key_manager.get_api_key("anthropic")
        
        if not api_key:
            raise ValueError("Anthropic API key not found. Please configure it in the onboarding process.")
        
        client = anthropic.Anthropic(api_key=api_key)
        
        # Prepare messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=messages
        )
        
        logger.info(f"[anthropic_text_response] Generated response with {len(response.content[0].text)} characters")
        return response.content[0].text
        
    except Exception as err:
        logger.error(f"Failed to get response from Anthropic: {err}. Retrying.")
        raise 