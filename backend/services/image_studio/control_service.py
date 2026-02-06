"""Control Studio service for AI-powered controlled image generation."""

from __future__ import annotations

import base64
import io
from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional

from PIL import Image

from services.stability_service import StabilityAIService
from utils.logging import get_service_logger


logger = get_service_logger("image_studio.control")


ControlOperationType = Literal[
    "sketch",
    "structure",
    "style",
    "style_transfer",
]


@dataclass
class ControlStudioRequest:
    """Normalized request payload for Control Studio operations."""

    operation: ControlOperationType
    prompt: str
    control_image_base64: str  # Sketch, structure, or style reference
    style_image_base64: Optional[str] = None  # For style_transfer only
    negative_prompt: Optional[str] = None
    control_strength: Optional[float] = None  # For sketch/structure
    fidelity: Optional[float] = None  # For style
    style_strength: Optional[float] = None  # For style_transfer
    composition_fidelity: Optional[float] = None  # For style_transfer
    change_strength: Optional[float] = None  # For style_transfer
    aspect_ratio: Optional[str] = None  # For style
    style_preset: Optional[str] = None
    seed: Optional[int] = None
    output_format: str = "png"


class ControlStudioService:
    """Service layer orchestrating Control Studio operations."""

    SUPPORTED_OPERATIONS: Dict[ControlOperationType, Dict[str, Any]] = {
        "sketch": {
            "label": "Sketch to Image",
            "description": "Transform sketches into refined images with precise control.",
            "provider": "stability",
            "fields": {
                "control_image": True,
                "style_image": False,
                "control_strength": True,
                "fidelity": False,
                "style_strength": False,
                "aspect_ratio": False,
            },
        },
        "structure": {
            "label": "Structure Control",
            "description": "Generate images maintaining the structure of an input image.",
            "provider": "stability",
            "fields": {
                "control_image": True,
                "style_image": False,
                "control_strength": True,
                "fidelity": False,
                "style_strength": False,
                "aspect_ratio": False,
            },
        },
        "style": {
            "label": "Style Control",
            "description": "Generate images using style from a reference image.",
            "provider": "stability",
            "fields": {
                "control_image": True,
                "style_image": False,
                "control_strength": False,
                "fidelity": True,
                "style_strength": False,
                "aspect_ratio": True,
            },
        },
        "style_transfer": {
            "label": "Style Transfer",
            "description": "Apply visual characteristics from a style image to a target image.",
            "provider": "stability",
            "fields": {
                "control_image": True,  # init_image
                "style_image": True,
                "control_strength": False,
                "fidelity": False,
                "style_strength": True,
                "aspect_ratio": False,
            },
        },
    }

    def __init__(self):
        logger.info("[Control Studio] Initialized control service")

    @staticmethod
    def _decode_base64_image(value: Optional[str]) -> Optional[bytes]:
        """Decode a base64 (or data URL) string to bytes."""
        if not value:
            return None

        try:
            # Handle data URLs (data:image/png;base64,...)
            if value.startswith("data:"):
                _, b64data = value.split(",", 1)
            else:
                b64data = value

            return base64.b64decode(b64data)
        except Exception as exc:
            logger.error(f"[Control Studio] Failed to decode base64 image: {exc}")
            raise ValueError("Invalid base64 image payload") from exc

    @staticmethod
    def _image_bytes_to_metadata(image_bytes: bytes) -> Dict[str, Any]:
        """Extract width/height metadata from image bytes."""
        with Image.open(io.BytesIO(image_bytes)) as img:
            return {
                "width": img.width,
                "height": img.height,
            }

    @staticmethod
    def _bytes_to_base64(image_bytes: bytes, output_format: str = "png") -> str:
        """Convert raw bytes to base64 data URL."""
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        return f"data:image/{output_format};base64,{b64}"

    def list_operations(self) -> Dict[str, Dict[str, Any]]:
        """Expose supported operations for UI rendering."""
        return self.SUPPORTED_OPERATIONS

    async def process_control(
        self,
        request: ControlStudioRequest,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process control request and return normalized response."""

        if user_id:
            from services.database import get_db
            from services.subscription import PricingService
            from services.subscription.preflight_validator import validate_image_control_operations
            from fastapi import HTTPException

            db = next(get_db())
            try:
                pricing_service = PricingService(db)
                logger.info(f"[Control Studio] 🛂 Running pre-flight validation for user {user_id}")
                validate_image_control_operations(
                    pricing_service=pricing_service,
                    user_id=user_id,
                    num_images=1,
                )
                logger.info("[Control Studio] ✅ Pre-flight validation passed")
            except HTTPException:
                logger.error("[Control Studio] ❌ Pre-flight validation failed")
                raise
            finally:
                db.close()
        else:
            logger.warning("[Control Studio] ⚠️ No user_id provided - skipping pre-flight validation")

        control_image_bytes = self._decode_base64_image(request.control_image_base64)
        if not control_image_bytes:
            raise ValueError("Control image payload is required")

        style_image_bytes = self._decode_base64_image(request.style_image_base64)

        operation = request.operation
        logger.info("[Control Studio] Processing operation='%s' for user=%s", operation, user_id)

        if operation not in self.SUPPORTED_OPERATIONS:
            raise ValueError(f"Unsupported control operation: {operation}")

        stability_service = StabilityAIService()
        async with stability_service:
            if operation == "sketch":
                result = await stability_service.control_sketch(
                    image=control_image_bytes,
                    prompt=request.prompt,
                    control_strength=request.control_strength or 0.7,
                    negative_prompt=request.negative_prompt,
                    seed=request.seed,
                    output_format=request.output_format,
                    style_preset=request.style_preset,
                )
            elif operation == "structure":
                result = await stability_service.control_structure(
                    image=control_image_bytes,
                    prompt=request.prompt,
                    control_strength=request.control_strength or 0.7,
                    negative_prompt=request.negative_prompt,
                    seed=request.seed,
                    output_format=request.output_format,
                    style_preset=request.style_preset,
                )
            elif operation == "style":
                result = await stability_service.control_style(
                    image=control_image_bytes,
                    prompt=request.prompt,
                    negative_prompt=request.negative_prompt,
                    aspect_ratio=request.aspect_ratio or "1:1",
                    fidelity=request.fidelity or 0.5,
                    seed=request.seed,
                    output_format=request.output_format,
                    style_preset=request.style_preset,
                )
            elif operation == "style_transfer":
                if not style_image_bytes:
                    raise ValueError("Style image is required for style transfer")
                result = await stability_service.control_style_transfer(
                    init_image=control_image_bytes,
                    style_image=style_image_bytes,
                    prompt=request.prompt or "",
                    negative_prompt=request.negative_prompt,
                    style_strength=request.style_strength or 1.0,
                    composition_fidelity=request.composition_fidelity or 0.9,
                    change_strength=request.change_strength or 0.9,
                    seed=request.seed,
                    output_format=request.output_format,
                )
            else:
                raise ValueError(f"Unsupported control operation: {operation}")

        image_bytes = self._extract_image_bytes(result)
        metadata = self._image_bytes_to_metadata(image_bytes)
        metadata.update(
            {
                "operation": operation,
                "style_preset": request.style_preset,
                "provider": self.SUPPORTED_OPERATIONS[operation]["provider"],
            }
        )

        response = {
            "success": True,
            "operation": operation,
            "provider": metadata["provider"],
            "image_base64": self._bytes_to_base64(image_bytes, request.output_format),
            "width": metadata["width"],
            "height": metadata["height"],
            "metadata": metadata,
        }

        logger.info("[Control Studio] ✅ Operation '%s' completed", operation)
        return response

    @staticmethod
    def _extract_image_bytes(result: Any) -> bytes:
        """Normalize Stability responses into raw image bytes."""
        if isinstance(result, bytes):
            return result

        if isinstance(result, dict):
            artifacts = result.get("artifacts") or result.get("data") or result.get("images") or []
            for artifact in artifacts:
                if isinstance(artifact, dict):
                    if artifact.get("base64"):
                        return base64.b64decode(artifact["base64"])
                    if artifact.get("b64_json"):
                        return base64.b64decode(artifact["b64_json"])

        raise RuntimeError("Unable to extract image bytes from provider response")

