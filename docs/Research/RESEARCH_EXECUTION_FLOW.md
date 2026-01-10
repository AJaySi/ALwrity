# Research Execution Flow - Code Walkthrough

## Overview
This document traces the complete flow from when a user clicks "Start Research" to when they see the results on the UI.

---

## 1. User Clicks "Start Research" Button

### Location: `ActionButtons.tsx` (Line 104-119)

```typescript
<Button
  variant="contained"
  color="primary"
  startIcon={isExecuting ? <CircularProgress size={16} color="inherit" /> : <PlayIcon />}
  onClick={onExecute}  // ← This is the entry point
  disabled={isExecuting || !canExecute}
>
  {isExecuting ? 'Researching...' : 'Start Research'}
</Button>
```

**What happens:**
- Button shows loading spinner when `isExecuting` is true
- Calls `onExecute` callback
- Button is disabled if no queries are selected (`canExecute` must be true)

---

## 2. IntentConfirmationPanel Handles Execution

### Location: `IntentConfirmationPanel.tsx` (Line 106-122)

```typescript
const handleExecute = () => {
  const updatedIntent = { ...intent };
  // Pass wizard state to onConfirm for draft saving
  onConfirm(updatedIntent, wizardState);
  
  // Get selected queries (sorted by priority)
  const queriesToUse = Array.from(selectedQueries)
    .sort((a, b) => a - b)
    .map(idx => editedQueries[idx])
    .filter(q => q && q.query.trim().length > 0);
  
  // Store updated trends config
  if (editedTrendsConfig && intentAnalysis) {
    intentAnalysis.trends_config = editedTrendsConfig;
  }
  
  onExecute(queriesToUse);  // ← Passes queries to ResearchInput
};
```

**What happens:**
1. Confirms the intent (saves draft)
2. Extracts selected queries from the UI
3. Updates trends configuration if modified
4. Calls `onExecute` with the selected queries

---

## 3. ResearchInput Passes to Execution Hook

### Location: `ResearchInput.tsx` (Line 580-586)

```typescript
onExecute={async (selectedQueries) => {
  const result = await execution.executeIntentResearch(state, selectedQueries);
  if (result?.success) {
    // Skip to results step
    onUpdate({ currentStep: 3 });
  }
}}
```

**What happens:**
1. Calls `execution.executeIntentResearch()` with wizard state and selected queries
2. If successful, automatically navigates to Step 3 (Results)

---

## 4. Execution Hook Processes Research

### Location: `useResearchExecution.ts` (Line 284-378)

```typescript
const executeIntentResearch = useCallback(async (
  state: WizardState,
  selectedQueries?: ResearchQuery[]
): Promise<IntentDrivenResearchResponse | null> => {
  // 1. Ensure intent is available
  let intent = confirmedIntent;
  if (!intent) {
    const analysis = await analyzeIntent(state);
    if (!analysis?.success) {
      return null;
    }
    intent = analysis.intent;
  }

  // 2. Set loading state
  setIsExecuting(true);
  setError(null);

  try {
    // 3. Prepare queries (use provided or fall back to suggested)
    const queriesToUse = selectedQueries || 
      intentAnalysis?.suggested_queries?.slice(0, 5) || [];
    
    // 4. Make API call
    const response = await intentResearchApi.executeIntentResearch({
      user_input: state.keywords.join(' '),
      confirmed_intent: intent,
      selected_queries: queriesToUse.map(q => ({
        query: q.query,
        purpose: q.purpose,
        provider: q.provider,
        priority: q.priority,
        expected_results: q.expected_results,
      })),
      max_sources: state.config.max_sources || 10,
      include_domains: state.config.exa_include_domains || 
        state.config.tavily_include_domains || [],
      exclude_domains: state.config.exa_exclude_domains || 
        state.config.tavily_exclude_domains || [],
      trends_config: intentAnalysis?.trends_config,
      skip_inference: true,
    });

    // 5. Handle response
    if (!response.success) {
      setError(response.error_message || 'Research failed');
      setIsExecuting(false);
      return null;
    }

    // 6. Store results
    setIntentResult(response);
    
    // 7. Save draft to database
    autoSaveDraft(state, {
      intentAnalysis: intentAnalysis || undefined,
      confirmedIntent: intent,
      intentResult: response,
    }).catch(error => {
      console.warn('[useResearchExecution] Failed to save draft:', error);
    });
    
    // 8. Transform to legacy format for backward compatibility
    const legacyResult = {
      success: true,
      sources: response.sources.map(s => ({
        title: s.title,
        url: s.url,
        excerpt: s.excerpt ?? undefined,
        credibility_score: s.credibility_score,
      })),
      keyword_analysis: {
        primary_keywords: state.keywords,
        secondary: response.suggested_outline,
      },
      competitor_analysis: {},
      suggested_angles: response.key_takeaways,
      search_queries: [],
      intent_result: response,
    };
    
    setResult(legacyResult);
    setIsExecuting(false);
    
    // 9. Cache result
    researchCache.cacheResult(
      state.keywords,
      state.industry,
      state.targetAudience,
      legacyResult
    );
    
    return response;
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : 'Research failed';
    setError(errorMessage);
    setIsExecuting(false);
    return null;
  }
}, [confirmedIntent, intentAnalysis, analyzeIntent]);
```

