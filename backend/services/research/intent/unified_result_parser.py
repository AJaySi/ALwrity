"""
Result parsing logic for unified research analyzer.

Parses LLM response into structured ResearchIntent, ResearchQuery,
and configuration dictionaries.
"""

from typing import Dict, Any, List
from loguru import logger

from models.research_intent_models import (
    ResearchIntent, ResearchQuery,
    ResearchPurpose, ContentOutput, ExpectedDeliverable,
    ResearchDepthLevel, InputType
)
from .query_deduplicator import deduplicate_queries


def _normalize_purpose(value: str) -> str:
    """Normalize purpose value to enum."""
    if not value or not isinstance(value, str):
        return "learn"
    value_lower = value.lower()
    # Check for exact match
    for purpose in ResearchPurpose:
        if value_lower == purpose.value or value_lower == purpose.name.lower():
            return purpose.value
    # Check for keywords in description
    if "content" in value_lower or "write" in value_lower or "create" in value_lower or "blog" in value_lower:
        return "create_content"
    elif "compare" in value_lower or "comparison" in value_lower:
        return "compare"
    elif "decision" in value_lower or "choose" in value_lower:
        return "make_decision"
    elif "problem" in value_lower or "solve" in value_lower:
        return "solve_problem"
    elif "data" in value_lower or "statistic" in value_lower or "fact" in value_lower:
        return "find_data"
    elif "trend" in value_lower:
        return "explore_trends"
    elif "validat" in value_lower or "verify" in value_lower:
        return "validate"
    elif "idea" in value_lower or "brainstorm" in value_lower:
        return "generate_ideas"
    return "learn"


def _normalize_content_output(value: str) -> str:
    """Normalize content_output value to enum."""
    if not value or not isinstance(value, str):
        return "general"
    value_lower = value.lower()
    # Check for exact match
    for output in ContentOutput:
        if value_lower == output.value or value_lower == output.name.lower():
            return output.value
    # Check for keywords
    if "blog" in value_lower or "article" in value_lower:
        return "blog"
    elif "podcast" in value_lower:
        return "podcast"
    elif "video" in value_lower:
        return "video"
    elif "social" in value_lower or "post" in value_lower:
        return "social_post"
    elif "newsletter" in value_lower:
        return "newsletter"
    elif "presentation" in value_lower or "slide" in value_lower:
        return "presentation"
    elif "report" in value_lower:
        return "report"
    elif "whitepaper" in value_lower or "white paper" in value_lower:
        return "whitepaper"
    elif "email" in value_lower:
        return "email"
    return "general"


def _normalize_deliverable(value: str) -> str:
    """Normalize deliverable value to enum."""
    if not value or not isinstance(value, str):
        return "key_statistics"
    value_lower = value.lower().strip()
    # Check for exact match first
    for deliverable in ExpectedDeliverable:
        if value_lower == deliverable.value or value_lower == deliverable.name.lower():
            return deliverable.value
    # Check for keywords (more aggressive matching)
    if "statistic" in value_lower or "data" in value_lower or "number" in value_lower or "metric" in value_lower or "report" in value_lower:
        return "key_statistics"
    elif "quote" in value_lower or "expert" in value_lower:
        return "expert_quotes"
    elif "case" in value_lower or "study" in value_lower:
        return "case_studies"
    elif "compar" in value_lower or "compare" in value_lower or "landscape" in value_lower or "matrix" in value_lower:
        return "comparisons"
    elif "trend" in value_lower or "keyword" in value_lower or "seo" in value_lower:
        return "trends"
    elif "practice" in value_lower or "best" in value_lower or "guideline" in value_lower or "recommendation" in value_lower or "calendar" in value_lower:
        return "best_practices"
    elif "step" in value_lower or "how" in value_lower or "process" in value_lower or "guide" in value_lower or "outline" in value_lower or "heading" in value_lower:
        return "step_by_step"
    elif ("pro" in value_lower and "con" in value_lower) or "advantage" in value_lower or "disadvantage" in value_lower:
        return "pros_cons"
    elif "defin" in value_lower or "explain" in value_lower:
        return "definitions"
    elif "citation" in value_lower or "source" in value_lower or "reference" in value_lower:
        return "citations"
    elif "example" in value_lower or "sample" in value_lower:
        return "examples"
    elif "prediction" in value_lower or "future" in value_lower or "outlook" in value_lower:
        return "predictions"
    # Default fallback
    return "key_statistics"


