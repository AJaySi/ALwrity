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
import sys
from pathlib import Path
import json
import re
from typing import Optional, Dict, Any

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
logger = get_service_logger("huggingface_provider")

from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warn("OpenAI library not available. Install with: pip install openai")

def get_huggingface_api_key() -> str:
    """Get Hugging Face API key with proper error handling."""
    api_key = os.getenv('HF_TOKEN')
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

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def huggingface_text_response(
    prompt: str,
    model: str = "openai/gpt-oss-120b:groq",
    temperature: float = 0.7,
    max_tokens: int = 2048,
    top_p: float = 0.9,
    system_prompt: Optional[str] = None
) -> str:
    """
    Generate text response using Hugging Face Inference Providers API.
    
    This function uses the Hugging Face Responses API which provides a unified interface
    for model interactions with built-in retry logic and error handling.
    
    Args:
        prompt (str): The input prompt for the AI model
        model (str): Hugging Face model identifier (default: "openai/gpt-oss-120b:groq")
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
        result = huggingface_text_response(
            prompt="Write a blog post about AI",
            model="openai/gpt-oss-120b:groq",
            temperature=0.7,
            max_tokens=2048,
            system_prompt="You are a professional content writer."
        )
    """
    try:
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not available. Install with: pip install openai")
        
        # Get API key with proper error handling
        api_key = get_huggingface_api_key()
        logger.info(f"🔑 Hugging Face API key loaded: {bool(api_key)} (length: {len(api_key) if api_key else 0})")
        
        if not api_key:
            raise Exception("HF_TOKEN not found in environment variables")
            
        # Initialize Hugging Face client using Responses API
        client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=api_key,
        )
        logger.info("✅ Hugging Face client initialized for text response")

        # Prepare input for the API
        input_content = []
        
        # Add system prompt if provided
        if system_prompt:
            input_content.append({
                "role": "system",
                "content": system_prompt
            })
        
        # Add user prompt
        input_content.append({
            "role": "user", 
            "content": prompt
        })

        # Add debugging for API call
        logger.info(
            "Hugging Face text call | model=%s | prompt_len=%s | temp=%s | top_p=%s | max_tokens=%s",
            model,
            len(prompt) if isinstance(prompt, str) else '<non-str>',
            temperature,
            top_p,
            max_tokens,
        )
        
        logger.info("🚀 Making Hugging Face API call...")
        
        # Add rate limiting to prevent expensive API calls
        import time
        time.sleep(1)  # 1 second delay between API calls
        
        # Make the API call using Responses API
        response = client.responses.parse(
            model=model,
            input=input_content,
            temperature=temperature,
            top_p=top_p,
        )
        
        # Extract text from response
        if hasattr(response, 'output_text') and response.output_text:
            generated_text = response.output_text
        elif hasattr(response, 'output') and response.output:
            # Handle case where output is a list
            if isinstance(response.output, list) and len(response.output) > 0:
                generated_text = response.output[0].get('content', '')
            else:
                generated_text = str(response.output)
        else:
            generated_text = str(response)
        
        # Clean up the response
        if generated_text:
            # Remove any markdown formatting if present
            generated_text = re.sub(r'```[a-zA-Z]*\n?', '', generated_text)
            generated_text = re.sub(r'```\n?', '', generated_text)
            generated_text = generated_text.strip()
        
        logger.info(f"✅ Hugging Face text response generated successfully (length: {len(generated_text)})")
        return generated_text
        
    except Exception as e:
        logger.error(f"❌ Hugging Face text generation failed: {str(e)}")
        raise Exception(f"Hugging Face text generation failed: {str(e)}")

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def huggingface_structured_json_response(
    prompt: str,
    schema: Dict[str, Any],
    model: str = "openai/gpt-oss-120b:groq",
    temperature: float = 0.7,
    max_tokens: int = 8192,
    system_prompt: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate structured JSON response using Hugging Face Inference Providers API.
    
    This function uses the Hugging Face Responses API with structured output support
    to generate JSON responses that match a provided schema.
    
    Args:
        prompt (str): The input prompt for the AI model
        schema (dict): JSON schema defining the expected output structure
        model (str): Hugging Face model identifier (default: "openai/gpt-oss-120b:groq")
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
        result = huggingface_structured_json_response(prompt, schema, temperature=0.2, max_tokens=8192)
    """
    try:
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not available. Install with: pip install openai")
        
        # Get API key with proper error handling
        api_key = get_huggingface_api_key()
        logger.info(f"🔑 Hugging Face API key loaded: {bool(api_key)} (length: {len(api_key) if api_key else 0})")
        
        if not api_key:
            raise Exception("HF_TOKEN not found in environment variables")
            
        # Initialize Hugging Face client using Responses API
        client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=api_key,
        )
        logger.info("✅ Hugging Face client initialized for structured JSON response")

        # Prepare input for the API
        input_content = []
        
        # Add system prompt if provided
        if system_prompt:
            input_content.append({
                "role": "system",
                "content": system_prompt
            })
        
        # Add user prompt with JSON instruction
        json_instruction = "Please respond with valid JSON that matches the provided schema."
        input_content.append({
            "role": "user", 
            "content": f"{prompt}\n\n{json_instruction}"
        })

        # Add debugging for API call
        logger.info(
            "Hugging Face structured call | model=%s | prompt_len=%s | schema_kind=%s | temp=%s | max_tokens=%s",
            model,
            len(prompt) if isinstance(prompt, str) else '<non-str>',
            type(schema).__name__,
            temperature,
            max_tokens,
        )
        
        logger.info("🚀 Making Hugging Face structured API call...")
        
        # Make the API call using Responses API with structured output
        # Use simple text generation and parse JSON manually to avoid API format issues
        logger.info("🚀 Making Hugging Face API call (text mode with JSON parsing)...")
        
        # Add JSON instruction to the prompt
        json_instruction = "\n\nPlease respond with valid JSON that matches this exact structure:\n" + json.dumps(schema, indent=2)
        input_content[-1]["content"] = input_content[-1]["content"] + json_instruction
        
        # Add rate limiting to prevent expensive API calls
        import time
        time.sleep(1)  # 1 second delay between API calls
        
        response = client.responses.parse(
            model=model,
            input=input_content,
            temperature=temperature
        )
        
        # Extract structured data from response
        if hasattr(response, 'output_parsed') and response.output_parsed:
            # The new API returns parsed data directly (Pydantic model case)
            logger.info("✅ Hugging Face structured JSON response parsed successfully")
            # Convert Pydantic model to dict if needed
            if hasattr(response.output_parsed, 'model_dump'):
                return response.output_parsed.model_dump()
            elif hasattr(response.output_parsed, 'dict'):
                return response.output_parsed.dict()
            else:
                return response.output_parsed
        elif hasattr(response, 'output_text') and response.output_text:
            # Fallback to text parsing if output_parsed is not available
            response_text = response.output_text
            # Clean up the response text
            response_text = re.sub(r'```json\n?', '', response_text)
            response_text = re.sub(r'```\n?', '', response_text)
            response_text = response_text.strip()
            
            # Fix common markdown artefacts that break JSON, e.g. lines starting with **"key":
            #     **"narration": "text"
            # becomes:
            #     "narration": "text"
            response_text = re.sub(r'^\s*\*\*(?=\s*")', '', response_text, flags=re.MULTILINE)
            
            try:
                parsed_json = json.loads(response_text)
                logger.info("✅ Hugging Face structured JSON response parsed from text")
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
                
                # If all else fails, return a structured error response
                logger.error("❌ All JSON parsing attempts failed")
                return {
                    "error": "Failed to parse JSON response",
                    "raw_response": response_text,
                    "schema_expected": schema
                }
        else:
            logger.error("❌ No valid response data found")
            return {
                "error": "No valid response data found",
                "raw_response": str(response),
                "schema_expected": schema
            }
        
    except Exception as e:
        error_msg = str(e) if str(e) else repr(e)
        error_type = type(e).__name__
        logger.error(f"❌ Hugging Face structured JSON generation failed: {error_type}: {error_msg}")
        logger.error(f"❌ Full exception details: {repr(e)}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        raise Exception(f"Hugging Face structured JSON generation failed: {error_type}: {error_msg}")

def get_available_models() -> list:
    """
    Get list of available Hugging Face models for text generation.
    
    Returns:
        list: List of available model identifiers
    """
    return [
        "openai/gpt-oss-120b:groq",
        "moonshotai/Kimi-K2-Instruct-0905:groq",
        "Qwen/Qwen2.5-VL-7B-Instruct",
        "meta-llama/Llama-3.1-8B-Instruct:groq",
        "microsoft/Phi-3-medium-4k-instruct:groq",
        "mistralai/Mistral-7B-Instruct-v0.3:groq"
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
