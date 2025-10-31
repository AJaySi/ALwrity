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


def generate_image(prompt: str, options: Optional[Dict[str, Any]] = None) -> ImageGenerationResult:
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


