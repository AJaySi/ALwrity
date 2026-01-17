from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)

async def normalize_research_preferences(research_data: Dict[str, Any], website_fallback: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if not research_data:
        logger.warning("⚠️ normalize_research_preferences: Empty research_data received")
        # If research_data is empty but we have website_fallback, use it
        if website_fallback:
            logger.warning("✅ Using website_analysis as fallback for research_preferences")
            research_data = {}

    # Log what we're receiving
    logger.warning(f"🔍 normalize_research_preferences received keys: {list(research_data.keys())}")
    logger.warning(f"  content_types: {research_data.get('content_types')}")
    logger.warning(f"  target_audience: {research_data.get('target_audience')}")
    logger.warning(f"  writing_style: {research_data.get('writing_style')}")
    logger.warning(f"  recommended_settings: {research_data.get('recommended_settings')}")

    # Extract content_types - this exists in the database
    content_types = research_data.get('content_types', [])
    if not content_types or (isinstance(content_types, list) and len(content_types) == 0):
        logger.warning("⚠️ content_types is empty or missing")
        # Try recommended_settings from research_data first
        recommended_settings = research_data.get('recommended_settings', {})
        if recommended_settings and isinstance(recommended_settings, dict):
            content_types = recommended_settings.get('content_type', [])
            if isinstance(content_types, str):
                content_types = [content_types]
        
        # If still empty, try website_fallback
        if (not content_types or len(content_types) == 0) and website_fallback:
            logger.warning("✅ Falling back to website_analysis for content_types")
            logger.warning(f"  Website fallback keys: {list(website_fallback.keys()) if website_fallback else 'NONE'}")
            logger.warning(f"  Website content_type: {website_fallback.get('content_type')}")
            logger.warning(f"  Website recommended_settings: {website_fallback.get('recommended_settings')}")
            
            website_content_type = website_fallback.get('content_type', {})
            if isinstance(website_content_type, dict):
                content_types = website_content_type.get('primary_type', [])
                if isinstance(content_types, str):
                    content_types = [content_types]
                logger.warning(f"  Extracted from content_type.primary_type: {content_types}")
            
            # Also try recommended_settings from website
            if (not content_types or len(content_types) == 0):
                website_recommended = website_fallback.get('recommended_settings', {})
                logger.warning(f"  Trying recommended_settings: {website_recommended}")
                if website_recommended and isinstance(website_recommended, dict):
                    content_types = website_recommended.get('content_type', [])
                    if isinstance(content_types, str):
                        content_types = [content_types]
                    logger.warning(f"  Extracted from recommended_settings.content_type: {content_types}")
            
            logger.warning(f"  Final content_types after fallback: {content_types}")

    # Extract target_audience data - this exists in the database
    target_audience_raw = research_data.get('target_audience', {})
    if not target_audience_raw and website_fallback:
        logger.warning("✅ Falling back to website_analysis for target_audience")
        logger.warning(f"  Website target_audience: {website_fallback.get('target_audience')}")
        target_audience_raw = website_fallback.get('target_audience', {})
        logger.warning(f"  Extracted target_audience_raw: {target_audience_raw}")
    if not target_audience_raw:
        target_audience_raw = {}
    
    # Extract writing_style data - this exists in the database
    writing_style_raw = research_data.get('writing_style', {})
    if not writing_style_raw and website_fallback:
        logger.warning("✅ Falling back to website_analysis for writing_style")
        logger.warning(f"  Website writing_style: {website_fallback.get('writing_style')}")
        writing_style_raw = website_fallback.get('writing_style', {})
        logger.warning(f"  Extracted writing_style_raw: {writing_style_raw}")
    if not writing_style_raw:
        writing_style_raw = {}
    
    # Extract recommended_settings - this exists in the database and might have useful data
    recommended_settings = research_data.get('recommended_settings', {})
    if not recommended_settings and website_fallback:
        logger.warning("✅ Falling back to website_analysis for recommended_settings")
        logger.warning(f"  Website recommended_settings: {website_fallback.get('recommended_settings')}")
        recommended_settings = website_fallback.get('recommended_settings', {})
        logger.warning(f"  Extracted recommended_settings: {recommended_settings}")
    if not recommended_settings:
        recommended_settings = {}

    # Build content_preferences from actual database fields
    # Extract content_topics from recommended_settings or website content_type or style_guidelines
    content_topics = []
    if isinstance(recommended_settings, dict):
        content_topics = recommended_settings.get('content_topics', [])
        logger.warning(f"  content_topics from recommended_settings: {content_topics}")
    if not content_topics and website_fallback:
        website_content_type = website_fallback.get('content_type', {})
        logger.warning(f"  Trying website content_type for content_topics: {website_content_type}")
        if isinstance(website_content_type, dict):
            content_topics = website_content_type.get('purpose', [])
            logger.warning(f"  Extracted content_topics from content_type.purpose: {content_topics}")
        
        # Try style_guidelines as fallback
        if not content_topics:
            style_guidelines = website_fallback.get('style_guidelines', {})
            logger.warning(f"  Trying style_guidelines for content_topics: {style_guidelines}")
            if isinstance(style_guidelines, dict):
                # style_guidelines might have topics or content_gaps
                content_topics = style_guidelines.get('topics', [])
                if not content_topics:
                    content_topics = style_guidelines.get('content_gaps', [])
                logger.warning(f"  Extracted content_topics from style_guidelines: {content_topics}")
    
    # Extract content_style from writing_style
    content_style = []
    if isinstance(writing_style_raw, dict):
        content_style = writing_style_raw.get('tone', [])
        logger.warning(f"  content_style from writing_style.tone: {content_style}")
        if not content_style:
            content_style = writing_style_raw.get('voice', [])
            logger.warning(f"  content_style from writing_style.voice: {content_style}")
    logger.warning(f"  Final content_style: {content_style}")
    
    content_preferences = {
        'preferred_formats': content_types if content_types else ['Blog Posts', 'Articles'],
        'content_topics': content_topics if content_topics else [],
        'content_style': content_style if content_style else [],
        'content_length': writing_style_raw.get('content_length', 'Medium (1000-2000 words)') if isinstance(writing_style_raw, dict) else 'Medium (1000-2000 words)',
        'visual_preferences': recommended_settings.get('visual_preferences', ['Infographics', 'Charts', 'Diagrams']) if isinstance(recommended_settings, dict) else ['Infographics', 'Charts', 'Diagrams'],
    }

    # Build audience_intelligence from actual database fields
    # Extract demographics from target_audience
    demographics = []
    if isinstance(target_audience_raw, dict):
        demographics = target_audience_raw.get('demographics', [])
        if not demographics:
            # Try to extract from other fields
            demographics = target_audience_raw.get('expertise_level', [])
            if isinstance(demographics, str):
                demographics = [demographics]
    
    audience_intelligence = {
        'target_audience': demographics if demographics else [],
        'pain_points': target_audience_raw.get('pain_points', []) if isinstance(target_audience_raw, dict) else [],
        'buying_journey': target_audience_raw.get('buying_journey', {}) if isinstance(target_audience_raw, dict) else {},
        'consumption_patterns': target_audience_raw.get('consumption_patterns', {}) if isinstance(target_audience_raw, dict) else {},
    }

    # Use content_types as research_topics fallback
    research_topics = recommended_settings.get('research_topics', content_types) if isinstance(recommended_settings, dict) else content_types

    normalized = {
        'content_preferences': content_preferences,
        'audience_intelligence': audience_intelligence,
        'research_goals': {
            'primary_goals': research_topics if research_topics else [],
            'secondary_goals': content_types if content_types else [],
            'success_metrics': recommended_settings.get('success_metrics', ['Website traffic', 'Lead quality', 'Engagement rates']) if isinstance(recommended_settings, dict) else ['Website traffic', 'Lead quality', 'Engagement rates'],
        },
        'data_quality': research_data.get('data_quality'),
        'confidence_level': research_data.get('confidence_level', 0.8),
        'data_freshness': research_data.get('data_freshness', 0.8),
    }

    logger.warning(f"✅ normalize_research_preferences output keys: {list(normalized.keys())}")
    logger.warning(f"  Normalized content_preferences: {normalized.get('content_preferences')}")
    logger.warning(f"  Normalized audience_intelligence: {normalized.get('audience_intelligence')}")

    return normalized 