# Intent-Driven Research Guide

**Date**: 2025-01-29  
**Status**: Current Architecture Documentation

---

## 📋 Overview

Intent-driven research is the core innovation of the ALwrity Research Engine. Instead of generic keyword-based searches, the system **understands what users want to accomplish** before executing research, then delivers exactly what they need.

### Key Innovation

**Traditional Research**:
```
User Input → Search → Generic Results → User filters/analyzes
```

**Intent-Driven Research**:
```
User Input → AI Understands Intent → Targeted Queries → Intent-Aware Analysis → Structured Deliverables
```

---

## 🎯 Core Concepts

### 1. **Intent Inference**
Before searching, the AI analyzes user input to understand:
- **What question** needs answering
- **What purpose** (learn, create content, make decision, etc.)
- **What deliverables** are expected (statistics, quotes, case studies, etc.)
- **What depth** is needed (overview, detailed, expert)

### 2. **Unified Analysis**
A single AI call performs:
- Intent inference
- Query generation (4-8 targeted queries)
- Provider parameter optimization (Exa/Tavily settings with justifications)

### 3. **Intent-Aware Result Analysis**
Results are analyzed through the lens of user intent, extracting:
- Specific deliverables (statistics, quotes, case studies)
- Structured answers to user's questions
- Relevant sources with credibility scores
- Actionable insights

---

## 🔄 Research Flow

### Step 1: Intent Analysis

**User Action**: Enters keywords/topic and clicks "Intent & Options"

**What Happens**:
1. Frontend calls `/api/research/intent/analyze`
2. `UnifiedResearchAnalyzer` performs single AI call:
   - Infers research intent
   - Generates 4-8 targeted queries
   - Optimizes Exa/Tavily parameters with justifications
   - Recommends best provider
3. Returns `ResearchIntent`, `ResearchQuery[]`, and `OptimizedConfig`

**User Sees**:
- Inferred intent (editable)
- Suggested queries (selectable)
- AI-optimized provider settings with justifications
- Recommended provider

### Step 2: Intent Confirmation

**User Action**: Reviews and optionally edits intent, then confirms

**What Happens**:
- User can edit:
  - Primary question
  - Purpose
  - Expected deliverables
  - Depth level
  - Content output type
- User selects which queries to execute
- User can override AI-optimized settings in Advanced Options

### Step 3: Research Execution

**User Action**: Clicks "Research" button

**What Happens**:
1. Frontend calls `/api/research/intent/research`
2. Backend executes selected queries via Exa/Tavily/Google
3. `IntentAwareAnalyzer` analyzes raw results based on intent
4. Extracts specific deliverables:
   - Statistics with citations
   - Expert quotes
   - Case studies
   - Trends
   - Comparisons
   - Best practices
   - Step-by-step guides
   - Pros/cons
   - Definitions
   - Examples
   - Predictions

### Step 4: Results Display

**User Sees**: Tabbed results organized by deliverable type:
- **Summary**: AI-generated overview
- **Deliverables**: Extracted statistics, quotes, case studies, etc.
- **Sources**: Citations with credibility scores
- **Analysis**: Deep insights based on intent

---

## 🏗️ Architecture Components

### Backend Components

#### 1. UnifiedResearchAnalyzer
**Location**: `backend/services/research/intent/unified_research_analyzer.py`

**Purpose**: Single AI call for intent + queries + params

**Key Method**:
```python
async def analyze(
    user_input: str,
    keywords: Optional[List[str]] = None,
    research_persona: Optional[ResearchPersona] = None,
    competitor_data: Optional[List[Dict]] = None,
    industry: Optional[str] = None,
    target_audience: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Dict[str, Any]
```

**Returns**:
- `intent`: ResearchIntent object
- `queries`: List[ResearchQuery] (4-8 queries)
- `exa_config`: Dict with settings + justifications
- `tavily_config`: Dict with settings + justifications
- `recommended_provider`: str ("exa" | "tavily" | "google")
- `provider_justification`: str

**Benefits**:
- 50% reduction in LLM calls (from 2-3 calls to 1)
- Coherent reasoning across intent, queries, and params
- User-friendly justifications for all settings

#### 2. IntentAwareAnalyzer
**Location**: `backend/services/research/intent/intent_aware_analyzer.py`

**Purpose**: Analyzes raw results based on user intent

**Key Method**:
```python
async def analyze(
    raw_results: Dict[str, Any],
    intent: ResearchIntent,
    research_persona: Optional[ResearchPersona] = None,
    user_id: Optional[str] = None,
) -> IntentDrivenResearchResult
```

