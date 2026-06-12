from typing import Any, Dict, Optional
import requests
from urllib.parse import urlparse
from loguru import logger

from .retry import wix_api_call_with_retry, WixAPIError


def _is_valid_image_url(url: str) -> bool:
    """Check if a URL looks like a valid, publicly accessible image URL for Wix import."""
    if not url or not isinstance(url, str):
        return False
    url = url.strip()
    if url.startswith('data:'):
        return False
    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https'):
        return False
    host = parsed.hostname or ''
    if host in ('localhost', '127.0.0.1', 'example.com') or host.endswith('.example.com'):
        return False
    return True


class WixMediaService:
    """Service for Wix Media Manager operations with retry logic and error handling."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url

    def import_image(self, access_token: str, image_url: str, display_name: str,
                     client_id: Optional[str] = None, site_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Import external image to Wix Media Manager.
        
        Official endpoint: https://www.wixapis.com/site-media/v1/files/import
        Reference: https://dev.wix.com/docs/rest/assets/media/media-manager/files/import-file
        
        Args:
            access_token: Valid access token
            image_url: URL of the image to import
            display_name: Display name for the image
            client_id: Optional Wix client ID for wix-client-id header
            site_id: Optional Wix metaSiteId for wix-site-id header
            
        Returns:
            Media result dict with 'file' key, or None on failure
            
        Raises:
            WixAPIError: On non-retryable failure or after retries exhausted
        """
        if not _is_valid_image_url(image_url):
            logger.warning(f"Skipping image import — URL not valid for Wix: {image_url[:80]}...")
            return None
        
        logger.info(f"Importing image to Wix: url={image_url[:80]}..., display_name={display_name}")
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }
        if client_id:
            headers['wix-client-id'] = client_id
        if not site_id:
            from .utils import extract_meta_from_token
            meta_info = extract_meta_from_token(access_token)
            site_id = meta_info.get('metaSiteId')
        if site_id:
            headers['wix-site-id'] = site_id
        payload = {
            'url': image_url,
            'mediaType': 'IMAGE',
            'displayName': display_name,
        }
        endpoint = f"{self.base_url}/site-media/v1/files/import"
        
        try:
            result = wix_api_call_with_retry(
                'POST', endpoint, headers, json_payload=payload, max_attempts=2
            )
            if result and 'file' in result and 'id' in result['file']:
                logger.info(f"Image imported successfully: {result['file']['id'][:16]}...")
                return result
            else:
                logger.warning(f"Image import returned unexpected structure: {list(result.keys()) if isinstance(result, dict) else type(result)}")
                return None
        except WixAPIError as e:
            if e.status_code == 403:
                logger.error(f"Image import forbidden (403): OAuth app may lack MEDIA.SITE_MEDIA_FILES_IMPORT scope")
            elif e.status_code == 400:
                logger.error(f"Image import bad request (400): {e.response_body}")
            elif e.status_code == 404:
                logger.error(f"Image import endpoint not found (404) — Wix Media API may not be available for this site")
            else:
                logger.error(f"Image import failed after retries: HTTP {e.status_code} - {e.response_body}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error importing image: {e}")
            raise

    def get_image_url(self, access_token: str, media_id: str) -> Optional[str]:
        """
        Get public URL for a Wix media item.
        
        Args:
            access_token: Valid access token
            media_id: Wix media ID
            
        Returns:
            Public URL string, or None
        """
        url = f"{self.base_url}/site-media/v1/files/{media_id}"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }
        
        try:
            result = wix_api_call_with_retry('GET', url, headers, max_attempts=2)
            if result and 'file' in result:
                return result['file'].get('url')
            return None
        except Exception as e:
            logger.warning(f"Failed to get image URL for {media_id}: {e}")
            return None
