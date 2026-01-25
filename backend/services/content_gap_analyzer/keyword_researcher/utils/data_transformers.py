"""
Data Transformers

Utility functions for data format conversion and transformation.
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import json
from loguru import logger

from ..models.shared import AnalysisStatus, PriorityLevel
from ..models.keyword_analysis import KeywordAnalysisResponse, TrendAnalysisResponse
from ..models.intent_analysis import IntentAnalysisResponse
from ..models.opportunity import OpportunityAnalysisResponse
from ..models.content_recommendation import ContentRecommendationResponse
from ..constants import DEFAULT_CONFIDENCE_SCORE


def transform_legacy_analysis_to_modern(
    legacy_results: Dict[str, Any],
    industry: str,
    target_url: str
) -> KeywordAnalysisResponse:
    """
    Transform legacy analysis results to modern model format.
    
    Args:
        legacy_results: Legacy analysis results
        industry: Industry category
        target_url: Target URL
        
    Returns:
        Modern KeywordAnalysisResponse
    """
    try:
        # Transform trend analysis
        trend_analysis = transform_legacy_trend_analysis(
            legacy_results.get('trend_analysis', {})
        )
        
        # Transform intent analysis
        intent_analysis = legacy_results.get('intent_analysis', {})
        
        # Transform opportunities
        opportunities = transform_legacy_opportunities(
            legacy_results.get('opportunities', [])
        )
        
        # Transform insights
        insights = legacy_results.get('insights', [])
        
        return KeywordAnalysisResponse(
            trend_analysis=trend_analysis,
            intent_analysis=intent_analysis,
            opportunities=opportunities,
            insights=insights,
            analysis_timestamp=datetime.utcnow().isoformat(),
            industry=industry,
            target_url=target_url
        )
        
    except Exception as e:
        logger.error(f"Error transforming legacy analysis: {e}")
        raise ValueError(f"Transformation error: {str(e)}")


def transform_legacy_trend_analysis(legacy_trends: Dict[str, Any]) -> TrendAnalysisResponse:
    """
    Transform legacy trend analysis to modern model format.
    
    Args:
        legacy_trends: Legacy trend analysis data
        
    Returns:
        Modern TrendAnalysisResponse
    """
    from ..models.trend_analysis import (
        TrendDirection, CompetitionLevel, SearchIntent,
        KeywordTrendData, TrendMetrics, TrendAnalysisResponse as ModernTrendResponse
    )
    
    # Transform trends data
    trends = {}
    for keyword, data in legacy_trends.get('trends', {}).items():
        trends[keyword] = KeywordTrendData(
            keyword=keyword,
            search_volume=data.get('search_volume', 0),
            difficulty_score=data.get('difficulty', 0),
            trend_direction=transform_trend_direction(data.get('trend', 'stable')),
            competition_level=transform_competition_level(data.get('competition', 'medium')),
            primary_intent=transform_search_intent(data.get('intent', 'informational')),
            cost_per_click=data.get('cpc', 0.0),
            seasonal_factor=data.get('seasonal_factor', 1.0)
        )
    
    # Transform summary
    summary_data = legacy_trends.get('summary', {})
    metrics = TrendMetrics(
        total_keywords_analyzed=summary_data.get('total_keywords', 0),
        rising_trends_count=0,  # Not available in legacy
        declining_trends_count=0,  # Not available in legacy
        average_difficulty=0,  # Calculate from trends
        high_opportunity_keywords=summary_data.get('low_competition_keywords', 0),
        seasonal_keywords=0  # Not available in legacy
    )
    
    # Transform recommendations
    recommendations = []
    for rec in legacy_trends.get('recommendations', []):
        from ..models.trend_analysis import TrendRecommendation
        recommendations.append(TrendRecommendation(
            keyword=rec.get('keyword', ''),
            recommendation=rec.get('recommendation', ''),
            priority=transform_priority(rec.get('priority', 'medium')),
            estimated_impact=rec.get('estimated_impact', '')
        ))
    
    return ModernTrendResponse(
        request_id=f"legacy_{datetime.utcnow().timestamp()}",
        analysis_timestamp=datetime.utcnow(),
        keyword_trends=trends,
        metrics=metrics,
        recommendations=recommendations,
        industry_insights=[]  # Not available in legacy
    )


def transform_legacy_opportunities(legacy_opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transform legacy opportunities to modern format.
    
    Args:
        legacy_opportunities: List of legacy opportunity data
        
    Returns:
        List of modern opportunity data
    """
    transformed_opportunities = []
    
    for opp in legacy_opportunities:
        transformed_opp = {
            'keyword': opp.get('keyword', ''),
            'opportunity_type': opp.get('opportunity_type', 'standard'),
            'search_volume': opp.get('search_volume', 0),
            'competition_level': opp.get('competition_level', 'medium'),
            'difficulty_score': opp.get('difficulty_score', 50),
            'estimated_traffic': opp.get('estimated_traffic', ''),
            'content_suggestions': opp.get('content_suggestions', []),
            'priority': opp.get('priority', 'medium'),
            'implementation_time': opp.get('implementation_time', '2-3 weeks'),
            'required_resources': ['Content creation', 'SEO optimization'],
            'success_probability': 75
        }
        transformed_opportunities.append(transformed_opp)
    
    return transformed_opportunities