**What happens:**
1. ✅ Validates intent is available
2. ✅ Sets `isExecuting = true` (shows loading state)
3. ✅ Prepares queries from selection or defaults
4. ✅ Makes API call to `/api/research/intent/research`
5. ✅ Handles success/error responses
6. ✅ Saves draft to database
7. ✅ Transforms result to legacy format
8. ✅ Caches result for future use
9. ✅ Sets `isExecuting = false` (hides loading state)

---

## 5. API Call to Backend

### Location: `intentResearchApi.ts` (Line 50-114)

```typescript
export const executeIntentResearch = async (
  request: IntentDrivenResearchRequest
): Promise<IntentDrivenResearchResponse> => {
  try {
    const response = await axios.post(
      '/api/research/intent/research',
      request,
      {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 300000, // 5 minutes
      }
    );
    return response.data;
  } catch (error: any) {
    // Error handling...
  }
};
```

**Backend Endpoint:** `POST /api/research/intent/research`

**Backend Handler:** `backend/api/research/handlers/intent.py` (Line 619-809)

**What backend does:**
1. Validates authentication
2. Gets research persona
3. Determines intent (from confirmed or infers)
4. Generates queries if not provided
5. Executes research using Research Engine
6. Runs Google Trends analysis in parallel (if enabled)
7. Analyzes results using IntentAwareAnalyzer
8. Merges trends data
9. Returns structured response

---

## 6. UI Updates During Execution

### Loading State Changes:

1. **Button State** (`ActionButtons.tsx`):
   - Text changes: "Start Research" → "Researching..."
   - Shows spinner icon
   - Button is disabled

2. **Execution Hook State** (`useResearchExecution.ts`):
   - `isExecuting = true` → triggers re-renders
   - `error = null` → clears any previous errors

3. **ResearchInput Component** (`ResearchInput.tsx`):
   - `execution.isExecuting` prop updates
   - IntentConfirmationPanel shows loading state

---

## 7. Navigation to Results Step

### Location: `ResearchInput.tsx` (Line 580-586)

```typescript
onExecute={async (selectedQueries) => {
  const result = await execution.executeIntentResearch(state, selectedQueries);
  if (result?.success) {
    // Skip to results step
    onUpdate({ currentStep: 3 });  // ← Navigates to Step 3
  }
}}
```

**What happens:**
- After successful research, automatically updates wizard state
- `currentStep` changes from `1` to `3`
- ResearchWizard re-renders and shows `StepResults` component

---

## 8. Results Display - StepResults Component

### Location: `StepResults.tsx` (Line 15-405)

### Initial Check (Line 19-35):

```typescript
// Check if we have intent-driven results
const intentResult: IntentDrivenResearchResponse | null = 
  execution?.intentResult || 
  (state.results as any)?.intent_result || 
  null;
  
// Determine if we have both types of results
const hasIntentResults = !!intentResult;
const hasTraditionalResults = !!state.results && !intentResult;
const hasAnyResults = hasIntentResults || hasTraditionalResults;

if (!hasAnyResults) {
  return (
    <div style={{ padding: '24px', textAlign: 'center' }}>
      <p style={{ color: '#666' }}>No results available</p>
    </div>
  );
}
```