def parse_unified_result(result: Dict[str, Any], user_input: str) -> Dict[str, Any]:
    """
    Parse the unified LLM result into structured response.
    
    Args:
        result: Raw LLM response dictionary
        user_input: Original user input for fallback values
        
    Returns:
        Structured response with intent, queries, configs, etc.
    """
    intent_data = result.get("intent", {})
    
    # Normalize enum values
    purpose_value = _normalize_purpose(intent_data.get("purpose", "learn"))
    content_output_value = _normalize_content_output(intent_data.get("content_output", "general"))
    
    # Normalize deliverables list
    deliverables_raw = intent_data.get("expected_deliverables", ["key_statistics"])
    if not isinstance(deliverables_raw, list):
        deliverables_raw = [deliverables_raw] if deliverables_raw else ["key_statistics"]
    normalized_deliverables = [_normalize_deliverable(d) for d in deliverables_raw if d]
    if not normalized_deliverables:
        normalized_deliverables = ["key_statistics"]
    
    # Build ResearchIntent
    try:
        intent = ResearchIntent(
            primary_question=intent_data.get("primary_question", user_input),
            secondary_questions=intent_data.get("secondary_questions", []),
            purpose=purpose_value,
            content_output=content_output_value,
            expected_deliverables=normalized_deliverables,
            depth=intent_data.get("depth", "detailed"),
            focus_areas=intent_data.get("focus_areas", []),
            also_answering=intent_data.get("also_answering", []),
            perspective=intent_data.get("perspective"),
            time_sensitivity=intent_data.get("time_sensitivity"),
            input_type=intent_data.get("input_type", "keywords"),
            original_input=user_input,
            confidence=float(intent_data.get("confidence", 0.7)),
            confidence_reason=intent_data.get("confidence_reason"),
            great_example=intent_data.get("great_example"),
            needs_clarification=intent_data.get("needs_clarification", False),
            clarifying_questions=intent_data.get("clarifying_questions", []),
        )
    except Exception as e:
        logger.error(f"Failed to parse intent: {e}, intent_data: {intent_data}")
        # Return fallback intent
        from .unified_analyzer_utils import create_fallback_response
        return create_fallback_response(user_input, [])
    
    # Build queries
    queries = []
    for q in result.get("queries", []):
        try:
            # Normalize query purpose
            query_purpose = _normalize_deliverable(q.get("purpose", "key_statistics"))
            queries.append(ResearchQuery(
                query=q.get("query", ""),
                purpose=query_purpose,
                provider=q.get("provider", "exa"),
                priority=int(q.get("priority", 3)),
                expected_results=q.get("expected_results", ""),
                addresses_primary_question=q.get("addresses_primary_question", False),
                addresses_secondary_questions=q.get("addresses_secondary_questions", []),
                targets_focus_areas=q.get("targets_focus_areas", []),
                covers_also_answering=q.get("covers_also_answering", []),
                justification=q.get("justification"),
            ))
        except Exception as e:
            logger.warning(f"Failed to parse query: {e}, query: {q}")
    
    # Deduplicate queries to avoid redundant API calls
    queries = deduplicate_queries(queries, intent)
    
    # Log warning if no queries after parsing
    if not queries:
        logger.warning("No valid queries parsed from LLM response")
    
    return {
        "success": True,
        "intent": intent,
        "queries": queries,
        "enhanced_keywords": result.get("enhanced_keywords", []),
        "research_angles": result.get("research_angles", []),
        "recommended_provider": result.get("recommended_provider", "exa"),
        "provider_justification": result.get("provider_justification", ""),
        "exa_config": result.get("exa_config", {}),
        "tavily_config": result.get("tavily_config", {}),
        "trends_config": result.get("trends_config", {}),  # Google Trends configuration
        "analysis_summary": intent_data.get("analysis_summary", ""),
    }
