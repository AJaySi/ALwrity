# Research Persona Data Sources & Generated Fields

## Overview

The Research Persona is an AI-generated profile that provides hyper-personalized research defaults, suggestions, and configurations based on a user's onboarding data. This document details what data is used to generate the persona and what fields are produced.

---

## Data Sources Used for Generation

### 1. **Website Analysis** (`website_analysis`)
**Source**: Onboarding Step 2 - Website Analysis  
**Location**: `WebsiteAnalysis` table in database  
**Key Fields Used**:
- `website_url`: User's website URL
- `writing_style`: Tone, voice, complexity, engagement level
- `content_characteristics`: Sentence structure, vocabulary, paragraph organization
- `target_audience`: Demographics, expertise level, industry focus
- `content_type`: Primary type, secondary types, purpose
- `recommended_settings`: Writing tone, target audience, content type
- `style_patterns`: Writing patterns analysis
- `style_guidelines`: Generated guidelines

**Usage**: Extracts industry focus, target audience, content preferences, and writing style patterns to inform research defaults.

### 2. **Core Persona** (`core_persona`)
**Source**: Onboarding Step 4 - Persona Generation  
**Location**: `PersonaData.core_persona` JSON field  
**Key Fields Used**:
- `industry`: User's primary industry
- `target_audience`: Detailed audience description
- `interests`: User's content interests and focus areas
- `pain_points`: Challenges and needs
- `content_goals`: What the user wants to achieve with content

**Usage**: Primary source for industry, audience, and content strategy insights.

### 3. **Research Preferences** (`research_preferences`)
**Source**: Onboarding Step 3 - Research Preferences  
**Location**: `ResearchPreferences` table  
**Key Fields Used**:
- `research_depth`: "standard", "comprehensive", "basic"
- `content_types`: Array of content types (e.g., ["blog", "social", "video"])
- `auto_research`: Whether to auto-enable research
- `factual_content`: Preference for factual vs. opinion-based content
- `writing_style`: Inherited from website analysis
- `content_characteristics`: Inherited from website analysis
- `target_audience`: Inherited from website analysis

**Usage**: Determines default research mode, provider preferences, and content type focus.

### 4. **Business Information** (`business_info`)
**Source**: Constructed from persona data and website analysis  
**Key Fields Used**:
- `industry`: Extracted from `core_persona.industry` or `website_analysis.target_audience.industry_focus`
- `target_audience`: Extracted from `core_persona.target_audience` or `website_analysis.target_audience.demographics`

**Usage**: Fallback and inference source when core persona data is minimal.

### 5. **Competitor Analysis** (Future Enhancement)
**Source**: Onboarding Step 3 - Competitor Discovery  
**Location**: `CompetitorAnalysis` table  
**Status**: Currently not used in persona generation, but available for future enhancements

**Potential Usage**: Could inform industry context, competitive landscape insights, and domain suggestions.

---

## Generated Research Persona Fields

### **1. Smart Defaults**

| Field | Type | Description | Source Priority |
|-------|------|-------------|-----------------|
| `default_industry` | string | User's primary industry | 1. core_persona.industry<br>2. business_info.industry<br>3. website_analysis.target_audience.industry_focus<br>4. Inferred from content_types |
| `default_target_audience` | string | Detailed audience description | 1. core_persona.target_audience<br>2. website_analysis.target_audience<br>3. business_info.target_audience<br>4. Default: "Professionals and content consumers" |
| `default_research_mode` | string | "basic" \| "comprehensive" \| "targeted" | Based on research_preferences.research_depth and content_type preferences |
| `default_provider` | string | "exa" \| "tavily" \| "google" | Based on user's typical research needs:<br>- Academic/research: "exa"<br>- News/current events: "tavily"<br>- General business: "exa"<br>- Default: "exa" |

### **2. Keyword Intelligence**

