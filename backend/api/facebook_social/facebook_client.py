import os
import httpx
import secrets
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class TokenExpiredError(Exception):
    """Raised when Facebook token is expired or invalid."""
    pass

class FacebookAPIError(Exception):
    """Raised when Facebook API returns an error."""
    def __init__(self, message: str, status_code: int = None, error_code: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code

class FacebookClient:
    """
    Facebook Graph API client for OAuth and posting.
    """
    
    def __init__(self):
        self.app_id = os.getenv("FACEBOOK_APP_ID")
        self.app_secret = os.getenv("FACEBOOK_APP_SECRET")
        self.redirect_uri = os.getenv("FACEBOOK_OAUTH_REDIRECT_URI")
        self.base_url = "https://graph.facebook.com/v19.0"
        
        if not all([self.app_id, self.app_secret, self.redirect_uri]):
            logger.warning("Facebook app credentials not fully configured")
    
    def generate_oauth_url(self, state: str) -> str:
        """Generate Facebook OAuth authorization URL."""
        scopes = "pages_show_list,pages_manage_posts"
        
        params = {
            "client_id": self.app_id,
            "redirect_uri": self.redirect_uri,
            "scope": scopes,
            "response_type": "code",
            "state": state
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        oauth_url = f"https://www.facebook.com/v19.0/dialog/oauth?{query_string}"
        
        logger.info(f"Generated OAuth URL for state: {state[:20]}...")
        return oauth_url
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        logger.info("Starting token exchange for Facebook OAuth")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/oauth/access_token",
                    params={
                        "client_id": self.app_id,
                        "client_secret": self.app_secret,
                        "redirect_uri": self.redirect_uri,
                        "code": code
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    access_token = data.get("access_token")
                    expires_in = data.get("expires_in", 0)
                    
                    logger.info(f"Short-lived token obtained, expires in {expires_in} seconds")
                    
                    if access_token:
                        # Get long-lived token
                        long_lived_token = await self._get_long_lived_token(access_token)
                        if long_lived_token:
                            logger.info("Successfully obtained long-lived token")
                            return {
                                "access_token": long_lived_token["access_token"],
                                "expires_in": long_lived_token.get("expires_in", 0),
                                "token_type": "bearer"
                            }
                        else:
                            logger.warning("Long-lived token failed, using short-lived token")
                            return {
                                "access_token": access_token,
                                "expires_in": expires_in,
                                "token_type": "bearer"
                            }
                
                logger.error(f"Token exchange failed: {response.status_code} - {response.text}")
                return {}
                
        except Exception as e:
            logger.error(f"Error exchanging code for token: {str(e)}")
            return {}
    
    async def _get_long_lived_token(self, short_lived_token: str) -> Optional[Dict[str, Any]]:
        """Get long-lived access token from short-lived token."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/oauth/access_token",
                    params={
                        "grant_type": "fb_exchange_token",
                        "client_id": self.app_id,
                        "client_secret": self.app_secret,
                        "fb_exchange_token": short_lived_token
                    }
                )
                
                if response.status_code == 200:
                    return response.json()
                
                logger.warning(f"Long-lived token request failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting long-lived token: {str(e)}")
            return None
    
    async def get_user_pages(self, user_access_token: str) -> List[Dict[str, Any]]:
        """Get user's Facebook pages."""
        logger.info("Fetching user's Facebook pages")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/me/accounts",
                    params={
                        "access_token": user_access_token,
                        "fields": "id,name,access_token,category"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    pages = data.get("data", [])
                    logger.info(f"Successfully retrieved {len(pages)} Facebook pages")
                    return pages
                
                # Handle token expiration
                if response.status_code == 401:
                    error_data = response.json() if response.text else {}
                    error_message = error_data.get("error", {}).get("message", "Unauthorized")
                    logger.warning(f"Token expired or invalid: {error_message}")
                    raise TokenExpiredError("Facebook token expired or invalid")
                
                logger.error(f"Failed to get pages: {response.status_code} - {response.text}")
                return []
                
        except TokenExpiredError:
            raise
        except Exception as e:
            logger.error(f"Error getting user pages: {str(e)}")
            return []
    
    async def publish_post(self, page_id: str, page_access_token: str, message: str, link: Optional[str] = None) -> Dict[str, Any]:
        """Publish a post to a Facebook page."""
        logger.info(f"Publishing post to Facebook page {page_id}")
        try:
            post_data = {
                "message": message,
                "access_token": page_access_token
            }
            
            if link:
                post_data["link"] = link
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/{page_id}/feed",
                    data=post_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    post_id = data.get("id")
                    
                    logger.info(f"Successfully published post {post_id} to page {page_id}")
                    
                    # Get permalink URL
                    permalink = await self._get_post_permalink(post_id, page_access_token)
                    
                    return {
                        "success": True,
                        "post_id": post_id,
                        "permalink_url": permalink
                    }
                
                # Handle specific Facebook API errors
                if response.status_code == 401:
                    error_data = response.json() if response.text else {}
                    error_message = error_data.get("error", {}).get("message", "Unauthorized")
                    logger.warning(f"Token expired during publish: {error_message}")
                    raise TokenExpiredError("Facebook token expired during publishing")
                
                if response.status_code == 403:
                    error_data = response.json() if response.text else {}
                    error_message = error_data.get("error", {}).get("message", "Forbidden")
                    logger.warning(f"Permission denied for page {page_id}: {error_message}")
                    raise FacebookAPIError(f"Permission denied: {error_message}", 403)
                
                logger.error(f"Failed to publish post: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Facebook API error: {response.status_code}",
                    "details": response.text
                }
                
        except (TokenExpiredError, FacebookAPIError):
            raise
        except Exception as e:
            logger.error(f"Error publishing post: {str(e)}")
            return {
                "success": False,
                "error": f"Publishing failed: {str(e)}"
            }
    
    async def _get_post_permalink(self, post_id: str, access_token: str) -> Optional[str]:
        """Get permalink URL for a published post."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/{post_id}",
                    params={
                        "access_token": access_token,
                        "fields": "permalink_url"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("permalink_url")
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting post permalink: {str(e)}")
            return None

# Global Facebook client instance
facebook_client = FacebookClient()
