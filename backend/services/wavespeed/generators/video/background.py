"""
Video background removal operations.
"""

import requests
from typing import Optional, Callable
from fastapi import HTTPException

from utils.logging import get_service_logger
from .base import VideoBase

logger = get_service_logger("wavespeed.generators.video.background")


class VideoBackground(VideoBase):
    """Video background removal operations."""
    
    def remove_background(
        self,
        video: str,  # Base64-encoded video or URL
        background_image: Optional[str] = None,  # Base64-encoded image or URL (optional)
        enable_sync_mode: bool = False,
        timeout: int = 300,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> bytes:
        """
        Remove or replace video background using Video Background Remover.
        
        Args:
            video: Base64-encoded video data URI or public URL (source video)
            background_image: Optional base64-encoded image data URI or public URL (replacement background)
            enable_sync_mode: If True, wait for result and return it directly
            timeout: Request timeout in seconds (default: 300)
            progress_callback: Optional callback function(progress: float, message: str) for progress updates
            
        Returns:
            bytes: Video with background removed/replaced
            
        Raises:
            HTTPException: If the background removal fails
        """
        model_path = "wavespeed-ai/video-background-remover"
        url = f"{self.base_url}/{model_path}"
        
        # Build payload
        payload = {
            "video": video,
        }
        
        if background_image:
            payload["background_image"] = background_image
        
        logger.info(
            f"[WaveSpeed] Video background removal request via {url} "
            f"(has_background={background_image is not None})"
        )
        
        # Submit the task
        response = requests.post(url, headers=self._get_headers(), json=payload, timeout=timeout)
        
        if response.status_code != 200:
            logger.error(f"[WaveSpeed] Video background removal submission failed: {response.status_code} {response.text}")
            raise HTTPException(
                status_code=502,
                detail={
                    "error": "WaveSpeed video background removal submission failed",
                    "status_code": response.status_code,
                    "response": response.text,
                },
            )
        
        response_json = response.json()
        data = response_json.get("data") or response_json
        prediction_id = data.get("id")
        
        if not prediction_id:
            logger.error(f"[WaveSpeed] No prediction ID in video background removal response: {response.text}")
            raise HTTPException(
                status_code=502,
                detail="WaveSpeed video background removal response missing prediction id",
            )
        
        logger.info(f"[WaveSpeed] Video background removal task submitted: {prediction_id}")
        
        if enable_sync_mode:
            result = self.polling.poll_until_complete(
                prediction_id,
                timeout_seconds=timeout,
                interval_seconds=2.0,
                progress_callback=progress_callback,
            )
            
            outputs = result.get("outputs") or []
            if not outputs:
                raise HTTPException(status_code=502, detail="WaveSpeed video background removal returned no outputs")
            
            video_url = None
            if isinstance(outputs[0], str):
                video_url = outputs[0]
            elif isinstance(outputs[0], dict):
                video_url = outputs[0].get("url") or outputs[0].get("video_url")
            
            if not video_url:
                raise HTTPException(status_code=502, detail="WaveSpeed video background removal output format not recognized")
            
            logger.info(f"[WaveSpeed] Downloading processed video from: {video_url}")
            video_response = requests.get(video_url, timeout=timeout)
            
            if video_response.status_code != 200:
                logger.error(f"[WaveSpeed] Failed to download processed video: {video_response.status_code}")
                raise HTTPException(
                    status_code=502,
                    detail="Failed to download processed video from WaveSpeed",
                )
            
            video_bytes = video_response.content
            logger.info(f"[WaveSpeed] Video background removal completed successfully (size: {len(video_bytes)} bytes)")
            
            return video_bytes
        else:
            raise HTTPException(
                status_code=501,
                detail={
                    "error": "Async mode not yet implemented for video background removal",
                    "prediction_id": prediction_id,
                },
            )
