"""Hunyuan Avatar adapter for Avatar Studio."""

import asyncio
from typing import Any, Dict, Optional
from fastapi import HTTPException
from loguru import logger

from services.wavespeed.hunyuan_avatar import create_hunyuan_avatar, calculate_hunyuan_avatar_cost
from services.wavespeed.client import WaveSpeedClient
from utils.logger_utils import get_service_logger

logger = get_service_logger("video_studio.hunyuan_avatar")


class HunyuanAvatarService:
    """Adapter for Hunyuan Avatar in Avatar Studio context."""
    
    def __init__(self, client: Optional[WaveSpeedClient] = None):
        """Initialize Hunyuan Avatar service adapter."""
        self.client = client or WaveSpeedClient()
        logger.info("[Hunyuan Avatar Adapter] Service initialized")
    
    def calculate_cost(self, resolution: str, duration: float) -> float:
        """Calculate cost for Hunyuan Avatar video.
        
        Args:
            resolution: Output resolution (480p or 720p)
            duration: Video duration in seconds
            
        Returns:
            Cost in USD
        """
        return calculate_hunyuan_avatar_cost(resolution, duration)
    
    async def create_talking_avatar(
        self,
        image_base64: str,
        audio_base64: str,
        resolution: str = "480p",
        prompt: Optional[str] = None,
        seed: Optional[int] = None,
        user_id: str = "video_studio",
        progress_callback: Optional[callable] = None,
    ) -> Dict[str, Any]:
        """Create talking avatar video using Hunyuan Avatar.
        
        Args:
            image_base64: Person image in base64 or data URI
            audio_base64: Audio file in base64 or data URI
            resolution: Output resolution (480p or 720p, default: 480p)
            prompt: Optional prompt for expression/style
            seed: Optional random seed
            user_id: User ID for tracking
            progress_callback: Optional progress callback function
            
        Returns:
            Dictionary with video_bytes, metadata, and cost
        """
        # Validate resolution
        if resolution not in ["480p", "720p"]:
            raise HTTPException(
                status_code=400,
                detail="Resolution must be '480p' or '720p' for Hunyuan Avatar"
            )
        
        # Decode image
        import base64
        try:
            if image_base64.startswith("data:"):
                if "," not in image_base64:
                    raise ValueError("Invalid data URI format: missing comma separator")
                header, encoded = image_base64.split(",", 1)
                mime_parts = header.split(":")[1].split(";")[0] if ":" in header else "image/png"
                image_mime = mime_parts.strip() or "image/png"
                image_bytes = base64.b64decode(encoded)
            else:
                image_bytes = base64.b64decode(image_base64)
                image_mime = "image/png"
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to decode image: {str(e)}"
            )
        
        # Decode audio
        try:
            if audio_base64.startswith("data:"):
                if "," not in audio_base64:
                    raise ValueError("Invalid data URI format: missing comma separator")
                header, encoded = audio_base64.split(",", 1)
                mime_parts = header.split(":")[1].split(";")[0] if ":" in header else "audio/mpeg"
                audio_mime = mime_parts.strip() or "audio/mpeg"
                audio_bytes = base64.b64decode(encoded)
            else:
                audio_bytes = base64.b64decode(audio_base64)
                audio_mime = "audio/mpeg"
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to decode audio: {str(e)}"
            )
        
        # Call Hunyuan Avatar function (run in thread since it's synchronous)
        try:
            result = await asyncio.to_thread(
                create_hunyuan_avatar,
                image_bytes=image_bytes,
                audio_bytes=audio_bytes,
                resolution=resolution,
                prompt=prompt,
                seed=seed,
                user_id=user_id,
                image_mime=image_mime,
                audio_mime=audio_mime,
                client=self.client,
                progress_callback=progress_callback,
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[Hunyuan Avatar Adapter] Error: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Hunyuan Avatar generation failed: {str(e)}"
            )
        
        # Calculate actual cost based on duration
        actual_cost = self.calculate_cost(resolution, result.get("duration", 5.0))
        
        # Update result with actual cost and additional metadata
        result["cost"] = actual_cost
        result["resolution"] = resolution
        
        # Get video dimensions from resolution
        resolution_dims = {
            "480p": (854, 480),
            "720p": (1280, 720),
        }
        width, height = resolution_dims.get(resolution, (854, 480))
        result["width"] = width
        result["height"] = height
        
        logger.info(
            f"[Hunyuan Avatar Adapter] ✅ Generated talking avatar: "
            f"resolution={resolution}, duration={result.get('duration', 5.0)}s, cost=${actual_cost:.2f}"
        )
        
        return result
