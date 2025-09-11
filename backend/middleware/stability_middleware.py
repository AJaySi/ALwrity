"""Middleware for Stability AI operations."""

import time
import asyncio
import os
from typing import Dict, Any, Optional
from collections import defaultdict, deque
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import json
from loguru import logger
from datetime import datetime, timedelta


class RateLimitMiddleware:
    """Rate limiting middleware for Stability AI API calls."""
    
    def __init__(self, requests_per_window: int = 150, window_seconds: int = 10):
        """Initialize rate limiter.
        
        Args:
            requests_per_window: Maximum requests per time window
            window_seconds: Time window in seconds
        """
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self.request_times: Dict[str, deque] = defaultdict(lambda: deque())
        self.blocked_until: Dict[str, float] = {}
    
    async def __call__(self, request: Request, call_next):
        """Process request with rate limiting.
        
        Args:
            request: FastAPI request
            call_next: Next middleware/endpoint
            
        Returns:
            Response
        """
        # Skip rate limiting for non-Stability endpoints
        if not request.url.path.startswith("/api/stability"):
            return await call_next(request)
        
        # Get client identifier (IP address or API key)
        client_id = self._get_client_id(request)
        current_time = time.time()
        
        # Check if client is currently blocked
        if client_id in self.blocked_until:
            if current_time < self.blocked_until[client_id]:
                remaining = int(self.blocked_until[client_id] - current_time)
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "retry_after": remaining,
                        "message": f"You have been timed out for {remaining} seconds"
                    }
                )
            else:
                # Timeout expired, remove block
                del self.blocked_until[client_id]
        
        # Clean old requests outside the window
        request_times = self.request_times[client_id]
        while request_times and request_times[0] < current_time - self.window_seconds:
            request_times.popleft()
        
        # Check rate limit
        if len(request_times) >= self.requests_per_window:
            # Rate limit exceeded, block for 60 seconds
            self.blocked_until[client_id] = current_time + 60
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "retry_after": 60,
                    "message": "You have exceeded the rate limit of 150 requests within a 10 second period"
                }
            )
        
        # Add current request time
        request_times.append(current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_window)
        response.headers["X-RateLimit-Remaining"] = str(self.requests_per_window - len(request_times))
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.window_seconds))
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting.
        
        Args:
            request: FastAPI request
            
        Returns:
            Client identifier
        """
        # Try to get API key from authorization header
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header[7:15]  # Use first 8 chars of API key
        
        # Fall back to IP address
        return request.client.host if request.client else "unknown"


class MonitoringMiddleware:
    """Monitoring middleware for Stability AI operations."""
    
    def __init__(self):
        """Initialize monitoring middleware."""
        self.request_stats = defaultdict(lambda: {
            "count": 0,
            "total_time": 0,
            "errors": 0,
            "last_request": None
        })
        self.active_requests = {}
    
    async def __call__(self, request: Request, call_next):
        """Process request with monitoring.
        
        Args:
            request: FastAPI request
            call_next: Next middleware/endpoint
            
        Returns:
            Response
        """
        # Skip monitoring for non-Stability endpoints
        if not request.url.path.startswith("/api/stability"):
            return await call_next(request)
        
        start_time = time.time()
        request_id = f"{int(start_time * 1000)}_{id(request)}"
        
        # Extract operation info
        operation = self._extract_operation(request.url.path)
        
        # Log request start
        self.active_requests[request_id] = {
            "operation": operation,
            "start_time": start_time,
            "path": request.url.path,
            "method": request.method
        }
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Update stats
            stats = self.request_stats[operation]
            stats["count"] += 1
            stats["total_time"] += processing_time
            stats["last_request"] = datetime.utcnow().isoformat()
            
            # Add monitoring headers
            response.headers["X-Processing-Time"] = str(round(processing_time, 3))
            response.headers["X-Operation"] = operation
            response.headers["X-Request-ID"] = request_id
            
            # Log successful request
            logger.info(f"Stability AI request completed: {operation} in {processing_time:.3f}s")
            
            return response
            
        except Exception as e:
            # Update error stats
            self.request_stats[operation]["errors"] += 1
            
            # Log error
            logger.error(f"Stability AI request failed: {operation} - {str(e)}")
            
            raise
        
        finally:
            # Clean up active request
            self.active_requests.pop(request_id, None)
    
    def _extract_operation(self, path: str) -> str:
        """Extract operation name from request path.
        
        Args:
            path: Request path
            
        Returns:
            Operation name
        """
        path_parts = path.split("/")
        
        if len(path_parts) >= 4:
            if "generate" in path_parts:
                return f"generate_{path_parts[-1]}"
            elif "edit" in path_parts:
                return f"edit_{path_parts[-1]}"
            elif "upscale" in path_parts:
                return f"upscale_{path_parts[-1]}"
            elif "control" in path_parts:
                return f"control_{path_parts[-1]}"
            elif "3d" in path_parts:
                return f"3d_{path_parts[-1]}"
            elif "audio" in path_parts:
                return f"audio_{path_parts[-1]}"
        
        return "unknown"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics.
        
        Returns:
            Monitoring statistics
        """
        stats = {}
        
        for operation, data in self.request_stats.items():
            avg_time = data["total_time"] / data["count"] if data["count"] > 0 else 0
            error_rate = (data["errors"] / data["count"]) * 100 if data["count"] > 0 else 0
            
            stats[operation] = {
                "total_requests": data["count"],
                "total_errors": data["errors"],
                "error_rate_percent": round(error_rate, 2),
                "average_processing_time": round(avg_time, 3),
                "last_request": data["last_request"]
            }
        
        stats["active_requests"] = len(self.active_requests)
        stats["total_operations"] = len(self.request_stats)
        
        return stats


