# Current Research Engine Architecture Overview

**Date**: 2025-01-29  
**Status**: Authoritative Architecture Documentation

---

## 📋 Overview

This document provides a comprehensive overview of the current Research Engine architecture. This is the **single source of truth** for understanding how the research system works.

**Note**: For detailed implementation rules and patterns, see `.cursor/rules/researcher-architecture.mdc`

---

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
├─────────────────────────────────────────────────────────────────┤
│  ResearchWizard (3 Steps)                                        │
│  ├── Step 1: ResearchInput (Input + Intent & Options)          │
│  ├── Step 2: StepProgress (Progress/Polling)                   │
│  └── Step 3: StepResults (Tabbed Results Display)              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND HOOKS                              │
├─────────────────────────────────────────────────────────────────┤
│  useIntentResearch                                              │
│  ├── analyzeIntent() → /api/research/intent/analyze            │
│  ├── confirmIntent() → Updates local state                      │
│  └── executeResearch() → /api/research/intent/research        │
│                                                                  │
│  useResearchExecution                                            │
│  ├── executeIntentResearch() → Intent-driven flow              │
│  └── executeTraditionalResearch() → Fallback flow              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API ENDPOINTS                               │
├─────────────────────────────────────────────────────────────────┤
│  POST /api/research/intent/analyze                              │
│  └── UnifiedResearchAnalyzer.analyze()                         │
│                                                                  │
│  POST /api/research/intent/research                            │
│  ├── ResearchEngine.research()                                  │
│  └── IntentAwareAnalyzer.analyze()                             │
│                                                                  │
│  POST /api/research/execute (Traditional - Fallback)           │
│  POST /api/research/start (Traditional - Async)                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND SERVICES                              │
├─────────────────────────────────────────────────────────────────┤
│  UnifiedResearchAnalyzer                                         │
│  ├── Intent Inference                                           │
│  ├── Query Generation                                           │
│  └── Parameter Optimization (Exa/Tavily)                        │
│                                                                  │
│  ResearchEngine                                                  │
│  ├── Provider Selection (Exa → Tavily → Google)               │
│  ├── ExaService                                                 │
│  ├── TavilyService                                              │
│  └── GoogleSearchService                                        │
│                                                                  │
│  IntentAwareAnalyzer                                            │
│  └── Intent-Based Result Analysis                               │
│                                                                  │
│  ResearchPersonaService                                         │
│  └── Persona Generation/Retrieval                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow

### Intent-Driven Research Flow

```
1. User Input
   │
   ▼
2. Frontend: useIntentResearch.analyzeIntent()
   │
   ▼
3. API: POST /api/research/intent/analyze
   │
   ▼
4. Backend: UnifiedResearchAnalyzer.analyze()
   ├── Fetches Research Persona (if enabled)
   ├── Fetches Competitor Data (if enabled)
   ├── Single LLM Call:
   │   ├── Intent Inference
   │   ├── Query Generation (4-8 queries)
   │   └── Parameter Optimization (Exa/Tavily)
   └── Returns: Intent + Queries + Optimized Config
   │
   ▼
5. Frontend: IntentConfirmationPanel
   ├── Displays inferred intent (editable)
   ├── Shows suggested queries (selectable)
   └── Shows AI-optimized settings with justifications
   │
   ▼
6. User Confirms Intent
   │
   ▼
7. Frontend: useIntentResearch.executeResearch()
   │
   ▼
8. API: POST /api/research/intent/research
   │
   ▼
9. Backend: ResearchEngine.research()
   ├── Executes queries via Exa/Tavily/Google
   └── Returns raw results
   │
   ▼
10. Backend: IntentAwareAnalyzer.analyze()
    ├── Analyzes raw results based on intent
    ├── Extracts specific deliverables:
    │   ├── Statistics
    │   ├── Expert Quotes
    │   ├── Case Studies
    │   ├── Trends
    │   ├── Comparisons
    │   └── More...
    └── Returns: IntentDrivenResearchResult
    │
    ▼
11. Frontend: IntentResultsDisplay
    ├── Summary Tab
    ├── Deliverables Tab
    ├── Sources Tab
    └── Analysis Tab
```

---

## 📁 Component Structure

### Backend Structure

