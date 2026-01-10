# Exa & Tavily Options Inference Guide

**Date**: 2025-01-29  
**Status**: Current Implementation Review

---

## Overview

When a user clicks "Intent & Options" button, the system uses AI to infer optimal Exa and Tavily API settings based on the user's research intent. This document explains how these options are generated.

---

## Flow: Intent & Options Button Click

```
User clicks "Intent & Options"
  ↓
Frontend: intentResearchApi.analyzeIntent()
  ↓
Backend: /api/research/intent/analyze
  ↓
UnifiedResearchAnalyzer.analyze()
  ↓
Single LLM Call with unified_prompt_builder.py
  ↓
LLM Returns:
  - ResearchIntent (with purpose, depth, focus_areas, also_answering, etc.)
  - ResearchQueries (4-8 diverse queries)
  - exa_config (optimized Exa settings with justifications)
  - tavily_config (optimized Tavily settings with justifications)
  - recommended_provider
  ↓
Backend maps to optimized_config
  ↓
Frontend receives AnalyzeIntentResponse with optimized_config
  ↓
Frontend applies optimized_config to ResearchConfig
  ↓
User sees optimized Exa/Tavily options in AdvancedProviderOptionsSection
```

---

## How Options Are Inferred

### 1. Time Sensitivity Rules

**Based on**: `intent.time_sensitivity` field

| Time Sensitivity | Exa Settings | Tavily Settings |
|-----------------|--------------|-----------------|
| **real_time** | `startPublishedDate = current year`, `type = "auto" or "fast"` | `time_range = "day" or "week"`, `topic = "news"` |
| **recent** | `startPublishedDate = current year or last 6 months` | `time_range = "month" or "week"` |
| **historical** | No date filters, `type = "deep" or "neural"` | `time_range = "year" or null`, `topic = "general"` |
| **evergreen** | No date filters, `type = "deep"` | `time_range = null`, `topic = "general"` |

**Example**:
- User input: "Latest AI trends in 2025"
- Time sensitivity inferred: `real_time`
- Exa: `startPublishedDate = "2025-01-01"`, `type = "fast"`
- Tavily: `time_range = "week"`, `topic = "news"`

---

### 2. Content Type Based on Focus Areas

**Based on**: `intent.focus_areas` field

| Focus Area Keywords | Exa Category | Exa Type | Tavily Topic |
|---------------------|-------------|----------|--------------|
| "academic", "research", "studies" | `"research paper"` | `"deep" or "neural"` | `"general"` |
| | `includeDomains = ["arxiv.org", "nature.com", "pubmed.ncbi.nlm.nih.gov"]` | | |
| "companies", "competitors", "business" | `"company"` | `"auto" or "deep"` | `"general"` |
| "news", "trends", "current events" | `"news"` (if using Exa) | `"auto"` | `"news"` |
| | | | `search_depth = "advanced"` |
| "social", "twitter", "social media" | `"tweet"` | `"auto"` | `"general"` |
| "github", "code", "technical" | `"github"` | `"auto" or "deep"` | `"general"` |

**Example**:
- User input: "AI research papers on transformer architectures"
- Focus areas inferred: `["academic", "research"]`
- Exa: `category = "research paper"`, `type = "deep"`, `includeDomains = ["arxiv.org", "nature.com"]`
- Tavily: `topic = "general"`

---

### 3. Depth-Based Settings

**Based on**: `intent.depth` field (overview, detailed, expert)

| Depth Level | Exa Settings | Tavily Settings |
|-------------|--------------|-----------------|
| **expert** | `type = "deep"`, `context = true`, `contextMaxCharacters = 15000+`, `numResults = 20-50` | `search_depth = "advanced"`, `chunks_per_source = 3`, `max_results = 15-20` |
| **detailed** | `type = "auto" or "deep"`, `context = true`, `contextMaxCharacters = 10000+`, `numResults = 10-20` | `search_depth = "advanced" or "basic"`, `chunks_per_source = 3`, `max_results = 10-15` |
| **overview** | `type = "auto" or "fast"`, `numResults = 5-10` | `search_depth = "basic" or "fast"`, `max_results = 5-10` |

**Example**:
- User input: "Comprehensive analysis of quantum computing"
- Depth inferred: `expert`
- Exa: `type = "deep"`, `context = true`, `contextMaxCharacters = 15000`, `numResults = 30`
- Tavily: `search_depth = "advanced"`, `chunks_per_source = 3`, `max_results = 15`

---

### 4. Query-Specific Settings

**Based on**: Primary query characteristics