class ContentModerationMiddleware:
    """Content moderation middleware for Stability AI requests."""
    
    def __init__(self):
        """Initialize content moderation middleware."""
        self.blocked_terms = self._load_blocked_terms()
        self.warning_terms = self._load_warning_terms()
    
    async def __call__(self, request: Request, call_next):
        """Process request with content moderation.
        
        Args:
            request: FastAPI request
            call_next: Next middleware/endpoint
            
        Returns:
            Response
        """
        # Skip moderation for non-generation endpoints
        if not self._should_moderate(request.url.path):
            return await call_next(request)
        
        # Extract and check prompt content
        prompt = await self._extract_prompt(request)
        
        if prompt:
            moderation_result = self._moderate_content(prompt)
            
            if moderation_result["blocked"]:
                return JSONResponse(
                    status_code=403,
                    content={
                        "error": "Content moderation",
                        "message": "Your request was flagged by our content moderation system",
                        "issues": moderation_result["issues"]
                    }
                )
            
            if moderation_result["warnings"]:
                logger.warning(f"Content warnings for prompt: {moderation_result['warnings']}")
        
        # Process request
        response = await call_next(request)
        
        # Add content moderation headers
        if prompt:
            response.headers["X-Content-Moderated"] = "true"
        
        return response
    
    def _should_moderate(self, path: str) -> bool:
        """Check if path should be moderated.
        
        Args:
            path: Request path
            
        Returns:
            True if should be moderated
        """
        moderated_paths = ["/generate/", "/edit/", "/control/", "/audio/"]
        return any(mod_path in path for mod_path in moderated_paths)
    
    async def _extract_prompt(self, request: Request) -> Optional[str]:
        """Extract prompt from request.
        
        Args:
            request: FastAPI request
            
        Returns:
            Extracted prompt or None
        """
        try:
            if request.method == "POST":
                # For form data, we'd need to parse the form
                # This is a simplified version
                body = await request.body()
                if b"prompt=" in body:
                    # Extract prompt from form data (simplified)
                    body_str = body.decode('utf-8', errors='ignore')
                    if "prompt=" in body_str:
                        start = body_str.find("prompt=") + 7
                        end = body_str.find("&", start)
                        if end == -1:
                            end = len(body_str)
                        return body_str[start:end]
        except:
            pass
        
        return None
    
    def _moderate_content(self, prompt: str) -> Dict[str, Any]:
        """Moderate content for policy violations.
        
        Args:
            prompt: Text prompt to moderate
            
        Returns:
            Moderation result
        """
        issues = []
        warnings = []
        
        prompt_lower = prompt.lower()
        
        # Check for blocked terms
        for term in self.blocked_terms:
            if term in prompt_lower:
                issues.append(f"Contains blocked term: {term}")
        
        # Check for warning terms
        for term in self.warning_terms:
            if term in prompt_lower:
                warnings.append(f"Contains flagged term: {term}")
        
        return {
            "blocked": len(issues) > 0,
            "issues": issues,
            "warnings": warnings
        }
    
    def _load_blocked_terms(self) -> List[str]:
        """Load blocked terms from configuration.
        
        Returns:
            List of blocked terms
        """
        # In production, this would load from a configuration file or database
        return [
            # Add actual blocked terms here
        ]
    
    def _load_warning_terms(self) -> List[str]:
        """Load warning terms from configuration.
        
        Returns:
            List of warning terms
        """
        # In production, this would load from a configuration file or database
        return [
            # Add actual warning terms here
        ]


