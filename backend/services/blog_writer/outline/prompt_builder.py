"""
Prompt Builder - Handles building of AI prompts for outline generation.

Constructs comprehensive prompts with research data, keywords, and strategic requirements.
"""

from typing import Dict, Any, List
from loguru import logger


class PromptBuilder:
    """Handles building of comprehensive AI prompts for outline generation."""
    
    def __init__(self):
        """Initialize the prompt builder."""
        pass
    
    def build_outline_prompt(self, primary_keywords: List[str], secondary_keywords: List[str], 
                           content_angles: List[str], sources: List, search_intent: str,
                           request, custom_instructions: str = None) -> str:
        """Build the comprehensive outline generation prompt using filtered research data."""
        
        # Use the filtered research data (already cleaned by ResearchDataFilter)
        research = request.research
        
        return f"""Create a comprehensive blog outline for: {', '.join(primary_keywords)}

CONTEXT:
Search Intent: {search_intent}
Target: {request.word_count or 1500} words
Industry: {getattr(request.persona, 'industry', 'General') if request.persona else 'General'}
Audience: {getattr(request.persona, 'target_audience', 'General') if request.persona else 'General'}

KEYWORDS:
Primary: {', '.join(primary_keywords)}
Secondary: {', '.join(secondary_keywords)}
Long-tail: {', '.join(research.keyword_analysis.get('long_tail', []))}
Semantic: {', '.join(research.keyword_analysis.get('semantic_keywords', []))}
Trending: {', '.join(research.keyword_analysis.get('trending_terms', []))}
Content Gaps: {', '.join(research.keyword_analysis.get('content_gaps', []))}

CONTENT ANGLES: {', '.join(content_angles)}

COMPETITIVE INTELLIGENCE:
Top Competitors: {', '.join(research.competitor_analysis.get('top_competitors', []))}
Market Opportunities: {', '.join(research.competitor_analysis.get('opportunities', []))}
Competitive Advantages: {', '.join(research.competitor_analysis.get('competitive_advantages', []))}

RESEARCH SOURCES: {len(sources)} authoritative sources available

{f"CUSTOM INSTRUCTIONS: {custom_instructions}" if custom_instructions else ""}

STRATEGIC REQUIREMENTS:
- Create SEO-optimized headings with natural keyword integration
- Build logical narrative flow from problem to solution
- Include data-driven insights from research sources
- Address content gaps and market opportunities
- Optimize for search intent and user questions
- Ensure engaging, actionable content throughout

Return JSON format:
{{
            "outline": [
                {{
                    "heading": "Section heading with primary keyword",
                    "subheadings": ["Subheading 1", "Subheading 2", "Subheading 3"],
                    "key_points": ["Key point 1", "Key point 2", "Key point 3"],
            "target_words": 300,
                    "keywords": ["primary keyword", "secondary keyword"]
                }}
            ]
}}"""
    
    def get_outline_schema(self) -> Dict[str, Any]:
        """Get the structured JSON schema for outline generation."""
        return {
            "type": "object",
            "properties": {
                "outline": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "heading": {"type": "string"},
                            "subheadings": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "key_points": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "target_words": {"type": "integer"},
                            "keywords": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["heading", "subheadings", "key_points", "target_words", "keywords"]
                    }
                }
            },
            "required": ["outline"],
            "propertyOrdering": ["outline"]
        }
