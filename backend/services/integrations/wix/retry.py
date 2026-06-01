"""
Retry utilities for Wix API calls with exponential backoff.

Production-grade retry logic that respects Wix rate limits and handles
transient failures gracefully.
"""

import time
import random
from typing import Callable, TypeVar, Optional
from loguru import logger

T = TypeVar('T')


class WixAPIError(Exception):
    """Custom exception for Wix API errors with status code context."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_body: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body
    
    def is_retryable(self) -> bool:
        """Determine if this error is retryable based on status code."""
        if self.status_code is None:
            return True  # Network errors are retryable
        # 429 = rate limit, 502/503/504 = gateway errors, 500 = internal server error (sometimes transient)
        return self.status_code in (429, 500, 502, 503, 504)
    
    def is_rate_limit(self) -> bool:
        """Check if this is a rate limit error."""
        return self.status_code == 429


def with_retry(
    fn: Callable[[], T],
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    retryable_exceptions: tuple = (Exception,),
    operation_name: str = "Wix API call"
) -> T:
    """
    Execute a function with exponential backoff retry logic.
    
    Args:
        fn: Function to execute (should make the API call)
        max_attempts: Maximum number of attempts (default: 3)
        base_delay: Initial delay in seconds (default: 1.0)
        max_delay: Maximum delay in seconds (default: 30.0)
        retryable_exceptions: Tuple of exception types to retry on
        operation_name: Name for logging
        
    Returns:
        Result of fn()
        
    Raises:
        WixAPIError: If all retries are exhausted
        Exception: If a non-retryable exception occurs
    """
    last_exception = None
    
    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except WixAPIError as e:
            last_exception = e
            if attempt >= max_attempts:
                break
            if not e.is_retryable():
                logger.warning(f"{operation_name}: non-retryable error (HTTP {e.status_code}), failing fast")
                raise
            
            # Calculate delay with exponential backoff and jitter
            delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
            # Add jitter (±25%) to prevent thundering herd
            jitter = delay * 0.25
            actual_delay = delay + random.uniform(-jitter, jitter)
            actual_delay = max(0.1, actual_delay)  # Minimum 100ms delay
            
            if e.is_rate_limit():
                # For rate limits, use a longer base delay
                actual_delay = max(actual_delay, 2.0)
                logger.warning(f"{operation_name}: rate limited (429), waiting {actual_delay:.1f}s before retry {attempt + 1}/{max_attempts}")
            else:
                logger.warning(f"{operation_name}: attempt {attempt}/{max_attempts} failed (HTTP {e.status_code}), waiting {actual_delay:.1f}s before retry")
            
            time.sleep(actual_delay)
            
        except retryable_exceptions as e:
            last_exception = e
            if attempt >= max_attempts:
                break
            
            delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
            jitter = delay * 0.25
            actual_delay = delay + random.uniform(-jitter, jitter)
            actual_delay = max(0.1, actual_delay)
            
            logger.warning(f"{operation_name}: attempt {attempt}/{max_attempts} failed ({type(e).__name__}), waiting {actual_delay:.1f}s before retry")
            time.sleep(actual_delay)
    
    # All retries exhausted
    if last_exception:
        if isinstance(last_exception, WixAPIError):
            raise last_exception
        raise WixAPIError(f"{operation_name}: failed after {max_attempts} attempts: {last_exception}")
    
    raise WixAPIError(f"{operation_name}: failed after {max_attempts} attempts")


def wix_api_call_with_retry(
    method: str,
    url: str,
    headers: dict,
    json_payload: Optional[dict] = None,
    max_attempts: int = 3
) -> dict:
    """
    Convenience wrapper for making Wix API calls with retry logic.
    
    Args:
        method: HTTP method ('GET', 'POST', etc.)
        url: Full API URL
        headers: Request headers
        json_payload: Optional JSON payload for POST/PUT
        max_attempts: Maximum retry attempts
        
    Returns:
        Parsed JSON response
        
    Raises:
        WixAPIError: On failure after retries
    """
    import requests
    
    def _call():
        if method.upper() == 'GET':
            resp = requests.get(url, headers=headers, timeout=30)
        elif method.upper() == 'POST':
            resp = requests.post(url, headers=headers, json=json_payload, timeout=30)
        elif method.upper() == 'PUT':
            resp = requests.put(url, headers=headers, json=json_payload, timeout=30)
        elif method.upper() == 'DELETE':
            resp = requests.delete(url, headers=headers, timeout=30)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        if resp.status_code >= 400:
            body = None
            try:
                body = resp.text[:500]
            except:
                body = str(resp.content)[:500]
            raise WixAPIError(
                f"Wix API {method} {url} failed: HTTP {resp.status_code}",
                status_code=resp.status_code,
                response_body=body
            )
        
        return resp.json()
    
    return with_retry(
        _call,
        max_attempts=max_attempts,
        operation_name=f"Wix {method} {url.split('/')[-1]}"
    )
