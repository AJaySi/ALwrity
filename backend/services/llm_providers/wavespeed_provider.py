"""
WaveSpeed LLM Provider Module for ALwrity

This module provides functions for interacting with WaveSpeed's LLM API
using the OpenAI-compatible interface for text generation.

Key Features:
- Text response generation with retry logic
- Comprehensive error handling and logging
- Automatic API key management
- Support for gpt-oss and other WaveSpeed models
- Integration with subscription/preflight checks

Best Practices:
1. Use appropriate temperature for your use case (0.7 for creative, 0.1-0.3 for factual)
2. Set max_tokens based on expected response length
3. Use system_prompt to guide model behavior
4. Handle errors gracefully in calling functions

Usage Examples:
    # Text response
    result = wavespeed_text_response(prompt, temperature=0.7, max_tokens=2048)
    
    # Structured JSON response
    schema = {"type": "object", "properties": {"title": {"type": "string"}}}
    result = wavespeed_structured_json_response(prompt, schema, temperature=0.2, max_tokens=8192)

Dependencies:
- openai (for WaveSpeed OpenAI-compatible API)
- tenacity (for retry logic)
- logging (for debugging)
- json (for fallback parsing)

Author: ALwrity Team
Version: 1.0
Last Updated: March 2026
"""

import os
import sys
from pathlib import Path
import json
import re
from typing import Optional, Dict, Any, List

from dotenv import load_dotenv

# Fix the environment loading path - load from backend directory
current_dir = Path(__file__).parent.parent  # services directory
backend_dir = current_dir.parent  # backend directory
env_path = backend_dir / '.env'

if env_path.exists():
    load_dotenv(env_path)
    print(f"Loaded .env from: {env_path}")
else:
    # Fallback to current directory
    load_dotenv()
    print(f"No .env found at {env_path}, using current directory")

from loguru import logger
from utils.logger_utils import get_service_logger

# Use service-specific logger to avoid conflicts
logger = get_service_logger("wavespeed_provider")

from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_random_exponential,
)

try:
    from openai import OpenAI
    from openai import NotFoundError
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    NotFoundError = Exception
    logger.warn("OpenAI library not available. Install with: pip install openai")

# Default WaveSpeed models for fallback
WAVESPEED_FALLBACK_MODELS = [
    "openai/gpt-oss-120b",
    "meta-llama/Llama-3.1-8B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.3",
    "google/gemma-7b-it",
]

def _candidate_model_variants(model: str):
    """Yield model ids to try for a single logical model preference."""
    if not model:
        return

    # Try configured model first
    yield model

    # Fallback to base repo id when provider suffix is not recognized by the router
    if ":" in model:
        base_model = model.split(":", 1)[0]
        if base_model:
            yield base_model

def _fallback_model_sequence(model: str, fallback_models: Optional[List[str]] = None):
    # IMPORTANT: Do not apply implicit global fallback chains.
    # Callers must explicitly provide fallback_models when they want multi-model retries.
    if fallback_models:
        sequence = [model] + fallback_models
    else:
        sequence = [model]
    seen = set()
    for preferred_model in sequence:
        for candidate in _candidate_model_variants(preferred_model):
            if candidate and candidate not in seen:
                seen.add(candidate)
                yield candidate

def _is_non_retryable_wavespeed_error(exc: Exception) -> bool:
    """Skip retries for deterministic WaveSpeed failures (e.g., unknown model ids, billing)."""
    msg = str(exc).lower()
    status = getattr(exc, "status_code", None)
    
    # Non-retryable errors
    if isinstance(exc, NotFoundError) or "not found" in msg or "404" in msg:
        return True
    if status == 402 or "402" in msg or "depleted" in msg or "credits" in msg:
        return True
    if status == 401 or "unauthorized" in msg or "401" in msg:
        return True
    if status == 403 or "forbidden" in msg or "403" in msg:
        return True
    
    return False

def _should_retry_wavespeed_error(exc: Exception) -> bool:
    return not _is_non_retryable_wavespeed_error(exc)

