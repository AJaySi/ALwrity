"""
Face swap operations.
"""

import requests
from typing import Optional, Callable
from fastapi import HTTPException

from utils.logging import get_service_logger
from .base import VideoBase

logger = get_service_logger("wavespeed.generators.video.face_swap")


class VideoFaceSwap(VideoBase):
    """Face swap operations."""
    
    def face_swap(
        self,
        image: str,  # Base64-encoded image or URL
        video: str,  # Base64-encoded video or URL
        prompt: Optional[str] = None,
        resolution: str = "480p",
        seed: Optional[int] = None,
        enable_sync_mode: bool = False,
        timeout: int = 300,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> bytes:
        """
        Perform face/character swap using MoCha (wavespeed-ai/wan-2.1/mocha).
        
        Args:
            image: Base64-encoded image data URI or public URL (reference character)
            video: Base64-encoded video data URI or public URL (source video)
            prompt: Optional prompt to guide the swap
            resolution: Output resolution ("480p" or "720p")
            seed: Random seed for reproducibility (-1 for random)
            enable_sync_mode: If True, wait for result and return it directly
            timeout: Request timeout in seconds (default: 300)
            progress_callback: Optional callback function(progress: float, message: str) for progress updates
            
        Returns:
            bytes: Face-swapped video bytes
            
        Raises:
            HTTPException: If the face swap fails
        """
        model_path = "wavespeed-ai/wan-2.1/mocha"
        url = f"{self.base_url}/{model_path}"
        
        # Build payload
        payload = {
            "image": image,
            "video": video,
        }
        
        if prompt:
            payload["prompt"] = prompt
        
        if resolution in ("480p", "720p"):
            payload["resolution"] = resolution
        else:
            payload["resolution"] = "480p"  # Default
        
        if seed is not None:
            payload["seed"] = seed
        else:
            payload["seed"] = -1  # Random seed
        
        logger.info(
            f"[WaveSpeed] Face swap request via {url} "
            f"(resolution={payload['resolution']}, seed={payload['seed']})"
        )
        
        # Submit the task
        response = requests.post(url, headers=self._get_headers(), json=payload, timeout=timeout)
        
        if response.status_code != 200:
            logger.error(f"[WaveSpeed] Face swap submission failed: {response.status_code} {response.text}")
            raise HTTPException(
                status_code=502,
                detail={
                    "error": "WaveSpeed face swap submission failed",
                    "status_code": response.status_code,
                    "response": response.text,
                },
            )
        
        response_json = response.json()
        data = response_json.get("data") or response_json
        
        if not data or "id" not in data:
            logger.error(f"[WaveSpeed] Unexpected face swap response: {response.text}")
            raise HTTPException(
                status_code=502,
                detail={"error": "WaveSpeed response missing prediction id"},
            )
        
        prediction_id = data["id"]
        logger.info(f"[WaveSpeed] Face swap submitted: {prediction_id}")
        
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
                    detail={"error": "Face swap completed but no output video found"},
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
                    detail={"error": "Face swap output format not recognized"},
                )
            
            # Download video
            logger.info(f"[WaveSpeed] Downloading face-swapped video from: {video_url}")
            video_response = requests.get(video_url, timeout=timeout)
            if video_response.status_code != 200:
                raise HTTPException(
                    status_code=502,
                    detail={"error": f"Failed to download face-swapped video: {video_response.status_code}"},
                )
            
            video_bytes = video_response.content
            logger.info(f"[WaveSpeed] Face swap completed: {len(video_bytes)} bytes")
            return video_bytes
        else:
            # Return prediction ID for async polling
            raise HTTPException(
                status_code=501,
                detail={
                    "error": "Async mode not yet implemented for face swap",
                    "prediction_id": prediction_id,
                },
            )
    
    def video_face_swap(
        self,
        video: str,  # Base64-encoded video or URL
        face_image: str,  # Base64-encoded image or URL
        target_gender: str = "all",
        target_index: int = 0,
        enable_sync_mode: bool = False,
        timeout: int = 300,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> bytes:
        """
        Perform face swap using Video Face Swap (wavespeed-ai/video-face-swap).
        
        Args:
            video: Base64-encoded video data URI or public URL (source video)
            face_image: Base64-encoded image data URI or public URL (reference face)
            target_gender: Filter which faces to swap ("all", "female", "male")
            target_index: Select which face to swap (0 = largest, 1 = second largest, etc.)
            enable_sync_mode: If True, wait for result and return it directly
            timeout: Request timeout in seconds (default: 300)
            progress_callback: Optional callback function(progress: float, message: str) for progress updates
            
        Returns:
            bytes: Face-swapped video bytes
            
        Raises:
            HTTPException: If the face swap fails
        """
        model_path = "wavespeed-ai/video-face-swap"
        url = f"{self.base_url}/{model_path}"
        
        # Build payload
        payload = {
            "video": video,
            "face_image": face_image,
        }
        
        if target_gender in ("all", "female", "male"):
            payload["target_gender"] = target_gender
        else:
            payload["target_gender"] = "all"  # Default
        
        if 0 <= target_index <= 10:
            payload["target_index"] = target_index
        else:
            payload["target_index"] = 0  # Default
        
        logger.info(
            f"[WaveSpeed] Video face swap request via {url} "
            f"(target_gender={payload['target_gender']}, target_index={payload['target_index']})"
        )
        
        # Submit the task
        response = requests.post(url, headers=self._get_headers(), json=payload, timeout=timeout)
        
        if response.status_code != 200:
            logger.error(f"[WaveSpeed] Video face swap submission failed: {response.status_code} {response.text}")
            raise HTTPException(
                status_code=502,
                detail={
                    "error": "WaveSpeed video face swap submission failed",
                    "status_code": response.status_code,
                    "response": response.text,
                },
            )
        
        response_json = response.json()
        data = response_json.get("data") or response_json
        
        if not data or "id" not in data:
            logger.error(f"[WaveSpeed] Unexpected video face swap response: {response.text}")
            raise HTTPException(
                status_code=502,
                detail={"error": "WaveSpeed response missing prediction id"},
            )
        
        prediction_id = data["id"]
        logger.info(f"[WaveSpeed] Video face swap submitted: {prediction_id}")
        
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
                    detail={"error": "Video face swap completed but no output video found"},
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
                    detail={"error": "Video face swap output format not recognized"},
                )
            
            # Download video
            logger.info(f"[WaveSpeed] Downloading face-swapped video from: {video_url}")
            video_response = requests.get(video_url, timeout=timeout)
            if video_response.status_code != 200:
                raise HTTPException(
                    status_code=502,
                    detail={"error": f"Failed to download face-swapped video: {video_response.status_code}"},
                )
            
            video_bytes = video_response.content
            logger.info(f"[WaveSpeed] Video face swap completed: {len(video_bytes)} bytes")
            return video_bytes
        else:
            # Return prediction ID for async polling
            raise HTTPException(
                status_code=501,
                detail={
                    "error": "Async mode not yet implemented for video face swap",
                    "prediction_id": prediction_id,
                },
            )
