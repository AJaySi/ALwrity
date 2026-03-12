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
from .gemini_provider import gemini_text_response, gemini_structured_json_response
from .huggingface_provider import huggingface_text_response, huggingface_structured_json_response
<<<<<<< HEAD
from .tenant_provider_config import get_available_text_providers, get_tenant_api_key
from .routing_observability import emit_routing_event


def _normalize_provider(provider: Optional[str]) -> Optional[str]:
    if not provider:
        return None
    provider_aliases = {
        "gemini": "google",
        "google": "google",
        "hf": "huggingface",
        "hf_response_api": "huggingface",
        "huggingface": "huggingface",
        "wavespeed": "huggingface",
    }
    value = str(provider).strip().lower()
    return provider_aliases.get(value, value)




def _parse_csv_env(value: Optional[str]) -> List[str]:
    if not value:
        return []
    return [v.strip() for v in str(value).split(",") if v.strip()]


def _resolve_provider_sequence(
    preferred_provider: Optional[str],
    env_provider_raw: str,
    available_providers: List[str],
) -> List[str]:
    configured = _parse_csv_env(preferred_provider) if preferred_provider else _parse_csv_env(env_provider_raw)
    normalized = [_normalize_provider(p) for p in configured if _normalize_provider(p)]

    if not normalized:
        if "google" in available_providers:
            return ["google"]
        if "huggingface" in available_providers:
            return ["huggingface"]
        return []

    # preserve order and keep only available providers
    sequence = []
    for provider in normalized:
        if provider in available_providers:
            sequence.append(provider)

    # strict mode for single configured provider: no silent remap
    if len(normalized) == 1:
        return sequence

    # multi-provider mode: append any other available providers as tail only if none configured are available
    if not sequence:
        return [p for p in ["huggingface", "google"] if p in available_providers]

    return sequence




def _map_logical_model_to_provider_model(provider: str, model_name: str) -> str:
    """Map logical model aliases/full names to provider-specific model IDs."""
    raw = (model_name or "").strip()
    if not raw:
        return raw

    # Full provider path supplied explicitly; use as-is.
    if "/" in raw:
        return raw

    key = raw.lower()

    hf_map = {
        "gpt-oss": "openai/gpt-oss-120b:cerebras",
        "gpt-oss-120b": "openai/gpt-oss-120b:cerebras",
        "gpt-oss-20b": "openai/gpt-oss-20b:cerebras",
        "mistral": "mistralai/Mistral-7B-Instruct-v0.3:cerebras",
        "mistral-7b": "mistralai/Mistral-7B-Instruct-v0.3:cerebras",
        "llama": "meta-llama/Llama-3.1-8B-Instruct:groq",
        "llama-8b": "meta-llama/Llama-3.1-8B-Instruct:groq",
        "llama-70b": "meta-llama/Llama-3.1-70B-Instruct:groq",
    }

    wavespeed_map = {
        "gpt-oss": "openai/gpt-oss-120b",
        "gpt-oss-120b": "openai/gpt-oss-120b",
        "gpt-oss-20b": "openai/gpt-oss-20b",
        "mistral": "mistralai/Mistral-7B-Instruct-v0.3",
        "mistral-7b": "mistralai/Mistral-7B-Instruct-v0.3",
        "llama": "meta-llama/Llama-3.1-8B-Instruct",
        "llama-8b": "meta-llama/Llama-3.1-8B-Instruct",
        "llama-70b": "meta-llama/Llama-3.1-70B-Instruct",
    }

    if provider in {"huggingface", "hf", "hf_response_api"}:
        return hf_map.get(key, raw)
    if provider == "wavespeed":
        return wavespeed_map.get(key, raw)

    return raw