**Returns**: `IntentDrivenResearchResult` with:
- `primary_answer`: str
- `secondary_answers`: Dict[str, str]
- `statistics`: List[StatisticWithCitation]
- `expert_quotes`: List[ExpertQuote]
- `case_studies`: List[CaseStudySummary]
- `trends`: List[TrendAnalysis]
- `comparisons`: List[ComparisonTable]
- `best_practices`: List[str]
- `step_by_step`: List[str]
- `pros_cons`: ProsCons
- `definitions`: Dict[str, str]
- `examples`: List[str]
- `predictions`: List[str]
- `executive_summary`: str
- `key_takeaways`: List[str]
- `suggested_outline`: List[str]
- `sources`: List[SourceWithRelevance]
- `confidence`: float
- `gaps_identified`: List[str]
- `follow_up_queries`: List[str]

#### 3. Research Engine
**Location**: `backend/services/research/core/research_engine.py`

**Purpose**: Orchestrates provider calls (Exa → Tavily → Google)

**Provider Priority**:
1. **Exa** (Primary) - Semantic understanding, academic papers, competitor research
2. **Tavily** (Secondary) - Real-time news, trending topics, quick facts
3. **Google** (Fallback) - Basic factual queries via Gemini grounding

### Frontend Components

#### 1. ResearchWizard
**Location**: `frontend/src/components/Research/ResearchWizard.tsx`

**Purpose**: Main wizard orchestrator (3 steps)

**Steps**:
1. `ResearchInput` - Input + Intent & Options button
2. `StepProgress` - Progress/polling
3. `StepResults` - Results display

#### 2. ResearchInput
**Location**: `frontend/src/components/Research/steps/ResearchInput.tsx`

**Features**:
- Keyword/topic input
- "Intent & Options" button (enabled after 2+ words)
- Industry and target audience selection
- Advanced options toggle

#### 3. IntentConfirmationPanel
**Location**: `frontend/src/components/Research/steps/components/IntentConfirmationPanel.tsx`

**Purpose**: Shows inferred intent and allows editing

**Features**:
- Displays inferred intent (editable)
- Shows suggested queries (selectable)
- Displays AI-optimized provider settings with justifications
- Advanced options for manual override
- "Research" button to execute

#### 4. IntentResultsDisplay
**Location**: `frontend/src/components/Research/steps/components/IntentResultsDisplay.tsx`

**Purpose**: Tabbed results display

**Tabs**:
- **Summary**: AI-generated overview
- **Deliverables**: Extracted statistics, quotes, case studies, etc.
- **Sources**: Citations with credibility scores
- **Analysis**: Deep insights based on intent

#### 5. AdvancedOptionsSection
**Location**: `frontend/src/components/Research/steps/components/AdvancedOptionsSection.tsx`

**Purpose**: Shows AI-optimized Exa/Tavily settings with justifications

**Features**:
- Exa options (type, category, domains, date filters, etc.)
- Tavily options (topic, search depth, time range, etc.)
- Each setting shows AI justification in tooltip
- User can override any setting

### Frontend Hooks

#### 1. useIntentResearch
**Location**: `frontend/src/components/Research/hooks/useIntentResearch.ts`

**Purpose**: Manages intent-driven research flow

**Key Methods**:
- `analyzeIntent(userInput: string)` - Analyzes user input
- `confirmIntent(intent: ResearchIntent)` - Confirms/modifies intent
- `executeResearch(selectedQueries?: ResearchQuery[])` - Executes research
- `reset()` - Resets state

**State**:
- `userInput`: string
- `intent`: ResearchIntent | null
- `suggestedQueries`: ResearchQuery[]
- `selectedQueries`: ResearchQuery[]
- `isAnalyzing`: boolean
- `isResearching`: boolean
- `result`: IntentDrivenResearchResponse | null

#### 2. useResearchExecution
**Location**: `frontend/src/components/Research/hooks/useResearchExecution.ts`

**Purpose**: Handles research execution and polling

**Key Methods**:
- `executeIntentResearch(state, queries)` - Executes intent-driven research
- `executeTraditionalResearch(state)` - Executes traditional research (fallback)
- `pollStatus(taskId)` - Polls async research status

---

## 📡 API Endpoints

### 1. POST `/api/research/intent/analyze`

**Purpose**: Analyze user input to understand research intent

**Request**:
```typescript
{
  user_input: string;
  keywords?: string[];
  use_persona?: boolean; // Default: true
  use_competitor_data?: boolean; // Default: true
}
```