```
backend/services/research/
├── core/
│   ├── research_engine.py           # Main orchestrator
│   ├── research_context.py          # Unified input schema
│   └── parameter_optimizer.py     # DEPRECATED (use unified analyzer)
│
├── intent/
│   ├── unified_research_analyzer.py # ⭐ Unified AI analyzer (intent + queries + params)
│   ├── research_intent_inference.py # Legacy (use unified)
│   ├── intent_query_generator.py    # Legacy (use unified)
│   ├── intent_aware_analyzer.py     # Result analysis based on intent
│   └── intent_prompt_builder.py     # LLM prompt builders
│
├── research_persona_service.py      # Research persona generation/retrieval
├── research_persona_prompt_builder.py # Persona generation prompts
├── exa_service.py                   # Exa API integration
├── tavily_service.py                 # Tavily API integration
└── google_search_service.py          # Google/Gemini grounding
```

### Frontend Structure

```
frontend/src/components/Research/
├── ResearchWizard.tsx                # Main wizard orchestrator
├── steps/
│   ├── ResearchInput.tsx             # Step 1: Input + Intent & Options
│   ├── StepProgress.tsx              # Step 2: Progress/polling
│   ├── StepResults.tsx               # Step 3: Results display
│   ├── components/
│   │   ├── ResearchInputHeader.tsx   # Header with Advanced toggle
│   │   ├── ResearchInputContainer.tsx # Main input with Intent & Options button
│   │   ├── IntentConfirmationPanel.tsx # Intent display/edit panel
│   │   ├── IntentResultsDisplay.tsx # Tabbed results (Summary, Deliverables, Sources, Analysis)
│   │   ├── AdvancedOptionsSection.tsx # Exa/Tavily options
│   │   ├── ProviderChips.tsx         # Provider availability display
│   │   └── ... (other components)
│   ├── hooks/
│   │   ├── useResearchConfig.ts      # Config + persona loading
│   │   ├── useKeywordExpansion.ts    # Keyword expansion with persona
│   │   └── useResearchAngles.ts       # Research angles generation
│   └── utils/
│       ├── placeholders.ts           # Personalized placeholders
│       ├── industryDefaults.ts       # Industry-specific defaults
│       └── ...
└── hooks/
    ├── useResearchWizard.ts          # Wizard state management
    ├── useResearchExecution.ts       # Research execution orchestration
    └── useIntentResearch.ts          # Intent research flow
```

---

## 🔑 Key Components

### 1. UnifiedResearchAnalyzer

**Purpose**: Single AI call for intent + queries + params

**Location**: `backend/services/research/intent/unified_research_analyzer.py`

**Key Features**:
- Combines intent inference, query generation, and parameter optimization
- Reduces LLM calls from 2-3 to 1 (50% reduction)
- Provides justifications for all parameter decisions
- Uses research persona for context

**Input**:
- `user_input`: string
- `keywords`: List[str]
- `research_persona`: ResearchPersona (optional)
- `competitor_data`: List[Dict] (optional)
- `industry`: string (optional)
- `target_audience`: string (optional)
- `user_id`: string (required for subscription checks)

**Output**:
- `intent`: ResearchIntent
- `queries`: List[ResearchQuery] (4-8 queries)
- `exa_config`: Dict with settings + justifications
- `tavily_config`: Dict with settings + justifications
- `recommended_provider`: str
- `provider_justification`: str

### 2. IntentAwareAnalyzer

**Purpose**: Analyzes results based on user intent

**Location**: `backend/services/research/intent/intent_aware_analyzer.py`

**Key Features**:
- Extracts specific deliverables based on intent
- Structures results by deliverable type
- Provides credibility scores for sources
- Identifies gaps and follow-up queries

**Input**:
- `raw_results`: Dict (from Exa/Tavily/Google)
- `intent`: ResearchIntent
- `research_persona`: ResearchPersona (optional)
- `user_id`: string (required for subscription checks)

**Output**:
- `IntentDrivenResearchResult` with:
  - Statistics, quotes, case studies, trends
  - Comparisons, best practices, step-by-step guides
  - Pros/cons, definitions, examples, predictions
  - Executive summary, key takeaways, suggested outline
  - Sources with credibility scores

### 3. ResearchEngine

**Purpose**: Orchestrates provider calls

**Location**: `backend/services/research/core/research_engine.py`

**Key Features**:
- Provider priority: Exa → Tavily → Google
- Handles provider availability
- Manages async research tasks
- Integrates with research persona

**Provider Selection**:
1. **Exa** (Primary): Semantic understanding, academic papers, competitor research
2. **Tavily** (Secondary): Real-time news, trending topics, quick facts
3. **Google** (Fallback): Basic factual queries via Gemini grounding

