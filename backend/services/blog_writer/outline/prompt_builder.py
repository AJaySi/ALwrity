"""
Prompt Builder - Handles building of AI prompts for outline generation.

Constructs comprehensive prompts with research data, keywords, and strategic requirements.
"""

from typing import Dict, Any, List


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
        
        primary_kw_text = ', '.join(primary_keywords) if primary_keywords else (request.topic or ', '.join(getattr(request.research, 'original_keywords', []) or ['the target topic']))
        secondary_kw_text = ', '.join(secondary_keywords) if secondary_keywords else "None provided"
        long_tail_text = ', '.join(research.keyword_analysis.get('long_tail', [])) if research and research.keyword_analysis else "None discovered"
        semantic_text = ', '.join(research.keyword_analysis.get('semantic_keywords', [])) if research and research.keyword_analysis else "None discovered"
        trending_text = ', '.join(research.keyword_analysis.get('trending_terms', [])) if research and research.keyword_analysis else "None discovered"
        content_gap_text = ', '.join(research.keyword_analysis.get('content_gaps', [])) if research and research.keyword_analysis else "None identified"
        content_angle_text = ', '.join(content_angles) if content_angles else "No explicit angles provided; infer compelling angles from research insights."
        competitor_text = ', '.join(research.competitor_analysis.get('top_competitors', [])) if research and research.competitor_analysis else "Not available"
        opportunity_text = ', '.join(research.competitor_analysis.get('opportunities', [])) if research and research.competitor_analysis else "Not available"
        advantages_text = ', '.join(research.competitor_analysis.get('competitive_advantages', [])) if research and research.competitor_analysis else "Not available"

        return f"""Create a comprehensive blog outline for: {primary_kw_text}

CONTEXT:
Search Intent: {search_intent}
Target: {request.word_count or 1500} words
Industry: {getattr(request.persona, 'industry', 'General') if request.persona else 'General'}
Audience: {getattr(request.persona, 'target_audience', 'General') if request.persona else 'General'}

KEYWORDS:
Primary: {primary_kw_text}
Secondary: {secondary_kw_text}
Long-tail: {long_tail_text}
Semantic: {semantic_text}
Trending: {trending_text}
Content Gaps: {content_gap_text}

CONTENT ANGLES / STORYLINES: {content_angle_text}

COMPETITIVE INTELLIGENCE:
Top Competitors: {competitor_text}
Market Opportunities: {opportunity_text}
Competitive Advantages: {advantages_text}

RESEARCH SOURCES: {len(sources)} authoritative sources available

{f"CUSTOM INSTRUCTIONS: {custom_instructions}" if custom_instructions else ""}

STRATEGIC REQUIREMENTS:
- Create SEO-optimized headings with natural keyword integration
- Surface the strongest research-backed angles within the outline
- Build logical narrative flow from problem to solution
- Include data-driven insights from research sources
- Address content gaps and market opportunities
- Optimize for search intent and user questions
- Ensure engaging, actionable content throughout

Return JSON format:
{
    "title_options": [
        "Title option 1",
        "Title option 2",
        "Title option 3"
    ],
    "outline": [
        {
            "heading": "Section heading with primary keyword",
            "subheadings": ["Subheading 1", "Subheading 2", "Subheading 3"],
            "key_points": ["Key point 1", "Key point 2", "Key point 3"],
            "target_words": 300,
            "keywords": ["primary keyword", "secondary keyword"]
        }
    ]
}"""
    
    def get_outline_schema(self) -> Dict[str, Any]:
        """Get the structured JSON schema for outline generation."""
        return {
            "type": "object",
            "properties": {
                "title_options": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
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
            "required": ["title_options", "outline"],
            "propertyOrdering": ["title_options", "outline"]
        }
