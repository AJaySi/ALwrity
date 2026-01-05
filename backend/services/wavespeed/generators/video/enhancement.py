"""
Video enhancement operations (upscaling).
"""

import requests
from typing import Optional, Callable
from fastapi import HTTPException

from utils.logger_utils import get_service_logger
from .base import VideoBase

logger = get_service_logger("wavespeed.generators.video.enhancement")


class VideoEnhancement(VideoBase):
    """Video enhancement operations."""
    
    def upscale_video(
        self,
        video: str,  # Base64-encoded video or URL
        target_resolution: str = "1080p",
        enable_sync_mode: bool = False,
        timeout: int = 300,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> bytes:
        """
        Upscale video using FlashVSR.
        
        Args:
            video: Base64-encoded video data URI or public URL
            target_resolution: Target resolution ("720p", "1080p", "2k", "4k")
            enable_sync_mode: If True, wait for result and return it directly
            timeout: Request timeout in seconds (default: 300 for long videos)
            progress_callback: Optional callback function(progress: float, message: str) for progress updates
            
        Returns:
            bytes: Upscaled video bytes
            
        Raises:
            HTTPException: If the upscaling fails
        """
        model_path = "wavespeed-ai/flashvsr"
        url = f"{self.base_url}/{model_path}"
        
        payload = {
            "video": video,
            "target_resolution": target_resolution,
        }
        
        logger.info(f"[WaveSpeed] Upscaling video via {url} (target={target_resolution})")
        
        # Submit the task
        response = requests.post(url, headers=self._get_headers(), json=payload, timeout=timeout)
        
        if response.status_code != 200:
            logger.error(f"[WaveSpeed] FlashVSR submission failed: {response.status_code} {response.text}")
            raise HTTPException(
                status_code=502,
                detail={
                    "error": "WaveSpeed FlashVSR submission failed",
                    "status_code": response.status_code,
                    "response": response.text,
                },
            )
        
        response_json = response.json()
        data = response_json.get("data") or response_json
        prediction_id = data.get("id")
        
        if not prediction_id:
            logger.error(f"[WaveSpeed] No prediction ID in FlashVSR response: {response.text}")
            raise HTTPException(
                status_code=502,
                detail="WaveSpeed FlashVSR response missing prediction id",
            )
        
        logger.info(f"[WaveSpeed] FlashVSR task submitted: {prediction_id}")
        
        # Poll for result
        result = self.polling.poll_until_complete(
            prediction_id,
            timeout_seconds=timeout,
            interval_seconds=2.0,  # Longer interval for upscaling (slower process)
            progress_callback=progress_callback,
        )
        
        outputs = result.get("outputs") or []
        if not outputs:
            raise HTTPException(status_code=502, detail="WaveSpeed FlashVSR returned no outputs")
        
        video_url = outputs[0] if isinstance(outputs[0], str) else outputs[0].get("url")
        if not video_url:
            raise HTTPException(status_code=502, detail="WaveSpeed FlashVSR output format not recognized")
        
        # Download the upscaled video
        logger.info(f"[WaveSpeed] Downloading upscaled video from: {video_url}")
        video_response = requests.get(video_url, timeout=timeout)
        
        if video_response.status_code != 200:
            logger.error(f"[WaveSpeed] Failed to download upscaled video: {video_response.status_code}")
            raise HTTPException(
                status_code=502,
                detail="Failed to download upscaled video from WaveSpeed",
            )
        
        video_bytes = video_response.content
        logger.info(f"[WaveSpeed] Video upscaling completed successfully (size: {len(video_bytes)} bytes)")
        
        return video_bytes
