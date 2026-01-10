"""
Intent Prompt Builder

Builds comprehensive AI prompts for:
1. Intent inference from user input
2. Targeted query generation
3. Intent-aware result analysis

Author: ALwrity Team
Version: 1.0
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from loguru import logger

from models.research_intent_models import (
    ResearchIntent,
    ResearchPurpose,
    ContentOutput,
    ExpectedDeliverable,
    ResearchDepthLevel,
)
from models.research_persona_models import ResearchPersona


class IntentPromptBuilder:
    """Builds prompts for intent-driven research."""
    
    def _get_current_date_context(self) -> str:
        """Get current date/time context for prompts."""
        now = datetime.now()
        current_year = now.year
        current_month = now.strftime("%B")  # Full month name
        current_date = now.strftime("%Y-%m-%d")
        return f"CURRENT DATE: {current_date} ({current_month} {current_year})\nCURRENT YEAR: {current_year}"
    
    # Purpose explanations for the AI
    PURPOSE_EXPLANATIONS = {
        ResearchPurpose.LEARN: "User wants to understand a topic for personal knowledge",
        ResearchPurpose.CREATE_CONTENT: "User will create content (blog, video, podcast) from this research",
        ResearchPurpose.MAKE_DECISION: "User needs to make a choice/decision based on research",
        ResearchPurpose.COMPARE: "User wants to compare alternatives or competitors",
        ResearchPurpose.SOLVE_PROBLEM: "User is looking for a solution to a specific problem",
        ResearchPurpose.FIND_DATA: "User needs specific statistics, facts, or citations",
        ResearchPurpose.EXPLORE_TRENDS: "User wants to understand current/future trends",
        ResearchPurpose.VALIDATE: "User wants to verify or fact-check information",
        ResearchPurpose.GENERATE_IDEAS: "User wants to brainstorm content ideas",
    }
    
    # Deliverable descriptions
    DELIVERABLE_DESCRIPTIONS = {
        ExpectedDeliverable.KEY_STATISTICS: "Numbers, percentages, data points with citations",
        ExpectedDeliverable.EXPERT_QUOTES: "Authoritative quotes from industry experts",
        ExpectedDeliverable.CASE_STUDIES: "Real examples and success stories",
        ExpectedDeliverable.COMPARISONS: "Side-by-side analysis tables",
        ExpectedDeliverable.TRENDS: "Current and emerging industry trends",
        ExpectedDeliverable.BEST_PRACTICES: "Recommended approaches and guidelines",
        ExpectedDeliverable.STEP_BY_STEP: "Process guides and how-to instructions",
        ExpectedDeliverable.PROS_CONS: "Advantages and disadvantages analysis",
        ExpectedDeliverable.DEFINITIONS: "Clear explanations of concepts and terms",
        ExpectedDeliverable.CITATIONS: "Authoritative sources for reference",
        ExpectedDeliverable.EXAMPLES: "Concrete examples to illustrate points",
        ExpectedDeliverable.PREDICTIONS: "Future outlook and predictions",
    }
    
    def build_intent_inference_prompt(
        self,
        user_input: str,
        keywords: List[str],
        research_persona: Optional[ResearchPersona] = None,
        competitor_data: Optional[List[Dict]] = None,
        industry: Optional[str] = None,
        target_audience: Optional[str] = None,
    ) -> str:
        """
        Build prompt for inferring user's research intent.
        
        This prompt analyzes the user's input and determines:
        - What they want to accomplish
        - What questions they need answered
        - What specific deliverables they need
        """
        
        # Get current date context
        date_context = self._get_current_date_context()
        now = datetime.now()
        current_year = now.year
        
        # Build persona context
        persona_context = self._build_persona_context(research_persona, industry, target_audience)
        
        # Build competitor context
        competitor_context = self._build_competitor_context(competitor_data)
        
        prompt = f"""You are an expert research intent analyzer. Your job is to understand what a content creator REALLY needs from their research.

## CURRENT DATE/TIME CONTEXT
{date_context}

**NOTE**: When user mentions time-sensitive terms (latest, current, recent, trends, predictions), prioritize {current_year} data.

## USER INPUT
"{user_input}"

{f"KEYWORDS: {', '.join(keywords)}" if keywords else ""}

## USER CONTEXT
{persona_context}

{competitor_context}

## YOUR TASK

Analyze the user's input and infer their research intent. Determine:

