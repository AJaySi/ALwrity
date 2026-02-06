"""
Prompt optimization generator for WaveSpeed API.
"""

import requests
from typing import Optional
from fastapi import HTTPException

from utils.logging import get_service_logger

logger = get_service_logger("wavespeed.generators.prompt")


class PromptGenerator:
    """Prompt optimization generator."""
    
    def __init__(self, api_key: str, base_url: str, polling):
        """Initialize prompt generator.
        
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
        url = f"{self.base_url}/{model_path}"
        
        payload = {
            "text": text,
            "mode": mode,
            "style": style,
            "enable_sync_mode": enable_sync_mode,
        }
        
        if image:
            payload["image"] = image
        
        logger.info(f"[WaveSpeed] Optimizing prompt via {url} (mode={mode}, style={style})")
        response = requests.post(url, headers=self._get_headers(), json=payload, timeout=timeout)
        
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
            optimized_prompt = self._extract_prompt_from_outputs(outputs, timeout)
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
        result = self.polling.poll_until_complete(prediction_id, timeout_seconds=60, interval_seconds=0.5)
        outputs = result.get("outputs") or []
        
        if not outputs:
            raise HTTPException(status_code=502, detail="WaveSpeed prompt optimizer returned no outputs")
        
        # Extract optimized prompt from outputs
        optimized_prompt = self._extract_prompt_from_outputs(outputs, timeout)
        if not optimized_prompt:
            raise HTTPException(
                status_code=502,
                detail="WaveSpeed prompt optimizer output format not recognized",
            )
        
        logger.info(f"[WaveSpeed] Prompt optimized successfully (length: {len(optimized_prompt)} chars)")
        return optimized_prompt
    
    def _extract_prompt_from_outputs(self, outputs: list, timeout: int) -> Optional[str]:
        """Extract optimized prompt from outputs, handling URLs and direct text."""
        if not isinstance(outputs, list) or len(outputs) == 0:
            return None
        
        first_output = outputs[0]
        
        # If it's a string that looks like a URL, fetch it
        if isinstance(first_output, str):
            if first_output.startswith("http://") or first_output.startswith("https://"):
                logger.info(f"[WaveSpeed] Fetching optimized prompt from URL: {first_output}")
                url_response = requests.get(first_output, timeout=timeout)
                if url_response.status_code == 200:
                    return url_response.text.strip()
                else:
                    logger.error(f"[WaveSpeed] Failed to fetch prompt from URL: {url_response.status_code}")
                    raise HTTPException(
                        status_code=502,
                        detail="Failed to fetch optimized prompt from WaveSpeed URL",
                    )
            else:
                # It's already the text
                return first_output
        elif isinstance(first_output, dict):
            return first_output.get("text") or first_output.get("prompt") or first_output.get("output")
        
        return None
