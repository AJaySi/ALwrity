"""
Speech generation generator for WaveSpeed API.
"""

import time
import base64
import requests
from typing import Optional
from requests import exceptions as requests_exceptions
from fastapi import HTTPException

from utils.logger_utils import get_service_logger

logger = get_service_logger("wavespeed.generators.speech")


class SpeechGenerator:
    """Speech generation generator."""
    
    def __init__(self, api_key: str, base_url: str, polling):
        """Initialize speech generator.
        
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
    
    def generate_speech(
        self,
        text: str,
        voice_id: str,
        speed: float = 1.0,
        volume: float = 1.0,
        pitch: float = 0.0,
        emotion: str = "happy",
        enable_sync_mode: bool = True,
        timeout: int = 120,
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
        url = f"{self.base_url}/{model_path}"
        
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

        # Retry on transient connection issues
        max_retries = 2
        retry_delay = 2.0
        for attempt in range(max_retries + 1):
            try:
                response = requests.post(
                    url,
                    headers=self._get_headers(),
                    json=payload,
                    timeout=(30, 60),  # connect, read
                )
                break
            except (requests_exceptions.ConnectTimeout, requests_exceptions.ConnectionError) as e:
                if attempt < max_retries:
                    logger.warning(
                        f"[WaveSpeed] Speech connection attempt {attempt + 1}/{max_retries + 1} failed, "
                        f"retrying in {retry_delay}s: {e}"
                    )
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                logger.error(f"[WaveSpeed] Speech connection failed after {max_retries + 1} attempts: {e}")
                raise HTTPException(
                    status_code=504,
                    detail={
                        "error": "Connection to WaveSpeed speech API timed out",
                        "message": "Unable to reach the speech service. Please try again.",
                        "exception": str(e),
                        "retry_recommended": True,
                    },
                )
            except requests_exceptions.Timeout as e:
                logger.error(f"[WaveSpeed] Speech request timeout: {e}")
                raise HTTPException(
                    status_code=504,
                    detail={
                        "error": "WaveSpeed speech request timed out",
                        "message": "The speech generation request took too long. Please try again.",
                        "exception": str(e),
                    },
                )
        
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
            
            audio_url = self._extract_audio_url(outputs)
            return self._download_audio(audio_url, timeout)
        
        # Async mode - return prediction ID for polling
        prediction_id = data.get("id")
        if not prediction_id:
            logger.error(f"[WaveSpeed] No prediction ID in async response: {response.text}")
            raise HTTPException(
                status_code=502,
                detail="WaveSpeed response missing prediction id for async mode",
            )
        
        # Poll for result
        result = self.polling.poll_until_complete(prediction_id, timeout_seconds=120, interval_seconds=0.5)
        outputs = result.get("outputs") or []
        
        if not outputs:
            raise HTTPException(status_code=502, detail="WaveSpeed speech generator returned no outputs")
        
        audio_url = self._extract_audio_url(outputs)
        return self._download_audio(audio_url, timeout)

    def voice_clone(
        self,
        audio_bytes: bytes,
        custom_voice_id: str,
        model: str = "speech-02-hd",
        *,
        audio_mime_type: str = "audio/wav",
        text: Optional[str] = None,
        need_noise_reduction: bool = False,
        need_volume_normalization: bool = False,
        accuracy: float = 0.7,
        language_boost: Optional[str] = None,
        timeout: int = 180,
    ) -> bytes:
        url = f"{self.base_url}/minimax/voice-clone"

        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        mime = audio_mime_type or "audio/wav"
        audio_data_url = f"data:{mime};base64,{audio_b64}"

        payload = {
            "audio": audio_data_url,
            "custom_voice_id": custom_voice_id,
            "model": model,
            "need_noise_reduction": need_noise_reduction,
            "need_volume_normalization": need_volume_normalization,
            "accuracy": accuracy,
        }
        if text:
            payload["text"] = text
        if language_boost:
            payload["language_boost"] = language_boost

        logger.info(f"[WaveSpeed] Voice clone via {url} (voice_id={custom_voice_id})")

        try:
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=payload,
                timeout=(30, 90),
            )
        except requests_exceptions.Timeout as e:
            raise HTTPException(status_code=504, detail={"error": "WaveSpeed voice clone timed out", "message": str(e)})
        except (requests_exceptions.ConnectionError, requests_exceptions.ConnectTimeout) as e:
            raise HTTPException(status_code=504, detail={"error": "WaveSpeed voice clone connection failed", "message": str(e)})

        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail={
                    "error": "WaveSpeed voice clone failed",
                    "status_code": response.status_code,
                    "response": response.text,
                },
            )

        response_json = response.json()
        data = response_json.get("data") or response_json

        outputs = data.get("outputs") or []
        status = data.get("status")
        prediction_id = data.get("id")

        if not outputs and prediction_id and status in {"created", "processing"}:
            result = self.polling.poll_until_complete(prediction_id, timeout_seconds=timeout, interval_seconds=0.8)
            outputs = result.get("outputs") or []

        if not outputs:
            raise HTTPException(status_code=502, detail="WaveSpeed voice clone returned no outputs")

        audio_url = self._extract_audio_url(outputs)
        return self._download_audio(audio_url, timeout)

    def qwen3_voice_clone(
        self,
        audio_bytes: bytes,
        text: str,
        *,
        audio_mime_type: str = "audio/wav",
        language: str = "auto",
        reference_text: Optional[str] = None,
        timeout: int = 180,
    ) -> bytes:
        url = f"{self.base_url}/wavespeed-ai/qwen3-tts/voice-clone"

        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        mime = audio_mime_type or "audio/wav"
        audio_data_url = f"data:{mime};base64,{audio_b64}"

        payload = {
            "audio": audio_data_url,
            "text": text,
            "language": language or "auto",
        }
        if reference_text:
            payload["reference_text"] = reference_text

        logger.info(f"[WaveSpeed] Qwen3 voice clone via {url} (language={payload.get('language')})")

        try:
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=payload,
                timeout=(30, 90),
            )
        except requests_exceptions.Timeout as e:
            raise HTTPException(status_code=504, detail={"error": "WaveSpeed Qwen3 voice clone timed out", "message": str(e)})
        except (requests_exceptions.ConnectionError, requests_exceptions.ConnectTimeout) as e:
            raise HTTPException(status_code=504, detail={"error": "WaveSpeed Qwen3 voice clone connection failed", "message": str(e)})

        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail={
                    "error": "WaveSpeed Qwen3 voice clone failed",
                    "status_code": response.status_code,
                    "response": response.text,
                },
            )

        response_json = response.json()
        data = response_json.get("data") or response_json

        outputs = data.get("outputs") or []
        status = data.get("status")
        prediction_id = data.get("id")

        if not outputs and prediction_id and status in {"created", "processing"}:
            result = self.polling.poll_until_complete(prediction_id, timeout_seconds=timeout, interval_seconds=0.8)
            outputs = result.get("outputs") or []

        if not outputs:
            raise HTTPException(status_code=502, detail="WaveSpeed Qwen3 voice clone returned no outputs")

        audio_url = self._extract_audio_url(outputs)
        return self._download_audio(audio_url, timeout)
    
    def _extract_audio_url(self, outputs: list) -> str:
        """Extract audio URL from outputs."""
        if not isinstance(outputs, list) or len(outputs) == 0:
            raise HTTPException(
                status_code=502,
                detail="WaveSpeed speech generator output format not recognized",
            )
        
        first_output = outputs[0]
        if isinstance(first_output, str):
            audio_url = first_output
        elif isinstance(first_output, dict):
            audio_url = first_output.get("url") or first_output.get("output")
        else:
            raise HTTPException(
                status_code=502,
                detail="WaveSpeed speech generator output format not recognized",
            )
        
        if not audio_url or not (audio_url.startswith("http://") or audio_url.startswith("https://")):
            raise HTTPException(
                status_code=502,
                detail="WaveSpeed speech generator output format not recognized",
            )
        
        return audio_url
    
    def _download_audio(self, audio_url: str, timeout: int) -> bytes:
        """Download audio from URL."""
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
