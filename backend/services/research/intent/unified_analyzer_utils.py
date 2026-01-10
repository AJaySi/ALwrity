"""
Utility functions for unified research analyzer.

Provides helper functions for date context, persona context,
competitor context, and fallback response creation.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional

from models.research_intent_models import ResearchIntent, ResearchQuery
from models.research_persona_models import ResearchPersona


def get_current_date_context() -> str:
    """Get current date/time context for prompts."""
    now = datetime.now()
    current_year = now.year
    current_month = now.strftime("%B")  # Full month name
    current_date = now.strftime("%Y-%m-%d")
    return f"CURRENT DATE: {current_date} ({current_month} {current_year})\nCURRENT YEAR: {current_year}"


def build_persona_context(
    research_persona: Optional[ResearchPersona],
    industry: Optional[str],
    target_audience: Optional[str],
) -> str:
    """Build persona context section."""
    parts = []
    
    if research_persona:
        if research_persona.default_industry:
            parts.append(f"Industry: {research_persona.default_industry}")
        if research_persona.default_target_audience:
            parts.append(f"Target Audience: {research_persona.default_target_audience}")
        if research_persona.research_angles:
            parts.append(f"Preferred Research Angles: {', '.join(research_persona.research_angles[:3])}")
        if research_persona.suggested_keywords:
            parts.append(f"Relevant Keywords: {', '.join(research_persona.suggested_keywords[:5])}")
    else:
        if industry:
            parts.append(f"Industry: {industry}")
        if target_audience:
            parts.append(f"Target Audience: {target_audience}")
    
    if not parts:
        return "No specific user context available. Use general best practices."
    
    return "\n".join(parts)


def build_competitor_context(competitor_data: Optional[List[Dict]]) -> str:
    """Build competitor context section."""
    if not competitor_data:
        return ""
    
    competitor_names = [c.get("name", c.get("url", "")) for c in competitor_data[:5]]
    if competitor_names:
        return f"\nKnown Competitors: {', '.join(competitor_names)}"
    return ""


def create_fallback_response(user_input: str, keywords: List[str]) -> Dict[str, Any]:
    """Create fallback response when analysis fails."""
    return {
        "success": False,
        "intent": ResearchIntent(
            primary_question=f"What are the key insights about: {user_input}?",
            purpose="learn",
            content_output="general",
            expected_deliverables=["key_statistics", "best_practices"],
            depth="detailed",
            focus_areas=[],
            also_answering=[],
            original_input=user_input,
            confidence=0.5,
        ),
        "queries": [
            ResearchQuery(
                query=user_input,
                purpose="key_statistics",
                provider="exa",
                priority=5,
                expected_results="General research results",
                addresses_primary_question=True,
                addresses_secondary_questions=[],
                targets_focus_areas=[],
                covers_also_answering=[],
            )
        ],
        "enhanced_keywords": keywords,
        "research_angles": [],
        "recommended_provider": "exa",
        "provider_justification": "Default fallback to Exa for semantic search",
        "exa_config": {
            "enabled": True,
            "type": "auto",
            "type_justification": "Auto mode for balanced results",
            "numResults": 10,
            "highlights": True,
        },
        "tavily_config": {
            "enabled": True,
            "topic": "general",
            "search_depth": "advanced",
            "include_answer": True,
        },
        "trends_config": {
            "enabled": False,  # Disabled in fallback
        },
    }
