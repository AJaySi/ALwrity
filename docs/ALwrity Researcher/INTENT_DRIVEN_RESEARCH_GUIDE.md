# Intent-Driven Research Guide

**Date**: 2025-01-29  
**Status**: Comprehensive Guide to Intent-Driven Research

---

## 📋 Overview

Intent-driven research is a paradigm shift from manual research configuration to AI-inferred research goals. Instead of users selecting research modes and configuring providers manually, the AI analyzes user input and automatically determines:

1. **What** the user wants to research (intent inference)
2. **How** to research it (query generation)
3. **Where** to search (provider optimization)
4. **What** to extract (deliverable identification)

---

## 🎯 Core Concept

### Traditional Research (Old)
```
User Input: "AI marketing tools"
  ↓
User selects: Comprehensive mode
User configures: Exa provider, 20 sources
  ↓
Research executes with user's configuration
  ↓
Generic results
```

### Intent-Driven Research (Current)
```
User Input: "AI marketing tools"
  ↓
AI Analyzes:
  - Intent: "Find and compare AI marketing automation platforms"
  - Queries: ["AI marketing automation platforms 2025", ...]
  - Provider: Exa (best for company/product info)
  - Deliverables: statistics, expert quotes, case studies
  ↓
Research executes with AI-optimized configuration
  ↓
Intent-aware results (extracted deliverables)
```

---

## 🏗️ Architecture

### Unified Research Analyzer

**Location**: `backend/services/research/intent/unified_research_analyzer.py`

**Purpose**: Single AI call that performs:
1. Intent inference
2. Query generation
3. Parameter optimization

**Why Single Call?**
- Reduces LLM calls from 2-3 to 1
- Faster response time
- Lower costs
- More consistent results

**Input**:
```python
{
  "user_input": "AI marketing tools",
  "industry": "Technology",
  "target_audience": "Marketing professionals"
}
```

**Output**:
```python
{
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
      "justification": "Exa excels at finding company and product information"
    }
  ],
  "optimized_config": {
    "provider": "exa",
    "exa_category": "company",
    "exa_search_type": "neural",
    "provider_justification": "Exa is best for company/product research"
  },
  "trends_config": {
    "keywords": ["AI marketing", "marketing automation"],
    "enabled": true
  }
}
```

### Intent-Aware Analyzer

**Location**: `backend/services/research/intent/intent_aware_analyzer.py`

**Purpose**: Analyzes raw research results based on user intent to extract specific deliverables

**Why Intent-Aware?**
- Extracts only relevant information
- Structures results based on user goals
- Provides actionable insights
- Reduces information overload

**Input**:
```python
{
  "raw_results": {
    "sources": [...],
    "content": "..."
  },
  "intent": {
    "primary_question": "...",
    "deliverables": ["statistics", "expert_quotes", "case_studies"]
  }
}
```

**Output**:
```python
{
  "summary": "Comprehensive overview...",
  "deliverables": {
    "statistics": [
      {
        "value": "85%",
        "description": "of marketers use AI tools",
        "citation": {...}
      }
    ],
    "expert_quotes": [
      {
        "quote": "...",
        "author": "...",
        "source": {...}
      }
    ],
    "case_studies": [...],
    "trends": [...]
  },
  "sources": [...],
  "analysis": "Deep insights based on intent..."
}
```

---

## 🔄 Research Flow

### Step-by-Step Flow

```
1. User Input
   User enters: "AI marketing tools"
   Industry: "Technology"
   Target Audience: "Marketing professionals"
   ↓

2. Intent Analysis (UnifiedResearchAnalyzer)
   POST /api/research/intent/analyze
   ↓
   AI analyzes:
   - What user wants to research
   - What information they need
   - Best way to research it
   ↓
   Returns:
   - ResearchIntent
   - ResearchQuery[]
   - OptimizedConfig
   - TrendsConfig (if applicable)
   ↓

3. Intent Confirmation (Frontend)
   User reviews:
   - Primary question
   - Generated queries
   - Provider settings
   - Google Trends keywords
   ↓
   User can:
   - Edit primary question
   - Toggle deliverables
   - Select/edit queries
   - Review provider settings
   ↓

4. Research Execution
   POST /api/research/intent/research
   ↓
   Execute queries via:
   - Exa (priority 1)
   - Tavily (priority 2)
   - Google (priority 3)
   ↓
   Parallel execution:
   - Core research queries
   - Google Trends (if enabled)
   ↓

5. Intent-Aware Analysis (IntentAwareAnalyzer)
   Analyze raw results based on intent
   ↓
   Extract:
   - Statistics with citations
   - Expert quotes
   - Case studies
   - Trends
   - Comparisons
   ↓

6. Results Display
   Tabbed view:
   - Summary: AI-generated overview
   - Deliverables: Extracted statistics, quotes, etc.
   - Sources: Citations with credibility scores
   - Analysis: Deep insights
```

