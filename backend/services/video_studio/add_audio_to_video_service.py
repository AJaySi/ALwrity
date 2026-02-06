"""
Add Audio to Video service for Video Studio.

Supports multiple models for adding audio to videos:
1. Hunyuan Video Foley - Generate realistic Foley and ambient audio from video
2. Think Sound - (To be added)
"""

import asyncio
import base64
from typing import Dict, Any, Optional, Callable
from fastapi import HTTPException

from utils.logging import get_service_logger
from ..wavespeed.client import WaveSpeedClient

logger = get_service_logger("video_studio.add_audio_to_video")


class AddAudioToVideoService:
    """Service for adding audio to video operations."""
    
    def __init__(self):
        """Initialize Add Audio to Video service."""
        self.wavespeed_client = WaveSpeedClient()
        logger.info("[AddAudioToVideo] Service initialized")
    
    def calculate_cost(self, model: str, duration: float = 10.0) -> float:
        """
        Calculate cost for adding audio to video operation.
        
        Args:
            model: Model to use ("hunyuan-video-foley" or "think-sound")
            duration: Video duration in seconds (for Hunyuan Video Foley)
            
        Returns:
            Cost in USD
        """
        if model == "hunyuan-video-foley":
            # Estimated pricing: $0.02/s (similar to other video processing models)
            # Minimum charge: 5 seconds
            # Maximum: 600 seconds (10 minutes)
            cost_per_second = 0.02
            billed_duration = max(5.0, min(duration, 600.0))
            return cost_per_second * billed_duration
        elif model == "think-sound":
            # Think Sound pricing: $0.05 per video (flat rate)
            return 0.05
        else:
            # Default fallback
            cost_per_second = 0.02
            billed_duration = max(5.0, min(duration, 600.0))
            return cost_per_second * billed_duration
    
    async def add_audio(
        self,
        video_data: bytes,
        model: str = "hunyuan-video-foley",
        prompt: Optional[str] = None,
        seed: Optional[int] = None,
        user_id: str = None,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> Dict[str, Any]:
        """
        Add audio to video using AI models.
        
        Args:
            video_data: Source video as bytes
            model: Model to use ("hunyuan-video-foley" or "think-sound")
            prompt: Optional text prompt describing desired sounds (Hunyuan Video Foley)
            seed: Random seed for reproducibility (-1 for random)
            user_id: User ID for tracking
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dict with processed video_url, cost, and metadata
        """
        try:
            logger.info(f"[AddAudioToVideo] Audio addition request: user={user_id}, model={model}, has_prompt={prompt is not None}")
            
            # Convert video to base64 data URI
            video_b64 = base64.b64encode(video_data).decode('utf-8')
            video_uri = f"data:video/mp4;base64,{video_b64}"
            
            # Handle different models
            if model == "hunyuan-video-foley":
                # Use Hunyuan Video Foley
                processed_video_bytes = await asyncio.to_thread(
                    self.wavespeed_client.hunyuan_video_foley,
                    video=video_uri,
                    prompt=prompt,
                    seed=seed if seed is not None else -1,
                    enable_sync_mode=False,  # Always use async with polling
                    timeout=600,  # 10 minutes max for long videos
                    progress_callback=progress_callback,
                )
            else:
                # Think Sound or other models (to be implemented)
                logger.warning(f"[AddAudioToVideo] Model '{model}' not yet implemented")
                raise HTTPException(
                    status_code=400,
                    detail=f"Model '{model}' is not yet supported. Currently only 'hunyuan-video-foley' is available."
                )
            
            # Estimate video duration (rough estimate: 1MB ≈ 1 second at 1080p)
            # Only needed for Hunyuan Video Foley (per-second pricing)
            estimated_duration = max(5, len(video_data) / (1024 * 1024)) if model == "hunyuan-video-foley" else 10.0
            cost = self.calculate_cost(model, estimated_duration)
            
            # Save processed video
            from .video_studio_service import VideoStudioService
            video_service = VideoStudioService()
            save_result = video_service._save_video_file(
                video_bytes=processed_video_bytes,
                operation_type="add_audio",
                user_id=user_id,
            )
            
            logger.info(f"[AddAudioToVideo] Audio addition successful: user={user_id}, model={model}, cost=${cost:.4f}")
            
            return {
                "success": True,
                "video_url": save_result["file_url"],
                "video_bytes": processed_video_bytes,
                "cost": cost,
                "model_used": model,
                "metadata": {
                    "original_size": len(video_data),
                    "processed_size": len(processed_video_bytes),
                    "estimated_duration": estimated_duration,
                    "has_prompt": prompt is not None,
                },
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[AddAudioToVideo] Audio addition failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Adding audio to video failed: {str(e)}"
            )
