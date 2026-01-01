"""WAN 2.5 service for Alibaba image-to-video generation via WaveSpeed."""

import base64
import asyncio
from typing import Any, Dict, Optional, Callable
import requests
from fastapi import HTTPException
from loguru import logger

from services.wavespeed.client import WaveSpeedClient
from utils.logger_utils import get_service_logger

logger = get_service_logger("image_studio.wan25")

WAN25_MODEL_PATH = "alibaba/wan-2.5/image-to-video"
WAN25_MODEL_NAME = "alibaba/wan-2.5/image-to-video"

# Pricing per second (from WaveSpeed docs)
PRICING = {
    "480p": 0.05,   # $0.05 per second
    "720p": 0.10,   # $0.10 per second
    "1080p": 0.15,  # $0.15 per second
}

MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10MB (recommended)
MAX_AUDIO_BYTES = 15 * 1024 * 1024  # 15MB (API limit)
MIN_AUDIO_DURATION = 3  # seconds
MAX_AUDIO_DURATION = 30  # seconds


def _as_data_uri(content_bytes: bytes, mime_type: str) -> str:
    """Convert bytes to data URI."""
    encoded = base64.b64encode(content_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def _decode_base64_image(image_base64: str) -> tuple[bytes, str]:
    """Decode base64 image, handling data URIs."""
    if image_base64.startswith("data:"):
        # Extract mime type and base64 data
        if "," not in image_base64:
            raise ValueError("Invalid data URI format: missing comma separator")
        header, encoded = image_base64.split(",", 1)
        mime_parts = header.split(":")[1].split(";")[0] if ":" in header else "image/png"
        mime_type = mime_parts.strip()
        if not mime_type:
            mime_type = "image/png"
        image_bytes = base64.b64decode(encoded)
    else:
        # Assume it's raw base64
        image_bytes = base64.b64decode(image_base64)
        mime_type = "image/png"  # Default
    
    return image_bytes, mime_type


def _decode_base64_audio(audio_base64: str) -> tuple[bytes, str]:
    """Decode base64 audio, handling data URIs."""
    if audio_base64.startswith("data:"):
        if "," not in audio_base64:
            raise ValueError("Invalid data URI format: missing comma separator")
        header, encoded = audio_base64.split(",", 1)
        mime_parts = header.split(":")[1].split(";")[0] if ":" in header else "audio/mpeg"
        mime_type = mime_parts.strip()
        if not mime_type:
            mime_type = "audio/mpeg"
        audio_bytes = base64.b64decode(encoded)
    else:
        audio_bytes = base64.b64decode(audio_base64)
        mime_type = "audio/mpeg"  # Default
    
    return audio_bytes, mime_type


class WAN25Service:
    """Service for Alibaba WAN 2.5 image-to-video generation."""
    
    def __init__(self, client: Optional[WaveSpeedClient] = None):
        """Initialize WAN 2.5 service."""
        self.client = client or WaveSpeedClient()
        logger.info("[WAN 2.5] Service initialized")
    
    def calculate_cost(self, resolution: str, duration: int) -> float:
        """Calculate cost for video generation.
        
        Args:
            resolution: Output resolution (480p, 720p, 1080p)
            duration: Video duration in seconds (5 or 10)
            
        Returns:
            Cost in USD
        """
        cost_per_second = PRICING.get(resolution, PRICING["720p"])
        return cost_per_second * duration
    
    async def generate_video(
        self,
        image_base64: str,
        prompt: str,
        audio_base64: Optional[str] = None,
        resolution: str = "720p",
        duration: int = 5,
        negative_prompt: Optional[str] = None,
        seed: Optional[int] = None,
        enable_prompt_expansion: bool = True,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> Dict[str, Any]:
        """Generate video using WAN 2.5.
        
        Args:
            image_base64: Image in base64 or data URI format
            prompt: Text prompt describing the video
            audio_base64: Optional audio file (wav/mp3, 3-30s, ≤15MB)
            resolution: Output resolution (480p, 720p, 1080p)
            duration: Video duration in seconds (5 or 10)
            negative_prompt: Optional negative prompt
            seed: Optional random seed for reproducibility
            enable_prompt_expansion: Enable prompt optimizer
            
        Returns:
            Dictionary with video bytes, metadata, and cost
        """
        # Validate resolution
        if resolution not in PRICING:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid resolution: {resolution}. Must be one of: {list(PRICING.keys())}"
            )
        
        # Validate duration
        if duration not in [5, 10]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid duration: {duration}. Must be 5 or 10 seconds"
            )
        
        # Validate prompt
        if not prompt or not prompt.strip():
            raise HTTPException(
                status_code=400,
                detail="Prompt is required and cannot be empty"
            )
        
        # Decode image
        try:
            image_bytes, image_mime = _decode_base64_image(image_base64)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to decode image: {str(e)}"
            )
        
        # Validate image size
        if len(image_bytes) > MAX_IMAGE_BYTES:
            raise HTTPException(
                status_code=400,
                detail=f"Image exceeds {MAX_IMAGE_BYTES / (1024*1024):.0f}MB limit"
            )
        
        # Build payload
        payload = {
            "image": _as_data_uri(image_bytes, image_mime),
            "prompt": prompt,
            "resolution": resolution,
            "duration": duration,
            "enable_prompt_expansion": enable_prompt_expansion,
        }
        
        # Add optional audio
        if audio_base64:
            try:
                audio_bytes, audio_mime = _decode_base64_audio(audio_base64)
                
                # Validate audio size
                if len(audio_bytes) > MAX_AUDIO_BYTES:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Audio exceeds {MAX_AUDIO_BYTES / (1024*1024):.0f}MB limit"
                    )
                
                # Note: Audio duration validation would require audio analysis
                # For now, we rely on API to handle it (API keeps first 5s/10s if longer)
                
                payload["audio"] = _as_data_uri(audio_bytes, audio_mime)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to decode audio: {str(e)}"
                )
        
        # Add optional parameters
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        
        if seed is not None:
            payload["seed"] = seed
        
        # Submit to WaveSpeed
        logger.info(
            f"[WAN 2.5] Submitting video generation request: resolution={resolution}, duration={duration}s"
        )
        
        try:
            prediction_id = self.client.submit_image_to_video(
                WAN25_MODEL_PATH,
                payload,
                timeout=60
            )
        except HTTPException as e:
            logger.error(f"[WAN 2.5] Submission failed: {e.detail}")
            raise
        
        # Poll for completion
        logger.info(f"[WAN 2.5] Polling for completion: prediction_id={prediction_id}")
        
        try:
            # WAN 2.5 typically takes 1-2 minutes
            result = self.client.poll_until_complete(
                prediction_id,
                timeout_seconds=180,  # 3 minutes max
                interval_seconds=2.0,
                progress_callback=progress_callback,
            )
        except HTTPException as e:
            detail = e.detail or {}
            if isinstance(detail, dict):
                detail.setdefault("prediction_id", prediction_id)
                detail.setdefault("resume_available", True)
            raise HTTPException(status_code=e.status_code, detail=detail)
        
        # Extract video URL
        outputs = result.get("outputs") or []
        if not outputs:
            raise HTTPException(
                status_code=502,
                detail="WAN 2.5 completed but returned no outputs"
            )
        
        video_url = outputs[0]
        if not isinstance(video_url, str) or not video_url.startswith("http"):
            raise HTTPException(
                status_code=502,
                detail=f"Invalid video URL format: {video_url}"
            )
        
        # Download video (run synchronous request in thread)
        logger.info(f"[WAN 2.5] Downloading video from: {video_url}")
        video_response = await asyncio.to_thread(
            requests.get,
            video_url,
            timeout=180
        )
        
        if video_response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail={
                    "error": "Failed to download WAN 2.5 video",
                    "status_code": video_response.status_code,
                    "response": video_response.text[:200],
                }
            )
        
        video_bytes = video_response.content
        metadata = result.get("metadata") or {}
        
        # Calculate cost
        cost = self.calculate_cost(resolution, duration)
        
        # Get video dimensions from resolution
        resolution_dims = {
            "480p": (854, 480),
            "720p": (1280, 720),
            "1080p": (1920, 1080),
        }
        width, height = resolution_dims.get(resolution, (1280, 720))
        
        logger.info(
            f"[WAN 2.5] ✅ Generated video: {len(video_bytes)} bytes, "
            f"resolution={resolution}, duration={duration}s, cost=${cost:.2f}"
        )
        
        return {
            "video_bytes": video_bytes,
            "prompt": prompt,
            "duration": float(duration),
            "model_name": WAN25_MODEL_NAME,
            "cost": cost,
            "provider": "wavespeed",
            "source_video_url": video_url,
            "prediction_id": prediction_id,
            "resolution": resolution,
            "width": width,
            "height": height,
            "metadata": metadata,
        }

