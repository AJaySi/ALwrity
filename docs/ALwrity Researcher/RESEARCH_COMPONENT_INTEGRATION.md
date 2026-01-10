# Research Component Integration Guide

**Date**: 2025-01-29  
**Status**: Updated for Intent-Driven Research Architecture

---

## 📋 Overview

The Research component is a standalone, intent-driven research system that can be integrated into any part of the application. This guide explains how to integrate and use the Research component.

**Key Features**:
- Intent-driven research (AI infers user goals)
- Standalone and reusable
- 3-step wizard interface
- Provider optimization (Exa → Tavily → Google)
- Research persona integration
- Google Trends integration

---

## 🏗️ Architecture

### Intent-Driven Research Flow

```
User Input
  ↓
UnifiedResearchAnalyzer (Single AI Call)
  ├── Intent Inference
  ├── Query Generation
  └── Parameter Optimization
  ↓
Research Execution (Exa → Tavily → Google)
  ↓
IntentAwareAnalyzer
  ├── Result Analysis
  └── Deliverable Extraction
  ↓
IntentDrivenResearchResult
```

### Component Structure

```
frontend/src/components/Research/
├── ResearchWizard.tsx                # Main wizard orchestrator
├── steps/
│   ├── ResearchInput.tsx             # Step 1: Input + Intent & Options
│   ├── StepProgress.tsx              # Step 2: Progress/polling
│   ├── StepResults.tsx               # Step 3: Results display
│   └── components/                   # Sub-components
├── hooks/
│   ├── useResearchWizard.ts         # Wizard state management
│   ├── useResearchExecution.ts      # API calls and polling
│   └── useIntentResearch.ts         # Intent-driven research flow
└── types/
    ├── research.types.ts            # Wizard state types
    └── intent.types.ts              # Intent-driven types
```

---

## 🔌 Integration

### Basic Integration

```typescript
import { ResearchWizard } from '../components/Research';

function MyComponent() {
  return (
    <ResearchWizard
      onComplete={(results) => {
        console.log('Research complete:', results);
        // Use results in your component
      }}
      onCancel={() => {
        console.log('Research cancelled');
      }}
    />
  );
}
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
    include_statistics: true,
    include_expert_quotes: true
  }}
  initialResults={savedResults} // For restoring saved projects
/>
```

### Blog Writer Integration

```typescript
import { BlogWriterAdapter } from '../components/Research/integrations/BlogWriterAdapter';

function BlogWriter() {
  const [researchData, setResearchData] = useState(null);

  return (
    <>
      <BlogWriterAdapter
        onResearchComplete={(data) => {
          setResearchData(data);
          // Use research data for blog generation
        }}
      />
      {/* Rest of blog writer UI */}
    </>
  );
}
```

---

## 🔄 Research Flow

### Step 1: Research Input

**User provides**:
- Keywords/topic
- Industry (optional, pre-filled from persona)
- Target audience (optional, pre-filled from persona)

**Component triggers**:
- Intent analysis when user clicks "Intent & Options"
- Shows `IntentConfirmationPanel` with AI-inferred intent

### Step 2: Intent Confirmation

**User reviews**:
- Primary research question
- Generated research queries
- Optimized provider settings
- Google Trends keywords (if applicable)

**User can**:
- Edit primary question
- Toggle deliverables
- Select/edit queries
- Review provider settings

**Component executes**:
- Research with selected queries
- Shows progress
- Auto-navigates to results

### Step 3: Results Display

**Component shows**:
- Summary tab (AI-generated overview)
- Deliverables tab (statistics, quotes, case studies, trends)
- Sources tab (citations with credibility scores)
- Analysis tab (deep insights)

---

## 🔌 API Integration

### Intent Analysis Endpoint

```typescript
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
    "primary_question": "What are the latest AI-powered marketing automation tools?",
    "research_goals": ["identify tools", "compare features", "analyze trends"],
    "deliverables": ["statistics", "expert_quotes", "case_studies"],
    "industry": "Technology",
    "target_audience": "Marketing professionals"
  },
  "queries": [
    {
      "query": "AI marketing automation platforms 2025",
      "provider": "exa",
      "justification": "Exa is best for finding company/product information"
    }
  ],
  "optimized_config": {
    "provider": "exa",
    "exa_category": "company",
    "provider_justification": "Exa excels at finding company and product information"
  },
  "trends_config": {
    "keywords": ["AI marketing", "marketing automation"],
    "enabled": true
  }
}
```

### Intent-Driven Research Endpoint

```typescript
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
    "summary": "Comprehensive overview...",
    "deliverables": {
      "statistics": [
        {
          "value": "85%",
          "description": "of marketers use AI tools",
          "citation": {...}
        }
      ],
      "expert_quotes": [...],
      "case_studies": [...],
      "trends": [...]
    },
    "sources": [...],
    "analysis": "Deep insights based on intent..."
  }
}
```

---

## 🎨 Customization

### Custom Styling

```typescript
import { ResearchWizard } from '../components/Research';
import { ThemeProvider, createTheme } from '@mui/material';

const customTheme = createTheme({
  // Your custom theme
});

<ThemeProvider theme={customTheme}>
  <ResearchWizard {...props} />
</ThemeProvider>
```