class CachingMiddleware:
    """Caching middleware for Stability AI responses."""
    
    def __init__(self, cache_duration: int = 3600):
        """Initialize caching middleware.
        
        Args:
            cache_duration: Cache duration in seconds
        """
        self.cache_duration = cache_duration
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_times: Dict[str, float] = {}
    
    async def __call__(self, request: Request, call_next):
        """Process request with caching.
        
        Args:
            request: FastAPI request
            call_next: Next middleware/endpoint
            
        Returns:
            Response (cached or fresh)
        """
        # Skip caching for non-cacheable endpoints
        if not self._should_cache(request):
            return await call_next(request)
        
        # Generate cache key
        cache_key = await self._generate_cache_key(request)
        
        # Check cache
        if self._is_cached(cache_key):
            logger.info(f"Returning cached result for {cache_key}")
            cached_data = self.cache[cache_key]
            
            return JSONResponse(
                content=cached_data["content"],
                headers={**cached_data["headers"], "X-Cache-Hit": "true"}
            )
        
        # Process request
        response = await call_next(request)
        
        # Cache successful responses
        if response.status_code == 200 and self._should_cache_response(response):
            await self._cache_response(cache_key, response)
        
        return response
    
    def _should_cache(self, request: Request) -> bool:
        """Check if request should be cached.
        
        Args:
            request: FastAPI request
            
        Returns:
            True if should be cached
        """
        # Only cache GET requests and certain POST operations
        if request.method == "GET":
            return True
        
        # Cache deterministic operations (those with seeds)
        cacheable_paths = ["/models/info", "/supported-formats", "/health"]
        return any(path in request.url.path for path in cacheable_paths)
    
    def _should_cache_response(self, response) -> bool:
        """Check if response should be cached.
        
        Args:
            response: FastAPI response
            
        Returns:
            True if should be cached
        """
        # Don't cache large binary responses
        content_length = response.headers.get("content-length")
        if content_length and int(content_length) > 1024 * 1024:  # 1MB
            return False
        
        return True
    
    async def _generate_cache_key(self, request: Request) -> str:
        """Generate cache key for request.
        
        Args:
            request: FastAPI request
            
        Returns:
            Cache key
        """
        import hashlib
        
        key_parts = [
            request.method,
            request.url.path,
            str(sorted(request.query_params.items()))
        ]
        
        # For POST requests, include body hash
        if request.method == "POST":
            body = await request.body()
            if body:
                key_parts.append(hashlib.md5(body).hexdigest())
        
        key_string = "|".join(key_parts)
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    def _is_cached(self, cache_key: str) -> bool:
        """Check if key is cached and not expired.
        
        Args:
            cache_key: Cache key
            
        Returns:
            True if cached and valid
        """
        if cache_key not in self.cache:
            return False
        
        cache_time = self.cache_times.get(cache_key, 0)
        return time.time() - cache_time < self.cache_duration
    
    async def _cache_response(self, cache_key: str, response) -> None:
        """Cache response data.
        
        Args:
            cache_key: Cache key
            response: Response to cache
        """
        try:
            # Only cache JSON responses for now
            if response.headers.get("content-type", "").startswith("application/json"):
                self.cache[cache_key] = {
                    "content": json.loads(response.body),
                    "headers": dict(response.headers)
                }
                self.cache_times[cache_key] = time.time()
        except:
            # Ignore cache errors
            pass
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        self.cache.clear()
        self.cache_times.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Cache statistics
        """
        current_time = time.time()
        expired_keys = [
            key for key, cache_time in self.cache_times.items()
            if current_time - cache_time > self.cache_duration
        ]
        
        return {
            "total_entries": len(self.cache),
            "expired_entries": len(expired_keys),
            "cache_hit_rate": "N/A",  # Would need request tracking
            "memory_usage": sum(len(str(data)) for data in self.cache.values())
        }


class RequestLoggingMiddleware:
    """Logging middleware for Stability AI requests."""
    
    def __init__(self):
        """Initialize logging middleware."""
        self.request_log = []
        self.max_log_entries = 1000
    
    async def __call__(self, request: Request, call_next):
        """Process request with logging.
        
        Args:
            request: FastAPI request
            call_next: Next middleware/endpoint
            
        Returns:
            Response
        """
        # Skip logging for non-Stability endpoints
        if not request.url.path.startswith("/api/stability"):
            return await call_next(request)
        
        start_time = time.time()
        request_id = f"{int(start_time * 1000)}_{id(request)}"
        
        # Log request details
        log_entry = {
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown")
        }
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Update log entry
            log_entry.update({
                "status_code": response.status_code,
                "processing_time": round(processing_time, 3),
                "response_size": len(response.body) if hasattr(response, 'body') else 0,
                "success": True
            })
            
            return response
            
        except Exception as e:
            # Log error
            log_entry.update({
                "error": str(e),
                "success": False,
                "processing_time": round(time.time() - start_time, 3)
            })
            raise
        
        finally:
            # Add to log
            self._add_log_entry(log_entry)
    
    def _add_log_entry(self, entry: Dict[str, Any]) -> None:
        """Add entry to request log.
        
        Args:
            entry: Log entry
        """
        self.request_log.append(entry)
        
        # Keep only recent entries
        if len(self.request_log) > self.max_log_entries:
            self.request_log = self.request_log[-self.max_log_entries:]
    
    def get_recent_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent log entries.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            Recent log entries
        """
        return self.request_log[-limit:]
    
    def get_log_summary(self) -> Dict[str, Any]:
        """Get summary of logged requests.
        
        Returns:
            Log summary statistics
        """
        if not self.request_log:
            return {"total_requests": 0}
        
        total_requests = len(self.request_log)
        successful_requests = sum(1 for entry in self.request_log if entry.get("success", False))
        
        # Calculate average processing time
        processing_times = [
            entry["processing_time"] for entry in self.request_log 
            if "processing_time" in entry
        ]
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        # Get operation breakdown
        operations = defaultdict(int)
        for entry in self.request_log:
            operation = entry.get("path", "unknown").split("/")[-1]
            operations[operation] += 1
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "error_rate_percent": round((1 - successful_requests / total_requests) * 100, 2),
            "average_processing_time": round(avg_processing_time, 3),
            "operations_breakdown": dict(operations),
            "time_range": {
                "start": self.request_log[0]["timestamp"],
                "end": self.request_log[-1]["timestamp"]
            }
        }


# Global middleware instances
rate_limiter = RateLimitMiddleware()
monitoring = MonitoringMiddleware()
caching = CachingMiddleware()
request_logging = RequestLoggingMiddleware()


def get_middleware_stats() -> Dict[str, Any]:
    """Get statistics from all middleware components.
    
    Returns:
        Combined middleware statistics
    """
    return {
        "rate_limiting": {
            "active_blocks": len(rate_limiter.blocked_until),
            "requests_per_window": rate_limiter.requests_per_window,
            "window_seconds": rate_limiter.window_seconds
        },
        "monitoring": monitoring.get_stats(),
        "caching": caching.get_cache_stats(),
        "logging": request_logging.get_log_summary()
    }