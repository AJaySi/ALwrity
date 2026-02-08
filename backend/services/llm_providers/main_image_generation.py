from __future__ import annotations

import os
import sys
import base64
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi.concurrency import run_in_threadpool

from .image_generation import (
    ImageGenerationOptions,
    ImageGenerationResult,
    ImageEditOptions,
    ImageEditProvider,
    HuggingFaceImageProvider,
    GeminiImageProvider,
    StabilityImageProvider,
    WaveSpeedImageProvider,
)
from .image_generation.base import FaceSwapOptions, FaceSwapProvider
from .image_generation.wavespeed_edit_provider import WaveSpeedEditProvider
from .image_generation.wavespeed_face_swap_provider import WaveSpeedFaceSwapProvider
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


def _get_face_swap_provider(provider_name: str) -> FaceSwapProvider:
    """Get face swap provider by name."""
    if provider_name == "wavespeed":
        return WaveSpeedFaceSwapProvider()
    raise ValueError(f"Unknown face swap provider: {provider_name}")


def _get_edit_provider(provider_name: str) -> ImageEditProvider:
    """Get editing provider instance.
    
    Args:
        provider_name: Provider name ("wavespeed", "stability", etc.)
        
    Returns:
        ImageEditProvider instance
        
    Raises:
        ValueError: If provider is not supported
    """
    if provider_name == "wavespeed":
        return WaveSpeedEditProvider()
    # TODO: Add Stability edit provider if needed
    # elif provider_name == "stability":
    #     return StabilityEditProvider()
    else:
        raise ValueError(f"Unknown edit provider: {provider_name}")


def _validate_image_operation(
    user_id: Optional[str],
    operation_type: str = "image-generation",
    num_operations: int = 1,
    log_prefix: str = "[Image Generation]"
) -> None:
    """
    Reusable pre-flight validation helper for all image operations.
    
    Extracted from generate_image() to be reused across all image operation functions.
    
    Args:
        user_id: User ID for subscription checking
        operation_type: Type of operation (for logging)
        num_operations: Number of operations to validate (default: 1)
        log_prefix: Logging prefix for operation-specific logs
        
    Raises:
        HTTPException: If validation fails (subscription limits exceeded, etc.)
    """
    if not user_id:
        logger.warning(f"{log_prefix} ⚠️ No user_id provided - skipping pre-flight validation (this should not happen in production)")
        return
    
    from services.database import get_session_for_user
    from services.subscription import PricingService
    from services.subscription.preflight_validator import validate_image_generation_operations
    from fastapi import HTTPException
    
    logger.info(f"{log_prefix} 🔍 Starting pre-flight validation for user_id={user_id}")
    db = get_session_for_user(user_id)
    try:
        pricing_service = PricingService(db)
        # Raises HTTPException immediately if validation fails - frontend gets immediate response
        validate_image_generation_operations(
            pricing_service=pricing_service,
            user_id=user_id,
            num_images=num_operations
        )
        logger.info(f"{log_prefix} ✅ Pre-flight validation passed for user_id={user_id} - proceeding with operation")
    except HTTPException as http_ex:
        # Re-raise immediately - don't proceed with API call
        logger.error(f"{log_prefix} ❌ Pre-flight validation failed for user_id={user_id} - blocking API call: {http_ex.detail}")
        raise
    finally:
        db.close()


