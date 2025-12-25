from __future__ import annotations

import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any

from .image_generation import (
    ImageGenerationOptions,
    ImageGenerationResult,
    HuggingFaceImageProvider,
    GeminiImageProvider,
    StabilityImageProvider,
    WaveSpeedImageProvider,
)
from utils.logger_utils import get_service_logger


logger = get_service_logger("image_generation.facade")


def _select_provider(explicit: Optional[str]) -> str:
    if explicit:
        return explicit
    gpt_provider = (os.getenv("GPT_PROVIDER") or "").lower()
    if gpt_provider.startswith("gemini"):
        return "gemini"
    if gpt_provider.startswith("hf"):
        return "huggingface"
    if os.getenv("STABILITY_API_KEY"):
        return "stability"
    if os.getenv("WAVESPEED_API_KEY"):
        return "wavespeed"
    # Fallback to huggingface to enable a path if configured
    return "huggingface"


def _get_provider(provider_name: str):
    if provider_name == "huggingface":
        return HuggingFaceImageProvider()
    if provider_name == "gemini":
        return GeminiImageProvider()
    if provider_name == "stability":
        return StabilityImageProvider()
    if provider_name == "wavespeed":
        return WaveSpeedImageProvider()
    raise ValueError(f"Unknown image provider: {provider_name}")