### Header Section (Line 73-134):

**What user sees:**
- **Title:** "Research Results"
- **Action Buttons:**
  - ← Back (returns to previous step)
  - 📥 Export JSON (downloads results)
  - 🔄 Start New Research (resets to step 1)

### Tab Navigation (Line 144-210):

**Tabs available:**
1. **📋 Summary** - Executive summary and key takeaways
2. **📊 Deliverables** - Statistics, quotes, case studies, trends
3. **🔗 Sources** - All research sources with links
4. **📈 Analysis** - Detailed analysis and insights

**Tab badges show counts:**
- Deliverables tab: Total count of all deliverables
- Sources tab: Number of sources found

### Summary Tab Content (Line 217-232):

**What user sees:**

1. **Executive Summary** (if available):
   ```typescript
   {intentResult.executive_summary && (
     <div style={{
       backgroundColor: '#f0f9ff',
       border: '1px solid #bae6fd',
       borderRadius: '8px',
       padding: '16px',
     }}>
       <h4>Executive Summary</h4>
       <p>{intentResult.executive_summary}</p>
     </div>
   )}
   ```

2. **Direct Answer** (if available):
   ```typescript
   {intentResult.primary_answer && (
     <div style={{
       backgroundColor: '#f0fdf4',
       border: '1px solid #86efac',
     }}>
       <h4>Direct Answer</h4>
       <p>{intentResult.primary_answer}</p>
     </div>
   )}
   ```

3. **Key Takeaways** (if available):
   - List of bullet points
   - Styled as cards or list items

### Deliverables Tab Content (Line 250-280):

**What user sees:**

1. **Statistics** (`intentResult.statistics`):
   - Data points with labels
   - Formatted as cards or tables
   - May include charts/graphs

2. **Expert Quotes** (`intentResult.expert_quotes`):
   - Quote text
   - Source attribution
   - Credibility score

3. **Case Studies** (`intentResult.case_studies`):
   - Case study title
   - Description
   - Key findings
   - Source link

4. **Trends** (`intentResult.trends`):
   - Trend description
   - Google Trends data (if available)
   - Charts showing interest over time
   - Regional interest data

5. **Best Practices** (`intentResult.best_practices`):
   - List of actionable recommendations

6. **Comparisons** (`intentResult.comparisons`):
   - Side-by-side comparisons
   - Pros/cons tables

### Sources Tab Content (Line 290-320):

**What user sees:**

```typescript
{intentResult.sources.map((source, idx) => (
  <div key={idx} style={{
    border: '1px solid #e0e0e0',
    borderRadius: '8px',
    padding: '12px',
    marginBottom: '12px',
  }}>
    <h4>
      <a href={source.url} target="_blank" rel="noopener noreferrer">
        {source.title}
      </a>
    </h4>
    {source.excerpt && <p>{source.excerpt}</p>}
    <div>
      <span>Credibility: {source.credibility_score}</span>
      <span>Domain: {new URL(source.url).hostname}</span>
    </div>
  </div>
))}
```

**Each source shows:**
- Title (clickable link)
- Excerpt/preview
- Credibility score
- Domain name
- Published date (if available)

### Analysis Tab Content (Line 330-360):

**What user sees:**

1. **Confidence Score:**
   - Visual indicator (progress bar or badge)
   - Percentage or rating

2. **Gaps Identified:**
   - List of areas needing more research
   - Suggestions for follow-up

3. **Follow-up Queries:**
   - Suggested next research questions
   - Clickable to start new research

4. **Suggested Outline:**
   - Content structure based on research
   - Organized by sections

---

## 9. IntentResultsDisplay Component

### Location: `IntentResultsDisplay.tsx`

**Used when:** Intent-driven results are available

**Features:**
- Tabbed interface for different deliverable types
- Interactive charts for trends
- Expandable sections for detailed views
- Export functionality for trends data

**Tabs:**
1. **Summary** - Overview and primary answer
2. **Statistics** - Data points and metrics
3. **Expert Quotes** - Quotations with sources
4. **Case Studies** - Real-world examples
5. **Trends** - Trend analysis with charts
6. **Sources** - All research sources

