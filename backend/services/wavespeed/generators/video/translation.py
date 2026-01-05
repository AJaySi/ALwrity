"""
Video translation operations.
"""

import requests
from typing import Optional, Callable
from fastapi import HTTPException

from utils.logger_utils import get_service_logger
from .base import VideoBase

logger = get_service_logger("wavespeed.generators.video.translation")


class VideoTranslation(VideoBase):
    """Video translation operations."""
    
    def video_translate(
        self,
        video: str,  # Base64-encoded video or URL
        output_language: str = "English",
        enable_sync_mode: bool = False,
        timeout: int = 600,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> bytes:
        """
        Translate video to target language using HeyGen Video Translate.
        
        Args:
            video: Base64-encoded video data URI or public URL (source video)
            output_language: Target language for translation (default: "English")
            enable_sync_mode: If True, wait for result and return it directly
            timeout: Request timeout in seconds (default: 600)
            progress_callback: Optional callback function(progress: float, message: str) for progress updates
            
        Returns:
            bytes: Translated video bytes
            
        Raises:
            HTTPException: If the video translation fails
        """
        model_path = "heygen/video-translate"
        url = f"{self.base_url}/{model_path}"
        
        # Build payload
        payload = {
            "video": video,
            "output_language": output_language,
        }
        
        logger.info(
            f"[WaveSpeed] Video translate request via {url} "
            f"(output_language={output_language})"
        )
        
        # Submit the task
        response = requests.post(url, headers=self._get_headers(), json=payload, timeout=timeout)
        
        if response.status_code != 200:
            logger.error(f"[WaveSpeed] Video translate submission failed: {response.status_code} {response.text}")
            raise HTTPException(
                status_code=502,
                detail={
                    "error": "WaveSpeed video translate submission failed",
                    "status_code": response.status_code,
                    "response": response.text,
                },
            )
        
        response_json = response.json()
        data = response_json.get("data") or response_json
        
        if not data or "id" not in data:
            logger.error(f"[WaveSpeed] Unexpected video translate response: {response.text}")
            raise HTTPException(
                status_code=502,
                detail={"error": "WaveSpeed response missing prediction id"},
            )
        
        prediction_id = data["id"]
        logger.info(f"[WaveSpeed] Video translate submitted: {prediction_id}")
        
        if enable_sync_mode:
            # Poll until complete
            result = self.polling.poll_until_complete(
                prediction_id,
                timeout_seconds=timeout,
                interval_seconds=2.0,
                progress_callback=progress_callback,
            )
            
            # Extract video URL from result
            outputs = result.get("outputs", [])
            if not outputs:
                raise HTTPException(
                    status_code=502,
                    detail={"error": "Video translate completed but no output video found"},
                )
            
            # Handle outputs - can be array of strings or array of objects
            video_url = None
            if isinstance(outputs[0], str):
                video_url = outputs[0]
            elif isinstance(outputs[0], dict):
                video_url = outputs[0].get("url") or outputs[0].get("video_url")
            
            if not video_url:
                raise HTTPException(
                    status_code=502,
                    detail={"error": "Video translate output format not recognized"},
                )
            
            # Download video
            logger.info(f"[WaveSpeed] Downloading translated video from: {video_url}")
            video_response = requests.get(video_url, timeout=timeout)
            if video_response.status_code != 200:
                raise HTTPException(
                    status_code=502,
                    detail={"error": f"Failed to download translated video: {video_response.status_code}"},
                )
            
            video_bytes = video_response.content
            logger.info(f"[WaveSpeed] Video translate completed: {len(video_bytes)} bytes")
            return video_bytes
        else:
            # Return prediction ID for async polling
            raise HTTPException(
                status_code=501,
                detail={
                    "error": "Async mode not yet implemented for video translate",
                    "prediction_id": prediction_id,
                },
            )
