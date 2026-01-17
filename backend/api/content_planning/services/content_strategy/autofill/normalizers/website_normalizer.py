from typing import Any, Dict

async def normalize_website_analysis(website_data: Dict[str, Any]) -> Dict[str, Any]:
    if not website_data:
        return {}

    processed_data = {
        'website_url': website_data.get('website_url'),
        'industry': (website_data.get('target_audience') or {}).get('industry_focus'),
        'market_position': 'Emerging',
        'business_size': 'Medium',
        'target_audience': (website_data.get('target_audience') or {}).get('demographics'),
        'content_goals': (website_data.get('content_type') or {}).get('purpose', []),
        'performance_metrics': {
            'traffic': (website_data.get('performance_metrics') or {}).get('traffic', 10000),
            'conversion_rate': (website_data.get('performance_metrics') or {}).get('conversion_rate', 2.5),
            'bounce_rate': (website_data.get('performance_metrics') or {}).get('bounce_rate', 50.0),
            'avg_session_duration': (website_data.get('performance_metrics') or {}).get('avg_session_duration', 150),
            'estimated_market_share': (website_data.get('performance_metrics') or {}).get('estimated_market_share')
        },
        'traffic_sources': website_data.get('traffic_sources') or {
            'organic': 70,
            'social': 20,
            'direct': 7,
            'referral': 3
        },
        'content_gaps': (website_data.get('style_guidelines') or {}).get('content_gaps', []),
        'topics': (website_data.get('content_type') or {}).get('primary_type', []),
        'content_quality_score': website_data.get('content_quality_score', 7.5),
        'seo_opportunities': (website_data.get('style_guidelines') or {}).get('seo_opportunities', []),
        'competitors': website_data.get('competitors', []),
        'competitive_advantages': (website_data.get('style_guidelines') or {}).get('advantages', []),
        'market_gaps': (website_data.get('style_guidelines') or {}).get('market_gaps', []),
        'data_quality': website_data.get('data_quality'),
        'confidence_level': website_data.get('confidence_level', 0.8),
        'data_freshness': website_data.get('data_freshness', 0.8),
        'content_budget': website_data.get('content_budget'),
        'team_size': website_data.get('team_size'),
        'implementation_timeline': website_data.get('implementation_timeline'),
        'market_share': website_data.get('market_share'),
        'target_metrics': website_data.get('target_metrics'),
    }

    return processed_data 