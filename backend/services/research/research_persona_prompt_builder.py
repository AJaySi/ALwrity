"""
Research Persona Prompt Builder

Handles building comprehensive prompts for research persona generation.
Generates personalized research defaults, suggestions, and configurations.
"""

from typing import Dict, Any
import json
from loguru import logger


class ResearchPersonaPromptBuilder:
    """Builds comprehensive prompts for research persona generation."""
    
    def build_research_persona_prompt(self, onboarding_data: Dict[str, Any]) -> str:
        """Build the research persona generation prompt with comprehensive data."""
        
        # Extract data from onboarding_data
        website_analysis = onboarding_data.get("website_analysis", {}) or {}
        persona_data = onboarding_data.get("persona_data", {}) or {}
        research_prefs = onboarding_data.get("research_preferences", {}) or {}
        business_info = onboarding_data.get("business_info", {}) or {}
        
        # Extract core persona
        core_persona = persona_data.get("core_persona", {}) or {}
        
        prompt = f"""
COMPREHENSIVE RESEARCH PERSONA GENERATION TASK: Create a highly detailed, personalized research persona based on the user's business, writing style, and content strategy. This persona will provide intelligent defaults and suggestions for research inputs.

=== USER CONTEXT ===

BUSINESS INFORMATION:
{json.dumps(business_info, indent=2)}

WEBSITE ANALYSIS:
{json.dumps(website_analysis, indent=2)}

CORE PERSONA:
{json.dumps(core_persona, indent=2)}

RESEARCH PREFERENCES:
{json.dumps(research_prefs, indent=2)}

=== RESEARCH PERSONA GENERATION REQUIREMENTS ===

Generate a comprehensive research persona in JSON format with the following structure:

1. DEFAULT VALUES:
   - "default_industry": Extract from core_persona.industry, business_info.industry, or website_analysis target_audience. Use "General" only if none available.
   - "default_target_audience": Extract from core_persona.target_audience, website_analysis.target_audience, or business_info.target_audience. Be specific and descriptive.
   - "default_research_mode": Suggest "basic", "comprehensive", or "targeted" based on research_preferences.research_depth and content_type preferences.
   - "default_provider": Suggest "google" for news/trends, "exa" for academic/technical deep-dives, or "google" as default.

2. KEYWORD INTELLIGENCE:
   - "suggested_keywords": Generate 8-12 keywords relevant to the user's industry, interests (from core_persona), and content goals.
   - "keyword_expansion_patterns": Create a dictionary mapping common keywords to expanded, industry-specific terms. Include 10-15 patterns like:
     {{"AI": ["healthcare AI", "medical AI", "clinical AI", "diagnostic AI"], "tools": ["medical devices", "clinical tools"], ...}}
     Focus on industry-specific terminology from the user's domain.

3. DOMAIN EXPERTISE:
   - "suggested_exa_domains": List 4-6 authoritative domains for the user's industry (e.g., Healthcare: ["pubmed.gov", "nejm.org", "thelancet.com"]).
   - "suggested_exa_category": Suggest appropriate Exa category based on industry:
     - Healthcare/Science: "research paper"
     - Finance: "financial report"
     - Technology/Business: "company" or "news"
     - Default: null (empty string for all categories)

4. RESEARCH ANGLES:
   - "research_angles": Generate 5-8 alternative research angles/focuses based on:
     - User's pain points and challenges (from core_persona)
     - Industry trends and opportunities
     - Content goals (from research_preferences)
     - Audience interests (from core_persona.interests)
   Examples: "Compare {{topic}} tools", "{{topic}} ROI analysis", "Latest {{topic}} trends", etc.

5. QUERY ENHANCEMENT:
   - "query_enhancement_rules": Create templates for improving vague user queries:
     {{"vague_ai": "Research: AI applications in {{industry}} for {{audience}}", "vague_tools": "Compare top {{industry}} tools", ...}}
     Include 5-8 enhancement patterns.

6. RECOMMENDED PRESETS:
   - "recommended_presets": Generate 3-5 personalized research preset templates. Each preset should include:
     - name: Descriptive name (e.g., "{{Industry}} Trends", "{{Audience}} Insights")
     - keywords: Research query string
     - industry: User's industry
     - target_audience: User's target audience
     - research_mode: "basic", "comprehensive", or "targeted"
     - config: Complete ResearchConfig object with appropriate settings
     - description: Brief explanation of what this preset researches
     Make presets relevant to the user's specific industry, audience, and content goals.

7. RESEARCH PREFERENCES:
   - "research_preferences": Extract and structure research preferences from onboarding:
     - research_depth: From research_preferences.research_depth
     - content_types: From research_preferences.content_types
     - auto_research: From research_preferences.auto_research
     - factual_content: From research_preferences.factual_content

=== OUTPUT REQUIREMENTS ===

Return a valid JSON object matching this exact structure:
{{
  "default_industry": "string",
  "default_target_audience": "string",
  "default_research_mode": "basic" | "comprehensive" | "targeted",
  "default_provider": "google" | "exa",
  "suggested_keywords": ["keyword1", "keyword2", ...],
  "keyword_expansion_patterns": {{
    "keyword": ["expansion1", "expansion2", ...]
  }},
  "suggested_exa_domains": ["domain1.com", "domain2.com", ...],
  "suggested_exa_category": "string or null",
  "research_angles": ["angle1", "angle2", ...],
  "query_enhancement_rules": {{
    "pattern": "template"
  }},
  "recommended_presets": [
    {{
      "name": "string",
      "keywords": "string",
      "industry": "string",
      "target_audience": "string",
      "research_mode": "basic" | "comprehensive" | "targeted",
      "config": {{
        "mode": "basic" | "comprehensive" | "targeted",
        "provider": "google" | "exa",
        "max_sources": 10 | 15 | 12,
        "include_statistics": true | false,
        "include_expert_quotes": true | false,
        "include_competitors": true | false,
        "include_trends": true | false,
        "exa_category": "string or null",
        "exa_include_domains": ["domain1.com", ...],
        "exa_search_type": "auto" | "keyword" | "neural"
      }},
      "description": "string"
    }}
  ],
  "research_preferences": {{
    "research_depth": "string",
    "content_types": ["type1", "type2", ...],
    "auto_research": true | false,
    "factual_content": true | false
  }},
  "version": "1.0",
  "confidence_score": 85.0
}}

=== IMPORTANT INSTRUCTIONS ===

1. Be highly specific and personalized - use actual data from the user's business, persona, and preferences.
2. Avoid generic suggestions - every field should reflect the user's unique context.
3. For industries not clearly identified, infer from website_analysis.content_characteristics or writing_style.
4. Ensure all suggested keywords, domains, and angles are relevant to the user's industry and audience.
5. Generate realistic, actionable presets that the user would actually want to use.
6. Confidence score should reflect data richness (0-100): higher if rich onboarding data, lower if minimal data.
7. Return ONLY valid JSON - no markdown formatting, no explanatory text.

Generate the research persona now:
"""
        
        return prompt
    
    def get_json_schema(self) -> Dict[str, Any]:
        """Return JSON schema for structured LLM response."""
        # This will be used with llm_text_gen(json_struct=...)
        from models.research_persona_models import ResearchPersona, ResearchPreset
        
        # Convert Pydantic model to JSON schema
        return ResearchPersona.schema()
