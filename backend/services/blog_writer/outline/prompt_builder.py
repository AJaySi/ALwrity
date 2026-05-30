"""
Prompt Builder - Handles building of AI prompts for outline generation.

Constructs comprehensive prompts using curated keyword payloads,
research data, and strategic requirements.
"""

from typing import Dict, Any, List
from datetime import datetime


class PromptBuilder:
    """Handles building of comprehensive AI prompts for outline generation."""
    
    def __init__(self):
        """Initialize the prompt builder."""
        pass
    
    def build_outline_prompt(self, curated_keywords: Dict[str, Any],
                           content_angles: List[str], sources: List, search_intent: str,
                           request, custom_instructions: str = None,
                           selected_content_angle: str = None,
                           selected_competitive_advantage: str = None) -> str:
        """Build the comprehensive outline generation prompt using curated keyword payload."""
        
        research = request.research
        
        primary_kw_text = ', '.join(curated_keywords.get('primary', [])) if curated_keywords.get('primary') else (request.topic or ', '.join(getattr(request.research, 'original_keywords', []) or ['the target topic']))
        secondary_kw_text = ', '.join(curated_keywords.get('secondary', [])) if curated_keywords.get('secondary') else "None provided"
        long_tail_text = ', '.join(curated_keywords.get('long_tail', [])) if curated_keywords.get('long_tail') else "None discovered"
        semantic_text = ', '.join(curated_keywords.get('semantic', [])) if curated_keywords.get('semantic') else "None discovered"
        trending_text = ', '.join(curated_keywords.get('trending', [])) if curated_keywords.get('trending') else "None discovered"
        content_gap_text = ', '.join(curated_keywords.get('content_gap', [])) if curated_keywords.get('content_gap') else "None identified"
        
        content_angle_text = ', '.join(content_angles) if content_angles else "No explicit angles provided; infer compelling angles from research insights."
        competitor_text = ', '.join(research.competitor_analysis.get('top_competitors', [])) if research and research.competitor_analysis else "Not available"
        opportunity_text = ', '.join(research.competitor_analysis.get('opportunities', [])) if research and research.competitor_analysis else "Not available"
        advantages_text = ', '.join(research.competitor_analysis.get('competitive_advantages', [])) if research and research.competitor_analysis else "Not available"
        
        # Extract additional UI-mapped context fields
        analysis_insights_text = (research.keyword_analysis.get('analysis_insights', '') or '') if research and research.keyword_analysis else ''
        market_positioning_text = (research.competitor_analysis.get('market_positioning', '') or '') if research and research.competitor_analysis else ''
        difficulty_score = research.keyword_analysis.get('difficulty', None) if research and research.keyword_analysis else None

        # Build selected angle prominence section
        if selected_content_angle and selected_content_angle.strip():
            selected_angle_section = f"""
PRIORITY CONTENT ANGLE (MUST PRIORITIZE):
- This outline MUST be built around the following selected content angle as its primary lens and narrative framework:
  "{selected_content_angle}"
- Every major section should connect back to this angle
- Title options should reflect this angle
- The overall narrative arc should follow this angle's implied storyline
"""
        else:
            selected_angle_section = ""

        # Build selected competitive advantage prominence section
        if selected_competitive_advantage and selected_competitive_advantage.strip():
            selected_advantage_section = f"""
PRIORITY COMPETITIVE ADVANTAGE (MUST LEVERAGE):
- This outline MUST prominently feature and leverage the following competitive advantage throughout the content:
  "{selected_competitive_advantage}"
- Weave this advantage into key sections as a differentiator
- Frame the solutions and recommendations around this advantage
- Use this advantage to counter competitor weaknesses mentioned in research
"""
        else:
            selected_advantage_section = ""

        # Import and use the KeywordCurator for the directive section
        from .keyword_curator import KeywordCurator
        keyword_directives = KeywordCurator().format_for_prompt(curated_keywords)

        current_date = datetime.now().strftime("%B %d, %Y")
        current_year = datetime.now().year

        return f"""Create a comprehensive blog outline for: {primary_kw_text}

CONTEXT:
Current Date: {current_date}
Search Intent: {search_intent}
{f"Keyword Difficulty: {difficulty_score}/10" if difficulty_score is not None else ""}
Target: {request.word_count or 1500} words
Industry: {getattr(request.persona, 'industry', 'General') if request.persona else 'General'}
Audience: {getattr(request.persona, 'target_audience', 'General') if request.persona else 'General'}

OVERVIEW KEYWORD SUMMARY:
- Primary: {primary_kw_text}
- Secondary: {secondary_kw_text}
- Long-tail: {long_tail_text}
- Semantic: {semantic_text}
- Trending: {trending_text}
- Content Gap: {content_gap_text}

{keyword_directives}

RESEARCH INSIGHTS SYNTHESIS:
{analysis_insights_text}

CONTENT ANGLES / STORYLINES: {content_angle_text}
{selected_angle_section}
{selected_advantage_section}
COMPETITIVE INTELLIGENCE:
Top Competitors: {competitor_text}
Market Opportunities: {opportunity_text}
Competitive Advantages: {advantages_text}
{f"Market Positioning: {market_positioning_text}" if market_positioning_text else ""}

RESEARCH SOURCES: {len(sources)} authoritative sources available

{f"CUSTOM INSTRUCTIONS: {custom_instructions}" if custom_instructions else ""}

STRATEGIC REQUIREMENTS:
- MUST prioritize and anchor the outline around the selected content angle above all others
- MUST highlight and leverage the selected competitive advantage as a key differentiator
- Follow the KEYWORD PLACEMENT DIRECTIVES — treat the locked keywords as the minimum anchor set; you MAY include closely related intent-matching variations where natural
- Create SEO-optimized headings with natural keyword integration
- Surface the strongest research-backed angles within the outline
- Build logical narrative flow from problem to solution
- Include data-driven insights from research sources
- Address content gaps and market opportunities
- Optimize for search intent and user questions
- Ensure engaging, actionable content throughout

Return JSON format:
{{
    "title_options": [
        "Title option 1",
        "Title option 2",
        "Title option 3"
    ],
    "outline": [
        {{
            "heading": "Section heading",
            "subheadings": ["Subheading 1", "Subheading 2", "Subheading 3"],
            "key_points": ["Key point 1", "Key point 2", "Key point 3"],
            "target_words": 300,
            "keywords": ["keyword 1", "keyword 2"]
        }}
    ]
}}"""
    
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
