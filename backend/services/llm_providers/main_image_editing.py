from __future__ import annotations

import os
import io
import base64
import logging
from typing import Optional, Dict, Any
from PIL import Image

from .image_generation import (
    ImageGenerationOptions,
    ImageGenerationResult,
)
from .image_generation.base import ImageEditOptions
from .image_generation.wavespeed_edit_provider import WaveSpeedEditProvider

from utils.logger_utils import get_service_logger

try:
    from huggingface_hub import InferenceClient
    HF_HUB_AVAILABLE = True
except ImportError:
    HF_HUB_AVAILABLE = False


logger = get_service_logger("image_editing.facade")


DEFAULT_IMAGE_EDIT_MODEL = os.getenv(
    "WAVESPEED_IMAGE_EDIT_MODEL",
    "qwen-edit-plus",
)


def _select_provider(explicit: Optional[str]) -> str:
    """
    Select the appropriate image editing provider.
    
    Priority:
    1. Explicitly requested provider
    2. WaveSpeed (if API key available) - Preferred for quality/speed
    3. Hugging Face (fallback)
    """
    if explicit:
        return explicit.lower()
    
    # Check for WaveSpeed API key first (Preferred provider)
    if os.getenv("WAVESPEED_API_KEY"):
        return "wavespeed"
        
    # Default to huggingface if WaveSpeed not available
    return "huggingface"


def _get_provider_client(provider_name: str, api_key: Optional[str] = None):
    """Get the client for the specified provider."""
    if provider_name == "wavespeed":
        return WaveSpeedEditProvider(api_key=api_key)
        
    if not HF_HUB_AVAILABLE:
        raise RuntimeError("huggingface_hub is not installed. Install with: pip install huggingface_hub")
    
    if provider_name == "huggingface":
        api_key = api_key or os.getenv("HF_TOKEN")
        if not api_key:
            raise RuntimeError("HF_TOKEN is required for Hugging Face image editing")
        # Use fal-ai provider for fast inference via HF Inference API
        return InferenceClient(provider="fal-ai", api_key=api_key)
    
    raise ValueError(f"Unknown image editing provider: {provider_name}")


