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


def llm_text_gen(
    prompt: str,
    system_prompt: Optional[str] = None,
    json_struct: Optional[Dict[str, Any]] = None,
    user_id: str = None,
    preferred_hf_models: Optional[List[str]] = None,
    preferred_provider: Optional[str] = None,
    flow_type: str = "default",
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
        logger.info("[llm_text_gen] Starting text generation")
        logger.debug(f"[llm_text_gen] Prompt length: {len(prompt)} characters")
        
        # Set default values for LLM parameters
        gpt_provider = "google"
        model = "gemini-2.0-flash-001"
        temperature = 0.7
        max_tokens = 4000
        top_p = 0.9
        n = 1

        env_provider_raw = os.getenv('GPT_PROVIDER', '').lower()
        env_provider = _normalize_provider(env_provider_raw)
        preferred_provider_normalized = _normalize_provider(preferred_provider)

        # Default blog characteristics
        blog_tone = "Professional"
        blog_demographic = "Professional"
        blog_type = "Informational"
        blog_language = "English"
        blog_output_format = "markdown"
        blog_length = 2000
        
        available_providers = get_available_text_providers(user_id)
        provider_sequence = _resolve_provider_sequence(preferred_provider, env_provider_raw, available_providers)

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

        # Generate response based on provider/model sequence
        response_text = None
        errors: List[str] = []

        for provider_idx, provider_name in enumerate(provider_sequence):
            candidate_models = _resolve_model_sequence(provider_name, preferred_hf_models)
            for model_idx, candidate_model in enumerate(candidate_models):
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

                    if provider_name == "google":
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
                                model=candidate_model,
                                temperature=temperature,
                                max_tokens=max_tokens,
                                system_prompt=system_instructions,
                                api_key=hf_api_key_current,
                            )
                        else:
                            response_text = huggingface_text_response(
                                prompt=prompt,
                                model=candidate_model,
                                temperature=temperature,
                                max_tokens=max_tokens,
                                top_p=top_p,
                                system_prompt=system_instructions,
                                api_key=hf_api_key_current,
                            )
                    else:
                        raise RuntimeError(f"Unknown provider {provider_name}")

                    if response_text:
                        logger.info(f"[llm_text_gen] ✅ API call successful, tracking usage for user {user_id}, provider {provider_enum.value}")
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

    except Exception as e:
        logger.error(f"[llm_text_gen] Error during text generation: {str(e)}")
        raise

def check_gpt_provider(gpt_provider: str) -> bool:
    """Check if the specified GPT provider is supported."""
    providers = [_normalize_provider(p) for p in _parse_csv_env(gpt_provider)]
    if not providers:
        providers = [_normalize_provider(gpt_provider)]
    supported_providers = {"google", "huggingface"}
    return all(p in supported_providers for p in providers if p)

def get_api_key(gpt_provider: str, user_id: Optional[str] = None) -> Optional[str]:
    """Get API key for the specified provider, preferring tenant-scoped keys."""
    try:
        return get_tenant_api_key(user_id, gpt_provider)
    except Exception as e:
        logger.error(f"[get_api_key] Error getting API key for {gpt_provider}: {str(e)}")
        return None