| Field | Type | Description | Generation Logic |
|-------|------|-------------|------------------|
| `suggested_keywords` | string[] | 8-12 relevant keywords | Generated from:<br>- User's industry<br>- Core persona interests<br>- Content goals<br>- Research preferences |
| `keyword_expansion_patterns` | Dict<string, string[]> | Mapping of keywords to expanded terms | 10-15 patterns like:<br>`{"AI": ["healthcare AI", "medical AI"], "tools": ["medical devices"]}`<br>Focuses on industry-specific terminology |

### **3. Exa Provider Optimization**

| Field | Type | Description | Generation Logic |
|-------|------|-------------|------------------|
| `suggested_exa_domains` | string[] | 4-6 authoritative domains | Industry-specific authoritative sources:<br>- Healthcare: ["pubmed.gov", "nejm.org"]<br>- Finance: ["sec.gov", "bloomberg.com"]<br>- Tech: ["github.com", "stackoverflow.com"] |
| `suggested_exa_category` | string? | Exa content category | Based on industry:<br>- Healthcare/Science: "research paper"<br>- Finance: "financial report"<br>- Tech/Business: "company" or "news"<br>- Social/Marketing: "tweet" or "linkedin profile"<br>- Default: null (all categories) |
| `suggested_exa_search_type` | string? | Exa search algorithm | Based on content needs:<br>- Academic/research: "neural"<br>- Current news/trends: "fast"<br>- General research: "auto"<br>- Code/technical: "neural" |

### **4. Tavily Provider Optimization**

| Field | Type | Description | Generation Logic |
|-------|------|-------------|------------------|
| `suggested_tavily_topic` | string? | "general" \| "news" \| "finance" | Based on content type:<br>- Financial content: "finance"<br>- News/current events: "news"<br>- General research: "general" |
| `suggested_tavily_search_depth` | string? | "basic" \| "advanced" \| "fast" \| "ultra-fast" | Based on research needs:<br>- Quick overview: "basic"<br>- In-depth analysis: "advanced"<br>- Breaking news: "fast" |
| `suggested_tavily_include_answer` | string? | "false" \| "basic" \| "advanced" | Based on query type:<br>- Factual queries: "advanced"<br>- Research summaries: "basic"<br>- Custom content: "false" |
| `suggested_tavily_time_range` | string? | "day" \| "week" \| "month" \| "year" \| null | Based on recency needs:<br>- Breaking news: "day"<br>- Recent developments: "week"<br>- Industry analysis: "month"<br>- Historical: null |
| `suggested_tavily_raw_content_format` | string? | "false" \| "markdown" \| "text" | Based on use case:<br>- Blog content: "markdown"<br>- Text extraction: "text"<br>- No raw content: "false" |

### **5. Provider Selection Logic**

| Field | Type | Description | Generation Logic |
|-------|------|-------------|------------------|
| `provider_recommendations` | Dict<string, string> | Use case → provider mapping | Example:<br>`{"trends": "tavily", "deep_research": "exa", "factual": "google", "news": "tavily", "academic": "exa"}` |

### **6. Research Intelligence**

| Field | Type | Description | Generation Logic |
|-------|------|-------------|------------------|
| `research_angles` | string[] | 5-8 alternative research angles | Generated from:<br>- User's pain points<br>- Industry trends<br>- Content goals<br>- Audience interests<br>Examples: "Compare {topic} tools", "{topic} ROI analysis" |
| `query_enhancement_rules` | Dict<string, string> | Templates for improving vague queries | 5-8 enhancement patterns:<br>`{"vague_ai": "Research: AI applications in {industry} for {audience}", "vague_tools": "Compare top {industry} tools"}` |

### **7. Research Presets**

| Field | Type | Description | Generation Logic |
|-------|------|-------------|------------------|
| `recommended_presets` | ResearchPreset[] | 3-5 personalized preset templates | Each preset includes:<br>- `name`: Descriptive name<br>- `keywords`: Research query<br>- `industry`: User's industry<br>- `target_audience`: User's audience<br>- `research_mode`: "basic" \| "comprehensive" \| "targeted"<br>- `config`: Complete ResearchConfig object<br>- `description`: Brief explanation |

