"""
Enhanced FastAPI Monitoring Middleware
Database-backed monitoring for API calls, errors, performance metrics, and usage tracking.
Includes comprehensive subscription-based usage monitoring and cost tracking.
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
import asyncio
from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
import re

from models.api_monitoring import APIRequest, APIEndpointStats, SystemHealth, CachePerformance
from models.subscription_models import APIProvider
from services.database import get_db
from .usage_tracking_service import UsageTrackingService
from .pricing_service import PricingService

class DatabaseAPIMonitor:
    """Database-backed API monitoring with usage tracking and subscription management."""
    
    def __init__(self):
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'hit_rate': 0.0
        }
        # API provider detection patterns - Updated to match actual endpoints
        self.provider_patterns = {
            APIProvider.GEMINI: [
                r'gemini', r'google.*ai'
            ],
            APIProvider.OPENAI: [r'openai', r'gpt', r'chatgpt'],
            APIProvider.ANTHROPIC: [r'anthropic', r'claude'],
            APIProvider.MISTRAL: [r'mistral'],
            APIProvider.TAVILY: [r'tavily'],
            APIProvider.SERPER: [r'serper'],
            APIProvider.METAPHOR: [r'metaphor', r'/exa'],
            APIProvider.FIRECRAWL: [r'firecrawl']
        }
    
    def detect_api_provider(self, path: str, user_agent: str = None) -> Optional[APIProvider]:
        """Detect which API provider is being used based on request details."""
        path_lower = path.lower()
        user_agent_lower = (user_agent or '').lower()

        # Permanently ignore internal route families that must not accrue or check provider usage
        if path_lower.startswith('/api/onboarding/') or path_lower.startswith('/api/subscription/'):
            return None
        
        for provider, patterns in self.provider_patterns.items():
            for pattern in patterns:
                if re.search(pattern, path_lower) or re.search(pattern, user_agent_lower):
                    return provider
        
        return None
    
    def extract_usage_metrics(self, request_body: str = None, response_body: str = None) -> Dict[str, Any]:
        """Extract usage metrics from request/response bodies."""
        metrics = {
            'tokens_input': 0,
            'tokens_output': 0,
            'model_used': None,
            'search_count': 0,
            'image_count': 0,
            'page_count': 0
        }
        
        try:
            # Try to parse request body for input tokens/content
            if request_body:
                request_data = json.loads(request_body) if isinstance(request_body, str) else request_body
                
                # Extract model information
                if 'model' in request_data:
                    metrics['model_used'] = request_data['model']
                
                # Estimate input tokens from prompt/content
                if 'prompt' in request_data:
                    metrics['tokens_input'] = self._estimate_tokens(request_data['prompt'])
                elif 'messages' in request_data:
                    total_content = ' '.join([msg.get('content', '') for msg in request_data['messages']])
                    metrics['tokens_input'] = self._estimate_tokens(total_content)
                elif 'input' in request_data:
                    metrics['tokens_input'] = self._estimate_tokens(str(request_data['input']))
                
                # Count specific request types
                if 'query' in request_data or 'search' in request_data:
                    metrics['search_count'] = 1
                if 'image' in request_data or 'generate_image' in request_data:
                    metrics['image_count'] = 1
                if 'url' in request_data or 'crawl' in request_data:
                    metrics['page_count'] = 1
            
            # Try to parse response body for output tokens
            if response_body:
                response_data = json.loads(response_body) if isinstance(response_body, str) else response_body
                
                # Extract output content and estimate tokens
                if 'text' in response_data:
                    metrics['tokens_output'] = self._estimate_tokens(response_data['text'])
                elif 'content' in response_data:
                    metrics['tokens_output'] = self._estimate_tokens(str(response_data['content']))
                elif 'choices' in response_data and response_data['choices']:
                    choice = response_data['choices'][0]
                    if 'message' in choice and 'content' in choice['message']:
                        metrics['tokens_output'] = self._estimate_tokens(choice['message']['content'])
                
                # Extract actual token usage if provided by API
                if 'usage' in response_data:
                    usage = response_data['usage']
                    if 'prompt_tokens' in usage:
                        metrics['tokens_input'] = usage['prompt_tokens']
                    if 'completion_tokens' in usage:
                        metrics['tokens_output'] = usage['completion_tokens']
        
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.debug(f"Could not extract usage metrics: {e}")
        
        return metrics
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (rough approximation)."""
        if not text:
            return 0
        # Rough estimation: 1.3 tokens per word on average
        word_count = len(str(text).split())
        return int(word_count * 1.3)

