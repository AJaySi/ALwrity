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
import sys
from typing import Any, Dict, Optional, Union

from fastapi import HTTPException

try:
    from huggingface_hub import InferenceClient
    HF_HUB_AVAILABLE = True
except ImportError:
    HF_HUB_AVAILABLE = False
    InferenceClient = None

from ..onboarding.api_key_manager import APIKeyManager
from services.subscription import PricingService
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
    According to HF docs, text_to_video() should return bytes directly.
    """
    logger.debug(f"[video_gen] _coerce_video_bytes received type: {type(output)}")
    
    # Most common case: bytes directly
    if isinstance(output, (bytes, bytearray, memoryview)):
        logger.debug(f"[video_gen] Output is bytes: {len(output)} bytes")
        return bytes(output)

    # Handle file-like objects
    if hasattr(output, "read"):
        logger.debug("[video_gen] Output has read() method, reading...")
        data = output.read()
        if isinstance(data, (bytes, bytearray, memoryview)):
            return bytes(data)
        raise TypeError(f"File-like object returned non-bytes: {type(data)}")

    # Objects with direct attribute access
    if hasattr(output, "video"):
        logger.debug("[video_gen] Output has 'video' attribute")
        data = getattr(output, "video")
        if isinstance(data, (bytes, bytearray, memoryview)):
            return bytes(data)
        if hasattr(data, "read"):
            return bytes(data.read())
    
    if hasattr(output, "bytes"):
        logger.debug("[video_gen] Output has 'bytes' attribute")
        data = getattr(output, "bytes")
        if isinstance(data, (bytes, bytearray, memoryview)):
            return bytes(data)
        if hasattr(data, "read"):
            return bytes(data.read())

    # Dict handling - but this shouldn't happen with text_to_video()
    if isinstance(output, dict):
        logger.warning(f"[video_gen] Received dict output (unexpected): keys={list(output.keys())}")
        # Try to get video key safely - use .get() to avoid KeyError
        data = output.get("video")
        if data is not None:
            if isinstance(data, (bytes, bytearray, memoryview)):
                return bytes(data)
            if hasattr(data, "read"):
                return bytes(data.read())
        # Try other common keys
        for key in ["data", "content", "file", "result", "output"]:
            data = output.get(key)
            if data is not None:
                if isinstance(data, (bytes, bytearray, memoryview)):
                    return bytes(data)
                if hasattr(data, "read"):
                    return bytes(data.read())
        raise TypeError(f"Dict output has no recognized video key. Keys: {list(output.keys())}")

    # String handling (base64)
    if isinstance(output, str):
        logger.debug("[video_gen] Output is string, attempting base64 decode")
        if output.startswith("data:"):
            _, encoded = output.split(",", 1)
            return base64.b64decode(encoded)
        try:
            return base64.b64decode(output)
        except Exception as exc:
            raise TypeError(f"Unable to decode string video payload: {exc}") from exc

    # Fallback: try to use output directly
    logger.warning(f"[video_gen] Unexpected output type: {type(output)}, attempting direct conversion")
    try:
        if hasattr(output, "__bytes__"):
            return bytes(output)
    except Exception:
        pass

    raise TypeError(f"Unsupported video payload type: {type(output)}. Output: {str(output)[:200]}")


def _generate_with_huggingface(
    prompt: str,
    num_frames: int = 24 * 4,
    guidance_scale: float = 7.5,
    num_inference_steps: int = 30,
    negative_prompt: Optional[str] = None,
    seed: Optional[int] = None,
    model: str = "tencent/HunyuanVideo",
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
        "[video_gen] HuggingFace request model=%s frames=%s steps=%s mode=text-to-video",
        model,
        num_frames,
        num_inference_steps,
    )

    try:
        logger.info("[video_gen] Calling client.text_to_video()...")
        video_output = client.text_to_video(
            prompt=prompt,
            model=model,
            **params,
        )
        
        logger.info(f"[video_gen] text_to_video() returned type: {type(video_output)}")
        if isinstance(video_output, dict):
            logger.info(f"[video_gen] Dict keys: {list(video_output.keys())}")
        elif hasattr(video_output, "__dict__"):
            logger.info(f"[video_gen] Object attributes: {dir(video_output)}")

        video_bytes = _coerce_video_bytes(video_output)

        if not isinstance(video_bytes, bytes):
            raise TypeError(f"Expected bytes from text_to_video, got {type(video_bytes)}")

        if len(video_bytes) == 0:
            raise ValueError("Received empty video bytes from Hugging Face API")

        logger.info(f"[video_gen] Successfully generated video: {len(video_bytes)} bytes")
        return video_bytes

    except KeyError as e:
        error_msg = str(e)
        logger.error(f"[video_gen] HF KeyError: {error_msg}", exc_info=True)
        logger.error(f"[video_gen] This suggests the API response format is unexpected. Check logs above for response type.")
        raise HTTPException(status_code=502, detail={
            "error": f"Hugging Face API returned unexpected response format: {error_msg}",
            "error_type": "KeyError",
            "hint": "The API response may have changed. Check server logs for details."
        })
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
    **kwargs,
) -> bytes:
    """
    Unified video generation entry point.

    - provider: 'huggingface' (default), 'gemini' (veo3 stub), 'openai' (sora stub)
    - kwargs: num_frames, guidance_scale, num_inference_steps, negative_prompt, seed, model

    Returns raw video bytes (mp4/webm depending on provider).
    """
    logger.info(f"[video_gen] provider={provider}")

    # Enforce authentication usage like text gen does
    if not user_id:
        raise RuntimeError("user_id is required for subscription/usage tracking.")

    # PRE-FLIGHT VALIDATION: Validate video generation before API call
    # MUST happen BEFORE any API calls - return immediately if validation fails
    from services.database import get_db
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
                **kwargs,
            )
        elif provider == "gemini":
            video_bytes = _generate_with_gemini(prompt=prompt, **kwargs)
        elif provider == "openai":
            video_bytes = _generate_with_openai(prompt=prompt, **kwargs)
        else:
            raise RuntimeError(f"Unknown video provider: {provider}")
        
        track_video_usage(
            user_id=user_id,
            provider=provider,
            model_name=model_name,
            prompt=prompt,
            video_bytes=video_bytes,
        )

        return video_bytes
        
    except HTTPException:
        # Re-raise HTTPExceptions (e.g., from validation or API errors)
        raise
    except Exception as e:
        logger.error(f"[video_gen] Error during video generation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail={"error": str(e)})


def track_video_usage(
    *,
    user_id: str,
    provider: str,
    model_name: str,
    prompt: str,
    video_bytes: bytes,
    cost_override: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Track subscription usage for any video generation (text-to-video or image-to-video).
    """
    from datetime import datetime

    from models.subscription_models import APIProvider, APIUsageLog, UsageSummary
    from services.database import get_db

    db_track = next(get_db())
    try:
        logger.info(f"[video_gen] Starting usage tracking for user={user_id}, provider={provider}, model={model_name}")
        pricing_service_track = PricingService(db_track)
        current_period = pricing_service_track.get_current_billing_period(user_id) or datetime.now().strftime("%Y-%m")
        logger.debug(f"[video_gen] Billing period: {current_period}")

        usage_summary = (
            db_track.query(UsageSummary)
            .filter(
                UsageSummary.user_id == user_id,
                UsageSummary.billing_period == current_period,
            )
            .first()
        )

        if not usage_summary:
            logger.debug(f"[video_gen] Creating new UsageSummary for user={user_id}, period={current_period}")
            usage_summary = UsageSummary(
                user_id=user_id,
                billing_period=current_period,
            )
            db_track.add(usage_summary)
            db_track.commit()
            db_track.refresh(usage_summary)
        else:
            logger.debug(f"[video_gen] Found existing UsageSummary: video_calls={getattr(usage_summary, 'video_calls', 0)}")

        cost_info = pricing_service_track.get_pricing_for_provider_model(
            APIProvider.VIDEO,
            model_name,
        )
        default_cost = 0.10
        if cost_info and cost_info.get("cost_per_request") is not None:
            default_cost = cost_info["cost_per_request"]
        cost_per_video = cost_override if cost_override is not None else default_cost
        logger.debug(f"[video_gen] Cost per video: ${cost_per_video} (override={cost_override}, default={default_cost})")

        current_video_calls_before = getattr(usage_summary, "video_calls", 0) or 0
        current_video_cost = getattr(usage_summary, "video_cost", 0.0) or 0.0
        usage_summary.video_calls = current_video_calls_before + 1
        usage_summary.video_cost = current_video_cost + cost_per_video
        usage_summary.total_calls = (usage_summary.total_calls or 0) + 1
        usage_summary.total_cost = (usage_summary.total_cost or 0.0) + cost_per_video
        # Ensure the object is in the session
        db_track.add(usage_summary)
        logger.debug(f"[video_gen] Updated usage_summary: video_calls={current_video_calls_before} → {usage_summary.video_calls}")

        limits = pricing_service_track.get_user_limits(user_id)
        plan_name = limits.get("plan_name", "unknown") if limits else "unknown"
        tier = limits.get("tier", "unknown") if limits else "unknown"
        video_limit = limits["limits"].get("video_calls", 0) if limits else 0
        current_image_calls = getattr(usage_summary, "stability_calls", 0) or 0
        image_limit = limits["limits"].get("stability_calls", 0) if limits else 0
        current_image_edit_calls = getattr(usage_summary, "image_edit_calls", 0) or 0
        image_edit_limit = limits["limits"].get("image_edit_calls", 0) if limits else 0
        current_audio_calls = getattr(usage_summary, "audio_calls", 0) or 0
        audio_limit = limits["limits"].get("audio_calls", 0) if limits else 0
        # Only show ∞ for Enterprise tier when limit is 0 (unlimited)
        audio_limit_display = audio_limit if (audio_limit > 0 or tier != 'enterprise') else '∞'

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
            response_time=0.0,
            status_code=200,
            request_size=len(prompt.encode("utf-8")),
            response_size=len(video_bytes),
            billing_period=current_period,
        )
        db_track.add(usage_log)
        logger.debug(f"[video_gen] Flushing changes before commit...")
        db_track.flush()
        logger.debug(f"[video_gen] Committing usage tracking changes...")
        db_track.commit()
        db_track.refresh(usage_summary)
        logger.debug(f"[video_gen] Commit successful. Final video_calls: {usage_summary.video_calls}, video_cost: {usage_summary.video_cost}")

        video_limit_display = video_limit if video_limit > 0 else '∞'

        log_message = f"""
[SUBSCRIPTION] Video Generation
├─ User: {user_id}
├─ Plan: {plan_name} ({tier})
├─ Provider: video
├─ Actual Provider: {provider}
├─ Model: {model_name or 'default'}
├─ Calls: {current_video_calls_before} → {usage_summary.video_calls} / {video_limit_display}
├─ Images: {current_image_calls} / {image_limit if image_limit > 0 else '∞'}
├─ Image Editing: {current_image_edit_calls} / {image_edit_limit if image_edit_limit > 0 else '∞'}
├─ Audio: {current_audio_calls} / {audio_limit_display}
└─ Status: ✅ Allowed & Tracked
"""
        logger.info(log_message)
        return {
            "previous_calls": current_video_calls_before,
            "current_calls": usage_summary.video_calls,
            "video_limit": video_limit,
            "video_limit_display": video_limit_display,
            "cost_per_video": cost_per_video,
            "total_video_cost": usage_summary.video_cost,
        }
    except Exception as track_error:
        logger.error(f"[video_gen] Error tracking usage: {track_error}", exc_info=True)
        logger.error(f"[video_gen] Exception type: {type(track_error).__name__}", exc_info=True)
        db_track.rollback()
    finally:
        db_track.close()


