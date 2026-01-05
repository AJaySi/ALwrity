import base64
import io
from dataclasses import dataclass
from typing import Literal, Optional, Dict, Any

from fastapi import HTTPException
from PIL import Image

from services.stability_service import StabilityAIService
from utils.logger_utils import get_service_logger

logger = get_service_logger("image_studio.upscale")


UpscaleMode = Literal["fast", "conservative", "creative", "auto"]


@dataclass
class UpscaleStudioRequest:
    image_base64: str
    mode: UpscaleMode = "auto"
    target_width: Optional[int] = None
    target_height: Optional[int] = None
    preset: Optional[str] = None  # e.g., web/print/social
    prompt: Optional[str] = None  # used for conservative/creative modes


class UpscaleStudioService:
    """Handles image upscaling workflows."""

    def __init__(self):
        logger.info("[Upscale Studio] Service initialized")

    async def process_upscale(
        self,
        request: UpscaleStudioRequest,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        # Pre-flight validation: Reuse unified helper
        # Note: Using image-generation validation since upscaling uses same subscription limits
        if user_id:
            from services.llm_providers.main_image_generation import _validate_image_operation
            _validate_image_operation(
                user_id=user_id,
                operation_type="image-upscale",
                num_operations=1,
                log_prefix="[Upscale Studio]"
            )

        image_bytes = self._decode_base64(request.image_base64)
        if not image_bytes:
            raise ValueError("Primary image is required for upscaling")

        mode = self._resolve_mode(request)

        async with StabilityAIService() as stability_service:
            logger.info("[Upscale Studio] Running '%s' upscale for user=%s", mode, user_id)

            params = {
                "target_width": request.target_width,
                "target_height": request.target_height,
            }
            # remove None values
            params = {k: v for k, v in params.items() if v is not None}

            if mode == "fast":
                result = await stability_service.upscale_fast(
                    image=image_bytes,
                    **params,
                )
            elif mode == "conservative":
                prompt = request.prompt or "High fidelity upscale preserving original details"
                result = await stability_service.upscale_conservative(
                    image=image_bytes,
                    prompt=prompt,
                    **params,
                )
            elif mode == "creative":
                prompt = request.prompt or "Creative upscale with enhanced artistic details"
                result = await stability_service.upscale_creative(
                    image=image_bytes,
                    prompt=prompt,
                    **params,
                )
            else:
                raise ValueError(f"Unsupported upscale mode: {mode}")

        image_bytes = self._extract_image_bytes(result)
        metadata = self._image_metadata(image_bytes)

        return {
            "success": True,
            "mode": mode,
            "image_base64": self._to_base64(image_bytes),
            "width": metadata["width"],
            "height": metadata["height"],
            "metadata": {
                "preset": request.preset,
                "target_width": request.target_width,
                "target_height": request.target_height,
                "prompt": request.prompt,
            },
        }

    @staticmethod
    def _decode_base64(value: Optional[str]) -> Optional[bytes]:
        if not value:
            return None
        try:
            if value.startswith("data:"):
                _, b64data = value.split(",", 1)
            else:
                b64data = value
            return base64.b64decode(b64data)
        except Exception as exc:
            logger.error("[Upscale Studio] Failed to decode base64 image: %s", exc)
            raise ValueError("Invalid base64 image payload") from exc

    @staticmethod
    def _to_base64(image_bytes: bytes) -> str:
        return f"data:image/png;base64,{base64.b64encode(image_bytes).decode('utf-8')}"

    @staticmethod
    def _image_metadata(image_bytes: bytes) -> Dict[str, int]:
        with Image.open(io.BytesIO(image_bytes)) as img:
            return {"width": img.width, "height": img.height}

    @staticmethod
    def _extract_image_bytes(result: Any) -> bytes:
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
        raise HTTPException(status_code=502, detail="Unable to extract image from provider response")

    @staticmethod
    def _resolve_mode(request: UpscaleStudioRequest) -> UpscaleMode:
        if request.mode != "auto":
            return request.mode
        # simple heuristic: if target >= 3000px, use conservative, else fast
        if (request.target_width and request.target_width >= 3000) or (
            request.target_height and request.target_height >= 3000
        ):
            return "conservative"
        return "fast"

