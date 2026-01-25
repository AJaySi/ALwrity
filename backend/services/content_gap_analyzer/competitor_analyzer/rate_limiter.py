"""
Rate limiting utilities for competitor analysis API.
"""

import time
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
from enum import Enum
from loguru import logger


class RateLimitType(Enum):
    """Rate limiting strategies."""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"


@dataclass
class RateLimitRule:
    """Rate limiting rule configuration."""
    requests_per_window: int
    window_seconds: int
    limit_type: RateLimitType = RateLimitType.SLIDING_WINDOW
    burst_capacity: Optional[int] = None
    refill_rate: Optional[float] = None
    
    def __post_init__(self):
        if self.burst_capacity is None:
            self.burst_capacity = self.requests_per_window
        if self.refill_rate is None:
            self.refill_rate = self.requests_per_window / self.window_seconds


@dataclass
class RateLimitResult:
    """Rate limiting result."""
    allowed: bool
    remaining_requests: int
    reset_time: datetime
    retry_after: Optional[float] = None
    limit_exceeded: bool = False


class SlidingWindowLimiter:
    """Sliding window rate limiter."""
    
    def __init__(self, requests: int, window_seconds: int):
        self.requests = requests
        self.window_seconds = window_seconds
        self._requests: Dict[str, deque] = defaultdict(lambda: deque())
    
    def is_allowed(self, key: str) -> RateLimitResult:
        """Check if request is allowed."""
        now = time.time()
        window_start = now - self.window_seconds
        
        # Clean old requests
        requests = self._requests[key]
        while requests and requests[0] <= window_start:
            requests.popleft()
        
        # Check if under limit
        if len(requests) < self.requests:
            requests.append(now)
            return RateLimitResult(
                allowed=True,
                remaining_requests=self.requests - len(requests),
                reset_time=datetime.fromtimestamp(now + self.window_seconds)
            )
        
        # Calculate retry after
        oldest_request = requests[0]
        retry_after = oldest_request + self.window_seconds - now
        
        return RateLimitResult(
            allowed=False,
            remaining_requests=0,
            reset_time=datetime.fromtimestamp(oldest_request + self.window_seconds),
            retry_after=max(0, retry_after),
            limit_exceeded=True
        )


class TokenBucketLimiter:
    """Token bucket rate limiter."""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate  # tokens per second
        self._buckets: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'tokens': capacity,
            'last_refill': time.time()
        })
    
    def is_allowed(self, key: str) -> RateLimitResult:
        """Check if request is allowed."""
        now = time.time()
        bucket = self._buckets[key]
        
        # Refill tokens
        time_passed = now - bucket['last_refill']
        tokens_to_add = time_passed * self.refill_rate
        bucket['tokens'] = min(self.capacity, bucket['tokens'] + tokens_to_add)
        bucket['last_refill'] = now
        
        # Check if has tokens
        if bucket['tokens'] >= 1:
            bucket['tokens'] -= 1
            return RateLimitResult(
                allowed=True,
                remaining_requests=int(bucket['tokens']),
                reset_time=datetime.fromtimestamp(now + (1 / self.refill_rate))
            )
        
        # Calculate retry after
        retry_after = (1 - bucket['tokens']) / self.refill_rate
        
        return RateLimitResult(
            allowed=False,
            remaining_requests=0,
            reset_time=datetime.fromtimestamp(now + retry_after),
            retry_after=retry_after,
            limit_exceeded=True
        )


