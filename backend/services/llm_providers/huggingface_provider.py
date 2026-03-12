"""
Hugging Face Provider Module for ALwrity

This module provides functions for interacting with Hugging Face's Inference Providers API
using the Responses API (beta) which provides a unified interface for model interactions.

Key Features:
- Text response generation with retry logic
- Structured JSON response generation with schema validation
- Comprehensive error handling and logging
- Automatic API key management
- Support for various Hugging Face models via Inference Providers
- Explicit fallback model sequences
- Client caching for performance

Best Practices:
1. Use structured output for complex, multi-field responses
2. Keep schemas simple and flat to avoid truncation
3. Set appropriate token limits (8192 for complex outputs)
4. Use low temperature (0.1-0.3) for consistent structured output
5. Implement proper error handling in calling functions
6. Use the Responses API for better compatibility

Usage Examples:
    # Text response
    result = huggingface_text_response(prompt, temperature=0.7, max_tokens=2048)
    
    # Structured JSON response
    schema = {
        "type": "object",
        "properties": {
            "tasks": {
                "type": "array",
                "items": {"type": "object", "properties": {...}}
            }
        }
    }
    result = huggingface_structured_json_response(prompt, schema, temperature=0.2, max_tokens=8192)

Dependencies:
- openai (for Hugging Face Responses API)
- tenacity (for retry logic)
- logging (for debugging)
- json (for fallback parsing)

Author: ALwrity Team
Version: 1.0
Last Updated: January 2025
"""

import os
import json
import re
from functools import lru_cache
from typing import Optional, Dict, Any, List

from loguru import logger
from utils.logger_utils import get_service_logger, emit_routing_event
from .routing_policy import PREMIUM_DEFAULT_MODEL, SIF_LOW_COST_MODEL_DEFAULTS

# Use service-specific logger to avoid conflicts
logger = get_service_logger("huggingface_provider")

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

HF_FALLBACK_MODELS = [
    PREMIUM_DEFAULT_MODEL,
    "moonshotai/Kimi-K2-Instruct-0905:groq",
    "meta-llama/Llama-3.1-8B-Instruct:groq",
    SIF_LOW_COST_MODEL_DEFAULTS[0],
]


def _should_retry_hf_error(exc: Exception) -> bool:
    """Determine if an error should trigger a retry based on error type and message."""
    if isinstance(exc, NotFoundError):
        return False  # Don't retry model not found errors
    
    msg = str(exc).lower()
    # Don't retry authentication errors
    if any(keyword in msg for keyword in ["unauthorized", "forbidden", "401", "403", "invalid api key"]):
        return False
    # Don't retry billing/quota errors
    if any(keyword in msg for keyword in ["insufficient", "quota", "billing", "payment", "credits", "balance"]):
        return False
    # Retry rate limiting and server errors
    if any(keyword in msg for keyword in ["rate limit", "429", "500", "502", "503", "504", "timeout"]):
        return True
    # Default to retry for unknown errors
    return True


def _classify_hf_error(exc: Exception) -> str:
    """Classify Hugging Face errors for better error reporting."""
    msg = str(exc).lower()
    if any(keyword in msg for keyword in ["insufficient", "quota", "billing", "payment", "credits", "balance"]):
        return "billing_or_quota"
    if any(keyword in msg for keyword in ["unauthorized", "forbidden", "401", "403"]):
        return "auth_or_permission"
    if "not found" in msg or "404" in msg:
        return "model_not_found"
    if any(keyword in msg for keyword in ["rate limit", "429"]):
        return "rate_limit"
    if any(keyword in msg for keyword in ["timeout", "500", "502", "503", "504"]):
        return "server_error"
    return "unknown"


def _error_details(exc: Exception) -> Dict[str, str]:
    """Extract error details for logging."""
    return {
        "type": type(exc).__name__,
        "message": str(exc),
        "repr": repr(exc),
    }


def _candidate_model_variants(model: str):
    """Yield model ids to try for a single logical model preference."""
    if not model:
        return

    # Try configured model first (supports provider suffixes like ":groq")
    yield model

    # Fallback to base repo id when provider suffix is not recognized by the router
    if ":" in model:
        base_model = model.split(":", 1)[0]
        if base_model:
            yield base_model


def _fallback_model_sequence(model: str, fallback_models: Optional[List[str]] = None):
    """Generate a sequence of models to try as fallbacks."""
    sequence = [model] + (fallback_models or HF_FALLBACK_MODELS)
    seen = set()
    for preferred_model in sequence:
        for candidate in _candidate_model_variants(preferred_model):
            if candidate and candidate not in seen:
                seen.add(candidate)
                yield candidate


def get_huggingface_api_key(explicit_api_key: Optional[str] = None) -> str:
    """Get Hugging Face API key with proper error handling."""
    api_key = explicit_api_key or os.getenv('HF_TOKEN')
    if not api_key:
        error_msg = "HF_TOKEN environment variable is not set. Please set it in your .env file."
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Validate API key format (basic check)
    if not api_key.startswith('hf_'):
        error_msg = "HF_TOKEN appears to be invalid. It should start with 'hf_'."
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    return api_key