| Query Type | Exa Settings | Tavily Settings |
|------------|--------------|-----------------|
| **Comprehensive** (addresses multiple secondary questions/focus areas) | `type = "deep"`, `context = true`, `contextMaxCharacters = 15000+` | `search_depth = "advanced"`, `chunks_per_source = 3` |
| **Simple factual** | `type = "fast"`, `numResults = 5-10` | `search_depth = "ultra-fast"`, `max_results = 5` |
| **Time-sensitive** | Apply time filters based on urgency | Apply time_range based on urgency |
| **Content-specific** | Match category to content type | Match topic to content type |

**Example**:
- Primary query: "What are the best practices for React performance optimization?"
- Query type: Comprehensive (needs detailed analysis)
- Exa: `type = "deep"`, `context = true`, `contextMaxCharacters = 12000`
- Tavily: `search_depth = "advanced"`, `chunks_per_source = 3`

---

### 5. Also Answering Topics Considerations

**Based on**: `intent.also_answering` field

**Rules**:
- If also_answering topics need different time ranges:
  - Use broader `time_range` in Tavily (e.g., "year" instead of "month")
  - Don't apply strict date filters in Exa
- If also_answering topics need different sources:
  - Consider including additional domains in `includeDomains`
  - Use more comprehensive search (`type = "deep"` in Exa)

**Example**:
- Primary: "Latest AI trends"
- Also answering: ["Historical AI development", "Future predictions"]
- Exa: No strict date filters, `type = "deep"` for comprehensive coverage
- Tavily: `time_range = "year"` to cover historical and recent

---

### 6. Provider Selection Logic

**Based on**: Combined analysis of all intent fields

**Use EXA when**:
- Primary query needs semantic understanding
- Focus areas include "academic", "research", "companies"
- Depth = "expert" or "detailed"
- Need comprehensive context (`context = true`)
- Query targets specific content types (research papers, companies, GitHub)

**Use TAVILY when**:
- Time sensitivity = "real_time" or "recent"
- Focus areas include "news", "trends", "current events"
- Need quick AI-generated answers
- Primary query is about recent developments
- Query needs real-time information

**Example**:
- User input: "Latest news about AI regulation"
- Provider selected: **Tavily** (real-time news focus)
- Tavily: `topic = "news"`, `search_depth = "advanced"`, `time_range = "week"`

---

## Exa Config Options Generated

The AI generates these Exa options with justifications:

### Core Options
- **`type`**: `"auto" | "fast" | "deep" | "neural" | "keyword"`
  - Justification references: query complexity, depth, time sensitivity
- **`category`**: `"company" | "research paper" | "news" | "linkedin profile" | "github" | "tweet" | "personal site" | "pdf" | "financial report"`
  - Justification references: focus_areas, content type needed
- **`numResults`**: `1-100`
  - Justification references: depth, query complexity, secondary questions count
- **`includeDomains`**: Array of domain strings
  - Justification references: focus_areas, content type requirements
- **`startPublishedDate`**: Date string (YYYY-MM-DD)
  - Justification references: time_sensitivity, query time requirements

### Content Options
- **`highlights`**: `true | false`
  - Justification: Whether snippets are needed for quick scanning
- **`context`**: `true | false` (required for `type = "deep"`)
  - Justification: Whether full context needed for RAG/AI processing
- **`contextMaxCharacters`**: Number (if context = true)
  - Justification: Depth requirements, query complexity

### Advanced Options (if applicable)
- **`additionalQueries`**: Array of query strings (only for `type = "deep"`)
  - Justification: Query variations needed for comprehensive coverage
- **`livecrawl`**: `"never" | "fallback" | "preferred" | "always"`
  - Justification: Freshness requirements based on time_sensitivity

---

## Tavily Config Options Generated

The AI generates these Tavily options with justifications:

### Core Options
- **`topic`**: `"general" | "news" | "finance"`
  - Justification references: focus_areas, content type
- **`search_depth`**: `"basic" | "advanced" | "fast" | "ultra-fast"`
  - Justification references: depth, query complexity, speed requirements
- **`include_answer`**: `true | false | "basic" | "advanced"`
  - Justification: Whether AI-generated answer is needed
- **`time_range`**: `"day" | "week" | "month" | "year" | null`
  - Justification references: time_sensitivity, query time requirements
- **`max_results`**: `0-20`
  - Justification references: depth, query complexity

### Advanced Options
- **`chunks_per_source`**: `1-3` (only for `search_depth = "advanced"`)
  - Justification: Depth requirements, comprehensive coverage needs
- **`include_raw_content`**: `true | false | "markdown" | "text"`
  - Justification: Whether full content needed for analysis
- **`country`**: Country code (only for `topic = "general"`)
  - Justification: Geographic relevance based on target_audience

---

## Example: Complete Inference Flow

