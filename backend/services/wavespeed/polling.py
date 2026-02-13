"""
Polling utilities for WaveSpeed API.
"""

import time
from typing import Any, Dict, Optional, Callable

import requests
from fastapi import HTTPException
from requests import exceptions as requests_exceptions

from utils.logging import get_service_logger

logger = get_service_logger("wavespeed.polling")


class WaveSpeedPolling:
    """Polling utilities for WaveSpeed API predictions."""
    
    def __init__(self, api_key: str, base_url: str):
        """Initialize polling utilities.
        
        Args:
            api_key: WaveSpeed API key
            base_url: WaveSpeed API base URL
        """
        self.api_key = api_key
        self.base_url = base_url
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests."""
        return {"Authorization": f"Bearer {self.api_key}"}
    
    def get_prediction_result(self, prediction_id: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Fetch the current status/result for a prediction.
        Matches the example pattern: simple GET request, check status_code == 200, return data.
        """
        url = f"{self.base_url}/predictions/{prediction_id}/result"
        headers = self._get_headers()
        
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
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
        
        # Match example pattern: check status_code == 200, then get data
        if response.status_code == 200:
            result = response.json().get("data")
            if not result:
                raise HTTPException(status_code=502, detail={"error": "WaveSpeed polling response missing data"})
            return result
        else:
            # Non-200 status - log and raise error (matching example's break behavior)
            logger.error(f"[WaveSpeed] Polling failed: {response.status_code} {response.text}")
            raise HTTPException(
                status_code=502,
                detail={
                    "error": "WaveSpeed prediction polling failed",
                    "status_code": response.status_code,
                    "response": response.text,
                },
            )
    
    def poll_until_complete(
        self,
        prediction_id: str,
        timeout_seconds: Optional[int] = None,
        interval_seconds: float = 1.0,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> Dict[str, Any]:
        """
        Poll WaveSpeed until the job completes or fails.
        Matches the example pattern: simple polling loop until status is "completed" or "failed".
        
        Args:
            prediction_id: The prediction ID to poll for
            timeout_seconds: Optional timeout in seconds. If None, polls indefinitely until completion/failure.
            interval_seconds: Seconds to wait between polling attempts (default: 1.0, faster than 2.0)
            progress_callback: Optional callback function(progress: float, message: str) for progress updates
        
        Returns:
            Dict containing the completed result
            
        Raises:
            HTTPException: If the task fails, polling fails, or times out (if timeout_seconds is set)
        """
        start_time = time.time()
        consecutive_errors = 0
        max_consecutive_errors = 6  # safety guard for non-transient errors
        
        while True:
            try:
                result = self.get_prediction_result(prediction_id)
                consecutive_errors = 0  # Reset error counter on success
            except HTTPException as exc:
                detail = exc.detail or {}
                if isinstance(detail, dict):
                    detail.setdefault("prediction_id", prediction_id)
                    detail.setdefault("resume_available", True)
                    detail.setdefault("error", detail.get("error", "WaveSpeed polling failed"))

                # Determine underlying status code (WaveSpeed vs proxy)
                status_code = detail.get("status_code", exc.status_code)

                # Treat 5xx as transient: keep polling indefinitely with backoff
                if 500 <= int(status_code) < 600:
                    consecutive_errors += 1
                    backoff = min(30.0, interval_seconds * (2 ** (consecutive_errors - 1)))
                    logger.warning(
                        f"[WaveSpeed] Transient polling error {consecutive_errors} for {prediction_id}: "
                        f"{status_code}. Backing off {backoff:.1f}s"
                    )
                    time.sleep(backoff)
                    continue

                # For non-transient (typically 4xx) errors, apply safety cap
                consecutive_errors += 1
                if consecutive_errors >= max_consecutive_errors:
                    logger.error(
                        f"[WaveSpeed] Too many polling errors ({consecutive_errors}) for {prediction_id}, "
                        f"status_code={status_code}. Giving up."
                    )
                raise HTTPException(status_code=exc.status_code, detail=detail) from exc

                backoff = min(30.0, interval_seconds * (2 ** (consecutive_errors - 1)))
                logger.warning(
                    f"[WaveSpeed] Polling error {consecutive_errors}/{max_consecutive_errors} for {prediction_id}: "
                    f"{status_code}. Backing off {backoff:.1f}s"
                )
                time.sleep(backoff)
                continue
            
            # Extract status from result (matching example pattern)
            status = result.get("status")
            
            if status == "completed":
                elapsed = time.time() - start_time
                logger.info(f"[WaveSpeed] Prediction {prediction_id} completed in {elapsed:.1f}s")
                return result
            
            if status == "failed":
                error_msg = result.get("error", "Unknown error")
                logger.error(f"[WaveSpeed] Prediction {prediction_id} failed: {error_msg}")
                raise HTTPException(
                    status_code=502,
                    detail={
                        "error": "WaveSpeed task failed",
                        "prediction_id": prediction_id,
                        "message": error_msg,
                        "details": result,
                    },
                )

            # Check timeout only if specified
            if timeout_seconds is not None:
                elapsed = time.time() - start_time
                if elapsed > timeout_seconds:
                    logger.error(f"[WaveSpeed] Prediction {prediction_id} timed out after {timeout_seconds}s")
                    raise HTTPException(
                        status_code=504,
                        detail={
                            "error": "WaveSpeed task timed out",
                            "prediction_id": prediction_id,
                            "timeout_seconds": timeout_seconds,
                            "current_status": status,
                            "message": f"Task did not complete within {timeout_seconds} seconds. Status: {status}",
                        },
                    )

            # Log progress periodically (every 30 seconds)
            elapsed = time.time() - start_time
            if int(elapsed) % 30 == 0 and elapsed > 0:
                logger.info(f"[WaveSpeed] Polling {prediction_id}: status={status}, elapsed={elapsed:.0f}s")
            
            # Call progress callback if provided
            if progress_callback:
                # Map elapsed time to progress (20-80% range during polling)
                # Assume typical completion time is timeout_seconds or 120s default
                estimated_total = timeout_seconds or 120
                progress = min(80.0, 20.0 + (elapsed / estimated_total) * 60.0)
                progress_callback(progress, f"Video generation in progress... ({elapsed:.0f}s)")
            
            # Poll faster (1.0s instead of 2.0s) to match example's responsiveness
            time.sleep(interval_seconds)
