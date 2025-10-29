"""
Rate Limiting Module
Handles rate limiting middleware and request tracking.
"""

import time
from collections import defaultdict
from typing import Dict, List, Optional
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from loguru import logger


class RateLimiter:
    """Manages rate limiting for ALwrity backend."""
    
    def __init__(self, window_seconds: int = 60, max_requests: int = 1000):  # Increased for development
        self.window_seconds = window_seconds
        self.max_requests = max_requests
        self.request_counts: Dict[str, List[float]] = defaultdict(list)
        
        # Endpoints exempt from rate limiting
        self.exempt_paths = [
            "/stream/strategies",
            "/stream/strategic-intelligence", 
            "/stream/keyword-research",
            "/latest-strategy",
            "/ai-analytics",
            "/gap-analysis",
            "/calendar-events",
            # Research endpoints - exempt from rate limiting
            "/api/research",
            "/api/blog-writer",
            "/api/blog-writer/research",
            "/api/blog-writer/research/",
            "/api/blog/research/status",
            "/calendar-generation/progress",
            "/health",
            "/health/database",
        ]
        # Prefixes to exempt entire route families (keep empty; rely on specific exemptions only)
        self.exempt_prefixes = []
    
    def is_exempt_path(self, path: str) -> bool:
        """Check if a path is exempt from rate limiting."""
        return any(exempt_path == path or exempt_path in path for exempt_path in self.exempt_paths) or any(
            path.startswith(prefix) for prefix in self.exempt_prefixes
        )
    
    def clean_old_requests(self, client_ip: str, current_time: float) -> None:
        """Clean old requests from the tracking dictionary."""
        self.request_counts[client_ip] = [
            req_time for req_time in self.request_counts[client_ip] 
            if current_time - req_time < self.window_seconds
        ]
    
    def is_rate_limited(self, client_ip: str, current_time: float) -> bool:
        """Check if a client has exceeded the rate limit."""
        self.clean_old_requests(client_ip, current_time)
        return len(self.request_counts[client_ip]) >= self.max_requests
    
    def add_request(self, client_ip: str, current_time: float) -> None:
        """Add a request to the tracking dictionary."""
        self.request_counts[client_ip].append(current_time)
    
    def get_rate_limit_response(self) -> JSONResponse:
        """Get a rate limit exceeded response."""
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Too many requests", 
                "retry_after": self.window_seconds
            },
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )
    
    async def rate_limit_middleware(self, request: Request, call_next) -> Response:
        """Rate limiting middleware with exemptions for streaming endpoints."""
        try:
            client_ip = request.client.host if request.client else "unknown"
            current_time = time.time()
            path = request.url.path
            
            # Check if path is exempt from rate limiting
            if self.is_exempt_path(path):
                response = await call_next(request)
                return response
            
            # Check rate limit
            if self.is_rate_limited(client_ip, current_time):
                logger.warning(f"Rate limit exceeded for {client_ip}")
                return self.get_rate_limit_response()
            
            # Add current request
            self.add_request(client_ip, current_time)
            
            response = await call_next(request)
            return response
            
        except Exception as e:
            logger.error(f"Error in rate limiting middleware: {e}")
            # Continue without rate limiting if there's an error
            response = await call_next(request)
            return response
    
    def get_rate_limit_status(self, client_ip: str) -> Dict[str, any]:
        """Get current rate limit status for a client."""
        current_time = time.time()
        self.clean_old_requests(client_ip, current_time)
        
        request_count = len(self.request_counts[client_ip])
        remaining_requests = max(0, self.max_requests - request_count)
        
        return {
            "client_ip": client_ip,
            "requests_in_window": request_count,
            "max_requests": self.max_requests,
            "remaining_requests": remaining_requests,
            "window_seconds": self.window_seconds,
            "is_limited": request_count >= self.max_requests
        }
    
    def reset_rate_limit(self, client_ip: Optional[str] = None) -> Dict[str, any]:
        """Reset rate limit for a specific client or all clients."""
        if client_ip:
            self.request_counts[client_ip] = []
            return {"message": f"Rate limit reset for {client_ip}"}
        else:
            self.request_counts.clear()
            return {"message": "Rate limit reset for all clients"}