def generate_image(prompt: str, options: Optional[Dict[str, Any]] = None, user_id: Optional[str] = None) -> ImageGenerationResult:
    """Generate image with pre-flight validation.
    
    Args:
        prompt: Image generation prompt
        options: Image generation options (provider, model, width, height, etc.)
        user_id: User ID for subscription checking (optional, but required for validation)
    """
    # PRE-FLIGHT VALIDATION: Validate image generation before API call
    # MUST happen BEFORE any API calls - return immediately if validation fails
    if user_id:
        from services.database import get_db
        from services.subscription import PricingService
        from services.subscription.preflight_validator import validate_image_generation_operations
        from fastapi import HTTPException
        
        logger.info(f"[Image Generation] 🔍 Starting pre-flight validation for user_id={user_id}")
        db = next(get_db())
        try:
            pricing_service = PricingService(db)
            # Raises HTTPException immediately if validation fails - frontend gets immediate response
            validate_image_generation_operations(
                pricing_service=pricing_service,
                user_id=user_id
            )
            logger.info(f"[Image Generation] ✅ Pre-flight validation passed for user_id={user_id} - proceeding with image generation")
        except HTTPException as http_ex:
            # Re-raise immediately - don't proceed with API call
            logger.error(f"[Image Generation] ❌ Pre-flight validation failed for user_id={user_id} - blocking API call: {http_ex.detail}")
            raise
        finally:
            db.close()
    else:
        logger.warning(f"[Image Generation] ⚠️ No user_id provided - skipping pre-flight validation (this should not happen in production)")
    opts = options or {}
    provider_name = _select_provider(opts.get("provider"))

    image_options = ImageGenerationOptions(
        prompt=prompt,
        negative_prompt=opts.get("negative_prompt"),
        width=int(opts.get("width", 1024)),
        height=int(opts.get("height", 1024)),
        guidance_scale=opts.get("guidance_scale"),
        steps=opts.get("steps"),
        seed=opts.get("seed"),
        model=opts.get("model"),
        extra=opts,
    )

    # Normalize obvious model/provider mismatches
    model_lower = (image_options.model or "").lower()
    if provider_name == "stability" and (model_lower.startswith("black-forest-labs/") or model_lower.startswith("runwayml/") or model_lower.startswith("stabilityai/flux")):
        logger.info("Remapping provider to huggingface for model=%s", image_options.model)
        provider_name = "huggingface"

    if provider_name == "huggingface" and not image_options.model:
        # Provide a sensible default HF model if none specified
        image_options.model = "black-forest-labs/FLUX.1-Krea-dev"
    
    if provider_name == "wavespeed" and not image_options.model:
        # Provide a sensible default WaveSpeed model if none specified
        image_options.model = "ideogram-v3-turbo"

    logger.info("Generating image via provider=%s model=%s", provider_name, image_options.model)
    provider = _get_provider(provider_name)
    result = provider.generate(image_options)
    
    # TRACK USAGE after successful API call
    has_image_bytes = bool(result.image_bytes) if result else False
    image_bytes_len = len(result.image_bytes) if (result and result.image_bytes) else 0
    logger.info(f"[Image Generation] Checking tracking conditions: user_id={user_id}, has_result={bool(result)}, has_image_bytes={has_image_bytes}, image_bytes_len={image_bytes_len}")
    if user_id and result and result.image_bytes:
        logger.info(f"[Image Generation] ✅ API call successful, tracking usage for user {user_id}")
        try:
            from services.database import get_db as get_db_track
            db_track = next(get_db_track())
            try:
                from models.subscription_models import UsageSummary, APIUsageLog, APIProvider
                from services.subscription import PricingService
                
                pricing = PricingService(db_track)
                current_period = pricing.get_current_billing_period(user_id) or datetime.now().strftime("%Y-%m")
                
                # Get or create usage summary
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
                    db_track.flush()
                
                # Get cost from result metadata or calculate
                estimated_cost = 0.0
                if result.metadata and "estimated_cost" in result.metadata:
                    estimated_cost = float(result.metadata["estimated_cost"])
                else:
                    # Fallback: estimate based on provider/model
                    if provider_name == "wavespeed":
                        if result.model and "qwen" in result.model.lower():
                            estimated_cost = 0.05
                        else:
                            estimated_cost = 0.10  # ideogram-v3-turbo default
                    elif provider_name == "stability":
                        estimated_cost = 0.04
                    else:
                        estimated_cost = 0.05  # Default estimate
                
                # Get current values before update
                current_calls_before = getattr(summary, "stability_calls", 0) or 0
                current_cost_before = getattr(summary, "stability_cost", 0.0) or 0.0
                
                # Update image calls and cost
                new_calls = current_calls_before + 1
                new_cost = current_cost_before + estimated_cost
                
                # Use direct SQL UPDATE for dynamic attributes
                from sqlalchemy import text as sql_text
                update_query = sql_text("""
                    UPDATE usage_summaries 
                    SET stability_calls = :new_calls,
                        stability_cost = :new_cost
                    WHERE user_id = :user_id AND billing_period = :period
                """)
                db_track.execute(update_query, {
                    'new_calls': new_calls,
                    'new_cost': new_cost,
                    'user_id': user_id,
                    'period': current_period
                })
                
                # Update total cost
                summary.total_cost = (summary.total_cost or 0.0) + estimated_cost
                summary.total_calls = (summary.total_calls or 0) + 1
                summary.updated_at = datetime.utcnow()
                
                # Determine API provider based on actual provider
                api_provider = APIProvider.STABILITY  # Default for image generation
                
                # Create usage log
                usage_log = APIUsageLog(
                    user_id=user_id,
                    provider=api_provider,
                    endpoint="/image-generation",
                    method="POST",
                    model_used=result.model or "unknown",
                    tokens_input=0,
                    tokens_output=0,
                    tokens_total=0,
                    cost_input=0.0,
                    cost_output=0.0,
                    cost_total=estimated_cost,
                    response_time=0.0,
                    status_code=200,
                    request_size=len(prompt.encode("utf-8")),
                    response_size=len(result.image_bytes),
                    billing_period=current_period,
                )
                db_track.add(usage_log)
                
                # Get plan details for unified log
                limits = pricing.get_user_limits(user_id)
                plan_name = limits.get('plan_name', 'unknown') if limits else 'unknown'
                tier = limits.get('tier', 'unknown') if limits else 'unknown'
                image_limit = limits['limits'].get("stability_calls", 0) if limits else 0
                # Only show ∞ for Enterprise tier when limit is 0 (unlimited)
                image_limit_display = image_limit if (image_limit > 0 or tier != 'enterprise') else '∞'
                
                # Get related stats for unified log
                current_audio_calls = getattr(summary, "audio_calls", 0) or 0
                audio_limit = limits['limits'].get("audio_calls", 0) if limits else 0
                current_image_edit_calls = getattr(summary, "image_edit_calls", 0) or 0
                image_edit_limit = limits['limits'].get("image_edit_calls", 0) if limits else 0
                current_video_calls = getattr(summary, "video_calls", 0) or 0
                video_limit = limits['limits'].get("video_calls", 0) if limits else 0
                
                db_track.commit()
                logger.info(f"[Image Generation] ✅ Successfully tracked usage: user {user_id} -> image -> {new_calls} calls, ${estimated_cost:.4f}")
                
                # UNIFIED SUBSCRIPTION LOG - Shows before/after state in one message
                print(f"""
[SUBSCRIPTION] Image Generation
├─ User: {user_id}
├─ Plan: {plan_name} ({tier})
├─ Provider: {provider_name}
├─ Actual Provider: {provider_name}
├─ Model: {result.model or 'unknown'}
├─ Calls: {current_calls_before} → {new_calls} / {image_limit_display}
├─ Cost: ${current_cost_before:.4f} → ${new_cost:.4f}
├─ Audio: {current_audio_calls} / {audio_limit if audio_limit > 0 else '∞'}
├─ Image Editing: {current_image_edit_calls} / {image_edit_limit if image_edit_limit > 0 else '∞'}
├─ Videos: {current_video_calls} / {video_limit if video_limit > 0 else '∞'}
└─ Status: ✅ Allowed & Tracked
""", flush=True)
                sys.stdout.flush()
                
            except Exception as track_error:
                logger.error(f"[Image Generation] ❌ Error tracking usage (non-blocking): {track_error}", exc_info=True)
                import traceback
                logger.error(f"[Image Generation] Full traceback: {traceback.format_exc()}")
                db_track.rollback()
            finally:
                db_track.close()
        except Exception as usage_error:
            logger.error(f"[Image Generation] ❌ Failed to track usage: {usage_error}", exc_info=True)
            import traceback
            logger.error(f"[Image Generation] Full traceback: {traceback.format_exc()}")
    else:
        logger.warning(f"[Image Generation] ⚠️ Skipping usage tracking: user_id={user_id}, image_bytes={len(result.image_bytes) if result.image_bytes else 0} bytes")
    
    return result


