from __future__ import annotations

import os
from typing import Optional, Dict, Any

from .image_generation import (
    ImageGenerationOptions,
    ImageGenerationResult,
    HuggingFaceImageProvider,
    GeminiImageProvider,
    StabilityImageProvider,
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
    # Fallback to huggingface to enable a path if configured
    return "huggingface"


def _get_provider(provider_name: str):
    if provider_name == "huggingface":
        return HuggingFaceImageProvider()
    if provider_name == "gemini":
        return GeminiImageProvider()
    if provider_name == "stability":
        return StabilityImageProvider()
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
        
        db = next(get_db())
        try:
            pricing_service = PricingService(db)
            # Raises HTTPException immediately if validation fails - frontend gets immediate response
            validate_image_generation_operations(
                pricing_service=pricing_service,
                user_id=user_id
            )
        except HTTPException as http_ex:
            # Re-raise immediately - don't proceed with API call
            logger.error(f"[Image Generation] ❌ Pre-flight validation failed - blocking API call")
            raise
        finally:
            db.close()
    
    logger.info(f"[Image Generation] ✅ Pre-flight validation passed - proceeding with image generation")
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

    logger.info("Generating image via provider=%s model=%s", provider_name, image_options.model)
    provider = _get_provider(provider_name)
    return provider.generate(image_options)


