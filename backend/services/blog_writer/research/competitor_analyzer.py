"""
Competitor Analyzer - AI-powered competitor analysis for research content.

Extracts competitor insights and market intelligence from research content.
"""

from typing import Dict, Any
from loguru import logger
import json


class CompetitorAnalyzer:
    """Analyzes competitors and market intelligence from research content."""
    
    def analyze(self, content: str, user_id: str = None) -> Dict[str, Any]:
        """Parse comprehensive competitor analysis from the research content using AI."""
        competitor_prompt = f"""
        Analyze the following research content and extract competitor insights:
        
        Research Content:
        {content[:8000]}
        
        Extract and analyze:
        1. Top competitors mentioned (companies, brands, platforms)
        2. Content gaps (what competitors are missing)
        3. Opportunities (untapped areas)
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
        
        from services.llm_providers.main_text_generation import llm_text_gen
        
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
        
        raw = llm_text_gen(
            prompt=competitor_prompt,
            user_id=user_id
        )
        
        # Parse JSON from LLM response (works with both string and dict return types)
        import re
        if isinstance(raw, str):
            cleaned = raw.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.startswith('```'):
                cleaned = cleaned[3:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            try:
                competitor_analysis = json.loads(cleaned)
            except json.JSONDecodeError:
                json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
                if json_match:
                    competitor_analysis = json.loads(json_match.group(0))
                else:
                    raise ValueError(f"Competitor analysis returned non-JSON string: {cleaned[:200]}")
        elif isinstance(raw, dict):
            competitor_analysis = raw
        else:
            raise ValueError(f"Unexpected LLM response type: {type(raw)}")
        
        if 'error' in competitor_analysis:
            raise ValueError(f"Competitor analysis failed: {competitor_analysis.get('error', 'Unknown error')}")
        
        logger.info("✅ AI competitor analysis completed successfully")
        return competitor_analysis
    