async def check_usage_limits_middleware(request: Request, user_id: str, request_body: str = None) -> Optional[JSONResponse]:
    """Check usage limits before processing request."""
    if not user_id:
        return None
    
    # No special whitelist; onboarding/subscription are ignored by provider detection
    try:
        path = request.url.path
    except Exception:
        pass
    
    try:
        db = next(get_db())
        api_monitor = DatabaseAPIMonitor()
        
        # Detect if this is an API call that should be rate limited
        api_provider = api_monitor.detect_api_provider(request.url.path, request.headers.get('user-agent'))
        if not api_provider:
            return None
        
        # Use provided request body or read it if not provided
        if request_body is None:
            try:
                if hasattr(request, '_body'):
                    request_body = request._body
                else:
                    # Try to read body (this might not work in all cases)
                    body = await request.body()
                    request_body = body.decode('utf-8') if body else None
            except:
                pass
        
        # Estimate tokens needed
        tokens_requested = 0
        if request_body:
            usage_metrics = api_monitor.extract_usage_metrics(request_body)
            tokens_requested = usage_metrics.get('tokens_input', 0)
        
        # Check limits
        usage_service = UsageTrackingService(db)
        can_proceed, message, usage_info = await usage_service.enforce_usage_limits(
            user_id=user_id,
            provider=api_provider,
            tokens_requested=tokens_requested
        )
        
        if not can_proceed:
            logger.warning(f"Usage limit exceeded for {user_id}: {message}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Usage limit exceeded",
                    "message": message,
                    "usage_info": usage_info,
                    "provider": api_provider.value
                }
            )
        
        # Warn if approaching limits
        if usage_info.get('call_usage_percentage', 0) >= 80 or usage_info.get('cost_usage_percentage', 0) >= 80:
            logger.warning(f"User {user_id} approaching usage limits: {usage_info}")
        
        return None
        
    except Exception as e:
        logger.error(f"Error checking usage limits: {e}")
        # Don't block requests if usage checking fails
        return None
    finally:
        db.close()

