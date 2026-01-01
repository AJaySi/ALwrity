"""
Video Background Remover service for Video Studio.

Removes or replaces video backgrounds using WaveSpeed Video Background Remover.
"""

import asyncio
import base64
from typing import Dict, Any, Optional, Callable
from fastapi import HTTPException

from utils.logger_utils import get_service_logger
from ..wavespeed.client import WaveSpeedClient

logger = get_service_logger("video_studio.video_background_remover")


class VideoBackgroundRemoverService:
    """Service for video background removal/replacement operations."""
    
    def __init__(self):
        """Initialize Video Background Remover service."""
        self.wavespeed_client = WaveSpeedClient()
        logger.info("[VideoBackgroundRemover] Service initialized")
    
    def calculate_cost(self, duration: float = 10.0) -> float:
        """
        Calculate cost for video background removal operation.
        
        Pricing from WaveSpeed documentation:
        - Rate: $0.01 per second
        - Minimum: $0.05 for ≤5 seconds
        - Maximum: $6.00 for 600 seconds (10 minutes)
        
        Args:
            duration: Video duration in seconds
            
        Returns:
            Cost in USD
        """
        # Pricing: $0.01 per second
        # Minimum charge: $0.05 for ≤5 seconds
        # Maximum: $6.00 for 600 seconds (10 minutes)
        cost_per_second = 0.01
        if duration <= 5.0:
            return 0.05  # Minimum charge
        elif duration >= 600.0:
            return 6.00  # Maximum charge
        else:
            return duration * cost_per_second
    
    async def remove_background(
        self,
        video_data: bytes,
        background_image_data: Optional[bytes] = None,
        user_id: str = None,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> Dict[str, Any]:
        """
        Remove or replace video background.
        
        Args:
            video_data: Source video as bytes
            background_image_data: Optional replacement background image as bytes
            user_id: User ID for tracking
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dict with processed video_url, cost, and metadata
        """
        try:
            logger.info(f"[VideoBackgroundRemover] Background removal request: user={user_id}, has_background={background_image_data is not None}")
            
            # Convert video to base64 data URI
            video_b64 = base64.b64encode(video_data).decode('utf-8')
            video_uri = f"data:video/mp4;base64,{video_b64}"
            
            # Convert background image to base64 if provided
            background_image_uri = None
            if background_image_data:
                image_b64 = base64.b64encode(background_image_data).decode('utf-8')
                background_image_uri = f"data:image/jpeg;base64,{image_b64}"
            
            # Call WaveSpeed API
            processed_video_bytes = await asyncio.to_thread(
                self.wavespeed_client.remove_background,
                video=video_uri,
                background_image=background_image_uri,
                enable_sync_mode=False,  # Always use async with polling
                timeout=600,  # 10 minutes max for long videos
                progress_callback=progress_callback,
            )
            
            # Estimate video duration (rough estimate: 1MB ≈ 1 second at 1080p)
            estimated_duration = max(5, len(video_data) / (1024 * 1024))  # Minimum 5 seconds
            cost = self.calculate_cost(estimated_duration)
            
            # Save processed video
            from .video_studio_service import VideoStudioService
            video_service = VideoStudioService()
            save_result = video_service._save_video_file(
                video_bytes=processed_video_bytes,
                operation_type="background_removal",
                user_id=user_id,
            )
            
            logger.info(f"[VideoBackgroundRemover] Background removal successful: user={user_id}, cost=${cost:.4f}")
            
            return {
                "success": True,
                "video_url": save_result["file_url"],
                "video_bytes": processed_video_bytes,
                "cost": cost,
                "has_background_replacement": background_image_data is not None,
                "metadata": {
                    "original_size": len(video_data),
                    "processed_size": len(processed_video_bytes),
                    "estimated_duration": estimated_duration,
                },
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[VideoBackgroundRemover] Background removal failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Video background removal failed: {str(e)}"
            )
