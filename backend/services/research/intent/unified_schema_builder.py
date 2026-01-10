"""
JSON schema builder for unified research analyzer.

Defines the structured JSON schema that the LLM must return
for intent analysis, query generation, and parameter optimization.
"""

from typing import Dict, Any


def build_unified_schema() -> Dict[str, Any]:
    """
    Build the JSON schema for unified response.
    
    This schema defines the structure expected from the LLM
    for intent + queries + provider settings.
    """
    return {
        "type": "object",
        "properties": {
            "intent": {
                "type": "object",
                "properties": {
                    "input_type": {"type": "string", "enum": ["keywords", "question", "goal", "mixed"]},
                    "primary_question": {"type": "string"},
                    "secondary_questions": {"type": "array", "items": {"type": "string"}},
                    "purpose": {"type": "string"},
                    "content_output": {"type": "string"},
                    "expected_deliverables": {"type": "array", "items": {"type": "string"}},
                    "depth": {"type": "string", "enum": ["overview", "detailed", "expert"]},
                    "focus_areas": {"type": "array", "items": {"type": "string"}},
                    "also_answering": {"type": "array", "items": {"type": "string"}},
                    "perspective": {"type": "string"},
                    "time_sensitivity": {"type": "string"},
                    "confidence": {"type": "number"},
                    "confidence_reason": {"type": "string"},
                    "great_example": {"type": "string"},
                    "needs_clarification": {"type": "boolean"},
                    "clarifying_questions": {"type": "array", "items": {"type": "string"}},
                    "analysis_summary": {"type": "string"}
                },
                "required": ["primary_question", "purpose", "expected_deliverables", "confidence"]
            },
            "queries": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "purpose": {"type": "string"},
                        "provider": {"type": "string"},
                        "priority": {"type": "integer"},
                        "expected_results": {"type": "string"},
                        "justification": {"type": "string"},
                        "addresses_primary_question": {"type": "boolean"},
                        "addresses_secondary_questions": {"type": "array", "items": {"type": "string"}},
                        "targets_focus_areas": {"type": "array", "items": {"type": "string"}},
                        "covers_also_answering": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["query", "purpose", "provider", "priority", "addresses_primary_question"]
                }
            },
            "enhanced_keywords": {"type": "array", "items": {"type": "string"}},
            "research_angles": {"type": "array", "items": {"type": "string"}},
            "recommended_provider": {"type": "string"},
            "provider_justification": {"type": "string"},
            "exa_config": {
                "type": "object",
                "properties": {
                    "enabled": {"type": "boolean"},
                    "type": {"type": "string"},
                    "type_justification": {"type": "string"},
                    "category": {"type": "string"},
                    "category_justification": {"type": "string"},
                    "numResults": {"type": "integer"},
                    "numResults_justification": {"type": "string"},
                    "includeDomains": {"type": "array", "items": {"type": "string"}},
                    "includeDomains_justification": {"type": "string"},
                    "startPublishedDate": {"type": "string"},
                    "date_justification": {"type": "string"},
                    "highlights": {"type": "boolean"},
                    "highlights_justification": {"type": "string"},
                    "context": {"type": "boolean"},
                    "context_justification": {"type": "string"},
                    "additionalQueries": {"type": "array", "items": {"type": "string"}},
                    "additionalQueries_justification": {"type": "string"},
                    "livecrawl": {"type": "string"},
                    "livecrawl_justification": {"type": "string"}
                }
            },
            "tavily_config": {
                "type": "object",
                "properties": {
                    "enabled": {"type": "boolean"},
                    "topic": {"type": "string"},
                    "topic_justification": {"type": "string"},
                    "search_depth": {"type": "string"},
                    "search_depth_justification": {"type": "string"},
                    "include_answer": {"oneOf": [{"type": "string"}, {"type": "boolean"}]},
                    "include_answer_justification": {"type": "string"},
                    "time_range": {"oneOf": [{"type": "string"}, {"type": "null"}]},
                    "time_range_justification": {"type": "string"},
                    "start_date": {"oneOf": [{"type": "string"}, {"type": "null"}]},
                    "start_date_justification": {"type": "string"},
                    "end_date": {"oneOf": [{"type": "string"}, {"type": "null"}]},
                    "end_date_justification": {"type": "string"},
                    "max_results": {"type": "integer"},
                    "max_results_justification": {"type": "string"},
                    "chunks_per_source": {"type": "integer"},
                    "chunks_per_source_justification": {"type": "string"},
                    "include_raw_content": {"oneOf": [{"type": "string"}, {"type": "boolean"}]},
                    "include_raw_content_justification": {"type": "string"},
                    "country": {"oneOf": [{"type": "string"}, {"type": "null"}]},
                    "country_justification": {"type": "string"},
                    "include_images": {"type": "boolean"},
                    "include_images_justification": {"type": "string"},
                    "include_image_descriptions": {"type": "boolean"},
                    "include_image_descriptions_justification": {"type": "string"},
                    "include_favicon": {"type": "boolean"},
                    "include_favicon_justification": {"type": "string"},
                    "auto_parameters": {"type": "boolean"},
                    "auto_parameters_justification": {"type": "string"}
                }
            },
            "trends_config": {
                "type": "object",
                "properties": {
                    "enabled": {"type": "boolean"},
                    "keywords": {"type": "array", "items": {"type": "string"}},
                    "keywords_justification": {"type": "string"},
                    "timeframe": {"type": "string"},
                    "timeframe_justification": {"type": "string"},
                    "geo": {"type": "string"},
                    "geo_justification": {"type": "string"},
                    "expected_insights": {"type": "array", "items": {"type": "string"}}
                }
            }
        },
        "required": ["intent", "queries", "recommended_provider", "exa_config", "tavily_config"]
    }
