"""
Unified Research Analyzer

Combines intent inference, query generation, and parameter optimization
into a single AI call with justifications for each decision.

This reduces 2 LLM calls to 1, improves coherence, and provides
user-friendly justifications for all settings.

Author: ALwrity Team
Version: 2.0 (Refactored)
"""

from typing import Dict, Any, List, Optional
from loguru import logger

from models.research_persona_models import ResearchPersona
from .unified_prompt_builder import build_unified_prompt
from .unified_schema_builder import build_unified_schema
from .unified_result_parser import parse_unified_result
from .unified_analyzer_utils import create_fallback_response


class UnifiedResearchAnalyzer:
    """
    Unified AI-driven analyzer that performs:
    1. Intent inference (what user wants)
    2. Query generation (how to search)
    3. Parameter optimization (Exa/Tavily settings)
    
    All in a single LLM call with justifications.
    
    Refactored to use modular components for better maintainability:
    - unified_prompt_builder: Builds the comprehensive LLM prompt
    - unified_schema_builder: Defines the JSON schema for structured output
    - unified_result_parser: Parses LLM response into structured models
    - unified_analyzer_utils: Utility functions for context and fallback
    - query_deduplicator: Removes redundant queries (used by parser)
    """
    
    def __init__(self):
        """Initialize the unified analyzer."""
        logger.info("UnifiedResearchAnalyzer initialized")
    
    async def analyze(
        self,
        user_input: str,
        keywords: Optional[List[str]] = None,
        research_persona: Optional[ResearchPersona] = None,
        competitor_data: Optional[List[Dict]] = None,
        industry: Optional[str] = None,
        target_audience: Optional[str] = None,
        user_id: Optional[str] = None,
        user_provided_purpose: Optional[str] = None,
        user_provided_content_output: Optional[str] = None,
        user_provided_depth: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Perform unified analysis of user research request.
        
        Args:
            user_input: The user's research input (keywords, question, etc.)
            keywords: Optional list of keywords
            research_persona: Optional research persona for personalization
            competitor_data: Optional competitor analysis data
            industry: Optional industry context
            target_audience: Optional target audience context
            user_id: User ID for subscription checks (required)
        
        Returns:
            Dict containing:
            - success: bool
            - intent: ResearchIntent
            - queries: List[ResearchQuery]
            - exa_config: Dict with settings and justifications
            - tavily_config: Dict with settings and justifications
            - recommended_provider: str
            - provider_justification: str
            - trends_config: Dict with Google Trends settings (optional)
            - enhanced_keywords: List[str]
            - research_angles: List[str]
            - analysis_summary: str
        """
        try:
            logger.info(f"Unified analysis for: {user_input[:100]}...")
            
            keywords = keywords or []
            
            # Build the unified prompt using the prompt builder module
            prompt = build_unified_prompt(
                user_input=user_input,
                keywords=keywords,
                research_persona=research_persona,
                competitor_data=competitor_data,
                industry=industry,
                target_audience=target_audience,
                user_provided_purpose=user_provided_purpose,
                user_provided_content_output=user_provided_content_output,
                user_provided_depth=user_provided_depth,
            )
            
            # Define the comprehensive JSON schema using the schema builder module
            unified_schema = build_unified_schema()
            
            # Call LLM (single call for everything)
            from services.llm_providers.main_text_generation import llm_text_gen
            
            result = llm_text_gen(
                prompt=prompt,
                json_struct=unified_schema,
                user_id=user_id
            )
            
            if isinstance(result, dict) and "error" in result:
                logger.error(f"Unified analysis failed: {result.get('error')}")
                return create_fallback_response(user_input, keywords)
            
            # Parse the unified result using the result parser module
            return parse_unified_result(result, user_input)
            
        except Exception as e:
            logger.error(f"Error in unified analysis: {e}")
            return create_fallback_response(user_input, keywords or [])
