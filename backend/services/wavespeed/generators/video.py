"""
Video generation generator for WaveSpeed API.
"""

import requests
from typing import Any, Dict, Optional, Callable
from fastapi import HTTPException

from utils.logger_utils import get_service_logger

logger = get_service_logger("wavespeed.generators.video")


class VideoGenerator:
    """Video generation generator."""
    
    def __init__(self, api_key: str, base_url: str, polling):
        """Initialize video generator.
        
        Args:
            api_key: WaveSpeed API key
            base_url: WaveSpeed API base URL
            polling: WaveSpeedPolling instance for async operations
        """
        self.api_key = api_key
        self.base_url = base_url
        self.polling = polling
    
    def _get_headers(self) -> dict:
        """Get HTTP headers for API requests."""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
    
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
                # prediction_id is already set from data.get("id") above (line 210)
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
    
    def _download_video(self, video_url: str) -> bytes:
        """Download video from URL."""
        logger.info(f"[WaveSpeed] Downloading video from: {video_url}")
        video_response = requests.get(video_url, timeout=180)
        
        if video_response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail={
                    "error": "Failed to download WAN 2.5 video",
                    "status_code": video_response.status_code,
                    "response": video_response.text[:200],
                }
            )
        
        return video_response.content
    
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