1. **INPUT TYPE**: Is this:
   - "keywords": Simple topic keywords (e.g., "AI healthcare {current_year}")
   - "question": A specific question (e.g., "What are the best AI tools for healthcare?")
   - "goal": A goal statement (e.g., "I need to write a blog about AI in healthcare")
   - "mixed": Combination of above

2. **PRIMARY QUESTION**: What is the main question to answer? Convert their input into a clear question.

3. **SECONDARY QUESTIONS**: What related questions should also be answered? (3-5 questions)

4. **PURPOSE**: Why are they researching? Choose ONE:
   - "learn": Understand a topic for personal knowledge
   - "create_content": Create content (blog, video, podcast)
   - "make_decision": Make a choice between options
   - "compare": Compare alternatives/competitors
   - "solve_problem": Find a solution
   - "find_data": Get specific statistics/facts
   - "explore_trends": Understand industry trends
   - "validate": Verify claims/information
   - "generate_ideas": Brainstorm ideas

5. **CONTENT OUTPUT**: What will they create? Choose ONE:
   - "blog", "podcast", "video", "social_post", "newsletter", "presentation", "report", "whitepaper", "email", "general"

6. **EXPECTED DELIVERABLES**: What specific outputs do they need? Choose ALL that apply:
   - "key_statistics": Numbers, data points
   - "expert_quotes": Authoritative quotes
   - "case_studies": Real examples
   - "comparisons": Side-by-side analysis
   - "trends": Industry trends
   - "best_practices": Recommendations
   - "step_by_step": How-to guides
   - "pros_cons": Advantages/disadvantages
   - "definitions": Concept explanations
   - "citations": Source references
   - "examples": Concrete examples
   - "predictions": Future outlook

7. **DEPTH**: How deep should the research go?
   - "overview": Quick summary
   - "detailed": In-depth analysis
   - "expert": Comprehensive expert-level

8. **FOCUS AREAS**: What specific aspects should be researched? (2-4 areas)

9. **PERSPECTIVE**: From whose viewpoint? (e.g., "marketing manager", "small business owner")

10. **TIME SENSITIVITY**: Is recency important?
    - "real_time": Latest only (past 24-48 hours)
    - "recent": Past week/month
    - "historical": Include older content
    - "evergreen": Timeless content

11. **CONFIDENCE**: How confident are you in this inference? (0.0-1.0)
    - If < 0.7, set needs_clarification to true and provide clarifying_questions
    - Provide a brief reason for your confidence level
    - If confidence is low, provide an example of what a great input would look like

## OUTPUT FORMAT

Return a JSON object:
```json
{{
    "input_type": "keywords|question|goal|mixed",
    "primary_question": "The main question to answer",
    "secondary_questions": ["question 1", "question 2", "question 3"],
    "purpose": "one of the purpose options",
    "content_output": "one of the content options",
    "expected_deliverables": ["deliverable1", "deliverable2"],
    "depth": "overview|detailed|expert",
    "focus_areas": ["area1", "area2"],
    "perspective": "target perspective or null",
    "time_sensitivity": "real_time|recent|historical|evergreen",
    "confidence": 0.85,
    "confidence_reason": "Brief explanation of why this confidence level (e.g., 'User provided clear keywords and context' or 'Input is vague, missing specific goals')",
    "great_example": "Example of what a great input would look like for this research (only if confidence < 0.8)",
    "needs_clarification": false,
    "clarifying_questions": [],
    "analysis_summary": "Brief summary of what the user wants"
}}
```

## IMPORTANT RULES

1. Always convert vague input into a specific primary question
2. Infer deliverables based on purpose (e.g., create_content → statistics + examples)
3. Use persona context to refine perspective and focus areas
4. If input is ambiguous, provide clarifying questions
5. Default to "detailed" depth unless input suggests otherwise
6. For content creation, include relevant deliverables automatically
"""

        return prompt
    
    def build_query_generation_prompt(
        self,
        intent: ResearchIntent,
        research_persona: Optional[ResearchPersona] = None,
    ) -> str:
        """
        Build prompt for generating targeted research queries.
        
        Generates multiple queries, each targeting a specific deliverable.
        """
        
        deliverables_list = "\n".join([
            f"- {d}: {self.DELIVERABLE_DESCRIPTIONS.get(ExpectedDeliverable(d), d)}"
            for d in intent.expected_deliverables
        ])
        
        persona_keywords = ""
        if research_persona and research_persona.suggested_keywords:
            persona_keywords = f"\nSUGGESTED KEYWORDS FROM PERSONA: {', '.join(research_persona.suggested_keywords[:10])}"
        
        # Get current date context
        date_context = self._get_current_date_context()
        now = datetime.now()
        current_year = now.year
        next_year = current_year + 1
        current_month_year = now.strftime("%B %Y")
        
        prompt = f"""You are a research query optimizer. Generate multiple targeted search queries based on the user's research intent.

