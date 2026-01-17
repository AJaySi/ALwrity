from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

async def normalize_competitor_analysis(competitor_analysis: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Normalize competitor analysis data from onboarding for content strategy autofill.
    
    Args:
        competitor_analysis: List of competitor analysis records from CompetitorAnalysis model
        
    Returns:
        Normalized competitor data structure
    """
    if not competitor_analysis or len(competitor_analysis) == 0:
        logger.warning("⚠️ normalize_competitor_analysis: Empty competitor_analysis received")
        logger.warning(f"  competitor_analysis type: {type(competitor_analysis)}")
        logger.warning(f"  competitor_analysis value: {competitor_analysis}")
        return {}
    
    logger.warning(f"🔍 normalize_competitor_analysis received {len(competitor_analysis)} competitors")
    logger.warning(f"  First competitor type: {type(competitor_analysis[0])}")
    logger.warning(f"  First competitor keys: {list(competitor_analysis[0].keys()) if isinstance(competitor_analysis[0], dict) else 'Not a dict'}")
    
    # Extract top competitors
    top_competitors = []
    competitor_strategies = []
    market_gaps = []
    industry_trends = []
    emerging_trends = []
    
    for competitor in competitor_analysis:
        # Extract competitor basic info - handle both formats
        # Format 1: From database_service.get_competitor_analysis() - has url, domain, competitive_insights, content_insights
        # Format 2: From CompetitorAnalysis.to_dict() - has competitor_url, competitor_domain, analysis_data
        competitor_url = competitor.get('competitor_url') or competitor.get('url', '')
        competitor_domain = competitor.get('competitor_domain') or competitor.get('domain', '')
        
        # Handle analysis_data - could be nested or flattened
        if 'analysis_data' in competitor:
            analysis_data = competitor.get('analysis_data') or {}
        else:
            # Data is already flattened (from database_service.get_competitor_analysis)
            analysis_data = {
                'title': competitor.get('title', ''),
                'summary': competitor.get('summary', ''),
                'highlights': competitor.get('highlights', []),
                'competitive_insights': competitor.get('competitive_insights', {}),
                'competitive_analysis': competitor.get('competitive_insights', {}),  # Alias
                'content_insights': competitor.get('content_insights', {})
            }
        
        # Build competitor entry
        competitor_entry = {
            'name': analysis_data.get('title') or competitor.get('title') or competitor_domain or competitor_url,
            'website': competitor_url,
            'strength': _extract_strengths(analysis_data),
            'weakness': _extract_weaknesses(analysis_data)
        }
        top_competitors.append(competitor_entry)
        
        # Extract content strategy insights
        content_insights = analysis_data.get('content_insights') or competitor.get('content_insights') or {}
        competitive_insights = analysis_data.get('competitive_insights') or analysis_data.get('competitive_analysis') or competitor.get('competitive_insights') or {}
        
        if content_insights or competitive_insights:
            strategy_entry = {
                'competitor': competitor_entry['name'],
                'content_types': content_insights.get('content_types') or [],
                'publishing_frequency': content_insights.get('frequency') or 'Unknown',
                'content_themes': content_insights.get('themes') or [],
                'distribution_channels': content_insights.get('channels') or [],
                'engagement_approach': competitive_insights.get('engagement_strategy') or ''
            }
            competitor_strategies.append(strategy_entry)
        
        # Extract market gaps and trends from competitive insights
        if competitive_insights:
            gaps = competitive_insights.get('market_gaps') or []
            if isinstance(gaps, list):
                market_gaps.extend(gaps)
            
            trends = competitive_insights.get('industry_trends') or []
            if isinstance(trends, list):
                industry_trends.extend(trends)
            
            emerging = competitive_insights.get('emerging_trends') or []
            if isinstance(emerging, list):
                emerging_trends.extend(emerging)
    
    # If no market gaps found, generate from competitor analysis
    if not market_gaps and top_competitors:
        # Generate market gaps based on competitor strengths/weaknesses
        for comp in top_competitors[:5]:  # Use top 5 competitors
            if comp.get('weakness'):
                market_gaps.append({
                    'gap_description': f"Opportunity in {comp.get('name', 'competitor')} weakness area",
                    'opportunity': comp.get('weakness', ''),
                    'target_audience': '',
                    'priority': 'Medium'
                })
    
    # If no industry trends found, generate from competitor content themes
    if not industry_trends:
        # Extract themes from competitor strategies
        all_themes = _aggregate_themes(competitor_strategies)
        if all_themes:
            for theme in all_themes[:5]:  # Use top 5 themes
                industry_trends.append({
                    'trend_name': theme,
                    'description': f"Trending topic in competitor content: {theme}",
                    'impact': 'Medium',
                    'relevance': 'Identified from competitor content analysis'
                })
        
        # Also extract from summaries if available
        for competitor in competitor_analysis[:3]:  # Check top 3 competitors
            analysis_data = competitor.get('analysis_data') or {}
            summary = analysis_data.get('summary') or competitor.get('summary', '')
            if summary and len(summary) > 50:
                # Look for industry keywords
                industry_keywords = ['digital', 'ai', 'automation', 'cloud', 'saas', 'platform', 'solution']
                found_keywords = [kw for kw in industry_keywords if kw in summary.lower()]
                if found_keywords:
                    industry_trends.append({
                        'trend_name': found_keywords[0].title() + ' adoption',
                        'description': summary[:200] if len(summary) > 200 else summary,
                        'impact': 'High',
                        'relevance': 'From competitor analysis'
                    })
                    break  # Only add one from summaries
    
    # If no emerging trends found, generate from recent competitor activity
    if not emerging_trends and top_competitors:
        # Use competitor strengths as emerging trends
        for comp in top_competitors[:3]:  # Use top 3 competitors
            if comp.get('strength'):
                emerging_trends.append({
                    'trend_name': f"Emerging strength in {comp.get('name', 'competitor')}",
                    'description': comp.get('strength', ''),
                    'growth_potential': 'High',
                    'early_adoption_benefit': 'Competitive advantage opportunity'
                })
    
    # Aggregate insights across all competitors
    # ALWAYS return the structure, even if lists are empty - this ensures transformer can check properly
    normalized = {
        'top_competitors': top_competitors[:10] if top_competitors else [],  # Limit to top 10, ensure list
        'competitor_content_strategies': {
            'content_types': _aggregate_content_types(competitor_strategies) or [],
            'publishing_frequency': _aggregate_frequency(competitor_strategies) or 'Unknown',
            'content_themes': _aggregate_themes(competitor_strategies) or [],
            'distribution_channels': _aggregate_channels(competitor_strategies) or [],
            'engagement_approach': _aggregate_engagement_approaches(competitor_strategies) or ''
        },
        'market_gaps': _deduplicate_and_format(market_gaps, item_type='market_gap') if market_gaps else [],
        'industry_trends': _deduplicate_and_format(industry_trends, item_type='industry_trend') if industry_trends else [],
        'emerging_trends': _deduplicate_and_format(emerging_trends, item_type='emerging_trend') if emerging_trends else []
    }
    
    logger.warning(f"✅ normalize_competitor_analysis output keys: {list(normalized.keys())}")
    logger.warning(f"  Top competitors: {len(normalized['top_competitors'])}")
    if normalized['top_competitors']:
        logger.warning(f"  🔍 Sample top_competitor: {normalized['top_competitors'][0]}")
    logger.warning(f"  Market gaps: {len(normalized['market_gaps'])}")
    if normalized['market_gaps']:
        logger.warning(f"  🔍 Sample market_gap: {normalized['market_gaps'][0]}")
    logger.warning(f"  Industry trends: {len(normalized['industry_trends'])}")
    if normalized['industry_trends']:
        logger.warning(f"  🔍 Sample industry_trend: {normalized['industry_trends'][0]}")
    logger.warning(f"  Emerging trends: {len(normalized['emerging_trends'])}")
    if normalized['emerging_trends']:
        logger.warning(f"  🔍 Sample emerging_trend: {normalized['emerging_trends'][0]}")
    
    return normalized

def _extract_strengths(analysis_data: Dict[str, Any]) -> str:
    """Extract competitor strengths from analysis data."""
    competitive_insights = analysis_data.get('competitive_insights') or analysis_data.get('competitive_analysis') or {}
    strengths = competitive_insights.get('strengths') or []
    
    if isinstance(strengths, list):
        return '\n'.join(strengths) if strengths else ''
    elif isinstance(strengths, str):
        return strengths
    
    # Fallback to highlights
    highlights = analysis_data.get('highlights') or []
    if isinstance(highlights, list):
        return '\n'.join(highlights[:3]) if highlights else ''
    
    return ''

def _extract_weaknesses(analysis_data: Dict[str, Any]) -> str:
    """Extract competitor weaknesses from analysis data."""
    competitive_insights = analysis_data.get('competitive_insights') or analysis_data.get('competitive_analysis') or {}
    weaknesses = competitive_insights.get('weaknesses') or []
    
    if isinstance(weaknesses, list):
        return '\n'.join(weaknesses) if weaknesses else ''
    elif isinstance(weaknesses, str):
        return weaknesses
    
    return ''

def _aggregate_content_types(strategies: List[Dict[str, Any]]) -> List[str]:
    """Aggregate content types across all competitors."""
    all_types = []
    for strategy in strategies:
        types = strategy.get('content_types') or []
        if isinstance(types, list):
            all_types.extend(types)
    return list(set(all_types))  # Remove duplicates

def _aggregate_frequency(strategies: List[Dict[str, Any]]) -> str:
    """Aggregate most common publishing frequency."""
    frequencies = [s.get('publishing_frequency') for s in strategies if s.get('publishing_frequency')]
    if not frequencies:
        return 'Unknown'
    # Return most common frequency
    from collections import Counter
    return Counter(frequencies).most_common(1)[0][0] if frequencies else 'Unknown'

def _aggregate_themes(strategies: List[Dict[str, Any]]) -> List[str]:
    """Aggregate content themes across all competitors."""
    all_themes = []
    for strategy in strategies:
        themes = strategy.get('content_themes') or []
        if isinstance(themes, list):
            all_themes.extend(themes)
    return list(set(all_themes))  # Remove duplicates

def _aggregate_channels(strategies: List[Dict[str, Any]]) -> List[str]:
    """Aggregate distribution channels across all competitors."""
    all_channels = []
    for strategy in strategies:
        channels = strategy.get('distribution_channels') or []
        if isinstance(channels, list):
            all_channels.extend(channels)
    return list(set(all_channels))  # Remove duplicates

def _aggregate_engagement_approaches(strategies: List[Dict[str, Any]]) -> str:
    """Aggregate engagement approaches."""
    approaches = [s.get('engagement_approach') for s in strategies if s.get('engagement_approach')]
    if not approaches:
        return ''
    # Combine all approaches
    return '\n\n'.join(approaches)

def _deduplicate_and_format(items: List[Any], item_type: str = 'trend') -> List[Dict[str, Any]]:
    """Deduplicate and format items (gaps, trends) into structured format matching frontend schemas.
    
    Args:
        items: List of items (strings or dicts)
        item_type: Type of item - 'trend', 'industry_trend', 'emerging_trend', or 'market_gap'
    """
    if not items:
        return []
    
    # If items are already dicts, ensure they have required fields
    if items and isinstance(items[0], dict):
        seen = set()
        unique = []
        for item in items:
            # Use name or description as key for deduplication
            key = item.get('name') or item.get('trend_name') or item.get('gap_description') or item.get('description') or str(item)
            if key not in seen:
                seen.add(key)
                # Ensure required fields are present based on item_type
                formatted_item = _ensure_required_fields(item, item_type)
                unique.append(formatted_item)
        return unique
    
    # If items are strings, convert to structured format matching frontend schema
    unique_strings = list(set([str(item) for item in items if item]))
    
    if item_type == 'market_gap':
        return [{
            'gap_description': item,
            'opportunity': '',
            'target_audience': '',
            'priority': 'Medium'
        } for item in unique_strings]
    elif item_type == 'industry_trend':
        return [{
            'trend_name': item,
            'description': item,
            'impact': 'Medium',
            'relevance': ''
        } for item in unique_strings]
    elif item_type == 'emerging_trend':
        return [{
            'trend_name': item,
            'description': item,
            'growth_potential': 'Medium',
            'early_adoption_benefit': ''
        } for item in unique_strings]
    else:  # Default to trend format
        return [{'trend_name': item, 'description': item} for item in unique_strings]

def _ensure_required_fields(item: Dict[str, Any], item_type: str) -> Dict[str, Any]:
    """Ensure item has all required fields based on frontend schema."""
    if item_type == 'market_gap':
        return {
            'gap_description': item.get('gap_description') or item.get('description') or item.get('name') or '',
            'opportunity': item.get('opportunity') or '',
            'target_audience': item.get('target_audience') or '',
            'priority': item.get('priority') or 'Medium'
        }
    elif item_type == 'industry_trend':
        return {
            'trend_name': item.get('trend_name') or item.get('name') or item.get('description') or '',
            'description': item.get('description') or item.get('trend_name') or item.get('name') or '',
            'impact': item.get('impact') or 'Medium',
            'relevance': item.get('relevance') or ''
        }
    elif item_type == 'emerging_trend':
        return {
            'trend_name': item.get('trend_name') or item.get('name') or item.get('description') or '',
            'description': item.get('description') or item.get('trend_name') or item.get('name') or '',
            'growth_potential': item.get('growth_potential') or 'Medium',
            'early_adoption_benefit': item.get('early_adoption_benefit') or ''
        }
    else:
        return item
