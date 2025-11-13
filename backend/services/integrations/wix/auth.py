from typing import Any, Dict, Optional, Tuple
import requests
from loguru import logger
import base64
import hashlib
import secrets


class WixAuthService:
    def __init__(self, client_id: Optional[str], redirect_uri: str, base_url: str):
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.base_url = base_url

    def generate_authorization_url(self, state: Optional[str] = None) -> Tuple[str, str]:
        if not self.client_id:
            raise ValueError("Wix client ID not configured")
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode('utf-8')).digest()
        ).decode('utf-8').rstrip('=')
        oauth_url = 'https://www.wix.com/oauth/authorize'
        from urllib.parse import urlencode
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': (
                'BLOG.CREATE-DRAFT,BLOG.PUBLISH-POST,BLOG.READ-CATEGORY,'
                'BLOG.CREATE-CATEGORY,BLOG.READ-TAG,BLOG.CREATE-TAG,'
                'MEDIA.SITE_MEDIA_FILES_IMPORT'
            ),
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256'
        }
        if state:
            params['state'] = state
        return f"{oauth_url}?{urlencode(params)}", code_verifier

    def exchange_code_for_tokens(self, code: str, code_verifier: str) -> Dict[str, Any]:
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'code_verifier': code_verifier,
        }
        token_url = f'{self.base_url}/oauth2/token'
        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()

    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': self.client_id,
        }
        token_url = f'{self.base_url}/oauth2/token'
        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()

    def get_site_info(self, access_token: str) -> Dict[str, Any]:
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        response = requests.get(f"{self.base_url}/sites/v1/site", headers=headers)
        response.raise_for_status()
        return response.json()

    def get_current_member(self, access_token: str, client_id: Optional[str]) -> Dict[str, Any]:
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        if client_id:
            headers['wix-client-id'] = client_id
        response = requests.get(f"{self.base_url}/members/v1/members/my", headers=headers)
        response.raise_for_status()
        return response.json()