### **8. Research Preferences (Structured)**

| Field | Type | Description | Source |
|-------|------|-------------|--------|
| `research_preferences` | Dict<string, any> | Structured research preferences | Extracted from onboarding:<br>- `research_depth`: From research_preferences.research_depth<br>- `content_types`: From research_preferences.content_types<br>- `auto_research`: From research_preferences.auto_research<br>- `factual_content`: From research_preferences.factual_content |

### **9. Metadata**

| Field | Type | Description |
|-------|------|-------------|
| `generated_at` | string? | ISO timestamp of generation |
| `confidence_score` | float? | Confidence score 0-1 (higher = richer data) |
| `version` | string? | Schema version (e.g., "1.0") |

---

## Data Collection Process

### Step 1: Collect Onboarding Data
```python
onboarding_data = {
    "website_analysis": get_website_analysis(user_id),
    "persona_data": get_persona_data(user_id),
    "research_preferences": get_research_preferences(user_id),
    "business_info": construct_business_info(persona_data, website_analysis)
}
```

### Step 2: Build AI Prompt
The prompt includes:
- All onboarding data (JSON formatted)
- Detailed instructions for each field
- Examples and use cases
- Rules for handling minimal data scenarios

### Step 3: LLM Generation
- Uses structured JSON response format
- Validates against `ResearchPersona` Pydantic model
- Adds metadata (generated_at, confidence_score)

### Step 4: Save to Database
- Stored in `PersonaData.research_persona` JSON field
- Cached with 7-day TTL
- Timestamp stored in `PersonaData.research_persona_generated_at`

---

## Handling Minimal Data Scenarios

When onboarding data is incomplete, the AI uses intelligent inference:

1. **Industry Inference**:
   - From `content_types`: "blog" → "Content Marketing", "video" → "Video Content Creation"
   - From `website_analysis.content_characteristics`: Patterns suggest industry
   - Default: "Technology" or "Business Consulting"

2. **Target Audience Inference**:
   - From `writing_style`: Complexity level suggests audience
   - From `content_goals`: Purpose suggests audience
   - Default: "Professionals and content consumers"

3. **Provider Defaults**:
   - Always defaults to "exa" for content creators
   - Uses "tavily" only for news/current events focus

4. **Never Uses "General"**:
   - The prompt explicitly instructs to never use "General"
   - Always infers specific categories based on available context

---

## Frontend Display

### Currently Displayed Fields:
✅ Default Settings (industry, audience, mode, provider)  
✅ Suggested Keywords  
✅ Research Angles  
✅ Recommended Presets  
✅ Metadata (generated_at, confidence_score, version)

### Recently Added Fields (Enhanced Display):
✅ Keyword Expansion Patterns  
✅ Exa Provider Settings (domains, category, search_type)  
✅ Tavily Provider Settings (topic, depth, answer, time_range, format)  
✅ Provider Recommendations  
✅ Query Enhancement Rules  
✅ Research Preferences (structured)

---

## Future Enhancements

1. **Competitor Analysis Integration**: Use competitor data to inform industry context and domain suggestions
2. **Research History**: Learn from past research queries to improve suggestions
3. **A/B Testing**: Test different persona generation strategies
4. **User Feedback Loop**: Allow users to rate and improve persona suggestions
5. **Multi-Industry Support**: Handle users with multiple industries/niches

---

## API Endpoints

- `GET /api/research/persona-defaults`: Get persona defaults (cached only)
- `GET /api/research/research-persona`: Get or generate research persona
- `POST /api/research/research-persona?force_refresh=true`: Force regenerate persona

---

## Related Files

- **Backend**: `backend/services/research/research_persona_service.py`
- **Prompt Builder**: `backend/services/research/research_persona_prompt_builder.py`
- **Models**: `backend/models/research_persona_models.py`
- **API**: `backend/api/research_config.py`
- **Frontend**: `frontend/src/pages/ResearchDashboard/ResearchDashboard.tsx` (Persona Details Modal)
