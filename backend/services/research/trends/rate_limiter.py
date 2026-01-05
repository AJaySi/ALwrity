"""
Rate Limiter for Google Trends API

Ensures we don't exceed Google Trends rate limits (1 request per second).
"""

import asyncio
from time import time
from collections import deque
from loguru import logger


class RateLimiter:
    """
    Simple rate limiter for Google Trends API.
    
    Limits requests to max_calls per period (in seconds).
    """
    
    def __init__(self, max_calls: int = 1, period: float = 1.0):
        """
        Initialize rate limiter.
        
        Args:
            max_calls: Maximum number of calls allowed
            period: Time period in seconds
        """
        self.max_calls = max_calls
        self.period = period
        self.calls = deque()
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """
        Acquire permission to make a request.
        
        Will wait if rate limit would be exceeded.
        """
        async with self._lock:
            now = time()
            
            # Remove old calls outside the period
            while self.calls and self.calls[0] < now - self.period:
                self.calls.popleft()
            
            # If at limit, wait until oldest call expires
            if len(self.calls) >= self.max_calls:
                sleep_time = self.period - (now - self.calls[0])
                if sleep_time > 0:
                    logger.debug(f"Rate limit reached, waiting {sleep_time:.2f}s")
                    await asyncio.sleep(sleep_time)
                    # Recursively try again after waiting
                    return await self.acquire()
            
            # Record this call
            self.calls.append(time())
            logger.debug(f"Rate limit check passed, {len(self.calls)}/{self.max_calls} calls in period")