def _resolve_model_sequence(provider: str, preferred_hf_models: Optional[List[str]] = None) -> List[str]:
    models_env = _parse_csv_env(os.getenv("TEXTGEN_AI_MODELS", ""))

    if provider == "google":
        return ["gemini-2.0-flash-001"]

    if preferred_hf_models:
        return [_map_logical_model_to_provider_model(provider, m) for m in preferred_hf_models if m]

    if not models_env:
        return ["openai/gpt-oss-120b:groq"]

    resolved = [_map_logical_model_to_provider_model(provider, m) for m in models_env if m.strip()]
    return resolved or ["openai/gpt-oss-120b:groq"]
=======
from .routing_policy import (
    PREMIUM_DEFAULT_MODEL,
    SIF_LOW_COST_MODEL_DEFAULTS,
    resolve_text_provider_alias,
)
>>>>>>> pr-417

PREMIUM_HF_MINIMAL_FALLBACK_MODELS = [
    "openai/gpt-oss-120b:groq",
]


def llm_text_gen(
    prompt: str,
    system_prompt: Optional[str] = None,
    json_struct: Optional[Dict[str, Any]] = None,
    user_id: str = None,
    preferred_hf_models: Optional[List[str]] = None,
    preferred_provider: Optional[str] = None,
<<<<<<< HEAD
    flow_type: Optional[str] = None,
=======
    flow_type: str = "default",
>>>>>>> pr-416
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
<<<<<<< HEAD
        gpt_provider = "huggingface"  # Default to premium HF route for ALwrity AI tools
        model = "openai/gpt-oss-120b:cerebras"
=======
        gpt_provider = "google"
        model = "gemini-2.0-flash-001"
<<<<<<< HEAD
>>>>>>> pr-416
=======
        hf_low_cost_default_model = SIF_LOW_COST_MODEL_DEFAULTS[0]
>>>>>>> pr-417
        temperature = 0.7
        max_tokens = 4000
        top_p = 0.9
        n = 1
<<<<<<< HEAD
        fp = 16
        frequency_penalty = 0.0
        presence_penalty = 0.0
        
        # Check for GPT_PROVIDER environment variable
        env_provider = os.getenv('GPT_PROVIDER', '').lower()
<<<<<<< HEAD
        provider_list = [p.strip() for p in env_provider.split(',') if p.strip()]
=======
        resolved_env_provider = resolve_text_provider_alias(env_provider)
        if resolved_env_provider == "google":
            gpt_provider = "google"
            model = "gemini-2.0-flash-001"
        elif resolved_env_provider == "huggingface":
            gpt_provider = "huggingface"
            model = PREMIUM_DEFAULT_MODEL
>>>>>>> pr-417
        
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
        
=======

        env_provider_raw = os.getenv('GPT_PROVIDER', '').lower()
        env_provider = _normalize_provider(env_provider_raw)
        preferred_provider_normalized = _normalize_provider(preferred_provider)

>>>>>>> pr-416
        # Default blog characteristics
        blog_tone = "Professional"
        blog_demographic = "Professional"
        blog_type = "Informational"
        blog_language = "English"
        blog_output_format = "markdown"
        blog_length = 2000
        
<<<<<<< HEAD
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
<<<<<<< HEAD
                model = "openai/gpt-oss-120b:cerebras"
            elif "wavespeed" in available_providers:
                gpt_provider = "wavespeed"
                model = "openai/gpt-oss-120b"
=======
                model = PREMIUM_DEFAULT_MODEL
>>>>>>> pr-417
            else:
                logger.error("[llm_text_gen] No API keys found for supported providers.")
                raise RuntimeError("No LLM API keys configured. Configure GEMINI_API_KEY or HF_TOKEN to enable AI responses.")
        else:
            # Environment variable was set, validate it's supported
            if gpt_provider not in available_providers:
<<<<<<< HEAD
                if strict_provider_mode:
                    # Strict mode: fail if specified provider not available
                    raise RuntimeError(f"Provider {gpt_provider} not available. Available: {available_providers}")
=======
                logger.warning(f"[llm_text_gen] Provider {gpt_provider} not available, falling back to available providers")
                if "google" in available_providers:
                    gpt_provider = "google"
                    model = "gemini-2.0-flash-001"
                elif "huggingface" in available_providers:
                    gpt_provider = "huggingface"
                    model = PREMIUM_DEFAULT_MODEL
>>>>>>> pr-417
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
=======
        available_providers = get_available_text_providers(user_id)
        provider_sequence = _resolve_provider_sequence(preferred_provider, env_provider_raw, available_providers)
>>>>>>> pr-416

<<<<<<< HEAD
<<<<<<< HEAD
        if not provider_sequence:
            logger.error("[llm_text_gen] No configured providers available for tenant.")
            raise RuntimeError("No LLM providers available for tenant.")

        # strict mode if single configured provider; multi-provider fallback if comma-separated providers
        pinned_provider = len(_parse_csv_env(preferred_provider or env_provider_raw)) == 1 and bool(preferred_provider or env_provider_raw)
        gpt_provider = provider_sequence[0]
        model_sequence = _resolve_model_sequence(gpt_provider, preferred_hf_models)
        model = model_sequence[0]

        hf_api_key = get_tenant_api_key(user_id, "huggingface") if gpt_provider == "huggingface" else None

        logger.info(
            "[llm_text_gen] Mode | providers={} | models={} | env_models={} | strict_provider={} | strict_model={}",
            provider_sequence,
            model_sequence,
            _parse_csv_env(os.getenv("TEXTGEN_AI_MODELS", "")),
            pinned_provider,
            len(model_sequence) == 1,
        )
=======
        if gpt_provider == "huggingface" and preferred_hf_models is not None:
            model = preferred_hf_models[0] if preferred_hf_models else hf_low_cost_default_model
            logger.info(f"[llm_text_gen] Using SIF low-cost HF model: {model}")
>>>>>>> pr-417
            
<<<<<<< HEAD
        logger.info(f"[llm_text_gen][{flow_tag}] Using provider={gpt_provider}, model={model}")
=======
=======
        hf_fallback_models: Optional[List[str]] = None
        hf_allow_model_variant_fallback = True
        if gpt_provider == "huggingface":
            if preferred_hf_models is not None:
                if preferred_hf_models:
                    model = preferred_hf_models[0]
                    hf_fallback_models = preferred_hf_models[1:]
                    logger.info(f"[llm_text_gen] Using caller-provided HF policy starting model: {model}")
                else:
                    # Explicit empty policy: only requested model (plus optional variant handling).
                    hf_fallback_models = []
                    logger.info("[llm_text_gen] Using caller-provided HF policy with no fallback models")
            else:
                # Premium/default path: minimal safe fallback chain to avoid excessive model hopping.
                hf_fallback_models = PREMIUM_HF_MINIMAL_FALLBACK_MODELS

>>>>>>> pr-418
        logger.debug(f"[llm_text_gen] Using provider: {gpt_provider}, model: {model}")
        emit_routing_event(
            logger,
            "text_route_selected",
            user_id=user_id,
            flow_type=flow_type,
            provider_selected=gpt_provider,
            model_selected=model,
            env_provider=env_provider_raw or "auto",
            fallback_count=0,
        )
>>>>>>> pr-416

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
                
                logger.info(
                    "[llm_text_gen][subscription_preflight] start | user_id={} | provider={} | tokens_requested={}",
                    user_id,
                    actual_provider_name or provider_enum.value,
                    estimated_total_tokens,
                )

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

                logger.info(
                    "[llm_text_gen][subscription_preflight] pass | user_id={} | provider={} | tokens_requested={}",
                    user_id,
                    actual_provider_name or provider_enum.value,
                    estimated_total_tokens,
                )

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

<<<<<<< HEAD
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
                        system_prompt=system_instructions,
                        fallback_models=hf_fallback_models,
                        allow_model_variant_fallback=hf_allow_model_variant_fallback,
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
                        system_prompt=system_instructions,
                        fallback_models=hf_fallback_models,
                        allow_model_variant_fallback=hf_allow_model_variant_fallback,
                    )
            else:
                logger.error(f"[llm_text_gen] Unknown provider: {gpt_provider}")
                raise RuntimeError("Unknown LLM provider. Supported providers: google, huggingface, wavespeed")
            
            # TRACK USAGE after successful API call
            if response_text:
                logger.info(
                    f"[llm_text_gen][{flow_tag}] ✅ API call successful, tracking usage for user {user_id}, provider {provider_enum.value}"
                )
