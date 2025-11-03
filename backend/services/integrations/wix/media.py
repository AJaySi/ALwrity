from typing import Any, Dict
import requests


class WixMediaService:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def import_image(self, access_token: str, image_url: str, display_name: str) -> Dict[str, Any]:
        """
        Import external image to Wix Media Manager.
        
        Official endpoint: https://www.wixapis.com/site-media/v1/files/import
        Reference: https://dev.wix.com/docs/rest/assets/media/media-manager/files/import-file
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }
        payload = {
            'url': image_url,
            'mediaType': 'IMAGE',
            'displayName': display_name,
        }
        # Correct endpoint per Wix API documentation
        endpoint = f"{self.base_url}/site-media/v1/files/import"
        response = requests.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()


