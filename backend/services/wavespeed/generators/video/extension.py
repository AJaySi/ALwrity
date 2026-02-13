"""
Video extension operations.
"""

import requests
from typing import Optional, Callable
from fastapi import HTTPException

from utils.logging import get_service_logger
from .base import VideoBase

logger = get_service_logger("wavespeed.generators.video.extension")


class VideoExtension(VideoBase):
    """Video extension operations."""
    
    def extend_video(
        self,
        video: str,  # Base64-encoded video or URL
        prompt: str,
        model: str = "wan-2.5",  # "wan-2.5", "wan-2.2-spicy", or "seedance-1.5-pro"
        audio: Optional[str] = None,  # Optional audio URL (WAN 2.5 only)
        negative_prompt: Optional[str] = None,  # WAN 2.5 only
        resolution: str = "720p",
        duration: int = 5,
        enable_prompt_expansion: bool = False,  # WAN 2.5 only
        generate_audio: bool = True,  # Seedance 1.5 Pro only
        camera_fixed: bool = False,  # Seedance 1.5 Pro only
        seed: Optional[int] = None,
        enable_sync_mode: bool = False,
        timeout: int = 300,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> bytes:
        """
        Extend video duration using WAN 2.5, WAN 2.2 Spicy, or Seedance 1.5 Pro video-extend.
        
        Args:
            video: Base64-encoded video data URI or public URL
            prompt: Text prompt describing how to extend the video
            model: Model to use ("wan-2.5", "wan-2.2-spicy", or "seedance-1.5-pro")
            audio: Optional audio URL to guide generation (WAN 2.5 only)
            negative_prompt: Optional negative prompt (WAN 2.5 only)
            resolution: Output resolution (varies by model)
            duration: Duration of extended video in seconds (varies by model)
            enable_prompt_expansion: Enable prompt optimizer (WAN 2.5 only)
            generate_audio: Generate audio for extended video (Seedance 1.5 Pro only)
            camera_fixed: Fix camera position (Seedance 1.5 Pro only)
            seed: Random seed for reproducibility (-1 for random)
            enable_sync_mode: If True, wait for result and return it directly
            timeout: Request timeout in seconds (default: 300)
            progress_callback: Optional callback function(progress: float, message: str) for progress updates
            
        Returns:
            bytes: Extended video bytes
            
        Raises:
            HTTPException: If the extension fails
        """
        # Determine model path
        if model in ("wan-2.2-spicy", "wavespeed-ai/wan-2.2-spicy/video-extend"):
            model_path = "wavespeed-ai/wan-2.2-spicy/video-extend"
        elif model in ("seedance-1.5-pro", "bytedance/seedance-v1.5-pro/video-extend"):
            model_path = "bytedance/seedance-v1.5-pro/video-extend"
        else:
            # Default to WAN 2.5
            model_path = "alibaba/wan-2.5/video-extend"
        
        url = f"{self.base_url}/{model_path}"
        
        # Base payload (common to all models)
        payload = {
            "video": video,
            "prompt": prompt,
            "resolution": resolution,
            "duration": duration,
        }
        
        # Model-specific parameters
        if model_path == "alibaba/wan-2.5/video-extend":
            # WAN 2.5 specific
            payload["enable_prompt_expansion"] = enable_prompt_expansion
            if audio:
                payload["audio"] = audio
            if negative_prompt:
                payload["negative_prompt"] = negative_prompt
        elif model_path == "bytedance/seedance-v1.5-pro/video-extend":
            # Seedance 1.5 Pro specific
            payload["generate_audio"] = generate_audio
            payload["camera_fixed"] = camera_fixed
        
        # Seed (all models support it)
        if seed is not None:
            payload["seed"] = seed
        
        logger.info(f"[WaveSpeed] Extending video via {url} (duration={duration}s, resolution={resolution})")
        
        # Submit the task
        response = requests.post(url, headers=self._get_headers(), json=payload, timeout=timeout)
        
        if response.status_code != 200:
            logger.error(f"[WaveSpeed] Video extend submission failed: {response.status_code} {response.text}")
            raise HTTPException(
                status_code=502,
                detail={
                    "error": "WaveSpeed video extend submission failed",
                    "status_code": response.status_code,
                    "response": response.text,
                },
            )
        
        response_json = response.json()
        data = response_json.get("data") or response_json
        prediction_id = data.get("id")
        
        if not prediction_id:
            logger.error(f"[WaveSpeed] No prediction ID in video extend response: {response.text}")
            raise HTTPException(
                status_code=502,
                detail="WaveSpeed video extend response missing prediction id",
            )
        
        logger.info(f"[WaveSpeed] Video extend task submitted: {prediction_id}")
        
        # Poll for result
        result = self.polling.poll_until_complete(
            prediction_id,
            timeout_seconds=timeout,
            interval_seconds=2.0,
            progress_callback=progress_callback,
        )
        
        outputs = result.get("outputs") or []
        if not outputs:
            raise HTTPException(status_code=502, detail="WaveSpeed video extend returned no outputs")
        
        # Handle outputs - can be array of strings or array of objects
        video_url = None
        if isinstance(outputs[0], str):
            video_url = outputs[0]
        elif isinstance(outputs[0], dict):
            video_url = outputs[0].get("url") or outputs[0].get("video_url")
        
        if not video_url:
            raise HTTPException(status_code=502, detail="WaveSpeed video extend output format not recognized")
        
        # Download the extended video
        logger.info(f"[WaveSpeed] Downloading extended video from: {video_url}")
        video_response = requests.get(video_url, timeout=timeout)
        
        if video_response.status_code != 200:
            logger.error(f"[WaveSpeed] Failed to download extended video: {video_response.status_code}")
            raise HTTPException(
                status_code=502,
                detail="Failed to download extended video from WaveSpeed",
            )
        
        video_bytes = video_response.content
        logger.info(f"[WaveSpeed] Video extension completed successfully (size: {len(video_bytes)} bytes)")
        
        return video_bytes