def edit_image(
    input_image_bytes: bytes,
    prompt: str,
    options: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    mask_bytes: Optional[bytes] = None,
) -> ImageGenerationResult:
    """Edit image with pre-flight validation.
    
    Args:
        input_image_bytes: Input image as bytes (PNG/JPEG)
        prompt: Natural language prompt describing desired edits (e.g., "Turn the cat into a tiger")
        options: Image editing options (provider, model, etc.)
        user_id: User ID for subscription checking (optional, but required for validation)
        mask_bytes: Optional mask image bytes for selective editing (grayscale, white=edit, black=preserve)
    
    Returns:
        ImageGenerationResult with edited image bytes and metadata
        
    Best Practices for Prompts:
    - Use clear, specific language describing desired changes
    - Describe what should change and what should remain
    - Examples: "Turn the cat into a tiger", "Change background to forest", 
                "Make it look like a watercolor painting"
    
    Note: Mask support depends on the specific model. Some models may ignore the mask parameter.
    """
    # PRE-FLIGHT VALIDATION: Validate image editing before API call
    # MUST happen BEFORE any API calls - return immediately if validation fails
    if user_id:
        from services.database import get_db
        from services.subscription import PricingService
        from services.subscription.preflight_validator import validate_image_editing_operations
        from fastapi import HTTPException
        
        logger.info(f"[Image Editing] 🔍 Starting pre-flight validation for user_id={user_id}")
        # Note: get_db() is a generator, so we need to use next() to get the session
        # and ensure we close it in the finally block
        db = next(get_db())
        try:
            pricing_service = PricingService(db)
            # Raises HTTPException immediately if validation fails - frontend gets immediate response
            validate_image_editing_operations(
                pricing_service=pricing_service,
                user_id=user_id
            )
            logger.info(f"[Image Editing] ✅ Pre-flight validation passed for user_id={user_id} - proceeding with image editing")
        except HTTPException as http_ex:
            # Re-raise immediately - don't proceed with API call
            logger.error(f"[Image Editing] ❌ Pre-flight validation failed for user_id={user_id} - blocking API call: {http_ex.detail}")
            raise
        except Exception as e:
            logger.error(f"[Image Editing] ❌ Unexpected error during pre-flight validation: {e}")
            raise HTTPException(status_code=500, detail=f"Image editing validation failed: {str(e)}")
        finally:
            db.close()
    else:
        logger.warning(f"[Image Editing] ⚠️ No user_id provided - skipping pre-flight validation (this should not happen in production)")
    
    # Validate input
    if not input_image_bytes:
        raise ValueError("input_image_bytes is required")
    if not prompt or not prompt.strip():
        raise ValueError("prompt is required for image editing")
    
    opts = options or {}
    provider_name = _select_provider(opts.get("provider"))
    model = opts.get("model") or DEFAULT_IMAGE_EDIT_MODEL
    
    logger.info(f"[Image Editing] Editing image via provider={provider_name} model={model}")
    
    # Get provider client
    client = _get_provider_client(provider_name, opts.get("api_key"))
    
    if provider_name == "wavespeed":
        # Handle WaveSpeed provider
        try:
            # Convert inputs to base64 for WaveSpeed
            image_b64 = base64.b64encode(input_image_bytes).decode('utf-8')
            mask_b64 = None
            if mask_bytes:
                mask_b64 = base64.b64encode(mask_bytes).decode('utf-8')
            
            # Determine operation type based on prompt/mask
            operation = "general_edit" # Default
            if not prompt and mask_b64:
                operation = "remove_bg" # Heuristic: mask but no prompt implies removal/in-painting
            elif prompt and not mask_b64:
                operation = "style_transfer" # Heuristic: prompt but no mask implies style transfer
            elif opts.get("operation"):
                operation = opts.get("operation")
                
            edit_options = ImageEditOptions(
                image_base64=image_b64,
                prompt=prompt.strip(),
                operation=operation,
                mask_base64=mask_b64,
                model=model,
                guidance_scale=opts.get("guidance_scale"),
                steps=opts.get("steps"),
                seed=opts.get("seed"),
                extra=opts
            )
            
            logger.info(f"[Image Editing] Calling WaveSpeed edit with model={model}")
            result = client.edit(edit_options)
            
            # TRACK USAGE after successful WaveSpeed call
            if user_id:
                try:
                    from services.llm_providers.main_image_generation import _track_image_operation_usage
                    
                    # Estimate cost (WaveSpeed default: $0.02)
                    estimated_cost = result.metadata.get("estimated_cost", 0.02) if result.metadata else 0.02
                    
                    _track_image_operation_usage(
                        user_id=user_id,
                        provider="wavespeed",
                        model=result.model or model,
                        operation_type="image-editing",
                        result_bytes=result.image_bytes,
                        cost=estimated_cost,
                        prompt=prompt,
                        endpoint="/image-editing",
                        metadata=result.metadata,
                        log_prefix="[Image Editing]"
                    )
                except Exception as track_error:
                    logger.warning(f"[Image Editing] ⚠️ Failed to track usage: {track_error}")
            
            return result
            
        except Exception as e:
            logger.error(f"[Image Editing] ❌ WaveSpeed editing failed: {e}", exc_info=True)
            raise RuntimeError(f"WaveSpeed editing failed: {str(e)}")
    
    # Hugging Face (Fallback)
    # Prepare parameters for image-to-image
    params: Dict[str, Any] = {}
    if opts.get("guidance_scale") is not None:
        params["guidance_scale"] = opts.get("guidance_scale")
    if opts.get("steps") is not None:
        params["num_inference_steps"] = opts.get("steps")
    if opts.get("seed") is not None:
        params["seed"] = opts.get("seed")
    
    try:
        # Convert input image bytes to PIL Image for validation
        input_image = Image.open(io.BytesIO(input_image_bytes))
        width = input_image.width
        height = input_image.height
        
        # Convert mask bytes to PIL Image if provided
        mask_image = None
        if mask_bytes:
            try:
                mask_image = Image.open(io.BytesIO(mask_bytes)).convert("L")  # Convert to grayscale
                # Ensure mask dimensions match input image
                if mask_image.size != input_image.size:
                    logger.warning(f"[Image Editing] Mask size {mask_image.size} doesn't match image size {input_image.size}, resizing mask")
                    mask_image = mask_image.resize(input_image.size, Image.Resampling.LANCZOS)
            except Exception as e:
                logger.warning(f"[Image Editing] Failed to process mask image: {e}, continuing without mask")
                mask_image = None
        
        # Use image_to_image method from Hugging Face InferenceClient
        # This follows the pattern from the Hugging Face documentation
        # Docs: https://huggingface.co/docs/inference-providers/en/guides/image-editor
        # Note: Mask support depends on the model - some models may ignore it
        call_params = params.copy()
        if mask_image:
            call_params["mask_image"] = mask_image
            logger.info("[Image Editing] Using mask for selective editing")
        
        edited_image: Image.Image = client.image_to_image(
            image=input_image,
            prompt=prompt.strip(),
            model=model,
            **call_params,
        )
        
        # Convert edited image back to bytes
        with io.BytesIO() as buf:
            edited_image.save(buf, format="PNG")
            edited_image_bytes = buf.getvalue()
        
        logger.info(f"[Image Editing] ✅ Successfully edited image: {len(edited_image_bytes)} bytes")
        
        # TRACK USAGE after successful HF call
        if user_id:
            try:
                from services.llm_providers.main_image_generation import _track_image_operation_usage
                
                # Estimate cost (HF/Fal-ai default: $0.05)
                estimated_cost = 0.05
                
                _track_image_operation_usage(
                    user_id=user_id,
                    provider="huggingface",
                    model=model,
                    operation_type="image-editing",
                    result_bytes=edited_image_bytes,
                    cost=estimated_cost,
                    prompt=prompt,
                    endpoint="/image-editing",
                    metadata={"provider": "fal-ai"},
                    log_prefix="[Image Editing]"
                )
            except Exception as track_error:
                logger.warning(f"[Image Editing] ⚠️ Failed to track usage: {track_error}")
        
        return ImageGenerationResult(
            image_bytes=edited_image_bytes,
            width=edited_image.width,
            height=edited_image.height,
            provider="huggingface",
            model=model,
            seed=opts.get("seed"),
            metadata={
                "provider": "fal-ai",
                "operation": "image_editing",
                "original_width": width,
                "original_height": height,
            },
        )
    except Exception as e:
        logger.error(f"[Image Editing] ❌ Error editing image: {e}", exc_info=True)
        raise RuntimeError(f"Image editing failed: {str(e)}")