@lru_cache(maxsize=16)
def _get_hf_client(api_key: str):
    """Get cached Hugging Face client for better performance."""
    return OpenAI(base_url="https://router.huggingface.co/v1", api_key=api_key)


@retry(
    retry=retry_if_exception(_should_retry_hf_error),
    wait=wait_random_exponential(min=1, max=60),
    stop=stop_after_attempt(6),
)
def huggingface_text_response(
    prompt: str,
    model: str = PREMIUM_DEFAULT_MODEL,
    fallback_models: Optional[List[str]] = None,
    temperature: float = 0.7,
    max_tokens: int = 2048,
    top_p: float = 0.9,
    system_prompt: Optional[str] = None,
    api_key: Optional[str] = None,
    tenant_user_id: Optional[str] = None,
) -> str:
    """
    Generate text response using Hugging Face Inference Providers API.
    
    This function uses the Hugging Face Responses API which provides a unified interface
    for model interactions with built-in retry logic and error handling.
    
    Args:
        prompt (str): The input prompt for the AI model
        model (str): Hugging Face model identifier (default: PREMIUM_DEFAULT_MODEL)
        fallback_models (list, optional): Custom fallback models to try
        temperature (float): Controls randomness (0.0-1.0)
        max_tokens (int): Maximum tokens in response
        top_p (float): Nucleus sampling parameter (0.0-1.0)
        system_prompt (str, optional): System instruction for the model
        api_key (str, optional): Explicit API key override
    
    Returns:
        str: Generated text response
        
    Raises:
        Exception: If API key is missing or API call fails
        
    Best Practices:
        - Use appropriate temperature for your use case (0.7 for creative, 0.1-0.3 for factual)
        - Set max_tokens based on expected response length
        - Use system_prompt to guide model behavior
        - Handle errors gracefully in calling functions
    """
    try:
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not available. Install with: pip install openai")
        
        # Get API key with proper error handling
        hf_api_key = get_huggingface_api_key(api_key)
        logger.info(f"🔑 Hugging Face API key loaded: {bool(hf_api_key)} (length: {len(hf_api_key) if hf_api_key else 0})")
        
        # Initialize Hugging Face client
        client = _get_hf_client(hf_api_key)
        logger.info("✅ Hugging Face client initialized for text response")

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
            "Hugging Face text call | model={} | prompt_len={} | temp={} | top_p={} | max_tokens={}",
            model,
            len(prompt) if isinstance(prompt, str) else '<non-str>',
            temperature,
            top_p,
            max_tokens,
        )
        
        logger.info("🚀 Making Hugging Face API call (chat completion)...")
        
        response = None
        last_error = None
        for candidate_model in _fallback_model_sequence(model, fallback_models):
            # Emit routing event for each model attempt
            route_intent = "primary" if candidate_model == model else "fallback"
            emit_routing_event(
                logger,
                flow_type="huggingface_text",
                route_intent=route_intent,
                provider_selected="huggingface",
                model_selected=candidate_model,
                tenant_user_id=tenant_user_id,
                extra={"original_model": model, "api_call": True}
            )
            
            try:
                response = client.chat.completions.create(
                    model=candidate_model,
                    messages=messages,
                    temperature=temperature,
                    top_p=top_p,
                    max_tokens=max_tokens
                )
                if candidate_model != model:
                    logger.warning("HF text fallback model used: {}", candidate_model)
                break
            except NotFoundError as nf_err:
                last_error = nf_err
                logger.warning("HF text model not found: {}", candidate_model)
                continue
            except Exception as call_err:
                last_error = call_err
                logger.warning("HF text call failed for model {}: {}", candidate_model, _error_details(call_err))
                continue

        if response is None:
            raise last_error or RuntimeError("All fallback models failed")
        
        # Extract text from response
        generated_text = response.choices[0].message.content or ""
        
        # Clean up the response
        generated_text = re.sub(r'```[a-zA-Z]*\n?', '', generated_text)
        generated_text = re.sub(r'```\n?', '', generated_text)
        generated_text = generated_text.strip()
        
        logger.info(f"✅ Hugging Face text response generated successfully (length: {len(generated_text)})")
        return generated_text
        
    except Exception as exc:
        details = _error_details(exc)
        logger.error(
            "❌ Hugging Face text generation failed | error_class={} | type={} | message={} | repr={}",
            _classify_hf_error(exc),
            details["type"],
            details["message"],
            details["repr"],
        )
        raise Exception(f"Hugging Face text generation failed: {exc}") from exc


