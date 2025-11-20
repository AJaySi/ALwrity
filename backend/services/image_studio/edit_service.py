"""Edit Studio service for AI-powered image editing and transformations."""

from __future__ import annotations

import asyncio
import base64
import io
from dataclasses import dataclass, field
from typing import Any, Dict, Literal, Optional

from PIL import Image

from services.llm_providers.main_image_editing import edit_image as huggingface_edit_image
from services.stability_service import StabilityAIService
from utils.logger_utils import get_service_logger


logger = get_service_logger("image_studio.edit")


EditOperationType = Literal[
    "remove_background",
    "inpaint",
    "outpaint",
    "search_replace",
    "search_recolor",
    "relight",
    "general_edit",
]


@dataclass
class EditStudioRequest:
    """Normalized request payload for Edit Studio operations."""

    image_base64: str
    operation: EditOperationType
    prompt: Optional[str] = None
    negative_prompt: Optional[str] = None
    mask_base64: Optional[str] = None
    search_prompt: Optional[str] = None
    select_prompt: Optional[str] = None
    background_image_base64: Optional[str] = None
    lighting_image_base64: Optional[str] = None
    expand_left: Optional[int] = None
    expand_right: Optional[int] = None
    expand_up: Optional[int] = None
    expand_down: Optional[int] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    style_preset: Optional[str] = None
    guidance_scale: Optional[float] = None
    steps: Optional[int] = None
    seed: Optional[int] = None
    output_format: str = "png"
    options: Dict[str, Any] = field(default_factory=dict)


