# Research Wizard Implementation Guide

**Date**: 2025-01-29  
**Status**: Updated for Intent-Driven Research Architecture

---

## 📋 Overview

The Research Wizard is a 3-step, intent-driven research system that uses AI to infer user intent, generate targeted queries, and optimize research parameters before executing research operations.

**Key Features**:
- Intent-driven research (AI infers what user wants to research)
- 3-step wizard flow
- Unified AI analyzer (single call for intent + queries + params)
- Provider optimization (Exa → Tavily → Google)
- Research persona integration
- Google Trends integration

---

## 🏗️ Architecture

### Current 3-Step Wizard Flow

```
Step 1: ResearchInput
  ├── User enters keywords/topic
  ├── Selects industry & target audience
  ├── Clicks "Intent & Options" button
  └── Shows IntentConfirmationPanel

Step 2: StepProgress (Auto-navigated)
  ├── Research execution in progress
  ├── Polling for completion
  └── Auto-navigates to Step 3 on completion

Step 3: StepResults
  ├── IntentResultsDisplay (tabbed view)
  │   ├── Summary tab
  │   ├── Deliverables tab
  │   ├── Sources tab
  │   └── Analysis tab
  └── Legacy results (fallback)
```

### Component Structure

```
frontend/src/components/Research/
├── ResearchWizard.tsx                # Main wizard orchestrator
├── steps/
│   ├── ResearchInput.tsx             # Step 1: Input + Intent & Options
│   ├── StepProgress.tsx              # Step 2: Progress/polling
│   ├── StepResults.tsx               # Step 3: Results display
│   └── components/
│       ├── ResearchInputHeader.tsx   # Header with Advanced toggle
│       ├── ResearchInputContainer.tsx # Main input with Intent & Options button
│       ├── IntentConfirmationPanel/  # Intent review/edit panel
│       │   ├── IntentConfirmationPanel.tsx
│       │   ├── IntentHeader.tsx
│       │   ├── PrimaryQuestionEditor.tsx
│       │   ├── IntentSummaryGrid.tsx
│       │   ├── DeliverablesSelector.tsx
│       │   ├── ResearchQueriesSection.tsx
│       │   ├── TrendsConfigSection.tsx
│       │   └── AdvancedProviderOptionsSection.tsx
│       ├── IntentResultsDisplay.tsx # Tabbed results (Summary, Deliverables, Sources, Analysis)
│       ├── AdvancedOptionsSection.tsx # Exa/Tavily options
│       ├── ProviderChips.tsx        # Provider availability display
│       └── ...
├── hooks/
│   ├── useResearchWizard.ts        # Wizard state management
│   ├── useResearchExecution.ts     # API calls and polling
│   └── useIntentResearch.ts         # Intent-driven research flow
└── types/
    ├── research.types.ts            # Wizard state types
    └── intent.types.ts              # Intent-driven types
```

---

## 🔄 Research Flow

### Step 1: ResearchInput

**Purpose**: User provides research topic and triggers intent analysis

**User Actions**:
1. Enter keywords/topic in textarea
2. Select industry (optional, pre-filled from persona)
3. Select target audience (optional, pre-filled from persona)
4. Click "Intent & Options" button (enabled after 2+ words)

**What Happens**:
```typescript
// User clicks "Intent & Options"
onClick={() => {
  execution.analyzeIntent(state.keywords, state.industry, state.target_audience);
}}
```

**Backend Call**:
- `POST /api/research/intent/analyze`
- `UnifiedResearchAnalyzer` analyzes input
- Returns: `ResearchIntent`, `ResearchQuery[]`, `OptimizedConfig`

**UI Update**:
- Shows `IntentConfirmationPanel` below input
- Displays inferred intent, queries, and optimized config

### Step 2: IntentConfirmationPanel

**Purpose**: User reviews and edits AI-inferred intent before execution

