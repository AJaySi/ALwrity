"""
SEO Data Builder for Wix Blog Posts

Builds Wix-compatible seoData objects from ALwrity SEO metadata.
"""

from typing import Dict, Any, Optional
from loguru import logger


def build_seo_data(seo_metadata: Dict[str, Any], default_title: str = None) -> Optional[Dict[str, Any]]:
    """
    Build Wix seoData object from our SEO metadata format.
    
    Args:
        seo_metadata: SEO metadata dict with fields like:
            - seo_title: SEO optimized title
            - meta_description: Meta description
            - focus_keyword: Main keyword
            - blog_tags: List of tag strings (for keywords)
            - open_graph: Open Graph data dict
            - canonical_url: Canonical URL
        default_title: Fallback title if seo_title not provided
        
    Returns:
        Wix seoData object with settings.keywords and tags array, or None if empty
    """
    seo_data = {
        'settings': {
            'keywords': [],
            'preventAutoRedirect': False  # Required by Wix API schema
        },
        'tags': []
    }
    
    # Build keywords array
    keywords_list = []
    
    # Add main keyword (focus_keyword) if provided
    focus_keyword = seo_metadata.get('focus_keyword')
    if focus_keyword:
        keywords_list.append({
            'term': str(focus_keyword),
            'isMain': True,
            'origin': 'USER'  # Required by Wix API
        })
    
    # Add additional keywords from blog_tags or other sources
    blog_tags = seo_metadata.get('blog_tags', [])
    if isinstance(blog_tags, list):
        for tag in blog_tags:
            tag_str = str(tag).strip()
            if tag_str and tag_str != focus_keyword:  # Don't duplicate main keyword
                keywords_list.append({
                    'term': tag_str,
                    'isMain': False,
                    'origin': 'USER'  # Required by Wix API
                })
    
    # Add social hashtags as keywords if available
    social_hashtags = seo_metadata.get('social_hashtags', [])
    if isinstance(social_hashtags, list):
        for hashtag in social_hashtags:
            # Remove # if present
            hashtag_str = str(hashtag).strip().lstrip('#')
            if hashtag_str and hashtag_str != focus_keyword:
                keywords_list.append({
                    'term': hashtag_str,
                    'isMain': False,
                    'origin': 'USER'  # Required by Wix API
                })
    
    # CRITICAL: Wix Blog API limits keywords to maximum 5
    # Prioritize: main keyword first, then most important additional keywords
    if len(keywords_list) > 5:
        logger.warning(f"Truncating keywords from {len(keywords_list)} to 5 (Wix API limit)")
        # Keep main keyword + next 4 most important
        keywords_list = keywords_list[:5]
    
    seo_data['settings']['keywords'] = keywords_list
    
    # Validate keywords list is not empty (or ensure at least one keyword exists)
    if not seo_data['settings']['keywords']:
        logger.warning("No keywords found in SEO metadata, adding empty keywords array")
    
    # Build tags array (meta tags, Open Graph, etc.)
    tags_list = []
    
    # Meta description
    meta_description = seo_metadata.get('meta_description')
    if meta_description:
        tags_list.append({
            'type': 'meta',
            'props': {
                'name': 'description',
                'content': str(meta_description)
            },
            'custom': True,
            'disabled': False
        })
    
    # SEO title - 'title' type uses 'children' field, not 'props.content'
    # Per Wix API example: title tags don't need 'custom' or 'disabled' fields
    seo_title = seo_metadata.get('seo_title') or default_title
    if seo_title:
        tags_list.append({
            'type': 'title',
            'children': str(seo_title)  # Title tags use 'children', not 'props.content'
            # Note: Wix example doesn't show 'custom' or 'disabled' for title tags
        })
    
    # Open Graph tags
    open_graph = seo_metadata.get('open_graph', {})
    if isinstance(open_graph, dict):
        # OG Title
        og_title = open_graph.get('title') or seo_title
        if og_title:
            tags_list.append({
                'type': 'meta',
                'props': {
                    'property': 'og:title',
                    'content': str(og_title)
                },
                'custom': True,
                'disabled': False
            })
        
        # OG Description
        og_description = open_graph.get('description') or meta_description
        if og_description:
            tags_list.append({
                'type': 'meta',
                'props': {
                    'property': 'og:description',
                    'content': str(og_description)
                },
                'custom': True,
                'disabled': False
            })
        
        # OG Image
        og_image = open_graph.get('image')
        if og_image:
            # Skip base64 images for OG tags (Wix needs URLs)
            if isinstance(og_image, str) and (og_image.startswith('http://') or og_image.startswith('https://')):
                tags_list.append({
                    'type': 'meta',
                    'props': {
                        'property': 'og:image',
                        'content': og_image
                    },
                    'custom': True,
                    'disabled': False
                })
        
        # OG Type
        tags_list.append({
            'type': 'meta',
            'props': {
                'property': 'og:type',
                'content': 'article'
            },
            'custom': True,
            'disabled': False
        })
        
        # OG URL (canonical or provided URL)
        og_url = open_graph.get('url') or seo_metadata.get('canonical_url')
        if og_url:
            tags_list.append({
                'type': 'meta',
                'props': {
                    'property': 'og:url',
                    'content': str(og_url)
                },
                'custom': True,
                'disabled': False
            })
    
    # Twitter Card tags
    twitter_card = seo_metadata.get('twitter_card', {})
    if isinstance(twitter_card, dict):
        twitter_title = twitter_card.get('title') or seo_title
        if twitter_title:
            tags_list.append({
                'type': 'meta',
                'props': {
                    'name': 'twitter:title',
                    'content': str(twitter_title)
                },
                'custom': True,
                'disabled': False
            })
        
        twitter_description = twitter_card.get('description') or meta_description
        if twitter_description:
            tags_list.append({
                'type': 'meta',
                'props': {
                    'name': 'twitter:description',
                    'content': str(twitter_description)
                },
                'custom': True,
                'disabled': False
            })
        
        twitter_image = twitter_card.get('image')
        if twitter_image and isinstance(twitter_image, str) and (twitter_image.startswith('http://') or twitter_image.startswith('https://')):
            tags_list.append({
                'type': 'meta',
                'props': {
                    'name': 'twitter:image',
                    'content': twitter_image
                },
                'custom': True,
                'disabled': False
            })
        
        twitter_card_type = twitter_card.get('card', 'summary_large_image')
        tags_list.append({
            'type': 'meta',
            'props': {
                'name': 'twitter:card',
                'content': str(twitter_card_type)
            },
            'custom': True,
            'disabled': False
        })
    
    # Canonical URL as link tag
    canonical_url = seo_metadata.get('canonical_url')
    if canonical_url:
        tags_list.append({
            'type': 'link',
            'props': {
                'rel': 'canonical',
                'href': str(canonical_url)
            },
            'custom': True,
            'disabled': False
        })
    
    # Validate all tags have required fields before adding
    validated_tags = []
    for tag in tags_list:
        if not isinstance(tag, dict):
            logger.warning(f"Skipping invalid tag (not a dict): {type(tag)}")
            continue
        # Ensure required fields exist
        if 'type' not in tag:
            logger.warning("Skipping tag missing 'type' field")
            continue
        # Ensure 'custom' and 'disabled' fields exist
        if 'custom' not in tag:
            tag['custom'] = True
        if 'disabled' not in tag:
            tag['disabled'] = False
        # Validate tag structure based on type
        tag_type = tag.get('type')
        if tag_type == 'title':
            if 'children' not in tag or not tag['children']:
                logger.warning("Skipping title tag with missing/invalid 'children' field")
                continue
        elif tag_type == 'meta':
            if 'props' not in tag or not isinstance(tag['props'], dict):
                logger.warning("Skipping meta tag with missing/invalid 'props' field")
                continue
            if 'name' not in tag['props'] and 'property' not in tag['props']:
                logger.warning("Skipping meta tag with missing 'name' or 'property' in props")
                continue
            # Ensure 'content' exists and is not empty
            if 'content' not in tag['props'] or not str(tag['props'].get('content', '')).strip():
                logger.warning(f"Skipping meta tag with missing/empty 'content': {tag.get('props', {})}")
                continue
        elif tag_type == 'link':
            if 'props' not in tag or not isinstance(tag['props'], dict):
                logger.warning("Skipping link tag with missing/invalid 'props' field")
                continue
            # Ensure 'href' exists and is not empty for link tags
            if 'href' not in tag['props'] or not str(tag['props'].get('href', '')).strip():
                logger.warning(f"Skipping link tag with missing/empty 'href': {tag.get('props', {})}")
                continue
        validated_tags.append(tag)
    
    seo_data['tags'] = validated_tags
    
    # Final validation: ensure seoData structure is complete
    if not isinstance(seo_data['settings'], dict):
        logger.error("seoData.settings is not a dict, creating default")
        seo_data['settings'] = {'keywords': []}
    if not isinstance(seo_data['settings'].get('keywords'), list):
        logger.error("seoData.settings.keywords is not a list, creating empty list")
        seo_data['settings']['keywords'] = []
    if not isinstance(seo_data['tags'], list):
        logger.error("seoData.tags is not a list, creating empty list")
        seo_data['tags'] = []
    
    # CRITICAL: Per Wix API patterns, omit empty structures instead of including them as {}
    # If keywords is empty, omit settings entirely
    if not seo_data['settings'].get('keywords'):
        logger.debug("No keywords found, omitting settings from seoData")
        seo_data.pop('settings', None)
    
    logger.debug(f"Built SEO data: {len(validated_tags)} tags, {len(keywords_list)} keywords")
    
    # Only return seoData if we have at least keywords or tags
    if keywords_list or validated_tags:
        return seo_data
    
    return None

