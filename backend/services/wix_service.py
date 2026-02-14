"""
Wix Integration Service

Handles authentication, permission checking, and blog publishing to Wix websites.
"""

import os
import json
import requests
import uuid
from typing import Dict, Any, Optional, List
from loguru import logger
from datetime import datetime, timedelta
import base64
from urllib.parse import urlencode, parse_qs
import jwt
import base64 as b64
from services.integrations.wix.blog import WixBlogService
from services.integrations.wix.media import WixMediaService
from services.integrations.wix.utils import extract_meta_from_token, normalize_token_string, extract_member_id_from_access_token as utils_extract_member
from services.integrations.wix.content import convert_content_to_ricos as ricos_builder
from services.integrations.wix.auth import WixAuthService
from services.integrations.wix.seo import build_seo_data
from services.integrations.wix.ricos_converter import markdown_to_html, convert_via_wix_api
from services.integrations.wix.blog_publisher import create_blog_post as publish_blog_post
from services.oauth_redirects import get_redirect_uri

class WixService:
    """Service for interacting with Wix APIs"""
    
    def __init__(self):
        self.client_id = os.getenv('WIX_CLIENT_ID')
        # Redirect URI must come from env and pass validation to avoid mixing
        # prod/stage/dev callback origins.
        try:
            self.redirect_uri = get_redirect_uri("Wix", "WIX_REDIRECT_URI")
        except ValueError as exc:
            logger.error(f"Wix OAuth redirect URI configuration error: {exc}")
            self.redirect_uri = None
        self.base_url = 'https://www.wixapis.com'
        self.oauth_url = 'https://www.wix.com/oauth/authorize'
        # Modular services
        self.blog_service = WixBlogService(self.base_url, self.client_id)
        self.media_service = WixMediaService(self.base_url)
        self.auth_service = WixAuthService(self.client_id, self.redirect_uri, self.base_url)
        
        if not self.client_id:
            logger.warning("Wix client ID not configured. Set WIX_CLIENT_ID environment variable.")
    
    def get_authorization_url(self, state: str = None) -> str:
        """
        Generate Wix OAuth authorization URL for "on behalf of user" authentication
        
        This implements the "Authenticate on behalf of a Wix User" flow as described in:
        https://dev.wix.com/docs/build-apps/develop-your-app/access/authentication/authenticate-on-behalf-of-a-wix-user
        
        Args:
            state: Optional state parameter for security
            
        Returns:
            Authorization URL for user to visit
        """
        oauth_config = self.get_oauth_config(state)
        return oauth_config["auth_url"]

    def get_oauth_config(self, state: str = None) -> Dict[str, Any]:
        """
        Generate Wix OAuth configuration (auth URL + PKCE metadata).
        """
        # Preserve existing flow by reusing WixAuthService but return the full
        # PKCE payload so the frontend can persist it for callback validation.
        if not self.redirect_uri:
            raise ValueError("Wix redirect URI is not configured.")
        oauth_config = self.auth_service.generate_authorization_url(state)
        self._code_verifier = oauth_config["code_verifier"]
        return oauth_config
    
    def _create_redirect_session_for_auth(self, redirect_uri: str, client_id: str, code_challenge: str, state: str) -> str:
        """
        Create a redirect session for Wix Headless OAuth authentication using Redirects API
        
        Args:
            redirect_uri: The redirect URI for OAuth callback
            client_id: The OAuth client ID
            code_challenge: The PKCE code challenge
            state: The OAuth state parameter
            
        Returns:
            The redirect URL for OAuth authentication
        """
        try:
            # According to Wix documentation, we need to use the Redirects API
            # to create a redirect session for OAuth authentication
            # This is the correct approach for Wix Headless OAuth
            
            # For now, return the direct OAuth URL as a fallback
            # In production, this should call the Wix Redirects API
            scope = (
                "BLOG.CREATE-DRAFT,BLOG.PUBLISH-POST,BLOG.READ-CATEGORY," \
                "BLOG.CREATE-CATEGORY,BLOG.READ-TAG,BLOG.CREATE-TAG," \
                "MEDIA.SITE_MEDIA_FILES_IMPORT"
            )
            redirect_url = (
                "https://www.wix.com/oauth/authorize?client_id="
                f"{client_id}&redirect_uri={redirect_uri}&response_type=code"
                f"&scope={scope}&code_challenge={code_challenge}"
                f"&code_challenge_method=S256&state={state}"
            )
            
            logger.info(f"Generated Wix Headless OAuth redirect URL: {redirect_url}")
            logger.warning("Using direct OAuth URL - should implement Redirects API for production")
            return redirect_url
            
        except Exception as e:
            logger.error(f"Failed to create redirect session for auth: {e}")
            raise
    
    def exchange_code_for_tokens(self, code: str, code_verifier: str = None) -> Dict[str, Any]:
        """
        Exchange authorization code for access and refresh tokens using PKCE
        
        Args:
            code: Authorization code from Wix
            code_verifier: PKCE code verifier (uses stored one if not provided)
            
        Returns:
            Token response with access_token, refresh_token, etc.
        """
        if not self.client_id:
            raise ValueError("Wix client ID not configured")
        if not code_verifier:
            code_verifier = getattr(self, '_code_verifier', None)
            if not code_verifier:
                raise ValueError("Code verifier not found. Please provide code_verifier parameter.")
        try:
            return self.auth_service.exchange_code_for_tokens(code, code_verifier)
        except requests.RequestException as e:
            logger.error(f"Failed to exchange code for tokens: {e}")
            raise
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token (Wix Headless OAuth)
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New token response
        """
        if not self.client_id:
            raise ValueError("Wix client ID not configured")
        try:
            return self.auth_service.refresh_access_token(refresh_token)
        except requests.RequestException as e:
            logger.error(f"Failed to refresh access token: {e}")
            raise
    
    def get_site_info(self, access_token: str) -> Dict[str, Any]:
        """
        Get information about the connected Wix site
        
        Args:
            access_token: Valid access token
            
        Returns:
            Site information
        """
        token_str = normalize_token_string(access_token)
        if not token_str:
            raise ValueError("Invalid access token format for create_blog_post")
        try:
            return self.auth_service.get_site_info(token_str)
        except requests.RequestException as e:
            logger.error(f"Failed to get site info: {e}")
            raise
    
    def get_current_member(self, access_token: str) -> Dict[str, Any]:
        """
        Get current member information (for third-party apps)
        
        Args:
            access_token: Valid access token
            
        Returns:
            Current member information
        """
        token_str = normalize_token_string(access_token)
        if not token_str:
            raise ValueError("Invalid access token format for get_current_member")
        try:
            return self.auth_service.get_current_member(token_str, self.client_id)
        except requests.RequestException as e:
            logger.error(f"Failed to get current member: {e}")
            raise

    def extract_member_id_from_access_token(self, access_token: Any) -> Optional[str]:
        return utils_extract_member(access_token)

    def _normalize_token_string(self, access_token: Any) -> Optional[str]:
        return normalize_token_string(access_token)
    
    def check_blog_permissions(self, access_token: str) -> Dict[str, Any]:
        """
        Check if the app has required blog permissions
        
        Args:
            access_token: Valid access token
            
        Returns:
            Permission status
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'wix-client-id': self.client_id or ''
        }
        
        try:
            # Try to list blog categories to check permissions
            response = requests.get(
                f"{self.base_url}/blog/v1/categories",
                headers=headers
            )
            
            if response.status_code == 200:
                return {
                    'has_permissions': True,
                    'can_create_posts': True,
                    'can_publish': True
                }
            elif response.status_code == 403:
                return {
                    'has_permissions': False,
                    'can_create_posts': False,
                    'can_publish': False,
                    'error': 'Insufficient permissions'
                }
            else:
                response.raise_for_status()
                
        except requests.RequestException as e:
            logger.error(f"Failed to check blog permissions: {e}")
            return {
                'has_permissions': False,
                'error': str(e)
            }
    
    def import_image_to_wix(self, access_token: str, image_url: str, display_name: str = None) -> str:
        """
        Import external image to Wix Media Manager
        
        Args:
            access_token: Valid access token
            image_url: URL of the image to import
            display_name: Optional display name for the image
            
        Returns:
            Wix media ID
        """
        try:
            result = self.media_service.import_image(
                access_token,
                image_url,
                display_name or f'Imported Image {datetime.now().strftime("%Y%m%d_%H%M%S")}'
            )

            # Wix response shape can vary (for example, `file`, `files[0]`, or nested id fields).
            file_obj = result.get('file') if isinstance(result, dict) else None
            if isinstance(file_obj, dict) and file_obj.get('id'):
                return str(file_obj['id']).strip()

            files = result.get('files') if isinstance(result, dict) else None
            if isinstance(files, list) and files:
                first = files[0]
                if isinstance(first, dict) and first.get('id'):
                    return str(first['id']).strip()

            raise ValueError(f"Wix media import succeeded but no file id returned: {result}")
        except requests.RequestException as e:
            logger.error(f"Failed to import image to Wix: {e}")
            raise
    
    def convert_content_to_ricos(self, content: str, images: List[str] = None, 
                                 use_wix_api: bool = False, access_token: str = None) -> Dict[str, Any]:
        """
        Convert markdown content to Ricos JSON format.
        
        Args:
            content: Markdown content to convert
            images: Optional list of image URLs
            use_wix_api: If True, use Wix's official Ricos Documents API (requires access_token)
            access_token: Wix access token (required if use_wix_api=True)
            
        Returns:
            Ricos JSON document
        """
        if use_wix_api and access_token:
            try:
                return convert_via_wix_api(content, access_token, self.base_url)
            except Exception as e:
                logger.warning(f"Failed to convert via Wix API, falling back to custom parser: {e}")
                # Fall back to custom parser
        
        # Use custom parser (current implementation)
        return ricos_builder(content, images)
    
    
    def create_blog_post(self, access_token: str, title: str, content: str, 
                        cover_image_url: str = None, category_ids: List[str] = None,
                        tag_ids: List[str] = None, publish: bool = True, 
                        member_id: str = None, seo_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create and optionally publish a blog post on Wix
        
        Args:
            access_token: Valid access token
            title: Blog post title
            content: Blog post content
            cover_image_url: Optional cover image URL
            category_ids: Optional list of category IDs
            tag_ids: Optional list of tag IDs
            publish: Whether to publish immediately or save as draft
            member_id: Required for third-party apps - the member ID of the post author
            seo_metadata: Optional SEO metadata dict with fields like:
                - seo_title: SEO optimized title
                - meta_description: Meta description
                - focus_keyword: Main keyword
                - blog_tags: List of tag strings (for keywords)
                - open_graph: Open Graph data
                - canonical_url: Canonical URL
            
        Returns:
            Created blog post information
        """
        # Normalize access token to string to avoid type issues (can be dict/int from storage)
        from services.integrations.wix.utils import normalize_token_string
        normalized_token = normalize_token_string(access_token)
        if normalized_token:
            token_to_use = normalized_token.strip()
        else:
            token_to_use = str(access_token).strip() if access_token is not None else ""
        
        if not token_to_use:
            raise ValueError("access_token is required to create a blog post")

        return publish_blog_post(
            blog_service=self.blog_service,
            access_token=token_to_use,
            title=title,
            content=content,
            member_id=member_id,
            cover_image_url=cover_image_url,
            category_ids=category_ids,
            tag_ids=tag_ids,
            publish=publish,
            seo_metadata=seo_metadata,
            import_image_func=self.import_image_to_wix,
            lookup_categories_func=self.lookup_or_create_categories,
            lookup_tags_func=self.lookup_or_create_tags,
            base_url=self.base_url
        )
    
    def get_blog_categories(self, access_token: str) -> List[Dict[str, Any]]:
        """
        Get available blog categories
        
        Args:
            access_token: Valid access token
            
        Returns:
            List of blog categories
        """
        try:
            return self.blog_service.list_categories(access_token)
        except requests.RequestException as e:
            logger.error(f"Failed to get blog categories: {e}")
            raise
    
    def get_blog_tags(self, access_token: str) -> List[Dict[str, Any]]:
        """
        Get available blog tags
        
        Args:
            access_token: Valid access token
            
        Returns:
            List of blog tags
        """
        try:
            return self.blog_service.list_tags(access_token)
        except requests.RequestException as e:
            logger.error(f"Failed to get blog tags: {e}")
            raise
    
    def lookup_or_create_categories(self, access_token: str, category_names: List[str], 
                                    extra_headers: Optional[Dict[str, str]] = None) -> List[str]:
        """
        Lookup existing categories by name or create new ones, return their IDs.
        
        Args:
            access_token: Valid access token
            category_names: List of category name strings
            extra_headers: Optional extra headers (e.g., wix-site-id)
            
        Returns:
            List of category UUIDs
        """
        if not category_names:
            return []
        
        try:
            # Get existing categories
            existing_categories = self.blog_service.list_categories(access_token, extra_headers)
            
            # Create name -> ID mapping (case-insensitive)
            category_map = {}
            for cat in existing_categories:
                cat_label = cat.get('label', '').strip()
                cat_id = cat.get('id')
                if cat_label and cat_id:
                    category_map[cat_label.lower()] = cat_id
            
            category_ids = []
            for category_name in category_names:
                category_name_clean = str(category_name).strip()
                if not category_name_clean:
                    continue
                
                # Lookup existing category (case-insensitive)
                category_id = category_map.get(category_name_clean.lower())
                
                if not category_id:
                    # Create new category
                    try:
                        logger.info(f"Creating new category: {category_name_clean}")
                        result = self.blog_service.create_category(
                            access_token, 
                            label=category_name_clean,
                            extra_headers=extra_headers
                        )
                        new_category = result.get('category', {})
                        category_id = new_category.get('id')
                        if category_id:
                            category_ids.append(category_id)
                            # Update map to avoid duplicate creates
                            category_map[category_name_clean.lower()] = category_id
                            logger.info(f"Created category '{category_name_clean}' with ID: {category_id}")
                    except Exception as create_error:
                        logger.warning(f"Failed to create category '{category_name_clean}': {create_error}")
                        # Continue with other categories
                else:
                    category_ids.append(category_id)
                    logger.info(f"Found existing category '{category_name_clean}' with ID: {category_id}")
            
            return category_ids
            
        except requests.RequestException as e:
            logger.error(f"Failed to lookup/create categories: {e}")
            return []
    
    def lookup_or_create_tags(self, access_token: str, tag_names: List[str],
                             extra_headers: Optional[Dict[str, str]] = None) -> List[str]:
        """
        Lookup existing tags by name or create new ones, return their IDs.
        
        Args:
            access_token: Valid access token
            tag_names: List of tag name strings
            extra_headers: Optional extra headers (e.g., wix-site-id)
            
        Returns:
            List of tag UUIDs
        """
        if not tag_names:
            return []
        
        try:
            # Get existing tags
            existing_tags = self.blog_service.list_tags(access_token, extra_headers)
            
            # Create name -> ID mapping (case-insensitive)
            tag_map = {}
            for tag in existing_tags:
                tag_label = tag.get('label', '').strip()
                tag_id = tag.get('id')
                if tag_label and tag_id:
                    tag_map[tag_label.lower()] = tag_id
            
            tag_ids = []
            for tag_name in tag_names:
                tag_name_clean = str(tag_name).strip()
                if not tag_name_clean:
                    continue
                
                # Lookup existing tag (case-insensitive)
                tag_id = tag_map.get(tag_name_clean.lower())
                
                if not tag_id:
                    # Create new tag
                    try:
                        logger.info(f"Creating new tag: {tag_name_clean}")
                        result = self.blog_service.create_tag(
                            access_token,
                            label=tag_name_clean,
                            extra_headers=extra_headers
                        )
                        new_tag = result.get('tag', {})
                        tag_id = new_tag.get('id')
                        if tag_id:
                            tag_ids.append(tag_id)
                            # Update map to avoid duplicate creates
                            tag_map[tag_name_clean.lower()] = tag_id
                            logger.info(f"Created tag '{tag_name_clean}' with ID: {tag_id}")
                    except Exception as create_error:
                        logger.warning(f"Failed to create tag '{tag_name_clean}': {create_error}")
                        # Continue with other tags
                else:
                    tag_ids.append(tag_id)
                    logger.info(f"Found existing tag '{tag_name_clean}' with ID: {tag_id}")
            
            return tag_ids
            
        except requests.RequestException as e:
            logger.error(f"Failed to lookup/create tags: {e}")
            return []

    def publish_draft_post(self, access_token: str, draft_post_id: str) -> Dict[str, Any]:
        """
        Publish a draft post by ID.
        """
        try:
            result = self.blog_service.publish_draft(access_token, draft_post_id)
            logger.info(f"DEBUG: Publish result: {result}")
            return result
        except requests.RequestException as e:
            logger.error(f"Failed to publish draft post: {e}")
            raise

    def create_category(self, access_token: str, label: str, description: Optional[str] = None,
                         language: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a blog category.
        """
        try:
            return self.blog_service.create_category(access_token, label, description, language)
        except requests.RequestException as e:
            logger.error(f"Failed to create category: {e}")
            raise

    def create_tag(self, access_token: str, label: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a blog tag.
        """
        try:
            return self.blog_service.create_tag(access_token, label, language)
        except requests.RequestException as e:
            logger.error(f"Failed to create tag: {e}")
            raise