**Components**:
- **PrimaryQuestionEditor**: Editable primary research question
- **IntentSummaryGrid**: Quick summary (industry, audience, mode, deliverables)
- **DeliverablesSelector**: Toggle specific deliverables (statistics, quotes, case studies, etc.)
- **ResearchQueriesSection**: List of generated queries (selectable, editable)
- **TrendsConfigSection**: Google Trends keywords (if applicable)
- **AdvancedProviderOptionsSection**: Exa/Tavily options with AI justifications

**User Actions**:
1. Review inferred intent
2. Edit primary question (optional)
3. Toggle deliverables (optional)
4. Select/edit queries (optional)
5. Review provider settings (optional)
6. Click "Research" button

**What Happens**:
```typescript
// User clicks "Research"
onExecute={async (selectedQueries) => {
  const result = await execution.executeIntentResearch(state, selectedQueries);
  if (result?.success) {
    onUpdate({ currentStep: 3 }); // Navigate to results
  }
}}
```

**Backend Call**:
- `POST /api/research/intent/research`
- Executes selected queries via Exa/Tavily/Google
- `IntentAwareAnalyzer` analyzes results based on intent
- Returns: `IntentDrivenResearchResult`

**UI Update**:
- Shows `StepProgress` (auto-navigated)
- Polls for completion
- Auto-navigates to Step 3 on completion

### Step 3: StepResults

**Purpose**: Display research results in organized tabs

**Components**:
- **IntentResultsDisplay**: Tabbed view for intent-driven results
  - **Summary Tab**: AI-generated overview
  - **Deliverables Tab**: Extracted statistics, quotes, case studies, trends
  - **Sources Tab**: Citations with credibility scores
  - **Analysis Tab**: Deep insights based on intent
- **Legacy Results**: Fallback for non-intent-driven research

**User Actions**:
- Browse results in different tabs
- Export results (future)
- Start new research
- Save research project (auto-saved)

---

## 🔌 Backend Integration

### API Endpoints

#### 1. Intent Analysis
```python
POST /api/research/intent/analyze

Request:
{
  "keywords": "AI marketing tools",
  "industry": "Technology",
  "target_audience": "Marketing professionals"
}

Response:
{
  "success": true,
  "intent": {
    "primary_question": "...",
    "research_goals": [...],
    "deliverables": [...],
    "industry": "...",
    "target_audience": "..."
  },
  "queries": [
    {
      "query": "...",
      "provider": "exa",
      "justification": "..."
    }
  ],
  "optimized_config": {
    "provider": "exa",
    "exa_category": "company",
    "provider_justification": "..."
  },
  "trends_config": {
    "keywords": [...],
    "enabled": true
  }
}
```

#### 2. Intent-Driven Research
```python
POST /api/research/intent/research

Request:
{
  "intent": {...},
  "queries": [...],
  "config": {...}
}

Response:
{
  "success": true,
  "result": {
    "summary": "...",
    "deliverables": {
      "statistics": [...],
      "expert_quotes": [...],
      "case_studies": [...],
      "trends": [...]
    },
    "sources": [...],
    "analysis": "..."
  }
}
```

### Backend Services

#### UnifiedResearchAnalyzer
**Location**: `backend/services/research/intent/unified_research_analyzer.py`

**Purpose**: Single AI call for intent inference, query generation, and parameter optimization

**Key Method**:
```python
async def analyze(
    user_input: str,
    industry: Optional[str] = None,
    target_audience: Optional[str] = None,
    user_id: Optional[str] = None
) -> UnifiedResearchAnalysis:
    """
    Analyzes user input and returns:
    - Inferred research intent
    - Generated research queries
    - Optimized provider configuration
    - Google Trends keywords (if applicable)
    """
```

#### IntentAwareAnalyzer
**Location**: `backend/services/research/intent/intent_aware_analyzer.py`

**Purpose**: Analyzes raw research results based on user intent

**Key Method**:
```python
async def analyze(
    raw_results: Dict[str, Any],
    intent: ResearchIntent,
    user_id: Optional[str] = None
) -> IntentDrivenResearchResult:
    """
    Analyzes raw results and extracts:
    - Statistics with citations
    - Expert quotes
    - Case studies
    - Trends
    - Comparisons
    - Based on user's research intent
    """
```

