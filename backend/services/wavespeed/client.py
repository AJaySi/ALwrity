from __future__ import annotations

import json
import time
from typing import Any, Dict, Optional

import requests
from fastapi import HTTPException
from requests import exceptions as requests_exceptions

from services.onboarding.api_key_manager import APIKeyManager
from utils.logger_utils import get_service_logger

logger = get_service_logger("wavespeed.client")


class WaveSpeedClient:
    """
    Thin HTTP client for the WaveSpeed AI API.
    Handles authentication, submission, and polling helpers.
    """

    BASE_URL = "https://api.wavespeed.ai/api/v3"

    def __init__(self, api_key: Optional[str] = None):
        manager = APIKeyManager()
        self.api_key = api_key or manager.get_api_key("wavespeed")
        if not self.api_key:
            raise RuntimeError("WAVESPEED_API_KEY is not configured. Please add it to your environment.")

    def _headers(self) -> Dict[str, str]:
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
        url = f"{self.BASE_URL}/{model_path}"
        logger.info(f"[WaveSpeed] Submitting request to {url}")
        response = requests.post(url, headers=self._headers(), json=payload, timeout=timeout)
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

    def get_prediction_result(self, prediction_id: str, timeout: int = 120) -> Dict[str, Any]:
        """
        Fetch the current status/result for a prediction.
        """
        url = f"{self.BASE_URL}/predictions/{prediction_id}/result"
        try:
            response = requests.get(url, headers={"Authorization": f"Bearer {self.api_key}"}, timeout=timeout)
        except requests_exceptions.Timeout as exc:
            raise HTTPException(
                status_code=504,
                detail={
                    "error": "WaveSpeed polling request timed out",
                    "prediction_id": prediction_id,
                    "resume_available": True,
                    "exception": str(exc),
                },
            ) from exc
        except requests_exceptions.RequestException as exc:
            raise HTTPException(
                status_code=502,
                detail={
                    "error": "WaveSpeed polling request failed",
                    "prediction_id": prediction_id,
                    "resume_available": True,
                    "exception": str(exc),
                },
            ) from exc
        if response.status_code != 200:
            logger.error(f"[WaveSpeed] Polling failed: {response.status_code} {response.text}")
            raise HTTPException(
                status_code=502,
                detail={
                    "error": "WaveSpeed prediction polling failed",
                    "status_code": response.status_code,
                    "response": response.text,
                },
            )

        result = response.json().get("data")
        if not result:
            raise HTTPException(status_code=502, detail={"error": "WaveSpeed polling response missing data"})
        return result

    def poll_until_complete(
        self,
        prediction_id: str,
        timeout_seconds: int = 240,
        interval_seconds: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Poll WaveSpeed until the job completes, fails, or times out.
        """
        start_time = time.time()
        while True:
            try:
                result = self.get_prediction_result(prediction_id)
            except HTTPException as exc:
                detail = exc.detail or {}
                if isinstance(detail, dict):
                    detail.setdefault("prediction_id", prediction_id)
                    detail.setdefault("resume_available", True)
                    detail.setdefault("error", detail.get("error", "WaveSpeed polling failed"))
                raise HTTPException(status_code=exc.status_code, detail=detail) from exc
            status = result.get("status")
            if status == "completed":
                logger.info(f"[WaveSpeed] Prediction {prediction_id} completed.")
                return result
            if status == "failed":
                logger.error(f"[WaveSpeed] Prediction {prediction_id} failed: {result.get('error')}")
                raise HTTPException(
                    status_code=502,
                    detail={
                        "error": "WaveSpeed animation failed",
                        "prediction_id": prediction_id,
                        "details": result.get("error"),
                    },
                )

            elapsed = time.time() - start_time
            if elapsed > timeout_seconds:
                logger.error(f"[WaveSpeed] Prediction {prediction_id} timed out after {timeout_seconds}s")
                raise HTTPException(
                    status_code=504,
                    detail={
                        "error": "WaveSpeed animation timed out",
                        "prediction_id": prediction_id,
                        "details": result,
                    },
                )

            logger.debug(f"[WaveSpeed] Prediction {prediction_id} status={status}. Waiting...")
            time.sleep(interval_seconds)

    def optimize_prompt(
        self,
        text: str,
        mode: str = "image",
        style: str = "default",
        image: Optional[str] = None,
        enable_sync_mode: bool = True,
        timeout: int = 30,
    ) -> str:
        """
        Optimize a prompt using WaveSpeed prompt optimizer.
        
        Args:
            text: The prompt text to optimize
            mode: "image" or "video" (default: "image")
            style: "default", "artistic", "photographic", "technical", "anime", "realistic" (default: "default")
            image: Base64-encoded image for context (optional)
            enable_sync_mode: If True, wait for result and return it directly (default: True)
            timeout: Request timeout in seconds (default: 30)
            
        Returns:
            Optimized prompt text
        """
        model_path = "wavespeed-ai/prompt-optimizer"
        url = f"{self.BASE_URL}/{model_path}"
        
        payload = {
            "text": text,
            "mode": mode,
            "style": style,
            "enable_sync_mode": enable_sync_mode,
        }
        
        if image:
            payload["image"] = image
        
        logger.info(f"[WaveSpeed] Optimizing prompt via {url} (mode={mode}, style={style})")
        response = requests.post(url, headers=self._headers(), json=payload, timeout=timeout)
        
        if response.status_code != 200:
            logger.error(f"[WaveSpeed] Prompt optimization failed: {response.status_code} {response.text}")
            raise HTTPException(
                status_code=502,
                detail={
                    "error": "WaveSpeed prompt optimization failed",
                    "status_code": response.status_code,
                    "response": response.text,
                },
            )
        
        response_json = response.json()
        data = response_json.get("data") or response_json
        
        # Handle sync mode - result should be directly in outputs
        if enable_sync_mode:
            outputs = data.get("outputs") or []
            if not outputs:
                logger.error(f"[WaveSpeed] No outputs in sync mode response: {response.text}")
                raise HTTPException(
                    status_code=502,
                    detail="WaveSpeed prompt optimizer returned no outputs",
                )
            
            # Extract optimized prompt from outputs
            # In sync mode, outputs[0] should be the optimized text directly (or a URL to fetch)
            optimized_prompt = None
            if isinstance(outputs, list) and len(outputs) > 0:
                first_output = outputs[0]
                
                # If it's a string that looks like a URL, fetch it
                if isinstance(first_output, str):
                    if first_output.startswith("http://") or first_output.startswith("https://"):
                        logger.info(f"[WaveSpeed] Fetching optimized prompt from URL: {first_output}")
                        url_response = requests.get(first_output, timeout=timeout)
                        if url_response.status_code == 200:
                            optimized_prompt = url_response.text.strip()
                        else:
                            logger.error(f"[WaveSpeed] Failed to fetch prompt from URL: {url_response.status_code}")
                            raise HTTPException(
                                status_code=502,
                                detail="Failed to fetch optimized prompt from WaveSpeed URL",
                            )
                    else:
                        # It's already the text
                        optimized_prompt = first_output
                elif isinstance(first_output, dict):
                    optimized_prompt = first_output.get("text") or first_output.get("prompt") or first_output.get("output")
            
            if not optimized_prompt:
                logger.error(f"[WaveSpeed] Could not extract optimized prompt from outputs: {outputs}")
                raise HTTPException(
                    status_code=502,
                    detail="WaveSpeed prompt optimizer output format not recognized",
                )
            
            logger.info(f"[WaveSpeed] Prompt optimized successfully (length: {len(optimized_prompt)} chars)")
            return optimized_prompt
        
        # Async mode - return prediction ID for polling
        prediction_id = data.get("id")
        if not prediction_id:
            logger.error(f"[WaveSpeed] No prediction ID in async response: {response.text}")
            raise HTTPException(
                status_code=502,
                detail="WaveSpeed response missing prediction id for async mode",
            )
        
        # Poll for result
        result = self.poll_until_complete(prediction_id, timeout_seconds=60, interval_seconds=0.5)
        outputs = result.get("outputs") or []
        
        if not outputs:
            raise HTTPException(status_code=502, detail="WaveSpeed prompt optimizer returned no outputs")
        
        # Extract optimized prompt from outputs
        # In async mode, outputs[0] is typically a URL that needs to be fetched
        optimized_prompt = None
        if isinstance(outputs, list) and len(outputs) > 0:
            first_output = outputs[0]
            
            # In async mode, it's usually a URL to fetch
            if isinstance(first_output, str):
                if first_output.startswith("http://") or first_output.startswith("https://"):
                    logger.info(f"[WaveSpeed] Fetching optimized prompt from URL: {first_output}")
                    url_response = requests.get(first_output, timeout=timeout)
                    if url_response.status_code == 200:
                        optimized_prompt = url_response.text.strip()
                    else:
                        logger.error(f"[WaveSpeed] Failed to fetch prompt from URL: {url_response.status_code}")
                        raise HTTPException(
                            status_code=502,
                            detail="Failed to fetch optimized prompt from WaveSpeed URL",
                        )
                else:
                    # If it's already text (shouldn't happen in async mode, but handle it)
                    optimized_prompt = first_output
            elif isinstance(first_output, dict):
                optimized_prompt = first_output.get("text") or first_output.get("prompt") or first_output.get("output")
        
        if not optimized_prompt:
            raise HTTPException(
                status_code=502,
                detail="WaveSpeed prompt optimizer output format not recognized",
            )
        
        logger.info(f"[WaveSpeed] Prompt optimized successfully (length: {len(optimized_prompt)} chars)")
        return optimized_prompt
    
    def generate_image(
        self,
        model: str,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        num_inference_steps: Optional[int] = None,
        guidance_scale: Optional[float] = None,
        negative_prompt: Optional[str] = None,
        seed: Optional[int] = None,
        enable_sync_mode: bool = True,
        timeout: int = 120,
        **kwargs
    ) -> bytes:
        """
        Generate image using WaveSpeed AI models (Ideogram V3 or Qwen Image).
        
        Args:
            model: Model to use ("ideogram-v3-turbo" or "qwen-image")
            prompt: Text prompt for image generation
            width: Image width (default: 1024)
            height: Image height (default: 1024)
            num_inference_steps: Number of inference steps
            guidance_scale: Guidance scale for generation
            negative_prompt: Negative prompt (what to avoid)
            seed: Random seed for reproducibility
            enable_sync_mode: If True, wait for result and return it directly (default: True)
            timeout: Request timeout in seconds (default: 120)
            **kwargs: Additional parameters
            
        Returns:
            bytes: Generated image bytes
        """
        # Map model names to WaveSpeed API paths
        model_paths = {
            "ideogram-v3-turbo": "ideogram-ai/ideogram-v3-turbo",
            "qwen-image": "wavespeed-ai/qwen-image/text-to-image",
        }
        
        model_path = model_paths.get(model)
        if not model_path:
            raise ValueError(f"Unsupported image model: {model}. Supported: {list(model_paths.keys())}")
        
        url = f"{self.BASE_URL}/{model_path}"
        
        payload = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "enable_sync_mode": enable_sync_mode,
        }
        
        # Add optional parameters
        if num_inference_steps is not None:
            payload["num_inference_steps"] = num_inference_steps
        if guidance_scale is not None:
            payload["guidance_scale"] = guidance_scale
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        if seed is not None:
            payload["seed"] = seed
        
        # Add any extra parameters
        for key, value in kwargs.items():
            if key not in payload:
                payload[key] = value
        
        logger.info(f"[WaveSpeed] Generating image via {url} (model={model}, prompt_length={len(prompt)})")
        response = requests.post(url, headers=self._headers(), json=payload, timeout=timeout)
        
        if response.status_code != 200:
            logger.error(f"[WaveSpeed] Image generation failed: {response.status_code} {response.text}")
            raise HTTPException(
                status_code=502,
                detail={
                    "error": "WaveSpeed image generation failed",
                    "status_code": response.status_code,
                    "response": response.text,
                },
            )
        
        response_json = response.json()
        data = response_json.get("data") or response_json
        
        # Handle sync mode - result should be directly in outputs
        if enable_sync_mode:
            outputs = data.get("outputs") or []
            if not outputs:
                logger.error(f"[WaveSpeed] No outputs in sync mode response: {response.text}")
                raise HTTPException(
                    status_code=502,
                    detail="WaveSpeed image generator returned no outputs",
                )
            
            # Extract image URL from outputs
            image_url = None
            if isinstance(outputs, list) and len(outputs) > 0:
                first_output = outputs[0]
                if isinstance(first_output, str):
                    image_url = first_output
                elif isinstance(first_output, dict):
                    image_url = first_output.get("url") or first_output.get("output")
            
            if not image_url or not (image_url.startswith("http://") or image_url.startswith("https://")):
                logger.error(f"[WaveSpeed] Invalid image URL in outputs: {outputs}")
                raise HTTPException(
                    status_code=502,
                    detail="WaveSpeed image generator output format not recognized",
                )
            
            # Fetch image bytes from URL
            logger.info(f"[WaveSpeed] Fetching image from URL: {image_url}")
            image_response = requests.get(image_url, timeout=timeout)
            if image_response.status_code == 200:
                image_bytes = image_response.content
                logger.info(f"[WaveSpeed] Image generated successfully (size: {len(image_bytes)} bytes)")
                return image_bytes
            else:
                logger.error(f"[WaveSpeed] Failed to fetch image from URL: {image_response.status_code}")
                raise HTTPException(
                    status_code=502,
                    detail="Failed to fetch generated image from WaveSpeed URL",
                )
        
        # Async mode - poll for result
        prediction_id = data.get("id")
        if not prediction_id:
            logger.error(f"[WaveSpeed] No prediction ID in async response: {response.text}")
            raise HTTPException(
                status_code=502,
                detail="WaveSpeed response missing prediction id for async mode",
            )
        
        # Poll for result
        result = self.poll_until_complete(prediction_id, timeout_seconds=240, interval_seconds=1.0)
        outputs = result.get("outputs") or []
        
        if not outputs:
            raise HTTPException(status_code=502, detail="WaveSpeed image generator returned no outputs")
        
        # Extract image URL and fetch
        image_url = None
        if isinstance(outputs, list) and len(outputs) > 0:
            first_output = outputs[0]
            if isinstance(first_output, str):
                image_url = first_output
            elif isinstance(first_output, dict):
                image_url = first_output.get("url") or first_output.get("output")
        
        if not image_url or not (image_url.startswith("http://") or image_url.startswith("https://")):
            raise HTTPException(
                status_code=502,
                detail="WaveSpeed image generator output format not recognized",
            )
        
        # Fetch image bytes
        logger.info(f"[WaveSpeed] Fetching image from URL: {image_url}")
        image_response = requests.get(image_url, timeout=timeout)
        if image_response.status_code == 200:
            image_bytes = image_response.content
            logger.info(f"[WaveSpeed] Image generated successfully (size: {len(image_bytes)} bytes)")
            return image_bytes
        else:
            logger.error(f"[WaveSpeed] Failed to fetch image from URL: {image_response.status_code}")
            raise HTTPException(
                status_code=502,
                detail="Failed to fetch generated image from WaveSpeed URL",
            )
    
    def generate_speech(
        self,
        text: str,
        voice_id: str,
        speed: float = 1.0,
        volume: float = 1.0,
        pitch: float = 0.0,
        emotion: str = "happy",
        enable_sync_mode: bool = True,
        timeout: int = 60,
        **kwargs
    ) -> bytes:
        """
        Generate speech audio using Minimax Speech 02 HD via WaveSpeed.
        
        Args:
            text: Text to convert to speech (max 10000 characters)
            voice_id: Voice ID (e.g., "Wise_Woman", "Friendly_Person", etc.)
            speed: Speech speed (0.5-2.0, default: 1.0)
            volume: Speech volume (0.1-10.0, default: 1.0)
            pitch: Speech pitch (-12 to 12, default: 0.0)
            emotion: Emotion ("happy", "sad", "angry", etc., default: "happy")
            enable_sync_mode: If True, wait for result and return it directly (default: True)
            timeout: Request timeout in seconds (default: 60)
            **kwargs: Additional parameters (sample_rate, bitrate, format, etc.)
            
        Returns:
            bytes: Generated audio bytes
        """
        model_path = "minimax/speech-02-hd"
        url = f"{self.BASE_URL}/{model_path}"
        
        payload = {
            "text": text,
            "voice_id": voice_id,
            "speed": speed,
            "volume": volume,
            "pitch": pitch,
            "emotion": emotion,
            "enable_sync_mode": enable_sync_mode,
        }
        
        # Add optional parameters
        optional_params = [
            "english_normalization",
            "sample_rate",
            "bitrate",
            "channel",
            "format",
            "language_boost",
        ]
        for param in optional_params:
            if param in kwargs:
                payload[param] = kwargs[param]
        
        logger.info(f"[WaveSpeed] Generating speech via {url} (voice={voice_id}, text_length={len(text)})")
        response = requests.post(url, headers=self._headers(), json=payload, timeout=timeout)
        
        if response.status_code != 200:
            logger.error(f"[WaveSpeed] Speech generation failed: {response.status_code} {response.text}")
            raise HTTPException(
                status_code=502,
                detail={
                    "error": "WaveSpeed speech generation failed",
                    "status_code": response.status_code,
                    "response": response.text,
                },
            )
        
        response_json = response.json()
        data = response_json.get("data") or response_json
        
        # Handle sync mode - result should be directly in outputs
        if enable_sync_mode:
            outputs = data.get("outputs") or []
            if not outputs:
                logger.error(f"[WaveSpeed] No outputs in sync mode response: {response.text}")
                raise HTTPException(
                    status_code=502,
                    detail="WaveSpeed speech generator returned no outputs",
                )
            
            # Extract audio URL from outputs
            audio_url = None
            if isinstance(outputs, list) and len(outputs) > 0:
                first_output = outputs[0]
                if isinstance(first_output, str):
                    audio_url = first_output
                elif isinstance(first_output, dict):
                    audio_url = first_output.get("url") or first_output.get("output")
            
            if not audio_url or not (audio_url.startswith("http://") or audio_url.startswith("https://")):
                logger.error(f"[WaveSpeed] Invalid audio URL in outputs: {outputs}")
                raise HTTPException(
                    status_code=502,
                    detail="WaveSpeed speech generator output format not recognized",
                )
            
            # Fetch audio bytes from URL
            logger.info(f"[WaveSpeed] Fetching audio from URL: {audio_url}")
            audio_response = requests.get(audio_url, timeout=timeout)
            if audio_response.status_code == 200:
                audio_bytes = audio_response.content
                logger.info(f"[WaveSpeed] Speech generated successfully (size: {len(audio_bytes)} bytes)")
                return audio_bytes
            else:
                logger.error(f"[WaveSpeed] Failed to fetch audio from URL: {audio_response.status_code}")
                raise HTTPException(
                    status_code=502,
                    detail="Failed to fetch generated audio from WaveSpeed URL",
                )
        
        # Async mode - return prediction ID for polling
        prediction_id = data.get("id")
        if not prediction_id:
            logger.error(f"[WaveSpeed] No prediction ID in async response: {response.text}")
            raise HTTPException(
                status_code=502,
                detail="WaveSpeed response missing prediction id for async mode",
            )
        
        # Poll for result
        result = self.poll_until_complete(prediction_id, timeout_seconds=120, interval_seconds=0.5)
        outputs = result.get("outputs") or []
        
        if not outputs:
            raise HTTPException(status_code=502, detail="WaveSpeed speech generator returned no outputs")
        
        # Extract audio URL and fetch
        audio_url = None
        if isinstance(outputs, list) and len(outputs) > 0:
            first_output = outputs[0]
            if isinstance(first_output, str):
                audio_url = first_output
            elif isinstance(first_output, dict):
                audio_url = first_output.get("url") or first_output.get("output")
        
        if not audio_url or not (audio_url.startswith("http://") or audio_url.startswith("https://")):
            raise HTTPException(
                status_code=502,
                detail="WaveSpeed speech generator output format not recognized",
            )
        
        # Fetch audio bytes
        logger.info(f"[WaveSpeed] Fetching audio from URL: {audio_url}")
        audio_response = requests.get(audio_url, timeout=timeout)
        if audio_response.status_code == 200:
            audio_bytes = audio_response.content
            logger.info(f"[WaveSpeed] Speech generated successfully (size: {len(audio_bytes)} bytes)")
            return audio_bytes
        else:
            logger.error(f"[WaveSpeed] Failed to fetch audio from URL: {audio_response.status_code}")
            raise HTTPException(
                status_code=502,
                detail="Failed to fetch generated audio from WaveSpeed URL",
            )
    
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
        url = f"{self.BASE_URL}/{model_path}"
        logger.info(f"[WaveSpeed] Submitting text-to-video request to {url}")
        response = requests.post(url, headers=self._headers(), json=payload, timeout=timeout)
        
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
            "enable_sync_mode": enable_sync_mode,  # Add sync mode to payload
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
            url = f"{self.BASE_URL}/{model_path}"
            response = requests.post(url, headers=self._headers(), json=payload, timeout=timeout)
            
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
            
            # In sync mode, result should be directly in outputs
            outputs = data.get("outputs") or []
            if not outputs:
                logger.error(f"[WaveSpeed] No outputs in sync mode response: {response.text[:500]}")
                raise HTTPException(
                    status_code=502,
                    detail="WaveSpeed text-to-video returned no outputs in sync mode",
                )
            
            # Extract video URL from outputs
            video_url = outputs[0]
            if not isinstance(video_url, str) or not video_url.startswith("http"):
                logger.error(f"[WaveSpeed] Invalid video URL format in sync mode: {video_url}")
                raise HTTPException(
                    status_code=502,
                    detail=f"Invalid video URL format: {video_url}",
                )
            
            # Download video
            logger.info(f"[WaveSpeed] Downloading video from sync mode URL: {video_url}")
            video_response = requests.get(video_url, timeout=180)
            
            if video_response.status_code != 200:
                raise HTTPException(
                    status_code=502,
                    detail={
                        "error": "Failed to download WAN 2.5 video from sync mode",
                        "status_code": video_response.status_code,
                        "response": video_response.text[:200],
                    }
                )
            
            video_bytes = video_response.content
            prediction_id = data.get("id", "sync_mode")
            metadata = data.get("metadata") or {}
            # video_url is already set above for sync mode
        else:
            # Async mode - submit and poll
            prediction_id = self.submit_text_to_video(model_path, payload, timeout=timeout)
            
            # Poll for completion
            try:
                result = self.poll_until_complete(
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
            
            # Download video
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
            
            video_bytes = video_response.content
            metadata = result.get("metadata") or {}
        
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