## CURRENT DATE/TIME CONTEXT
{date_context}

**CRITICAL**: When generating queries:
- ALWAYS use the CURRENT YEAR ({current_year}) for time-sensitive queries
- For trends, predictions, or future-looking queries, use {current_year} or {next_year}
- For recent/real-time queries, use current month/year: {current_month_year}
- NEVER use outdated years from training data (e.g., 2024, 2025 if we're past those dates)
- When user mentions "latest", "current", "recent", or time-sensitive terms, prioritize {current_year} data

## RESEARCH INTENT

PRIMARY QUESTION: {intent.primary_question}

SECONDARY QUESTIONS:
{chr(10).join(f'- {q}' for q in intent.secondary_questions) if intent.secondary_questions else 'None'}

PURPOSE: {intent.purpose} - {self.PURPOSE_EXPLANATIONS.get(ResearchPurpose(intent.purpose), intent.purpose)}

CONTENT OUTPUT: {intent.content_output}

EXPECTED DELIVERABLES:
{deliverables_list}

DEPTH: {intent.depth}

FOCUS AREAS: {', '.join(intent.focus_areas) if intent.focus_areas else 'General'}

PERSPECTIVE: {intent.perspective or 'General audience'}

TIME SENSITIVITY: {intent.time_sensitivity or 'No specific requirement'}
{persona_keywords}

## YOUR TASK

Generate 4-8 targeted research queries. Each query should:
1. Target a specific deliverable or question
2. Be optimized for semantic search (Exa/Tavily)
3. Include relevant context for better results

For each query, specify:
- The query string
- What deliverable it targets
- Best provider (exa for semantic/deep, tavily for news/real-time, google for factual)
- Priority (1-5, higher = more important)
- What we expect to find

## OUTPUT FORMAT

Return a JSON object:
```json
{{
    "queries": [
        {{
            "query": "Healthcare AI adoption statistics {current_year} hospitals implementation data",
            "purpose": "key_statistics",
            "provider": "exa",
            "priority": 5,
            "expected_results": "Statistics on hospital AI adoption rates"
        }},
        {{
            "query": "AI healthcare trends predictions future outlook {current_year} {next_year}",
            "purpose": "trends",
            "provider": "tavily",
            "priority": 4,
            "expected_results": "Current trends and future predictions in healthcare AI"
        }}
    ],
    "enhanced_keywords": ["keyword1", "keyword2", "keyword3"],
    "research_angles": [
        "Angle 1: Focus on adoption challenges",
        "Angle 2: Focus on ROI and outcomes"
    ]
}}
```

## QUERY OPTIMIZATION RULES

1. For STATISTICS: Include words like "statistics", "data", "percentage", "report", "study", and CURRENT YEAR ({current_year})
2. For CASE STUDIES: Include "case study", "success story", "implementation", "example"
3. For TRENDS: Include "trends", "future", "predictions", "emerging", and CURRENT YEAR ({current_year}) or {next_year}
4. For EXPERT QUOTES: Include expert names if known, or "expert opinion", "interview"
5. For COMPARISONS: Include "vs", "compare", "comparison", "alternative"
6. For NEWS/REAL-TIME: Use Tavily, include CURRENT YEAR ({current_year}) and current month/year ({current_month_year})
7. For ACADEMIC/DEEP: Use Exa with neural search
8. **CRITICAL**: Always use {current_year} (not outdated years) for time-sensitive queries
"""

        return prompt
    
    def build_intent_aware_analysis_prompt(
        self,
        raw_results: str,
        intent: ResearchIntent,
        research_persona: Optional[ResearchPersona] = None,
    ) -> str:
        """
        Build prompt for analyzing research results based on user intent.
        
        This is the key prompt that extracts exactly what the user needs.
        """
        
        purpose_explanation = self.PURPOSE_EXPLANATIONS.get(
            ResearchPurpose(intent.purpose), 
            intent.purpose
        )
        
        deliverables_instructions = self._build_deliverables_instructions(intent.expected_deliverables)
        
        perspective_instruction = ""
        if intent.perspective:
            perspective_instruction = f"\n**PERSPECTIVE**: Analyze results from the viewpoint of: {intent.perspective}"
        
        # Get current date context
        date_context = self._get_current_date_context()
        now = datetime.now()
        current_year = now.year
        
        prompt = f"""You are a research analyst helping a content creator find exactly what they need. Your job is to analyze raw research results and extract precisely what the user is looking for.

## CURRENT DATE/TIME CONTEXT
{date_context}

**CRITICAL**: When analyzing results:
- Prioritize data from CURRENT YEAR ({current_year}) or recent dates
- If statistics/quotes mention outdated years, note the recency in context
- For trends/predictions, ensure timelines reference {current_year} or future years
- NEVER present outdated data as "current" or "latest" - always check dates

## USER'S RESEARCH INTENT

**PRIMARY QUESTION**: {intent.primary_question}

**SECONDARY QUESTIONS TO ANSWER**:
{chr(10).join(f'- {q}' for q in intent.secondary_questions) if intent.secondary_questions else 'None specified'}

**FOCUS AREAS** (prioritize information related to these):
{', '.join(intent.focus_areas) if intent.focus_areas else 'General - no specific focus areas'}

**ALSO ANSWERING** (address these topics if found in results):
{', '.join(intent.also_answering) if intent.also_answering else 'None specified'}

**PURPOSE**: {intent.purpose}
→ {purpose_explanation}

**CONTENT OUTPUT**: {intent.content_output}

**EXPECTED DELIVERABLES**: {', '.join(intent.expected_deliverables)}

**PERSPECTIVE**: {intent.perspective or 'General audience'}
{perspective_instruction}

## RAW RESEARCH RESULTS

{raw_results[:15000]}  # Truncated for token limits

## YOUR TASK

Analyze the raw research results and extract EXACTLY what the user needs. Use a **generalized approach** - don't over-optimize for specific fields, but ensure all intent aspects are considered naturally.

### ANALYSIS GUIDELINES:

1. **PRIMARY QUESTION**: Always provide a direct, clear answer to the primary question in 2-3 sentences.

2. **SECONDARY QUESTIONS**: For each secondary question, provide an answer if information is available in the results. If not available, note it in gaps_identified. Don't force answers - only include what's actually in the results.

3. **FOCUS AREAS**: When extracting deliverables, prioritize information that relates to the focus areas. If focus areas are specified:
   - Weight relevance scores higher for sources/content matching focus areas
   - Include focus area context in extracted statistics, quotes, case studies
   - If results don't address focus areas, note this in gaps_identified
   - Provide a brief summary of what was found for each focus area in focus_areas_coverage

4. **ALSO ANSWERING**: If results contain information about "also answering" topics, include it naturally in the analysis. Don't create separate sections unless the information is substantial. Provide a brief summary of what was found for each topic in also_answering_coverage.

5. **GENERALIZED EXTRACTION**: 
   - Extract deliverables based on expected_deliverables
   - Use perspective to frame information appropriately
   - Consider content_output when structuring results
   - Don't over-optimize - let the results guide what's extracted

6. **CONTEXTUAL LINKING**: When extracting information, consider:
   - How it relates to the primary question
   - Which secondary questions it answers
   - Which focus areas it addresses
   - This helps create a cohesive research result

{deliverables_instructions}

## OUTPUT REQUIREMENTS

Provide results in this JSON structure:

```json
{{
    "primary_answer": "Direct 2-3 sentence answer to the primary question",
    "secondary_answers": {{
        "Secondary Question 1?": "Answer if found in results, or null if not available",
        "Secondary Question 2?": "Answer if found in results, or null if not available"
    }},
    "focus_areas_coverage": {{
        "Focus Area 1": "Brief summary of what was found related to this focus area, or null if not covered",
        "Focus Area 2": "Brief summary of what was found related to this focus area, or null if not covered"
    }},
    "also_answering_coverage": {{
        "Topic 1": "Information found about this topic, or null if not found",
        "Topic 2": "Information found about this topic, or null if not found"
    }},
    "executive_summary": "2-3 sentence executive summary of all findings",
    "key_takeaways": [
        "Key takeaway 1 - most important finding",
        "Key takeaway 2",
        "Key takeaway 3",
        "Key takeaway 4",
        "Key takeaway 5"
    ],
    "statistics": [
        {{
            "statistic": "72% of hospitals plan to adopt AI by {current_year}",
            "value": "72%",
            "context": "Survey of 500 US hospitals in {current_year}",
            "source": "Healthcare AI Report {current_year}",
            "url": "https://example.com/report",
            "credibility": 0.9,
            "recency": "{current_year}"
        }}
    ],
    "expert_quotes": [
        {{
            "quote": "AI will revolutionize patient care within 5 years",
            "speaker": "Dr. Jane Smith",
            "title": "Chief Medical Officer",
            "organization": "HealthTech Inc",
            "source": "TechCrunch",
            "url": "https://example.com/article"
        }}
    ],
    "case_studies": [
        {{
            "title": "Mayo Clinic AI Implementation",
            "organization": "Mayo Clinic",
            "challenge": "High patient wait times",
            "solution": "AI-powered triage system",
            "outcome": "40% reduction in wait times",
            "key_metrics": ["40% faster triage", "95% patient satisfaction"],
            "source": "Healthcare IT News",
            "url": "https://example.com"
        }}
    ],
    "trends": [
        {{
            "trend": "AI-assisted diagnostics adoption",
            "direction": "growing",
            "evidence": ["25% YoY growth", "Major hospital chains investing"],
            "impact": "Could reduce misdiagnosis by 30%",
            "timeline": "Expected mainstream by {current_year + 2}",
            "sources": ["url1", "url2"]
        }}
    ],
    "comparisons": [
        {{
            "title": "Top AI Healthcare Platforms",
            "criteria": ["Cost", "Features", "Support"],
            "items": [
                {{
                    "name": "Platform A",
                    "pros": ["Easy integration", "Good support"],
                    "cons": ["Higher cost"],
                    "features": {{"Cost": "$500/month", "Support": "24/7"}}
                }}
            ],
            "verdict": "Platform A best for large hospitals"
        }}
    ],
    "best_practices": [
        "Start with a pilot program before full deployment",
        "Ensure staff training is comprehensive"
    ],
    "step_by_step": [
        "Step 1: Assess current infrastructure",
        "Step 2: Define use cases",
        "Step 3: Select vendor"
    ],
    "pros_cons": {{
        "subject": "AI in Healthcare",
        "pros": ["Improved accuracy", "Cost savings"],
        "cons": ["Initial investment", "Training required"],
        "balanced_verdict": "Benefits outweigh costs for most hospitals"
    }},
    "definitions": {{
        "Clinical AI": "AI systems designed for medical diagnosis and treatment recommendations"
    }},
    "examples": [
        "Example: Hospital X reduced readmissions by 25% using predictive AI"
    ],
    "predictions": [
        "By {current_year + 5}, AI will assist in 80% of initial diagnoses"
    ],
    "suggested_outline": [
        "1. Introduction: The AI Healthcare Revolution",
        "2. Current State: Where We Are Today",
        "3. Key Statistics and Trends",
        "4. Case Studies: Success Stories",
        "5. Implementation Guide",
        "6. Future Outlook"
    ],
    "sources": [
        {{
            "title": "Healthcare AI Report {current_year}",
            "url": "https://example.com",
            "relevance_score": 0.95,
            "relevance_reason": "Directly addresses adoption statistics",
            "content_type": "research report",
            "credibility_score": 0.9
        }}
    ],
    "confidence": 0.85,
    "gaps_identified": [
        "Specific cost data for small clinics not found",
        "Limited information on regulatory challenges"
    ],
    "follow_up_queries": [
        "AI healthcare regulations FDA {current_year}",
        "Small clinic AI implementation costs"
    ]
}}
```

## CRITICAL RULES

1. **ONLY include information directly from the raw results** - do not make up data
2. **ALWAYS include source URLs** for every statistic, quote, and case study
3. **If a deliverable type has no relevant data**, return an empty array for it
4. **Prioritize recency and credibility** when multiple sources conflict
5. **Answer the PRIMARY QUESTION directly** in 2-3 clear sentences
6. **Keep KEY TAKEAWAYS to 5-7 points** - the most important findings
7. **Add to gaps_identified** if expected information is missing
8. **Suggest follow_up_queries** for gaps or incomplete areas
9. **Rate confidence** based on how well results match the user's intent
10. **Include deliverables ONLY if they are in expected_deliverables** or critical to the question
11. **Don't over-optimize** - use a natural, generalized approach that considers all intent fields without forcing connections
12. **For focus_areas_coverage and also_answering_coverage**: Only include entries for focus areas/topics that actually have information in the results. Use null for areas/topics not covered.
"""

        return prompt
    
    def _build_persona_context(
        self,
        research_persona: Optional[ResearchPersona],
        industry: Optional[str],
        target_audience: Optional[str],
    ) -> str:
        """Build persona context section for prompts."""
        
        if not research_persona and not industry:
            return "No specific persona context available."
        
        context_parts = []
        
        if research_persona:
            context_parts.append(f"INDUSTRY: {research_persona.default_industry}")
            context_parts.append(f"TARGET AUDIENCE: {research_persona.default_target_audience}")
            if research_persona.suggested_keywords:
                context_parts.append(f"TYPICAL TOPICS: {', '.join(research_persona.suggested_keywords[:5])}")
            if research_persona.research_angles:
                context_parts.append(f"RESEARCH ANGLES: {', '.join(research_persona.research_angles[:3])}")
        else:
            if industry:
                context_parts.append(f"INDUSTRY: {industry}")
            if target_audience:
                context_parts.append(f"TARGET AUDIENCE: {target_audience}")
        
        return "\n".join(context_parts)
    
    def _build_competitor_context(self, competitor_data: Optional[List[Dict]]) -> str:
        """Build competitor context section for prompts."""
        
        if not competitor_data:
            return ""
        
        competitor_names = []
        for comp in competitor_data[:5]:  # Limit to 5
            name = comp.get("name") or comp.get("domain") or comp.get("url", "Unknown")
            competitor_names.append(name)
        
        if competitor_names:
            return f"\nKNOWN COMPETITORS: {', '.join(competitor_names)}"
        
        return ""
    
    def _build_deliverables_instructions(self, expected_deliverables: List[str]) -> str:
        """Build specific extraction instructions for each expected deliverable."""
        
        instructions = ["### EXTRACTION INSTRUCTIONS\n"]
        instructions.append("For each requested deliverable, extract the following:\n")
        
        deliverable_instructions = {
            ExpectedDeliverable.KEY_STATISTICS: """
**STATISTICS**:
- Extract ALL relevant statistics with exact numbers
- Include source attribution (publication name, URL)
- Note the recency of the data
- Rate credibility based on source authority
- Format: statistic statement, value, context, source, URL, credibility score
""",
            ExpectedDeliverable.EXPERT_QUOTES: """
**EXPERT QUOTES**:
- Extract authoritative quotes from named experts
- Include speaker name, title, and organization
- Provide context for the quote
- Include source URL
""",
            ExpectedDeliverable.CASE_STUDIES: """
**CASE STUDIES**:
- Summarize each case study: challenge → solution → outcome
- Include key metrics and results
- Name the organization involved
- Provide source URL
""",
            ExpectedDeliverable.TRENDS: """
**TRENDS**:
- Identify current and emerging trends
- Note direction: growing, declining, emerging, or stable
- List supporting evidence
- Include timeline predictions if available
- Cite sources
""",
            ExpectedDeliverable.COMPARISONS: """
**COMPARISONS**:
- Build comparison tables where applicable
- Define clear comparison criteria
- List pros and cons for each option
- Provide a verdict/recommendation if data supports it
""",
            ExpectedDeliverable.BEST_PRACTICES: """
**BEST PRACTICES**:
- Extract recommended approaches
- Provide actionable guidelines
- Order by importance or sequence
""",
            ExpectedDeliverable.STEP_BY_STEP: """
**STEP BY STEP**:
- Extract process/how-to instructions
- Number steps clearly
- Include any prerequisites or requirements
""",
            ExpectedDeliverable.PROS_CONS: """
**PROS AND CONS**:
- List advantages (pros)
- List disadvantages (cons)
- Provide a balanced verdict
""",
            ExpectedDeliverable.DEFINITIONS: """
**DEFINITIONS**:
- Extract clear explanations of key terms and concepts
- Keep definitions concise but comprehensive
""",
            ExpectedDeliverable.EXAMPLES: """
**EXAMPLES**:
- Extract concrete examples that illustrate key points
- Include real-world applications
""",
            ExpectedDeliverable.PREDICTIONS: """
**PREDICTIONS**:
- Extract future outlook and predictions
- Note the source and their track record if known
- Include timeframes where mentioned
""",
            ExpectedDeliverable.CITATIONS: """
**CITATIONS**:
- List all authoritative sources with URLs
- Rate credibility and relevance
- Note content type (research, news, opinion, etc.)
""",
        }
        
        for deliverable in expected_deliverables:
            try:
                d_enum = ExpectedDeliverable(deliverable)
                if d_enum in deliverable_instructions:
                    instructions.append(deliverable_instructions[d_enum])
            except ValueError:
                pass
        
        return "\n".join(instructions)
