"""
Main Video Generation Service

Provides a unified interface for AI video generation providers.
Initial support: Hugging Face Inference Providers (text-to-video).
Stubs included for Gemini (Veo 3) and OpenAI (Sora) for future use.
"""
from __future__ import annotations

import os
import base64
import io
from typing import Any, Dict, Optional, Union

from fastapi import HTTPException

try:
    from huggingface_hub import InferenceClient
    HF_HUB_AVAILABLE = True
except ImportError:
    HF_HUB_AVAILABLE = False
    InferenceClient = None

from ..onboarding.api_key_manager import APIKeyManager
from utils.logger_utils import get_service_logger

logger = get_service_logger("video_generation_service")


class VideoProviderNotImplemented(Exception):
    pass


def _get_api_key(provider: str) -> Optional[str]:
    try:
        manager = APIKeyManager()
        mapping = {
            "huggingface": "hf_token",
            "gemini": "gemini",          # placeholder for Veo 3
            "openai": "openai_api_key",  # placeholder for Sora
        }
        return manager.get_api_key(mapping.get(provider, provider))
    except Exception as e:
        logger.error(f"[video_gen] Failed to read API key for {provider}: {e}")
        return None


def _coerce_video_bytes(output: Any) -> bytes:
    """
    Normalizes the different return shapes that huggingface_hub may emit for video tasks.
    Depending on the provider/library version we may get:
      - raw bytes
      - an object with `.video` or `.bytes` attributes (plus optional `.save`)
      - a dict containing a `video` key with bytes/base64 data
    """
    data: Union[bytes, bytearray, memoryview, io.BufferedIOBase, None] = None

    if isinstance(output, (bytes, bytearray, memoryview)):
        return bytes(output)

    # Objects with direct attribute access
    if hasattr(output, "video"):
        data = getattr(output, "video")
    elif hasattr(output, "bytes"):
        data = getattr(output, "bytes")
    elif isinstance(output, dict) and "video" in output:
        data = output["video"]
    else:
        data = output

    # Handle file-like responses
    if hasattr(data, "read"):
        data = data.read()

    if isinstance(data, (bytes, bytearray, memoryview)):
        return bytes(data)

    if isinstance(data, str):
        # Expecting data URI or raw base64 string
        if data.startswith("data:"):
            _, encoded = data.split(",", 1)
            return base64.b64decode(encoded)
        try:
            return base64.b64decode(data)
        except Exception as exc:
            raise TypeError(f"Unable to decode string video payload: {exc}") from exc

    raise TypeError(f"Unsupported video payload type: {type(data)}")


def _generate_with_huggingface(
    prompt: str,
    num_frames: int = 24 * 4,
    guidance_scale: float = 7.5,
    num_inference_steps: int = 30,
    negative_prompt: Optional[str] = None,
    seed: Optional[int] = None,
    model: str = "tencent/HunyuanVideo",
    input_image_bytes: Optional[bytes] = None,
) -> bytes:
    """
    Generates video bytes using Hugging Face's InferenceClient.
    """
    if not HF_HUB_AVAILABLE:
        raise RuntimeError("huggingface_hub is not installed. Install with: pip install huggingface_hub")

    token = _get_api_key("huggingface")
    if not token:
        raise RuntimeError("HF token not configured. Set an hf_token in APIKeyManager.")

    client = InferenceClient(
        model=model,
        provider="fal-ai",
        token=token,
    )
    logger.info("[video_gen] Using HuggingFace provider 'fal-ai'")

    params: Dict[str, Any] = {
        "num_frames": num_frames,
        "guidance_scale": guidance_scale,
        "num_inference_steps": num_inference_steps,
    }
    if negative_prompt:
        params["negative_prompt"] = negative_prompt if isinstance(negative_prompt, list) else [negative_prompt]
    if seed is not None:
        params["seed"] = seed

    logger.info(
        "[video_gen] HuggingFace request model=%s frames=%s steps=%s mode=%s",
        model,
        num_frames,
        num_inference_steps,
        "image-to-video" if input_image_bytes else "text-to-video",
    )

    try:
        call_kwargs = {**params, "model": model}
        if input_image_bytes:
            video_output = client.image_to_video(
                image=input_image_bytes,
                prompt=prompt,
                **call_kwargs,
            )
        else:
            video_output = client.text_to_video(
                prompt,
                **call_kwargs,
            )

        video_bytes = _coerce_video_bytes(video_output)

        if not isinstance(video_bytes, bytes):
            raise TypeError(f"Expected bytes from text_to_video, got {type(video_bytes)}")

        if len(video_bytes) == 0:
            raise ValueError("Received empty video bytes from Hugging Face API")

        logger.info(f"[video_gen] Successfully generated video: {len(video_bytes)} bytes")
        return video_bytes

    except Exception as e:
        error_msg = str(e)
        error_type = type(e).__name__
        logger.error(f"[video_gen] HF error ({error_type}): {error_msg}", exc_info=True)
        raise HTTPException(status_code=502, detail={
            "error": f"Hugging Face video generation failed: {error_msg}",
            "error_type": error_type
        })