=======
        # Generate response based on provider/model sequence
        response_text = None
        errors: List[str] = []

        for provider_idx, provider_name in enumerate(provider_sequence):
            candidate_models = _resolve_model_sequence(provider_name, preferred_hf_models)
            for model_idx, candidate_model in enumerate(candidate_models):
>>>>>>> pr-416
                try:
                    emit_routing_event(
                        logger,
                        "text_route_attempt",
                        user_id=user_id,
                        flow_type=flow_type,
                        provider_selected=provider_name,
                        model_selected=candidate_model,
                        provider_attempt=provider_idx + 1,
                        model_attempt=model_idx + 1,
                    )
<<<<<<< HEAD
                    
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
<<<<<<< HEAD
                        fallback_model = preferred_hf_models[0] if preferred_hf_models else "openai/gpt-oss-120b:cerebras"
                    elif fallback_provider == "wavespeed":
                        provider_enum = APIProvider.WAVESPEED
                        actual_provider_name = "wavespeed"
                        fallback_model = "openai/gpt-oss-120b"
=======
                        fallback_model = preferred_hf_models[0] if preferred_hf_models else PREMIUM_DEFAULT_MODEL
>>>>>>> pr-417
                    
                    if fallback_provider == "google":
=======

                    if provider_name == "google":