### 4. ResearchPersonaService

**Purpose**: Generates and retrieves research persona

**Location**: `backend/services/research/research_persona_service.py`

**Key Features**:
- Generates persona from onboarding data (core persona, website analysis, competitor analysis)
- Caches persona (7-day TTL)
- Provides persona defaults for UI pre-filling

**Persona Sources**:
- Core persona (onboarding step 1)
- Website analysis (onboarding step 2)
- Competitor analysis (onboarding step 3)

---

## 🔌 API Endpoints

### Intent-Driven Endpoints

1. **POST `/api/research/intent/analyze`**
   - Analyzes user input to understand intent
   - Generates queries and optimizes parameters
   - Returns intent, queries, and optimized config

2. **POST `/api/research/intent/research`**
   - Executes research based on confirmed intent
   - Returns structured deliverables

### Traditional Endpoints (Fallback)

3. **POST `/api/research/execute`**
   - Synchronous research execution
   - Returns traditional research results

4. **POST `/api/research/start`**
   - Asynchronous research execution
   - Returns task_id for polling

5. **GET `/api/research/status/{task_id}`**
   - Polls async research status
   - Returns progress and results

### Configuration Endpoints

6. **GET `/api/research/config`**
   - Returns provider availability + persona defaults

7. **GET `/api/research/providers/status`**
   - Returns provider availability only

8. **GET `/api/research/persona-defaults`**
   - Returns persona defaults only

---

## 🎯 Key Patterns

### Pattern 1: Unified Analysis

**Always use UnifiedResearchAnalyzer** for new intent-driven research:

```python
from services.research.intent.unified_research_analyzer import UnifiedResearchAnalyzer

analyzer = UnifiedResearchAnalyzer()
result = await analyzer.analyze(
    user_input=user_input,
    keywords=keywords,
    research_persona=research_persona,
    user_id=user_id,  # Required
)
```

### Pattern 2: Intent-Aware Analysis

**Always analyze results based on intent**:

```python
from services.research.intent.intent_aware_analyzer import IntentAwareAnalyzer

analyzer = IntentAwareAnalyzer()
result = await analyzer.analyze(
    raw_results=raw_results,
    intent=research_intent,
    research_persona=research_persona,
    user_id=user_id,  # Required
)
```

### Pattern 3: Provider Selection

**Priority order**: Exa → Tavily → Google

```python
if provider_availability.exa_available:
    provider = "exa"
elif provider_availability.tavily_available:
    provider = "tavily"
else:
    provider = "google"
```

### Pattern 4: Persona Integration

**Always check for research persona**:

```python
from services.research.research_persona_service import ResearchPersonaService

persona_service = ResearchPersonaService(db)
research_persona = persona_service.get_or_generate(user_id)
```

### Pattern 5: Subscription Checks

**Always pass user_id to LLM calls**:

```python
result = llm_text_gen(
    prompt=prompt,
    json_struct=schema,
    user_id=user_id  # Required for subscription checks
)
```

---

## 🔄 Research Modes

### Intent-Driven Research (Current - Recommended)

**Flow**: Intent Analysis → Confirmation → Execution → Intent-Aware Analysis

**Benefits**:
- Understands user goals before searching
- Delivers exactly what users need
- Structured deliverables
- 50% reduction in LLM calls

**Use When**: User wants specific deliverables (statistics, quotes, case studies, etc.)

### Traditional Research (Fallback)

**Flow**: Direct Execution → Generic Analysis

**Benefits**:
- Faster for simple queries
- No intent analysis overhead

**Use When**: Simple factual queries or when intent analysis fails

---

## 📊 Data Models

### ResearchIntent

```python
class ResearchIntent:
    primary_question: str
    secondary_questions: List[str]
    purpose: ResearchPurpose  # learn, create_content, make_decision, etc.
    content_output: ContentOutput  # blog, podcast, video, etc.
    expected_deliverables: List[ExpectedDeliverable]
    depth: ResearchDepthLevel  # overview, detailed, expert
    focus_areas: List[str]
    perspective: Optional[str]
    time_sensitivity: str
    confidence: float
    confidence_reason: Optional[str]
    great_example: Optional[str]
    needs_clarification: bool
    clarifying_questions: List[str]
```

### ResearchQuery