---

## 10. State Management After Completion

### Draft Saving (Line 330-337):

```typescript
// Save draft with research results
autoSaveDraft(state, {
  intentAnalysis: intentAnalysis || undefined,
  confirmedIntent: intent,
  intentResult: response,
}).catch(error => {
  console.warn('[useResearchExecution] Failed to save draft:', error);
});
```

**What happens:**
- Saves complete research state to:
  1. **localStorage** (for browser persistence)
  2. **Database** (via `/api/research/projects/save`)

**Saved data includes:**
- Keywords
- Intent analysis
- Confirmed intent
- Research results
- Configuration
- Current step (3 = completed)

### Result Caching (Line 363-369):

```typescript
researchCache.cacheResult(
  state.keywords,
  state.industry,
  state.targetAudience,
  legacyResult
);
```

**Purpose:** Allows quick retrieval of results for similar queries

---

## 11. User Actions After Results

### Available Actions:

1. **← Back Button:**
   - Returns to Step 1 (Research Input)
   - Preserves all data

2. **📥 Export JSON:**
   - Downloads complete results as JSON file
   - Includes all deliverables, sources, and metadata

3. **🔄 Start New Research:**
   - Resets wizard to Step 1
   - Clears all results
   - Starts fresh research

4. **Tab Navigation:**
   - Switch between Summary, Deliverables, Sources, Analysis
   - Each tab shows different aspect of results

---

## 12. Error Handling

### If Research Fails:

1. **API Error:**
   - `setError(errorMessage)` in execution hook
   - Error displayed in UI
   - Button re-enabled for retry

2. **Network Error:**
   - Timeout after 5 minutes
   - User sees "Network error" message
   - Can retry the request

3. **Validation Error:**
   - If no queries selected: Warning alert shown
   - Button remains disabled until valid

---

## Summary Flow Diagram

```
User clicks "Start Research"
    ↓
ActionButtons.onExecute()
    ↓
IntentConfirmationPanel.handleExecute()
    ↓
ResearchInput.onExecute(selectedQueries)
    ↓
execution.executeIntentResearch(state, queries)
    ↓
[Loading State: isExecuting = true]
    ↓
intentResearchApi.executeIntentResearch(request)
    ↓
POST /api/research/intent/research
    ↓
Backend: Research Engine + Intent Analyzer
    ↓
Response: IntentDrivenResearchResponse
    ↓
[Save draft to database]
    ↓
[Cache result]
    ↓
[Loading State: isExecuting = false]
    ↓
onUpdate({ currentStep: 3 })
    ↓
StepResults Component Renders
    ↓
User sees:
  - Executive Summary
  - Direct Answer
  - Key Takeaways
  - Deliverables (Statistics, Quotes, Case Studies, Trends)
  - Sources (with links)
  - Analysis (Confidence, Gaps, Follow-ups)
```

---

## Key Files Reference

1. **Frontend Components:**
   - `ActionButtons.tsx` - Start Research button
   - `IntentConfirmationPanel.tsx` - Intent confirmation UI
   - `ResearchInput.tsx` - Step 1 component
   - `StepResults.tsx` - Step 3 results display
   - `IntentResultsDisplay.tsx` - Intent-driven results renderer

2. **Hooks:**
   - `useResearchExecution.ts` - Research execution logic
   - `useResearchWizard.ts` - Wizard state management

3. **API:**
   - `intentResearchApi.ts` - API client for research endpoints

4. **Backend:**
   - `handlers/intent.py` - Intent research endpoint handler
   - `services/research/intent/` - Intent analysis services
   - `services/research/core/` - Research engine

---

## UI States Summary

| State | Button Text | Button State | UI Feedback |
|-------|------------|--------------|-------------|
| **Ready** | "Start Research" | Enabled | Info alert: "Ready to start research!" |
| **No Queries** | "Start Research" | Disabled | Warning: "Please select at least one query" |
| **Executing** | "Researching..." | Disabled + Spinner | Loading indicator |
| **Success** | N/A (on Results page) | N/A | Results displayed in tabs |
| **Error** | "Start Research" | Enabled | Error message displayed |

---

This completes the code walkthrough from button click to results display! 🎉