>>>>>>> pr-416
                        if json_struct:
                            response_text = gemini_structured_json_response(
                                prompt=prompt,
                                schema=json_struct,
                                temperature=temperature,
                                top_p=top_p,
                                top_k=n,
                                max_tokens=max_tokens,
                                system_prompt=system_instructions,
                            )
                        else:
                            response_text = gemini_text_response(
                                prompt=prompt,
                                temperature=temperature,
                                top_p=top_p,
                                n=n,
                                max_tokens=max_tokens,
                                system_prompt=system_instructions,
                            )
                    elif provider_name == "huggingface":
                        hf_api_key_current = get_tenant_api_key(user_id, "huggingface")
                        if json_struct:
                            response_text = huggingface_structured_json_response(
                                prompt=prompt,
                                schema=json_struct,
<<<<<<< HEAD
<<<<<<< HEAD
                                model=fallback_model,
                                fallback_models=hf_fallback_models,
=======
                                model=candidate_model,
>>>>>>> pr-416
=======
                                model=fallback_model,
>>>>>>> pr-417
                                temperature=temperature,
                                max_tokens=max_tokens,
                                system_prompt=system_instructions,
<<<<<<< HEAD
                                api_key=hf_api_key_current,
=======
                                fallback_models=PREMIUM_HF_MINIMAL_FALLBACK_MODELS,
                                allow_model_variant_fallback=True,
>>>>>>> pr-418
                            )
                        else:
                            response_text = huggingface_text_response(
                                prompt=prompt,
<<<<<<< HEAD
<<<<<<< HEAD
                                model=fallback_model,
                                fallback_models=hf_fallback_models,
=======
                                model=fallback_model,
>>>>>>> pr-417
                                temperature=temperature,
                                max_tokens=max_tokens,
                                top_p=top_p,
                                system_prompt=system_instructions,
                                fallback_models=PREMIUM_HF_MINIMAL_FALLBACK_MODELS,
                                allow_model_variant_fallback=True,
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
=======
                                model=candidate_model,
>>>>>>> pr-416
                                temperature=temperature,
                                max_tokens=max_tokens,
                                top_p=top_p,
                                system_prompt=system_instructions,
                                api_key=hf_api_key_current,
                            )
                    else:
                        raise RuntimeError(f"Unknown provider {provider_name}")

                    if response_text:
