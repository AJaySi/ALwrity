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