def generate_character_image(
    prompt: str,
    reference_image_bytes: bytes,
    user_id: Optional[str] = None,
    style: str = "Realistic",
    aspect_ratio: str = "16:9",
    rendering_speed: str = "Quality",
    timeout: Optional[int] = None,
) -> bytes:
    """Generate character-consistent image with pre-flight validation and usage tracking.
    
    Uses Ideogram Character API via WaveSpeed to maintain character consistency.
    
    Args:
        prompt: Text prompt describing the scene/context for the character
        reference_image_bytes: Reference image bytes (base avatar)
        user_id: User ID for subscription checking (required)
        style: Character style type ("Auto", "Fiction", or "Realistic")
        aspect_ratio: Aspect ratio ("1:1", "16:9", "9:16", "4:3", "3:4")
        rendering_speed: Rendering speed ("Default", "Turbo", "Quality")
        timeout: Total timeout in seconds for submission + polling (default: 180)
        
    Returns:
        bytes: Generated image bytes with consistent character
    """
    # PRE-FLIGHT VALIDATION: Validate image generation before API call
    if user_id:
        from services.database import get_db
        from services.subscription import PricingService
        from services.subscription.preflight_validator import validate_image_generation_operations
        from fastapi import HTTPException
        
        logger.info(f"[Character Image Generation] 🔍 Starting pre-flight validation for user_id={user_id}")
        db = next(get_db())
        try:
            pricing_service = PricingService(db)
            # Raises HTTPException immediately if validation fails
            validate_image_generation_operations(
                pricing_service=pricing_service,
                user_id=user_id,
                num_images=1,
            )
            logger.info(f"[Character Image Generation] ✅ Pre-flight validation passed for user_id={user_id} - proceeding with character image generation")
        except HTTPException as http_ex:
            # Re-raise immediately - don't proceed with API call
            logger.error(f"[Character Image Generation] ❌ Pre-flight validation failed for user_id={user_id} - blocking API call: {http_ex.detail}")
            raise
        finally:
            db.close()
    else:
        logger.warning(f"[Character Image Generation] ⚠️ No user_id provided - skipping pre-flight validation (this should not happen in production)")
    
    # Generate character image via WaveSpeed
    from services.wavespeed.client import WaveSpeedClient
    from fastapi import HTTPException
    
    try:
        wavespeed_client = WaveSpeedClient()
        image_bytes = wavespeed_client.generate_character_image(
            prompt=prompt,
            reference_image_bytes=reference_image_bytes,
            style=style,
            aspect_ratio=aspect_ratio,
            rendering_speed=rendering_speed,
            timeout=timeout,
        )
        
        # TRACK USAGE after successful API call
        has_image_bytes = bool(image_bytes) if image_bytes else False
        image_bytes_len = len(image_bytes) if image_bytes else 0
        logger.info(f"[Character Image Generation] Checking tracking conditions: user_id={user_id}, has_image_bytes={has_image_bytes}, image_bytes_len={image_bytes_len}")
        if user_id and image_bytes:
            logger.info(f"[Character Image Generation] ✅ API call successful, tracking usage for user {user_id}")
            try:
                from services.database import get_db as get_db_track
                db_track = next(get_db_track())
                try:
                    from models.subscription_models import UsageSummary, APIUsageLog, APIProvider
                    from services.subscription import PricingService
                    
                    pricing = PricingService(db_track)
                    current_period = pricing.get_current_billing_period(user_id) or datetime.now().strftime("%Y-%m")
                    
                    # Get or create usage summary
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
                        db_track.flush()
                    
                    # Character image cost (same as ideogram-v3-turbo)
                    estimated_cost = 0.10
                    current_calls_before = getattr(summary, "stability_calls", 0) or 0
                    current_cost_before = getattr(summary, "stability_cost", 0.0) or 0.0
                    
                    new_calls = current_calls_before + 1
                    new_cost = current_cost_before + estimated_cost
                    
                    # Use direct SQL UPDATE for dynamic attributes
                    from sqlalchemy import text as sql_text
                    update_query = sql_text("""
                        UPDATE usage_summaries 
                        SET stability_calls = :new_calls,
                            stability_cost = :new_cost
                        WHERE user_id = :user_id AND billing_period = :period
                    """)
                    db_track.execute(update_query, {
                        'new_calls': new_calls,
                        'new_cost': new_cost,
                        'user_id': user_id,
                        'period': current_period
                    })
                    
                    # Update total cost
                    summary.total_cost = (summary.total_cost or 0.0) + estimated_cost
                    summary.total_calls = (summary.total_calls or 0) + 1
                    summary.updated_at = datetime.utcnow()
                    
                    # Create usage log
                    usage_log = APIUsageLog(
                        user_id=user_id,
                        provider=APIProvider.STABILITY,  # Image generation uses STABILITY provider
                        endpoint="/image-generation/character",
                        method="POST",
                        model_used="ideogram-character",
                        tokens_input=0,
                        tokens_output=0,
                        tokens_total=0,
                        cost_input=0.0,
                        cost_output=0.0,
                        cost_total=estimated_cost,
                        response_time=0.0,
                        status_code=200,
                        request_size=len(prompt.encode("utf-8")),
                        response_size=len(image_bytes),
                        billing_period=current_period,
                    )
                    db_track.add(usage_log)
                    
                    # Get plan details for unified log
                    limits = pricing.get_user_limits(user_id)
                    plan_name = limits.get('plan_name', 'unknown') if limits else 'unknown'
                    tier = limits.get('tier', 'unknown') if limits else 'unknown'
                    image_limit = limits['limits'].get("stability_calls", 0) if limits else 0
                    image_limit_display = image_limit if (image_limit > 0 or tier != 'enterprise') else '∞'
                    
                    # Get related stats
                    current_audio_calls = getattr(summary, "audio_calls", 0) or 0
                    audio_limit = limits['limits'].get("audio_calls", 0) if limits else 0
                    current_image_edit_calls = getattr(summary, "image_edit_calls", 0) or 0
                    image_edit_limit = limits['limits'].get("image_edit_calls", 0) if limits else 0
                    current_video_calls = getattr(summary, "video_calls", 0) or 0
                    video_limit = limits['limits'].get("video_calls", 0) if limits else 0
                    
                    db_track.commit()
                    
                    # UNIFIED SUBSCRIPTION LOG
                    print(f"""
[SUBSCRIPTION] Image Generation (Character)
├─ User: {user_id}
├─ Plan: {plan_name} ({tier})
├─ Provider: wavespeed
├─ Actual Provider: wavespeed
├─ Model: ideogram-character
├─ Calls: {current_calls_before} → {new_calls} / {image_limit_display}
├─ Cost: ${current_cost_before:.4f} → ${new_cost:.4f}
├─ Audio: {current_audio_calls} / {audio_limit if audio_limit > 0 else '∞'}
├─ Image Editing: {current_image_edit_calls} / {image_edit_limit if image_edit_limit > 0 else '∞'}
├─ Videos: {current_video_calls} / {video_limit if video_limit > 0 else '∞'}
└─ Status: ✅ Allowed & Tracked
""", flush=True)
                    sys.stdout.flush()
                    
                    logger.info(f"[Character Image Generation] ✅ Successfully tracked usage: user {user_id} -> {new_calls} calls, ${estimated_cost:.4f}")
                    
                except Exception as track_error:
                    logger.error(f"[Character Image Generation] ❌ Error tracking usage (non-blocking): {track_error}", exc_info=True)
                    import traceback
                    logger.error(f"[Character Image Generation] Full traceback: {traceback.format_exc()}")
                    db_track.rollback()
                finally:
                    db_track.close()
            except Exception as usage_error:
                logger.error(f"[Character Image Generation] ❌ Failed to track usage: {usage_error}", exc_info=True)
                import traceback
                logger.error(f"[Character Image Generation] Full traceback: {traceback.format_exc()}")
        else:
            logger.warning(f"[Character Image Generation] ⚠️ Skipping usage tracking: user_id={user_id}, image_bytes={len(image_bytes) if image_bytes else 0} bytes")
        
        return image_bytes
        
    except HTTPException:
        raise
    except Exception as api_error:
        logger.error(f"[Character Image Generation] Character image generation API failed: {api_error}")
        raise HTTPException(
            status_code=502,
            detail={
                "error": "Character image generation failed",
                "message": str(api_error)
            }
        )