```python
class ResearchQuery:
    query: str
    purpose: ExpectedDeliverable
    provider: str  # "exa" | "tavily"
    priority: int  # 1-5
    expected_results: str
    justification: Optional[str]
```

### IntentDrivenResearchResult

```python
class IntentDrivenResearchResult:
    primary_answer: str
    secondary_answers: Dict[str, str]
    statistics: List[StatisticWithCitation]
    expert_quotes: List[ExpertQuote]
    case_studies: List[CaseStudySummary]
    trends: List[TrendAnalysis]
    comparisons: List[ComparisonTable]
    best_practices: List[str]
    step_by_step: List[str]
    pros_cons: Optional[ProsCons]
    definitions: Dict[str, str]
    examples: List[str]
    predictions: List[str]
    executive_summary: str
    key_takeaways: List[str]
    suggested_outline: List[str]
    sources: List[SourceWithRelevance]
    confidence: float
    gaps_identified: List[str]
    follow_up_queries: List[str]
```

---

## 🎨 UI Components

### ResearchWizard

**Purpose**: Main wizard orchestrator

**Steps**:
1. **ResearchInput**: Input + Intent & Options button
2. **StepProgress**: Progress/polling for async research
3. **StepResults**: Tabbed results display

### IntentConfirmationPanel

**Purpose**: Shows inferred intent and allows editing

**Features**:
- Displays inferred intent (editable)
- Shows suggested queries (selectable)
- Displays AI-optimized settings with justifications
- Advanced options for manual override

### IntentResultsDisplay

**Purpose**: Tabbed results display

**Tabs**:
- **Summary**: AI-generated overview
- **Deliverables**: Extracted statistics, quotes, case studies, etc.
- **Sources**: Citations with credibility scores
- **Analysis**: Deep insights based on intent

---

## 🔐 Security & Subscription

### Authentication

All endpoints require JWT authentication via `get_current_user` dependency.

### Subscription Checks

All LLM calls must pass `user_id` for subscription and pre-flight validation:

```python
result = llm_text_gen(
    prompt=prompt,
    json_struct=schema,
    user_id=user_id  # Required
)
```

### Rate Limiting

- Subject to subscription tier limits
- Provider APIs (Exa/Tavily/Google) have their own rate limits

---

## 📈 Performance

### Intent Analysis

- **Typical Time**: 2-5 seconds
- **LLM Calls**: 1 (unified analyzer)
- **Caching**: Research persona cached (7-day TTL)

### Research Execution

- **Typical Time**: 10-30 seconds
- **Depends On**: Provider, query count, result count
- **Async Support**: Yes (via `/api/research/start`)

### Result Analysis

- **Typical Time**: 5-10 seconds
- **LLM Calls**: 1 (intent-aware analyzer)

---

## 🔗 Integration Points

### Blog Writer Integration

Research Engine can be imported by Blog Writer:

```python
from services.research.core.research_engine import ResearchEngine
from services.research.core.research_context import ResearchContext

context = ResearchContext(
    query=blog_topic,
    keywords=blog_keywords,
    goal=ResearchGoal.FACTUAL,
    depth=ResearchDepth.COMPREHENSIVE,
)

engine = ResearchEngine()
result = await engine.research(context, user_id=user_id)
```

### Frontend Integration

Research Wizard can be reused in other tools:

```tsx
import { ResearchWizard } from '@/components/Research/ResearchWizard';

<ResearchWizard
  onComplete={(results) => {
    // Use results in blog/video generation
  }}
  initialKeywords={blogTopic}
  initialIndustry={userIndustry}
/>
```

---

## 📚 Related Documentation

- **Architecture Rules**: `.cursor/rules/researcher-architecture.mdc` (Authoritative)
- **Intent-Driven Guide**: `INTENT_DRIVEN_RESEARCH_GUIDE.md`
- **API Reference**: `INTENT_RESEARCH_API_REFERENCE.md`
- **Documentation Review**: `DOCUMENTATION_REVIEW_AND_UPDATE_PLAN.md`

---

## ✅ Best Practices

1. **Always use UnifiedResearchAnalyzer** for new intent-driven research
2. **Always pass user_id** to all LLM calls
3. **Always use IntentAwareAnalyzer** for result analysis
4. **Check provider availability** before using providers
5. **Provide justifications** for all AI-driven settings
6. **Allow user overrides** in Advanced Options
7. **Never fallback to "General"** - always use persona defaults

---

**Status**: Authoritative Architecture Documentation - Single Source of Truth
