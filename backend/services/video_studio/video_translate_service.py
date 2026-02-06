"""
Video Translate service for Video Studio.

Uses HeyGen Video Translate (heygen/video-translate) for video translation.
"""

import base64
from typing import Dict, Any, Optional, Callable
from fastapi import HTTPException

from utils.logging import get_service_logger
from ..wavespeed.client import WaveSpeedClient

logger = get_service_logger("video_studio.video_translate")


class VideoTranslateService:
    """Service for video translation operations."""
    
    def __init__(self):
        """Initialize Video Translate service."""
        self.wavespeed_client = WaveSpeedClient()
        logger.info("[VideoTranslate] Service initialized")
    
    def calculate_cost(self, duration: float = 10.0) -> float:
        """
        Calculate cost for video translation operation.
        
        Args:
            duration: Video duration in seconds
            
        Returns:
            Cost in USD
        """
        # HeyGen Video Translate pricing: $0.0375/s
        # No minimum charge mentioned in docs, but we'll use 1 second minimum
        cost_per_second = 0.0375
        billed_duration = max(1.0, duration)
        return cost_per_second * billed_duration
    
    async def translate_video(
        self,
        video_data: bytes,
        output_language: str = "English",
        user_id: str = None,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> Dict[str, Any]:
        """
        Translate video to target language using HeyGen Video Translate.
        
        Args:
            video_data: Source video as bytes
            output_language: Target language for translation
            user_id: User ID for tracking
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dict with translated video_url, cost, and metadata
        """
        try:
            logger.info(
                f"[VideoTranslate] Video translate request: user={user_id}, "
                f"output_language={output_language}"
            )
            
            if not user_id:
                raise ValueError("user_id is required for video translation")
            
            # Convert video to base64 data URI
            video_b64 = base64.b64encode(video_data).decode('utf-8')
            video_uri = f"data:video/mp4;base64,{video_b64}"
            
            # Estimate duration (we'll use a default, actual duration would come from video metadata)
            estimated_duration = 10.0  # Default estimate, should be improved with actual video duration
            
            # Calculate cost estimate
            cost = self.calculate_cost(estimated_duration)
            
            if progress_callback:
                progress_callback(10.0, f"Submitting video translation request to HeyGen ({output_language})...")
            
            # Perform video translation
            # video_translate is synchronous (uses sync_mode internally)
            translated_video_bytes = self.wavespeed_client.video_translate(
                video=video_uri,
                output_language=output_language,
                enable_sync_mode=True,
                timeout=600,  # 10 minutes timeout
                progress_callback=progress_callback,
            )
            
            if progress_callback:
                progress_callback(90.0, "Video translation complete, saving video...")
            
            # Save translated video
            from . import VideoStudioService
            video_service = VideoStudioService()
            save_result = video_service._save_video_file(
                video_bytes=translated_video_bytes,
                operation_type="video_translate",
                user_id=user_id,
            )
            
            # Recalculate cost with actual duration if available
            # For now, use estimated cost
            actual_cost = cost
            
            logger.info(
                f"[VideoTranslate] Video translate successful: user={user_id}, "
                f"output_language={output_language}, cost=${actual_cost:.4f}"
            )
            
            metadata = {
                "original_video_size": len(video_data),
                "translated_video_size": len(translated_video_bytes),
                "output_language": output_language,
            }
            
            return {
                "success": True,
                "video_url": save_result["file_url"],
                "video_bytes": translated_video_bytes,
                "cost": actual_cost,
                "output_language": output_language,
                "metadata": metadata,
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[VideoTranslate] Video translate error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
