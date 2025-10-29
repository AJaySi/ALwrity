"""DeepSeek Provider Service for ALwrity Backend.

This service handles DeepSeek API integrations,
migrated from the legacy lib/gpt_providers/text_generation/deepseek_text_gen.py
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
    import openai
except ImportError:
    openai = None
    logger.warning("OpenAI library not available. Install with: pip install openai")

async def test_deepseek_api_key(api_key: str) -> Tuple[bool, str]:
    """
    Test if the provided DeepSeek API key is valid.
    
    Args:
        api_key (str): The DeepSeek API key to test
        
    Returns:
        tuple[bool, str]: A tuple containing (is_valid, message)
    """
    if not openai:
        return False, "OpenAI library not available"
    
    try:
        # Create DeepSeek client with the provided key
        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1"
        )
        
        # Try to generate a simple response as a test
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10,
            temperature=0.1
        )
        
        # If we get here, the key is valid
        return True, "DeepSeek API key is valid"
        
    except openai.AuthenticationError:
        return False, "Invalid DeepSeek API key"
    except openai.RateLimitError:
        return False, "Rate limit exceeded. Please try again later."
    except Exception as e:
        return False, f"Error testing DeepSeek API key: {str(e)}"

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def deepseek_text_response(prompt: str, model: str = "deepseek-chat", 
                          temperature: float = 0.7, max_tokens: int = 4000, 
                          system_prompt: str = None) -> str:
    """Get response from DeepSeek."""
    if not openai:
        logger.error("OpenAI library not available")
        return "OpenAI library not available. Please install openai package."
    
    try:
        # Use APIKeyManager instead of direct environment variable access
        api_key_manager = APIKeyManager()
        api_key = api_key_manager.get_api_key("deepseek")
        
        if not api_key:
            raise ValueError("DeepSeek API key not found. Please configure it in the onboarding process.")
        
        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1"
        )
        
        # Prepare messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        logger.info(f"[deepseek_text_response] Generated response with {len(response.choices[0].message.content)} characters")
        return response.choices[0].message.content
        
    except Exception as err:
        logger.error(f"Failed to get response from DeepSeek: {err}. Retrying.")
        raise 