def _track_image_operation_usage(
    user_id: str,
    provider: str,
    model: str,
    operation_type: str,
    result_bytes: bytes,
    cost: float,
    prompt: Optional[str] = None,
    endpoint: str = "/image-generation",
    metadata: Optional[Dict[str, Any]] = None,
    log_prefix: str = "[Image Generation]",
    response_time: float = 0.0
) -> Dict[str, Any]:
    """
    Reusable usage tracking helper for all image operations.
    
    Extracted from generate_image() to be reused across all image operation functions.
    
    Args:
        user_id: User ID for tracking
        provider: Provider name (e.g., "wavespeed", "stability")
        model: Model name used
        operation_type: Type of operation (for logging)
        result_bytes: Generated/processed image bytes
        cost: Cost of the operation
        prompt: Optional prompt text (for request size calculation)
        endpoint: API endpoint path (for logging)
        metadata: Optional additional metadata
        log_prefix: Logging prefix for operation-specific logs
        
    Returns:
        Dictionary with tracking information (current_calls, cost, etc.)
    """
    try:
        from services.database import get_session_for_user
        db_track = get_session_for_user(user_id)
        try:
            from models.subscription_models import UsageSummary, APIUsageLog, APIProvider
            from services.subscription.provider_detection import detect_actual_provider
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
            
            # Get current values before update
            current_calls_before = getattr(summary, "stability_calls", 0) or 0
            current_cost_before = getattr(summary, "stability_cost", 0.0) or 0.0
            
            # Update image calls and cost
            new_calls = current_calls_before + 1
            new_cost = current_cost_before + cost
            
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
            summary.total_cost = (summary.total_cost or 0.0) + cost
            summary.total_calls = (summary.total_calls or 0) + 1
            summary.updated_at = datetime.utcnow()
            
            # Determine API provider based on actual provider
            api_provider = APIProvider.STABILITY  # Default for image generation
            
            # Detect actual provider name (WaveSpeed, Stability, HuggingFace, etc.)
            actual_provider = detect_actual_provider(
                provider_enum=api_provider,
                model_name=model,
                endpoint=endpoint
            )
            
            # Create usage log
            request_size = len(prompt.encode("utf-8")) if prompt else 0
            usage_log = APIUsageLog(
                user_id=user_id,
                provider=api_provider,
                endpoint=endpoint,
                method="POST",
                model_used=model or "unknown",
                actual_provider_name=actual_provider,  # Track actual provider (WaveSpeed, Stability, etc.)
                tokens_input=0,
                tokens_output=0,
                tokens_total=0,
                cost_input=0.0,
                cost_output=0.0,
                cost_total=cost,
                response_time=response_time,  # Use actual response time
                status_code=200,
                request_size=request_size,
                response_size=len(result_bytes),
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
            logger.info(f"{log_prefix} ✅ Successfully tracked usage: user {user_id} -> {operation_type} -> {new_calls} calls, ${cost:.4f}")
            
            # UNIFIED SUBSCRIPTION LOG - Shows before/after state in one message
            operation_name = operation_type.replace("-", " ").title()
            print(f"""
[SUBSCRIPTION] {operation_name}
├─ User: {user_id}
├─ Plan: {plan_name} ({tier})
├─ Provider: {provider}
├─ Actual Provider: {provider}
├─ Model: {model or 'unknown'}
├─ Calls: {current_calls_before} → {new_calls} / {image_limit_display}
├─ Cost: ${current_cost_before:.4f} → ${new_cost:.4f}
├─ Audio: {current_audio_calls} / {audio_limit if audio_limit > 0 else '∞'}
├─ Image Editing: {current_image_edit_calls} / {image_edit_limit if image_edit_limit > 0 else '∞'}
├─ Videos: {current_video_calls} / {video_limit if video_limit > 0 else '∞'}
└─ Status: ✅ Allowed & Tracked
""", flush=True)
            sys.stdout.flush()
            
            return {
                "current_calls": new_calls,
                "cost": cost,
                "total_cost": new_cost,
            }
            
        except Exception as track_error:
            logger.error(f"{log_prefix} ❌ Error tracking usage (non-blocking): {track_error}", exc_info=True)
            import traceback
            logger.error(f"{log_prefix} Full traceback: {traceback.format_exc()}")
            db_track.rollback()
            return {}
        finally:
            db_track.close()
    except Exception as usage_error:
        logger.error(f"{log_prefix} ❌ Failed to track usage: {usage_error}", exc_info=True)
        import traceback
        logger.error(f"{log_prefix} Full traceback: {traceback.format_exc()}")
        return {}


def generate_image(prompt: str, options: Optional[Dict[str, Any]] = None, user_id: Optional[str] = None) -> ImageGenerationResult:
    """Generate image with pre-flight validation.
    
    Args:
        prompt: Image generation prompt
        options: Image generation options (provider, model, width, height, etc.)
        user_id: User ID for subscription checking (optional, but required for validation)
    """
    # PRE-FLIGHT VALIDATION: Reuse extracted helper
    _validate_image_operation(
        user_id=user_id,
        operation_type="image-generation",
        num_operations=1,
        log_prefix="[Image Generation]"
    )
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
    
    # Detect Wavespeed models and remap provider if needed
    wavespeed_models = ["qwen-image", "ideogram-v3-turbo", "flux-kontext-pro"]
    if model_lower in wavespeed_models and provider_name != "wavespeed":
        logger.info("Remapping provider to wavespeed for model=%s", image_options.model)
        provider_name = "wavespeed"
    
    # Detect HuggingFace models and remap provider if needed
    if provider_name == "stability" and (model_lower.startswith("black-forest-labs/") or model_lower.startswith("runwayml/") or model_lower.startswith("stabilityai/flux")):
        logger.info("Remapping provider to huggingface for model=%s", image_options.model)
        provider_name = "huggingface"
    
    # Detect HuggingFace models when provider is not explicitly set
    if not opts.get("provider") and (model_lower.startswith("black-forest-labs/") or model_lower.startswith("runwayml/") or model_lower.startswith("stabilityai/flux")):
        logger.info("Auto-detecting provider as huggingface for model=%s", image_options.model)
        provider_name = "huggingface"

    if provider_name == "huggingface" and not image_options.model:
        # Provide a sensible default HF model if none specified
        image_options.model = "black-forest-labs/FLUX.1-Krea-dev"
    
    if provider_name == "wavespeed" and not image_options.model:
        # Default to cost-effective model: Qwen Image ($0.05/image, optimized for blog images)
        image_options.model = "qwen-image"

    logger.info("Generating image via provider=%s model=%s", provider_name, image_options.model)
    provider = _get_provider(provider_name)
    
    # Track response time
    import time
    start_time = time.time()
    result = provider.generate(image_options)
    response_time = time.time() - start_time
    
    # TRACK USAGE after successful API call - Reuse extracted helper
    if user_id and result and result.image_bytes:
        logger.info(f"[Image Generation] ✅ API call successful, tracking usage for user {user_id}")
        
        # Calculate cost from result metadata or estimate
        estimated_cost = 0.0
        if result.metadata and "estimated_cost" in result.metadata:
            estimated_cost = float(result.metadata["estimated_cost"])
        else:
            # Fallback: estimate based on provider/model (OSS-focused pricing)
            if provider_name == "wavespeed":
                if result.model and "qwen" in result.model.lower():
                    estimated_cost = 0.05  # Qwen Image: $0.05/image
                elif result.model and "ideogram" in result.model.lower():
                    estimated_cost = 0.10  # Ideogram V3 Turbo: $0.10/image
                else:
                    estimated_cost = 0.05  # Default to Qwen Image pricing
            elif provider_name == "stability":
                estimated_cost = 0.04
            else:
                estimated_cost = 0.05  # Default estimate
        
        # Reuse tracking helper
        _track_image_operation_usage(
            user_id=user_id,
            provider=provider_name,
            model=result.model or "unknown",
            operation_type="image-generation",
            result_bytes=result.image_bytes,
            cost=estimated_cost,
            prompt=prompt,
            endpoint="/image-generation",
            metadata=result.metadata,
            log_prefix="[Image Generation]",
            response_time=response_time
        )
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
    # PRE-FLIGHT VALIDATION: Reuse extracted helper
    _validate_image_operation(
        user_id=user_id,
        operation_type="character-image-generation",
        num_operations=1,
        log_prefix="[Character Image Generation]"
    )
    
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
        
        # TRACK USAGE after successful API call - Reuse extracted helper
        if user_id and image_bytes:
            logger.info(f"[Character Image Generation] ✅ API call successful, tracking usage for user {user_id}")
            
            # Character image cost (same as ideogram-v3-turbo)
            estimated_cost = 0.10
            
            # Reuse tracking helper
            _track_image_operation_usage(
                user_id=user_id,
                provider="wavespeed",
                model="ideogram-character",
                operation_type="character-image-generation",
                result_bytes=image_bytes,
                cost=estimated_cost,
                prompt=prompt,
                endpoint="/image-generation/character",
                metadata=None,
                log_prefix="[Character Image Generation]"
            )
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


def generate_image_edit(
    image_base64: str,
    prompt: str,
    operation: str = "general_edit",
    model: Optional[str] = None,
    options: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None
) -> ImageGenerationResult:
    """
    Generate edited image - REUSES validation and tracking helpers.
    
    Args:
        image_base64: Base64-encoded input image (or data URI)
        prompt: Edit instruction prompt
        operation: Type of edit operation (e.g., "general_edit", "inpaint", "outpaint")
        model: Model ID to use (default: auto-select based on provider)
        options: Additional options (mask_base64, negative_prompt, width, height, etc.)
        user_id: User ID for validation and tracking
        
    Returns:
        ImageGenerationResult with edited image
        
    Raises:
        HTTPException: If validation fails or editing fails
        ValueError: If options are invalid
    """
    # 1. REUSE: Validation helper
    _validate_image_operation(
        user_id=user_id,
        operation_type="image-edit",
        num_operations=1,
        log_prefix="[Image Edit]"
    )
    
    # 2. Determine provider from model or default to wavespeed
    opts = options or {}
    provider_name = opts.get("provider", "wavespeed")
    
    # If model is specified and starts with "wavespeed", use wavespeed provider
    if model and (model.startswith("wavespeed") or model.startswith("qwen") or model.startswith("flux") or model.startswith("nano-banana")):
        provider_name = "wavespeed"
    
    # 3. Get provider (REUSES provider pattern)
    try:
        provider = _get_edit_provider(provider_name)
    except ValueError as e:
        logger.error(f"[Image Edit] ❌ Provider error: {str(e)}")
        raise ValueError(f"Unsupported edit provider: {provider_name}")
    
    # 4. Prepare edit options
    edit_options = ImageEditOptions(
        image_base64=image_base64,
        prompt=prompt,
        operation=operation,
        mask_base64=opts.get("mask_base64"),
        negative_prompt=opts.get("negative_prompt"),
        model=model,
        width=opts.get("width"),
        height=opts.get("height"),
        guidance_scale=opts.get("guidance_scale"),
        steps=opts.get("steps"),
        seed=opts.get("seed"),
        extra=opts.get("extra"),
    )
    
    # 5. Edit image
    logger.info(f"[Image Edit] Starting edit: operation={operation}, model={model}, provider={provider_name}")
    try:
        result = provider.edit(edit_options)
    except Exception as e:
        logger.error(f"[Image Edit] ❌ Edit failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=502,
            detail={
                "error": "Image editing failed",
                "message": str(e)
            }
        )


def generate_face_swap(
    base_image_base64: str,
    face_image_base64: str,
    model: Optional[str] = None,
    options: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None
) -> ImageGenerationResult:
    """
    Generate face swap - REUSES validation and tracking helpers.
    
    Args:
        base_image_base64: Base64-encoded base image (or data URI)
        face_image_base64: Base64-encoded face image to swap (or data URI)
        model: Model ID to use (default: auto-select)
        options: Additional options (target_face_index, target_gender, etc.)
        user_id: User ID for validation and tracking
        
    Returns:
        ImageGenerationResult with swapped face image
        
    Raises:
        HTTPException: If validation fails or face swap fails
        ValueError: If options are invalid
    """
    # 1. REUSE: Validation helper
    _validate_image_operation(
        user_id=user_id,
        operation_type="face-swap",
        image_base64=base_image_base64,  # Use base image for validation
        log_prefix="[Face Swap]"
    )
    
    # 2. Get provider (default to wavespeed)
    provider_name = "wavespeed"
    provider = _get_face_swap_provider(provider_name)
    
    # 3. Prepare options
    face_swap_options = FaceSwapOptions(
        base_image_base64=base_image_base64,
        face_image_base64=face_image_base64,
        model=model,
        target_face_index=options.get("target_face_index") if options else None,
        target_gender=options.get("target_gender") if options else None,
        extra=options,
    )
    
    # 4. Swap face
    try:
        result = provider.swap_face(face_swap_options)
        
        # 5. REUSE: Tracking helper
        if user_id and result and result.image_bytes:
            logger.info(f"[Face Swap] ✅ API call successful, tracking usage for user {user_id}")
            
            # Get model cost
            model_id = model or (list(WaveSpeedFaceSwapProvider.SUPPORTED_MODELS.keys())[0] if WaveSpeedFaceSwapProvider.SUPPORTED_MODELS else "unknown")
            model_info = WaveSpeedFaceSwapProvider.SUPPORTED_MODELS.get(model_id, {})
            estimated_cost = model_info.get("cost", 0.025)  # Default to Pro cost
            
            # Reuse tracking helper
            _track_image_operation_usage(
                user_id=user_id,
                provider=provider_name,
                model=model_id,
                operation_type="face-swap",
                result_bytes=result.image_bytes,
                cost=estimated_cost,
                prompt=None,  # Face swap doesn't use prompts
                endpoint="/image-studio/face-swap/process",
                metadata={
                    "base_image_size": len(base_image_base64),
                    "face_image_size": len(face_image_base64),
                },
                log_prefix="[Face Swap]"
            )
        else:
            logger.warning(f"[Face Swap] ⚠️ Skipping usage tracking: user_id={user_id}, image_bytes={len(result.image_bytes) if result and result.image_bytes else 0} bytes")
        
        return result
        
    except HTTPException:
        raise
    except Exception as api_error:
        logger.error(f"[Face Swap] Face swap API failed: {api_error}")
        raise HTTPException(
            status_code=502,
            detail={
                "error": "Face swap failed",
                "message": str(api_error)
            }
        )
    
    # 6. REUSE: Tracking helper
    if user_id and result and result.image_bytes:
        logger.info(f"[Image Edit] ✅ API call successful, tracking usage for user {user_id}")
        
        # Get cost from result metadata or estimate
        estimated_cost = 0.0
        if result.metadata and "estimated_cost" in result.metadata:
            estimated_cost = float(result.metadata["estimated_cost"])
        else:
            # Fallback: estimate based on provider/model
            if provider_name == "wavespeed":
                # Default WaveSpeed edit cost
                estimated_cost = 0.02  # Default for most editing models
            else:
                estimated_cost = 0.05  # Default estimate
        
        # Reuse tracking helper
        _track_image_operation_usage(
            user_id=user_id,
            provider=provider_name,
            model=result.model or model or "unknown",
            operation_type="image-edit",
            result_bytes=result.image_bytes,
            cost=estimated_cost,
            prompt=prompt,
            endpoint="/image-generation/edit",
            metadata=result.metadata,
            log_prefix="[Image Edit]"
        )
    else:
        logger.warning(f"[Image Edit] ⚠️ Skipping usage tracking: user_id={user_id}, image_bytes={len(result.image_bytes) if result.image_bytes else 0} bytes")
    
    return result


async def generate_image_with_provider(
    prompt: str,
    user_id: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Async wrapper for generate_image to support step4_asset_routes.
    """
    # Construct options from kwargs
    options = kwargs.copy()
    
    try:
        # Run in threadpool since generate_image is blocking
        result = await run_in_threadpool(
            generate_image,
            prompt=prompt,
            options=options,
            user_id=user_id
        )
        
        image_base64 = base64.b64encode(result.image_bytes).decode('utf-8')
        
        return {
            "success": True,
            "image_base64": image_base64,
            "image_url": None, 
            "error": None,
            "metadata": result.metadata
        }
    except Exception as e:
        logger.error(f"Error in generate_image_with_provider: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def enhance_image_prompt(prompt: str, user_id: Optional[str] = None) -> str:
    """
    Enhance image prompt using LLM.
    Placeholder implementation.
    """
    return prompt


async def generate_image_variation(
    image: Any, 
    prompt: str,
    user_id: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate variation of an existing image.
    Placeholder implementation.
    """
    return {
        "success": False,
        "error": "Not implemented yet"
    }