---

## 🎨 Frontend Hooks

### useResearchWizard
**Location**: `frontend/src/components/Research/hooks/useResearchWizard.ts`

**Purpose**: Manages wizard state (step, keywords, industry, config, results)

**Key Methods**:
```typescript
const wizard = useResearchWizard(initialKeywords, ...);

wizard.state.currentStep;      // Current step (1, 2, or 3)
wizard.state.keywords;         // Research keywords
wizard.state.industry;         // Selected industry
wizard.state.config;           // Research configuration
wizard.state.results;          // Research results

wizard.updateState({ ... });  // Update state
wizard.nextStep();             // Navigate to next step
wizard.previousStep();         // Navigate to previous step
```

### useResearchExecution
**Location**: `frontend/src/components/Research/hooks/useResearchExecution.ts`

**Purpose**: Handles API calls and research execution

**Key Methods**:
```typescript
const execution = useResearchExecution();

execution.analyzeIntent(keywords, industry, audience);
execution.intentAnalysis;      // Result from intent analysis
execution.confirmIntent(intent); // Confirm/modify intent
execution.executeIntentResearch(state, queries); // Execute research
execution.isAnalyzingIntent;    // Loading state
execution.isExecuting;          // Execution state
```

### useIntentResearch
**Location**: `frontend/src/components/Research/hooks/useIntentResearch.ts`

**Purpose**: Manages intent-driven research flow

**Key Methods**:
```typescript
const intentResearch = useIntentResearch();

intentResearch.analyzeIntent(userInput);
intentResearch.confirmIntent(intent);
intentResearch.executeResearch(queries);
```

---

## 🔗 Integration Examples

### Standalone Usage
```typescript
import { ResearchWizard } from '../components/Research';

<ResearchWizard
  onComplete={(results) => {
    console.log('Research complete:', results);
  }}
  onCancel={() => {
    console.log('Research cancelled');
  }}
/>
```

### With Initial Data
```typescript
<ResearchWizard
  initialKeywords={['AI marketing tools']}
  initialIndustry="Technology"
  initialTargetAudience="Marketing professionals"
  initialResearchMode="comprehensive"
  initialConfig={{
    provider: 'exa',
    max_sources: 20,
    include_statistics: true
  }}
  initialResults={savedResults} // For restoring saved projects
/>
```

### Blog Writer Integration
```typescript
// In BlogWriter component
import { BlogWriterAdapter } from '../components/Research/integrations/BlogWriterAdapter';

<BlogWriterAdapter
  onResearchComplete={(researchData) => {
    // Use research data in blog generation
  }}
/>
```

---

## 🎯 Key Differences from Old Architecture

### Old Architecture (Deprecated)
- **4-Step Wizard**: StepKeyword → StepOptions → StepProgress → StepResults
- **Mode Selection**: User manually selects Basic/Comprehensive/Targeted
- **Strategy Pattern**: Different strategies for different modes
- **Rule-Based**: Rule-based parameter optimization

### Current Architecture
- **3-Step Wizard**: ResearchInput → StepProgress → StepResults
- **Intent-Driven**: AI infers intent, no manual mode selection
- **Unified Analyzer**: Single AI call for intent + queries + params
- **AI-Optimized**: AI-driven parameter optimization with justifications

---

## 📝 Notes

- **Backward Compatibility**: Legacy research endpoints still work for non-intent-driven research
- **Research Persona**: Persona data pre-fills industry, audience, and suggests presets
- **Google Trends**: Automatically included when relevant to research topic
- **Auto-Save**: Research projects are automatically saved to Asset Library upon completion

---

## ✅ Implementation Status

- ✅ 3-step wizard implemented
- ✅ Intent-driven research flow working
- ✅ UnifiedResearchAnalyzer integrated
- ✅ IntentAwareAnalyzer integrated
- ✅ Google Trends integrated
- ✅ Research persona integration
- ✅ My Projects feature (auto-save)
- ✅ Component refactoring complete

---

**Status**: Current and Accurate
