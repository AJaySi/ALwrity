from typing import Any, Dict, List, Optional
import requests
from loguru import logger


class WixBlogService:
    def __init__(self, base_url: str, client_id: Optional[str]):
        self.base_url = base_url
        self.client_id = client_id

    def headers(self, access_token: str, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        h: Dict[str, str] = {
            'Content-Type': 'application/json',
        }
        
        # Support both OAuth tokens and API keys
        # API keys don't use 'Bearer' prefix
        # Ensure access_token is a string (defensive check)
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
                # CRITICAL: Wix OAuth tokens can have format "OauthNG.JWS.xxx.yyy.zzz"
                # These should use "Bearer" prefix even though they have more than 2 dots
                if token.startswith('OauthNG.JWS.'):
                    # Wix OAuth token - use Bearer prefix
                    h['Authorization'] = f'Bearer {token}'
                    logger.debug("Using Wix OAuth token with Bearer prefix (OauthNG.JWS. format detected)")
                elif '.' not in token or len(token) > 500:
                    # Likely an API key - use directly without Bearer prefix
                    h['Authorization'] = token
                    logger.debug("Using API key for authorization")
                else:
                    # Standard JWT OAuth token (xxx.yyy.zzz format) - use Bearer prefix
                    h['Authorization'] = f'Bearer {token}'
                    logger.debug("Using OAuth Bearer token for authorization")
        
        if self.client_id:
            h['wix-client-id'] = self.client_id
        if extra:
            h.update(extra)
        return h

    def create_draft_post(self, access_token: str, payload: Dict[str, Any], extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Create draft post with consolidated logging"""
        from .logger import wix_logger
        import json
        
        # Build payload summary for logging
        payload_summary = {}
        if 'draftPost' in payload:
            dp = payload['draftPost']
            payload_summary['draftPost'] = {
                'title': dp.get('title'),
                'richContent': {'nodes': len(dp.get('richContent', {}).get('nodes', []))} if 'richContent' in dp else None,
                'seoData': 'seoData' in dp
            }
        
        request_headers = self.headers(access_token, extra_headers)
        response = requests.post(f"{self.base_url}/blog/v3/draft-posts", headers=request_headers, json=payload)
        
        # Consolidated error logging
        error_body = None
        if response.status_code >= 400:
            try:
                error_body = response.json()
            except:
                error_body = {'message': response.text[:200]}
        
        wix_logger.log_api_call("POST", "/blog/v3/draft-posts", response.status_code, payload_summary, error_body)
        
        if response.status_code >= 400:
            # Only show detailed error info for debugging
            if response.status_code == 500:
                logger.debug(f"   Full error: {json.dumps(error_body, indent=2) if isinstance(error_body, dict) else error_body}")
        
        response.raise_for_status()
        return response.json()

    def publish_draft(self, access_token: str, draft_post_id: str, extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        response = requests.post(f"{self.base_url}/blog/v3/draft-posts/{draft_post_id}/publish", headers=self.headers(access_token, extra_headers))
        response.raise_for_status()
        return response.json()

    def list_categories(self, access_token: str, extra_headers: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        response = requests.get(f"{self.base_url}/blog/v3/categories", headers=self.headers(access_token, extra_headers))
        response.raise_for_status()
        return response.json().get('categories', [])

    def create_category(self, access_token: str, label: str, description: Optional[str] = None, language: Optional[str] = None, extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {'category': {'label': label}, 'fieldsets': ['URL']}
        if description:
            payload['category']['description'] = description
        if language:
            payload['category']['language'] = language
        response = requests.post(f"{self.base_url}/blog/v3/categories", headers=self.headers(access_token, extra_headers), json=payload)
        response.raise_for_status()
        return response.json()

    def list_tags(self, access_token: str, extra_headers: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        response = requests.get(f"{self.base_url}/blog/v3/tags", headers=self.headers(access_token, extra_headers))
        response.raise_for_status()
        return response.json().get('tags', [])

    def create_tag(self, access_token: str, label: str, language: Optional[str] = None, extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {'label': label, 'fieldsets': ['URL']}
        if language:
            payload['language'] = language
        response = requests.post(f"{self.base_url}/blog/v3/tags", headers=self.headers(access_token, extra_headers), json=payload)
        response.raise_for_status()
        return response.json()


