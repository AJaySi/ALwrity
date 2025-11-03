from typing import Any, Dict, List, Optional
import requests
from loguru import logger


class WixBlogService:
    def __init__(self, base_url: str, client_id: Optional[str]):
        self.base_url = base_url
        self.client_id = client_id

    def headers(self, access_token: str, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        h: Dict[str, str] = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }
        if self.client_id:
            h['wix-client-id'] = self.client_id
        if extra:
            h.update(extra)
        return h

    def create_draft_post(self, access_token: str, payload: Dict[str, Any], extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        # Log the exact payload being sent for debugging
        import json
        logger.warning(f"📤 Sending to Wix Blog API:")
        logger.warning(f"  Endpoint: {self.base_url}/blog/v3/draft-posts")
        logger.warning(f"  Payload top-level keys: {list(payload.keys())}")
        if 'draftPost' in payload:
            dp = payload['draftPost']
            logger.warning(f"  draftPost keys: {list(dp.keys())}")
            if 'richContent' in dp:
                rc = dp['richContent']
                logger.warning(f"  richContent keys: {list(rc.keys()) if isinstance(rc, dict) else 'N/A'}")
                if isinstance(rc, dict) and 'nodes' in rc:
                    nodes = rc['nodes']
                    logger.warning(f"  richContent.nodes count: {len(nodes) if isinstance(nodes, list) else 'N/A'}")
                    # Inspect first LIST_ITEM node if any
                    for i, node in enumerate(nodes[:10]):
                        if isinstance(node, dict) and node.get('type') == 'LIST_ITEM':
                            logger.warning(f"  Found LIST_ITEM at index {i}:")
                            logger.warning(f"    Keys: {list(node.keys())}")
                            logger.warning(f"    Has listItemData: {'listItemData' in node}")
                            if 'listItemData' in node:
                                logger.warning(f"    listItemData type: {type(node['listItemData'])}, value: {node['listItemData']}")
                            if 'nodes' in node:
                                nested = node['nodes']
                                logger.warning(f"    Nested nodes count: {len(nested) if isinstance(nested, list) else 'N/A'}")
                                for j, n_node in enumerate(nested[:3]):
                                    if isinstance(n_node, dict):
                                        logger.warning(f"      Nested node {j}: type={n_node.get('type')}, keys={list(n_node.keys())}")
                                        if n_node.get('type') == 'PARAGRAPH' and 'paragraphData' in n_node:
                                            logger.warning(f"        paragraphData type: {type(n_node['paragraphData'])}, value: {n_node['paragraphData']}")
                            break  # Only inspect first LIST_ITEM
        
        logger.warning(f"  Full Payload JSON (first 8000 chars):\n{json.dumps(payload, indent=2, ensure_ascii=False)[:8000]}...")
        
        response = requests.post(f"{self.base_url}/blog/v3/draft-posts", headers=self.headers(access_token, extra_headers), json=payload)
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