### User Input
```
Keywords: "AI marketing tools for small businesses"
Purpose: create_content (user-selected)
Content Output: blog_post (user-selected)
Depth: detailed (user-selected)
```

### AI Inference
```
Intent:
  - primary_question: "What are the best AI marketing tools for small businesses?"
  - secondary_questions: ["What are the pricing models?", "What features do they offer?"]
  - focus_areas: ["tools", "small business", "marketing automation"]
  - also_answering: ["How to choose the right tool", "Implementation best practices"]
  - time_sensitivity: "recent"
  - depth: "detailed"

Recommended Provider: EXA (needs comprehensive analysis, not just news)

Exa Config:
  - type: "auto"
    justification: "Balanced speed and quality for comprehensive tool research"
  - category: null (general search)
    justification: "Tools can be found across multiple content types"
  - numResults: 15
    justification: "Detailed depth requires more sources to cover tools, pricing, and features"
  - includeDomains: []
    justification: "No specific domain restrictions needed"
  - startPublishedDate: "2024-01-01"
    justification: "Recent time sensitivity requires current year data"
  - highlights: true
    justification: "Snippets help quickly identify relevant tools"
  - context: true
    justification: "Detailed depth requires full context for comprehensive analysis"
  - contextMaxCharacters: 10000
    justification: "Detailed depth needs substantial context per source"

Tavily Config:
  - topic: "general"
    justification: "General topic covers tools and business content"
  - search_depth: "advanced"
    justification: "Detailed depth requires comprehensive search"
  - include_answer: true
    justification: "AI-generated answers provide quick insights"
  - time_range: "year"
    justification: "Recent time sensitivity with also_answering topics needing broader coverage"
  - max_results: 12
    justification: "Detailed depth requires multiple sources"
  - chunks_per_source: 3
    justification: "Detailed depth needs comprehensive content per source"
```

---

## Key Files

### Backend
1. **`backend/services/research/intent/unified_prompt_builder.py`**
   - Contains all optimization rules (lines 155-275)
   - Defines how intent fields map to Exa/Tavily settings

2. **`backend/services/research/intent/unified_schema_builder.py`**
   - Defines JSON schema for exa_config and tavily_config (lines 67-124)
   - Specifies all available options and their types

3. **`backend/services/research/intent/unified_result_parser.py`**
   - Extracts exa_config and tavily_config from LLM response (lines 205-206)

4. **`backend/api/research/handlers/intent.py`**
   - Maps exa_config/tavily_config to optimized_config (lines 124-155)
   - Returns optimized_config in AnalyzeIntentResponse

### Frontend
1. **`frontend/src/components/Research/types/intent.types.ts`**
   - Defines OptimizedConfig interface (lines 224-280)
   - Includes all Exa/Tavily options with justifications

2. **`frontend/src/components/Research/steps/components/IntentConfirmationPanel/AdvancedProviderOptionsSection.tsx`**
   - Displays optimized Exa/Tavily options
   - Shows AI justifications for each option

3. **`frontend/src/components/Research/steps/ResearchInput.tsx`**
   - Applies optimized_config to ResearchConfig (lines 464-512)

---

## Current Implementation Status

### ✅ Fully Implemented
- Time sensitivity → Exa/Tavily date filters
- Focus areas → Exa category / Tavily topic
- Depth → Exa type / Tavily search_depth
- Query characteristics → Provider selection
- Also answering → Broader time ranges

### ⚠️ Partially Implemented
- Some Exa options are inferred but not all are exposed in UI
- Some Tavily options are inferred but not all are exposed in UI
- Advanced options (livecrawl, additionalQueries) are in schema but rarely used

### 📋 Options Available in Schema (May Not All Be Used)

**Exa Options**:
- ✅ type, category, numResults, includeDomains, startPublishedDate, highlights, context
- ⚠️ excludeDomains, contextMaxCharacters, additionalQueries, livecrawl

**Tavily Options**:
- ✅ topic, search_depth, include_answer, time_range, max_results, chunks_per_source
- ⚠️ start_date, end_date, include_raw_content, country, include_images, include_image_descriptions, include_favicon, auto_parameters

---

## References

- `docs/ALwrity Researcher/EXA_INTEGRATION_ENHANCEMENTS.md` - Exa search types and latency
- `docs/ALwrity Researcher/EXA_API_OPTIONS_AUDIT.md` - Complete Exa API options comparison
- `docs/ALwrity Researcher/EXA_TAVILY_OPTIONS_DISPLAY_REVIEW.md` - UI display review
- `docs/ALwrity Researcher/INTENT_DRIVEN_RESEARCH_IMPLEMENTATION_STATUS.md` - Implementation status

---

**Status**: Current implementation infers Exa and Tavily options based on comprehensive intent analysis with detailed justifications.