---

## 🔌 API Endpoints

### 1. Intent Analysis

**Endpoint**: `POST /api/research/intent/analyze`

**Request**:
```json
{
  "keywords": "AI marketing tools",
  "industry": "Technology",
  "target_audience": "Marketing professionals"
}
```

**Response**:
```json
{
  "success": true,
  "intent": {
    "primary_question": "What are the latest AI-powered marketing automation tools?",
    "research_goals": [
      "identify top AI marketing tools",
      "compare features and pricing",
      "analyze market trends"
    ],
    "deliverables": [
      "statistics",
      "expert_quotes",
      "case_studies",
      "trends"
    ],
    "industry": "Technology",
    "target_audience": "Marketing professionals"
  },
  "queries": [
    {
      "query": "AI marketing automation platforms 2025",
      "provider": "exa",
      "justification": "Exa excels at finding company and product information"
    },
    {
      "query": "best AI marketing tools comparison",
      "provider": "tavily",
      "justification": "Tavily is best for recent comparisons and reviews"
    }
  ],
  "optimized_config": {
    "provider": "exa",
    "exa_category": "company",
    "exa_search_type": "neural",
    "max_sources": 20,
    "include_statistics": true,
    "include_expert_quotes": true,
    "include_case_studies": true,
    "include_trends": true,
    "provider_justification": "Exa is best for company/product research"
  },
  "trends_config": {
    "keywords": ["AI marketing", "marketing automation", "AI tools"],
    "enabled": true
  }
}
```

### 2. Intent-Driven Research

**Endpoint**: `POST /api/research/intent/research`

**Request**:
```json
{
  "intent": {
    "primary_question": "...",
    "research_goals": [...],
    "deliverables": [...]
  },
  "queries": [
    {
      "query": "...",
      "provider": "exa"
    }
  ],
  "config": {
    "provider": "exa",
    "exa_category": "company",
    "max_sources": 20
  },
  "trends_config": {
    "keywords": [...],
    "enabled": true
  }
}
```

**Response**:
```json
{
  "success": true,
  "result": {
    "summary": "Comprehensive overview of AI marketing tools...",
    "deliverables": {
      "statistics": [
        {
          "value": "85%",
          "description": "of marketers use AI tools in their workflow",
          "citation": {
            "source": "Marketing AI Report 2025",
            "url": "https://...",
            "credibility_score": 0.9
          }
        }
      ],
      "expert_quotes": [
        {
          "quote": "AI marketing tools are transforming how we approach customer engagement...",
          "author": "John Doe",
          "title": "CMO at TechCorp",
          "source": {...}
        }
      ],
      "case_studies": [
        {
          "title": "How Company X Increased ROI by 200%",
          "summary": "...",
          "source": {...}
        }
      ],
      "trends": [
        {
          "trend": "AI personalization",
          "description": "...",
          "data": {...}
        }
      ]
    },
    "sources": [
      {
        "title": "...",
        "url": "...",
        "credibility_score": 0.9,
        "relevance_score": 0.95
      }
    ],
    "analysis": "Deep insights based on research intent..."
  }
}
```

---

## 🎨 Frontend Integration

### useIntentResearch Hook

**Location**: `frontend/src/components/Research/hooks/useIntentResearch.ts`

**Usage**:
```typescript
import { useIntentResearch } from '../hooks/useIntentResearch';

function ResearchComponent() {
  const intentResearch = useIntentResearch();

  // Analyze intent
  const handleAnalyze = async () => {
    await intentResearch.analyzeIntent(
      "AI marketing tools",
      "Technology",
      "Marketing professionals"
    );
  };

  // Confirm intent
  const handleConfirm = (intent: ResearchIntent) => {
    intentResearch.confirmIntent(intent);
  };

  // Execute research
  const handleExecute = async (queries: ResearchQuery[]) => {
    const result = await intentResearch.executeResearch(queries);
    if (result?.success) {
      // Handle results
    }
  };

  return (
    <div>
      {/* UI */}
    </div>
  );
}
```

### IntentConfirmationPanel Component

**Location**: `frontend/src/components/Research/steps/components/IntentConfirmationPanel/`

**Purpose**: Allows users to review and edit AI-inferred intent

**Features**:
- Editable primary question
- Toggle deliverables
- Select/edit queries
- Review provider settings
- Google Trends keywords display