def transform_trend_direction(trend_str: str) -> str:
    """
    Transform legacy trend direction to enum.
    
    Args:
        trend_str: Legacy trend string
        
    Returns:
        Trend direction enum value
    """
    from ..models.trend_analysis import TrendDirection
    
    trend_mapping = {
        'rising': TrendDirection.RISING,
        'stable': TrendDirection.STABLE,
        'declining': TrendDirection.DECLINING,
        'seasonal': TrendDirection.SEASONAL
    }
    
    return trend_mapping.get(trend_str.lower(), TrendDirection.STABLE)


def transform_competition_level(competition_str: str) -> str:
    """
    Transform legacy competition level to enum.
    
    Args:
        competition_str: Legacy competition string
        
    Returns:
        Competition level enum value
    """
    from ..models.trend_analysis import CompetitionLevel
    
    competition_mapping = {
        'low': CompetitionLevel.LOW,
        'medium': CompetitionLevel.MEDIUM,
        'high': CompetitionLevel.HIGH,
        'very_high': CompetitionLevel.VERY_HIGH
    }
    
    return competition_mapping.get(competition_str.lower(), CompetitionLevel.MEDIUM)


def transform_search_intent(intent_str: str) -> str:
    """
    Transform legacy intent to enum.
    
    Args:
        intent_str: Legacy intent string
        
    Returns:
        Search intent enum value
    """
    from ..models.intent_analysis import SearchIntent
    
    intent_mapping = {
        'informational': SearchIntent.INFORMATIONAL,
        'transactional': SearchIntent.TRANSACTIONAL,
        'navigational': SearchIntent.NAVIGATIONAL,
        'commercial': SearchIntent.COMMERCIAL
    }
    
    return intent_mapping.get(intent_str.lower(), SearchIntent.INFORMATIONAL)


def transform_priority(priority_str: str) -> str:
    """
    Transform legacy priority to enum.
    
    Args:
        priority_str: Legacy priority string
        
    Returns:
        Priority level enum value
    """
    priority_mapping = {
        'high': PriorityLevel.HIGH,
        'medium': PriorityLevel.MEDIUM,
        'low': PriorityLevel.LOW,
        'critical': PriorityLevel.HIGH  # Map critical to high
    }
    
    return priority_mapping.get(priority_str.lower(), PriorityLevel.MEDIUM)


