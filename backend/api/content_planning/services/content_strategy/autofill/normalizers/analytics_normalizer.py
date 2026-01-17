from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)

async def normalize_gsc_analytics(gsc_data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize Google Search Console analytics data for content strategy autofill.
    
    Args:
        gsc_data: Raw GSC analytics data from SEODashboardService
        
    Returns:
        Normalized GSC analytics structure
    """
    if not gsc_data:
        logger.warning("⚠️ normalize_gsc_analytics: Empty gsc_data received")
        return {}
    
    logger.warning(f"🔍 normalize_gsc_analytics received keys: {list(gsc_data.keys())}")
    
    # Extract metrics from GSC data
    metrics = gsc_data.get('metrics', {})
    data = gsc_data.get('data', {})
    
    normalized = {
        'traffic_metrics': {
            'total_clicks': metrics.get('total_clicks', 0) or data.get('clicks', 0),
            'total_impressions': metrics.get('total_impressions', 0) or data.get('impressions', 0),
            'avg_ctr': metrics.get('avg_ctr', 0) or data.get('ctr', 0),
            'avg_position': metrics.get('avg_position', 0) or data.get('position', 0)
        },
        'top_queries': data.get('top_queries', []) or metrics.get('top_queries', []),
        'top_pages': data.get('top_pages', []) or metrics.get('top_pages', []),
        'traffic_sources': {
            'organic_search': {
                'clicks': metrics.get('total_clicks', 0) or data.get('clicks', 0),
                'impressions': metrics.get('total_impressions', 0) or data.get('impressions', 0),
                'ctr': metrics.get('avg_ctr', 0) or data.get('ctr', 0)
            }
        },
        'performance_metrics': {
            'traffic': metrics.get('total_clicks', 0) or data.get('clicks', 0),
            'conversion_rate': 0,  # GSC doesn't provide conversion data
            'bounce_rate': 0,  # GSC doesn't provide bounce rate
            'avg_session_duration': 0  # GSC doesn't provide session duration
        },
        'engagement_metrics': {
            'clicks': metrics.get('total_clicks', 0) or data.get('clicks', 0),
            'impressions': metrics.get('total_impressions', 0) or data.get('impressions', 0),
            'click_through_rate': metrics.get('avg_ctr', 0) or data.get('ctr', 0),
            'avg_position': metrics.get('avg_position', 0) or data.get('position', 0)
        },
        'date_range': gsc_data.get('date_range', {})
    }
    
    logger.warning(f"✅ normalize_gsc_analytics output keys: {list(normalized.keys())}")
    return normalized

async def normalize_bing_analytics(bing_data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize Bing Webmaster Tools analytics data for content strategy autofill.
    
    Args:
        bing_data: Raw Bing analytics data from SEODashboardService or BingAnalyticsStorageService
        
    Returns:
        Normalized Bing analytics structure
    """
    if not bing_data:
        logger.warning("⚠️ normalize_bing_analytics: Empty bing_data received")
        return {}
    
    logger.warning(f"🔍 normalize_bing_analytics received keys: {list(bing_data.keys())}")
    
    # Extract metrics from Bing data (could be from API or storage)
    metrics = bing_data.get('metrics', {})
    data = bing_data.get('data', {})
    summary = bing_data.get('summary', {})
    
    # Use summary if available (from storage), otherwise use API data
    if summary and not summary.get('error'):
        total_clicks = summary.get('total_clicks', 0)
        total_impressions = summary.get('total_impressions', 0)
        avg_ctr = summary.get('avg_ctr', 0)
        top_queries = summary.get('top_queries', [])
    else:
        total_clicks = metrics.get('total_clicks', 0) or data.get('clicks', 0)
        total_impressions = metrics.get('total_impressions', 0) or data.get('impressions', 0)
        avg_ctr = metrics.get('avg_ctr', 0) or data.get('ctr', 0)
        top_queries = data.get('top_queries', []) or metrics.get('top_queries', [])
    
    normalized = {
        'traffic_metrics': {
            'total_clicks': total_clicks,
            'total_impressions': total_impressions,
            'avg_ctr': avg_ctr,
            'avg_position': metrics.get('avg_position', 0) or data.get('position', 0)
        },
        'top_queries': top_queries,
        'traffic_sources': {
            'organic_search': {
                'clicks': total_clicks,
                'impressions': total_impressions,
                'ctr': avg_ctr
            }
        },
        'performance_metrics': {
            'traffic': total_clicks,
            'conversion_rate': 0,  # Bing doesn't provide conversion data
            'bounce_rate': 0,  # Bing doesn't provide bounce rate
            'avg_session_duration': 0  # Bing doesn't provide session duration
        },
        'engagement_metrics': {
            'clicks': total_clicks,
            'impressions': total_impressions,
            'click_through_rate': avg_ctr,
            'avg_position': metrics.get('avg_position', 0) or data.get('position', 0)
        },
        'date_range': bing_data.get('date_range', {})
    }
    
    logger.warning(f"✅ normalize_bing_analytics output keys: {list(normalized.keys())}")
    return normalized

async def normalize_analytics_combined(gsc_data: Dict[str, Any], bing_data: Dict[str, Any]) -> Dict[str, Any]:
    """Combine and normalize GSC and Bing analytics data.
    
    Args:
        gsc_data: Normalized GSC analytics
        bing_data: Normalized Bing analytics
        
    Returns:
        Combined analytics structure
    """
    combined = {
        'traffic_sources': {},
        'performance_metrics': {},
        'engagement_metrics': {},
        'top_queries': [],
        'data_sources': []
    }
    
    # Combine traffic sources
    if gsc_data.get('traffic_sources'):
        combined['traffic_sources'].update(gsc_data['traffic_sources'])
        combined['data_sources'].append('gsc')
    if bing_data.get('traffic_sources'):
        # Merge organic search data
        if 'organic_search' in combined['traffic_sources'] and 'organic_search' in bing_data['traffic_sources']:
            gsc_organic = combined['traffic_sources']['organic_search']
            bing_organic = bing_data['traffic_sources']['organic_search']
            combined['traffic_sources']['organic_search'] = {
                'clicks': gsc_organic.get('clicks', 0) + bing_organic.get('clicks', 0),
                'impressions': gsc_organic.get('impressions', 0) + bing_organic.get('impressions', 0),
                'ctr': (gsc_organic.get('ctr', 0) + bing_organic.get('ctr', 0)) / 2 if gsc_organic.get('ctr') and bing_organic.get('ctr') else (gsc_organic.get('ctr', 0) or bing_organic.get('ctr', 0))
            }
        else:
            combined['traffic_sources'].update(bing_data['traffic_sources'])
        combined['data_sources'].append('bing')
    
    # Combine performance metrics (prefer GSC if both available)
    if gsc_data.get('performance_metrics'):
        combined['performance_metrics'] = gsc_data['performance_metrics'].copy()
    elif bing_data.get('performance_metrics'):
        combined['performance_metrics'] = bing_data['performance_metrics'].copy()
    
    # Combine engagement metrics (average if both available)
    if gsc_data.get('engagement_metrics') and bing_data.get('engagement_metrics'):
        gsc_eng = gsc_data['engagement_metrics']
        bing_eng = bing_data['engagement_metrics']
        combined['engagement_metrics'] = {
            'clicks': gsc_eng.get('clicks', 0) + bing_eng.get('clicks', 0),
            'impressions': gsc_eng.get('impressions', 0) + bing_eng.get('impressions', 0),
            'click_through_rate': (gsc_eng.get('click_through_rate', 0) + bing_eng.get('click_through_rate', 0)) / 2,
            'avg_position': (gsc_eng.get('avg_position', 0) + bing_eng.get('avg_position', 0)) / 2 if gsc_eng.get('avg_position') and bing_eng.get('avg_position') else (gsc_eng.get('avg_position', 0) or bing_eng.get('avg_position', 0))
        }
    elif gsc_data.get('engagement_metrics'):
        combined['engagement_metrics'] = gsc_data['engagement_metrics'].copy()
    elif bing_data.get('engagement_metrics'):
        combined['engagement_metrics'] = bing_data['engagement_metrics'].copy()
    
    # Combine top queries (merge and deduplicate)
    all_queries = []
    if gsc_data.get('top_queries'):
        all_queries.extend(gsc_data['top_queries'])
    if bing_data.get('top_queries'):
        all_queries.extend(bing_data['top_queries'])
    
    # Deduplicate and sort by clicks
    query_dict = {}
    for query in all_queries:
        q_text = query.get('query') or query.get('Query', '')
        if q_text:
            if q_text not in query_dict:
                query_dict[q_text] = {
                    'query': q_text,
                    'clicks': 0,
                    'impressions': 0,
                    'ctr': 0
                }
            query_dict[q_text]['clicks'] += query.get('clicks', 0) or query.get('Clicks', 0)
            query_dict[q_text]['impressions'] += query.get('impressions', 0) or query.get('Impressions', 0)
    
    # Calculate CTR and sort
    for q in query_dict.values():
        if q['impressions'] > 0:
            q['ctr'] = (q['clicks'] / q['impressions']) * 100
    
    combined['top_queries'] = sorted(query_dict.values(), key=lambda x: x['clicks'], reverse=True)[:20]
    
    logger.warning(f"✅ normalize_analytics_combined output: {len(combined['data_sources'])} sources, {len(combined['top_queries'])} top queries")
    return combined
