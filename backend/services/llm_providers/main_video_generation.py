"""
Main Video Generation Service

Provides a unified interface for AI video generation providers.
Supports:
- Text-to-video: Hugging Face Inference Providers, WaveSpeed models
- Image-to-video: WaveSpeed WAN 2.5, Kandinsky 5 Pro
Stubs included for Gemini (Veo 3) and OpenAI (Sora) for future use.
"""
from __future__ import annotations

import os
import base64
import io
import sys
import asyncio
from typing import Any, Dict, Optional, Union, Callable

from fastapi import HTTPException

try:
    from huggingface_hub import InferenceClient
    HF_HUB_AVAILABLE = True
except ImportError:
    HF_HUB_AVAILABLE = False
    InferenceClient = None

from ..onboarding.api_key_manager import APIKeyManager
from services.subscription import PricingService
from services.subscription.provider_detection import detect_actual_provider
from utils.logging import get_service_logger

logger = get_service_logger("video_generation_service")

class VideoProviderNotImplemented(Exception):
    pass


def _get_api_key(provider: str) -> Optional[str]:
    try:
        manager = APIKeyManager()
        mapping = {
            "huggingface": "hf_token",
            "wavespeed": "wavespeed",     # WaveSpeed API key
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


async def _generate_image_to_video_wavespeed(
    image_data: Optional[bytes] = None,
    image_base64: Optional[str] = None,
    prompt: str = "",
    duration: int = 5,
    resolution: str = "720p",
    model: str = "alibaba/wan-2.5/image-to-video",
    negative_prompt: Optional[str] = None,
    seed: Optional[int] = None,
    audio_base64: Optional[str] = None,
    enable_prompt_expansion: bool = True,
    progress_callback: Optional[Callable[[float, str], None]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate video from image using WaveSpeed (WAN 2.5 or Kandinsky 5 Pro).
    
    Args:
        image_data: Image bytes (required if image_base64 not provided)
        image_base64: Image in base64 or data URI format (required if image_data not provided)
        prompt: Text prompt describing the video motion
        duration: Video duration in seconds (5 or 10)
        resolution: Output resolution (480p, 720p, 1080p)
        model: Model to use (alibaba/wan-2.5/image-to-video, wavespeed/kandinsky5-pro/image-to-video)
        negative_prompt: Optional negative prompt
        seed: Optional random seed
        audio_base64: Optional audio file for synchronization
        enable_prompt_expansion: Enable prompt optimization
        
    Returns:
        Dictionary with video_bytes and metadata (cost, duration, resolution, width, height, etc.)
    """
    # Import here to avoid circular dependencies
    from services.image_studio.wan25_service import WAN25Service
    
    logger.info(f"[video_gen] WaveSpeed image-to-video: model={model}, resolution={resolution}, duration={duration}s")
    
    # Validate inputs
    if not image_data and not image_base64:
        raise ValueError("Either image_data or image_base64 must be provided for image-to-video")
    
    # Convert image_data to base64 if needed
    if image_data and not image_base64:
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        # Add data URI prefix if not present
        if not image_base64.startswith("data:"):
            image_base64 = f"data:image/png;base64,{image_base64}"
    
    # Initialize WAN25Service (handles both WAN 2.5 and Kandinsky 5 Pro)
    wan25_service = WAN25Service()
    
    try:
        # Generate video using WAN25Service (returns full metadata)
        result = await wan25_service.generate_video(
            image_base64=image_base64,
            prompt=prompt,
            audio_base64=audio_base64,
            resolution=resolution,
            duration=duration,
            negative_prompt=negative_prompt,
            seed=seed,
            enable_prompt_expansion=enable_prompt_expansion,
            progress_callback=progress_callback,
        )
        
        video_bytes = result.get("video_bytes")
        if not video_bytes:
            raise ValueError("WAN25Service returned no video bytes")
        
        if not isinstance(video_bytes, bytes):
            raise TypeError(f"Expected bytes from WAN25Service, got {type(video_bytes)}")
        
        if len(video_bytes) == 0:
            raise ValueError("Received empty video bytes from WaveSpeed API")
        
        logger.info(f"[video_gen] Successfully generated image-to-video: {len(video_bytes)} bytes")
        
        # Return video bytes with metadata
        return {
            "video_bytes": video_bytes,
            "prompt": result.get("prompt", prompt),
            "duration": result.get("duration", float(duration)),
            "model_name": result.get("model_name", model),
            "cost": result.get("cost", 0.0),
            "provider": result.get("provider", "wavespeed"),
            "resolution": result.get("resolution", resolution),
            "width": result.get("width", 1280),
            "height": result.get("height", 720),
            "metadata": result.get("metadata", {}),
            "source_video_url": result.get("source_video_url"),
            "prediction_id": result.get("prediction_id"),
        }
        
    except HTTPException:
        # Re-raise HTTPExceptions from WAN25Service
        raise
    except Exception as e:
        error_msg = str(e)
        error_type = type(e).__name__
        logger.error(f"[video_gen] WaveSpeed image-to-video error ({error_type}): {error_msg}", exc_info=True)
        raise HTTPException(
            status_code=502,
            detail={
                "error": f"WaveSpeed image-to-video generation failed: {error_msg}",
                "error_type": error_type
            }
        )


def _generate_with_gemini(prompt: str, **kwargs) -> bytes:
    raise VideoProviderNotImplemented("Gemini Veo 3 integration coming soon.")

def _generate_with_openai(prompt: str, **kwargs) -> bytes:
    raise VideoProviderNotImplemented("OpenAI Sora integration coming soon.")


async def _generate_text_to_video_wavespeed(
    prompt: str,
    duration: int = 5,
    resolution: str = "720p",
    model: str = "hunyuan-video-1.5",
    negative_prompt: Optional[str] = None,
    seed: Optional[int] = None,
    audio_base64: Optional[str] = None,
    enable_prompt_expansion: bool = True,
    progress_callback: Optional[Callable[[float, str], None]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate text-to-video using WaveSpeed models.
    
    Args:
        prompt: Text prompt describing the video
        duration: Video duration in seconds
        resolution: Output resolution (480p, 720p)
        model: Model identifier (e.g., "hunyuan-video-1.5")
        negative_prompt: Optional negative prompt
        seed: Optional random seed
        audio_base64: Optional audio (not supported by all models)
        enable_prompt_expansion: Enable prompt optimization (not supported by all models)
        progress_callback: Optional progress callback function
        **kwargs: Additional model-specific parameters
        
    Returns:
        Dictionary with video_bytes, prompt, duration, model_name, cost, etc.
    """
    from .video_generation.wavespeed_provider import get_wavespeed_text_to_video_service
    
    logger.info(f"[video_gen] WaveSpeed text-to-video: model={model}, resolution={resolution}, duration={duration}s")
    
    # Get the appropriate service for the model
    try:
        service = get_wavespeed_text_to_video_service(model)
    except ValueError as e:
        logger.error(f"[video_gen] Unsupported WaveSpeed text-to-video model: {model}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    
    # Generate video using the service
    try:
        result = await service.generate_video(
            prompt=prompt,
            duration=duration,
            resolution=resolution,
            negative_prompt=negative_prompt,
            seed=seed,
            audio_base64=audio_base64,
            enable_prompt_expansion=enable_prompt_expansion,
            progress_callback=progress_callback,
            **kwargs
        )
        
        logger.info(f"[video_gen] Successfully generated text-to-video: {len(result.get('video_bytes', b''))} bytes")
        return result
        
    except HTTPException:
        # Re-raise HTTPExceptions from service
        raise
    except Exception as e:
        error_msg = str(e)
        error_type = type(e).__name__
        logger.error(f"[video_gen] WaveSpeed text-to-video error ({error_type}): {error_msg}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"WaveSpeed text-to-video generation failed: {error_msg}",
                "type": error_type,
            }
        )


async def ai_video_generate(
    prompt: Optional[str] = None,
    image_data: Optional[bytes] = None,
    image_base64: Optional[str] = None,
    operation_type: str = "text-to-video",
    provider: str = "huggingface",
    user_id: Optional[str] = None,
    progress_callback: Optional[Callable[[float, str], None]] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    Unified video generation entry point for ALL video operations.
    
    Supports:
    - text-to-video: prompt required, provider: 'huggingface', 'wavespeed', 'gemini' (stub), 'openai' (stub)
    - image-to-video: image_data or image_base64 required, provider: 'wavespeed'
    
    Args:
        prompt: Text prompt (required for text-to-video)
        image_data: Image bytes (required for image-to-video if image_base64 not provided)
        image_base64: Image base64 string (required for image-to-video if image_data not provided)
        operation_type: "text-to-video" or "image-to-video" (default: "text-to-video")
        provider: Provider name (default: "huggingface" for text-to-video, "wavespeed" for image-to-video)
        user_id: Required for subscription/usage tracking
        progress_callback: Optional function(progress: float, message: str) -> None
            Called at key stages: submission (10%), polling (20-80%), completion (100%)
        **kwargs: Model-specific parameters:
            - For text-to-video: num_frames, guidance_scale, num_inference_steps, negative_prompt, seed, model
            - For image-to-video: duration, resolution, negative_prompt, seed, audio_base64, enable_prompt_expansion, model
    
    Returns:
        Dictionary with:
        - video_bytes: Raw video bytes (mp4/webm depending on provider)
        - prompt: The prompt used (may be enhanced)
        - duration: Video duration in seconds
        - model_name: Model used for generation
        - cost: Cost of generation
        - provider: Provider name
        - resolution: Video resolution (for image-to-video)
        - width: Video width in pixels (for image-to-video)
        - height: Video height in pixels (for image-to-video)
        - metadata: Additional metadata dict
    """
    logger.info(f"[video_gen] operation={operation_type}, provider={provider}")

    # Enforce authentication usage like text gen does
    if not user_id:
        raise RuntimeError("user_id is required for subscription/usage tracking.")

    # Validate operation type and required inputs
    if operation_type == "text-to-video":
        if not prompt:
            raise ValueError("prompt is required for text-to-video generation")
        # Set default provider if not specified
        if provider == "huggingface" and "model" not in kwargs:
            kwargs.setdefault("model", "tencent/HunyuanVideo")
    elif operation_type == "image-to-video":
        if not image_data and not image_base64:
            raise ValueError("image_data or image_base64 is required for image-to-video generation")
        # Set default provider and model for image-to-video
        if provider not in ["wavespeed"]:
            logger.warning(f"[video_gen] Provider {provider} not supported for image-to-video, defaulting to wavespeed")
            provider = "wavespeed"
        if "model" not in kwargs:
            kwargs.setdefault("model", "alibaba/wan-2.5/image-to-video")
        # Set defaults for image-to-video
        kwargs.setdefault("duration", 5)
        kwargs.setdefault("resolution", "720p")
    else:
        raise ValueError(f"Invalid operation_type: {operation_type}. Must be 'text-to-video' or 'image-to-video'")

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
    
    logger.info(f"[Video Generation] ✅ Pre-flight validation passed - proceeding with {operation_type}")

    # Progress callback: Initial submission
    if progress_callback:
        progress_callback(10.0, f"Submitting {operation_type} request to {provider}...")

    # Generate video based on operation type
    model_name = kwargs.get("model", _get_default_model(operation_type, provider))
    
    # Track response time for video generation
    import time
    start_time = time.time()
    
    try:
        if operation_type == "text-to-video":
            if provider == "huggingface":
                video_bytes = _generate_with_huggingface(
                    prompt=prompt,
                    **kwargs,
                )
                # For text-to-video, create metadata dict (HuggingFace doesn't return metadata)
                result_dict = {
                    "video_bytes": video_bytes,
                    "prompt": prompt,
                    "duration": kwargs.get("duration", 5.0),
                    "model_name": model_name,
                    "cost": 0.10,  # Default cost, will be calculated in track_video_usage
                    "provider": provider,
                    "resolution": kwargs.get("resolution", "720p"),
                    "width": 1280,  # Default, actual may vary
                    "height": 720,  # Default, actual may vary
                    "metadata": {},
                }
            elif provider == "wavespeed":
                # WaveSpeed text-to-video - use unified service
                result_dict = await _generate_text_to_video_wavespeed(
                    prompt=prompt,
                    progress_callback=progress_callback,
                    **kwargs,
                )
            elif provider == "gemini":
                video_bytes = _generate_with_gemini(prompt=prompt, **kwargs)
                result_dict = {
                    "video_bytes": video_bytes,
                    "prompt": prompt,
                    "duration": kwargs.get("duration", 5.0),
                    "model_name": model_name,
                    "cost": 0.10,
                    "provider": provider,
                    "resolution": kwargs.get("resolution", "720p"),
                    "width": 1280,
                    "height": 720,
                    "metadata": {},
                }
            elif provider == "openai":
                video_bytes = _generate_with_openai(prompt=prompt, **kwargs)
                result_dict = {
                    "video_bytes": video_bytes,
                    "prompt": prompt,
                    "duration": kwargs.get("duration", 5.0),
                    "model_name": model_name,
                    "cost": 0.10,
                    "provider": provider,
                    "resolution": kwargs.get("resolution", "720p"),
                    "width": 1280,
                    "height": 720,
                    "metadata": {},
                }
            else:
                raise RuntimeError(f"Unknown provider for text-to-video: {provider}")
        
        elif operation_type == "image-to-video":
            if provider == "wavespeed":
                # Progress callback: Starting generation
                if progress_callback:
                    progress_callback(20.0, "Video generation in progress...")
                
                # Handle async call from sync context
                # Since ai_video_generate is sync, we need to run async function
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # We're in an async context - use ThreadPoolExecutor to run in new event loop
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(
                                asyncio.run,
                                _generate_image_to_video_wavespeed(
                                    image_data=image_data,
                                    image_base64=image_base64,
                                    prompt=prompt or kwargs.get("prompt", ""),
                                    progress_callback=progress_callback,
                                    **kwargs
                                )
                            )
                            result_dict = future.result()
                    else:
                        # Event loop exists but not running - use it
                        result_dict = loop.run_until_complete(_generate_image_to_video_wavespeed(
                            image_data=image_data,
                            image_base64=image_base64,
                            prompt=prompt or kwargs.get("prompt", ""),
                            progress_callback=progress_callback,
                            **kwargs
                        ))
                except RuntimeError:
                    # No event loop exists, create a new one
                    result_dict = asyncio.run(_generate_image_to_video_wavespeed(
                        image_data=image_data,
                        image_base64=image_base64,
                        prompt=prompt or kwargs.get("prompt", ""),
                        progress_callback=progress_callback,
                        **kwargs
                    ))
                video_bytes = result_dict["video_bytes"]
                model_name = result_dict.get("model_name", model_name)
                
                # Progress callback: Processing result
                if progress_callback:
                    progress_callback(90.0, "Processing video result...")
            else:
                raise RuntimeError(f"Unknown provider for image-to-video: {provider}. Only 'wavespeed' is supported.")
        
        # Track usage (same pattern as text generation)
        # Use cost from result_dict if available, otherwise calculate
        response_time = time.time() - start_time
        cost_override = result_dict.get("cost") if operation_type == "image-to-video" else kwargs.get("cost_override")
        track_video_usage(
            user_id=user_id,
            provider=provider,
            model_name=model_name,
            prompt=result_dict.get("prompt", prompt or ""),
            video_bytes=video_bytes,
            cost_override=cost_override,
            response_time=response_time,
        )

        # Progress callback: Complete
        if progress_callback:
            progress_callback(100.0, "Video generation complete!")

        return result_dict
        
    except HTTPException:
        # Re-raise HTTPExceptions (e.g., from validation or API errors)
        raise
    except Exception as e:
        logger.error(f"[video_gen] Error during video generation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail={"error": str(e)})


def _get_default_model(operation_type: str, provider: str) -> str:
    """Get default model for operation type and provider."""
    defaults = {
        ("text-to-video", "huggingface"): "tencent/HunyuanVideo",
        ("text-to-video", "wavespeed"): "hunyuan-video-1.5",
        ("image-to-video", "wavespeed"): "alibaba/wan-2.5/image-to-video",
    }
    return defaults.get((operation_type, provider), "hunyuan-video-1.5")


def track_video_usage(
    *,
    user_id: str,
    provider: str,
    model_name: str,
    prompt: str,
    video_bytes: bytes,
    cost_override: Optional[float] = None,
    response_time: float = 0.0,
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

        # Detect actual provider name (WaveSpeed, HuggingFace, Google, etc.)
        actual_provider = detect_actual_provider(
            provider_enum=APIProvider.VIDEO,
            model_name=model_name,
            endpoint=f"/video-generation/{provider}"
        )
        
        usage_log = APIUsageLog(
            user_id=user_id,
            provider=APIProvider.VIDEO,
            endpoint=f"/video-generation/{provider}",
            method="POST",
            model_used=model_name,
            actual_provider_name=actual_provider,  # Track actual provider (WaveSpeed, HuggingFace, etc.)
            tokens_input=0,
            tokens_output=0,
            tokens_total=0,
            cost_input=0.0,
            cost_output=0.0,
            cost_total=cost_per_video,
            response_time=response_time,  # Use actual response time
            status_code=200,
            request_size=len((prompt or "").encode("utf-8")),
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


