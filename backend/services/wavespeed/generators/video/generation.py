"""
Video generation operations (text-to-video and image-to-video).
"""

import requests
from typing import Any, Dict, Optional
from fastapi import HTTPException

from utils.logging import get_service_logger
from .base import VideoBase

logger = get_service_logger("wavespeed.generators.video.generation")


class VideoGeneration(VideoBase):
    """Video generation operations."""
    
    def submit_image_to_video(
        self,
        model_path: str,
        payload: Dict[str, Any],
        timeout: int = 30,
    ) -> str:
        """
        Submit an image-to-video generation request.

        Returns the prediction ID for polling.
        """
        url = f"{self.base_url}/{model_path}"
        logger.info(f"[WaveSpeed] Submitting request to {url}")
        response = requests.post(url, headers=self._get_headers(), json=payload, timeout=timeout)
        if response.status_code != 200:
            logger.error(f"[WaveSpeed] Submission failed: {response.status_code} {response.text}")
            raise HTTPException(
                status_code=502,
                detail={
                    "error": "WaveSpeed image-to-video submission failed",
                    "status_code": response.status_code,
                    "response": response.text,
                },
            )

        data = response.json().get("data")
        if not data or "id" not in data:
            logger.error(f"[WaveSpeed] Unexpected submission response: {response.text}")
            raise HTTPException(
                status_code=502,
                detail={"error": "WaveSpeed response missing prediction id"},
            )

        prediction_id = data["id"]
        logger.info(f"[WaveSpeed] Submitted request: {prediction_id}")
        return prediction_id
    
    def submit_text_to_video(
        self,
        model_path: str,
        payload: Dict[str, Any],
        timeout: int = 60,
    ) -> str:
        """
        Submit a text-to-video generation request to WaveSpeed.
        
        Args:
            model_path: Model path (e.g., "alibaba/wan-2.5/text-to-video")
            payload: Request payload with prompt, resolution, duration, optional audio
            timeout: Request timeout in seconds
            
        Returns:
            Prediction ID for polling
        """
        url = f"{self.base_url}/{model_path}"
        logger.info(f"[WaveSpeed] Submitting text-to-video request to {url}")
        response = requests.post(url, headers=self._get_headers(), json=payload, timeout=timeout)
        
        if response.status_code != 200:
            logger.error(f"[WaveSpeed] Text-to-video submission failed: {response.status_code} {response.text}")
            raise HTTPException(
                status_code=502,
                detail={
                    "error": "WaveSpeed text-to-video submission failed",
                    "status_code": response.status_code,
                    "response": response.text,
                },
            )
        
        data = response.json().get("data")
        if not data or "id" not in data:
            logger.error(f"[WaveSpeed] Unexpected text-to-video response: {response.text}")
            raise HTTPException(
                status_code=502,
                detail={"error": "WaveSpeed response missing prediction id"},
            )
        
        prediction_id = data["id"]
        logger.info(f"[WaveSpeed] Submitted text-to-video request: {prediction_id}")
        return prediction_id
    
    def generate_text_video(
        self,
        prompt: str,
        resolution: str = "720p",  # 480p, 720p, 1080p
        duration: int = 5,  # 5 or 10 seconds
        audio_base64: Optional[str] = None,  # Optional audio for lip-sync
        negative_prompt: Optional[str] = None,
        seed: Optional[int] = None,
        enable_prompt_expansion: bool = True,
        enable_sync_mode: bool = False,
        timeout: int = 180,
    ) -> Dict[str, Any]:
        """
        Generate video from text prompt using WAN 2.5 text-to-video.
        
        Args:
            prompt: Text prompt describing the video
            resolution: Output resolution (480p, 720p, 1080p)
            duration: Video duration in seconds (5 or 10)
            audio_base64: Optional audio file (wav/mp3, 3-30s, ≤15MB) for lip-sync
            negative_prompt: Optional negative prompt
            seed: Optional random seed for reproducibility
            enable_prompt_expansion: Enable prompt optimizer
            enable_sync_mode: If True, wait for result and return it directly
            timeout: Request timeout in seconds
            
        Returns:
            Dictionary with video bytes, metadata, and cost
        """
        model_path = "alibaba/wan-2.5/text-to-video"
        
        # Validate resolution
        valid_resolutions = ["480p", "720p", "1080p"]
        if resolution not in valid_resolutions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid resolution: {resolution}. Must be one of: {valid_resolutions}"
            )
        
        # Validate duration
        if duration not in [5, 10]:
            raise HTTPException(
                status_code=400,
                detail="Duration must be 5 or 10 seconds"
            )
        
        # Build payload
        payload = {
            "prompt": prompt,
            "resolution": resolution,
            "duration": duration,
            "enable_prompt_expansion": enable_prompt_expansion,
            "enable_sync_mode": enable_sync_mode,
        }
        
        # Add optional audio
        if audio_base64:
            payload["audio"] = audio_base64
        
        # Add optional parameters
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        if seed is not None:
            payload["seed"] = seed
        
        # Submit request
        logger.info(
            f"[WaveSpeed] Generating text-to-video: resolution={resolution}, "
            f"duration={duration}s, prompt_length={len(prompt)}, sync_mode={enable_sync_mode}"
        )
        
        # For sync mode, submit and get result directly
        if enable_sync_mode:
            url = f"{self.base_url}/{model_path}"
            response = requests.post(url, headers=self._get_headers(), json=payload, timeout=timeout)
            
            if response.status_code != 200:
                logger.error(f"[WaveSpeed] Text-to-video submission failed: {response.status_code} {response.text}")
                raise HTTPException(
                    status_code=502,
                    detail={
                        "error": "WaveSpeed text-to-video submission failed",
                        "status_code": response.status_code,
                        "response": response.text[:500],
                    },
                )
            
            response_json = response.json()
            data = response_json.get("data") or response_json
            
            # Check status - if "created" or "processing", we need to poll even in sync mode
            status = data.get("status", "").lower()
            outputs = data.get("outputs") or []
            prediction_id = data.get("id")
            
            logger.debug(
                f"[WaveSpeed] Sync mode response: status='{status}', outputs_count={len(outputs)}, "
                f"prediction_id={prediction_id}"
            )
            
            # Handle sync mode - result should be directly in outputs
            if status == "completed" and outputs:
                # Sync mode returned completed result - use it directly
                logger.info(f"[WaveSpeed] Got immediate video results from sync mode (status: {status})")
                video_url = outputs[0]
                if not isinstance(video_url, str) or not video_url.startswith("http"):
                    logger.error(f"[WaveSpeed] Invalid video URL format in sync mode: {video_url}")
                    raise HTTPException(
                        status_code=502,
                        detail=f"Invalid video URL format: {video_url}",
                    )
                
                video_bytes = self._download_video(video_url)
                metadata = data.get("metadata") or {}
            else:
                # Sync mode returned "created", "processing", or incomplete status - need to poll
                if not prediction_id:
                    logger.error(
                        f"[WaveSpeed] Sync mode returned status '{status}' but no prediction ID. "
                        f"Response: {response.text[:500]}"
                    )
                    raise HTTPException(
                        status_code=502,
                        detail="WaveSpeed text-to-video sync mode returned async response without prediction ID",
                    )
                
                logger.info(
                    f"[WaveSpeed] Sync mode returned status '{status}' with {len(outputs)} output(s). "
                    f"Falling back to polling (prediction_id: {prediction_id})"
                )
                
                # Poll for completion
                try:
                    result = self.polling.poll_until_complete(
                        prediction_id,
                        timeout_seconds=timeout,
                        interval_seconds=2.0,
                    )
                except HTTPException as e:
                    detail = e.detail or {}
                    if isinstance(detail, dict):
                        detail.setdefault("prediction_id", prediction_id)
                        detail.setdefault("resume_available", True)
                    raise HTTPException(status_code=e.status_code, detail=detail)
                
                outputs = result.get("outputs") or []
                if not outputs:
                    logger.error(f"[WaveSpeed] Polling completed but no outputs: {result}")
                    raise HTTPException(
                        status_code=502,
                        detail="WaveSpeed text-to-video completed but returned no outputs",
                    )
                
                video_url = outputs[0]
                if not isinstance(video_url, str) or not video_url.startswith("http"):
                    logger.error(f"[WaveSpeed] Invalid video URL format after polling: {video_url}")
                    raise HTTPException(
                        status_code=502,
                        detail=f"Invalid video URL format: {video_url}",
                    )
                
                video_bytes = self._download_video(video_url)
                metadata = result.get("metadata") or {}
        else:
            # Async mode - submit and poll
            prediction_id = self.submit_text_to_video(model_path, payload, timeout=timeout)
            
            # Poll for completion
            try:
                result = self.polling.poll_until_complete(
                    prediction_id,
                    timeout_seconds=timeout,
                    interval_seconds=2.0
                )
            except HTTPException as e:
                detail = e.detail or {}
                if isinstance(detail, dict):
                    detail.setdefault("prediction_id", prediction_id)
                    detail.setdefault("resume_available", True)
                raise HTTPException(status_code=e.status_code, detail=detail)
            
            # Extract video URL
            outputs = result.get("outputs") or []
            if not outputs:
                raise HTTPException(
                    status_code=502,
                    detail="WAN 2.5 text-to-video completed but returned no outputs"
                )
            
            video_url = outputs[0]
            if not isinstance(video_url, str) or not video_url.startswith("http"):
                raise HTTPException(
                    status_code=502,
                    detail=f"Invalid video URL format: {video_url}"
                )
            
            video_bytes = self._download_video(video_url)
            metadata = result.get("metadata") or {}
            # prediction_id is already set from earlier in the function
        
        # Calculate cost (same pricing as image-to-video)
        pricing = {
            "480p": 0.05,
            "720p": 0.10,
            "1080p": 0.15,
        }
        cost = pricing.get(resolution, 0.10) * duration
        
        # Get video dimensions
        resolution_dims = {
            "480p": (854, 480),
            "720p": (1280, 720),
            "1080p": (1920, 1080),
        }
        width, height = resolution_dims.get(resolution, (1280, 720))
        
        logger.info(
            f"[WaveSpeed] ✅ Generated text-to-video: {len(video_bytes)} bytes, "
            f"resolution={resolution}, duration={duration}s, cost=${cost:.2f}"
        )
        
        return {
            "video_bytes": video_bytes,
            "prompt": prompt,
            "duration": float(duration),
            "model_name": "alibaba/wan-2.5/text-to-video",
            "cost": cost,
            "provider": "wavespeed",
            "source_video_url": video_url,
            "prediction_id": prediction_id,
            "resolution": resolution,
            "width": width,
            "height": height,
            "metadata": metadata,
        }
