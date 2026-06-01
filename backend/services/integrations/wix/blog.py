from typing import Any, Dict, List, Optional
import requests
from loguru import logger

from .retry import wix_api_call_with_retry, WixAPIError


class WixBlogService:
    """Service for Wix Blog API operations with retry logic and error handling."""
    
    def __init__(self, base_url: str, client_id: Optional[str]):
        self.base_url = base_url
        self.client_id = client_id

    def headers(self, access_token: str, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Build headers with automatic token type detection."""
        h: Dict[str, str] = {
            'Content-Type': 'application/json',
        }
        
        if access_token:
            # Normalize token to string if needed
            if not isinstance(access_token, str):
                from .utils import normalize_token_string
                normalized = normalize_token_string(access_token)
                if normalized:
                    access_token = normalized
                else:
                    access_token = str(access_token)
            
            token = access_token.strip()
            if token:
                if token.startswith('OauthNG.JWS.'):
                    h['Authorization'] = f'Bearer {token}'
                    logger.debug("Using Wix OAuth token with Bearer prefix (OauthNG.JWS. format detected)")
                elif token.startswith('IST.'):
                    h['Authorization'] = token
                    logger.debug("Using Wix API key for authorization (IST. format detected)")
                elif token.count('.') == 2:
                    h['Authorization'] = f'Bearer {token}'
                    logger.debug("Using OAuth Bearer token for authorization (JWT: 2 dots)")
                else:
                    h['Authorization'] = token
                    logger.debug("Using token as-is for authorization")
        
        if self.client_id:
            h['wix-client-id'] = self.client_id
        if extra:
            h.update(extra)
        return h

    def create_draft_post(self, access_token: str, payload: Dict[str, Any], extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Create draft post with retry logic and consolidated logging."""
        from .logger import wix_logger
        import json
        import traceback as tb
        
        # Build payload summary for logging (safe, no sensitive data)
        payload_summary = {}
        if 'draftPost' in payload:
            dp = payload['draftPost']
            payload_summary['draftPost'] = {
                'title': dp.get('title'),
                'richContent': {'nodes': len(dp.get('richContent', {}).get('nodes', []))} if 'richContent' in dp else None,
                'seoData': 'seoData' in dp
            }
        
        request_headers = self.headers(access_token, extra_headers)
        logger.debug(f"Wix API request headers: {list(request_headers.keys())}")
        if 'wix-site-id' in request_headers:
            logger.info(f"Wix API call includes wix-site-id: {request_headers['wix-site-id'][:8]}...")
        else:
            logger.warning("Wix API call MISSING wix-site-id header — this may fail for multi-site tokens")
        
        url = f"{self.base_url}/blog/v3/draft-posts"
        
        try:
            result = wix_api_call_with_retry('POST', url, request_headers, json_payload=payload, max_attempts=3)
            wix_logger.log_api_call("POST", "/blog/v3/draft-posts", 200, payload_summary, None)
            return result
        except WixAPIError as e:
            wix_logger.log_api_call("POST", "/blog/v3/draft-posts", e.status_code or 500, payload_summary, e.response_body)
            logger.error(f"Wix create_draft_post failed after retries: HTTP {e.status_code} - {e.response_body}")
            raise
        except Exception as e:
            wix_logger.log_api_call("POST", "/blog/v3/draft-posts", 500, payload_summary, str(e)[:200])
            logger.error(f"Unexpected error in create_draft_post: {e}")
            raise

    def publish_draft(self, access_token: str, draft_post_id: str, extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Publish a draft post with retry logic."""
        url = f"{self.base_url}/blog/v3/draft-posts/{draft_post_id}/publish"
        headers = self.headers(access_token, extra_headers)
        
        try:
            return wix_api_call_with_retry('POST', url, headers, max_attempts=3)
        except WixAPIError as e:
            logger.error(f"Wix publish_draft failed: HTTP {e.status_code} - {e.response_body}")
            raise

    def list_categories(self, access_token: str, extra_headers: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """List blog categories with retry logic."""
        url = f"{self.base_url}/blog/v3/categories"
        headers = self.headers(access_token, extra_headers)
        
        try:
            result = wix_api_call_with_retry('GET', url, headers, max_attempts=3)
            return result.get('categories', [])
        except WixAPIError as e:
            logger.error(f"Wix list_categories failed: HTTP {e.status_code}")
            raise

    def create_category(self, access_token: str, label: str, description: Optional[str] = None, 
                        language: Optional[str] = None, extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Create a blog category with retry logic."""
        url = f"{self.base_url}/blog/v3/categories"
        headers = self.headers(access_token, extra_headers)
        payload: Dict[str, Any] = {'category': {'label': label}, 'fieldsets': ['URL']}
        if description:
            payload['category']['description'] = description
        if language:
            payload['category']['language'] = language
        
        try:
            return wix_api_call_with_retry('POST', url, headers, json_payload=payload, max_attempts=3)
        except WixAPIError as e:
            logger.error(f"Wix create_category failed: HTTP {e.status_code}")
            raise

    def list_tags(self, access_token: str, extra_headers: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """List blog tags with retry logic."""
        url = f"{self.base_url}/blog/v3/tags"
        headers = self.headers(access_token, extra_headers)
        
        try:
            result = wix_api_call_with_retry('GET', url, headers, max_attempts=3)
            return result.get('tags', [])
        except WixAPIError as e:
            logger.error(f"Wix list_tags failed: HTTP {e.status_code}")
            raise

    def create_tag(self, access_token: str, label: str, language: Optional[str] = None, 
                   extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Create a blog tag with retry logic."""
        url = f"{self.base_url}/blog/v3/tags"
        headers = self.headers(access_token, extra_headers)
        payload: Dict[str, Any] = {'label': label, 'fieldsets': ['URL']}
        if language:
            payload['language'] = language
        
        try:
            return wix_api_call_with_retry('POST', url, headers, json_payload=payload, max_attempts=3)
        except WixAPIError as e:
            logger.error(f"Wix create_tag failed: HTTP {e.status_code}")
            raise

    def get_draft_post(self, access_token: str, draft_post_id: str, 
                       extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Get a draft post by ID with retry logic."""
        url = f"{self.base_url}/blog/v3/draft-posts/{draft_post_id}"
        headers = self.headers(access_token, extra_headers)
        
        try:
            return wix_api_call_with_retry('GET', url, headers, max_attempts=3)
        except WixAPIError as e:
            logger.error(f"Wix get_draft_post failed: HTTP {e.status_code}")
            raise

    def update_draft_post(self, access_token: str, draft_post_id: str, payload: Dict[str, Any],
                          extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Update a draft post with retry logic."""
        url = f"{self.base_url}/blog/v3/draft-posts/{draft_post_id}"
        headers = self.headers(access_token, extra_headers)
        
        try:
            return wix_api_call_with_retry('PUT', url, headers, json_payload=payload, max_attempts=3)
        except WixAPIError as e:
            logger.error(f"Wix update_draft_post failed: HTTP {e.status_code}")
            raise
