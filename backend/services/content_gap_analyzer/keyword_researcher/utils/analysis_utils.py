"""
Analysis Utilities

Utility functions for data analysis, statistical functions, and pattern analysis.
"""

from typing import Dict, Any, List, Optional, Tuple
from collections import Counter, defaultdict
import statistics
from loguru import logger

from ..constants import (
    MIN_OPPORTUNITY_SCORE,
    MAX_DIFFICULTY_SCORE,
    HIGH_VOLUME_THRESHOLD,
    LOW_COMPETITION_THRESHOLD,
    DEFAULT_CONFIDENCE_SCORE
)
from ..enums import IntentType, PriorityLevel, CompetitionLevel


def analyze_intent_patterns(keyword_intents: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze patterns in keyword intents.
    
    Args:
        keyword_intents: Dictionary of keyword intent analyses
        
    Returns:
        Dictionary with pattern analysis results
    """
    if not keyword_intents:
        return {
            'intent_distribution': {},
            'dominant_intent': IntentType.INFORMATIONAL,
            'intent_mix': 'focused',
            'total_keywords': 0
        }
    
    # Count intent types
    intent_counts = Counter(intent['intent_type'] for intent in keyword_intents.values())
    total_keywords = len(keyword_intents)
    
    # Calculate distribution
    intent_distribution = {
        intent: count / total_keywords for intent, count in intent_counts.items()
    }
    
    # Determine dominant intent
    dominant_intent = intent_counts.most_common(1)[0][0] if intent_counts else IntentType.INFORMATIONAL
    
    # Determine intent mix
    intent_mix = 'balanced' if len(intent_counts) >= 3 else 'focused'
    
    return {
        'intent_distribution': intent_distribution,
        'dominant_intent': dominant_intent,
        'intent_mix': intent_mix,
        'total_keywords': total_keywords,
        'intent_counts': dict(intent_counts)
    }


def map_user_journey(keyword_intents: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map user journey based on keyword intents.
    
    Args:
        keyword_intents: Dictionary of keyword intent analyses
        
    Returns:
        Dictionary with user journey mapping
    """
    journey_stages = {
        'awareness': [],
        'consideration': [],
        'decision': []
    }
    
    for keyword, intent in keyword_intents.items():
        intent_type = intent.get('intent_type', IntentType.INFORMATIONAL)
        
        if intent_type == IntentType.INFORMATIONAL:
            journey_stages['awareness'].append(keyword)
        elif intent_type == IntentType.COMMERCIAL:
            journey_stages['consideration'].append(keyword)
        elif intent_type == IntentType.TRANSACTIONAL:
            journey_stages['decision'].append(keyword)
    
    content_strategy = {
        'awareness': 'Educational content and guides',
        'consideration': 'Comparison and review content',
        'decision': 'Product and pricing content'
    }
    
    return {
        'journey_stages': journey_stages,
        'content_strategy': content_strategy,
        'stage_distribution': {
            stage: len(keywords) for stage, keywords in journey_stages.items()
        }
    }


def calculate_opportunity_score(
    search_volume: int,
    difficulty: float,
    trend_score: float = 0.5,
    relevance_score: float = 0.8
) -> Dict[str, float]:
    """
    Calculate opportunity score for a keyword.
    
    Args:
        search_volume: Monthly search volume
        difficulty: Difficulty score (0-100)
        trend_score: Trend score (0-1)
        relevance_score: Relevance score (0-1)
        
    Returns:
        Dictionary with opportunity score components
    """
    # Normalize scores
    volume_score = min(1.0, search_volume / HIGH_VOLUME_THRESHOLD)
    competition_score = max(0.0, (100 - difficulty) / 100)  # Invert difficulty
    
    # Calculate weighted opportunity score
    weights = {
        'volume': 0.3,
        'competition': 0.25,
        'trend': 0.2,
        'relevance': 0.25
    }
    
    overall_score = (
        volume_score * weights['volume'] +
        competition_score * weights['competition'] +
        trend_score * weights['trend'] +
        relevance_score * weights['relevance']
    ) * 100  # Convert to 0-100 scale
    
    return {
        'overall_score': round(overall_score, 2),
        'volume_score': round(volume_score * 100, 2),
        'competition_score': round(competition_score * 100, 2),
        'trend_score': round(trend_score * 100, 2),
        'relevance_score': round(relevance_score * 100, 2)
    }


def categorize_opportunity_type(
    search_volume: int,
    difficulty: float,
    trend_direction: str = "stable"
) -> str:
    """
    Categorize the type of opportunity.
    
    Args:
        search_volume: Monthly search volume
        difficulty: Difficulty score (0-100)
        trend_direction: Trend direction
        
    Returns:
        Opportunity type string
    """
    if search_volume > HIGH_VOLUME_THRESHOLD and difficulty < LOW_COMPETITION_THRESHOLD:
        return 'high_volume_low_competition'
    elif search_volume > HIGH_VOLUME_THRESHOLD / 2 and difficulty < MAX_DIFFICULTY_SCORE:
        return 'medium_volume_medium_competition'
    elif trend_direction == 'rising':
        return 'trending_keyword'
    elif difficulty < LOW_COMPETITION_THRESHOLD:
        return 'low_competition_opportunity'
    else:
        return 'standard_opportunity'


def analyze_keyword_distribution(keywords: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze the distribution of keywords.
    
    Args:
        keywords: List of keyword dictionaries with metrics
        
    Returns:
        Dictionary with distribution analysis
    """
    if not keywords:
        return {
            'total_keywords': 0,
            'volume_distribution': {},
            'difficulty_distribution': {},
            'opportunity_distribution': {}
        }
    
    # Extract metrics
    volumes = [kw.get('search_volume', 0) for kw in keywords]
    difficulties = [kw.get('difficulty', 0) for kw in keywords]
    
    # Calculate distributions
    volume_distribution = {
        'low': len([v for v in volumes if v < 1000]),
        'medium': len([v for v in volumes if 1000 <= v < 5000]),
        'high': len([v for v in volumes if v >= 5000])
    }
    
    difficulty_distribution = {
        'easy': len([d for d in difficulties if d < 30]),
        'medium': len([d for d in difficulties if 30 <= d < 70]),
        'hard': len([d for d in difficulties if d >= 70])
    }
    
    # Calculate opportunity scores and distribution
    opportunity_scores = []
    opportunity_distribution = {
        'high': 0,
        'medium': 0,
        'low': 0
    }
    
    for kw in keywords:
        score_data = calculate_opportunity_score(
            kw.get('search_volume', 0),
            kw.get('difficulty', 50),
            kw.get('trend_score', 0.5),
            kw.get('relevance_score', 0.8)
        )
        opportunity_scores.append(score_data['overall_score'])
        
        if score_data['overall_score'] >= 75:
            opportunity_distribution['high'] += 1
        elif score_data['overall_score'] >= 50:
            opportunity_distribution['medium'] += 1
        else:
            opportunity_distribution['low'] += 1
    
    return {
        'total_keywords': len(keywords),
        'volume_distribution': volume_distribution,
        'difficulty_distribution': difficulty_distribution,
        'opportunity_distribution': opportunity_distribution,
        'average_volume': statistics.mean(volumes) if volumes else 0,
        'average_difficulty': statistics.mean(difficulties) if difficulties else 0,
        'average_opportunity_score': statistics.mean(opportunity_scores) if opportunity_scores else 0
    }


def identify_content_gaps(keyword_intents: Dict[str, Any], existing_content: List[str]) -> List[str]:
    """
    Identify content gaps based on keyword analysis.
    
    Args:
        keyword_intents: Dictionary of keyword intent analyses
        existing_content: List of existing content topics
        
    Returns:
        List of content gap recommendations
    """
    content_gaps = []
    
    # Group keywords by intent
    intent_groups = defaultdict(list)
    for keyword, intent_data in keyword_intents.items():
        intent_type = intent_data.get('intent_type', IntentType.INFORMATIONAL)
        intent_groups[intent_type].append(keyword)
    
    # Check for gaps in each intent category
    for intent_type, keywords in intent_groups.items():
        # Find keywords that don't have corresponding content
        missing_content = []
        for keyword in keywords:
            if not any(keyword.lower() in content.lower() for content in existing_content):
                missing_content.append(keyword)
        
        if missing_content:
            content_gaps.extend(missing_content)
    
    return content_gaps


def calculate_keyword_similarity(keyword1: str, keyword2: str) -> float:
    """
    Calculate similarity between two keywords using Jaccard similarity.
    
    Args:
        keyword1: First keyword
        keyword2: Second keyword
        
    Returns:
        Similarity score (0-1)
    """
    words1 = set(keyword1.lower().split())
    words2 = set(keyword2.lower().split())
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    if not union:
        return 0.0
    
    return len(intersection) / len(union)


def find_similar_keywords(target_keyword: str, keyword_list: List[str], threshold: float = 0.5) -> List[Tuple[str, float]]:
    """
    Find keywords similar to a target keyword.
    
    Args:
        target_keyword: The keyword to find similarities for
        keyword_list: List of keywords to compare against
        threshold: Minimum similarity threshold
        
    Returns:
        List of tuples (keyword, similarity_score) sorted by similarity
    """
    similar_keywords = []
    
    for keyword in keyword_list:
        if keyword.lower() == target_keyword.lower():
            continue  # Skip exact matches
        
        similarity = calculate_keyword_similarity(target_keyword, keyword)
        if similarity >= threshold:
            similar_keywords.append((keyword, similarity))
    
    # Sort by similarity score (descending)
    similar_keywords.sort(key=lambda x: x[1], reverse=True)
    
    return similar_keywords


def analyze_keyword_clusters(keywords: List[str], similarity_threshold: float = 0.3) -> List[List[str]]:
    """
    Cluster keywords based on similarity.
    
    Args:
        keywords: List of keywords to cluster
        similarity_threshold: Minimum similarity for clustering
        
    Returns:
        List of keyword clusters
    """
    if not keywords:
        return []
    
    clusters = []
    unclustered = keywords.copy()
    
    while unclustered:
        # Start a new cluster with the first unclustered keyword
        current_cluster = [unclustered.pop(0)]
        
        # Find similar keywords for the cluster
        i = 0
        while i < len(unclustered):
            keyword = unclustered[i]
            
            # Check if keyword is similar to any keyword in the current cluster
            is_similar = any(
                calculate_keyword_similarity(keyword, cluster_keyword) >= similarity_threshold
                for cluster_keyword in current_cluster
            )
            
            if is_similar:
                current_cluster.append(keyword)
                unclustered.pop(i)
            else:
                i += 1
        
        clusters.append(current_cluster)
    
    return clusters


def calculate_content_priority(
    opportunity_score: float,
    search_volume: int,
    competition_level: str
) -> PriorityLevel:
    """
    Calculate content creation priority.
    
    Args:
        opportunity_score: Overall opportunity score (0-100)
        search_volume: Monthly search volume
        competition_level: Competition level string
        
    Returns:
        Priority level
    """
    # High priority: high opportunity + good volume + manageable competition
    if (opportunity_score >= 75 and 
        search_volume >= 1000 and 
        competition_level in ['low', 'medium']):
        return PriorityLevel.HIGH
    
    # Medium priority: decent opportunity or volume
    if (opportunity_score >= 50 or search_volume >= 500):
        return PriorityLevel.MEDIUM
    
    # Low priority: everything else
    return PriorityLevel.LOW


def generate_summary_metrics(keywords: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate summary metrics for keyword analysis.
    
    Args:
        keywords: List of keyword dictionaries
        
    Returns:
        Dictionary with summary metrics
    """
    if not keywords:
        return {
            'total_keywords': 0,
            'high_opportunity_keywords': 0,
            'low_competition_keywords': 0,
            'average_opportunity_score': 0,
            'recommended_priority_keywords': 0
        }
    
    # Calculate opportunity scores
    opportunity_scores = []
    high_opportunity_count = 0
    low_competition_count = 0
    high_priority_count = 0
    
    for kw in keywords:
        score_data = calculate_opportunity_score(
            kw.get('search_volume', 0),
            kw.get('difficulty', 50),
            kw.get('trend_score', 0.5),
            kw.get('relevance_score', 0.8)
        )
        
        opportunity_scores.append(score_data['overall_score'])
        
        if score_data['overall_score'] >= 75:
            high_opportunity_count += 1
        
        if kw.get('difficulty', 50) < LOW_COMPETITION_THRESHOLD:
            low_competition_count += 1
        
        priority = calculate_content_priority(
            score_data['overall_score'],
            kw.get('search_volume', 0),
            kw.get('competition_level', 'medium')
        )
        
        if priority in [PriorityLevel.HIGH, PriorityLevel.MEDIUM]:
            high_priority_count += 1
    
    return {
        'total_keywords': len(keywords),
        'high_opportunity_keywords': high_opportunity_count,
        'low_competition_keywords': low_competition_count,
        'average_opportunity_score': statistics.mean(opportunity_scores) if opportunity_scores else 0,
        'recommended_priority_keywords': high_priority_count,
        'opportunity_rate': (high_opportunity_count / len(keywords)) * 100 if keywords else 0
    }


def validate_analysis_results(results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate analysis results for consistency and completeness.
    
    Args:
        results: Analysis results to validate
        
    Returns:
        Dictionary with validation results
    """
    validation_errors = []
    validation_warnings = []
    
    # Check required fields
    required_fields = ['trend_analysis', 'intent_analysis', 'opportunities', 'insights']
    for field in required_fields:
        if field not in results:
            validation_errors.append(f"Missing required field: {field}")
    
    # Validate data types
    if 'opportunities' in results and not isinstance(results['opportunities'], list):
        validation_errors.append("Opportunities should be a list")
    
    if 'insights' in results and not isinstance(results['insights'], list):
        validation_errors.append("Insights should be a list")
    
    # Check for empty results
    if 'opportunities' in results and len(results['opportunities']) == 0:
        validation_warnings.append("No opportunities identified")
    
    if 'insights' in results and len(results['insights']) == 0:
        validation_warnings.append("No insights generated")
    
    # Validate opportunity data structure
    if 'opportunities' in results:
        for i, opportunity in enumerate(results['opportunities']):
            if not isinstance(opportunity, dict):
                validation_errors.append(f"Opportunity {i} should be a dictionary")
                continue
            
            required_opportunity_fields = ['keyword', 'opportunity_type', 'search_volume']
            for field in required_opportunity_fields:
                if field not in opportunity:
                    validation_errors.append(f"Opportunity {i} missing field: {field}")
    
    return {
        'is_valid': len(validation_errors) == 0,
        'errors': validation_errors,
        'warnings': validation_warnings,
        'validation_summary': f"Valid: {len(validation_errors) == 0}, Errors: {len(validation_errors)}, Warnings: {len(validation_warnings)}"
    }