def _classify_wavespeed_error(exc: Exception) -> str:
    """Classify WaveSpeed failures for actionable logs."""
    msg = str(exc).lower()
    if any(token in msg for token in ["insufficient", "balance", "quota", "billing", "payment", "402"]):
        return "billing_or_quota"
    if "unauthorized" in msg or "forbidden" in msg or "401" in msg or "403" in msg:
        return "auth_or_permission"
    if "not found" in msg or "404" in msg:
        return "model_not_found"
    return "unknown"

def _wavespeed_error_details(exc: Exception) -> str:
    """Return compact, actionable exception details for logs."""
    status = getattr(exc, "status_code", None)
    err_type = type(exc).__name__
    message = str(exc)
    raw_body = getattr(exc, "body", None)
    details = f"type={err_type}"
    if status is not None:
        details += f", status={status}"
    if message:
        details += f", message={message}"
    if raw_body:
        details += f", body={raw_body}"
    details += f", repr={repr(exc)}"
    return details

def get_wavespeed_api_key() -> str:
    """Get WaveSpeed API key with proper error handling."""
    api_key = os.getenv('WAVESPEED_API_KEY')
    if not api_key:
        error_msg = "WAVESPEED_API_KEY environment variable is not set. Please set it in your .env file."
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Validate API key format (basic check)
    if not api_key or len(api_key) < 10:
        error_msg = "WAVESPEED_API_KEY appears to be invalid."
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    return api_key

