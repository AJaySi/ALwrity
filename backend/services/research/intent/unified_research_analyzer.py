"""
Unified Research Analyzer

Combines intent inference, query generation, and parameter optimization
into a single AI call with justifications for each decision.

This reduces 2 LLM calls to 1, improves coherence, and provides
user-friendly justifications for all settings.

Author: ALwrity Team
Version: 1.0
"""

import json
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger

from models.research_intent_models import (
    ResearchIntent,
    ResearchQuery,
    IntentInferenceResponse,
    ResearchPurpose,
    ContentOutput,
    ExpectedDeliverable,
    ResearchDepthLevel,
    InputType,
)
from models.research_persona_models import ResearchPersona


class UnifiedResearchAnalyzer:
    """
    Unified AI-driven analyzer that performs:
    1. Intent inference (what user wants)
    2. Query generation (how to search)
    3. Parameter optimization (Exa/Tavily settings)
    
    All in a single LLM call with justifications.
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
    ) -> Dict[str, Any]:
        """
        Perform unified analysis of user research request.
        
        Returns:
            Dict containing:
            - intent: ResearchIntent
            - queries: List[ResearchQuery]
            - exa_config: Dict with settings and justifications
            - tavily_config: Dict with settings and justifications
            - recommended_provider: str
            - provider_justification: str
        """
        try:
            logger.info(f"Unified analysis for: {user_input[:100]}...")
            
            keywords = keywords or []
            
            # Build the unified prompt
            prompt = self._build_unified_prompt(
                user_input=user_input,
                keywords=keywords,
                research_persona=research_persona,
                competitor_data=competitor_data,
                industry=industry,
                target_audience=target_audience,
            )
            
            # Define the comprehensive JSON schema
            unified_schema = self._build_unified_schema()
            
            # Call LLM (single call for everything)
            from services.llm_providers.main_text_generation import llm_text_gen
            
            result = llm_text_gen(
                prompt=prompt,
                json_struct=unified_schema,
                user_id=user_id
            )
            
            if isinstance(result, dict) and "error" in result:
                logger.error(f"Unified analysis failed: {result.get('error')}")
                return self._create_fallback_response(user_input, keywords)
            
            # Parse the unified result
            return self._parse_unified_result(result, user_input)
            
        except Exception as e:
            logger.error(f"Error in unified analysis: {e}")
            return self._create_fallback_response(user_input, keywords or [])
    
    def _build_unified_prompt(
        self,
        user_input: str,
        keywords: List[str],
        research_persona: Optional[ResearchPersona] = None,
        competitor_data: Optional[List[Dict]] = None,
        industry: Optional[str] = None,
        target_audience: Optional[str] = None,
    ) -> str:
        """Build the unified prompt for intent + queries + parameters."""
        
        # Build persona context
        persona_context = self._build_persona_context(research_persona, industry, target_audience)
        
        # Build competitor context
        competitor_context = self._build_competitor_context(competitor_data)
        
        prompt = f'''You are an expert AI research strategist. Analyze the user's research request and provide a complete research plan including intent understanding, search queries, and optimal API settings.

## USER INPUT
"{user_input}"
{f"KEYWORDS: {', '.join(keywords)}" if keywords else ""}

## USER CONTEXT
{persona_context}
{competitor_context}

## YOUR TASK: Provide a Complete Research Plan

### PART 1: INTENT ANALYSIS
Understand what the user really wants from their research.

### PART 2: SEARCH QUERIES
Generate 4-8 targeted search queries optimized for semantic search.

### PART 3: PROVIDER SETTINGS
Configure Exa and Tavily API parameters with justifications.

### PART 4: GOOGLE TRENDS KEYWORDS (if trends in deliverables)
If "trends" is in expected_deliverables OR purpose is "explore_trends":
- Suggest 1-3 optimized keywords for Google Trends analysis
- These may differ from research queries (trends need broader, searchable terms)
- Consider: What keywords will show meaningful trends over time?
- Consider: What timeframe will show relevant trends? (1 year, 12 months, etc.)
- Consider: What geographic region is most relevant for the user?
- Explain what insights trends will uncover for content generation:
  * Search interest trends over time (optimal publication timing)
  * Regional interest distribution (audience targeting)
  * Related topics for content expansion
  * Related queries for FAQ sections
  * Rising topics for timely content opportunities

---

## AVAILABLE PROVIDER OPTIONS

### EXA API OPTIONS (Semantic Search Engine)
| Parameter | Options | Description |
|-----------|---------|-------------|
| type | "auto", "neural", "fast", "deep" | "neural" = semantic understanding, "deep" = comprehensive with query expansion |
| category | "company", "research paper", "news", "github", "tweet", "personal site", "pdf", "financial report", "people" | Focus on specific content types |
| numResults | 5-25 | Number of results (10 recommended) |
| includeDomains | string[] | Domains to include (e.g., ["arxiv.org", "nature.com"]) |
| excludeDomains | string[] | Domains to exclude |
| startPublishedDate | ISO date | Filter by publish date (e.g., "2024-01-01T00:00:00.000Z") |
| text | boolean | Include full text content |
| highlights | boolean | Extract key highlights |
| context | boolean | Return as single context string for RAG |

**WHEN TO USE EXA:**
- Semantic understanding needed (finding similar content)
- Academic/research papers
- Company/competitor research
- Deep, comprehensive results
- Historical content

### TAVILY API OPTIONS (AI-Powered Search)
| Parameter | Options | Description |
|-----------|---------|-------------|
| topic | "general", "news", "finance" | Search topic category |
| search_depth | "basic", "advanced" | "advanced" = multiple semantic snippets per URL |
| include_answer | false, true, "basic", "advanced" | AI-generated answer from results |
| include_raw_content | false, true, "markdown", "text" | Raw page content format |
| time_range | "day", "week", "month", "year" | Filter by recency |
| max_results | 5-20 | Number of results |
| include_domains | string[] | Domains to include |
| exclude_domains | string[] | Domains to exclude |

**WHEN TO USE TAVILY:**
- Real-time/current events
- News and trending topics
- Quick facts with AI answers
- Financial data
- Recent time-sensitive content

---

## OUTPUT FORMAT

Return a JSON object with this exact structure:

```json
{{
    "intent": {{
        "input_type": "keywords|question|goal|mixed",
        "primary_question": "The main question to answer",
        "secondary_questions": ["question 1", "question 2"],
        "purpose": "learn|create_content|make_decision|compare|solve_problem|find_data|explore_trends|validate|generate_ideas",
        "content_output": "blog|podcast|video|social_post|newsletter|presentation|report|whitepaper|email|general",
        "expected_deliverables": ["key_statistics", "expert_quotes", "case_studies", "trends", "best_practices"],
        "depth": "overview|detailed|expert",
        "focus_areas": ["area1", "area2"],
        "perspective": "target perspective or null",
        "time_sensitivity": "real_time|recent|historical|evergreen",
        "confidence": 0.85,
        "confidence_reason": "Why this confidence level",
        "great_example": "Example of better input if confidence < 0.8",
        "needs_clarification": false,
        "clarifying_questions": [],
        "analysis_summary": "Brief summary of research plan"
    }},
    "queries": [
        {{
            "query": "Optimized search query string",
            "purpose": "key_statistics|expert_quotes|case_studies|trends|etc",
            "provider": "exa|tavily",
            "priority": 5,
            "expected_results": "What we expect to find",
            "justification": "Why this query and provider"
        }}
    ],
    "enhanced_keywords": ["expanded", "related", "keywords"],
    "research_angles": ["Angle 1: ...", "Angle 2: ..."],
    "recommended_provider": "exa|tavily",
    "provider_justification": "Why this provider is best for this research",
    "exa_config": {{
        "enabled": true,
        "type": "auto|neural|fast|deep",
        "type_justification": "Why this search type",
        "category": "news|research paper|company|etc or null",
        "category_justification": "Why this category or null",
        "numResults": 10,
        "numResults_justification": "Why this number",
        "includeDomains": [],
        "includeDomains_justification": "Why these domains or empty",
        "startPublishedDate": "2024-01-01T00:00:00.000Z or null",
        "date_justification": "Why this date filter or null",
        "highlights": true,
        "highlights_justification": "Why enable/disable highlights",
        "context": true,
        "context_justification": "Why enable/disable context string"
    }},
    "tavily_config": {{
        "enabled": true,
        "topic": "general|news|finance",
        "topic_justification": "Why this topic",
        "search_depth": "basic|advanced",
        "search_depth_justification": "Why this depth",
        "include_answer": "true|false|basic|advanced",
        "include_answer_justification": "Why this answer mode",
        "time_range": "day|week|month|year|null",
        "time_range_justification": "Why this time range or null",
        "max_results": 10,
        "max_results_justification": "Why this number",
        "include_raw_content": "false|true|markdown|text",
        "include_raw_content_justification": "Why this content mode"
    }},
    "trends_config": {{
        "enabled": true|false,
        "keywords": ["keyword1", "keyword2"],
        "keywords_justification": "Why these keywords for trends analysis",
        "timeframe": "today 1-y|today 12-m|all",
        "timeframe_justification": "Why this timeframe",
        "geo": "US|GB|IN|etc",
        "geo_justification": "Why this geographic region",
        "expected_insights": [
            "Search interest trends over the past year",
            "Regional interest distribution",
            "Related topics for content expansion",
            "Related queries for FAQ sections",
            "Optimal publication timing based on interest peaks"
        ]
    }}
}}
```

## DECISION RULES

1. **Provider Selection:**
   - Use EXA for: academic research, competitor analysis, deep understanding, finding similar content
   - Use TAVILY for: news, current events, quick facts, financial data, real-time info

2. **Query Optimization:**
   - Include relevant keywords for semantic matching
   - Add context words based on deliverables (e.g., "statistics 2024" for key_statistics)
   - Match query style to provider (natural language for Exa, keyword-rich for Tavily)

3. **Parameter Selection:**
   - ALWAYS provide justification for each parameter choice
   - Consider time sensitivity when setting date filters
   - Match category/topic to content type
   - Use "advanced" depth when quality matters more than speed

4. **Google Trends Keywords (if trends enabled):**
   - Suggest 1-3 keywords optimized for trends analysis
   - Keywords should be broader than research queries (e.g., "AI marketing" vs "AI marketing tools for small businesses")
   - Consider what will show meaningful search interest trends
   - Choose timeframe based on content type (12 months for blogs, 1 year for comprehensive)
   - Select geo based on user's target audience or industry
   - List specific insights trends will uncover

5. **Justifications:**
   - Keep justifications concise (1 sentence)
   - Explain the "why" not the "what"
   - Reference user's intent when relevant
'''

        return prompt
    
    def _build_unified_schema(self) -> Dict[str, Any]:
        """Build the JSON schema for unified response."""
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
                            "justification": {"type": "string"}
                        },
                        "required": ["query", "purpose", "provider", "priority"]
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
                        "context_justification": {"type": "string"}
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
                        "include_answer": {"type": "string"},
                        "include_answer_justification": {"type": "string"},
                        "time_range": {"type": "string"},
                        "time_range_justification": {"type": "string"},
                        "max_results": {"type": "integer"},
                        "max_results_justification": {"type": "string"},
                        "include_raw_content": {"type": "string"},
                        "include_raw_content_justification": {"type": "string"}
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
    
    def _build_persona_context(
        self,
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
    
    def _build_competitor_context(self, competitor_data: Optional[List[Dict]]) -> str:
        """Build competitor context section."""
        if not competitor_data:
            return ""
        
        competitor_names = [c.get("name", c.get("url", "")) for c in competitor_data[:5]]
        if competitor_names:
            return f"\nKnown Competitors: {', '.join(competitor_names)}"
        return ""
    
    def _parse_unified_result(self, result: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """Parse the unified LLM result into structured response."""
        
        intent_data = result.get("intent", {})
        
        # Build ResearchIntent
        intent = ResearchIntent(
            primary_question=intent_data.get("primary_question", user_input),
            secondary_questions=intent_data.get("secondary_questions", []),
            purpose=intent_data.get("purpose", "learn"),
            content_output=intent_data.get("content_output", "general"),
            expected_deliverables=intent_data.get("expected_deliverables", ["key_statistics"]),
            depth=intent_data.get("depth", "detailed"),
            focus_areas=intent_data.get("focus_areas", []),
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
        
        # Build queries
        queries = []
        for q in result.get("queries", []):
            try:
                queries.append(ResearchQuery(
                    query=q.get("query", ""),
                    purpose=q.get("purpose", "key_statistics"),
                    provider=q.get("provider", "exa"),
                    priority=int(q.get("priority", 3)),
                    expected_results=q.get("expected_results", ""),
                ))
            except Exception as e:
                logger.warning(f"Failed to parse query: {e}")
        
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
            "trends_config": result.get("trends_config", {}),  # NEW: Google Trends configuration
            "analysis_summary": intent_data.get("analysis_summary", ""),
        }
    
    def _create_fallback_response(self, user_input: str, keywords: List[str]) -> Dict[str, Any]:
        """Create fallback response when analysis fails."""
        return {
            "success": False,
            "intent": ResearchIntent(
                primary_question=f"What are the key insights about: {user_input}?",
                purpose="learn",
                content_output="general",
                expected_deliverables=["key_statistics", "best_practices"],
                depth="detailed",
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
