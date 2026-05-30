"""
Strategy utility functions for analysis, scoring, and data processing.
Provides utility functions for content strategy operations including strategic scoring,
market positioning analysis, competitive advantages, risk assessment, and opportunity analysis.
"""

import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)


def calculate_strategic_scores(ai_recommendations: Dict[str, Any]) -> Dict[str, float]:
    """
    Calculate strategic performance scores from AI recommendations.
    Dimension-specific weights — no blanket multipliers.
    
    Args:
        ai_recommendations: Dictionary containing AI analysis results
        
    Returns:
        Dictionary with calculated strategic scores
    """
    scores = {
        'overall_score': 0.0,
        'content_quality_score': 0.0,
        'engagement_score': 0.0,
        'conversion_score': 0.0,
        'innovation_score': 0.0
    }

    weight_sum = 0.0

    dimension_weights = {
        'comprehensive_strategy': {'quality': 0.35, 'engagement': 0.20, 'conversion': 0.25, 'innovation': 0.20},
        'audience_intelligence': {'quality': 0.25, 'engagement': 0.40, 'conversion': 0.20, 'innovation': 0.15},
        'competitive_intelligence': {'quality': 0.30, 'engagement': 0.15, 'conversion': 0.25, 'innovation': 0.30},
        'performance_optimization': {'quality': 0.20, 'engagement': 0.15, 'conversion': 0.45, 'innovation': 0.20},
        'content_calendar_optimization': {'quality': 0.30, 'engagement': 0.25, 'conversion': 0.20, 'innovation': 0.25},
    }

    for analysis_type, recommendations in ai_recommendations.items():
        if not isinstance(recommendations, dict):
            continue
        metrics = recommendations.get('metrics')
        if not isinstance(metrics, dict):
            continue

        score = metrics.get('score', 50)
        confidence = metrics.get('confidence', 0.5)
        weight = confidence

        scores['overall_score'] += score * weight
        weight_sum += weight

        weights = dimension_weights.get(analysis_type, {'quality': 0.25, 'engagement': 0.25, 'conversion': 0.25, 'innovation': 0.25})
        scores['content_quality_score'] += score * weights['quality'] * weight
        scores['engagement_score'] += score * weights['engagement'] * weight
        scores['conversion_score'] += score * weights['conversion'] * weight
        scores['innovation_score'] += score * weights['innovation'] * weight

    if weight_sum > 0:
        for k in scores:
            scores[k] = round(scores[k] / weight_sum, 2)

    return scores


