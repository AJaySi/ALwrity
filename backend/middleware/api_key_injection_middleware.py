"""
API Key Injection Middleware

Temporarily injects user-specific API keys into os.environ for the duration of the request.
This allows existing code that uses os.getenv('GEMINI_API_KEY') to work without modification.

IMPORTANT: This is a compatibility layer. For new code, use UserAPIKeyContext directly.
"""

import os
from fastapi import Request
from loguru import logger
from typing import Callable
from services.user_api_key_context import user_api_keys


class APIKeyInjectionMiddleware:
    """
    Middleware that injects user-specific API keys into environment variables
    for the duration of each request.
    """
    
    def __init__(self):
        self.original_keys = {}
    
    async def __call__(self, request: Request, call_next: Callable):
        """
        Inject user-specific API keys before processing request,
        restore original values after request completes.
        """
        
        # Try to extract user_id from Authorization header
        user_id = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            try:
                from middleware.auth_middleware import clerk_auth
                token = auth_header.replace('Bearer ', '')
                user = await clerk_auth.verify_token(token)
                if user:
                    # Try different possible keys for user_id
                    user_id = user.get('user_id') or user.get('clerk_user_id') or user.get('id')
                    logger.debug(f"[API Key Injection] Extracted user_id: {user_id}")
            except Exception as e:
                logger.debug(f"[API Key Injection] Could not extract user from token: {e}")
        
        if not user_id:
            # No authenticated user, proceed without injection
            return await call_next(request)
        
        # Check if we're in production mode
        is_production = os.getenv('DEPLOY_ENV', 'local') == 'production'
        
        if not is_production:
            # Local mode - keys already in .env, no injection needed
            return await call_next(request)
        
        # Get user-specific API keys from database
        with user_api_keys(user_id) as user_keys:
            if not user_keys:
                logger.warning(f"No API keys found for user {user_id}")
                return await call_next(request)
            
            # Save original environment values
            original_keys = {}
            keys_to_inject = {
                'gemini': 'GEMINI_API_KEY',
                'exa': 'EXA_API_KEY',
                'copilotkit': 'COPILOTKIT_API_KEY',
                'openai': 'OPENAI_API_KEY',
                'anthropic': 'ANTHROPIC_API_KEY',
                'tavily': 'TAVILY_API_KEY',
                'serper': 'SERPER_API_KEY',
                'firecrawl': 'FIRECRAWL_API_KEY',
            }
            
            # Inject user-specific keys into environment
            for provider, env_var in keys_to_inject.items():
                if provider in user_keys and user_keys[provider]:
                    # Save original value (if any)
                    original_keys[env_var] = os.environ.get(env_var)
                    # Inject user-specific key
                    os.environ[env_var] = user_keys[provider]
                    logger.debug(f"[PRODUCTION] Injected {env_var} for user {user_id}")
            
            try:
                # Process request with user-specific keys in environment
                response = await call_next(request)
                return response
                
            finally:
                # CRITICAL: Restore original environment values
                for env_var, original_value in original_keys.items():
                    if original_value is None:
                        # Key didn't exist before, remove it
                        os.environ.pop(env_var, None)
                    else:
                        # Restore original value
                        os.environ[env_var] = original_value
                
                logger.debug(f"[PRODUCTION] Cleaned up environment for user {user_id}")


async def api_key_injection_middleware(request: Request, call_next: Callable):
    """
    Middleware function that injects user-specific API keys into environment.
    
    Usage in app.py:
        app.middleware("http")(api_key_injection_middleware)
    """
    middleware = APIKeyInjectionMiddleware()
    return await middleware(request, call_next)

