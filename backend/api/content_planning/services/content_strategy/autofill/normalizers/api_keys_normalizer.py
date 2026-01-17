from typing import Any, Dict

async def normalize_api_keys(api_data: Dict[str, Any]) -> Dict[str, Any]:
    if not api_data:
        return {}

    providers = api_data.get('providers', [])

    return {
        'analytics_data': {
            'google_analytics': {
                'connected': 'google_analytics' in providers,
                'metrics': (api_data.get('google_analytics') or {}).get('metrics', {})
            },
            'google_search_console': {
                'connected': 'google_search_console' in providers,
                'metrics': (api_data.get('google_search_console') or {}).get('metrics', {})
            }
        },
        'social_media_data': api_data.get('social_media_data') or {},
        'competitor_data': api_data.get('competitor_data') or {},
        'data_quality': api_data.get('data_quality'),
        'confidence_level': api_data.get('confidence_level', 0.8),
        'data_freshness': api_data.get('data_freshness', 0.8)
    } 