def extract_market_positioning(ai_recommendations: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract market positioning insights from AI recommendations.
    Scans all analysis types for positioning signals. Returns empty dict if none found.
    
    Args:
        ai_recommendations: Dictionary containing AI analysis results
        
    Returns:
        Dictionary with market positioning data
    """
    positioning = {}
    best_confidence = 0.0

    for analysis_type, recommendations in ai_recommendations.items():
        if not isinstance(recommendations, dict):
            continue
        metrics = recommendations.get('metrics', {})
        confidence = metrics.get('confidence', 0.0)
        if confidence <= best_confidence:
            continue

        recs = recommendations.get('recommendations', [])
        if isinstance(recs, list):
            for r in recs:
                if not isinstance(r, dict):
                    continue
                pos = r.get('market_position') or r.get('positioning')
                adv = r.get('competitive_advantage')
                share = r.get('market_share')
                score = r.get('positioning_score') or metrics.get('positioning_score')
                if any([pos, adv, share, score]):
                    best_confidence = confidence
                    if pos:
                        positioning['industry_position'] = pos
                    if adv:
                        positioning['competitive_advantage'] = adv
                    if share:
                        positioning['market_share'] = str(share)
                    if score is not None:
                        positioning['positioning_score'] = score

    if not positioning:
        for key in ('industry_position', 'competitive_advantage', 'market_share', 'positioning_score'):
            val = ai_recommendations.get(key)
            if val is not None:
                positioning[key] = val

    return positioning


def extract_competitive_advantages(ai_recommendations: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract competitive advantages from AI recommendations.
    Scans all analysis types for advantage signals. Returns empty list if none found.
    
    Args:
        ai_recommendations: Dictionary containing AI analysis results
        
    Returns:
        List of competitive advantages with impact and implementation status
    """
    advantages = []

    for analysis_type, recommendations in ai_recommendations.items():
        if not isinstance(recommendations, dict):
            continue
        recs = recommendations.get('recommendations', [])
        if not isinstance(recs, list):
            continue
        for r in recs:
            if not isinstance(r, dict):
                continue
            adv = r.get('advantage') or r.get('competitive_advantage')
            if adv:
                advantages.append({
                    'advantage': adv,
                    'impact': r.get('impact', 'Medium'),
                    'implementation': r.get('implementation', 'Planned')
                })

    seen = set()
    unique = []
    for a in advantages:
        key = a['advantage'].strip().lower()
        if key not in seen:
            seen.add(key)
            unique.append(a)

    return unique


def extract_strategic_risks(ai_recommendations: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract strategic risks from AI recommendations.
    Scans all analysis types for risk signals. Returns empty list if none found.
    
    Args:
        ai_recommendations: Dictionary containing AI analysis results
        
    Returns:
        List of strategic risks with probability and impact assessment
    """
    risks = []

    for analysis_type, recommendations in ai_recommendations.items():
        if not isinstance(recommendations, dict):
            continue
        recs = recommendations.get('recommendations', [])
        if not isinstance(recs, list):
            continue
        for r in recs:
            if not isinstance(r, dict):
                continue
            risk_text = r.get('risk') or r.get('strategic_risk') or r.get('threat')
            if risk_text:
                risks.append({
                    'risk': risk_text,
                    'probability': r.get('probability', 'Medium'),
                    'impact': r.get('impact', 'Medium')
                })

        risks_list = recommendations.get('risks') or recommendations.get('strategic_risks')
        if isinstance(risks_list, list):
            for r in risks_list:
                if isinstance(r, dict) and r.get('risk'):
                    risks.append(r)

    seen = set()
    unique = []
    for r in risks:
        key = r['risk'].strip().lower()
        if key not in seen:
            seen.add(key)
            unique.append(r)

    return unique


def extract_opportunity_analysis(ai_recommendations: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract opportunity analysis from AI recommendations.
    Scans all analysis types for opportunity signals. Returns empty list if none found.
    
    Args:
        ai_recommendations: Dictionary containing AI analysis results
        
    Returns:
        List of opportunities with potential impact and implementation ease
    """
    opportunities = []

    for analysis_type, recommendations in ai_recommendations.items():
        if not isinstance(recommendations, dict):
            continue
        recs = recommendations.get('recommendations', [])
        if not isinstance(recs, list):
            continue
        for r in recs:
            if not isinstance(r, dict):
                continue
            opp = r.get('opportunity') or r.get('growth_opportunity')
            if opp:
                opportunities.append({
                    'opportunity': opp,
                    'potential_impact': r.get('potential_impact', 'Medium'),
                    'implementation_ease': r.get('implementation_ease', 'Medium')
                })

        opps_list = recommendations.get('opportunities') or recommendations.get('growth_opportunities')
        if isinstance(opps_list, list):
            for o in opps_list:
                if isinstance(o, dict) and o.get('opportunity'):
                    opportunities.append(o)

    seen = set()
    unique = []
    for o in opportunities:
        key = o['opportunity'].strip().lower()
        if key not in seen:
            seen.add(key)
            unique.append(o)

    return unique


def initialize_caches() -> Dict[str, Any]:
    """
    Initialize in-memory caches for strategy operations.
    
    Returns:
        Dictionary with initialized cache structures
    """
    return {
        'performance_metrics': {
            'response_times': [],
            'cache_hit_rates': {},
            'error_rates': {},
            'throughput_metrics': {}
        },
        'strategy_cache': {},
        'ai_analysis_cache': {},
        'onboarding_cache': {}
    }


def calculate_data_quality_scores(data_sources: Dict[str, Any]) -> Dict[str, float]:
    """
    Calculate data quality scores for different data sources.
    
    Args:
        data_sources: Dictionary containing data source information
        
    Returns:
        Dictionary with quality scores for each data source
    """
    quality_scores = {}
    
    for source_name, source_data in data_sources.items():
        if isinstance(source_data, dict):
            # Calculate quality based on data completeness and freshness
            completeness = source_data.get('completeness', 0.5)
            freshness = source_data.get('freshness', 0.5)
            confidence = source_data.get('confidence', 0.5)
            
            # Weighted average of quality factors
            quality_score = (completeness * 0.4 + freshness * 0.3 + confidence * 0.3)
            quality_scores[source_name] = round(quality_score, 2)
        else:
            quality_scores[source_name] = 0.5  # Default score
    
    return quality_scores


def extract_content_preferences_from_style(writing_style: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract content preferences from writing style analysis.
    
    Args:
        writing_style: Dictionary containing writing style analysis
        
    Returns:
        Dictionary with extracted content preferences
    """
    preferences = {
        'tone': writing_style.get('tone', 'professional'),
        'complexity': writing_style.get('complexity', 'intermediate'),
        'engagement_level': writing_style.get('engagement_level', 'medium'),
        'content_type': writing_style.get('content_type', 'blog')
    }
    
    return preferences


def extract_brand_voice_from_guidelines(style_guidelines: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract brand voice from style guidelines.
    
    Args:
        style_guidelines: Dictionary containing style guidelines
        
    Returns:
        Dictionary with extracted brand voice information
    """
    brand_voice = {
        'tone': style_guidelines.get('tone', 'professional'),
        'personality': style_guidelines.get('personality', 'authoritative'),
        'style': style_guidelines.get('style', 'formal'),
        'voice_characteristics': style_guidelines.get('voice_characteristics', [])
    }
    
    return brand_voice


def extract_editorial_guidelines_from_style(writing_style: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract editorial guidelines from writing style analysis.
    
    Args:
        writing_style: Dictionary containing writing style analysis
        
    Returns:
        Dictionary with extracted editorial guidelines
    """
    guidelines = {
        'sentence_structure': writing_style.get('sentence_structure', 'clear'),
        'vocabulary_level': writing_style.get('vocabulary_level', 'intermediate'),
        'paragraph_organization': writing_style.get('paragraph_organization', 'logical'),
        'style_rules': writing_style.get('style_rules', [])
    }
    
    return guidelines


def create_field_mappings() -> Dict[str, str]:
    """
    Create field mappings for strategy data transformation.
    
    Returns:
        Dictionary mapping field names to their corresponding data sources
    """
    return {
        'business_objectives': 'website_analysis',
        'target_metrics': 'research_preferences',
        'content_budget': 'onboarding_session',
        'team_size': 'onboarding_session',
        'implementation_timeline': 'onboarding_session',
        'market_share': 'website_analysis',
        'competitive_position': 'website_analysis',
        'performance_metrics': 'website_analysis',
        'content_preferences': 'website_analysis',
        'consumption_patterns': 'research_preferences',
        'audience_pain_points': 'website_analysis',
        'buying_journey': 'website_analysis',
        'seasonal_trends': 'research_preferences',
        'engagement_metrics': 'website_analysis',
        'top_competitors': 'website_analysis',
        'competitor_content_strategies': 'website_analysis',
        'market_gaps': 'website_analysis',
        'industry_trends': 'website_analysis',
        'emerging_trends': 'website_analysis',
        'preferred_formats': 'website_analysis',
        'content_mix': 'research_preferences',
        'content_frequency': 'research_preferences',
        'optimal_timing': 'research_preferences',
        'quality_metrics': 'website_analysis',
        'editorial_guidelines': 'website_analysis',
        'brand_voice': 'website_analysis',
        'traffic_sources': 'website_analysis',
        'conversion_rates': 'website_analysis',
        'content_roi_targets': 'website_analysis',
        'ab_testing_capabilities': 'onboarding_session'
    }


class StrategyUtils:
    """
    Utility class for strategy-related operations.
    Provides static methods for strategy analysis and data processing.
    """
    
    @staticmethod
    def calculate_strategic_scores(ai_recommendations: Dict[str, Any]) -> Dict[str, float]:
        """Calculate strategic performance scores from AI recommendations."""
        return calculate_strategic_scores(ai_recommendations)
    
    @staticmethod
    def extract_market_positioning(ai_recommendations: Dict[str, Any]) -> Dict[str, Any]:
        """Extract market positioning insights from AI recommendations."""
        return extract_market_positioning(ai_recommendations)
    
    @staticmethod
    def extract_competitive_advantages(ai_recommendations: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract competitive advantages from AI recommendations."""
        return extract_competitive_advantages(ai_recommendations)
    
    @staticmethod
    def extract_strategic_risks(ai_recommendations: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract strategic risks from AI recommendations."""
        return extract_strategic_risks(ai_recommendations)
    
    @staticmethod
    def extract_opportunity_analysis(ai_recommendations: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract opportunity analysis from AI recommendations."""
        return extract_opportunity_analysis(ai_recommendations)
    
    @staticmethod
    def initialize_caches() -> Dict[str, Any]:
        """Initialize in-memory caches for strategy operations."""
        return initialize_caches()
    
    @staticmethod
    def calculate_data_quality_scores(data_sources: Dict[str, Any]) -> Dict[str, float]:
        """Calculate data quality scores for different data sources."""
        return calculate_data_quality_scores(data_sources)
    
    @staticmethod
    def extract_content_preferences_from_style(writing_style: Dict[str, Any]) -> Dict[str, Any]:
        """Extract content preferences from writing style analysis."""
        return extract_content_preferences_from_style(writing_style)
    
    @staticmethod
    def extract_brand_voice_from_guidelines(style_guidelines: Dict[str, Any]) -> Dict[str, Any]:
        """Extract brand voice from style guidelines."""
        return extract_brand_voice_from_guidelines(style_guidelines)
    
    @staticmethod
    def extract_editorial_guidelines_from_style(writing_style: Dict[str, Any]) -> Dict[str, Any]:
        """Extract editorial guidelines from writing style analysis."""
        return extract_editorial_guidelines_from_style(writing_style)
    
    @staticmethod
    def create_field_mappings() -> Dict[str, str]:
        """Create field mappings for strategy data transformation."""
        return create_field_mappings() 