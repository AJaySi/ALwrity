"""
Video audio generation operations.
"""

import requests
from typing import Optional, Callable
from fastapi import HTTPException

from utils.logging import get_service_logger
from .base import VideoBase

logger = get_service_logger("wavespeed.generators.video.audio")


class VideoAudio(VideoBase):
    """Video audio generation operations."""
    
    def hunyuan_video_foley(
        self,
        video: str,  # Base64-encoded video or URL
        prompt: Optional[str] = None,  # Optional text prompt describing desired sounds
        seed: int = -1,  # Random seed (-1 for random)
        enable_sync_mode: bool = False,
        timeout: int = 300,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> bytes:
        """
        Generate realistic Foley and ambient audio from video using Hunyuan Video Foley.
        
        Args:
            video: Base64-encoded video data URI or public URL (source video)
            prompt: Optional text prompt describing desired sounds (e.g., "ocean waves, seagulls")
            seed: Random seed for reproducibility (-1 for random)
            enable_sync_mode: If True, wait for result and return it directly
            timeout: Request timeout in seconds (default: 300)
            progress_callback: Optional callback function(progress: float, message: str) for progress updates
            
        Returns:
            bytes: Video with generated audio
            
        Raises:
            HTTPException: If the audio generation fails
        """
        model_path = "wavespeed-ai/hunyuan-video-foley"
        url = f"{self.base_url}/{model_path}"
        
        # Build payload
        payload = {
            "video": video,
            "seed": seed,
        }
        
        if prompt:
            payload["prompt"] = prompt
        
        logger.info(
            f"[WaveSpeed] Hunyuan Video Foley request via {url} "
            f"(has_prompt={prompt is not None}, seed={seed})"
        )
        
        # Submit the task
        response = requests.post(url, headers=self._get_headers(), json=payload, timeout=timeout)
        
        if response.status_code != 200:
            logger.error(f"[WaveSpeed] Hunyuan Video Foley submission failed: {response.status_code} {response.text}")
            raise HTTPException(
                status_code=502,
                detail={
                    "error": "WaveSpeed Hunyuan Video Foley submission failed",
                    "status_code": response.status_code,
                    "response": response.text,
                },
            )
        
        response_json = response.json()
        data = response_json.get("data") or response_json
        prediction_id = data.get("id")
        
        if not prediction_id:
            logger.error(f"[WaveSpeed] No prediction ID in Hunyuan Video Foley response: {response.text}")
            raise HTTPException(
                status_code=502,
                detail="WaveSpeed Hunyuan Video Foley response missing prediction id",
            )
        
        logger.info(f"[WaveSpeed] Hunyuan Video Foley task submitted: {prediction_id}")
        
        if enable_sync_mode:
            result = self.polling.poll_until_complete(
                prediction_id,
                timeout_seconds=timeout,
                interval_seconds=2.0,
                progress_callback=progress_callback,
            )
            
            outputs = result.get("outputs") or []
            if not outputs:
                raise HTTPException(status_code=502, detail="WaveSpeed Hunyuan Video Foley returned no outputs")
            
            video_url = None
            if isinstance(outputs[0], str):
                video_url = outputs[0]
            elif isinstance(outputs[0], dict):
                video_url = outputs[0].get("url") or outputs[0].get("video_url")
            
            if not video_url:
                raise HTTPException(status_code=502, detail="WaveSpeed Hunyuan Video Foley output format not recognized")
            
            logger.info(f"[WaveSpeed] Downloading video with audio from: {video_url}")
            video_response = requests.get(video_url, timeout=timeout)
            
            if video_response.status_code != 200:
                logger.error(f"[WaveSpeed] Failed to download video with audio: {video_response.status_code}")
                raise HTTPException(
                    status_code=502,
                    detail="Failed to download video with audio from WaveSpeed",
                )
            
            video_bytes = video_response.content
            logger.info(f"[WaveSpeed] Hunyuan Video Foley completed successfully (size: {len(video_bytes)} bytes)")
            
            return video_bytes
        else:
            raise HTTPException(
                status_code=501,
                detail={
                    "error": "Async mode not yet implemented for Hunyuan Video Foley",
                    "prediction_id": prediction_id,
                },
            )
    
    def think_sound(
        self,
        video: str,  # Base64-encoded video or URL
        prompt: Optional[str] = None,  # Optional text prompt describing desired sounds
        seed: int = -1,  # Random seed (-1 for random)
        enable_sync_mode: bool = False,
        timeout: int = 300,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> bytes:
        """
        Generate realistic sound effects and audio tracks from video using Think Sound.
        
        Args:
            video: Base64-encoded video data URI or public URL (source video)
            prompt: Optional text prompt describing desired sounds (e.g., "engine roaring, footsteps on gravel")
            seed: Random seed for reproducibility (-1 for random)
            enable_sync_mode: If True, wait for result and return it directly
            timeout: Request timeout in seconds (default: 300)
            progress_callback: Optional callback function(progress: float, message: str) for progress updates
            
        Returns:
            bytes: Video with generated audio
            
        Raises:
            HTTPException: If the audio generation fails
        """
        model_path = "wavespeed-ai/think-sound"
        url = f"{self.base_url}/{model_path}"
        
        # Build payload
        payload = {
            "video": video,
            "seed": seed,
        }
        
        if prompt:
            payload["prompt"] = prompt
        
        logger.info(
            f"[WaveSpeed] Think Sound request via {url} "
            f"(has_prompt={prompt is not None}, seed={seed})"
        )
        
        # Submit the task
        response = requests.post(url, headers=self._get_headers(), json=payload, timeout=timeout)
        
        if response.status_code != 200:
            logger.error(f"[WaveSpeed] Think Sound submission failed: {response.status_code} {response.text}")
            raise HTTPException(
                status_code=502,
                detail={
                    "error": "WaveSpeed Think Sound submission failed",
                    "status_code": response.status_code,
                    "response": response.text,
                },
            )
        
        response_json = response.json()
        data = response_json.get("data") or response_json
        prediction_id = data.get("id")
        
        if not prediction_id:
            logger.error(f"[WaveSpeed] No prediction ID in Think Sound response: {response.text}")
            raise HTTPException(
                status_code=502,
                detail="WaveSpeed Think Sound response missing prediction id",
            )
        
        logger.info(f"[WaveSpeed] Think Sound task submitted: {prediction_id}")
        
        if enable_sync_mode:
            result = self.polling.poll_until_complete(
                prediction_id,
                timeout_seconds=timeout,
                interval_seconds=2.0,
                progress_callback=progress_callback,
            )
            
            outputs = result.get("outputs") or []
            if not outputs:
                raise HTTPException(status_code=502, detail="WaveSpeed Think Sound returned no outputs")
            
            video_url = None
            if isinstance(outputs[0], str):
                video_url = outputs[0]
            elif isinstance(outputs[0], dict):
                video_url = outputs[0].get("url") or outputs[0].get("video_url")
            
            if not video_url:
                raise HTTPException(status_code=502, detail="WaveSpeed Think Sound output format not recognized")
            
            logger.info(f"[WaveSpeed] Downloading video with audio from: {video_url}")
            video_response = requests.get(video_url, timeout=timeout)
            
            if video_response.status_code != 200:
                logger.error(f"[WaveSpeed] Failed to download video with audio: {video_response.status_code}")
                raise HTTPException(
                    status_code=502,
                    detail="Failed to download video with audio from WaveSpeed",
                )
            
            video_bytes = video_response.content
            logger.info(f"[WaveSpeed] Think Sound completed successfully (size: {len(video_bytes)} bytes)")
            
            return video_bytes
        else:
            raise HTTPException(
                status_code=501,
                detail={
                    "error": "Async mode not yet implemented for Think Sound",
                    "prediction_id": prediction_id,
                },
            )
