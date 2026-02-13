"""
Keyword Researcher Utilities

This package contains utility functions for keyword researcher services.
Utilities are organized by functional domain for better maintainability.
"""

# Import all utility modules
from .keyword_utils import (
    validate_keyword,
    normalize_keyword,
    generate_keyword_variations,
    generate_long_tail_keywords,
    generate_semantic_variations,
    generate_related_keywords,
    categorize_keywords_by_intent,
    analyze_single_keyword_intent,
    calculate_keyword_metrics,
    remove_duplicate_keywords,
    sort_keywords_by_relevance,
    extract_keywords_from_text,
    filter_keywords_by_length,
    merge_keyword_lists,
    get_keyword_statistics,
)

from .analysis_utils import (
    analyze_intent_patterns,
    map_user_journey,
    calculate_opportunity_score,
    categorize_opportunity_type,
    analyze_keyword_distribution,
    identify_content_gaps,
    calculate_keyword_similarity,
    find_similar_keywords,
    analyze_keyword_clusters,
    calculate_content_priority,
    generate_summary_metrics,
    validate_analysis_results,
)

from .ai_prompt_utils import (
    generate_trend_analysis_prompt,
    generate_trend_analysis_schema,
    generate_intent_analysis_prompt,
    generate_intent_analysis_schema,
    generate_opportunity_identification_prompt,
    generate_opportunity_identification_schema,
    generate_insights_prompt,
    generate_insights_schema,
    generate_content_format_prompt,
    generate_content_format_schema,
    generate_topic_cluster_prompt,
    generate_topic_cluster_schema,
    parse_ai_response,
    validate_ai_response,
    create_fallback_response,
    get_content_recommendations_by_intent,
    get_opportunity_recommendation,
)

from .data_transformers import (
    transform_legacy_analysis_to_modern,
    transform_legacy_trend_analysis,
    transform_legacy_opportunities,
    transform_trend_direction,
    transform_competition_level,
    transform_search_intent,
    transform_priority,
    transform_keyword_expansion_results,
    transform_content_recommendations,
    calculate_content_priorities,
    generate_implementation_roadmap,
    transform_analysis_summary,
    transform_health_check_results,
    serialize_analysis_results,
    deserialize_analysis_results,
    validate_data_structure,
    sanitize_keyword_data,
)

# Export all utilities for easy import
__all__ = [
    # Keyword Utils
    "validate_keyword",
    "normalize_keyword",
    "generate_keyword_variations",
    "generate_long_tail_keywords",
    "generate_semantic_variations",
    "generate_related_keywords",
    "categorize_keywords_by_intent",
    "analyze_single_keyword_intent",
    "calculate_keyword_metrics",
    "remove_duplicate_keywords",
    "sort_keywords_by_relevance",
    "extract_keywords_from_text",
    "filter_keywords_by_length",
    "merge_keyword_lists",
    "get_keyword_statistics",
    
    # Analysis Utils
    "analyze_intent_patterns",
    "map_user_journey",
    "calculate_opportunity_score",
    "categorize_opportunity_type",
    "analyze_keyword_distribution",
    "identify_content_gaps",
    "calculate_keyword_similarity",
    "find_similar_keywords",
    "analyze_keyword_clusters",
    "calculate_content_priority",
    "generate_summary_metrics",
    "validate_analysis_results",
    
    # AI Prompt Utils
    "generate_trend_analysis_prompt",
    "generate_trend_analysis_schema",
    "generate_intent_analysis_prompt",
    "generate_intent_analysis_schema",
    "generate_opportunity_identification_prompt",
    "generate_opportunity_identification_schema",
    "generate_insights_prompt",
    "generate_insights_schema",
    "generate_content_format_prompt",
    "generate_content_format_schema",
    "generate_topic_cluster_prompt",
    "generate_topic_cluster_schema",
    "parse_ai_response",
    "validate_ai_response",
    "create_fallback_response",
    "get_content_recommendations_by_intent",
    "get_opportunity_recommendation",
    
    # Data Transformers
    "transform_legacy_analysis_to_modern",
    "transform_legacy_trend_analysis",
    "transform_legacy_opportunities",
    "transform_trend_direction",
    "transform_competition_level",
    "transform_search_intent",
    "transform_priority",
    "transform_keyword_expansion_results",
    "transform_content_recommendations",
    "calculate_content_priorities",
    "generate_implementation_roadmap",
    "transform_analysis_summary",
    "transform_health_check_results",
    "serialize_analysis_results",
    "deserialize_analysis_results",
    "validate_data_structure",
    "sanitize_keyword_data",
]

# Version information
__version__ = "1.0.0"
__description__ = "Utility functions for keyword researcher service"
