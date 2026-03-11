"""Main Text Generation Service for ALwrity Backend.

This service provides the main LLM text generation functionality,
migrated from the legacy lib/gpt_providers/text_generation/main_text_generation.py
"""

import os
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from loguru import logger
from fastapi import HTTPException
from ..onboarding.api_key_manager import APIKeyManager

from .gemini_provider import gemini_text_response, gemini_structured_json_response
from .huggingface_provider import huggingface_text_response, huggingface_structured_json_response


def llm_text_gen(
    prompt: str,
    system_prompt: Optional[str] = None,
    json_struct: Optional[Dict[str, Any]] = None,
    user_id: str = None,
    preferred_hf_models: Optional[List[str]] = None,
    preferred_provider: Optional[str] = None,
    flow_type: Optional[str] = None,
) -> str:
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
        resolved_flow_type = flow_type or ("sif_agent" if preferred_hf_models else "premium_tool")
        flow_tag = f"flow_type={resolved_flow_type}"
        subscription_preflight_completed = False

        logger.info(f"[llm_text_gen][{flow_tag}] Starting text generation")
        logger.debug(f"[llm_text_gen] Prompt length: {len(prompt)} characters")
        
        # Set default values for LLM parameters
        gpt_provider = "huggingface"  # Default to premium HF route for ALwrity AI tools
        model = "openai/gpt-oss-120b:cerebras"
        temperature = 0.7
        max_tokens = 4000
        top_p = 0.9
        n = 1
        fp = 16
        frequency_penalty = 0.0
        presence_penalty = 0.0
        
        # Check for GPT_PROVIDER environment variable
        env_provider = os.getenv('GPT_PROVIDER', '').lower()
        provider_list = [p.strip() for p in env_provider.split(',') if p.strip()]
        
        # Determine if we're in strict mode (single provider) or fallback mode (multiple providers)
        strict_provider_mode = len(provider_list) == 1
        
        if provider_list:
            # Use first provider as primary
            primary_provider = provider_list[0]
            if primary_provider in ['gemini', 'google']:
                gpt_provider = "google"
                model = "gemini-2.0-flash-001"
            elif primary_provider in ['hf_response_api', 'huggingface', 'hf']:
                gpt_provider = "huggingface"
                model = "openai/gpt-oss-120b:cerebras"
            elif primary_provider == 'wavespeed':
                gpt_provider = "wavespeed"
                model = "openai/gpt-oss-120b"
        else:
            # Auto-detect mode
            strict_provider_mode = False  # Auto-detect allows fallbacks
            gpt_provider = None
            model = None

        # Explicit per-call provider override (used by tool-specific flows like podcast maker)
        if preferred_provider:
            preferred_providers = [p.strip() for p in preferred_provider.split(',') if p.strip()]
            # If explicit provider is set, it's strict mode (no cross-provider fallbacks)
            strict_provider_mode = len(preferred_providers) == 1
            
            primary_provider = preferred_providers[0]
            if primary_provider in ['gemini', 'google']:
                gpt_provider = "google"
                model = "gemini-2.0-flash-001"
            elif primary_provider in ['hf_response_api', 'huggingface', 'hf']:
                gpt_provider = "huggingface"
                model = "openai/gpt-oss-120b:cerebras"
            elif primary_provider == 'wavespeed':
                gpt_provider = "wavespeed"
                model = "openai/gpt-oss-120b"
        
        # Handle TEXTGEN_AI_MODELS for model selection
        textgen_models_env = os.getenv('TEXTGEN_AI_MODELS', '').strip()
        model_list = [m.strip() for m in textgen_models_env.split(',') if m.strip()] if textgen_models_env else []
        strict_model_mode = len(model_list) == 1
        
        # Map model names to actual provider models
        if model_list:
            if gpt_provider == "huggingface":
                # Handle both short names and full model names
                model_mapping = {
                    "gpt-oss": "openai/gpt-oss-120b:cerebras",
                    "gpt-oss-120b": "openai/gpt-oss-120b:cerebras",
                    "mistral": "mistralai/Mistral-7B-Instruct-v0.3:cerebras",
                    "mistral-7b": "mistralai/Mistral-7B-Instruct-v0.3:cerebras",
                    "llama": "meta-llama/Llama-3.1-8B-Instruct:cerebras",
                    "llama-8b": "meta-llama/Llama-3.1-8B-Instruct:cerebras",
                    "llama-70b": "meta-llama/Llama-3.1-70B-Instruct:cerebras"
                }
                # If model name contains "/", assume it's already a full model name
                if "/" in model_list[0]:
                    model = model_list[0]
                else:
                    model = model_mapping.get(model_list[0], model_list[0])
            elif gpt_provider == "wavespeed":
                # Handle both short names and full model names
                model_mapping = {
                    "gpt-oss": "openai/gpt-oss-120b",
                    "gpt-oss-120b": "openai/gpt-oss-120b",
                    "mistral": "mistralai/Mistral-7B-Instruct-v0.3",
                    "mistral-7b": "mistralai/Mistral-7B-Instruct-v0.3",
                    "llama": "meta-llama/Llama-3.1-8B-Instruct",
                    "llama-8b": "meta-llama/Llama-3.1-8B-Instruct",
                    "llama-70b": "meta-llama/Llama-3.1-70B-Instruct"
                }
                # If model name contains "/", assume it's already a full model name
                if "/" in model_list[0]:
                    model = model_list[0]
                else:
                    model = model_mapping.get(model_list[0], model_list[0])
            elif gpt_provider == "google":
                model = "gemini-2.0-flash-001"  # Google has fewer options
        
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
        if api_key_manager.get_api_key("wavespeed"):
            available_providers.append("wavespeed")
        logger.info(
            f"[llm_text_gen][{flow_tag}] Provider preflight: env_provider='{env_provider or 'auto'}', "
            f"provider_list={provider_list}, strict_provider_mode={strict_provider_mode}, "
            f"available_providers={available_providers}, preferred_provider={preferred_provider or 'none'}"
        )
        
        if model_list:
            logger.info(
                f"[llm_text_gen][{flow_tag}] Model configuration: model_list={model_list}, "
                f"strict_model_mode={strict_model_mode}"
            )
        
        # If no environment variable set, auto-detect based on available keys
        if not env_provider:
            # Prefer Google Gemini if available, otherwise use Hugging Face
            if preferred_provider:
                # Respect explicit per-call preference if the provider key exists
                if gpt_provider not in available_providers:
                    logger.warning(
                        f"[llm_text_gen] Preferred provider {gpt_provider} unavailable, falling back to available providers"
                    )
                    if "huggingface" in available_providers:
                        gpt_provider = "huggingface"
                        model = "openai/gpt-oss-120b:cerebras"
                    elif "wavespeed" in available_providers:
                        gpt_provider = "wavespeed"
                        model = "openai/gpt-oss-120b"
                    elif "google" in available_providers:
                        gpt_provider = "google"
                        model = "gemini-2.0-flash-001"
                    else:
                        logger.error("[llm_text_gen] No API keys found for supported providers.")
                        raise RuntimeError("No LLM API keys configured. Configure GEMINI_API_KEY or HF_TOKEN to enable AI responses.")
            elif preferred_hf_models and "huggingface" in available_providers:
                # Low-cost SIF/agent flows pass preferred_hf_models; route directly to HF.
                gpt_provider = "huggingface"
                model = preferred_hf_models[0]
                logger.info(f"[llm_text_gen] Using preferred low-cost HF model: {model}")
            elif "google" in available_providers:
                gpt_provider = "google"
                model = "gemini-2.0-flash-001"
            elif "huggingface" in available_providers:
                gpt_provider = "huggingface"
                model = "openai/gpt-oss-120b:cerebras"
            elif "wavespeed" in available_providers:
                gpt_provider = "wavespeed"
                model = "openai/gpt-oss-120b"
            else:
                logger.error("[llm_text_gen] No API keys found for supported providers.")
                raise RuntimeError("No LLM API keys configured. Configure GEMINI_API_KEY or HF_TOKEN to enable AI responses.")
        else:
            # Environment variable was set, validate it's supported
            if gpt_provider not in available_providers:
                if strict_provider_mode:
                    # Strict mode: fail if specified provider not available
                    raise RuntimeError(f"Provider {gpt_provider} not available. Available: {available_providers}")
                else:
                    # Fallback mode: try other providers
                    logger.warning(f"[llm_text_gen] Provider {gpt_provider} not available, falling back to available providers")
                    if "google" in available_providers:
                        gpt_provider = "google"
                        model = "gemini-2.0-flash-001"
                    elif "huggingface" in available_providers:
                        gpt_provider = "huggingface"
                        model = "openai/gpt-oss-120b:cerebras"
                    elif "wavespeed" in available_providers:
                        gpt_provider = "wavespeed"
                        model = "openai/gpt-oss-120b"
                    else:
                        raise RuntimeError("No supported providers available.")

        if gpt_provider == "huggingface" and preferred_hf_models:
            model = preferred_hf_models[0]
            logger.info(f"[llm_text_gen] Using preferred low-cost HF model: {model}")
            
        logger.info(f"[llm_text_gen][{flow_tag}] Using provider={gpt_provider}, model={model}")

        # Map provider name to APIProvider enum (define at function scope for usage tracking)
        from models.subscription_models import APIProvider
        provider_enum = None
        # Store actual provider name for logging (e.g., "huggingface", "gemini", "wavespeed")
        actual_provider_name = None
        if gpt_provider == "google":
            provider_enum = APIProvider.GEMINI
            actual_provider_name = "gemini"  # Use "gemini" for consistency in logs
        elif gpt_provider == "huggingface":
            provider_enum = APIProvider.MISTRAL  # HuggingFace maps to Mistral enum for usage tracking
            actual_provider_name = "huggingface"  # Keep actual provider name for logs
        elif gpt_provider == "wavespeed":
            provider_enum = APIProvider.WAVESPEED
            actual_provider_name = "wavespeed"
        
        if not provider_enum:
            raise RuntimeError(f"Unknown provider {gpt_provider} for subscription checking")

        # SUBSCRIPTION CHECK - Required and strict enforcement
        if not user_id:
            raise RuntimeError("user_id is required for subscription checking. Please provide Clerk user ID.")
        
        try:
            from services.database import get_session_for_user
            from services.subscription import UsageTrackingService, PricingService
            from models.subscription_models import UsageSummary

            logger.info(
                f"[llm_text_gen][{flow_tag}] Starting subscription preflight for user={user_id}, "
                f"provider={actual_provider_name}, model={model}"
            )
            
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
                subscription_preflight_completed = True

                logger.info(
                    f"[llm_text_gen][{flow_tag}] Subscription preflight complete: can_proceed={can_proceed}, "
                    f"estimated_tokens={estimated_total_tokens}, provider={actual_provider_name}"
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

        # HF behavior: fail fast on selected model; no intra-provider model fallback chain.
        hf_fallback_models: List[str] = []
        
        # Set up model fallbacks based on strict_model_mode
        if not strict_model_mode and model_list and len(model_list) > 1:
            # Multi-model mode: create fallback list from TEXTGEN_AI_MODELS
            if gpt_provider == "huggingface":
                model_mapping = {
                    "gpt-oss": "openai/gpt-oss-120b:cerebras",
                    "gpt-oss-120b": "openai/gpt-oss-120b:cerebras",
                    "mistral": "mistralai/Mistral-7B-Instruct-v0.3:cerebras",
                    "mistral-7b": "mistralai/Mistral-7B-Instruct-v0.3:cerebras",
                    "llama": "meta-llama/Llama-3.1-8B-Instruct:cerebras",
                    "llama-8b": "meta-llama/Llama-3.1-8B-Instruct:cerebras",
                    "llama-70b": "meta-llama/Llama-3.1-70B-Instruct:cerebras"
                }
                hf_fallback_models = []
                for model_name in model_list[1:]:
                    if "/" in model_name:
                        # Full model name, use as-is
                        hf_fallback_models.append(model_name)
                    else:
                        # Short name, map it
                        mapped_model = model_mapping.get(model_name, model_name)
                        hf_fallback_models.append(mapped_model)

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
                        fallback_models=hf_fallback_models,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        system_prompt=system_instructions
                    )
                else:
                    response_text = huggingface_text_response(
                        prompt=prompt,
                        model=model,
                        fallback_models=hf_fallback_models,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        top_p=top_p,
                        system_prompt=system_instructions
                    )
            elif gpt_provider == "wavespeed":
                from .wavespeed_provider import wavespeed_text_response, wavespeed_structured_json_response
                if json_struct:
                    response_text = wavespeed_structured_json_response(
                        prompt=prompt,
                        schema=json_struct,
                        model=model,
                        fallback_models=None,  # No fallbacks for WaveSpeed initially
                        temperature=temperature,
                        max_tokens=max_tokens,
                        system_prompt=system_instructions
                    )
                else:
                    response_text = wavespeed_text_response(
                        prompt=prompt,
                        model=model,
                        fallback_models=None,  # No fallbacks for WaveSpeed initially
                        temperature=temperature,
                        max_tokens=max_tokens,
                        top_p=top_p,
                        system_prompt=system_instructions
                    )
            else:
                logger.error(f"[llm_text_gen] Unknown provider: {gpt_provider}")
                raise RuntimeError("Unknown LLM provider. Supported providers: google, huggingface, wavespeed")
            
            # TRACK USAGE after successful API call
            if response_text:
                logger.info(
                    f"[llm_text_gen][{flow_tag}] ✅ API call successful, tracking usage for user {user_id}, provider {provider_enum.value}"
                )
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
            logger.error(
                f"[llm_text_gen][{flow_tag}] Provider {gpt_provider} failed: {str(provider_error)} | "
                f"subscription_preflight_completed={subscription_preflight_completed} | model={model}"
            )
            
            # CIRCUIT BREAKER: Only try ONE fallback to prevent expensive API calls
            # Use provider list from environment if available, otherwise default
            if provider_list and len(provider_list) > 1:
                # Use the specified fallback providers from GPT_PROVIDER
                fallback_providers = provider_list[1:]  # Skip the primary (already tried)
            else:
                # Default fallback order
                fallback_providers = ["google", "huggingface", "wavespeed"]
            
            # Filter to available providers and exclude current failed provider
            fallback_providers = [p for p in fallback_providers if p in available_providers and p != gpt_provider]
            
            # Skip fallbacks if in strict provider mode
            if strict_provider_mode:
                logger.info(f"[llm_text_gen][{flow_tag}] Strict provider mode enabled; skipping cross-provider fallback")
                fallback_providers = []
            
            if preferred_provider:
                # Caller explicitly pinned provider (e.g. podcast premium HF). Avoid cross-provider fallback noise.
                logger.info(f"[llm_text_gen][{flow_tag}] preferred_provider is set; skipping cross-provider fallback")
                fallback_providers = []
            
            if fallback_providers:
                fallback_provider = fallback_providers[0]  # Only try the first available
                try:
                    logger.info(f"[llm_text_gen][{flow_tag}] Trying SINGLE fallback provider: {fallback_provider}")
                    actual_provider_used = fallback_provider
                    
                    # Update provider enum for fallback
                    if fallback_provider == "google":
                        provider_enum = APIProvider.GEMINI
                        actual_provider_name = "gemini"
                        fallback_model = "gemini-2.0-flash-lite"
                    elif fallback_provider == "huggingface":
                        provider_enum = APIProvider.MISTRAL
                        actual_provider_name = "huggingface"
                        fallback_model = preferred_hf_models[0] if preferred_hf_models else "openai/gpt-oss-120b:cerebras"
                    elif fallback_provider == "wavespeed":
                        provider_enum = APIProvider.WAVESPEED
                        actual_provider_name = "wavespeed"
                        fallback_model = "openai/gpt-oss-120b"
                    
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
                                model=fallback_model,
                                fallback_models=hf_fallback_models,
                                temperature=temperature,
                                max_tokens=max_tokens,
                                system_prompt=system_instructions
                            )
                        else:
                            response_text = huggingface_text_response(
                                prompt=prompt,
                                model=fallback_model,
                                fallback_models=hf_fallback_models,
                                temperature=temperature,
                                max_tokens=max_tokens,
                                top_p=top_p,
                                system_prompt=system_instructions
                            )
                    elif fallback_provider == "wavespeed":
                        from .wavespeed_provider import wavespeed_text_response, wavespeed_structured_json_response
                        if json_struct:
                            response_text = wavespeed_structured_json_response(
                                prompt=prompt,
                                schema=json_struct,
                                model=fallback_model,
                                fallback_models=None,
                                temperature=temperature,
                                max_tokens=max_tokens,
                                system_prompt=system_instructions
                            )
                        else:
                            response_text = wavespeed_text_response(
                                prompt=prompt,
                                model=fallback_model,
                                fallback_models=None,
                                temperature=temperature,
                                max_tokens=max_tokens,
                                top_p=top_p,
                                system_prompt=system_instructions
                            )
                    
                    # TRACK USAGE after successful fallback call
                    if response_text:
                        logger.info(
                            f"[llm_text_gen][{flow_tag}] ✅ Fallback API call successful, tracking usage for user {user_id}, provider {provider_enum.value}"
                        )
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
                    logger.error(f"[llm_text_gen][{flow_tag}] Fallback provider {fallback_provider} also failed: {str(fallback_error)}")
            
            # CIRCUIT BREAKER: Stop immediately to prevent expensive API calls
            logger.error(f"[llm_text_gen][{flow_tag}] CIRCUIT BREAKER: Stopping to prevent expensive API calls.")
            raise RuntimeError("All LLM providers failed to generate a response.")

    except Exception as e:
        logger.error(f"[llm_text_gen][{flow_tag}] Error during text generation: {str(e)}")
        raise

def check_gpt_provider(gpt_provider: str) -> bool:
    """Check if the specified GPT provider is supported."""
    supported_providers = ["google", "huggingface", "wavespeed"]
    return gpt_provider in supported_providers

def get_api_key(gpt_provider: str) -> Optional[str]:
    """Get API key for the specified provider."""
    try:
        api_key_manager = APIKeyManager()
        provider_mapping = {
            "google": "gemini",
            "huggingface": "hf_token",
            "wavespeed": "wavespeed"
        }
        
        mapped_provider = provider_mapping.get(gpt_provider, gpt_provider)
        return api_key_manager.get_api_key(mapped_provider)
    except Exception as e:
        logger.error(f"[get_api_key] Error getting API key for {gpt_provider}: {str(e)}")
        return None 
