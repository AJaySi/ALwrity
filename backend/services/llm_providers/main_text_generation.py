"""Main Text Generation Service for ALwrity Backend.

This service provides the main LLM text generation functionality,
migrated from the legacy lib/gpt_providers/text_generation/main_text_generation.py
"""

import os
import json
from typing import Optional, Dict, Any
from datetime import datetime
from loguru import logger
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
            from services.database import get_db
            from services.subscription import UsageTrackingService, PricingService
            from models.subscription_models import UsageSummary
            
            db = next(get_db())
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
                    db_track = next(get_db())
                    try:
                        # Estimate tokens from prompt and response
                        # Recalculate input tokens from prompt (consistent with pre-flight estimation)
                        tokens_input = int(len(prompt.split()) * 1.3)
                        tokens_output = int(len(str(response_text).split()) * 1.3)  # Estimate output tokens
                        tokens_total = tokens_input + tokens_output
                        
                        logger.debug(f"[llm_text_gen] Token estimates: input={tokens_input}, output={tokens_output}, total={tokens_total}")
                        
                        # Get or create usage summary
                        from models.subscription_models import UsageSummary
                        from services.subscription import PricingService
                        
                        pricing = PricingService(db_track)
                        current_period = pricing.get_current_billing_period(user_id) or datetime.now().strftime("%Y-%m")
                        
                        logger.debug(f"[llm_text_gen] Looking for usage summary: user_id={user_id}, period={current_period}")
                        
                        # Get limits once for safety check (to prevent exceeding limits even if actual usage > estimate)
                        provider_name = provider_enum.value
                        limits = pricing.get_user_limits(user_id)
                        token_limit = 0
                        if limits and limits.get('limits'):
                            token_limit = limits['limits'].get(f"{provider_name}_tokens", 0) or 0
                        
                        # CRITICAL: Use raw SQL to read current values directly from DB, bypassing SQLAlchemy cache
                        # This ensures we always get the absolute latest committed values, even across different sessions
                        from sqlalchemy import text
                        current_calls_before = 0
                        current_tokens_before = 0
                        record_count = 0  # Initialize to ensure it's always defined
                        
                        # CRITICAL: First check if record exists using COUNT query
                        try:
                            check_query = text("SELECT COUNT(*) FROM usage_summaries WHERE user_id = :user_id AND billing_period = :period")
                            record_count = db_track.execute(check_query, {'user_id': user_id, 'period': current_period}).scalar()
                            logger.debug(f"[llm_text_gen] 🔍 DEBUG: Record count check - found {record_count} record(s) for user={user_id}, period={current_period}")
                        except Exception as count_error:
                            logger.error(f"[llm_text_gen] ❌ COUNT query failed: {count_error}", exc_info=True)
                            record_count = 0
                        
                        if record_count and record_count > 0:
                            # Record exists - read current values with raw SQL
                            try:
                                # Validate provider_name to prevent SQL injection (whitelist approach)
                                valid_providers = ['gemini', 'openai', 'anthropic', 'mistral']
                                if provider_name not in valid_providers:
                                    raise ValueError(f"Invalid provider_name for SQL query: {provider_name}")
                                
                                # Read current values directly from database using raw SQL
                                # CRITICAL: This bypasses SQLAlchemy's session cache and gets absolute latest values
                                sql_query = text(f"""
                                    SELECT {provider_name}_calls, {provider_name}_tokens 
                                    FROM usage_summaries 
                                    WHERE user_id = :user_id AND billing_period = :period 
                                    LIMIT 1
                                """)
                                logger.debug(f"[llm_text_gen] 🔍 Executing raw SQL for EXISTING record: SELECT {provider_name}_calls, {provider_name}_tokens WHERE user_id={user_id}, period={current_period}")
                                result = db_track.execute(sql_query, {'user_id': user_id, 'period': current_period}).first()
                                if result:
                                    raw_calls = result[0] if result[0] is not None else 0
                                    raw_tokens = result[1] if result[1] is not None else 0
                                    current_calls_before = raw_calls
                                    current_tokens_before = raw_tokens
                                    logger.debug(f"[llm_text_gen] ✅ Raw SQL SUCCESS: Found EXISTING record - calls={current_calls_before}, tokens={current_tokens_before} (provider={provider_name}, column={provider_name}_calls/{provider_name}_tokens)")
                                    logger.debug(f"[llm_text_gen] 🔍 Raw SQL returned row: {result}, extracted calls={raw_calls}, tokens={raw_tokens}")
                                else:
                                    logger.error(f"[llm_text_gen] ❌ CRITICAL BUG: Record EXISTS (count={record_count}) but SELECT query returned None! Query: {sql_query}")
                                    # Fallback: Use ORM to get values
                                    summary_fallback = db_track.query(UsageSummary).filter(
                                        UsageSummary.user_id == user_id,
                                        UsageSummary.billing_period == current_period
                                    ).first()
                                    if summary_fallback:
                                        db_track.refresh(summary_fallback)
                                        current_calls_before = getattr(summary_fallback, f"{provider_name}_calls", 0) or 0
                                        current_tokens_before = getattr(summary_fallback, f"{provider_name}_tokens", 0) or 0
                                        logger.warning(f"[llm_text_gen] ⚠️ Using ORM fallback: calls={current_calls_before}, tokens={current_tokens_before}")
                            except Exception as sql_error:
                                logger.error(f"[llm_text_gen] ❌ Raw SQL query failed: {sql_error}", exc_info=True)
                                # Fallback: Use ORM to get values
                                summary_fallback = db_track.query(UsageSummary).filter(
                                    UsageSummary.user_id == user_id,
                                    UsageSummary.billing_period == current_period
                                ).first()
                                if summary_fallback:
                                    db_track.refresh(summary_fallback)
                                    current_calls_before = getattr(summary_fallback, f"{provider_name}_calls", 0) or 0
                                    current_tokens_before = getattr(summary_fallback, f"{provider_name}_tokens", 0) or 0
                        else:
                            logger.debug(f"[llm_text_gen] ℹ️ No record exists yet (will create new) - user={user_id}, period={current_period}")
                        
                        # Get or create usage summary object (needed for ORM update)
                        summary = db_track.query(UsageSummary).filter(
                            UsageSummary.user_id == user_id,
                            UsageSummary.billing_period == current_period
                        ).first()
                        
                        if not summary:
                            logger.debug(f"[llm_text_gen] Creating NEW usage summary for user {user_id}, period {current_period}")
                            summary = UsageSummary(
                                user_id=user_id,
                                billing_period=current_period
                            )
                            db_track.add(summary)
                            db_track.flush()  # Ensure summary is persisted before updating
                            # New record - values are already 0, no need to set
                            logger.debug(f"[llm_text_gen] ✅ New summary created - starting from 0")
                        else:
                            # CRITICAL: Update the ORM object with values from raw SQL query
                            # This ensures the ORM object reflects the actual database state before we increment
                            logger.debug(f"[llm_text_gen] 🔄 Existing summary found - syncing with raw SQL values: calls={current_calls_before}, tokens={current_tokens_before}")
                            setattr(summary, f"{provider_name}_calls", current_calls_before)
                            if provider_enum in [APIProvider.GEMINI, APIProvider.OPENAI, APIProvider.ANTHROPIC, APIProvider.MISTRAL]:
                                setattr(summary, f"{provider_name}_tokens", current_tokens_before)
                            logger.debug(f"[llm_text_gen] ✅ Synchronized ORM object: {provider_name}_calls={current_calls_before}, {provider_name}_tokens={current_tokens_before}")
                        
                        logger.debug(f"[llm_text_gen] Current {provider_name}_calls from DB (raw SQL): {current_calls_before}")
                        
                        # Update provider-specific counters (sync operation)
                        new_calls = current_calls_before + 1
                        
                        # CRITICAL: Use direct SQL UPDATE instead of ORM setattr for dynamic attributes
                        # SQLAlchemy doesn't detect changes when using setattr() on dynamic attributes
                        # Using raw SQL UPDATE ensures the change is persisted
                        from sqlalchemy import text
                        update_calls_query = text(f"""
                            UPDATE usage_summaries 
                            SET {provider_name}_calls = :new_calls 
                            WHERE user_id = :user_id AND billing_period = :period
                        """)
                        db_track.execute(update_calls_query, {
                            'new_calls': new_calls,
                            'user_id': user_id,
                            'period': current_period
                        })
                        logger.debug(f"[llm_text_gen] Updated {provider_name}_calls via SQL: {current_calls_before} -> {new_calls}")
                        
                        # Update token usage for LLM providers with safety check
                        # CRITICAL: Use current_tokens_before from raw SQL query (NOT from ORM object)
                        # The ORM object may have stale values, but raw SQL always has the latest committed values
                        if provider_enum in [APIProvider.GEMINI, APIProvider.OPENAI, APIProvider.ANTHROPIC, APIProvider.MISTRAL]:
                            logger.debug(f"[llm_text_gen] Current {provider_name}_tokens from DB (raw SQL): {current_tokens_before}")
                            
                            # SAFETY CHECK: Prevent exceeding token limit even if actual usage exceeds estimate
                            # This prevents abuse where actual response tokens exceed pre-flight validation estimate
                            projected_new_tokens = current_tokens_before + tokens_total
                            
                            # If limit is set (> 0) and would be exceeded, cap at limit
                            if token_limit > 0 and projected_new_tokens > token_limit:
                                logger.warning(
                                    f"[llm_text_gen] ⚠️ ACTUAL token usage ({tokens_total}) exceeded estimate. "
                                    f"Would exceed limit: {projected_new_tokens} > {token_limit}. "
                                    f"Capping tracked tokens at limit to prevent abuse."
                                )
                                # Cap at limit to prevent abuse
                                new_tokens = token_limit
                                # Adjust tokens_total for accurate total tracking
                                tokens_total = token_limit - current_tokens_before
                                if tokens_total < 0:
                                    tokens_total = 0
                            else:
                                new_tokens = projected_new_tokens
                            
                            # CRITICAL: Use direct SQL UPDATE instead of ORM setattr for dynamic attributes
                            update_tokens_query = text(f"""
                                UPDATE usage_summaries 
                                SET {provider_name}_tokens = :new_tokens 
                                WHERE user_id = :user_id AND billing_period = :period
                            """)
                            db_track.execute(update_tokens_query, {
                                'new_tokens': new_tokens,
                                'user_id': user_id,
                                'period': current_period
                            })
                            logger.debug(f"[llm_text_gen] Updated {provider_name}_tokens via SQL: {current_tokens_before} -> {new_tokens}")
                        else:
                            current_tokens_before = 0
                            new_tokens = 0
                        
                        # Determine tracked tokens (after any safety capping)
                        tracked_tokens_input = min(tokens_input, tokens_total)
                        tracked_tokens_output = max(tokens_total - tracked_tokens_input, 0)
                        
                        # Calculate and persist cost for this call
                        try:
                            cost_info = pricing.calculate_api_cost(
                                provider=provider_enum,
                                model_name=model,
                                tokens_input=tracked_tokens_input,
                                tokens_output=tracked_tokens_output,
                                request_count=1
                            )
                            cost_total = cost_info.get('cost_total', 0.0) or 0.0
                        except Exception as cost_error:
                            cost_total = 0.0
                            logger.error(f"[llm_text_gen] ❌ Failed to calculate API cost: {cost_error}", exc_info=True)
                        
                        if cost_total > 0:
                            logger.debug(f"[llm_text_gen] 💰 Calculated cost for {provider_name}: ${cost_total:.6f}")
                            update_costs_query = text(f"""
                                UPDATE usage_summaries 
                                SET {provider_name}_cost = COALESCE({provider_name}_cost, 0) + :cost,
                                    total_cost = COALESCE(total_cost, 0) + :cost
                                WHERE user_id = :user_id AND billing_period = :period
                            """)
                            db_track.execute(update_costs_query, {
                                'cost': cost_total,
                                'user_id': user_id,
                                'period': current_period
                            })
                            
                            # Keep ORM object in sync for logging/debugging
                            current_provider_cost = getattr(summary, f"{provider_name}_cost", 0.0) or 0.0
                            setattr(summary, f"{provider_name}_cost", current_provider_cost + cost_total)
                            summary.total_cost = (summary.total_cost or 0.0) + cost_total
                        else:
                            logger.debug(f"[llm_text_gen] 💰 Cost calculation returned $0 for {provider_name} (tokens_input={tracked_tokens_input}, tokens_output={tracked_tokens_output})")
                        
                        # Update totals using SQL UPDATE
                        old_total_calls = summary.total_calls or 0
                        old_total_tokens = summary.total_tokens or 0
                        new_total_calls = old_total_calls + 1
                        new_total_tokens = old_total_tokens + tokens_total
                        
                        update_totals_query = text("""
                            UPDATE usage_summaries 
                            SET total_calls = :total_calls, total_tokens = :total_tokens 
                            WHERE user_id = :user_id AND billing_period = :period
                        """)
                        db_track.execute(update_totals_query, {
                            'total_calls': new_total_calls,
                            'total_tokens': new_total_tokens,
                            'user_id': user_id,
                            'period': current_period
                        })
                        logger.debug(f"[llm_text_gen] Updated totals via SQL: calls {old_total_calls} -> {new_total_calls}, tokens {old_total_tokens} -> {new_total_tokens}")
                        
                        # Get plan details for unified log
                        limits = pricing.get_user_limits(user_id)
                        plan_name = limits.get('plan_name', 'unknown') if limits else 'unknown'
                        tier = limits.get('tier', 'unknown') if limits else 'unknown'
                        call_limit = limits['limits'].get(f"{provider_name}_calls", 0) if limits else 0
                        token_limit = limits['limits'].get(f"{provider_name}_tokens", 0) if limits else 0
                        
                        # Get image stats for unified log
                        current_images_before = getattr(summary, "stability_calls", 0) or 0
                        image_limit = limits['limits'].get("stability_calls", 0) if limits else 0
                        
                        # CRITICAL DEBUG: Print diagnostic info BEFORE commit (always visible, flushed immediately)
                        import sys
                        debug_msg = f"[DEBUG] BEFORE COMMIT - Record count: {record_count}, Raw SQL values: calls={current_calls_before}, tokens={current_tokens_before}, Provider: {provider_name}, Period: {current_period}, New calls will be: {new_calls}, New tokens will be: {new_tokens}"
                        print(debug_msg, flush=True)
                        sys.stdout.flush()
                        logger.debug(f"[llm_text_gen] {debug_msg}")
                        
                        # CRITICAL: Flush before commit to ensure changes are immediately visible to other sessions
                        db_track.flush()  # Flush to ensure changes are in DB (not just in transaction)
                        db_track.commit()  # Commit transaction to make changes visible to other sessions
                        logger.debug(f"[llm_text_gen] ✅ Successfully tracked usage: user {user_id} -> provider {provider_name} -> {new_calls} calls, {new_tokens} tokens (COMMITTED to DB)")
                        logger.debug(f"[llm_text_gen] Database state after commit: {provider_name}_calls={new_calls}, {provider_name}_tokens={new_tokens} (should be visible to next session)")
                        
                        # CRITICAL: Verify commit worked by reading back from DB immediately after commit
                        try:
                            verify_query = text(f"SELECT {provider_name}_calls, {provider_name}_tokens FROM usage_summaries WHERE user_id = :user_id AND billing_period = :period LIMIT 1")
                            verify_result = db_track.execute(verify_query, {'user_id': user_id, 'period': current_period}).first()
                            if verify_result:
                                verified_calls = verify_result[0] if verify_result[0] is not None else 0
                                verified_tokens = verify_result[1] if verify_result[1] is not None else 0
                                logger.debug(f"[llm_text_gen] ✅ VERIFICATION AFTER COMMIT: Read back calls={verified_calls}, tokens={verified_tokens} (expected: calls={new_calls}, tokens={new_tokens})")
                                if verified_calls != new_calls or verified_tokens != new_tokens:
                                    logger.error(f"[llm_text_gen] ❌ CRITICAL: COMMIT VERIFICATION FAILED! Expected calls={new_calls}, tokens={new_tokens}, but DB has calls={verified_calls}, tokens={verified_tokens}")
                                    # Force another commit attempt
                                    db_track.commit()
                                    verify_result2 = db_track.execute(verify_query, {'user_id': user_id, 'period': current_period}).first()
                                    if verify_result2:
                                        verified_calls2 = verify_result2[0] if verify_result2[0] is not None else 0
                                        verified_tokens2 = verify_result2[1] if verify_result2[1] is not None else 0
                                        logger.debug(f"[llm_text_gen] 🔄 After second commit attempt: calls={verified_calls2}, tokens={verified_tokens2}")
                                else:
                                    logger.debug(f"[llm_text_gen] ✅ COMMIT VERIFICATION PASSED: Values match expected values")
                            else:
                                logger.error(f"[llm_text_gen] ❌ CRITICAL: COMMIT VERIFICATION FAILED! Record not found after commit!")
                        except Exception as verify_error:
                            logger.error(f"[llm_text_gen] ❌ Error verifying commit: {verify_error}", exc_info=True)
                        
                        # UNIFIED SUBSCRIPTION LOG - Shows before/after state in one message
                        # Use actual_provider_name (e.g., "huggingface") instead of enum value (e.g., "mistral")
                        # Include image stats in the log
                        # DEBUG: Log the actual values being used
                        logger.debug(f"[llm_text_gen] 📊 FINAL VALUES FOR LOG: calls_before={current_calls_before}, calls_after={new_calls}, tokens_before={current_tokens_before}, tokens_after={new_tokens}, provider={provider_name}, enum={provider_enum}")
                        
                        # CRITICAL DEBUG: Print diagnostic info to stdout (always visible)
                        print(f"[DEBUG] Record count: {record_count}, Raw SQL values: calls={current_calls_before}, tokens={current_tokens_before}, Provider: {provider_name}")
                        
                        print(f"""
[SUBSCRIPTION] LLM Text Generation
├─ User: {user_id}
├─ Plan: {plan_name} ({tier})
├─ Provider: {actual_provider_name}
├─ Model: {model}
├─ Calls: {current_calls_before} → {new_calls} / {call_limit if call_limit > 0 else '∞'}
├─ Tokens: {current_tokens_before} → {new_tokens} / {token_limit if token_limit > 0 else '∞'}
├─ Images: {current_images_before} / {image_limit if image_limit > 0 else '∞'}
└─ Status: ✅ Allowed & Tracked
""")
                    except Exception as track_error:
                        logger.error(f"[llm_text_gen] ❌ Error tracking usage (non-blocking): {track_error}", exc_info=True)
                        db_track.rollback()
                    finally:
                        db_track.close()
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
                            db_track = next(get_db())
                            try:
                                # Estimate tokens from prompt and response
                                # Recalculate input tokens from prompt (consistent with pre-flight estimation)
                                tokens_input = int(len(prompt.split()) * 1.3)
                                tokens_output = int(len(str(response_text).split()) * 1.3)
                                tokens_total = tokens_input + tokens_output
                                
                                # Get or create usage summary
                                from models.subscription_models import UsageSummary
                                from services.subscription import PricingService
                                
                                pricing = PricingService(db_track)
                                current_period = pricing.get_current_billing_period(user_id) or datetime.now().strftime("%Y-%m")
                                
                                # Get limits once for safety check (to prevent exceeding limits even if actual usage > estimate)
                                provider_name = provider_enum.value
                                limits = pricing.get_user_limits(user_id)
                                token_limit = 0
                                if limits and limits.get('limits'):
                                    token_limit = limits['limits'].get(f"{provider_name}_tokens", 0) or 0
                                
                                # CRITICAL: Use raw SQL to read current values directly from DB, bypassing SQLAlchemy cache
                                from sqlalchemy import text
                                current_calls_before = 0
                                current_tokens_before = 0
                                
                                try:
                                    # Validate provider_name to prevent SQL injection
                                    valid_providers = ['gemini', 'openai', 'anthropic', 'mistral']
                                    if provider_name not in valid_providers:
                                        raise ValueError(f"Invalid provider_name for SQL query: {provider_name}")
                                    
                                    # Read current values directly from database using raw SQL
                                    sql_query = text(f"""
                                        SELECT {provider_name}_calls, {provider_name}_tokens 
                                        FROM usage_summaries 
                                        WHERE user_id = :user_id AND billing_period = :period 
                                        LIMIT 1
                                    """)
                                    result = db_track.execute(sql_query, {'user_id': user_id, 'period': current_period}).first()
                                    if result:
                                        current_calls_before = result[0] if result[0] is not None else 0
                                        current_tokens_before = result[1] if result[1] is not None else 0
                                        logger.debug(f"[llm_text_gen] Raw SQL read current values (fallback): calls={current_calls_before}, tokens={current_tokens_before}")
                                except Exception as sql_error:
                                    logger.warning(f"[llm_text_gen] Raw SQL query failed (fallback), falling back to ORM: {sql_error}")
                                    # Fallback to ORM query if raw SQL fails
                                    summary = db_track.query(UsageSummary).filter(
                                        UsageSummary.user_id == user_id,
                                        UsageSummary.billing_period == current_period
                                    ).first()
                                    if summary:
                                        db_track.refresh(summary)
                                        current_calls_before = getattr(summary, f"{provider_name}_calls", 0) or 0
                                        current_tokens_before = getattr(summary, f"{provider_name}_tokens", 0) or 0
                                
                                # Get or create usage summary object (needed for ORM update)
                                summary = db_track.query(UsageSummary).filter(
                                    UsageSummary.user_id == user_id,
                                    UsageSummary.billing_period == current_period
                                ).first()
                                
                                if not summary:
                                    summary = UsageSummary(
                                        user_id=user_id,
                                        billing_period=current_period
                                    )
                                    db_track.add(summary)
                                    db_track.flush()  # Ensure summary is persisted before updating
                                else:
                                    # CRITICAL: Update the ORM object with values from raw SQL query
                                    # This ensures the ORM object reflects the actual database state before we increment
                                    setattr(summary, f"{provider_name}_calls", current_calls_before)
                                    if provider_enum in [APIProvider.GEMINI, APIProvider.OPENAI, APIProvider.ANTHROPIC, APIProvider.MISTRAL]:
                                        setattr(summary, f"{provider_name}_tokens", current_tokens_before)
                                    logger.debug(f"[llm_text_gen] Synchronized summary object with raw SQL values (fallback): calls={current_calls_before}, tokens={current_tokens_before}")
                                
                                # Get "before" state for unified log (from raw SQL query)
                                logger.debug(f"[llm_text_gen] Current {provider_name}_calls from DB (fallback, raw SQL): {current_calls_before}")
                                
                                # Update provider-specific counters (sync operation)
                                new_calls = current_calls_before + 1
                                setattr(summary, f"{provider_name}_calls", new_calls)
                                
                                # Update token usage for LLM providers with safety check
                                # Use current_tokens_before from raw SQL query (most reliable)
                                if provider_enum in [APIProvider.GEMINI, APIProvider.OPENAI, APIProvider.ANTHROPIC, APIProvider.MISTRAL]:
                                    logger.debug(f"[llm_text_gen] Current {provider_name}_tokens from DB (fallback, raw SQL): {current_tokens_before}")
                                    
                                    # SAFETY CHECK: Prevent exceeding token limit even if actual usage exceeds estimate
                                    # This prevents abuse where actual response tokens exceed pre-flight validation estimate
                                    projected_new_tokens = current_tokens_before + tokens_total
                                    
                                    # If limit is set (> 0) and would be exceeded, cap at limit
                                    if token_limit > 0 and projected_new_tokens > token_limit:
                                        logger.warning(
                                            f"[llm_text_gen] ⚠️ ACTUAL token usage ({tokens_total}) exceeded estimate in fallback provider. "
                                            f"Would exceed limit: {projected_new_tokens} > {token_limit}. "
                                            f"Capping tracked tokens at limit to prevent abuse."
                                        )
                                        # Cap at limit to prevent abuse
                                        new_tokens = token_limit
                                        # Adjust tokens_total for accurate total tracking
                                        tokens_total = token_limit - current_tokens_before
                                        if tokens_total < 0:
                                            tokens_total = 0
                                    else:
                                        new_tokens = projected_new_tokens
                                    
                                    setattr(summary, f"{provider_name}_tokens", new_tokens)
                                else:
                                    current_tokens_before = 0
                                    new_tokens = 0
                                
                                # Determine tracked tokens after any safety capping
                                tracked_tokens_input = min(tokens_input, tokens_total)
                                tracked_tokens_output = max(tokens_total - tracked_tokens_input, 0)
                                
                                # Calculate and persist cost for this fallback call
                                cost_total = 0.0
                                try:
                                    cost_info = pricing.calculate_api_cost(
                                        provider=provider_enum,
                                        model_name=fallback_model,
                                        tokens_input=tracked_tokens_input,
                                        tokens_output=tracked_tokens_output,
                                        request_count=1
                                    )
                                    cost_total = cost_info.get('cost_total', 0.0) or 0.0
                                except Exception as cost_error:
                                    logger.error(f"[llm_text_gen] ❌ Failed to calculate fallback cost: {cost_error}", exc_info=True)
                                
                                if cost_total > 0:
                                    update_costs_query = text(f"""
                                        UPDATE usage_summaries 
                                        SET {provider_name}_cost = COALESCE({provider_name}_cost, 0) + :cost,
                                            total_cost = COALESCE(total_cost, 0) + :cost
                                        WHERE user_id = :user_id AND billing_period = :period
                                    """)
                                    db_track.execute(update_costs_query, {
                                        'cost': cost_total,
                                        'user_id': user_id,
                                        'period': current_period
                                    })
                                    setattr(summary, f"{provider_name}_cost", (getattr(summary, f"{provider_name}_cost", 0.0) or 0.0) + cost_total)
                                    summary.total_cost = (summary.total_cost or 0.0) + cost_total
                                
                                # Update totals (using potentially capped tokens_total from safety check)
                                summary.total_calls = (summary.total_calls or 0) + 1
                                summary.total_tokens = (summary.total_tokens or 0) + tokens_total
                                
                                # Get plan details for unified log (limits already retrieved above)
                                plan_name = limits.get('plan_name', 'unknown') if limits else 'unknown'
                                tier = limits.get('tier', 'unknown') if limits else 'unknown'
                                call_limit = limits['limits'].get(f"{provider_name}_calls", 0) if limits else 0
                                
                                # Get image stats for unified log
                                current_images_before = getattr(summary, "stability_calls", 0) or 0
                                image_limit = limits['limits'].get("stability_calls", 0) if limits else 0
                                
                                # CRITICAL: Flush before commit to ensure changes are immediately visible to other sessions
                                db_track.flush()  # Flush to ensure changes are in DB (not just in transaction)
                                db_track.commit()  # Commit transaction to make changes visible to other sessions
                                logger.info(f"[llm_text_gen] ✅ Successfully tracked fallback usage: user {user_id} -> provider {provider_name} -> {new_calls} calls, {new_tokens} tokens (committed)")
                                
                                # UNIFIED SUBSCRIPTION LOG for fallback
                                # Use actual_provider_name (e.g., "huggingface") instead of enum value (e.g., "mistral")
                                # Include image stats in the log
                                print(f"""
[SUBSCRIPTION] LLM Text Generation (Fallback)
├─ User: {user_id}
├─ Plan: {plan_name} ({tier})
├─ Provider: {actual_provider_name}
├─ Model: {fallback_model}
├─ Calls: {current_calls_before} → {new_calls} / {call_limit if call_limit > 0 else '∞'}
├─ Tokens: {current_tokens_before} → {new_tokens} / {token_limit if token_limit > 0 else '∞'}
├─ Images: {current_images_before} / {image_limit if image_limit > 0 else '∞'}
└─ Status: ✅ Allowed & Tracked
""")
                            except Exception as track_error:
                                logger.error(f"[llm_text_gen] ❌ Error tracking fallback usage (non-blocking): {track_error}", exc_info=True)
                                db_track.rollback()
                            finally:
                                db_track.close()
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