class EditStudioService:
    """Service layer orchestrating Edit Studio operations."""

    SUPPORTED_OPERATIONS: Dict[EditOperationType, Dict[str, Any]] = {
        "remove_background": {
            "label": "Remove Background",
            "description": "Isolate the main subject and remove the background.",
            "provider": "stability",
            "async": False,
            "fields": {
                "prompt": False,
                "mask": False,
                "negative_prompt": False,
                "search_prompt": False,
                "select_prompt": False,
                "background": False,
                "lighting": False,
                "expansion": False,
            },
        },
        "inpaint": {
            "label": "Inpaint & Fix",
            "description": "Edit specific regions using prompts and optional masks.",
            "provider": "stability",
            "async": False,
            "fields": {
                "prompt": True,
                "mask": True,
                "negative_prompt": True,
                "search_prompt": False,
                "select_prompt": False,
                "background": False,
                "lighting": False,
                "expansion": False,
            },
        },
        "outpaint": {
            "label": "Outpaint",
            "description": "Extend the canvas in any direction with smart fill.",
            "provider": "stability",
            "async": False,
            "fields": {
                "prompt": False,
                "mask": False,
                "negative_prompt": True,
                "search_prompt": False,
                "select_prompt": False,
                "background": False,
                "lighting": False,
                "expansion": True,
            },
        },
        "search_replace": {
            "label": "Search & Replace",
            "description": "Locate objects via search prompt and replace them.",
            "provider": "stability",
            "async": False,
            "fields": {
                "prompt": True,
                "mask": False,
                "negative_prompt": False,
                "search_prompt": True,
                "select_prompt": False,
                "background": False,
                "lighting": False,
                "expansion": False,
            },
        },
        "search_recolor": {
            "label": "Search & Recolor",
            "description": "Select elements via prompt and recolor them.",
            "provider": "stability",
            "async": False,
            "fields": {
                "prompt": True,
                "mask": False,
                "negative_prompt": False,
                "search_prompt": False,
                "select_prompt": True,
                "background": False,
                "lighting": False,
                "expansion": False,
            },
        },
        "relight": {
            "label": "Replace Background & Relight",
            "description": "Swap backgrounds and relight using reference images.",
            "provider": "stability",
            "async": True,
            "fields": {
                "prompt": False,
                "mask": False,
                "negative_prompt": False,
                "search_prompt": False,
                "select_prompt": False,
                "background": True,
                "lighting": True,
                "expansion": False,
            },
        },
        "general_edit": {
            "label": "Prompt-based Edit",
            "description": "Free-form editing powered by Hugging Face image-to-image models.",
            "provider": "huggingface",
            "async": False,
            "fields": {
                "prompt": True,
                "mask": False,
                "negative_prompt": True,
                "search_prompt": False,
                "select_prompt": False,
                "background": False,
                "lighting": False,
                "expansion": False,
            },
        },
    }

    def __init__(self):
        logger.info("[Edit Studio] Initialized edit service")

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
            logger.error(f"[Edit Studio] Failed to decode base64 image: {exc}")
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

    async def process_edit(
        self,
        request: EditStudioRequest,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process edit request and return normalized response."""

        if user_id:
            from services.database import get_db
            from services.subscription import PricingService
            from services.subscription.preflight_validator import validate_image_editing_operations
            from fastapi import HTTPException

            db = next(get_db())
            try:
                pricing_service = PricingService(db)
                logger.info(f"[Edit Studio] 🛂 Running pre-flight validation for user {user_id}")
                validate_image_editing_operations(
                    pricing_service=pricing_service,
                    user_id=user_id,
                )
                logger.info("[Edit Studio] ✅ Pre-flight validation passed")
            except HTTPException:
                logger.error("[Edit Studio] ❌ Pre-flight validation failed")
                raise
            finally:
                db.close()
        else:
            logger.warning("[Edit Studio] ⚠️ No user_id provided - skipping pre-flight validation")

        image_bytes = self._decode_base64_image(request.image_base64)
        if not image_bytes:
            raise ValueError("Primary image payload is required")

        mask_bytes = self._decode_base64_image(request.mask_base64)
        background_bytes = self._decode_base64_image(request.background_image_base64)
        lighting_bytes = self._decode_base64_image(request.lighting_image_base64)

        operation = request.operation
        logger.info("[Edit Studio] Processing operation='%s' for user=%s", operation, user_id)

        if operation not in self.SUPPORTED_OPERATIONS:
            raise ValueError(f"Unsupported edit operation: {operation}")

        if operation in {"remove_background", "inpaint", "outpaint", "search_replace", "search_recolor", "relight"}:
            image_bytes = await self._handle_stability_edit(
                operation=operation,
                request=request,
                image_bytes=image_bytes,
                mask_bytes=mask_bytes,
                background_bytes=background_bytes,
                lighting_bytes=lighting_bytes,
            )
        else:
            image_bytes = await self._handle_general_edit(
                request=request,
                image_bytes=image_bytes,
                mask_bytes=mask_bytes,
                user_id=user_id,
            )

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

        logger.info("[Edit Studio] ✅ Operation '%s' completed", operation)
        return response

    async def _handle_stability_edit(
        self,
        operation: EditOperationType,
        request: EditStudioRequest,
        image_bytes: bytes,
        mask_bytes: Optional[bytes],
        background_bytes: Optional[bytes],
        lighting_bytes: Optional[bytes],
    ) -> bytes:
        """Execute Stability AI edit workflows."""
        stability_service = StabilityAIService()

        async with stability_service:
            if operation == "remove_background":
                result = await stability_service.remove_background(
                    image=image_bytes,
                    output_format=request.output_format,
                )
            elif operation == "inpaint":
                if not request.prompt:
                    raise ValueError("Prompt is required for inpainting")
                result = await stability_service.inpaint(
                    image=image_bytes,
                    prompt=request.prompt,
                    mask=mask_bytes,
                    negative_prompt=request.negative_prompt,
                    output_format=request.output_format,
                    style_preset=request.style_preset,
                    grow_mask=request.options.get("grow_mask", 5),
                )
            elif operation == "outpaint":
                result = await stability_service.outpaint(
                    image=image_bytes,
                    prompt=request.prompt,
                    negative_prompt=request.negative_prompt,
                    output_format=request.output_format,
                    left=request.expand_left or 0,
                    right=request.expand_right or 0,
                    up=request.expand_up or 0,
                    down=request.expand_down or 0,
                    style_preset=request.style_preset,
                )
            elif operation == "search_replace":
                if not (request.prompt and request.search_prompt):
                    raise ValueError("Both prompt and search_prompt are required for search & replace")
                result = await stability_service.search_and_replace(
                    image=image_bytes,
                    prompt=request.prompt,
                    search_prompt=request.search_prompt,
                    output_format=request.output_format,
                )
            elif operation == "search_recolor":
                if not (request.prompt and request.select_prompt):
                    raise ValueError("Both prompt and select_prompt are required for search & recolor")
                result = await stability_service.search_and_recolor(
                    image=image_bytes,
                    prompt=request.prompt,
                    select_prompt=request.select_prompt,
                    output_format=request.output_format,
                )
            elif operation == "relight":
                if not background_bytes and not lighting_bytes:
                    raise ValueError("At least one reference (background or lighting) is required for relight")
                result = await stability_service.replace_background_and_relight(
                    subject_image=image_bytes,
                    background_reference=background_bytes,
                    light_reference=lighting_bytes,
                    output_format=request.output_format,
                )
                if isinstance(result, dict) and result.get("id"):
                    result = await self._poll_stability_result(
                        stability_service,
                        generation_id=result["id"],
                        output_format=request.output_format,
                    )
            else:
                raise ValueError(f"Unsupported Stability operation: {operation}")

        return self._extract_image_bytes(result)

    async def _handle_general_edit(
        self,
        request: EditStudioRequest,
        image_bytes: bytes,
        mask_bytes: Optional[bytes],
        user_id: Optional[str],
    ) -> bytes:
        """Execute Hugging Face powered general editing (synchronous API)."""
        if not request.prompt:
            raise ValueError("Prompt is required for general edits")

        options = {
            "provider": request.provider or "huggingface",
            "model": request.model,
            "guidance_scale": request.guidance_scale,
            "steps": request.steps,
            "seed": request.seed,
        }

        # huggingface edit is synchronous - run in thread
        result = await asyncio.to_thread(
            huggingface_edit_image,
            image_bytes,
            request.prompt,
            options,
            user_id,
        )

        return result.image_bytes

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

    async def _poll_stability_result(
        self,
        stability_service: StabilityAIService,
        generation_id: str,
        output_format: str,
        timeout_seconds: int = 240,
        interval_seconds: float = 2.0,
    ) -> bytes:
        """Poll Stability async endpoint until result is ready."""
        elapsed = 0.0
        while elapsed < timeout_seconds:
            result = await stability_service.get_generation_result(
                generation_id=generation_id,
                accept_type="*/*",
            )

            if isinstance(result, bytes):
                return result

            if isinstance(result, dict):
                state = (result.get("state") or result.get("status") or "").lower()
                if state in {"succeeded", "success", "ready", "completed"}:
                    return self._extract_image_bytes(result)
                if state in {"failed", "error"}:
                    raise RuntimeError(f"Stability generation failed: {result}")

            await asyncio.sleep(interval_seconds)
            elapsed += interval_seconds

        raise RuntimeError("Timed out waiting for Stability generation result")