def _generate_with_gemini(prompt: str, **kwargs) -> bytes:
    raise VideoProviderNotImplemented("Gemini Veo 3 integration coming soon.")

def _generate_with_openai(prompt: str, **kwargs) -> bytes:
    raise VideoProviderNotImplemented("OpenAI Sora integration coming soon.")


def ai_video_generate(
    prompt: str,
    provider: str = "huggingface",
    user_id: Optional[str] = None,
    input_image_bytes: Optional[bytes] = None,
    **kwargs,
) -> bytes:
    """
    Unified video generation entry point.

    - provider: 'huggingface' (default), 'gemini' (veo3 stub), 'openai' (sora stub)
    - kwargs: num_frames, guidance_scale, num_inference_steps, negative_prompt, seed, model
    - input_image_bytes: optional bytes for image-to-video flows (uses image as motion anchor)

    Returns raw video bytes (mp4/webm depending on provider).
    """
    logger.info(f"[video_gen] provider={provider}")

    # Enforce authentication usage like text gen does
    if not user_id:
        raise RuntimeError("user_id is required for subscription/usage tracking.")

    # PRE-FLIGHT VALIDATION: Validate video generation before API call
    # MUST happen BEFORE any API calls - return immediately if validation fails
    from services.database import get_db
    from services.subscription import PricingService
    from services.subscription.preflight_validator import validate_video_generation_operations
    from fastapi import HTTPException
    
    db = next(get_db())
    try:
        pricing_service = PricingService(db)
        # Raises HTTPException immediately if validation fails - frontend gets immediate response
        validate_video_generation_operations(
            pricing_service=pricing_service,
            user_id=user_id
        )
    except HTTPException:
        # Re-raise immediately - don't proceed with API call
        logger.error(f"[Video Generation] ❌ Pre-flight validation failed - blocking API call")
        raise
    finally:
        db.close()
    
    logger.info(f"[Video Generation] ✅ Pre-flight validation passed - proceeding with video generation")

    # Generate video
    model_name = kwargs.get("model", "tencent/HunyuanVideo")
    try:
        if provider == "huggingface":
            video_bytes = _generate_with_huggingface(
                prompt=prompt,
                input_image_bytes=input_image_bytes,
                **kwargs,
            )
        elif provider == "gemini":
            video_bytes = _generate_with_gemini(prompt=prompt, **kwargs)
        elif provider == "openai":
            video_bytes = _generate_with_openai(prompt=prompt, **kwargs)
        else:
            raise RuntimeError(f"Unknown video provider: {provider}")
        
        # Track usage AFTER successful generation
        db_track = next(get_db())
        try:
            from models.subscription_models import APIProvider, UsageSummary, APIUsageLog
            from datetime import datetime
            from services.subscription import PricingService
            
            # Create pricing service for tracking (uses same DB session)
            pricing_service_track = PricingService(db_track)
            
            # Get current billing period
            current_period = pricing_service_track.get_current_billing_period(user_id) or datetime.now().strftime("%Y-%m")
            
            # Get or create usage summary
            usage_summary = db_track.query(UsageSummary).filter(
                UsageSummary.user_id == user_id,
                UsageSummary.billing_period == current_period
            ).first()
            
            if not usage_summary:
                usage_summary = UsageSummary(
                    user_id=user_id,
                    billing_period=current_period
                )
                db_track.add(usage_summary)
                db_track.commit()
            
            # Calculate cost using pricing service
            cost_info = pricing_service_track.get_pricing_for_provider_model(
                APIProvider.VIDEO,
                model_name
            )
            cost_per_video = cost_info.get('cost_per_request', 0.10) if cost_info else 0.10
            
            # Get "before" state for unified log
            current_video_calls_before = getattr(usage_summary, 'video_calls', 0) or 0
            current_video_cost = getattr(usage_summary, 'video_cost', 0.0) or 0.0
            
            # Increment video_calls and track cost
            new_video_calls = current_video_calls_before + 1
            usage_summary.video_calls = new_video_calls
            usage_summary.video_cost = current_video_cost + cost_per_video
            usage_summary.total_calls = (usage_summary.total_calls or 0) + 1
            usage_summary.total_cost = (usage_summary.total_cost or 0.0) + cost_per_video
            
            # Get plan details for unified log (before commit, in case commit fails)
            limits = pricing_service_track.get_user_limits(user_id)
            plan_name = limits.get('plan_name', 'unknown') if limits else 'unknown'
            tier = limits.get('tier', 'unknown') if limits else 'unknown'
            video_limit = limits['limits'].get("video_calls", 0) if limits else 0
            
            # Get image and image editing stats for unified log
            current_image_calls = getattr(usage_summary, "stability_calls", 0) or 0
            image_limit = limits['limits'].get("stability_calls", 0) if limits else 0
            current_image_edit_calls = getattr(usage_summary, "image_edit_calls", 0) or 0
            image_edit_limit = limits['limits'].get("image_edit_calls", 0) if limits else 0
            
            # Create usage log entry for audit trail
            usage_log = APIUsageLog(
                user_id=user_id,
                provider=APIProvider.VIDEO,
                endpoint=f"/video-generation/{provider}",
                method="POST",
                model_used=model_name,
                tokens_input=0,
                tokens_output=0,
                tokens_total=0,
                cost_input=0.0,
                cost_output=0.0,
                cost_total=cost_per_video,
                response_time=0.0,  # Could track actual time if needed
                status_code=200,
                request_size=len(prompt.encode('utf-8')),
                response_size=len(video_bytes),
                billing_period=current_period
            )
            db_track.add(usage_log)
            
            db_track.commit()
            logger.info(f"[video_gen] ✅ Successfully tracked usage: user {user_id} -> 1 video call, ${cost_per_video:.4f} cost")
            
            # UNIFIED SUBSCRIPTION LOG - Shows before/after state in one message
            # Flush immediately to ensure it's visible in console/logs
            import sys
            log_message = f"""
[SUBSCRIPTION] Video Generation
├─ User: {user_id}
├─ Plan: {plan_name} ({tier})
├─ Provider: video
├─ Actual Provider: {provider}
├─ Model: {model_name or 'default'}
├─ Calls: {current_video_calls_before} → {new_video_calls} / {video_limit if video_limit > 0 else '∞'}
├─ Images: {current_image_calls} / {image_limit if image_limit > 0 else '∞'}
├─ Image Editing: {current_image_edit_calls} / {image_edit_limit if image_edit_limit > 0 else '∞'}
└─ Status: ✅ Allowed & Tracked
"""
            print(log_message, flush=True)
            sys.stdout.flush()
            
        except Exception as track_error:
            logger.error(f"[video_gen] Error tracking usage: {track_error}", exc_info=True)
            db_track.rollback()
            # Don't fail video generation if tracking fails - video is already generated
        finally:
            db_track.close()
        
        return video_bytes
        
    except HTTPException:
        # Re-raise HTTPExceptions (e.g., from validation or API errors)
        raise
    except Exception as e:
        logger.error(f"[video_gen] Error during video generation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail={"error": str(e)})