### Custom Hooks

```typescript
import { useResearchWizard, useResearchExecution } from '../components/Research';

function CustomResearchComponent() {
  const wizard = useResearchWizard();
  const execution = useResearchExecution();

  // Custom logic here
  return <div>Custom UI</div>;
}
```

---

## 🔧 Backend Services

### UnifiedResearchAnalyzer

**Location**: `backend/services/research/intent/unified_research_analyzer.py`

**Purpose**: Single AI call for intent inference, query generation, and parameter optimization

**Usage**:
```python
from backend.services.research.intent.unified_research_analyzer import UnifiedResearchAnalyzer

analyzer = UnifiedResearchAnalyzer()
result = await analyzer.analyze(
    user_input="AI marketing tools",
    industry="Technology",
    target_audience="Marketing professionals",
    user_id="user_123"
)
```

### IntentAwareAnalyzer

**Location**: `backend/services/research/intent/intent_aware_analyzer.py`

**Purpose**: Analyzes raw research results based on user intent

**Usage**:
```python
from backend.services.research.intent.intent_aware_analyzer import IntentAwareAnalyzer

analyzer = IntentAwareAnalyzer()
result = await analyzer.analyze(
    raw_results={...},
    intent=research_intent,
    user_id="user_123"
)
```

---

## 📝 Type Definitions

### Research Types

```typescript
// research.types.ts
export interface WizardState {
  currentStep: number;
  keywords: string[];
  industry: string;
  target_audience: string;
  research_mode: ResearchMode;
  config: ResearchConfig;
  results: BlogResearchResponse | null;
}

export interface ResearchWizardProps {
  onComplete?: (results: BlogResearchResponse) => void;
  onCancel?: () => void;
  initialKeywords?: string[];
  initialIndustry?: string;
  initialTargetAudience?: string;
  initialResearchMode?: ResearchMode;
  initialConfig?: ResearchConfig;
  initialResults?: BlogResearchResponse | null;
}
```

### Intent Types

```typescript
// intent.types.ts
export interface ResearchIntent {
  primary_question: string;
  research_goals: string[];
  deliverables: string[];
  industry: string;
  target_audience: string;
}

export interface ResearchQuery {
  query: string;
  provider: 'exa' | 'tavily' | 'google';
  justification?: string;
}

export interface IntentDrivenResearchResult {
  summary: string;
  deliverables: {
    statistics: StatisticWithCitation[];
    expert_quotes: ExpertQuote[];
    case_studies: CaseStudySummary[];
    trends: TrendAnalysis[];
  };
  sources: Source[];
  analysis: string;
}
```

---

## 🧪 Testing

### Standalone Testing

Navigate to `/research-test` for isolated testing:
- Test research flow
- Debug intent analysis
- Review results
- Export data

### Integration Testing

1. Import `ResearchWizard` in your component
2. Test with various initial data
3. Verify `onComplete` callback
4. Check error handling

---

## 🚀 Best Practices

### 1. Always Provide Initial Data When Available

```typescript
// Good: Pre-fill from user data
<ResearchWizard
  initialIndustry={userProfile.industry}
  initialTargetAudience={userProfile.targetAudience}
/>

// Avoid: Empty wizard when data is available
<ResearchWizard />
```

### 2. Handle Results Properly

```typescript
<ResearchWizard
  onComplete={(results) => {
    // Save results
    saveResearchResults(results);
    
    // Use in your component
    setResearchData(results);
    
    // Navigate if needed
    navigate('/blog-writer', { state: { research: results } });
  }}
/>
```

### 3. Use Research Persona

```typescript
// Research persona automatically pre-fills:
// - Industry
// - Target audience
// - Research preferences
// - Provider settings

// No additional code needed - it's automatic!
```

---

## 🔄 Migration from Old Architecture

### Old Architecture (Deprecated)
- 4-step wizard (StepKeyword → StepOptions → StepProgress → StepResults)
- Strategy pattern (Basic/Comprehensive/Targeted modes)
- Rule-based parameter optimization

### New Architecture
- 3-step wizard (ResearchInput → StepProgress → StepResults)
- Intent-driven (AI infers intent)
- Unified AI analyzer (single call)
- AI-optimized parameters

### Migration Steps
1. Replace old wizard components with `ResearchWizard`
2. Remove mode selection UI (handled by AI)
3. Update API calls to use intent-driven endpoints
4. Update result handling for new result structure

---

## 📚 Additional Resources

- **Architecture Rules**: `.cursor/rules/researcher-architecture.mdc`
- **Implementation Guide**: `RESEARCH_WIZARD_IMPLEMENTATION.md`
- **Intent-Driven Guide**: `INTENT_DRIVEN_RESEARCH_GUIDE.md`
- **Current Architecture**: `CURRENT_ARCHITECTURE_OVERVIEW.md`

---

## ✅ Implementation Status

- ✅ Intent-driven research implemented
- ✅ UnifiedResearchAnalyzer working
- ✅ IntentAwareAnalyzer working
- ✅ Google Trends integrated
- ✅ Research persona integrated
- ✅ My Projects feature (auto-save)
- ✅ Component refactoring complete

---

**Status**: Current and Accurate
