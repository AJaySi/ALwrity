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
from services.usage_tracking_service import UsageTrackingService
from services.pricing_service import PricingService

class DatabaseAPIMonitor:
    """Database-backed API monitoring with usage tracking and subscription management."""
    
    def __init__(self):
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'hit_rate': 0.0
        }
        # API provider detection patterns
        self.provider_patterns = {
            APIProvider.GEMINI: [r'/gemini', r'gemini', r'google.*ai'],
            APIProvider.OPENAI: [r'/openai', r'openai', r'gpt'],
            APIProvider.ANTHROPIC: [r'/anthropic', r'claude', r'anthropic'],
            APIProvider.MISTRAL: [r'/mistral', r'mistral'],
            APIProvider.TAVILY: [r'/tavily', r'tavily'],
            APIProvider.SERPER: [r'/serper', r'serper', r'google.*search'],
            APIProvider.METAPHOR: [r'/metaphor', r'/exa', r'metaphor', r'exa'],
            APIProvider.FIRECRAWL: [r'/firecrawl', r'firecrawl'],
            APIProvider.STABILITY: [r'/stability', r'stable.*diffusion', r'stability']
        }
    
    def detect_api_provider(self, path: str, user_agent: str = None) -> Optional[APIProvider]:
        """Detect which API provider is being used based on request details."""
        path_lower = path.lower()
        user_agent_lower = (user_agent or '').lower()
        
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

    async def add_request(self, db: Session, path: str, method: str, status_code: int, 
                         duration: float, user_id: str = None, cache_hit: bool = None,
                         request_size: int = None, response_size: int = None,
                         user_agent: str = None, ip_address: str = None,
                         request_body: str = None, response_body: str = None):
        """Add a request to database monitoring with usage tracking."""
        try:
            # Store individual request
            api_request = APIRequest(
                path=path,
                method=method,
                status_code=status_code,
                duration=duration,
                user_id=user_id,
                cache_hit=cache_hit,
                request_size=request_size,
                response_size=response_size,
                user_agent=user_agent,
                ip_address=ip_address
            )
            db.add(api_request)
            
            # Track API usage if this is an API call to external providers
            api_provider = self.detect_api_provider(path, user_agent)
            if api_provider and user_id:
                try:
                    # Extract usage metrics
                    usage_metrics = self.extract_usage_metrics(request_body, response_body)
                    
                    # Track usage with the usage tracking service
                    usage_service = UsageTrackingService(db)
                    await usage_service.track_api_usage(
                        user_id=user_id,
                        provider=api_provider,
                        endpoint=path,
                        method=method,
                        model_used=usage_metrics.get('model_used'),
                        tokens_input=usage_metrics.get('tokens_input', 0),
                        tokens_output=usage_metrics.get('tokens_output', 0),
                        response_time=duration,
                        status_code=status_code,
                        request_size=request_size,
                        response_size=response_size,
                        user_agent=user_agent,
                        ip_address=ip_address,
                        search_count=usage_metrics.get('search_count', 0),
                        image_count=usage_metrics.get('image_count', 0),
                        page_count=usage_metrics.get('page_count', 0)
                    )
                    logger.info(f"Tracked usage for {user_id}: {api_provider.value} - {usage_metrics.get('tokens_input', 0)}+{usage_metrics.get('tokens_output', 0)} tokens")
                except Exception as usage_error:
                    logger.error(f"Error tracking API usage: {usage_error}")
                    # Don't fail the main request if usage tracking fails
            
            # Update endpoint stats
            endpoint_key = f"{method} {path}"
            endpoint_stats = db.query(APIEndpointStats).filter(
                APIEndpointStats.endpoint == endpoint_key
            ).first()
            
            if not endpoint_stats:
                endpoint_stats = APIEndpointStats(endpoint=endpoint_key)
                db.add(endpoint_stats)
            
            # Update statistics - handle None values
            endpoint_stats.total_requests = (endpoint_stats.total_requests or 0) + 1
            endpoint_stats.total_duration = (endpoint_stats.total_duration or 0.0) + duration
            endpoint_stats.avg_duration = endpoint_stats.total_duration / endpoint_stats.total_requests
            endpoint_stats.last_called = datetime.utcnow()
            
            if status_code >= 400:
                endpoint_stats.total_errors = (endpoint_stats.total_errors or 0) + 1
            
            if cache_hit is not None:
                if cache_hit:
                    endpoint_stats.cache_hits = (endpoint_stats.cache_hits or 0) + 1
                else:
                    endpoint_stats.cache_misses = (endpoint_stats.cache_misses or 0) + 1
                
                total_cache_requests = endpoint_stats.cache_hits + endpoint_stats.cache_misses
                if total_cache_requests > 0:
                    endpoint_stats.cache_hit_rate = (endpoint_stats.cache_hits / total_cache_requests) * 100
            
            # Update min/max duration
            if endpoint_stats.min_duration is None or duration < endpoint_stats.min_duration:
                endpoint_stats.min_duration = duration
            if endpoint_stats.max_duration is None or duration > endpoint_stats.max_duration:
                endpoint_stats.max_duration = duration
            
            db.commit()
            
            # Update cache stats
            if cache_hit is not None:
                if cache_hit:
                    self.cache_stats['hits'] += 1
                else:
                    self.cache_stats['misses'] += 1
                
                total_cache_requests = self.cache_stats['hits'] + self.cache_stats['misses']
                if total_cache_requests > 0:
                    self.cache_stats['hit_rate'] = (self.cache_stats['hits'] / total_cache_requests) * 100
            
        except Exception as e:
            logger.error(f"❌ Error storing API request: {str(e)}")
            db.rollback()
    
    async def get_stats(self, db: Session, minutes: int = 5) -> Dict[str, Any]:
        """Get current monitoring statistics from database."""
        try:
            now = datetime.utcnow()
            since = now - timedelta(minutes=minutes)
            
            # Recent requests
            recent_requests = db.query(APIRequest).filter(
                APIRequest.timestamp >= since
            ).count()
            
            # Recent errors
            recent_errors = db.query(APIRequest).filter(
                and_(
                    APIRequest.timestamp >= since,
                    APIRequest.status_code >= 400
                )
            ).count()
            
            # Top endpoints
            top_endpoints = db.query(APIEndpointStats).order_by(
                APIEndpointStats.total_requests.desc()
            ).limit(10).all()
            
            # Recent errors details
            recent_error_details = db.query(APIRequest).filter(
                and_(
                    APIRequest.timestamp >= since,
                    APIRequest.status_code >= 400
                )
            ).order_by(APIRequest.timestamp.desc()).limit(10).all()
            
            # Overall stats
            total_requests = db.query(APIRequest).count()
            total_errors = db.query(APIRequest).filter(APIRequest.status_code >= 400).count()
            
            # Calculate error rate
            error_rate = (recent_errors / max(recent_requests, 1)) * 100
            
            return {
                'timestamp': now.isoformat(),
                'overview': {
                    'total_requests': total_requests,
                    'total_errors': total_errors,
                    'recent_requests': recent_requests,
                    'recent_errors': recent_errors
                },
                'cache_performance': self.cache_stats,
                'top_endpoints': [
                    {
                        'endpoint': endpoint.endpoint,
                        'count': endpoint.total_requests or 0,
                        'avg_time': round(endpoint.avg_duration or 0.0, 3),
                        'errors': endpoint.total_errors or 0,
                        'last_called': endpoint.last_called.isoformat() if endpoint.last_called else None,
                        'cache_hit_rate': round(endpoint.cache_hit_rate or 0.0, 2)
                    }
                    for endpoint in top_endpoints
                ],
                'recent_errors': [
                    {
                        'timestamp': error.timestamp.isoformat(),
                        'path': error.path,
                        'method': error.method,
                        'status_code': error.status_code,
                        'duration': error.duration
                    }
                    for error in recent_error_details
                ],
                'system_health': {
                    'status': 'healthy' if recent_errors < 5 else 'warning',
                    'error_rate': round(error_rate, 2)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting monitoring stats: {str(e)}")
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e),
                'overview': {'total_requests': 0, 'total_errors': 0, 'recent_requests': 0, 'recent_errors': 0},
                'system_health': {'status': 'unknown', 'error_rate': 0.0}
            }
    
    async def get_lightweight_stats(self, db: Session) -> Dict[str, Any]:
        """Get lightweight stats for dashboard header."""
        try:
            now = datetime.utcnow()
            since = now - timedelta(minutes=5)
            
            # Quick stats for dashboard
            recent_requests = db.query(APIRequest).filter(
                APIRequest.timestamp >= since
            ).count()
            
            recent_errors = db.query(APIRequest).filter(
                and_(
                    APIRequest.timestamp >= since,
                    APIRequest.status_code >= 400
                )
            ).count()
            
            # Determine status
            if recent_errors == 0:
                status = "healthy"
                icon = "🟢"
            elif recent_errors < 3:
                status = "warning"
                icon = "🟡"
            else:
                status = "critical"
                icon = "🔴"
            
            return {
                'status': status,
                'icon': icon,
                'recent_requests': recent_requests,
                'recent_errors': recent_errors,
                'error_rate': round((recent_errors / max(recent_requests, 1)) * 100, 1),
                'timestamp': now.isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting lightweight stats: {str(e)}")
            return {
                'status': 'unknown',
                'icon': '⚪',
                'recent_requests': 0,
                'recent_errors': 0,
                'error_rate': 0.0,
                'timestamp': datetime.utcnow().isoformat()
            }

# Global monitor instance
api_monitor = DatabaseAPIMonitor()

# List of endpoints to exclude from monitoring
EXCLUDED_ENDPOINTS = [
    "/api/content-planning/monitoring/lightweight-stats",
    "/api/content-planning/monitoring/api-stats",
    "/api/content-planning/monitoring/cache-stats",
    "/api/content-planning/monitoring/health"
]

def should_monitor_endpoint(path: str) -> bool:
    """Check if an endpoint should be monitored."""
    return not any(path.endswith(excluded) for excluded in EXCLUDED_ENDPOINTS)

async def check_usage_limits_middleware(request: Request, user_id: str, request_body: str = None) -> Optional[JSONResponse]:
    """Check usage limits before processing request."""
    if not user_id:
        return None
    
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
    
    # Skip monitoring for excluded endpoints
    if not should_monitor_endpoint(request.url.path):
        response = await call_next(request)
        return response
    
    # Extract request details
    user_id = None
    try:
        if hasattr(request, 'query_params') and 'user_id' in request.query_params:
            user_id = request.query_params['user_id']
        elif hasattr(request, 'path_params') and 'user_id' in request.path_params:
            user_id = request.path_params['user_id']
        # Also check headers for user identification
        elif 'x-user-id' in request.headers:
            user_id = request.headers['x-user-id']
        # Check for authorization header with user info
        elif 'authorization' in request.headers:
            # This would need to be implemented based on your auth system
            pass
    except:
        pass
    
    # Capture request body for usage tracking (read once)
    request_body = None
    try:
        if hasattr(request, '_body'):
            request_body = request._body.decode('utf-8') if request._body else None
        else:
            body = await request.body()
            request_body = body.decode('utf-8') if body else None
    except:
        pass
    
    # Check usage limits before processing
    limit_response = await check_usage_limits_middleware(request, user_id, request_body)
    if limit_response:
        return limit_response
    
    # Get database session
    db = next(get_db())
    
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
        
        # Check for cache-related headers
        cache_hit = None
        if hasattr(response, 'headers'):
            cache_header = response.headers.get('x-cache-status')
            if cache_header:
                cache_hit = cache_header.lower() == 'hit'
        
        # Store in database with enhanced tracking
        await api_monitor.add_request(
            db=db,
            path=request.url.path,
            method=request.method,
            status_code=status_code,
            duration=duration,
            user_id=user_id,
            cache_hit=cache_hit,
            request_size=len(request_body) if request_body else None,
            response_size=len(response_body) if response_body else None,
            user_agent=request.headers.get('user-agent'),
            ip_address=request.client.host if request.client else None,
            request_body=request_body,
            response_body=response_body
        )
        
        # Add monitoring headers
        response.headers['x-response-time'] = f"{duration:.3f}s"
        response.headers['x-monitor-id'] = f"{int(time.time())}"
        
        return response
        
    except Exception as e:
        duration = time.time() - start_time
        status_code = 500
        
        # Store error in database with enhanced tracking
        await api_monitor.add_request(
            db=db,
            path=request.url.path,
            method=request.method,
            status_code=status_code,
            duration=duration,
            user_id=user_id,
            cache_hit=False,
            request_size=len(request_body) if request_body else None,
            response_size=None,
            user_agent=request.headers.get('user-agent'),
            ip_address=request.client.host if request.client else None,
            request_body=request_body,
            response_body=None
        )
        
        logger.error(f"❌ API Error: {request.method} {request.url.path} - {str(e)}")
        
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "monitor_id": int(time.time())}
        )
    finally:
        db.close()

async def get_monitoring_stats(minutes: int = 5) -> Dict[str, Any]:
    """Get current monitoring statistics."""
    db = next(get_db())
    try:
        return await api_monitor.get_stats(db, minutes)
    finally:
        db.close()

async def get_lightweight_stats() -> Dict[str, Any]:
    """Get lightweight stats for dashboard header."""
    db = next(get_db())
    try:
        return await api_monitor.get_lightweight_stats(db)
    finally:
        db.close()