**Usage**:
```typescript
<IntentConfirmationPanel
  isAnalyzing={execution.isAnalyzingIntent}
  intentAnalysis={execution.intentAnalysis}
  confirmedIntent={execution.confirmedIntent}
  onConfirm={execution.confirmIntent}
  onUpdateField={execution.updateIntentField}
  onExecute={async (selectedQueries) => {
    await execution.executeIntentResearch(state, selectedQueries);
  }}
  onDismiss={execution.clearIntent}
  isExecuting={execution.isExecuting}
  showAdvancedOptions={advanced}
  onAdvancedOptionsChange={setAdvanced}
  providerAvailability={providerAvailability}
  config={state.config}
  onConfigUpdate={handleConfigUpdate}
/>
```

---

## 🔧 Backend Implementation

### UnifiedResearchAnalyzer

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
    # Build unified prompt
    prompt = self._build_unified_prompt(
        user_input, industry, target_audience
    )
    
    # Single LLM call
    response = await llm_text_gen(
        prompt=prompt,
        user_id=user_id,
        response_format={"type": "json_object"}
    )
    
    # Parse response
    analysis = UnifiedResearchAnalysis.parse_raw(response)
    
    return analysis
```

**Prompt Structure**:
1. User input context
2. Current date/time context (for time-sensitive queries)
3. Intent inference instructions
4. Query generation rules
5. Parameter optimization guidelines
6. Google Trends keyword suggestions

### IntentAwareAnalyzer

**Key Method**:
```python
async def analyze(
    raw_results: Dict[str, Any],
    intent: ResearchIntent,
    user_id: Optional[str] = None
) -> IntentDrivenResearchResult:
    """
    Analyzes raw results based on user intent
    """
    # Build analysis prompt
    prompt = self._build_analysis_prompt(
        raw_results, intent
    )
    
    # LLM call
    response = await llm_text_gen(
        prompt=prompt,
        user_id=user_id,
        response_format={"type": "json_object"}
    )
    
    # Parse and structure results
    result = IntentDrivenResearchResult.parse_raw(response)
    
    return result
```

---

## 📊 Benefits

### For Users
- **Faster**: No manual configuration needed
- **Smarter**: AI optimizes for best results
- **Better Results**: Intent-aware extraction
- **Less Overwhelming**: Structured deliverables

### For Developers
- **Simpler**: Single API call instead of multiple
- **Consistent**: AI ensures consistent quality
- **Maintainable**: Less configuration logic
- **Extensible**: Easy to add new providers/features

### For Business
- **Lower Costs**: Fewer LLM calls
- **Better UX**: Users get results faster
- **Higher Quality**: AI-optimized research
- **Scalable**: Handles complex research needs

---

## 🎯 Best Practices

### 1. Always Use Intent Analysis First
```typescript
// Good: Analyze intent before research
const analysis = await analyzeIntent(keywords, industry, audience);
const result = await executeResearch(analysis.queries, analysis.config);

// Avoid: Skip intent analysis
const result = await executeResearch([keywords], defaultConfig);
```

### 2. Let Users Review Intent
```typescript
// Good: Show IntentConfirmationPanel
<IntentConfirmationPanel
  intentAnalysis={analysis}
  onConfirm={handleConfirm}
/>

// Avoid: Auto-execute without confirmation
await executeResearch(analysis.queries); // User can't review
```

### 3. Use Intent-Aware Results
```typescript
// Good: Use structured deliverables
result.deliverables.statistics.forEach(stat => {
  // Use structured data
});

// Avoid: Parse raw results manually
const stats = parseRawResults(result.raw_content); // Manual parsing
```

---

## 🔄 Migration Guide

### From Traditional Research

**Old Code**:
```typescript
// User selects mode
const mode = 'comprehensive';

// User configures provider
const config = {
  provider: 'exa',
  max_sources: 20
};

// Execute research
const result = await executeResearch(keywords, mode, config);
```

**New Code**:
```typescript
// Analyze intent
const analysis = await analyzeIntent(keywords, industry, audience);

// User reviews (optional)
// Execute with AI-optimized config
const result = await executeIntentResearch(
  analysis.intent,
  analysis.queries,
  analysis.optimized_config
);
```

---

## 📚 Additional Resources

- **Architecture Rules**: `.cursor/rules/researcher-architecture.mdc`
- **Implementation Guide**: `RESEARCH_WIZARD_IMPLEMENTATION.md`
- **Integration Guide**: `RESEARCH_COMPONENT_INTEGRATION.md`
- **Current Architecture**: `CURRENT_ARCHITECTURE_OVERVIEW.md`

---

## ✅ Implementation Status

- ✅ UnifiedResearchAnalyzer implemented
- ✅ IntentAwareAnalyzer implemented
- ✅ Intent-driven API endpoints working
- ✅ Frontend integration complete
- ✅ Google Trends integrated
- ✅ Research persona integrated

---

**Status**: Current and Comprehensive
