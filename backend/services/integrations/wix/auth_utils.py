"""
Authentication utilities for Wix API requests.

Supports both OAuth Bearer tokens and API keys for Wix Headless apps.
"""

import os
from typing import Dict, Optional
from loguru import logger


def get_wix_headers(
    access_token: str,
    client_id: Optional[str] = None,
    extra: Optional[Dict[str, str]] = None
) -> Dict[str, str]:
    """
    Build headers for Wix API requests with automatic token type detection.
    
    Supports:
    - OAuth Bearer tokens (JWT format: xxx.yyy.zzz)
    - Wix API keys (for Headless apps)
    
    Args:
        access_token: OAuth token OR API key
        client_id: Optional Wix client ID
        extra: Additional headers to include
        
    Returns:
        Headers dict with proper Authorization format
    """
    headers: Dict[str, str] = {
        'Content-Type': 'application/json',
    }
    
    if access_token:
        # Ensure access_token is a string (defensive check)
        if not isinstance(access_token, str):
            from services.integrations.wix.utils import normalize_token_string
            normalized = normalize_token_string(access_token)
            if normalized:
                access_token = normalized
            else:
                access_token = str(access_token)
        
        token = access_token.strip()
        if token:
            # Detect token type
            # API keys are typically longer and don't have JWT structure (xxx.yyy.zzz)
            # JWT tokens have exactly 2 dots separating 3 parts
            # Wix OAuth tokens can have format "OauthNG.JWS.xxx.yyy.zzz"
            
            # CRITICAL: Wix OAuth tokens can have format "OauthNG.JWS.xxx.yyy.zzz"
            # These should use "Bearer" prefix even though they have more than 2 dots
            if token.startswith('OauthNG.JWS.'):
                # Wix OAuth token - use Bearer prefix
                headers['Authorization'] = f'Bearer {token}'
                logger.debug(f"Using Wix OAuth token with Bearer prefix (OauthNG.JWS. format detected)")
            else:
                # Count dots - JWT has exactly 2 dots
                dot_count = token.count('.')
                
                if dot_count == 2 and len(token) < 500:
                    # Likely OAuth JWT token - use Bearer prefix
                    headers['Authorization'] = f'Bearer {token}'
                    logger.debug(f"Using OAuth Bearer token (JWT format detected)")
                else:
                    # Likely API key - use directly without Bearer prefix
                    headers['Authorization'] = token
                    logger.debug(f"Using API key for authorization (non-JWT format detected)")
    
    if client_id:
        headers['wix-client-id'] = client_id
    
    if extra:
        headers.update(extra)
    
    return headers


def get_wix_api_key() -> Optional[str]:
    """
    Get Wix API key from environment.
    
    For Wix Headless apps, API keys provide admin-level access.
    
    Returns:
        API key if set, None otherwise
    """
    api_key = os.getenv('WIX_API_KEY')
    if api_key:
        logger.warning(f"✅ Wix API key found in environment ({len(api_key)} chars)")
    else:
        logger.warning("❌ No Wix API key in environment")
    return api_key


def should_use_api_key(access_token: Optional[str] = None) -> bool:
    """
    Determine if we should use API key instead of OAuth token.
    
    Use API key if:
    - No OAuth token provided
    - OAuth token is getting 403 errors
    - API key is available in environment
    
    Args:
        access_token: Optional OAuth token
        
    Returns:
        True if should use API key, False otherwise
    """
    # If no access token, check for API key
    if not access_token or not access_token.strip():
        return get_wix_api_key() is not None
    
    # If access token looks like API key already, use it
    # Ensure access_token is a string (defensive check)
    if not isinstance(access_token, str):
        from services.integrations.wix.utils import normalize_token_string
        normalized = normalize_token_string(access_token)
        if normalized:
            access_token = normalized
        else:
            access_token = str(access_token)
    
    token = access_token.strip()
    if token.count('.') != 2 or len(token) > 500:
        return True
    
    return False

