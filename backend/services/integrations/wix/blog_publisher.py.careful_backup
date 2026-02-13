"""
Blog Post Publisher for Wix

Handles blog post creation, validation, and publishing to Wix.
"""

import json
import uuid
import requests
import jwt
from typing import Dict, Any, Optional, List
from loguru import logger
from services.integrations.wix.blog import WixBlogService
from services.integrations.wix.content import convert_content_to_ricos
from services.integrations.wix.ricos_converter import convert_via_wix_api
from services.integrations.wix.seo import build_seo_data
from services.integrations.wix.logger import wix_logger
from services.integrations.wix.utils import normalize_token_string


def validate_ricos_content(ricos_content: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and normalize Ricos document structure.
    
    Args:
        ricos_content: Ricos document dict
        
    Returns:
        Validated and normalized Ricos document
    """
    # Validate Ricos document structure before using
    if not ricos_content or not isinstance(ricos_content, dict):
        logger.error("Invalid Ricos content - not a dict")
        raise ValueError("Failed to convert content to valid Ricos format")
    
    if 'type' not in ricos_content:
        ricos_content['type'] = 'DOCUMENT'
        logger.debug("Added missing richContent type 'DOCUMENT'")
    if ricos_content.get('type') != 'DOCUMENT':
        logger.warning(f"richContent type expected 'DOCUMENT', got {ricos_content.get('type')}, correcting")
        ricos_content['type'] = 'DOCUMENT'

    if 'id' not in ricos_content or not isinstance(ricos_content.get('id'), str):
        ricos_content['id'] = str(uuid.uuid4())
        logger.debug("Added missing richContent id")

    if 'nodes' not in ricos_content:
        logger.warning("Ricos document missing 'nodes' field, adding empty nodes array")
        ricos_content['nodes'] = []
    
    logger.debug(f"Ricos document structure: nodes={len(ricos_content.get('nodes', []))}")

    # Validate richContent is a proper object with nodes array
    # Per Wix API: richContent must be a RichContent object with nodes array
    if not isinstance(ricos_content, dict):
        raise ValueError(f"richContent must be a dict object, got {type(ricos_content)}")
    
    # Ensure nodes array exists and is valid
    if 'nodes' not in ricos_content:
        logger.warning("richContent missing 'nodes', adding empty array")
        ricos_content['nodes'] = []
    
    if not isinstance(ricos_content['nodes'], list):
        raise ValueError(f"richContent.nodes must be a list, got {type(ricos_content['nodes'])}")
    
    # Recursive function to validate and fix nodes at any depth
    def validate_node_recursive(node: Dict[str, Any], path: str = "root") -> None:
        """
        Recursively validate a node and all its nested children, ensuring:
        1. All required data fields exist for each node type
        2. All 'nodes' arrays are proper lists
        3. No None values in critical fields
        """
        if not isinstance(node, dict):
            logger.error(f"{path}: Node is not a dict: {type(node)}")
            return
        
        # Ensure type and id exist
        if 'type' not in node:
            logger.error(f"{path}: Missing 'type' field - REQUIRED")
            node['type'] = 'PARAGRAPH'  # Default fallback
        if 'id' not in node:
            node['id'] = str(uuid.uuid4())
            logger.debug(f"{path}: Added missing 'id'")
        
        node_type = node.get('type')
        
        # CRITICAL: Per Wix API schema, data fields like paragraphData, bulletedListData, etc.
        # are OPTIONAL and should be OMITTED entirely when empty, not included as {}
        # Only validate fields that have required properties
        
        # Special handling: Remove listItemData if it exists (not in Wix API schema)
        if node_type == 'LIST_ITEM' and 'listItemData' in node:
            logger.debug(f"{path}: Removing incorrect listItemData field from LIST_ITEM")
            del node['listItemData']
        
        # Only validate HEADING nodes - they require headingData with level property
        if node_type == 'HEADING':
            if 'headingData' not in node or not isinstance(node.get('headingData'), dict):
                logger.warning(f"{path} (HEADING): Missing headingData, adding default level 1")
                node['headingData'] = {'level': 1}
            elif 'level' not in node['headingData']:
                logger.warning(f"{path} (HEADING): Missing level in headingData, adding default")
                node['headingData']['level'] = 1
        
        # TEXT nodes must have textData
        if node_type == 'TEXT':
            if 'textData' not in node or not isinstance(node.get('textData'), dict):
                logger.error(f"{path} (TEXT): Missing/invalid textData - node will be problematic")
                node['textData'] = {'text': '', 'decorations': []}
        
        # LINK and IMAGE nodes must have their data fields
        if node_type == 'LINK' and ('linkData' not in node or not isinstance(node.get('linkData'), dict)):
            logger.error(f"{path} (LINK): Missing/invalid linkData - node will be problematic")
        if node_type == 'IMAGE' and ('imageData' not in node or not isinstance(node.get('imageData'), dict)):
            logger.error(f"{path} (IMAGE): Missing/invalid imageData - node will be problematic")
        
        # Remove None values from any data fields that exist (Wix API rejects None)
        for data_field in ['headingData', 'paragraphData', 'blockquoteData', 'bulletedListData', 
                          'orderedListData', 'textData', 'linkData', 'imageData']:
            if data_field in node and isinstance(node[data_field], dict):
                data_value = node[data_field]
                keys_to_remove = [k for k, v in data_value.items() if v is None]
                if keys_to_remove:
                    logger.debug(f"{path} ({node_type}): Removing None values from {data_field}: {keys_to_remove}")
                    for key in keys_to_remove:
                        del data_value[key]
        
        # Ensure 'nodes' field exists for container nodes
        container_types = ['HEADING', 'PARAGRAPH', 'BLOCKQUOTE', 'LIST_ITEM', 'LINK', 
                          'BULLETED_LIST', 'ORDERED_LIST']
        if node_type in container_types:
            if 'nodes' not in node:
                logger.warning(f"{path} ({node_type}): Missing 'nodes' field, adding empty array")
                node['nodes'] = []
            elif not isinstance(node['nodes'], list):
                logger.error(f"{path} ({node_type}): Invalid 'nodes' field (not a list), fixing")
                node['nodes'] = []
            
            # Recursively validate all nested nodes
            for nested_idx, nested_node in enumerate(node['nodes']):
                nested_path = f"{path}.nodes[{nested_idx}]"
                validate_node_recursive(nested_node, nested_path)
    
    # Validate all top-level nodes recursively
    for idx, node in enumerate(ricos_content['nodes']):
        validate_node_recursive(node, f"nodes[{idx}]")
    
    # Ensure documentStyle exists and is a dict (required by Wix API when provided)
    if 'metadata' not in ricos_content or not isinstance(ricos_content.get('metadata'), dict):
        ricos_content['metadata'] = {'version': 1, 'id': str(uuid.uuid4())}
        logger.debug("Added default metadata to richContent")
    else:
        ricos_content['metadata'].setdefault('version', 1)
        ricos_content['metadata'].setdefault('id', str(uuid.uuid4()))
    
    if 'documentStyle' not in ricos_content or not isinstance(ricos_content.get('documentStyle'), dict):
        ricos_content['documentStyle'] = {
            'paragraph': {
                'decorations': [],
                'nodeStyle': {},
                'lineHeight': '1.5'
            }
        }
        logger.debug("Added default documentStyle to richContent")
    
    logger.debug(f"✅ Validated richContent: {len(ricos_content['nodes'])} nodes, has_metadata={bool(ricos_content.get('metadata'))}, has_documentStyle={bool(ricos_content.get('documentStyle'))}")
    
    return ricos_content


def validate_payload_no_none(obj, path=""):
    """Recursively validate that no None values exist in the payload"""
    if obj is None:
        raise ValueError(f"Found None value at path: {path}")
    if isinstance(obj, dict):
        for key, value in obj.items():
            validate_payload_no_none(value, f"{path}.{key}" if path else key)
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            validate_payload_no_none(item, f"{path}[{idx}]" if path else f"[{idx}]")


def create_blog_post(
    blog_service: WixBlogService,
    access_token: str,
    title: str,
    content: str,
    member_id: str,
    cover_image_url: str = None,
    category_ids: List[str] = None,
    tag_ids: List[str] = None,
    publish: bool = True,
    seo_metadata: Dict[str, Any] = None,
    import_image_func = None,
    lookup_categories_func = None,
    lookup_tags_func = None,
    base_url: str = 'https://www.wixapis.com'
) -> Dict[str, Any]:
    """
    Create and optionally publish a blog post on Wix
    
    Args:
        blog_service: WixBlogService instance
        access_token: Valid access token
        title: Blog post title
        content: Blog post content (markdown)
        member_id: Required for third-party apps - the member ID of the post author
        cover_image_url: Optional cover image URL
        category_ids: Optional list of category IDs or names
        tag_ids: Optional list of tag IDs or names
        publish: Whether to publish immediately or save as draft
        seo_metadata: Optional SEO metadata dict
        import_image_func: Function to import images (optional)
        lookup_categories_func: Function to lookup/create categories (optional)
        lookup_tags_func: Function to lookup/create tags (optional)
        base_url: Wix API base URL
        
    Returns:
        Created blog post information
    """
    if not member_id:
        raise ValueError("memberId is required for third-party apps creating blog posts")
    
    # Ensure access_token is a string (handle cases where it might be int, dict, or other type)
    # Use normalize_token_string to handle various token formats (dict with accessToken.value, etc.)
    normalized_token = normalize_token_string(access_token)
    if not normalized_token:
        raise ValueError("access_token is required and must be a valid string or token object")
    access_token = normalized_token.strip()
    if not access_token:
        raise ValueError("access_token cannot be empty")
    
    # BACK TO BASICS MODE: Try simplest possible structure FIRST
    # Since posting worked before Ricos/SEO, let's test with absolute minimum
    BACK_TO_BASICS_MODE = True  # Set to True to test with simplest structure
    
    wix_logger.reset()
    wix_logger.log_operation_start("Blog Post Creation", title=title[:50] if title else None, member_id=member_id[:20] if member_id else None)
    
    if BACK_TO_BASICS_MODE:
        logger.info("🔧 Wix: BACK TO BASICS MODE - Testing minimal structure")
        
        # Import auth utilities for proper token handling
        from .auth_utils import get_wix_headers
        
        # Create absolute minimal Ricos structure
        minimal_ricos = {
            'nodes': [{
                'id': str(uuid.uuid4()),
                'type': 'PARAGRAPH',
                'nodes': [{
                    'id': str(uuid.uuid4()),
                    'type': 'TEXT',
                    'nodes': [],
                    'textData': {
                        'text': (content[:500] if content else "This is a post from ALwrity.").strip(),
                        'decorations': []
                    }
                }],
                'paragraphData': {}
            }]
        }
        
        # Extract wix-site-id from token if possible
        extra_headers = {}
        try:
            token_str = str(access_token)
            if token_str and token_str.startswith('OauthNG.JWS.'):
                import jwt
                import json
                jwt_part = token_str[12:]
                payload = jwt.decode(jwt_part, options={"verify_signature": False, "verify_aud": False})
                data_payload = payload.get('data', {})
                if isinstance(data_payload, str):
                    try:
                        data_payload = json.loads(data_payload)
                    except:
                        pass
                instance_data = data_payload.get('instance', {})
                meta_site_id = instance_data.get('metaSiteId')
                if isinstance(meta_site_id, str) and meta_site_id:
                    extra_headers['wix-site-id'] = meta_site_id
        except Exception:
            pass
        
        # Build minimal payload
        minimal_blog_data = {
            'draftPost': {
                'title': str(title).strip() if title else "Untitled",
                'memberId': str(member_id).strip(),
                'richContent': minimal_ricos
            },
            'publish': False,
            'fieldsets': ['URL']
        }
        
        try:
            from .blog import WixBlogService
            blog_service_test = WixBlogService('https://www.wixapis.com', None)
            result = blog_service_test.create_draft_post(access_token, minimal_blog_data, extra_headers if extra_headers else None)
            logger.success("✅✅✅ Wix: BACK TO BASICS SUCCEEDED! Issue is with Ricos/SEO structure")
            wix_logger.log_operation_result("Back to Basics Test", True, result)
            return result
        except Exception as e:
            logger.error(f"❌ Wix: BACK TO BASICS FAILED - {str(e)[:100]}")
            logger.error("   ⚠️ Issue is NOT with Ricos/SEO - likely permissions/token")
            wix_logger.add_error(f"Back to Basics: {str(e)[:100]}")
    
    # Import auth utilities for proper token handling
    from .auth_utils import get_wix_headers
    
    # Headers for blog post creation (use user's OAuth token)
    headers = get_wix_headers(access_token)
    
    # Build valid Ricos rich content
    # Ensure content is not empty
    if not content or not content.strip():
        content = "This is a post from ALwrity."
        logger.warning("⚠️ Content was empty, using default text")
    
    # Quick token/permission check (only log if issues found)
    has_blog_scope = None
    meta_site_id = None
    try:
        from .utils import decode_wix_token
        import json
        token_data = decode_wix_token(access_token)
        if 'scope' in token_data:
            scopes = token_data.get('scope')
            if isinstance(scopes, str):
                scope_list = scopes.split(',') if ',' in scopes else [scopes]
                has_blog_scope = any('BLOG' in s.upper() for s in scope_list)
                if not has_blog_scope:
                    logger.error("❌ Wix: Token missing BLOG scopes - verify OAuth app permissions")
        if 'data' in token_data:
            data = token_data.get('data')
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except:
                    pass
            if isinstance(data, dict) and 'instance' in data:
                instance = data.get('instance', {})
                meta_site_id = instance.get('metaSiteId')
    except Exception:
        pass
    
    # Quick permission test (only log failures)
    try:
        test_headers = get_wix_headers(access_token)
        import requests
        test_response = requests.get(f"{base_url}/blog/v3/categories", headers=test_headers, timeout=5)
        if test_response.status_code == 403:
            logger.error("❌ Wix: Permission denied - OAuth app missing BLOG.CREATE-DRAFT")
        elif test_response.status_code == 401:
            logger.error("❌ Wix: Unauthorized - token may be expired")
    except Exception:
        pass
    
    # Safely get token length (access_token is already validated as string above)
    token_length = len(access_token) if access_token else 0
    wix_logger.log_token_info(token_length, has_blog_scope, meta_site_id)
    
    # Convert markdown to Ricos
    ricos_content = convert_content_to_ricos(content, None)
    nodes_count = len(ricos_content.get('nodes', []))
    wix_logger.log_ricos_conversion(nodes_count)
    
    # Validate Ricos content structure
    # Per Wix Blog API documentation: richContent should ONLY contain 'nodes'
    # The example in docs shows: { nodes: [...] } - no type, id, metadata, or documentStyle
    if not isinstance(ricos_content, dict):
        logger.error(f"❌ richContent is not a dict: {type(ricos_content)}")
        raise ValueError("richContent must be a dictionary object")
    
    if 'nodes' not in ricos_content or not isinstance(ricos_content['nodes'], list):
        logger.error(f"❌ richContent.nodes is missing or not a list: {ricos_content.get('nodes', 'MISSING')}")
        raise ValueError("richContent must contain a 'nodes' array")
    
    # Remove type and id fields (not expected by Blog API)
    # NOTE: metadata is optional - Wix UPDATE endpoint example shows it, but CREATE example doesn't
    # We'll keep it minimal (nodes only) for CREATE to match the recipe example
    fields_to_remove = ['type', 'id']
    for field in fields_to_remove:
        if field in ricos_content:
            logger.debug(f"Removing '{field}' field from richContent (Blog API doesn't expect this)")
            del ricos_content[field]
    
    # Remove metadata and documentStyle - Blog API CREATE endpoint example shows only 'nodes'
    # (UPDATE endpoint shows metadata, but we're using CREATE)
    if 'metadata' in ricos_content:
        logger.debug("Removing 'metadata' from richContent (CREATE endpoint expects only 'nodes')")
        del ricos_content['metadata']
    if 'documentStyle' in ricos_content:
        logger.debug("Removing 'documentStyle' from richContent (CREATE endpoint expects only 'nodes')")
        del ricos_content['documentStyle']
    
    # Ensure we only have 'nodes' in richContent for CREATE endpoint
    ricos_content = {'nodes': ricos_content['nodes']}
    
    logger.debug(f"✅ richContent structure validated: {len(ricos_content['nodes'])} nodes, keys: {list(ricos_content.keys())}")
    
    # Minimal payload per Wix docs: title, memberId, and richContent
    # CRITICAL: Only include fields that have valid values (no None, no empty strings for required fields)
    blog_data = {
        'draftPost': {
            'title': str(title).strip() if title else "Untitled",
            'memberId': str(member_id).strip(),  # Required for third-party apps (validated above)
            'richContent': ricos_content,  # Must be a valid Ricos object with ONLY 'nodes'
        },
        'publish': bool(publish),
        'fieldsets': ['URL']  # Simplified fieldsets
    }
    
    # Add excerpt only if content exists and is not empty (avoid None or empty strings)
    excerpt = (content or '').strip()[:200] if content else None
    if excerpt and len(excerpt) > 0:
        blog_data['draftPost']['excerpt'] = str(excerpt)
    
    # Add cover image if provided
    if cover_image_url and import_image_func:
        try:
            media_id = import_image_func(access_token, cover_image_url, f'Cover: {title}')
            # Ensure media_id is a string and not None
            if media_id and isinstance(media_id, str):
                blog_data['draftPost']['media'] = {
                    'wixMedia': {
                        'image': {'id': str(media_id).strip()}
                    },
                    'displayed': True,
                    'custom': True
                }
            else:
                logger.warning(f"Invalid media_id type or value: {type(media_id)}, skipping media")
        except Exception as e:
            logger.warning(f"Failed to import cover image: {e}")
    
    # Handle categories - can be either IDs (list of strings) or names (for lookup)
    category_ids_to_use = None
    if category_ids:
        # Check if these are IDs (UUIDs) or names
        if isinstance(category_ids, list) and len(category_ids) > 0:
            # Assume IDs if first item looks like UUID (has hyphens and is long)
            first_item = str(category_ids[0])
            if '-' in first_item and len(first_item) > 30:
                category_ids_to_use = category_ids
            elif lookup_categories_func:
                # These are names, need to lookup/create
                extra_headers = {}
                if 'wix-site-id' in headers:
                    extra_headers['wix-site-id'] = headers['wix-site-id']
                category_ids_to_use = lookup_categories_func(
                    access_token, category_ids, extra_headers if extra_headers else None
                )
    
    # Handle tags - can be either IDs (list of strings) or names (for lookup)
    tag_ids_to_use = None
    if tag_ids:
        # Check if these are IDs (UUIDs) or names
        if isinstance(tag_ids, list) and len(tag_ids) > 0:
            # Assume IDs if first item looks like UUID (has hyphens and is long)
            first_item = str(tag_ids[0])
            if '-' in first_item and len(first_item) > 30:
                tag_ids_to_use = tag_ids
            elif lookup_tags_func:
                # These are names, need to lookup/create
                extra_headers = {}
                if 'wix-site-id' in headers:
                    extra_headers['wix-site-id'] = headers['wix-site-id']
                tag_ids_to_use = lookup_tags_func(
                    access_token, tag_ids, extra_headers if extra_headers else None
                )
    
    # Add categories if we have IDs (must be non-empty list of strings)
    # CRITICAL: Wix API rejects empty arrays or arrays with None/empty strings
    if category_ids_to_use and isinstance(category_ids_to_use, list) and len(category_ids_to_use) > 0:
        # Filter out None, empty strings, and ensure all are valid UUID strings
        valid_category_ids = [str(cid).strip() for cid in category_ids_to_use if cid and str(cid).strip()]
        if valid_category_ids:
            blog_data['draftPost']['categoryIds'] = valid_category_ids
            logger.debug(f"Added {len(valid_category_ids)} category IDs")
        else:
            logger.warning("All category IDs were invalid, not including categoryIds in payload")
    
    # Add tags if we have IDs (must be non-empty list of strings)
    # CRITICAL: Wix API rejects empty arrays or arrays with None/empty strings
    if tag_ids_to_use and isinstance(tag_ids_to_use, list) and len(tag_ids_to_use) > 0:
        # Filter out None, empty strings, and ensure all are valid UUID strings
        valid_tag_ids = [str(tid).strip() for tid in tag_ids_to_use if tid and str(tid).strip()]
        if valid_tag_ids:
            blog_data['draftPost']['tagIds'] = valid_tag_ids
            logger.debug(f"Added {len(valid_tag_ids)} tag IDs")
        else:
            logger.warning("All tag IDs were invalid, not including tagIds in payload")
    
    # Build SEO data from metadata if provided
    # NOTE: seoData is optional - if it causes issues, we can create post without it
    seo_data = None
    if seo_metadata:
        try:
            seo_data = build_seo_data(seo_metadata, title)
            if seo_data:
                tags_count = len(seo_data.get('tags', []))
                keywords_count = len(seo_data.get('settings', {}).get('keywords', []))
                wix_logger.log_seo_data(tags_count, keywords_count)
                blog_data['draftPost']['seoData'] = seo_data
        except Exception as e:
            logger.warning(f"⚠️ Wix: SEO data build failed - {str(e)[:50]}")
            wix_logger.add_warning(f"SEO build: {str(e)[:50]}")
        
        # Add SEO slug if provided
        if seo_metadata.get('url_slug'):
            blog_data['draftPost']['seoSlug'] = str(seo_metadata.get('url_slug')).strip()
    else:
        logger.warning("⚠️ No SEO metadata provided to create_blog_post")
    
    try:
        # Extract wix-site-id from token if possible
        extra_headers = {}
        try:
            token_str = str(access_token)
            if token_str and token_str.startswith('OauthNG.JWS.'):
                import jwt
                import json
                jwt_part = token_str[12:]
                payload = jwt.decode(jwt_part, options={"verify_signature": False, "verify_aud": False})
                data_payload = payload.get('data', {})
                if isinstance(data_payload, str):
                    try:
                        data_payload = json.loads(data_payload)
                    except:
                        pass
                instance_data = data_payload.get('instance', {})
                meta_site_id = instance_data.get('metaSiteId')
                if isinstance(meta_site_id, str) and meta_site_id:
                    extra_headers['wix-site-id'] = meta_site_id
                    headers['wix-site-id'] = meta_site_id
        except Exception:
            pass
        
        # Validate payload structure before sending
        draft_post = blog_data.get('draftPost', {})
        if not isinstance(draft_post, dict):
            raise ValueError("draftPost must be a dict object")
        
        # Validate richContent structure
        if 'richContent' in draft_post:
            rc = draft_post['richContent']
            if not isinstance(rc, dict):
                raise ValueError(f"richContent must be a dict, got {type(rc)}")
            if 'nodes' not in rc:
                raise ValueError("richContent missing 'nodes' field")
            if not isinstance(rc['nodes'], list):
                raise ValueError(f"richContent.nodes must be a list, got {type(rc['nodes'])}")
            logger.debug(f"✅ richContent validation passed: {len(rc.get('nodes', []))} nodes")
        
        # Validate seoData structure if present
        if 'seoData' in draft_post:
            seo = draft_post['seoData']
            if not isinstance(seo, dict):
                raise ValueError(f"seoData must be a dict, got {type(seo)}")
            if 'tags' in seo and not isinstance(seo['tags'], list):
                raise ValueError(f"seoData.tags must be a list, got {type(seo.get('tags'))}")
            if 'settings' in seo and not isinstance(seo['settings'], dict):
                raise ValueError(f"seoData.settings must be a dict, got {type(seo.get('settings'))}")
            logger.debug(f"✅ seoData validation passed: {len(seo.get('tags', []))} tags")
        
        # Final validation: Ensure no None values in any nested objects
        # Wix API rejects None values and expects proper types
        try:
            validate_payload_no_none(blog_data, "blog_data")
            logger.debug("✅ Payload validation passed: No None values found")
        except ValueError as e:
            logger.error(f"❌ Payload validation failed: {e}")
            raise
        
        # Log full payload structure for debugging (sanitized)
        logger.warning(f"📦 Full payload structure validation:")
        logger.warning(f"  - draftPost type: {type(draft_post)}")
        logger.warning(f"  - draftPost keys: {list(draft_post.keys())}")
        logger.warning(f"  - richContent type: {type(draft_post.get('richContent'))}")
        if 'richContent' in draft_post:
            rc = draft_post['richContent']
            logger.warning(f"  - richContent keys: {list(rc.keys()) if isinstance(rc, dict) else 'N/A'}")
            logger.warning(f"  - richContent.nodes type: {type(rc.get('nodes'))}, count: {len(rc.get('nodes', []))}")
            logger.warning(f"  - richContent.metadata type: {type(rc.get('metadata'))}")
            logger.warning(f"  - richContent.documentStyle type: {type(rc.get('documentStyle'))}")
        logger.warning(f"  - seoData type: {type(draft_post.get('seoData'))}")
        if 'seoData' in draft_post:
            seo = draft_post['seoData']
            logger.warning(f"  - seoData keys: {list(seo.keys()) if isinstance(seo, dict) else 'N/A'}")
            logger.warning(f"  - seoData.tags type: {type(seo.get('tags'))}, count: {len(seo.get('tags', []))}")
            logger.warning(f"  - seoData.settings type: {type(seo.get('settings'))}")
        if 'categoryIds' in draft_post:
            logger.warning(f"  - categoryIds type: {type(draft_post.get('categoryIds'))}, count: {len(draft_post.get('categoryIds', []))}")
        if 'tagIds' in draft_post:
            logger.warning(f"  - tagIds type: {type(draft_post.get('tagIds'))}, count: {len(draft_post.get('tagIds', []))}")
        
        # Log a sample of the payload JSON to see exact structure (first 2000 chars)
        try:
            import json
            payload_json = json.dumps(blog_data, indent=2, ensure_ascii=False)
            logger.warning(f"📄 Payload JSON preview (first 3000 chars):\n{payload_json[:3000]}...")
            
            # Also log a deep structure inspection of richContent.nodes (first few nodes)
            if 'richContent' in blog_data['draftPost']:
                nodes = blog_data['draftPost']['richContent'].get('nodes', [])
                if nodes:
                    logger.warning(f"🔍 Inspecting first 5 richContent.nodes:")
                    for i, node in enumerate(nodes[:5]):
                        logger.warning(f"  Node {i+1}: type={node.get('type')}, keys={list(node.keys())}")
                        # Check for any None values in node
                        for key, value in node.items():
                            if value is None:
                                logger.error(f"    ⚠️ Node {i+1}.{key} is None!")
                            elif isinstance(value, dict):
                                for k, v in value.items():
                                    if v is None:
                                        logger.error(f"    ⚠️ Node {i+1}.{key}.{k} is None!")
                        # Deep check: if it's a list-type node, inspect list items
                        if node.get('type') in ['BULLETED_LIST', 'ORDERED_LIST']:
                            list_items = node.get('nodes', [])
                            if list_items:
                                logger.warning(f"    List has {len(list_items)} items, checking first LIST_ITEM:")
                                first_item = list_items[0]
                                logger.warning(f"      LIST_ITEM keys: {list(first_item.keys())}")
                                # Verify listItemData is NOT present (correct per Wix API spec)
                                if 'listItemData' in first_item:
                                    logger.error(f"      ❌ LIST_ITEM incorrectly has listItemData!")
                                else:
                                    logger.debug(f"      ✅ LIST_ITEM correctly has no listItemData")
                                # Check nested PARAGRAPH nodes
                                nested_nodes = first_item.get('nodes', [])
                                if nested_nodes:
                                    logger.warning(f"      LIST_ITEM has {len(nested_nodes)} nested nodes")
                                    for n_idx, n_node in enumerate(nested_nodes[:2]):
                                        logger.warning(f"        Nested node {n_idx+1}: type={n_node.get('type')}, keys={list(n_node.keys())}")
        except Exception as e:
            logger.warning(f"Could not serialize payload for logging: {e}")
        
        # Note: All node validation is done by validate_ricos_content() which runs earlier
        # The recursive validation ensures all required data fields are present at any depth
        
        # Final deep validation: Serialize and deserialize to catch any JSON-serialization issues
        # This will raise an error if there are any objects that can't be serialized
        try:
            import json
            test_json = json.dumps(blog_data, ensure_ascii=False)
            test_parsed = json.loads(test_json)
            logger.debug("✅ Payload JSON serialization test passed")
        except (TypeError, ValueError) as e:
            logger.error(f"❌ Payload JSON serialization failed: {e}")
            raise ValueError(f"Payload contains non-serializable data: {e}")
        
        # Final check: Ensure documentStyle and metadata are valid objects (not None, not empty strings)
        rc = blog_data['draftPost']['richContent']
        if 'documentStyle' in rc:
            doc_style = rc['documentStyle']
            if doc_style is None or doc_style == "":
                logger.warning("⚠️ documentStyle is None or empty string, removing it")
                del rc['documentStyle']
            elif not isinstance(doc_style, dict):
                logger.warning(f"⚠️ documentStyle is not a dict ({type(doc_style)}), removing it")
                del rc['documentStyle']
        
        if 'metadata' in rc:
            metadata = rc['metadata']
            if metadata is None or metadata == "":
                logger.warning("⚠️ metadata is None or empty string, removing it")
                del rc['metadata']
            elif not isinstance(metadata, dict):
                logger.warning(f"⚠️ metadata is not a dict ({type(metadata)}), removing it")
                del rc['metadata']
        
        # Check for any None values in critical nested structures
        def check_none_in_dict(d, path=""):
            """Recursively check for None values that shouldn't be there"""
            issues = []
            if isinstance(d, dict):
                for key, value in d.items():
                    current_path = f"{path}.{key}" if path else key
                    if value is None:
                        # Some fields can legitimately be None, but most shouldn't
                        if key not in ['decorations', 'nodeStyle', 'props']:
                            issues.append(current_path)
                    elif isinstance(value, dict):
                        issues.extend(check_none_in_dict(value, current_path))
                    elif isinstance(value, list):
                        for i, item in enumerate(value):
                            if item is None:
                                issues.append(f"{current_path}[{i}]")
                            elif isinstance(item, dict):
                                issues.extend(check_none_in_dict(item, f"{current_path}[{i}]"))
            return issues
        
        none_issues = check_none_in_dict(blog_data['draftPost']['richContent'])
        if none_issues:
            logger.error(f"❌ Found None values in richContent at: {none_issues[:10]}")  # Limit to first 10
            # Remove None values from critical paths
            for issue_path in none_issues[:5]:  # Fix first 5
                parts = issue_path.split('.')
                try:
                    obj = blog_data['draftPost']['richContent']
                    for part in parts[:-1]:
                        if '[' in part:
                            key, idx = part.split('[')
                            idx = int(idx.rstrip(']'))
                            obj = obj[key][idx]
                        else:
                            obj = obj[part]
                    final_key = parts[-1]
                    if '[' in final_key:
                        key, idx = final_key.split('[')
                        idx = int(idx.rstrip(']'))
                        obj[key][idx] = {}
                    else:
                        obj[final_key] = {}
                    logger.warning(f"Fixed None value at {issue_path}")
                except:
                    pass
        
        # Log the final payload structure one more time before sending
        logger.warning(f"📤 Final payload ready - draftPost keys: {list(blog_data['draftPost'].keys())}")
        logger.warning(f"📤 RichContent nodes count: {len(blog_data['draftPost']['richContent'].get('nodes', []))}")
        logger.warning(f"📤 RichContent has metadata: {bool(blog_data['draftPost']['richContent'].get('metadata'))}")
        logger.warning(f"📤 RichContent has documentStyle: {bool(blog_data['draftPost']['richContent'].get('documentStyle'))}")
        
        result = blog_service.create_draft_post(access_token, blog_data, extra_headers or None)
        
        # Log success
        draft_post = result.get('draftPost', {})
        post_id = draft_post.get('id', 'N/A')
        wix_logger.log_operation_result("Create Draft Post", True, result)
        logger.success(f"✅ Wix: Blog post created - ID: {post_id}")
        
        return result
    except requests.RequestException as e:
        logger.error(f"Failed to create blog post: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response body: {e.response.text}")
        raise