async def monitoring_middleware(request: Request, call_next):
    """Enhanced FastAPI middleware for monitoring API calls with usage tracking."""
    start_time = time.time()
    
    # Get database session
    db = next(get_db())
    
    # Extract request details - Enhanced user identification
    user_id = None
    try:
        # PRIORITY 1: Check request.state.user_id (set by API key injection middleware)
        if hasattr(request.state, 'user_id') and request.state.user_id:
            user_id = request.state.user_id
            logger.debug(f"Monitoring: Using user_id from request.state: {user_id}")
        
        # PRIORITY 2: Check query parameters
        elif hasattr(request, 'query_params') and 'user_id' in request.query_params:
            user_id = request.query_params['user_id']
        elif hasattr(request, 'path_params') and 'user_id' in request.path_params:
            user_id = request.path_params['user_id']
        
        # PRIORITY 3: Check headers for user identification
        elif 'x-user-id' in request.headers:
            user_id = request.headers['x-user-id']
        elif 'x-user-email' in request.headers:
            user_id = request.headers['x-user-email']  # Use email as user identifier
        elif 'x-session-id' in request.headers:
            user_id = request.headers['x-session-id']  # Use session as fallback
        
        # Check for authorization header with user info
        elif 'authorization' in request.headers:
            # Auth middleware should have set request.state.user_id
            # If not, this indicates an authentication failure that should be logged
            user_id = None
            logger.warning("Monitoring: Auth header present but no user_id in state - authentication may have failed")
        
        # Final fallback: None (skip usage limits for truly anonymous/unauthenticated)
        else:
            user_id = None
            
    except Exception as e:
        logger.debug(f"Error extracting user ID: {e}")
        user_id = None  # On error, skip usage limits
    
    # Capture request body for usage tracking (read once, safely)
    request_body = None
    try:
        # Only read body for POST/PUT/PATCH requests to avoid issues
        if request.method in ['POST', 'PUT', 'PATCH']:
            if hasattr(request, '_body') and request._body:
                request_body = request._body.decode('utf-8')
            else:
                # Read body only if it hasn't been read yet
                try:
                    body = await request.body()
                    request_body = body.decode('utf-8') if body else None
                except Exception as body_error:
                    logger.debug(f"Could not read request body: {body_error}")
                    request_body = None
    except Exception as e:
        logger.debug(f"Error capturing request body: {e}")
        request_body = None
    
    # Check usage limits before processing
    limit_response = await check_usage_limits_middleware(request, user_id, request_body)
    if limit_response:
        return limit_response
    
    try:
        response = await call_next(request)
        status_code = response.status_code
        duration = time.time() - start_time
        
        # Capture response body for usage tracking
        response_body = None
        try:
            if hasattr(response, 'body'):
                response_body = response.body.decode('utf-8') if response.body else None
            elif hasattr(response, '_content'):
                response_body = response._content.decode('utf-8') if response._content else None
        except:
            pass
        
        # Track API usage if this is an API call to external providers
        api_monitor = DatabaseAPIMonitor()
        api_provider = api_monitor.detect_api_provider(request.url.path, request.headers.get('user-agent'))
        if api_provider and user_id:
            logger.info(f"Detected API call: {request.url.path} -> {api_provider.value} for user: {user_id}")
            try:
                # Extract usage metrics
                usage_metrics = api_monitor.extract_usage_metrics(request_body, response_body)
                
                # Track usage with the usage tracking service
                usage_service = UsageTrackingService(db)
                await usage_service.track_api_usage(
                    user_id=user_id,
                    provider=api_provider,
                    endpoint=request.url.path,
                    method=request.method,
                    model_used=usage_metrics.get('model_used'),
                    tokens_input=usage_metrics.get('tokens_input', 0),
                    tokens_output=usage_metrics.get('tokens_output', 0),
                    response_time=duration,
                    status_code=status_code,
                    request_size=len(request_body) if request_body else None,
                    response_size=len(response_body) if response_body else None,
                    user_agent=request.headers.get('user-agent'),
                    ip_address=request.client.host if request.client else None,
                    search_count=usage_metrics.get('search_count', 0),
                    image_count=usage_metrics.get('image_count', 0),
                    page_count=usage_metrics.get('page_count', 0)
                )
            except Exception as usage_error:
                logger.error(f"Error tracking API usage: {usage_error}")
                # Don't fail the main request if usage tracking fails
        
        return response
        
    except Exception as e:
        duration = time.time() - start_time
        status_code = 500
        
        # Store minimal error info
        logger.error(f"API Error: {request.method} {request.url.path} - {str(e)}")
        
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )
    finally:
        db.close()

async def get_monitoring_stats(minutes: int = 5) -> Dict[str, Any]:
    """Get current monitoring statistics."""
    db = next(get_db())
    try:
        # Placeholder to match old API; heavy stats handled elsewhere
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'overview': {
                'recent_requests': 0,
                'recent_errors': 0,
            },
            'cache_performance': {'hits': 0, 'misses': 0, 'hit_rate': 0.0},
            'recent_errors': [],
            'system_health': {'status': 'healthy', 'error_rate': 0.0}
        }
    finally:
        db.close()

async def get_lightweight_stats() -> Dict[str, Any]:
    """Get lightweight stats for dashboard header."""
    db = next(get_db())
    try:
        # Minimal viable placeholder values
        now = datetime.utcnow()
        return {
            'status': 'healthy',
            'icon': '🟢',
            'recent_requests': 0,
            'recent_errors': 0,
            'error_rate': 0.0,
            'timestamp': now.isoformat()
        }
    finally:
        db.close()