def transform_keyword_expansion_results(
    seed_keywords: List[str],
    expanded_results: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Transform keyword expansion results to standard format.
    
    Args:
        seed_keywords: Original seed keywords
        expanded_results: Raw expansion results
        
    Returns:
        Standardized expansion results
    """
    return {
        'seed_keywords': seed_keywords,
        'expanded_keywords': expanded_results.get('expanded_keywords', []),
        'keyword_categories': expanded_results.get('keyword_categories', {}),
        'long_tail_opportunities': expanded_results.get('long_tail_opportunities', []),
        'semantic_variations': expanded_results.get('semantic_variations', []),
        'related_keywords': expanded_results.get('related_keywords', []),
        'expansion_metrics': {
            'total_expanded': len(expanded_results.get('expanded_keywords', [])),
            'total_long_tail': len(expanded_results.get('long_tail_opportunities', [])),
            'total_semantic': len(expanded_results.get('semantic_variations', [])),
            'total_related': len(expanded_results.get('related_keywords', [])),
            'expansion_ratio': len(expanded_results.get('expanded_keywords', [])) / len(seed_keywords) if seed_keywords else 0
        }
    }


def transform_content_recommendations(
    content_recs: Dict[str, Any],
    intent_analysis: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Transform content recommendations to standard format.
    
    Args:
        content_recs: Raw content recommendations
        intent_analysis: Intent analysis results
        
    Returns:
        Standardized content recommendations
    """
    return {
        'recommendations_by_intent': content_recs,
        'content_strategy': {
            'dominant_intent': intent_analysis.get('summary', {}).get('dominant_intent', 'informational'),
            'strategy_recommendations': intent_analysis.get('summary', {}).get('content_strategy_recommendations', [])
        },
        'content_priorities': calculate_content_priorities(content_recs),
        'implementation_roadmap': generate_implementation_roadmap(content_recs)
    }


def calculate_content_priorities(content_recs: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Calculate content priorities based on recommendations.
    
    Args:
        content_recs: Content recommendations by intent
        
    Returns:
        Dictionary with prioritized content lists
    """
    priorities = {
        'high_priority': [],
        'medium_priority': [],
        'low_priority': []
    }
    
    # High priority: informational content (usually highest volume)
    informational_recs = content_recs.get('informational', [])
    priorities['high_priority'].extend(informational_recs[:2])  # Top 2 informational
    
    # Medium priority: commercial content
    commercial_recs = content_recs.get('commercial', [])
    priorities['medium_priority'].extend(commercial_recs[:2])  # Top 2 commercial
    
    # Low priority: transactional and navigational
    transactional_recs = content_recs.get('transactional', [])
    navigational_recs = content_recs.get('navigational', [])
    priorities['low_priority'].extend(transactional_recs[:1])  # Top 1 transactional
    priorities['low_priority'].extend(navigational_recs[:1])  # Top 1 navigational
    
    return priorities


def generate_implementation_roadmap(content_recs: Dict[str, Any]) -> List[str]:
    """
    Generate implementation roadmap based on content recommendations.
    
    Args:
        content_recs: Content recommendations by intent
        
    Returns:
        List of implementation steps
    """
    roadmap = []
    
    # Phase 1: Foundation content
    informational_recs = content_recs.get('informational', [])
    if informational_recs:
        roadmap.append(f"Phase 1: Create foundational educational content ({len(informational_recs)} pieces)")
    
    # Phase 2: Commercial content
    commercial_recs = content_recs.get('commercial', [])
    if commercial_recs:
        roadmap.append(f"Phase 2: Develop commercial comparison content ({len(commercial_recs)} pieces)")
    
    # Phase 3: Transactional content
    transactional_recs = content_recs.get('transactional', [])
    if transactional_recs:
        roadmap.append(f"Phase 3: Build transactional product content ({len(transactional_recs)} pieces)")
    
    # Phase 4: Navigational content
    navigational_recs = content_recs.get('navigational', [])
    if navigational_recs:
        roadmap.append(f"Phase 4: Establish navigational brand content ({len(navigational_recs)} pieces)")
    
    return roadmap


def transform_analysis_summary(
    analysis_results: Dict[str, Any],
    processing_time: Optional[float] = None
) -> Dict[str, Any]:
    """
    Transform analysis results to summary format.
    
    Args:
        analysis_results: Complete analysis results
        processing_time: Optional processing time in seconds
        
    Returns:
        Analysis summary
    """
    opportunities = analysis_results.get('opportunities', [])
    insights = analysis_results.get('insights', [])
    
    # Calculate summary metrics
    high_opportunity_count = len([
        opp for opp in opportunities 
        if opp.get('priority') == 'high'
    ])
    
    return {
        'analysis_id': f"analysis_{datetime.utcnow().timestamp()}",
        'status': AnalysisStatus.COMPLETED,
        'summary_metrics': {
            'total_opportunities': len(opportunities),
            'high_priority_opportunities': high_opportunity_count,
            'total_insights': len(insights),
            'processing_time_seconds': processing_time,
            'analysis_timestamp': datetime.utcnow().isoformat()
        },
        'key_findings': {
            'dominant_intent': analysis_results.get('intent_analysis', {}).get('summary', {}).get('dominant_intent', 'unknown'),
            'opportunity_types': list(set(opp.get('opportunity_type', 'standard') for opp in opportunities)),
            'insight_categories': list(set(insight.get('category', 'general') for insight in insights))
        },
        'next_steps': [
            'Review high-priority opportunities',
            'Create content based on insights',
            'Monitor keyword performance',
            'Adjust strategy based on results'
        ]
    }


def transform_health_check_results(
    test_results: Dict[str, bool],
    processing_time: float
) -> Dict[str, Any]:
    """
    Transform health check results to standard format.
    
    Args:
        test_results: Results of health check tests
        processing_time: Total processing time
        
    Returns:
        Standardized health check response
    """
    from ..models.shared import HealthCheckResponse
    
    tests_passed = sum(1 for result in test_results.values() if result)
    total_tests = len(test_results)
    
    status = "healthy" if tests_passed == total_tests else "unhealthy"
    
    return HealthCheckResponse(
        service_name="KeywordResearcher",
        status=status,
        version="1.0.0",
        uptime_seconds=processing_time,
        last_check=datetime.utcnow(),
        dependencies={
            "ai_engine": "healthy" if test_results.get("ai_test", False) else "unhealthy",
            "database": "healthy" if test_results.get("db_test", False) else "unhealthy"
        },
        metrics={
            "tests_passed": tests_passed,
            "total_tests": total_tests,
            "success_rate": (tests_passed / total_tests) * 100 if total_tests > 0 else 0,
            "processing_time": processing_time
        }
    )


def serialize_analysis_results(results: Dict[str, Any]) -> str:
    """
    Serialize analysis results to JSON string.
    
    Args:
        results: Analysis results to serialize
        
    Returns:
        JSON string
    """
    try:
        # Convert datetime objects to ISO format
        def json_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        return json.dumps(results, default=json_serializer, indent=2)
    except Exception as e:
        logger.error(f"Error serializing analysis results: {e}")
        raise ValueError(f"Serialization error: {str(e)}")


def deserialize_analysis_results(json_str: str) -> Dict[str, Any]:
    """
    Deserialize JSON string to analysis results.
    
    Args:
        json_str: JSON string to deserialize
        
    Returns:
        Analysis results dictionary
    """
    try:
        results = json.loads(json_str)
        
        # Convert ISO format strings back to datetime objects if needed
        # This would be handled by Pydantic models in most cases
        
        return results
    except json.JSONDecodeError as e:
        logger.error(f"Error deserializing analysis results: {e}")
        raise ValueError(f"Deserialization error: {str(e)}")


def validate_data_structure(data: Dict[str, Any], required_fields: List[str]) -> bool:
    """
    Validate that data structure contains required fields.
    
    Args:
        data: Data dictionary to validate
        required_fields: List of required field names
        
    Returns:
        True if valid, False otherwise
    """
    missing_fields = []
    
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    
    if missing_fields:
        logger.warning(f"Missing required fields: {missing_fields}")
        return False
    
    return True


def sanitize_keyword_data(keyword_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize keyword data by removing invalid or harmful content.
    
    Args:
        keyword_data: Raw keyword data
        
    Returns:
        Sanitized keyword data
    """
    sanitized = keyword_data.copy()
    
    # Sanitize keyword string
    if 'keyword' in sanitized:
        keyword = sanitized['keyword']
        # Remove potentially harmful characters
        sanitized['keyword'] = ''.join(
            char for char in keyword 
            if char.isalnum() or char.isspace() or char in '-_'
        ).strip()
    
    # Ensure numeric fields are within reasonable ranges
    numeric_fields = ['search_volume', 'difficulty', 'relevance_score']
    for field in numeric_fields:
        if field in sanitized and isinstance(sanitized[field], (int, float)):
            sanitized[field] = max(0, min(1000000, sanitized[field]))  # Reasonable bounds
    
    return sanitized
