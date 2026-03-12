"""LLM Text Generator Module

This module contains the main text generation logic extracted from main_text_generation.py
to resolve merge conflicts and improve maintainability.
"""

import os
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from loguru import logger
from fastapi import HTTPException

from ..gemini_provider import gemini_text_response, gemini_structured_json_response
from ..huggingface_provider import huggingface_text_response, huggingface_structured_json_response
from ..tenant_provider_config import tenant_provider_config_resolver
from ..routing_policy import (
    PREMIUM_DEFAULT_MODEL,
    SIF_LOW_COST_MODEL_DEFAULTS,
    resolve_text_provider_alias,
)
from ...utils.logger_utils import emit_routing_event


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
    flow_type: str = "default",
) -> str:
    """
    Generate text using Language Model (LLM) based on the provided prompt.
    
    Args:
        prompt (str): The prompt to generate text from.
        system_prompt (str, optional): Custom system prompt to use instead of the default one.
        json_struct (dict, optional): JSON schema structure for structured responses.
        user_id (str): Clerk user ID for subscription checking (required).
        preferred_hf_models (list, optional): Preferred HuggingFace models to use.
        preferred_provider (str, optional): Preferred provider to use.
        flow_type (str): Type of flow for logging and routing.
        
    Returns:
        str: Generated text based on the prompt.
        
    Raises:
        RuntimeError: If subscription limits are exceeded or user_id is missing.
        HTTPException: For subscription limit errors (429 status).
    """
    try:
        resolved_flow_type = flow_type or ("sif_agent" if preferred_hf_models else "premium_tool")
        flow_tag = f"flow_type={resolved_flow_type}"
        subscription_preflight_completed = False
        
        # Initialize routing state for structured logging
        fallback_count = 0
        fallback_models_tried = []

        logger.info(f"[llm_text_gen][{flow_tag}] Starting text generation")
        logger.debug(f"[llm_text_gen] Prompt length: {len(prompt)} characters")
        
        # Set default values for LLM parameters
        gpt_provider = "google"
        model = "gemini-2.0-flash-001"
        hf_low_cost_default_model = SIF_LOW_COST_MODEL_DEFAULTS[0]
        temperature = 0.7
        max_tokens = 4000
        top_p = 0.9
        n = 1
        
        # Resolve provider configuration using tenant-aware resolver
        try:
            provider_cfg = tenant_provider_config_resolver.resolve(
                modality="text",
                user_id=user_id,
                explicit_provider=preferred_provider
            )
            
            if provider_cfg.selected_providers:
                gpt_provider = provider_cfg.selected_providers[0]
                if provider_cfg.model_policy.get("default_model"):
                    model = provider_cfg.model_policy["default_model"]
            
            logger.info(f"[llm_text_gen] Resolved provider: {gpt_provider}, model: {model}")
            
        except Exception as config_error:
            logger.warning(f"[llm_text_gen] Provider config resolution failed: {config_error}")
            # Continue with defaults
        
        # Handle preferred HF models for SIF flows
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

        # Default blog characteristics
        blog_tone = "Professional"
        blog_demographic = "Professional"
        blog_type = "Informational"
        blog_language = "English"
        blog_output_format = "markdown"
        blog_length = 2000
        
        # Check available providers
        available_providers = []
        for provider in ("google", "huggingface"):
            if get_api_key(provider, user_id=user_id):
                available_providers.append(provider)

        if gpt_provider not in available_providers:
            logger.warning(f"[llm_text_gen] Provider {gpt_provider} unavailable for user {user_id}, falling back.")
            if available_providers:
                gpt_provider = available_providers[0]
            else:
                logger.error("[llm_text_gen] No API keys found for supported providers.")
                raise RuntimeError("No LLM API keys configured for tenant or environment defaults.")

        # Ensure downstream provider clients receive resolved key
        resolved_key = get_api_key(gpt_provider, user_id=user_id)
        if gpt_provider == "google" and resolved_key:
            os.environ["GEMINI_API_KEY"] = resolved_key
            os.environ.setdefault("GOOGLE_API_KEY", resolved_key)
        elif gpt_provider == "huggingface" and resolved_key:
            os.environ["HF_TOKEN"] = resolved_key

        logger.debug(f"[llm_text_gen] Using provider: {gpt_provider}, model: {model}")
        
        # Emit routing event for primary selection
        emit_routing_event(
            logger,
            flow_type=resolved_flow_type,
            route_intent="primary",
            provider_selected=gpt_provider,
            model_selected=model,
            preferred_provider=preferred_provider,
            fallback_count=fallback_count,
            fallback_models_tried=fallback_models_tried,
            tenant_user_id=user_id,
            extra={"available_providers": available_providers}
        )

        # Map provider name to APIProvider enum (define at function scope for usage tracking)
        from models.subscription_models import APIProvider
        provider_enum = None
        actual_provider_name = None
        if gpt_provider == "google":
            provider_enum = APIProvider.GEMINI
            actual_provider_name = "gemini"
        elif gpt_provider == "huggingface":
            provider_enum = APIProvider.MISTRAL
            actual_provider_name = "huggingface"
        
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
                input_tokens = int(len(prompt.split()) * 1.3)
                # Worst-case estimate: assume maximum possible output tokens
                if max_tokens:
                    estimated_output_tokens = max_tokens
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
                    actual_provider_name=actual_provider_name
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
                        fallback_models=hf_fallback_models,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        system_prompt=system_instructions,
                        allow_model_variant_fallback=hf_allow_model_variant_fallback,
                        tenant_user_id=user_id
                    )
                else:
                    response_text = huggingface_text_response(
                        prompt=prompt,
                        model=model,
                        fallback_models=hf_fallback_models,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        top_p=top_p,
                        system_prompt=system_instructions,
                        tenant_user_id=user_id
                    )
            else:
                logger.error(f"[llm_text_gen] Unknown provider: {gpt_provider}")
                raise RuntimeError("Unknown LLM provider. Supported providers: google, huggingface")
            
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
            fallback_providers = ["google", "huggingface"]
            fallback_providers = [p for p in fallback_providers if p in available_providers and p != gpt_provider]
            
            if fallback_providers:
                fallback_provider = fallback_providers[0]  # Only try the first available
                try:
                    logger.info(f"[llm_text_gen][{flow_tag}] Trying SINGLE fallback provider: {fallback_provider}")
                    actual_provider_used = fallback_provider
                    fallback_count += 1
                    route_intent = "fallback"
                    
                    # Update provider enum for fallback
                    if fallback_provider == "google":
                        provider_enum = APIProvider.GEMINI
                        actual_provider_name = "gemini"
                        fallback_model = "gemini-2.0-flash-lite"
                        fallback_models_tried.append(fallback_model)
                    elif fallback_provider == "huggingface":
                        provider_enum = APIProvider.MISTRAL
                        actual_provider_name = "huggingface"
                        fallback_model = preferred_hf_models[0] if preferred_hf_models else PREMIUM_DEFAULT_MODEL
                        fallback_models_tried.append(fallback_model)
                    
                    # Emit routing event for fallback attempt
                    emit_routing_event(
                        logger,
                        flow_type=resolved_flow_type,
                        route_intent=route_intent,
                        provider_selected=fallback_provider,
                        model_selected=fallback_model,
                        preferred_provider=preferred_provider,
                        fallback_count=fallback_count,
                        fallback_models_tried=fallback_models_tried,
                        tenant_user_id=user_id,
                        extra={"available_providers": available_providers}
                    )
                    
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
                                temperature=temperature,
                                max_tokens=max_tokens,
                                system_prompt=system_instructions,
                                fallback_models=PREMIUM_HF_MINIMAL_FALLBACK_MODELS,
                                allow_model_variant_fallback=True,
                                tenant_user_id=user_id
                            )
                        else:
                            response_text = huggingface_text_response(
                                prompt=prompt,
                                model=fallback_model,
                                temperature=temperature,
                                max_tokens=max_tokens,
                                top_p=top_p,
                                system_prompt=system_instructions,
                                fallback_models=PREMIUM_HF_MINIMAL_FALLBACK_MODELS,
                                allow_model_variant_fallback=True,
                                tenant_user_id=user_id
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


def get_api_key(gpt_provider: str, user_id: Optional[str] = None) -> Optional[str]:
    """Get API key for the specified provider."""
    try:
        provider_mapping = {
            "google": "gemini",
            "huggingface": "huggingface"
        }
        mapped_provider = provider_mapping.get(gpt_provider, gpt_provider)
        key, _source = tenant_provider_config_resolver.resolve_provider_key(mapped_provider, user_id=user_id)
        return key
    except Exception as e:
        logger.error(f"[get_api_key] Error getting API key for {gpt_provider}: {str(e)}")
        return None