**Response**:
```typescript
{
  success: boolean;
  intent: ResearchIntent;
  analysis_summary: string;
  suggested_queries: ResearchQuery[];
  suggested_keywords: string[];
  suggested_angles: string[];
  confidence_reason?: string;
  great_example?: string;
  optimized_config: {
    provider: string;
    provider_justification: string;
    exa_type: string;
    exa_type_justification: string;
    exa_category?: string;
    exa_category_justification?: string;
    // ... more Exa settings with justifications
    tavily_topic: string;
    tavily_topic_justification: string;
    tavily_search_depth: string;
    tavily_search_depth_justification: string;
    // ... more Tavily settings with justifications
  };
  recommended_provider: string;
  error_message?: string;
}
```

**What It Does**:
1. Fetches research persona (if `use_persona: true`)
2. Fetches competitor data (if `use_competitor_data: true`)
3. Calls `UnifiedResearchAnalyzer.analyze()`
4. Returns intent, queries, and optimized config with justifications

### 2. POST `/api/research/intent/research`

**Purpose**: Execute research based on confirmed intent

**Request**:
```typescript
{
  user_input: string;
  confirmed_intent?: ResearchIntent; // If not provided, infers from user_input
  selected_queries?: ResearchQuery[]; // If not provided, generates from intent
  max_sources?: number; // Default: 10
  include_domains?: string[];
  exclude_domains?: string[];
  skip_inference?: boolean; // Skip intent inference if intent provided
}
```

**Response**:
```typescript
{
  success: boolean;
  primary_answer: string;
  secondary_answers: Dict<string, string>;
  statistics: StatisticWithCitation[];
  expert_quotes: ExpertQuote[];
  case_studies: CaseStudySummary[];
  trends: TrendAnalysis[];
  comparisons: ComparisonTable[];
  best_practices: string[];
  step_by_step: string[];
  pros_cons?: ProsCons;
  definitions: Dict<string, string>;
  examples: string[];
  predictions: string[];
  executive_summary: string;
  key_takeaways: string[];
  suggested_outline: string[];
  sources: SourceWithRelevance[];
  confidence: number;
  gaps_identified: string[];
  follow_up_queries: string[];
  intent?: ResearchIntent;
  error_message?: string;
}
```

**What It Does**:
1. Uses confirmed intent (or infers if not provided)
2. Uses selected queries (or generates if not provided)
3. Executes research via `ResearchEngine`
4. Analyzes results via `IntentAwareAnalyzer`
5. Returns structured deliverables

---

## 🎨 User Experience Flow

### Example: User wants to research "AI marketing tools"

#### Step 1: User Input
```
User enters: "AI marketing tools"
Clicks: "Intent & Options" button
```

#### Step 2: Intent Analysis
```
AI infers:
- Primary Question: "What are the best AI marketing tools available?"
- Purpose: "make_decision"
- Expected Deliverables: ["key_statistics", "case_studies", "comparisons", "best_practices"]
- Depth: "detailed"
- Content Output: "blog"

AI generates queries:
1. "best AI marketing tools 2024 comparison" (priority: 5)
2. "AI marketing tools statistics adoption rates" (priority: 4)
3. "AI marketing tools case studies ROI" (priority: 4)
4. "AI marketing automation platforms features" (priority: 3)

AI optimizes settings:
- Provider: Exa (semantic understanding needed)
- Exa Type: "neural" (for semantic matching)
- Exa Category: "company" (tool providers)
- Justification: "Neural search best for finding similar tools and comparisons"
```

#### Step 3: User Confirmation
```
User sees:
- Inferred intent (can edit)
- 4 suggested queries (can select/deselect)
- AI-optimized settings with justifications (can override)

User confirms and clicks "Research"
```

#### Step 4: Research Execution
```
Backend:
1. Executes 4 queries via Exa
2. Gets raw results (sources, content)
3. IntentAwareAnalyzer extracts:
   - Statistics: "78% of marketers use AI tools"
   - Case studies: "Company X increased ROI by 40%"
   - Comparisons: Tool comparison table
   - Best practices: "5 best practices for AI marketing"
```

#### Step 5: Results Display
```
User sees tabbed results:
- Summary: Overview of AI marketing tools landscape
- Deliverables: Statistics, quotes, case studies, comparisons
- Sources: Citations with credibility scores
- Analysis: Deep insights and recommendations
```

---

## 🔑 Key Patterns

### Pattern 1: Always Use UnifiedResearchAnalyzer

