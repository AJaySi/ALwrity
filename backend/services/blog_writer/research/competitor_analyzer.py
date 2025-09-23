"""
Competitor Analyzer - AI-powered competitor analysis for research content.

Extracts competitor insights and market intelligence from research content.
"""

from typing import Dict, Any
from loguru import logger


class CompetitorAnalyzer:
    """Analyzes competitors and market intelligence from research content."""
    
    def analyze(self, content: str) -> Dict[str, Any]:
        """Parse comprehensive competitor analysis from the research content using AI."""
        competitor_prompt = f"""
        Analyze the following research content and extract competitor insights:
        
        Research Content:
        {content[:3000]}
        
        Extract and analyze:
        1. Top competitors mentioned (companies, brands, platforms)
        2. Content gaps (what competitors are missing)
        3. Market opportunities (untapped areas)
        4. Competitive advantages (what makes content unique)
        5. Market positioning insights
        6. Industry leaders and their strategies
        
        Respond with JSON:
        {{
            "top_competitors": ["competitor1", "competitor2"],
            "content_gaps": ["gap1", "gap2"],
            "opportunities": ["opportunity1", "opportunity2"],
            "competitive_advantages": ["advantage1", "advantage2"],
            "market_positioning": "positioning insights",
            "industry_leaders": ["leader1", "leader2"],
            "analysis_notes": "Comprehensive competitor analysis summary"
        }}
        """
        
        from services.llm_providers.gemini_provider import gemini_structured_json_response
        
        competitor_schema = {
            "type": "object",
            "properties": {
                "top_competitors": {"type": "array", "items": {"type": "string"}},
                "content_gaps": {"type": "array", "items": {"type": "string"}},
                "opportunities": {"type": "array", "items": {"type": "string"}},
                "competitive_advantages": {"type": "array", "items": {"type": "string"}},
                "market_positioning": {"type": "string"},
                "industry_leaders": {"type": "array", "items": {"type": "string"}},
                "analysis_notes": {"type": "string"}
            },
            "required": ["top_competitors", "content_gaps", "opportunities", "competitive_advantages", "market_positioning", "industry_leaders", "analysis_notes"]
        }
        
        competitor_analysis = gemini_structured_json_response(
            prompt=competitor_prompt,
            schema=competitor_schema,
            temperature=0.3,
            max_tokens=4000
        )
        
        if isinstance(competitor_analysis, dict) and 'error' not in competitor_analysis:
            logger.info("✅ AI competitor analysis completed successfully")
            return competitor_analysis
        else:
            # Fail gracefully - no fallback data
            error_msg = competitor_analysis.get('error', 'Unknown error') if isinstance(competitor_analysis, dict) else str(competitor_analysis)
            logger.error(f"AI competitor analysis failed: {error_msg}")
            raise ValueError(f"Competitor analysis failed: {error_msg}")
    