@retry(
    retry=retry_if_exception(_should_retry_hf_error),
    wait=wait_random_exponential(min=1, max=60),
    stop=stop_after_attempt(6),
)
def huggingface_structured_json_response(
    prompt: str,
    schema: Dict[str, Any],
    model: str = PREMIUM_DEFAULT_MODEL,
    fallback_models: Optional[List[str]] = None,
    temperature: float = 0.7,
    max_tokens: int = 8192,
    system_prompt: Optional[str] = None,
    api_key: Optional[str] = None,
    tenant_user_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate structured JSON response using Hugging Face Inference Providers API.
    
    This function uses the Hugging Face Responses API with structured output support
    to generate JSON responses that match a provided schema.
    
    Args:
        prompt (str): The input prompt for the AI model
        schema (dict): JSON schema defining the expected output structure
        model (str): Hugging Face model identifier (default: PREMIUM_DEFAULT_MODEL)
        fallback_models (list, optional): Custom fallback models to try
        temperature (float): Controls randomness (0.0-1.0). Use 0.1-0.3 for structured output
        max_tokens (int): Maximum tokens in response. Use 8192 for complex outputs
        system_prompt (str, optional): System instruction for the model
        api_key (str, optional): Explicit API key override
    
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
    """
    try:
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not available. Install with: pip install openai")
        
        # Get API key with proper error handling
        hf_api_key = get_huggingface_api_key(api_key)
        logger.info(f"🔑 Hugging Face API key loaded: {bool(hf_api_key)} (length: {len(hf_api_key) if hf_api_key else 0})")
        
        # Initialize OpenAI client with Hugging Face base URL
        client = _get_hf_client(hf_api_key)
        logger.info("✅ Hugging Face client initialized for structured JSON response")

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
            "Hugging Face structured call | model={} | prompt_len={} | schema_kind={} | temp={} | max_tokens={}",
            model,
            len(prompt) if isinstance(prompt, str) else '<non-str>',
            type(schema).__name__,
            temperature,
            max_tokens,
        )
        
        logger.info("🚀 Making Hugging Face structured API call...")
        
        # Add JSON schema to prompt for guidance
        json_schema_str = json.dumps(schema, indent=2)
        messages[-1]["content"] += f"\n\nJSON Schema:\n{json_schema_str}"
        
        response = None
        last_error = None

        for candidate_model in _fallback_model_sequence(model, fallback_models):
            # Emit routing event for each model attempt
            route_intent = "primary" if candidate_model == model else "fallback"
            emit_routing_event(
                logger,
                flow_type="huggingface_structured",
                route_intent=route_intent,
                provider_selected="huggingface",
                model_selected=candidate_model,
                tenant_user_id=tenant_user_id,
                extra={"original_model": model, "api_call": True, "response_format": "json_object"}
            )
            
            try:
                response = client.chat.completions.create(
                    model=candidate_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    response_format={"type": "json_object"}
                )
                if candidate_model != model:
                    logger.warning("HF structured fallback model used: {}", candidate_model)
                break
            except Exception as err:
                last_error = err
                if isinstance(err, NotFoundError):
                    logger.warning("HF structured model not found: {}", candidate_model)
                    continue

                msg = str(err).lower()
                if "422" in msg or "not supported" in msg:
                    try:
                        response = client.chat.completions.create(
                            model=candidate_model,
                            messages=messages,
                            temperature=temperature,
                            max_tokens=max_tokens,
                        )
                        if candidate_model != model:
                            logger.warning("HF structured fallback(no response_format) model: {}", candidate_model)
                        break
                    except Exception as second_err:
                        last_error = second_err
                        continue

        if response is None:
            raise last_error or RuntimeError("All fallback models failed")
        
        response_text = (response.choices[0].message.content or "").strip()
        
        # Clean up response text if needed
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        try:
            parsed_json = json.loads(response_text)
            logger.info("✅ Hugging Face structured JSON response parsed successfully")
            return parsed_json
        except json.JSONDecodeError:
            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"error": "Failed to parse JSON response", "raw_response": response_text}
        
    except Exception as exc:
        details = _error_details(exc)
        logger.error(
            "❌ Hugging Face structured JSON generation failed | error_class={} | type={} | message={} | repr={}",
            _classify_hf_error(exc),
            details["type"],
            details["message"],
            details["repr"],
        )
        raise Exception(f"Hugging Face structured JSON generation failed: {exc}") from exc


def get_available_models() -> list:
    """
    Get list of available Hugging Face models for text generation.
    
    Returns:
        list: List of available model identifiers
    """
    return [
        PREMIUM_DEFAULT_MODEL,
        "moonshotai/Kimi-K2-Instruct-0905:groq",
        "Qwen/Qwen2.5-VL-7B-Instruct",
        "meta-llama/Llama-3.1-8B-Instruct:groq",
        "microsoft/Phi-3-medium-4k-instruct:groq",
        SIF_LOW_COST_MODEL_DEFAULTS[0]
    ]


def validate_model(model: str) -> bool:
    """
    Validate if a model identifier is supported.
    
    Args:
        model (str): Model identifier to validate
        
    Returns:
        bool: True if model is supported, False otherwise
    """
    available_models = get_available_models()
    return model in available_models
