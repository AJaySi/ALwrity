"""
Keyword Analyzer - AI-powered keyword analysis for research content.

Extracts and analyzes keywords from research content using structured AI responses.
"""

from typing import Dict, Any, List
from loguru import logger
import json


class KeywordAnalyzer:
    """Analyzes keywords from research content using AI-powered extraction."""
    
    def analyze(self, content: str, original_keywords: List[str], user_id: str = None) -> Dict[str, Any]:
        """Parse comprehensive keyword analysis from the research content using AI."""
        # Use AI to extract and analyze keywords from the rich research content
        keyword_prompt = f"""
        Analyze the following research content and extract comprehensive keyword insights for: {', '.join(original_keywords)}
        
        Research Content:
        {content[:3000]}  # Limit to avoid token limits
        
        Extract and analyze:
        1. Primary keywords (main topic terms)
        2. Secondary keywords (related terms, synonyms)
        3. Long-tail opportunities (specific phrases people search for)
        4. Search intent (informational, commercial, navigational, transactional)
        5. Keyword difficulty assessment (1-10 scale)
        6. Content gaps (what competitors are missing)
        7. Semantic keywords (related concepts)
        8. Trending terms (emerging keywords)
        
        Respond with JSON:
        {{
            "primary": ["keyword1", "keyword2"],
            "secondary": ["related1", "related2"],
            "long_tail": ["specific phrase 1", "specific phrase 2"],
            "search_intent": "informational|commercial|navigational|transactional",
            "difficulty": 7,
            "content_gaps": ["gap1", "gap2"],
            "semantic_keywords": ["concept1", "concept2"],
            "trending_terms": ["trend1", "trend2"],
            "analysis_insights": "Brief analysis of keyword landscape"
        }}
        """
        
        from services.llm_providers.main_text_generation import llm_text_gen
        
        keyword_schema = {
            "type": "object",
            "properties": {
                "primary": {"type": "array", "items": {"type": "string"}},
                "secondary": {"type": "array", "items": {"type": "string"}},
                "long_tail": {"type": "array", "items": {"type": "string"}},
                "search_intent": {"type": "string"},
                "difficulty": {"type": "integer"},
                "content_gaps": {"type": "array", "items": {"type": "string"}},
                "semantic_keywords": {"type": "array", "items": {"type": "string"}},
                "trending_terms": {"type": "array", "items": {"type": "string"}},
                "analysis_insights": {"type": "string"}
            },
            "required": ["primary", "secondary", "long_tail", "search_intent", "difficulty", "content_gaps", "semantic_keywords", "trending_terms", "analysis_insights"]
        }
        
        raw = llm_text_gen(
            prompt=keyword_prompt,
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
                keyword_analysis = json.loads(cleaned)
            except json.JSONDecodeError:
                json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
                if json_match:
                    keyword_analysis = json.loads(json_match.group(0))
                else:
                    raise ValueError(f"Keyword analysis returned non-JSON string: {cleaned[:200]}")
        elif isinstance(raw, dict):
            keyword_analysis = raw
        else:
            raise ValueError(f"Unexpected LLM response type: {type(raw)}")
        
        if 'error' in keyword_analysis:
            raise ValueError(f"Keyword analysis failed: {keyword_analysis.get('error', 'Unknown error')}")
        
        logger.info("✅ AI keyword analysis completed successfully")
        return keyword_analysis
    
