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
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Build valid Ricos rich content
    # Ensure content is not empty
    if not content or not content.strip():
        content = "This is a post from ALwrity."
        logger.warning("⚠️ Content was empty, using default text")
    
    # Try Wix API first (more reliable), fall back to custom parser
    ricos_content = None
    try:
        logger.warning("🔄 Attempting to convert markdown to Ricos via Wix API...")
        ricos_content = convert_via_wix_api(content, access_token, base_url)
        logger.warning(f"✅ Wix API conversion successful. Ricos document has {len(ricos_content.get('nodes', []))} nodes")
    except Exception as e:
        logger.warning(f"⚠️ Wix Ricos API conversion failed: {e}. Falling back to custom parser...")
        # Fall back to custom parser
        ricos_content = convert_content_to_ricos(content, None)
        logger.warning(f"✅ Custom parser conversion complete. Ricos document has {len(ricos_content.get('nodes', []))} nodes")
    
    # Validate Ricos content
    ricos_content = validate_ricos_content(ricos_content)
    
    # Minimal payload per Wix docs: title, memberId, and richContent
    # CRITICAL: Only include fields that have valid values (no None, no empty strings for required fields)
    blog_data = {
        'draftPost': {
            'title': str(title).strip() if title else "Untitled",
            'memberId': str(member_id).strip(),  # Required for third-party apps (validated above)
            'richContent': ricos_content,  # Must be a valid Ricos document object
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
    # TESTING: Skip SEO data temporarily to confirm richContent fix
    test_skip_seo = True
    if test_skip_seo:
        logger.warning("🧪 TESTING: Skipping SEO data to isolate richContent vs seoData issue")
        seo_data = None
    elif seo_metadata:
        logger.warning(f"📊 Building SEO data from metadata. Keys: {list(seo_metadata.keys())}")
        seo_data = build_seo_data(seo_metadata, title)
        if seo_data:
            # Log detailed SEO structure
            logger.warning(f"📋 SEO data built: {len(seo_data.get('tags', []))} tags, {len(seo_data.get('settings', {}).get('keywords', []))} keywords")
            
            # Log each SEO tag for debugging (key ones only to avoid too much output)
            if seo_data.get('tags'):
                for idx, tag in enumerate(seo_data['tags'][:3]):  # First 3 tags only
                    tag_type = tag.get('type')
                    if tag_type == 'title':
                        logger.warning(f"  SEO tag {idx+1}: type={tag_type}, children={str(tag.get('children', ''))[:50]}...")
                    else:
                        props = tag.get('props', {})
                        content_preview = str(props.get('content', props.get('href', props.get('name', ''))))[:50]
                        logger.warning(f"  SEO tag {idx+1}: type={tag_type}, props={list(props.keys())}, content={content_preview}...")
                if len(seo_data['tags']) > 3:
                    logger.warning(f"  ... and {len(seo_data['tags']) - 3} more SEO tags")
            
            blog_data['draftPost']['seoData'] = seo_data
            logger.warning(f"✅ Added seoData to blog post with {len(seo_data.get('tags', []))} tags")
        else:
            logger.warning("⚠️ SEO data was empty after building - check build_seo_data function")
        
        # Add SEO slug if provided (separate field from seoData)
        if seo_metadata and seo_metadata.get('url_slug'):
            blog_data['draftPost']['seoSlug'] = str(seo_metadata.get('url_slug')).strip()
            logger.warning(f"✅ Added SEO slug: {blog_data['draftPost']['seoSlug']}")
    
    if test_skip_seo:
        logger.warning("⚠️ SEO data skipped for testing - will add back once richContent is confirmed working")
    elif not seo_metadata:
        logger.warning("⚠️ No SEO metadata provided to create_blog_post")
    
    # Log the payload structure for debugging (without sensitive data)
    logger.warning(f"📝 Creating blog post with title: '{title}'")
    logger.warning(f"📋 Draft post fields: {list(blog_data['draftPost'].keys())}")
    
    # Detailed SEO logging
    if 'seoData' in blog_data['draftPost']:
        seo_data_debug = blog_data['draftPost']['seoData']
        logger.warning(f"📊 SEO data in payload: {len(seo_data_debug.get('tags', []))} tags, {len(seo_data_debug.get('settings', {}).get('keywords', []))} keywords")
        
        # Log sample SEO tags (first 2 only to avoid too much output)
        if seo_data_debug.get('tags'):
            logger.warning("📋 SEO Tags sample:")
            for i, tag in enumerate(seo_data_debug['tags'][:2]):  # First 2 tags
                logger.warning(f"  Tag {i+1}: type={tag.get('type')}, custom={tag.get('custom')}, disabled={tag.get('disabled')}")
            if len(seo_data_debug['tags']) > 2:
                logger.warning(f"  ... and {len(seo_data_debug['tags']) - 2} more tags")
        
        if seo_data_debug.get('settings', {}).get('keywords'):
            keywords_list = [k.get('term') for k in seo_data_debug['settings']['keywords'][:3]]
            logger.warning(f"🔑 Keywords: {keywords_list}")
        
        # Log FULL seoData structure for debugging
        import json
        try:
            seo_json = json.dumps(seo_data_debug, indent=2, ensure_ascii=False)
            logger.warning(f"📄 FULL seoData JSON:\n{seo_json[:2000]}...")  # First 2000 chars
        except Exception as e:
            logger.error(f"Failed to serialize seoData: {e}")
    else:
        logger.warning("⚠️ No seoData in draft post payload!")
    
    try:
        # Add wix-site-id header if we can extract it from token
        extra_headers = {}
        try:
            token_str = str(access_token)
            if token_str and token_str.startswith('OauthNG.JWS.'):
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
        except Exception as e:
            logger.debug(f"Could not extract site ID from token: {e}")
        
        # Make the API call
        logger.warning(f"🚀 Calling Wix API: POST /blog/v3/draft-posts")
        logger.warning(f"📦 Payload: title='{blog_data['draftPost'].get('title')}', has_seoData={'seoData' in blog_data['draftPost']}, has_richContent={'richContent' in blog_data['draftPost']}")
        
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
        
        # Try sending WITHOUT SEO data first to isolate the issue
        test_without_seo = False  # Disabled - listItemData issue fixed
        if test_without_seo and 'seoData' in blog_data['draftPost']:
            logger.warning("🧪 TESTING WITHOUT SEO DATA to isolate issue...")
            # Clone the payload without SEO data
            test_payload_no_seo = {
                'draftPost': {
                    'title': blog_data['draftPost']['title'],
                    'memberId': blog_data['draftPost']['memberId'],
                    'richContent': blog_data['draftPost']['richContent'],
                    'excerpt': blog_data['draftPost'].get('excerpt', '')
                },
                'publish': False,
                'fieldsets': ['URL']
            }
            try:
                logger.warning("🧪 Attempting without SEO data...")
                test_result = blog_service.create_draft_post(access_token, test_payload_no_seo, extra_headers or None)
                logger.warning(f"✅ WITHOUT SEO DATA SUCCEEDED! Post ID: {test_result.get('draftPost', {}).get('id')}")
                logger.error("⚠️⚠️⚠️ ISSUE IS WITH SEO DATA STRUCTURE!")
                # If this succeeds, don't send the full payload, just return this result
                return test_result
            except Exception as e:
                logger.warning(f"❌ WITHOUT SEO DATA ALSO FAILED: {e}")
                logger.warning("⚠️ Issue is NOT with SEO data, continuing with full payload...")
        
        # Try sending with minimal structure first to isolate the issue
        # Create a test payload with just required fields
        minimal_test = False  # Set to True to test with minimal payload
        if minimal_test:
            logger.warning("🧪 TESTING WITH MINIMAL PAYLOAD (title + memberId + simple richContent)")
            test_payload = {
                'draftPost': {
                    'title': blog_data['draftPost']['title'],
                    'memberId': blog_data['draftPost']['memberId'],
                    'richContent': {
                        'nodes': [
                            {
                                'id': str(uuid.uuid4()),
                                'type': 'PARAGRAPH',
                                'nodes': [
                                    {
                                        'id': str(uuid.uuid4()),
                                        'type': 'TEXT',
                                        'textData': {
                                            'text': 'Test paragraph',
                                            'decorations': []
                                        }
                                    }
                                ],
                                'paragraphData': {}
                            }
                        ],
                        'metadata': {'version': 1, 'id': str(uuid.uuid4())},
                        'documentStyle': {}
                    }
                },
                'publish': False,
                'fieldsets': ['URL']
            }
            logger.warning("🧪 Attempting minimal payload first...")
            try:
                test_result = blog_service.create_draft_post(access_token, test_payload, extra_headers or None)
                logger.warning(f"✅ MINIMAL PAYLOAD SUCCEEDED! Post ID: {test_result.get('draftPost', {}).get('id')}")
                logger.warning("⚠️ Issue is with complex content, not basic structure")
            except Exception as e:
                logger.error(f"❌ MINIMAL PAYLOAD ALSO FAILED: {e}")
                logger.error("⚠️ Issue is with basic structure or permissions")
        
        result = blog_service.create_draft_post(access_token, blog_data, extra_headers or None)
        
        # Log response
        draft_post = result.get('draftPost', {})
        logger.warning(f"✅ Blog post created successfully! Post ID: {draft_post.get('id', 'N/A')}")
        
        # Check if SEO data was preserved in response
        if 'seoData' in draft_post:
            seo_response = draft_post['seoData']
            logger.warning(f"✅ SEO data confirmed in response: {len(seo_response.get('tags', []))} tags, {len(seo_response.get('settings', {}).get('keywords', []))} keywords")
        else:
            logger.warning("⚠️ No seoData in response - it may have been filtered out by Wix API")
            logger.warning(f"📋 Response fields: {list(draft_post.keys())}")
        
        return result
    except requests.RequestException as e:
        logger.error(f"Failed to create blog post: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response body: {e.response.text}")
        raise

