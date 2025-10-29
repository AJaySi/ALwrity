"""Main Text Generation Service for ALwrity Backend.

This service provides the main LLM text generation functionality,
migrated from the legacy lib/gpt_providers/text_generation/main_text_generation.py
"""

import os
import json
from typing import Optional, Dict, Any
from loguru import logger
from ..onboarding.api_key_manager import APIKeyManager

from .gemini_provider import gemini_text_response, gemini_structured_json_response
from .huggingface_provider import huggingface_text_response, huggingface_structured_json_response


def llm_text_gen(prompt: str, system_prompt: Optional[str] = None, json_struct: Optional[Dict[str, Any]] = None) -> str:
    """
    Generate text using Language Model (LLM) based on the provided prompt.
    
    Args:
        prompt (str): The prompt to generate text from.
        system_prompt (str, optional): Custom system prompt to use instead of the default one.
        json_struct (dict, optional): JSON schema structure for structured responses.
        
    Returns:
        str: Generated text based on the prompt.
    """
    try:
        logger.info("[llm_text_gen] Starting text generation")
        logger.debug(f"[llm_text_gen] Prompt length: {len(prompt)} characters")
        
        # Set default values for LLM parameters
        gpt_provider = "google"  # Default to Google Gemini
        model = "gemini-2.0-flash-001"
        temperature = 0.7
        max_tokens = 4000
        top_p = 0.9
        n = 1
        fp = 16
        frequency_penalty = 0.0
        presence_penalty = 0.0
        
        # Check for GPT_PROVIDER environment variable
        env_provider = os.getenv('GPT_PROVIDER', '').lower()
        if env_provider in ['gemini', 'google']:
            gpt_provider = "google"
            model = "gemini-2.0-flash-001"
        elif env_provider in ['hf_response_api', 'huggingface', 'hf']:
            gpt_provider = "huggingface"
            model = "openai/gpt-oss-120b:groq"
        
        # Default blog characteristics
        blog_tone = "Professional"
        blog_demographic = "Professional"
        blog_type = "Informational"
        blog_language = "English"
        blog_output_format = "markdown"
        blog_length = 2000
        
        # Check which providers have API keys available using APIKeyManager
        api_key_manager = APIKeyManager()
        available_providers = []
        if api_key_manager.get_api_key("gemini"):
            available_providers.append("google")
        if api_key_manager.get_api_key("hf_token"):
            available_providers.append("huggingface")
        
        # If no environment variable set, auto-detect based on available keys
        if not env_provider:
            # Prefer Google Gemini if available, otherwise use Hugging Face
            if "google" in available_providers:
                gpt_provider = "google"
                model = "gemini-2.0-flash-001"
            elif "huggingface" in available_providers:
                gpt_provider = "huggingface"
                model = "openai/gpt-oss-120b:groq"
            else:
                logger.error("[llm_text_gen] No API keys found for supported providers.")
                raise RuntimeError("No LLM API keys configured. Configure GEMINI_API_KEY or HF_TOKEN to enable AI responses.")
        else:
            # Environment variable was set, validate it's supported
            if gpt_provider not in available_providers:
                logger.warning(f"[llm_text_gen] Provider {gpt_provider} not available, falling back to available providers")
                if "google" in available_providers:
                    gpt_provider = "google"
                    model = "gemini-2.0-flash-001"
                elif "huggingface" in available_providers:
                    gpt_provider = "huggingface"
                    model = "openai/gpt-oss-120b:groq"
                else:
                    raise RuntimeError("No supported providers available.")
            
        logger.debug(f"[llm_text_gen] Using provider: {gpt_provider}, model: {model}")

        # Construct the system prompt if not provided
        if system_prompt is None:
            system_instructions = f"""You are a highly skilled content writer with a knack for creating engaging and informative content. 
                Your expertise spans various writing styles and formats.

                Writing Style Guidelines:
                - Tone: {blog_tone}
                - Target Audience: {blog_demographic}
                - Content Type: {blog_type}
                - Language: {blog_language}
                - Output Format: {blog_output_format}
                - Target Length: {blog_length} words

                Please provide responses that are:
                - Well-structured and easy to read
                - Engaging and informative
                - Tailored to the specified tone and audience
                - Professional yet accessible
                - Optimized for the target content type
            """
        else:
            system_instructions = system_prompt

        # Generate response based on provider
        try:
            if gpt_provider == "google":
                if json_struct:
                    return gemini_structured_json_response(
                        prompt=prompt,
                        schema=json_struct,
                        temperature=temperature,
                        top_p=top_p,
                        top_k=n,
                        max_tokens=max_tokens,
                        system_prompt=system_instructions
                    )
                else:
                    return gemini_text_response(
                        prompt=prompt,
                        temperature=temperature,
                        top_p=top_p,
                        n=n,
                        max_tokens=max_tokens,
                        system_prompt=system_instructions
                    )
            elif gpt_provider == "huggingface":
                if json_struct:
                    return huggingface_structured_json_response(
                        prompt=prompt,
                        schema=json_struct,
                        model=model,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        system_prompt=system_instructions
                    )
                else:
                    return huggingface_text_response(
                        prompt=prompt,
                        model=model,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        top_p=top_p,
                        system_prompt=system_instructions
                    )
            else:
                logger.error(f"[llm_text_gen] Unknown provider: {gpt_provider}")
                raise RuntimeError("Unknown LLM provider. Supported providers: google, huggingface")
        except Exception as provider_error:
            logger.error(f"[llm_text_gen] Provider {gpt_provider} failed: {str(provider_error)}")
            
            # CIRCUIT BREAKER: Only try ONE fallback to prevent expensive API calls
            fallback_providers = ["google", "huggingface"]
            fallback_providers = [p for p in fallback_providers if p in available_providers and p != gpt_provider]
            
            if fallback_providers:
                fallback_provider = fallback_providers[0]  # Only try the first available
                try:
                    logger.info(f"[llm_text_gen] Trying SINGLE fallback provider: {fallback_provider}")
                    if fallback_provider == "google":
                        if json_struct:
                            return gemini_structured_json_response(
                                prompt=prompt,
                                schema=json_struct,
                                temperature=temperature,
                                top_p=top_p,
                                top_k=n,
                                max_tokens=max_tokens,
                                system_prompt=system_instructions
                            )
                        else:
                            return gemini_text_response(
                                prompt=prompt,
                                temperature=temperature,
                                top_p=top_p,
                                n=n,
                                max_tokens=max_tokens,
                                system_prompt=system_instructions
                            )
                    elif fallback_provider == "huggingface":
                        if json_struct:
                            return huggingface_structured_json_response(
                                prompt=prompt,
                                schema=json_struct,
                                model="openai/gpt-oss-120b:groq",
                                temperature=temperature,
                                max_tokens=max_tokens,
                                system_prompt=system_instructions
                            )
                        else:
                            return huggingface_text_response(
                                prompt=prompt,
                                model="openai/gpt-oss-120b:groq",
                                temperature=temperature,
                                max_tokens=max_tokens,
                                top_p=top_p,
                                system_prompt=system_instructions
                            )
                except Exception as fallback_error:
                    logger.error(f"[llm_text_gen] Fallback provider {fallback_provider} also failed: {str(fallback_error)}")
            
            # CIRCUIT BREAKER: Stop immediately to prevent expensive API calls
            logger.error("[llm_text_gen] CIRCUIT BREAKER: Stopping to prevent expensive API calls.")
            raise RuntimeError("All LLM providers failed to generate a response.")

    except Exception as e:
        logger.error(f"[llm_text_gen] Error during text generation: {str(e)}")
        raise

def check_gpt_provider(gpt_provider: str) -> bool:
    """Check if the specified GPT provider is supported."""
    supported_providers = ["google", "huggingface"]
    return gpt_provider in supported_providers

def get_api_key(gpt_provider: str) -> Optional[str]:
    """Get API key for the specified provider."""
    try:
        api_key_manager = APIKeyManager()
        provider_mapping = {
            "google": "gemini",
            "huggingface": "hf_token"
        }
        
        mapped_provider = provider_mapping.get(gpt_provider, gpt_provider)
        return api_key_manager.get_api_key(mapped_provider)
    except Exception as e:
        logger.error(f"[get_api_key] Error getting API key for {gpt_provider}: {str(e)}")
        return None 