@retry(
    retry=retry_if_exception(_should_retry_wavespeed_error),
    wait=wait_random_exponential(min=1, max=60),
    stop=stop_after_attempt(6),
)
def wavespeed_text_response(
    prompt: str,
    model: str = "openai/gpt-oss-120b",
    fallback_models: Optional[List[str]] = None,
    temperature: float = 0.7,
    max_tokens: int = 2048,
    top_p: float = 0.9,
    system_prompt: Optional[str] = None
) -> str:
    """
    Generate text response using WaveSpeed LLM API.
    
    This function uses the WaveSpeed OpenAI-compatible API for text generation
    with built-in retry logic and error handling.
    
    Args:
        prompt (str): The input prompt for the AI model
        model (str): WaveSpeed model identifier (default: "openai/gpt-oss-120b")
        temperature (float): Controls randomness (0.0-1.0)
        max_tokens (int): Maximum tokens in response
        top_p (float): Nucleus sampling parameter (0.0-1.0)
        system_prompt (str, optional): System instruction for the model
    
    Returns:
        str: Generated text response
        
    Raises:
        Exception: If API key is missing or API call fails
        
    Best Practices:
        - Use appropriate temperature for your use case (0.7 for creative, 0.1-0.3 for factual)
        - Set max_tokens based on expected response length
        - Use system_prompt to guide model behavior
        - Handle errors gracefully in calling functions
        
    Example:
        result = wavespeed_text_response(
            prompt="Write a blog post about AI",
            model="openai/gpt-oss-120b",
            temperature=0.7,
            max_tokens=2048,
            system_prompt="You are a professional content writer."
        )
    """
    try:
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not available. Install with: pip install openai")
        
        # Get API key with proper error handling
        api_key = get_wavespeed_api_key()
        logger.info(f"🔑 WaveSpeed API key loaded: {bool(api_key)} (length: {len(api_key) if api_key else 0})")
        
        if not api_key:
            raise Exception("WAVESPEED_API_KEY not found in environment variables")
            
        # Initialize WaveSpeed client
        client = OpenAI(
            base_url="https://llm.wavespeed.ai/v1",
            api_key=api_key,
        )
        logger.info("✅ WaveSpeed client initialized for text response")

        # Prepare input for the API
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        # Add user prompt
        messages.append({
            "role": "user", 
            "content": prompt
        })

        # Add debugging for API call
        logger.info(
            "WaveSpeed text call | model={} | prompt_len={} | temp={} | top_p={} | max_tokens={}",
            model,
            len(prompt) if isinstance(prompt, str) else '<non-str>',
            temperature,
            top_p,
            max_tokens,
        )
        
        logger.info("🚀 Making WaveSpeed API call (chat completion)...")
        
        # Add rate limiting to prevent expensive API calls
        import time
        time.sleep(1)  # 1 second delay between API calls
        
        # Call exactly the requested model; no retries, no fallbacks, no variants
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens
        )
        
        # Extract text from response
        generated_text = response.choices[0].message.content
        
        # Clean up the response
        if generated_text:
            # Remove any markdown formatting if present
            generated_text = re.sub(r'```[a-zA-Z]*\n?', '', generated_text)
            generated_text = re.sub(r'```\n?', '', generated_text)
            generated_text = generated_text.strip()
        
        logger.info(f"✅ WaveSpeed text response generated successfully (length: {len(generated_text)})")
        return generated_text
        
    except Exception as e:
        error_class = _classify_wavespeed_error(e)
        error_details = _wavespeed_error_details(e)
        logger.error(f"❌ WaveSpeed text generation failed: {error_details}")
        
        # Extra diagnostics: try to capture raw response if available
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"🔍 WaveSpeed Error Diagnostics:")
            logger.error(f"  - Status: {e.response.status_code}")
            logger.error(f"  - Headers: {dict(e.response.headers)}")
            try:
                body_json = e.response.json()
                logger.error(f"  - Body JSON: {json.dumps(body_json, indent=2)}")
            except Exception:
                logger.error(f"  - Body Raw: {e.response.text[:1000]}")
        else:
            logger.error(f"🔍 No HTTP response attached to exception object.")
        
        raise Exception(f"WaveSpeed text generation failed: {str(e)}")

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def wavespeed_structured_json_response(
    prompt: str,
    schema: Dict[str, Any],
    model: str = "openai/gpt-oss-120b",
    fallback_models: Optional[List[str]] = None,
    temperature: float = 0.7,
    max_tokens: int = 8192,
    system_prompt: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate structured JSON response using WaveSpeed LLM API.
    
    This function uses the WaveSpeed OpenAI-compatible API with structured output support
    to generate JSON responses that match a provided schema.
    
    Args:
        prompt (str): The input prompt for the AI model
        schema (dict): JSON schema defining the expected output structure
        model (str): WaveSpeed model identifier (default: "openai/gpt-oss-120b")
        temperature (float): Controls randomness (0.0-1.0). Use 0.1-0.3 for structured output
        max_tokens (int): Maximum tokens in response. Use 8192 for complex outputs
        system_prompt (str, optional): System instruction for the model
    
    Returns:
        dict: Parsed JSON response matching the provided schema
        
    Raises:
        Exception: If API key is missing or API call fails
        
    Best Practices:
        - Keep schemas simple and flat to avoid truncation
        - Use low temperature (0.1-0.3) for consistent structured output
        - Set max_tokens to 8192 for complex multi-field responses
        - Avoid deeply nested schemas with many required fields
        - Test with smaller outputs first, then scale up
        
    Example:
        schema = {
            "type": "object",
            "properties": {
                "tasks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "description": {"type": "string"}
                        }
                    }
                }
            }
        }
        result = wavespeed_structured_json_response(prompt, schema, temperature=0.2, max_tokens=8192)
    """
    try:
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not available. Install with: pip install openai")
        
        # Get API key with proper error handling
        api_key = get_wavespeed_api_key()
        logger.info(f"🔑 WaveSpeed API key loaded: {bool(api_key)} (length: {len(api_key) if api_key else 0})")
        
        if not api_key:
            raise Exception("WAVESPEED_API_KEY not found in environment variables")
            
        # Initialize OpenAI client with WaveSpeed base URL
        client = OpenAI(
            base_url="https://llm.wavespeed.ai/v1",
            api_key=api_key,
        )
        logger.info("✅ WaveSpeed client initialized for structured JSON response")

        # Prepare input for the API
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        # Add user prompt with JSON instruction
        json_instruction = "Please respond with valid JSON that matches the provided schema."
        messages.append({
            "role": "user", 
            "content": f"{prompt}\n\n{json_instruction}"
        })

        # Add debugging for API call
        logger.info(
            "WaveSpeed structured call | model={} | prompt_len={} | schema_kind={} | temp={} | max_tokens={}",
            model,
            len(prompt) if isinstance(prompt, str) else '<non-str>',
            type(schema).__name__,
            temperature,
            max_tokens,
        )
        
        logger.info("🚀 Making WaveSpeed structured API call...")
        
        # Add JSON schema to prompt for guidance
        json_schema_str = json.dumps(schema, indent=2)
        messages[-1]["content"] += f"\n\nJSON Schema:\n{json_schema_str}"
        
        # Add rate limiting to prevent expensive API calls
        import time
        time.sleep(1)  # 1 second delay between API calls
        
        try:
            response = None
            last_error = None
            for candidate_model in _fallback_model_sequence(model, fallback_models):
                try:
                    response = client.chat.completions.create(
                        model=candidate_model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        response_format={"type": "json_object"} # Try to enforce JSON mode if supported
                    )
                    if candidate_model != model:
                        logger.warning("WaveSpeed structured generation switched to fallback model: {}", candidate_model)
                    break
                except NotFoundError as nf_err:
                    last_error = nf_err
                    logger.warning("WaveSpeed structured model not found: {}. Trying fallback model.", candidate_model)
                    continue

            if response is None:
                raise last_error or Exception("WaveSpeed structured generation failed: all fallback models failed")
            
            response_text = response.choices[0].message.content
            
            # Clean up response text if needed
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            try:
                parsed_json = json.loads(response_text)
                logger.info("✅ WaveSpeed structured JSON response parsed successfully")
                return parsed_json
            except json.JSONDecodeError as json_err:
                logger.error(f"❌ JSON parsing failed: {json_err}")
                logger.error(f"Raw response: {response_text}")
                
                # Try to extract JSON from the response using regex
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    try:
                        extracted_json = json.loads(json_match.group())
                        logger.info("✅ JSON extracted using regex fallback")
                        return extracted_json
                    except json.JSONDecodeError:
                        pass
                
                return {"error": "Failed to parse JSON response", "raw_response": response_text}
                
        except Exception as e:
            logger.error(f"❌ WaveSpeed API call failed: {e}")
            # If 422 Unprocessable Entity (often due to response_format not supported), retry without it
            if "422" in str(e) or "not supported" in str(e).lower() or isinstance(e, NotFoundError):
                logger.info("Retrying without response_format...")
                response = None
                last_error = None
                for candidate_model in _fallback_model_sequence(model, fallback_models):
                    try:
                        response = client.chat.completions.create(
                            model=candidate_model,
                            messages=messages,
                            temperature=temperature,
                            max_tokens=max_tokens
                        )
                        if candidate_model != model:
                            logger.warning("WaveSpeed structured no-response-format fallback model: {}", candidate_model)
                        break
                    except NotFoundError as nf_err:
                        last_error = nf_err
                        logger.warning("WaveSpeed structured model not found (no response_format path): {}", candidate_model)
                        continue

                if response is None:
                    raise last_error or e
                response_text = response.choices[0].message.content
                # ... (same parsing logic would apply, simplified here for brevity)
                try:
                    return json.loads(response_text)
                except:
                     # Regex fallback
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                         return json.loads(json_match.group())
                    return {"error": "Failed to parse JSON response", "raw_response": response_text}
            raise e
        
    except Exception as e:
        error_msg = str(e) if str(e) else repr(e)
        error_type = type(e).__name__
        logger.error(f"❌ WaveSpeed structured JSON generation failed [{error_type}]: {error_msg}")
        raise Exception(f"WaveSpeed structured JSON generation failed: {error_msg}")