<<<<<<< HEAD
                        logger.info(
                            f"[llm_text_gen][{flow_tag}] ✅ Fallback API call successful, tracking usage for user {user_id}, provider {provider_enum.value}"
                        )
=======
                        logger.info(f"[llm_text_gen] ✅ API call successful, tracking usage for user {user_id}, provider {provider_enum.value}")
>>>>>>> pr-416
                        try:
                            from services.intelligence.agents.agent_usage_tracking import track_agent_usage_sync
                            track_agent_usage_sync(
                                user_id=user_id,
                                model_name=candidate_model,
                                prompt=prompt,
                                response_text=response_text,
                                duration=0.5,
                            )
                        except Exception as usage_error:
<<<<<<< HEAD
                            logger.error(f"[llm_text_gen] ❌ Failed to track fallback usage: {usage_error}", exc_info=True)
                    
                    return response_text
                except Exception as fallback_error:
                    logger.error(f"[llm_text_gen][{flow_tag}] Fallback provider {fallback_provider} also failed: {str(fallback_error)}")
            
            # CIRCUIT BREAKER: Stop immediately to prevent expensive API calls
            logger.error(f"[llm_text_gen][{flow_tag}] CIRCUIT BREAKER: Stopping to prevent expensive API calls.")
            raise RuntimeError("All LLM providers failed to generate a response.")
=======
                            logger.error(f"[llm_text_gen] ❌ Failed to track usage: {usage_error}", exc_info=True)
                        return response_text
                except Exception as provider_error:
                    err = f"provider={provider_name},model={candidate_model},error={provider_error}"
                    errors.append(err)
                    logger.error("[llm_text_gen] Attempt failed: {}", err)
                    continue

            # strict provider mode: single configured provider should not switch
            if pinned_provider and len(provider_sequence) == 1:
                break

        logger.error("[llm_text_gen] CIRCUIT BREAKER: All configured provider/model attempts failed. {}", errors)
        raise RuntimeError("All configured LLM provider/model attempts failed.")
>>>>>>> pr-416

    except Exception as e:
        logger.error(f"[llm_text_gen][{flow_tag}] Error during text generation: {str(e)}")
        raise

def check_gpt_provider(gpt_provider: str) -> bool:
    """Check if the specified GPT provider is supported."""
<<<<<<< HEAD
<<<<<<< HEAD
    supported_providers = ["google", "huggingface", "wavespeed"]
    return gpt_provider in supported_providers
=======
    providers = [_normalize_provider(p) for p in _parse_csv_env(gpt_provider)]
    if not providers:
        providers = [_normalize_provider(gpt_provider)]
    supported_providers = {"google", "huggingface"}
    return all(p in supported_providers for p in providers if p)
>>>>>>> pr-416
=======
    supported_providers = ["google", "huggingface"]
    resolved_provider = resolve_text_provider_alias(gpt_provider) or gpt_provider
    return resolved_provider in supported_providers
>>>>>>> pr-417

def get_api_key(gpt_provider: str, user_id: Optional[str] = None) -> Optional[str]:
    """Get API key for the specified provider, preferring tenant-scoped keys."""
    try:
<<<<<<< HEAD
        api_key_manager = APIKeyManager()
        provider_mapping = {
            "google": "gemini",
            "huggingface": "hf_token",
<<<<<<< HEAD
            "wavespeed": "wavespeed"
=======
            "wavespeed": "hf_token"
>>>>>>> pr-417
        }
        
        resolved_provider = resolve_text_provider_alias(gpt_provider) or gpt_provider
        mapped_provider = provider_mapping.get(resolved_provider, resolved_provider)
        return api_key_manager.get_api_key(mapped_provider)
=======
        return get_tenant_api_key(user_id, gpt_provider)
>>>>>>> pr-416
    except Exception as e:
        logger.error(f"[get_api_key] Error getting API key for {gpt_provider}: {str(e)}")
        return None

