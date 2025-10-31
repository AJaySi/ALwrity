from __future__ import annotations

import io
import os
from typing import Optional, Dict, Any

import requests
from PIL import Image

from .base import ImageGenerationOptions, ImageGenerationResult, ImageGenerationProvider
from utils.logger_utils import get_service_logger


logger = get_service_logger("image_generation.stability")


DEFAULT_STABILITY_MODEL = os.getenv("STABILITY_MODEL", "stable-diffusion-xl-1024-v1-0")


class StabilityImageProvider(ImageGenerationProvider):
    """Stability AI Images API provider (simple text-to-image).

    This uses the v1 text-to-image endpoint format. Adjust to match your existing
    Stability integration if different.
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("STABILITY_API_KEY")
        if not self.api_key:
            logger.warning("STABILITY_API_KEY not set. Stability generation may fail at runtime.")
        logger.info("StabilityImageProvider initialized")

    def generate(self, options: ImageGenerationOptions) -> ImageGenerationResult:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {
            "text_prompts": [
                {"text": options.prompt, "weight": 1.0},
            ],
            "cfg_scale": options.guidance_scale or 7.0,
            "steps": options.steps or 30,
            "width": options.width,
            "height": options.height,
            "seed": options.seed,
        }
        if options.negative_prompt:
            payload["text_prompts"].append({"text": options.negative_prompt, "weight": -1.0})

        model = options.model or DEFAULT_STABILITY_MODEL
        url = f"https://api.stability.ai/v1/generation/{model}/text-to-image"

        logger.debug("Stability generate: model=%s payload_keys=%s", model, list(payload.keys()))
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        # Expecting data["artifacts"][0]["base64"]
        import base64

        artifact = (data.get("artifacts") or [{}])[0]
        b64 = artifact.get("base64", "")
        image_bytes = base64.b64decode(b64)

        # Confirm dimensions by loading once (optional)
        img = Image.open(io.BytesIO(image_bytes))

        return ImageGenerationResult(
            image_bytes=image_bytes,
            width=img.width,
            height=img.height,
            provider="stability",
            model=model,
            seed=options.seed,
        )