**✅ Correct**:
```python
from services.research.intent.unified_research_analyzer import UnifiedResearchAnalyzer

analyzer = UnifiedResearchAnalyzer()
result = await analyzer.analyze(
    user_input=user_input,
    keywords=keywords,
    research_persona=research_persona,
    user_id=user_id,
)
```

**❌ Incorrect** (Legacy - Don't Use):
```python
# Don't use separate intent inference + query generation
intent_service = ResearchIntentInference()
query_generator = IntentQueryGenerator()
# ... multiple LLM calls
```

### Pattern 2: Always Pass user_id

**✅ Correct**:
```python
result = llm_text_gen(
    prompt=prompt,
    json_struct=schema,
    user_id=user_id  # Required for subscription checks
)
```

**❌ Incorrect**:
```python
result = llm_text_gen(prompt=prompt, json_struct=schema)  # Missing user_id
```

### Pattern 3: Intent-Aware Result Analysis

**✅ Correct**:
```python
from services.research.intent.intent_aware_analyzer import IntentAwareAnalyzer

analyzer = IntentAwareAnalyzer()
result = await analyzer.analyze(
    raw_results=raw_results,
    intent=research_intent,
    research_persona=research_persona,
    user_id=user_id,
)
```

**❌ Incorrect** (Generic Analysis):
```python
# Don't do generic analysis - always use intent
summary = analyze_generic(raw_results)  # Wrong approach
```

---

## 🎯 Benefits

### 1. **50% Reduction in LLM Calls**
- Old: 2-3 separate calls (intent + queries + params)
- New: 1 unified call

### 2. **Better Results**
- Intent-aware analysis extracts exactly what users need
- Structured deliverables instead of generic summaries

### 3. **User-Friendly**
- AI justifications explain why settings were chosen
- Users can understand and override AI decisions

### 4. **Coherent Reasoning**
- Single AI call ensures intent, queries, and params are aligned
- No inconsistencies between intent and search strategy

---

## 🚀 Integration Examples

### Frontend: Using useIntentResearch Hook

```typescript
import { useIntentResearch } from '../hooks/useIntentResearch';

const MyComponent = () => {
  const {
    state,
    analyzeIntent,
    confirmIntent,
    executeResearch,
    isAnalyzing,
    isResearching,
    result,
  } = useIntentResearch({
    usePersona: true,
    useCompetitorData: true,
    maxSources: 10,
  });

  const handleAnalyze = async () => {
    await analyzeIntent("AI marketing tools");
  };

  const handleResearch = async () => {
    await executeResearch(state.selectedQueries);
  };

  return (
    <div>
      <button onClick={handleAnalyze} disabled={isAnalyzing}>
        {isAnalyzing ? 'Analyzing...' : 'Intent & Options'}
      </button>
      {state.intent && (
        <IntentConfirmationPanel
          intentAnalysis={state.intent}
          onConfirm={confirmIntent}
          onExecute={handleResearch}
        />
      )}
      {result && <IntentResultsDisplay result={result} />}
    </div>
  );
};
```

### Backend: Using UnifiedResearchAnalyzer

```python
from services.research.intent.unified_research_analyzer import UnifiedResearchAnalyzer

async def analyze_user_request(user_input: str, user_id: str):
    analyzer = UnifiedResearchAnalyzer()
    
    result = await analyzer.analyze(
        user_input=user_input,
        keywords=extract_keywords(user_input),
        research_persona=get_research_persona(user_id),
        user_id=user_id,
    )
    
    return {
        "intent": result["intent"],
        "queries": result["queries"],
        "exa_config": result["exa_config"],
        "tavily_config": result["tavily_config"],
        "recommended_provider": result["recommended_provider"],
    }
```

---

## 📚 Related Documentation

- **Architecture Rules**: `.cursor/rules/researcher-architecture.mdc` (Authoritative source)
- **API Reference**: `INTENT_RESEARCH_API_REFERENCE.md`
- **Architecture Overview**: `CURRENT_ARCHITECTURE_OVERVIEW.md`

---

## ✅ Best Practices

1. **Always use UnifiedResearchAnalyzer** for new intent-driven research
2. **Always pass user_id** to all LLM calls for subscription checks
3. **Always use IntentAwareAnalyzer** for result analysis
4. **Provide justifications** for all AI-driven settings
5. **Allow user overrides** in Advanced Options
6. **Check provider availability** before suggesting/using providers

---

**Status**: Current Architecture - Use this as reference for intent-driven research implementation.
