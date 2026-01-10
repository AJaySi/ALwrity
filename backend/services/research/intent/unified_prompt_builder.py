"""
Prompt builder for unified research analyzer.

Builds the comprehensive LLM prompt that guides intent inference,
query generation, and parameter optimization in a single call.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional

from models.research_persona_models import ResearchPersona
from .unified_analyzer_utils import (
    get_current_date_context,
    build_persona_context,
    build_competitor_context,
)


def build_unified_prompt(
    user_input: str,
    keywords: List[str],
    research_persona: Optional[ResearchPersona] = None,
    competitor_data: Optional[List[Dict]] = None,
    industry: Optional[str] = None,
    target_audience: Optional[str] = None,
    user_provided_purpose: Optional[str] = None,
    user_provided_content_output: Optional[str] = None,
    user_provided_depth: Optional[str] = None,
) -> str:
    """
    Build the unified prompt for intent + queries + parameters.
    
    This prompt guides the LLM to:
    1. Infer research intent (or use user-provided purpose/content_output/depth)
    2. Generate targeted queries linked to intent fields
    3. Optimize provider settings based on queries and intent
    """
    # Get current date context
    date_context = get_current_date_context()
    now = datetime.now()
    current_year = now.year
    next_year = current_year + 1
    current_month_year = now.strftime("%B %Y")
    
    # Build persona context
    persona_context = build_persona_context(research_persona, industry, target_audience)
    
    # Build competitor context
    competitor_context = build_competitor_context(competitor_data)
    
    prompt = f'''You are an expert AI research strategist. Analyze the user's research request and provide a complete research plan including intent understanding, search queries, and optimal API settings.

## CURRENT DATE/TIME CONTEXT
{date_context}

**NOTE**: When user mentions time-sensitive terms (latest, current, recent, trends, predictions), prioritize {current_year} data.

## USER INPUT
"{user_input}"
{f"KEYWORDS: {', '.join(keywords)}" if keywords else ""}

## USER CONTEXT
{persona_context}
{competitor_context}
{f'''
## USER-PROVIDED INTENT SETTINGS
The user has explicitly selected these settings - USE THESE VALUES, do NOT infer different ones:
- purpose: {user_provided_purpose} (USE THIS EXACT VALUE)
- content_output: {user_provided_content_output} (USE THIS EXACT VALUE)
- depth: {user_provided_depth} (USE THIS EXACT VALUE)

IMPORTANT: Since the user has explicitly selected these, you should:
1. Use the provided purpose, content_output, and depth values exactly as given
2. Still infer secondary_questions, focus_areas, also_answering, and expected_deliverables based on the user input and these provided settings
3. Generate queries that align with the user's explicit selections
''' if (user_provided_purpose or user_provided_content_output or user_provided_depth) else ''}

## YOUR TASK: Provide a Complete Research Plan

### PART 1: INTENT ANALYSIS
{f"Use the user-provided settings above. For fields not provided, infer what the user really wants from their research." if (user_provided_purpose or user_provided_content_output or user_provided_depth) else "Understand what the user really wants from their research."}

**CRITICAL: Use EXACT enum values - do NOT return descriptive strings.**
- purpose: Must be one of: "learn", "create_content", "make_decision", "compare", "solve_problem", "find_data", "explore_trends", "validate", "generate_ideas"
  {f"**USER PROVIDED: {user_provided_purpose} - USE THIS EXACT VALUE**" if user_provided_purpose else "- Infer from user input"}
- content_output: Must be one of: "blog", "podcast", "video", "social_post", "newsletter", "presentation", "report", "whitepaper", "email", "general"
  {f"**USER PROVIDED: {user_provided_content_output} - USE THIS EXACT VALUE**" if user_provided_content_output else "- Infer from user input"}
- depth: Must be one of: "overview", "detailed", "expert"
  {f"**USER PROVIDED: {user_provided_depth} - USE THIS EXACT VALUE**" if user_provided_depth else "- Infer from user input"}
- expected_deliverables: Must be an array of exact values: "key_statistics", "expert_quotes", "case_studies", "comparisons", "trends", "best_practices", "step_by_step", "pros_cons", "definitions", "citations", "examples", "predictions"
  - Infer based on purpose, content_output, and user input

**CRITICAL: ALWAYS generate focus_areas and also_answering fields:**
- focus_areas: Generate 2-5 specific focus areas based on user input (e.g., "academic research", "industry trends", "company analysis", "practical applications", "safety considerations")
- also_answering: Generate 2-4 related topics or questions that should also be addressed (e.g., "benefits and drawbacks", "alternatives", "implementation steps", "cost considerations")
- These fields are REQUIRED and MUST be populated - do NOT leave them empty
- Think about what additional aspects of the topic would be valuable to cover

### PART 2: SEARCH QUERIES
Generate 4-8 targeted, diverse search queries optimized for semantic search.

**CRITICAL: Generate MULTIPLE DIVERSE queries (minimum 4, maximum 8). Do NOT generate just one query.**

**QUERY GENERATION RULES:**

1. **PRIMARY QUERY**: Generate 1 query that directly addresses the primary_question
   - This should be the highest priority (priority: 5)
   - Should comprehensively cover the main research goal
   - Set addresses_primary_question: true

2. **SECONDARY QUERY MAPPING**: For EACH secondary_question, generate a SEPARATE query that addresses it
   - Link each query to its corresponding secondary_question in addresses_secondary_questions array
   - Priority: 4 (high but secondary to primary)
   - **CRITICAL**: Create SEPARATE queries for each secondary question UNLESS they are extremely similar (same keywords, same search intent)
   - Only merge if queries would return identical results

3. **FOCUS AREA QUERIES**: Generate SEPARATE queries for EACH focus_area
   - **CRITICAL**: If focus_areas exist, generate AT LEAST one query per focus_area
   - Add each focus area to targets_focus_areas array for its corresponding query
   - Priority: 3-4 depending on importance
   - **CRITICAL**: Create SEPARATE queries for each focus_area UNLESS they are extremely similar (same search intent, same keywords)
   - Each focus area should have its own dedicated query to ensure comprehensive coverage

4. **ALSO ANSWERING QUERIES**: Generate queries for EACH also_answering topic
   - **CRITICAL**: Generate at least one query per also_answering topic that is NOT covered by primary/secondary queries
   - Lower priority (priority: 2-3)
   - Add each topic to covers_also_answering array for its corresponding query
   - Only skip if the topic is already fully covered by existing queries

5. **QUERY DIVERSITY RULES** (IMPORTANT):
   - **CRITICAL**: Ensure queries are DISTINCT and target DIFFERENT aspects
   - Vary search terms: use synonyms, related terms, different angles
   - Vary query structure: some specific, some broader
   - Vary providers: mix Exa and Tavily when appropriate
   - Target different content types: academic, news, practical guides, etc.
   - **DO NOT** create queries that are just slight variations of each other
   - **DO NOT** merge queries that target different focus areas or also_answering topics

6. **MINIMUM QUERY REQUIREMENTS**:
   - **ALWAYS generate at least 4 queries** (even for simple topics)
   - If you have: 1 primary + 1 secondary + 2 focus areas = generate at least 4 queries
   - If you have: 1 primary + 3 secondary + 2 focus areas + 2 also_answering = generate 6-8 queries
   - **If focus_areas or also_answering are empty, generate queries covering different angles/aspects of the primary question**

7. **QUERY-TO-INTENT LINKING**: For each query, specify:
   - addresses_primary_question: true/false (only one query should be true)
   - addresses_secondary_questions: array of secondary question strings (can be empty, or contain one/multiple)
   - targets_focus_areas: array of focus area strings (should match focus_areas when relevant)
   - covers_also_answering: array of also_answering topic strings (should match also_answering when relevant)
   - justification: brief explanation explaining how this query differs from others and what it will find

**OUTPUT FORMAT FOR QUERIES:**
Each query must include these linking fields. Ensure queries are DIVERSE and target different aspects, not just variations of the same search.

### PART 3: PROVIDER SETTINGS
Configure Exa and Tavily API parameters with justifications.

**Provider settings should be optimized based on:**
1. **Primary query characteristics** (most important - this is what will be executed)
2. **Secondary questions** (if they require different settings for comprehensive coverage)
3. **Focus areas** (if they need specific content types or sources)
4. **Also answering topics** (if they need different time ranges or sources)
5. **Time sensitivity** from intent (real_time, recent, historical, evergreen)
6. **Depth requirements** from intent (overview, detailed, expert)

**SETTING OPTIMIZATION RULES:**

1. **Time Sensitivity Based on Intent**:
   - If time_sensitivity = "real_time" OR any secondary_question/focus_area needs recent data:
     - Tavily: time_range = "day" or "week", topic = "news"
     - Exa: startPublishedDate = current year, type = "auto" or "fast"
   - If time_sensitivity = "historical":
     - Exa: No date filters, use historical content, type = "deep" or "neural"
     - Tavily: time_range = "year" or null, topic = "general"
   - If time_sensitivity = "recent":
     - Exa: startPublishedDate = current year or last 6 months
     - Tavily: time_range = "month" or "week"
   - If time_sensitivity = "evergreen":
     - Exa: No date filters, type = "deep" for comprehensive coverage
     - Tavily: time_range = null, topic = "general"

2. **Content Type Based on Focus Areas**:
   - If focus_areas include "academic" or "research" or "studies":
     - Exa: category = "research paper", includeDomains = ["arxiv.org", "nature.com", "pubmed.ncbi.nlm.nih.gov"]
     - Exa: type = "deep" or "neural" for comprehensive academic coverage
   - If focus_areas include "companies" or "competitors" or "business":
     - Exa: category = "company"
     - Exa: type = "auto" or "deep" for company research
   - If focus_areas include "news" or "trends" or "current events":
     - Tavily: topic = "news", search_depth = "advanced"
     - Exa: category = "news" (if using Exa for news)
   - If focus_areas include "social" or "twitter" or "social media":
     - Exa: category = "tweet"
   - If focus_areas include "github" or "code" or "technical":
     - Exa: category = "github"

3. **Depth Based on Intent Depth and Secondary Questions**:
   - If depth = "expert" OR secondary_questions require detailed analysis:
     - Exa: type = "deep", context = true, contextMaxCharacters = 15000+, numResults = 20-50
     - Tavily: search_depth = "advanced", chunks_per_source = 3, max_results = 15-20
   - If depth = "detailed":
     - Exa: type = "auto" or "deep", context = true, contextMaxCharacters = 10000+, numResults = 10-20
     - Tavily: search_depth = "advanced" or "basic", chunks_per_source = 3, max_results = 10-15
   - If depth = "overview":
     - Exa: type = "auto" or "fast", numResults = 5-10
     - Tavily: search_depth = "basic" or "fast", max_results = 5-10

4. **Query-Specific Settings (Primary Query Focus)**:
   - If primary query needs comprehensive results (addresses multiple secondary questions or focus areas):
     - Exa: type = "deep", context = true, contextMaxCharacters = 15000+
     - Tavily: search_depth = "advanced", chunks_per_source = 3
   - If primary query needs speed (simple factual answer):
     - Exa: type = "fast", numResults = 5-10
     - Tavily: search_depth = "ultra-fast", max_results = 5
   - If primary query targets specific content type:
     - Match Exa category or Tavily topic to content type
   - If primary query is time-sensitive:
     - Apply time filters based on urgency

5. **Also Answering Topics Considerations**:
   - If also_answering topics need different time ranges:
     - Use broader time_range in Tavily (e.g., "year" instead of "month")
     - Don't apply strict date filters in Exa
   - If also_answering topics need different sources:
     - Consider including additional domains in includeDomains
     - Use more comprehensive search (type = "deep" in Exa)

6. **Provider Selection Based on Intent**:
   - Use EXA when:
     * Primary query needs semantic understanding
     * Focus areas include "academic", "research", "companies"
     * Depth = "expert" or "detailed"
     * Need comprehensive context (context = true)
   - Use TAVILY when:
     * Time sensitivity = "real_time" or "recent"
     * Focus areas include "news", "trends", "current events"
     * Need quick AI-generated answers
     * Primary query is about recent developments

**NOTE**: Since we're executing only the PRIMARY query initially, optimize settings for the primary query, but ensure settings can accommodate secondary questions and focus areas in the results. The settings should be comprehensive enough to capture information relevant to all intent aspects.

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

## PROVIDER OPTIONS

**EXA**: type (auto/fast/deep/neural/keyword), category (company/research paper/news/etc), numResults (1-100), includeDomains, startPublishedDate, highlights, context (required for deep). Best for: academic, companies, deep analysis.

**TAVILY**: topic (general/news/finance), search_depth (advanced/basic/fast/ultra-fast), time_range, max_results (0-20), chunks_per_source (1-3). Best for: news, real-time, quick facts.

---

## OUTPUT FORMAT

Return JSON with: intent (all fields), queries (with linking fields), enhanced_keywords, research_angles, recommended_provider, provider_justification, exa_config (enabled, type, category, numResults, includeDomains, excludeDomains, startPublishedDate, highlights, context, contextMaxCharacters, and justifications), tavily_config (enabled, topic, search_depth, include_answer, time_range, max_results, chunks_per_source, and justifications), trends_config (if trends enabled).

**Key Requirements:**
- Provide brief justifications (1 sentence) for all config parameters
- Reference intent fields (depth, time_sensitivity, focus_areas) in justifications
- Include current year ({current_year}) in time-sensitive queries
- Use EXA for academic/companies/deep analysis, TAVILY for news/real-time
'''

    return prompt