class RateLimiter:
    """
    Comprehensive rate limiting system.
    
    Features:
    - Multiple rate limiting strategies
    - Per-key rate limiting
    - Burst handling
    - Detailed rate limit information
    - Automatic cleanup
    """
    
    def __init__(self):
        self._limiters: Dict[str, Any] = {}
        self._rules: Dict[str, RateLimitRule] = {}
        self._stats = {
            'total_requests': 0,
            'allowed_requests': 0,
            'blocked_requests': 0,
            'rate_limit_exceeded': 0
        }
        
        logger.info("✅ RateLimiter initialized")
    
    def add_rule(self, 
                 key: str, 
                 requests_per_window: int, 
                 window_seconds: int,
                 limit_type: RateLimitType = RateLimitType.SLIDING_WINDOW) -> None:
        """
        Add a rate limiting rule.
        
        Args:
            key: Rule identifier (e.g., 'api_calls', 'analysis_requests')
            requests_per_window: Number of requests allowed
            window_seconds: Time window in seconds
            limit_type: Type of rate limiting
        """
        rule = RateLimitRule(
            requests_per_window=requests_per_window,
            window_seconds=window_seconds,
            limit_type=limit_type
        )
        
        self._rules[key] = rule
        
        # Create appropriate limiter
        if limit_type == RateLimitType.SLIDING_WINDOW:
            self._limiters[key] = SlidingWindowLimiter(requests_per_window, window_seconds)
        elif limit_type == RateLimitType.TOKEN_BUCKET:
            self._limiters[key] = TokenBucketLimiter(rule.burst_capacity, rule.refill_rate)
        else:
            # Default to sliding window
            self._limiters[key] = SlidingWindowLimiter(requests_per_window, window_seconds)
        
        logger.info(f"🚦 Added rate limit rule '{key}': {requests_per_window}/{window_seconds}s ({limit_type.value})")
    
    def is_allowed(self, 
                  key: str, 
                  identifier: str = "default") -> RateLimitResult:
        """
        Check if request is allowed.
        
        Args:
            key: Rule identifier
            identifier: Unique identifier (IP, user ID, API key, etc.)
            
        Returns:
            Rate limit result
        """
        self._stats['total_requests'] += 1
        
        if key not in self._limiters:
            logger.warning(f"Rate limit rule '{key}' not found, allowing request")
            self._stats['allowed_requests'] += 1
            return RateLimitResult(
                allowed=True,
                remaining_requests=999,
                reset_time=datetime.utcnow() + timedelta(hours=1)
            )
        
        limiter_key = f"{key}:{identifier}"
        result = self._limiters[key].is_allowed(limiter_key)
        
        if result.allowed:
            self._stats['allowed_requests'] += 1
        else:
            self._stats['blocked_requests'] += 1
            if result.limit_exceeded:
                self._stats['rate_limit_exceeded'] += 1
        
        return result
    
    def check_multiple(self, 
                      checks: List[tuple]) -> Dict[str, RateLimitResult]:
        """
        Check multiple rate limits.
        
        Args:
            checks: List of (key, identifier) tuples
            
        Returns:
            Dictionary of results
        """
        results = {}
        for key, identifier in checks:
            results[key] = self.is_allowed(key, identifier)
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiting statistics."""
        total = self._stats['total_requests']
        allowed_rate = (self._stats['allowed_requests'] / total * 100) if total > 0 else 0
        
        return {
            **self._stats,
            'allowed_rate_percent': round(allowed_rate, 2),
            'blocked_rate_percent': round(100 - allowed_rate, 2),
            'active_rules': len(self._rules),
            'rule_details': {
                key: {
                    'requests_per_window': rule.requests_per_window,
                    'window_seconds': rule.window_seconds,
                    'type': rule.limit_type.value
                }
                for key, rule in self._rules.items()
            }
        }
    
    def reset_stats(self) -> None:
        """Reset statistics."""
        self._stats = {
            'total_requests': 0,
            'allowed_requests': 0,
            'blocked_requests': 0,
            'rate_limit_exceeded': 0
        }
        logger.info("📊 Rate limiter stats reset")
    
    def cleanup_expired(self) -> int:
        """Clean up expired rate limit data."""
        # This would be implemented based on the specific limiter types
        # For now, return 0 as most limiters handle cleanup automatically
        return 0


# Global rate limiter instance
_rate_limiter = RateLimiter()

def get_rate_limiter() -> RateLimiter:
    """Get the global rate limiter instance."""
    return _rate_limiter

# Initialize default rate limits
def initialize_default_limits():
    """Initialize default rate limiting rules."""
    limiter = get_rate_limiter()
    
    # API calls per minute
    limiter.add_rule(
        key="api_calls",
        requests_per_window=60,
        window_seconds=60,
        limit_type=RateLimitType.SLIDING_WINDOW
    )
    
    # Analysis requests per hour
    limiter.add_rule(
        key="analysis_requests",
        requests_per_window=100,
        window_seconds=3600,
        limit_type=RateLimitType.SLIDING_WINDOW
    )
    
    # Concurrent analyses
    limiter.add_rule(
        key="concurrent_analyses",
        requests_per_window=5,
        window_seconds=60,
        limit_type=RateLimitType.TOKEN_BUCKET
    )
    
    # Heavy analysis requests per day
    limiter.add_rule(
        key="heavy_analysis",
        requests_per_window=20,
        window_seconds=86400,
        limit_type=RateLimitType.SLIDING_WINDOW
    )
    
    logger.info("🚦 Default rate limits initialized")

# Decorator for rate limiting
def rate_limit(key: str, identifier: str = "default"):
    """
    Decorator to apply rate limiting to functions.
    
    Args:
        key: Rate limit rule key
        identifier: Identifier for rate limiting (IP, user ID, etc.)
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            limiter = get_rate_limiter()
            result = limiter.is_allowed(key, identifier)
            
            if not result.allowed:
                logger.warning(f"🚫 Rate limit exceeded for {key}:{identifier}")
                raise RateLimitExceeded(
                    f"Rate limit exceeded for {key}",
                    retry_after=result.retry_after,
                    reset_time=result.reset_time
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(self, message: str, retry_after: Optional[float] = None, reset_time: Optional[datetime] = None):
        super().__init__(message)
        self.retry_after = retry_after
        self.reset_time = reset_time

# Utility functions
def get_client_identifier(request) -> str:
    """Extract client identifier from request."""
    # This would be implemented based on your web framework
    # For now, return a simple identifier
    return getattr(request, 'client_ip', 'unknown')

def create_rate_limit_response(result: RateLimitResult) -> Dict[str, Any]:
    """Create rate limit response for API."""
    return {
        'error': 'Rate limit exceeded',
        'message': 'Too many requests',
        'retry_after': result.retry_after,
        'reset_time': result.reset_time.isoformat(),
        'remaining_requests': result.remaining_requests
    }
