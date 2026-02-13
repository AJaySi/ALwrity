"""Main Text Generation Service for ALwrity Backend.

This service provides the main LLM text generation functionality,
migrated from the legacy lib/gpt_providers/text_generation/main_text_generation.py
"""

import os
import json
from typing import Optional, Dict, Any
from datetime import datetime
from utils.logging import get_logger
logger = get_logger("main_text_generation_provider", migration_mode=True)
from fastapi import HTTPException
from ..onboarding.api_key_manager import APIKeyManager

from .gemini_provider import gemini_text_response, gemini_structured_json_response
from .huggingface_provider import huggingface_text_response, huggingface_structured_json_response


def llm_text_gen(prompt: str, system_prompt: Optional[str] = None, json_struct: Optional[Dict[str, Any]] = None, user_id: str = None) -> str:
    """
    Generate text using Language Model (LLM) based on the provided prompt.
    
    Args:
        prompt (str): The prompt to generate text from.
        system_prompt (str, optional): Custom system prompt to use instead of the default one.
        json_struct (dict, optional): JSON schema structure for structured responses.
        user_id (str): Clerk user ID for subscription checking (required).
        
    Returns:
        str: Generated text based on the prompt.
        
    Raises:
        RuntimeError: If subscription limits are exceeded or user_id is missing.
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

        # Map provider name to APIProvider enum (define at function scope for usage tracking)
        from models.subscription_models import APIProvider
        provider_enum = None
        # Store actual provider name for logging (e.g., "huggingface", "gemini")
        actual_provider_name = None
        if gpt_provider == "google":
            provider_enum = APIProvider.GEMINI
            actual_provider_name = "gemini"  # Use "gemini" for consistency in logs
        elif gpt_provider == "huggingface":
            provider_enum = APIProvider.MISTRAL  # HuggingFace maps to Mistral enum for usage tracking
            actual_provider_name = "huggingface"  # Keep actual provider name for logs
        
        if not provider_enum:
            raise RuntimeError(f"Unknown provider {gpt_provider} for subscription checking")

        # SUBSCRIPTION CHECK - Required and strict enforcement
        if not user_id:
            raise RuntimeError("user_id is required for subscription checking. Please provide Clerk user ID.")
        
        try:
            from services.database import get_session_for_user
            from services.subscription import UsageTrackingService, PricingService
            from models.subscription_models import UsageSummary
            
            db = get_session_for_user(user_id)
            if not db:
                 logger.error(f"[llm_text_gen] Could not get database session for user {user_id}")
                 raise RuntimeError("Database connection failed")
            try:
                
                usage_service = UsageTrackingService(db)
                pricing_service = PricingService(db)
                
                # Estimate tokens from prompt (input tokens)
                # CRITICAL: Use worst-case scenario (input + max_tokens) for validation to prevent abuse
                # This ensures we block requests that would exceed limits even if response is longer than expected
                input_tokens = int(len(prompt.split()) * 1.3)
                # Worst-case estimate: assume maximum possible output tokens (max_tokens if specified)
                # This prevents abuse where actual response tokens exceed the estimate
                if max_tokens:
                    estimated_output_tokens = max_tokens  # Use maximum allowed output tokens
                else:
                    # If max_tokens not specified, use conservative estimate (input * 1.5)
                    estimated_output_tokens = int(input_tokens * 1.5)
                estimated_total_tokens = input_tokens + estimated_output_tokens
                
                # Check limits using sync method from pricing service (strict enforcement)
                can_proceed, message, usage_info = pricing_service.check_usage_limits(
                    user_id=user_id,
                    provider=provider_enum,
                    tokens_requested=estimated_total_tokens,
                    actual_provider_name=actual_provider_name  # Pass actual provider name for correct error messages
                )
                
                if not can_proceed:
                    logger.warning(f"[llm_text_gen] Subscription limit exceeded for user {user_id}: {message}")
                    # Raise HTTPException(429) with usage info so frontend can display subscription modal
                    error_detail = {
                        'error': message,
                        'message': message,
                        'provider': actual_provider_name or provider_enum.value,
                        'usage_info': usage_info if usage_info else {}
                    }
                    raise HTTPException(status_code=429, detail=error_detail)
                
                # Get current usage for limit checking only
                current_period = pricing_service.get_current_billing_period(user_id) or datetime.now().strftime("%Y-%m")
                usage = db.query(UsageSummary).filter(
                    UsageSummary.user_id == user_id,
                    UsageSummary.billing_period == current_period
                ).first()
                
                # No separate log here - we'll create unified log after API call and usage tracking
                
            finally:
                db.close()
        except HTTPException:
            # Re-raise HTTPExceptions (e.g., 429 subscription limit) - preserve error details
            raise
        except RuntimeError:
            # Re-raise subscription limit errors
            raise
        except Exception as sub_error:
            # STRICT: Fail on subscription check errors
            logger.error(f"[llm_text_gen] Subscription check failed for user {user_id}: {sub_error}")
            raise RuntimeError(f"Subscription check failed: {str(sub_error)}")

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
        response_text = None
        actual_provider_used = gpt_provider
        try:
            if gpt_provider == "google":
                if json_struct:
                    response_text = gemini_structured_json_response(
                        prompt=prompt,
                        schema=json_struct,
                        temperature=temperature,
                        top_p=top_p,
                        top_k=n,
                        max_tokens=max_tokens,
                        system_prompt=system_instructions
                    )
                else:
                    response_text = gemini_text_response(
                        prompt=prompt,
                        temperature=temperature,
                        top_p=top_p,
                        n=n,
                        max_tokens=max_tokens,
                        system_prompt=system_instructions
                    )
            elif gpt_provider == "huggingface":
                if json_struct:
                    response_text = huggingface_structured_json_response(
                        prompt=prompt,
                        schema=json_struct,
                        model=model,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        system_prompt=system_instructions
                    )
                else:
                    response_text = huggingface_text_response(
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
            
            # TRACK USAGE after successful API call
            if response_text:
                logger.info(f"[llm_text_gen] ✅ API call successful, tracking usage for user {user_id}, provider {provider_enum.value}")
                try:
                    from services.intelligence.agents.agent_usage_tracking import track_agent_usage_sync
                    
                    # Estimate tokens
                    tokens_input = int(len(prompt.split()) * 1.3)
                    
                    # Calculate duration (mocking it since we didn't track start time explicitly in this function)
                    # Ideally we should track start_time at beginning of function
                    duration = 0.5 
                    
                    track_agent_usage_sync(
                        user_id=user_id,
                        model_name=model,
                        prompt=prompt,
                        response_text=response_text,
                        duration=duration
                    )
                    
                except Exception as usage_error:
                    # Non-blocking: log error but don't fail the request
                    logger.error(f"[llm_text_gen] ❌ Failed to track usage: {usage_error}", exc_info=True)
            
            return response_text
        except Exception as provider_error:
            logger.error(f"[llm_text_gen] Provider {gpt_provider} failed: {str(provider_error)}")
            
            # CIRCUIT BREAKER: Only try ONE fallback to prevent expensive API calls
            fallback_providers = ["google", "huggingface"]
            fallback_providers = [p for p in fallback_providers if p in available_providers and p != gpt_provider]
            
            if fallback_providers:
                fallback_provider = fallback_providers[0]  # Only try the first available
                try:
                    logger.info(f"[llm_text_gen] Trying SINGLE fallback provider: {fallback_provider}")
                    actual_provider_used = fallback_provider
                    
                    # Update provider enum for fallback
                    if fallback_provider == "google":
                        provider_enum = APIProvider.GEMINI
                        actual_provider_name = "gemini"
                        fallback_model = "gemini-2.0-flash-lite"
                    elif fallback_provider == "huggingface":
                        provider_enum = APIProvider.MISTRAL
                        actual_provider_name = "huggingface"
                        fallback_model = "openai/gpt-oss-120b:groq"
                    
                    if fallback_provider == "google":
                        if json_struct:
                            response_text = gemini_structured_json_response(
                                prompt=prompt,
                                schema=json_struct,
                                temperature=temperature,
                                top_p=top_p,
                                top_k=n,
                                max_tokens=max_tokens,
                                system_prompt=system_instructions
                            )
                        else:
                            response_text = gemini_text_response(
                                prompt=prompt,
                                temperature=temperature,
                                top_p=top_p,
                                n=n,
                                max_tokens=max_tokens,
                                system_prompt=system_instructions
                            )
                    elif fallback_provider == "huggingface":
                        if json_struct:
                            response_text = huggingface_structured_json_response(
                                prompt=prompt,
                                schema=json_struct,
                                model="openai/gpt-oss-120b:groq",
                                temperature=temperature,
                                max_tokens=max_tokens,
                                system_prompt=system_instructions
                            )
                        else:
                            response_text = huggingface_text_response(
                                prompt=prompt,
                                model="openai/gpt-oss-120b:groq",
                                temperature=temperature,
                                max_tokens=max_tokens,
                                top_p=top_p,
                                system_prompt=system_instructions
                            )
                    
                    # TRACK USAGE after successful fallback call
                    if response_text:
                        logger.info(f"[llm_text_gen] ✅ Fallback API call successful, tracking usage for user {user_id}, provider {provider_enum.value}")
                        try:
                            from services.intelligence.agents.agent_usage_tracking import track_agent_usage_sync
                            
                            # Estimate tokens
                            tokens_input = int(len(prompt.split()) * 1.3)
                            
                            track_agent_usage_sync(
                                user_id=user_id,
                                model_name=fallback_model,
                                prompt=prompt,
                                response_text=response_text,
                                duration=0.5 # Approximate duration
                            )
                        except Exception as usage_error:
                            logger.error(f"[llm_text_gen] ❌ Failed to track fallback usage: {usage_error}", exc_info=True)
                    
                    return response_text
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