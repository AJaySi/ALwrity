# Google Trends Implementation Plan - Phase 1

**Date**: 2025-01-29  
**Status**: Implementation Plan - Ready to Start

---

## 📋 Design Decisions

### Question 1: Extend Unified Prompt or Separate?

**Decision**: ✅ **Extend UnifiedResearchAnalyzer** (Single AI Call)

**Rationale**:
- Maintains single LLM call pattern (50% reduction)
- Coherent reasoning across research queries + trends keywords
- Consistent with Exa/Tavily parameter optimization approach
- Trends keywords should align with research intent

**Implementation**:
- Add "PART 4: GOOGLE TRENDS KEYWORDS" to unified prompt
- AI suggests optimized keywords for trends analysis
- Include trends config in unified response schema

### Question 2: How to Present Trends Inputs?

**Decision**: ✅ **Show in IntentConfirmationPanel** alongside other inputs

**Display**:
- Show trends keywords (AI-suggested, user-editable)
- Show timeframe and geo settings (with justifications)
- Show what insights trends will uncover (preview)
- Allow user to enable/disable trends analysis

### Question 3: Parallel Execution?

**Decision**: ✅ **Execute in Parallel** with research

**Implementation**:
- Use `asyncio.gather()` to run Exa/Tavily/Google + Google Trends in parallel
- Merge trends data into research results
- Display in enhanced Trends tab

---

## 🏗️ Implementation Architecture

### Phase 1: Core Service (Week 1)

#### 1.1 Create Google Trends Service

**File**: `backend/services/research/trends/google_trends_service.py`

**Features**:
```python
class GoogleTrendsService:
    async def get_interest_over_time(
        keywords: List[str],
        timeframe: str = "today 12-m",
        geo: str = "US"
    ) -> Dict[str, Any]
    
    async def get_interest_by_region(
        keywords: List[str],
        geo: str = "US"
    ) -> Dict[str, Any]
    
    async def get_related_topics(
        keywords: List[str],
        timeframe: str = "today 12-m"
    ) -> Dict[str, List[Dict[str, Any]]]
    
    async def get_related_queries(
        keywords: List[str],
        timeframe: str = "today 12-m"
    ) -> Dict[str, List[Dict[str, Any]]]
    
    async def get_trending_searches(
        country: str = "united_states"
    ) -> List[str]
    
    async def analyze_trends(
        keywords: List[str],
        timeframe: str = "today 12-m",
        geo: str = "US"
    ) -> GoogleTrendsData
```

**Key Requirements**:
- ✅ Proper error handling with retry logic
- ✅ Rate limiting (1 request per second)
- ✅ Caching (24-hour TTL)
- ✅ Async support
- ✅ Data serialization (convert DataFrames to dicts)
- ✅ Subscription checks (pass user_id)

#### 1.2 Create Data Models

**File**: `backend/models/research_trends_models.py` (NEW)

```python
class GoogleTrendsData(BaseModel):
    """Structured Google Trends data."""
    interest_over_time: List[Dict[str, Any]]
    interest_by_region: List[Dict[str, Any]]
    related_topics: Dict[str, List[Dict[str, Any]]]  # {top: [...], rising: [...]}
    related_queries: Dict[str, List[Dict[str, Any]]]  # {top: [...], rising: [...]}
    trending_searches: Optional[List[str]] = None
    timeframe: str
    geo: str
    keywords: List[str]
    timestamp: datetime

class TrendsConfig(BaseModel):
    """Google Trends configuration with justifications."""
    enabled: bool
    keywords: List[str]  # AI-optimized keywords for trends
    keywords_justification: str
    timeframe: str  # "today 1-y", "today 12-m", etc.
    timeframe_justification: str
    geo: str  # Country code
    geo_justification: str
    expected_insights: List[str]  # What insights trends will uncover
```

---

### Phase 2: Extend UnifiedResearchAnalyzer (Week 1)

#### 2.1 Enhance Unified Prompt

**File**: `backend/services/research/intent/unified_research_analyzer.py`

**Add to Prompt**:

```python
### PART 4: GOOGLE TRENDS KEYWORDS (if trends in deliverables)
If "trends" is in expected_deliverables OR purpose is "explore_trends":
- Suggest 1-3 optimized keywords for Google Trends analysis
- These may differ from research queries (trends need broader, searchable terms)
- Consider: What keywords will show meaningful trends?
- Consider: What timeframe will show relevant trends? (1 year, 12 months, etc.)
- Consider: What geographic region is most relevant?
- Explain what insights trends will uncover for content generation
```

**Add to Output Schema**:

```json
{
    "trends_config": {
        "enabled": true,
        "keywords": ["AI marketing", "marketing automation"],
        "keywords_justification": "These keywords will show search interest trends over time",
        "timeframe": "today 12-m",
        "timeframe_justification": "12 months provides enough data to see trends without being too historical",
        "geo": "US",
        "geo_justification": "US market is most relevant for this topic",
        "expected_insights": [
            "Search interest trends over the past year",
            "Regional interest distribution",
            "Related topics and queries for content expansion",
            "Optimal publication timing based on interest peaks"
        ]
    }
}
```

#### 2.2 Update Schema Builder

**Add to `_build_unified_schema()`**:

```python
"trends_config": {
    "type": "object",
    "properties": {
        "enabled": {"type": "boolean"},
        "keywords": {"type": "array", "items": {"type": "string"}},
        "keywords_justification": {"type": "string"},
        "timeframe": {"type": "string"},
        "timeframe_justification": {"type": "string"},
        "geo": {"type": "string"},
        "geo_justification": {"type": "string"},
        "expected_insights": {"type": "array", "items": {"type": "string"}}
    }
}
```

#### 2.3 Update Response Parser

**Add to `_parse_unified_result()`**:

```python
return {
    "success": True,
    "intent": intent,
    "queries": queries,
    "enhanced_keywords": result.get("enhanced_keywords", []),
    "research_angles": result.get("research_angles", []),
    "recommended_provider": result.get("recommended_provider", "exa"),
    "provider_justification": result.get("provider_justification", ""),
    "exa_config": result.get("exa_config", {}),
    "tavily_config": result.get("tavily_config", {}),
    "trends_config": result.get("trends_config", {}),  # NEW
    "analysis_summary": intent_data.get("analysis_summary", ""),
}
```

---

### Phase 3: Parallel Execution Integration (Week 1-2)

#### 3.1 Enhance IntentAwareAnalyzer

**File**: `backend/services/research/intent/intent_aware_analyzer.py`

**Add Method**:

```python
async def analyze_with_trends(
    self,
    raw_results: Dict[str, Any],
    intent: ResearchIntent,
    trends_config: Optional[Dict[str, Any]] = None,
    research_persona: Optional[ResearchPersona] = None,
    user_id: Optional[str] = None,
) -> IntentDrivenResearchResult:
    """
    Analyze results with Google Trends data in parallel.
    """
    # Run analysis and trends in parallel
    analysis_task = asyncio.create_task(
        self.analyze(raw_results, intent, research_persona, user_id)
    )
    
    trends_task = None
    if trends_config and trends_config.get("enabled"):
        from services.research.trends.google_trends_service import GoogleTrendsService
        trends_service = GoogleTrendsService()
        trends_task = asyncio.create_task(
            trends_service.analyze_trends(
                keywords=trends_config.get("keywords", []),
                timeframe=trends_config.get("timeframe", "today 12-m"),
                geo=trends_config.get("geo", "US"),
                user_id=user_id
            )
        )
    
    # Wait for both
    analyzed_result = await analysis_task
    trends_data = await trends_task if trends_task else None
    
    # Merge trends data into result
    if trends_data:
        analyzed_result = self._merge_trends_data(analyzed_result, trends_data)
    
    return analyzed_result
```

#### 3.2 Enhance Research Execution

**File**: `backend/api/research/router.py` (intent/research endpoint)

**Modify**:

```python
# Execute research and trends in parallel
research_task = asyncio.create_task(engine.research(context))
trends_task = None

if trends_config and trends_config.get("enabled"):
    from services.research.trends.google_trends_service import GoogleTrendsService
    trends_service = GoogleTrendsService()
    trends_task = asyncio.create_task(
        trends_service.analyze_trends(
            keywords=trends_config.get("keywords", []),
            timeframe=trends_config.get("timeframe", "today 12-m"),
            geo=trends_config.get("geo", "US"),
            user_id=user_id
        )
    )

# Wait for both
raw_result = await research_task
trends_data = await trends_task if trends_task else None

# Analyze results with trends
analyzer = IntentAwareAnalyzer()
analyzed_result = await analyzer.analyze_with_trends(
    raw_results={
        "content": raw_result.raw_content or "",
        "sources": raw_result.sources,
        "grounding_metadata": raw_result.grounding_metadata,
    },
    intent=intent,
    trends_config=trends_config,
    research_persona=research_persona,
    user_id=user_id,
)
```

---

### Phase 4: Frontend Integration (Week 2)

#### 4.1 Enhance IntentConfirmationPanel

**File**: `frontend/src/components/Research/steps/components/IntentConfirmationPanel.tsx`

**Add Trends Section**:

```tsx
{intentAnalysis?.trends_config?.enabled && (
  <Accordion>
    <AccordionSummary>
      <Box display="flex" alignItems="center" gap={1}>
        <TrendIcon />
        <Typography>Google Trends Analysis</Typography>
        <Chip label="Auto-enabled" size="small" color="success" />
      </Box>
    </AccordionSummary>
    <AccordionDetails>
      {/* Trends Keywords */}
      <TextField
        label="Trends Keywords"
        value={trendsConfig.keywords.join(", ")}
        onChange={(e) => updateTrendsKeywords(e.target.value.split(", "))}
        helperText={intentAnalysis.trends_config.keywords_justification}
        fullWidth
        margin="normal"
      />
      
      {/* Expected Insights Preview */}
      <Box mt={2}>
        <Typography variant="subtitle2" gutterBottom>
          What Trends Will Uncover:
        </Typography>
        <List dense>
          {intentAnalysis.trends_config.expected_insights.map((insight, idx) => (
            <ListItem key={idx}>
              <ListItemIcon>
                <CheckIcon color="success" fontSize="small" />
              </ListItemIcon>
              <ListItemText primary={insight} />
            </ListItem>
          ))}
        </List>
      </Box>
      
      {/* Settings with Justifications */}
      <Box mt={2}>
        <Typography variant="caption" color="text.secondary">
          Timeframe: {intentAnalysis.trends_config.timeframe}
          <Tooltip title={intentAnalysis.trends_config.timeframe_justification}>
            <InfoIcon fontSize="small" sx={{ ml: 0.5 }} />
          </Tooltip>
        </Typography>
        <Typography variant="caption" color="text.secondary" display="block">
          Region: {intentAnalysis.trends_config.geo}
          <Tooltip title={intentAnalysis.trends_config.geo_justification}>
            <InfoIcon fontSize="small" sx={{ ml: 0.5 }} />
          </Tooltip>
        </Typography>
      </Box>
    </AccordionDetails>
  </Accordion>
)}
```

#### 4.2 Enhance IntentResultsDisplay

**File**: `frontend/src/components/Research/steps/components/IntentResultsDisplay.tsx`

**Enhance Trends Tab**:

```tsx
{currentTab === 'trends' && (
  <Box>
    {/* Google Trends Data */}
    {result.google_trends_data && (
      <>
        {/* Interest Over Time Chart */}
        <Box mb={3}>
          <Typography variant="h6" gutterBottom>
            Interest Over Time
          </Typography>
          <LineChart data={result.google_trends_data.interest_over_time} />
        </Box>
        
        {/* Interest by Region */}
        <Box mb={3}>
          <Typography variant="h6" gutterBottom>
            Interest by Region
          </Typography>
          <RegionTable data={result.google_trends_data.interest_by_region} />
        </Box>
        
        {/* Related Topics */}
        <Box mb={3}>
          <Typography variant="h6" gutterBottom>
            Related Topics
          </Typography>
          <Tabs>
            <Tab label="Top" />
            <Tab label="Rising" />
          </Tabs>
          <TopicsList data={result.google_trends_data.related_topics} />
        </Box>
        
        {/* Related Queries */}
        <Box mb={3}>
          <Typography variant="h6" gutterBottom>
            Related Queries
          </Typography>
          <Tabs>
            <Tab label="Top" />
            <Tab label="Rising" />
          </Tabs>
          <QueriesList data={result.google_trends_data.related_queries} />
        </Box>
      </>
    )}
    
    {/* AI-Extracted Trends (existing) */}
    {result.trends.length > 0 && (
      <Box>
        <Typography variant="h6" gutterBottom>
          AI-Extracted Trends
        </Typography>
        <TrendsList trends={result.trends} />
      </Box>
    )}
  </Box>
)}
```

---

## 📊 Data Flow

```
User Input → Intent Analysis
     │
     ▼
UnifiedResearchAnalyzer
     ├── Infers Intent
     ├── Generates Research Queries
     ├── Optimizes Exa/Tavily Params
     └── Suggests Trends Keywords ← NEW
     │
     ▼
IntentConfirmationPanel
     ├── Shows Intent (editable)
     ├── Shows Research Queries
     ├── Shows Exa/Tavily Settings
     └── Shows Trends Config ← NEW
          ├── Trends Keywords (editable)
          ├── Timeframe & Geo (with justifications)
          └── Expected Insights Preview
     │
     ▼
User Clicks "Research"
     │
     ▼
Parallel Execution (asyncio.gather)
     ├── Research Task (Exa/Tavily/Google)
     └── Trends Task (Google Trends) ← NEW
     │
     ▼
IntentAwareAnalyzer
     ├── Analyzes Research Results
     └── Merges Trends Data ← NEW
     │
     ▼
IntentResultsDisplay
     └── Enhanced Trends Tab ← NEW
          ├── Interest Over Time Chart
          ├── Interest by Region
          ├── Related Topics/Queries
          └── AI-Extracted Trends
```

---

## 🔧 Implementation Details

### 1. Google Trends Service Structure

```python
# backend/services/research/trends/google_trends_service.py

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from pytrends.request import TrendReq
from loguru import logger
import pandas as pd

class GoogleTrendsService:
    def __init__(self):
        self.cache = {}  # Simple in-memory cache (replace with Redis in production)
        self.rate_limiter = RateLimiter(max_calls=1, period=1.0)  # 1 req/sec
    
    async def analyze_trends(
        self,
        keywords: List[str],
        timeframe: str = "today 12-m",
        geo: str = "US",
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive trends analysis.
        Returns all trends data in one call.
        """
        # Check cache first
        cache_key = f"trends:{':'.join(keywords)}:{timeframe}:{geo}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Rate limit
        await self.rate_limiter.acquire()
        
        try:
            # Initialize pytrends
            pytrends = TrendReq(hl='en-US', tz=360)
            pytrends.build_payload(keywords, timeframe=timeframe, geo=geo)
            
            # Fetch all data in parallel (pytrends methods are sync, so we'll use asyncio.to_thread)
            interest_over_time_task = asyncio.to_thread(
                lambda: self._format_interest_over_time(pytrends.interest_over_time())
            )
            interest_by_region_task = asyncio.to_thread(
                lambda: self._format_interest_by_region(pytrends.interest_by_region())
            )
            related_topics_task = asyncio.to_thread(
                lambda: self._format_related_topics(pytrends.related_topics())
            )
            related_queries_task = asyncio.to_thread(
                lambda: self._format_related_queries(pytrends.related_queries())
            )
            
            # Wait for all
            interest_over_time, interest_by_region, related_topics, related_queries = await asyncio.gather(
                interest_over_time_task,
                interest_by_region_task,
                related_topics_task,
                related_queries_task
            )
            
            result = {
                "interest_over_time": interest_over_time,
                "interest_by_region": interest_by_region,
                "related_topics": related_topics,
                "related_queries": related_queries,
                "timeframe": timeframe,
                "geo": geo,
                "keywords": keywords,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Cache for 24 hours
            self.cache[cache_key] = result
            asyncio.create_task(self._expire_cache(cache_key, 24 * 3600))
            
            return result
            
        except Exception as e:
            logger.error(f"Google Trends analysis failed: {e}")
            # Return partial data if available
            return self._create_fallback_response(keywords, timeframe, geo)
    
    def _format_interest_over_time(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Convert DataFrame to serializable format."""
        if df.empty:
            return []
        return df.reset_index().to_dict('records')
    
    def _format_interest_by_region(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Convert DataFrame to serializable format."""
        if df.empty:
            return []
        return df.reset_index().to_dict('records')
    
    def _format_related_topics(self, data: Dict) -> Dict[str, List[Dict[str, Any]]]:
        """Format related topics."""
        result = {"top": [], "rising": []}
        for keyword, topics in data.items():
            if isinstance(topics, dict):
                if "top" in topics and not topics["top"].empty:
                    result["top"].extend(topics["top"].to_dict('records'))
                if "rising" in topics and not topics["rising"].empty:
                    result["rising"].extend(topics["rising"].to_dict('records'))
        return result
    
    def _format_related_queries(self, data: Dict) -> Dict[str, List[Dict[str, Any]]]:
        """Format related queries."""
        result = {"top": [], "rising": []}
        for keyword, queries in data.items():
            if isinstance(queries, dict):
                if "top" in queries and not queries["top"].empty:
                    result["top"].extend(queries["top"].to_dict('records'))
                if "rising" in queries and not queries["rising"].empty:
                    result["rising"].extend(queries["rising"].to_dict('records'))
        return result
```

### 2. Rate Limiter

```python
# backend/services/research/trends/rate_limiter.py

import asyncio
from time import time
from collections import deque

class RateLimiter:
    def __init__(self, max_calls: int, period: float):
        self.max_calls = max_calls
        self.period = period
        self.calls = deque()
    
    async def acquire(self):
        now = time()
        # Remove old calls
        while self.calls and self.calls[0] < now - self.period:
            self.calls.popleft()
        
        # Wait if at limit
        if len(self.calls) >= self.max_calls:
            sleep_time = self.period - (now - self.calls[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
            return await self.acquire()
        
        self.calls.append(time())
```

### 3. Enhanced TrendAnalysis Model

**File**: `backend/models/research_intent_models.py`

**Update**:

```python
class TrendAnalysis(BaseModel):
    """Enhanced trend analysis with Google Trends data."""
    trend: str
    direction: str
    evidence: List[str]
    impact: Optional[str]
    timeline: Optional[str]
    sources: List[str]
    
    # Google Trends specific (optional)
    google_trends_data: Optional[Dict[str, Any]] = None
    interest_score: Optional[float] = None  # 0-100 from Google Trends
    regional_interest: Optional[Dict[str, float]] = None
    related_topics: Optional[List[str]] = None
    related_queries: Optional[List[str]] = None
```

---

## 🎯 User Experience Flow

### Step 1: Intent Analysis

**User enters**: "AI marketing tools for small businesses"

**UnifiedResearchAnalyzer returns**:
```json
{
  "intent": {
    "purpose": "make_decision",
    "expected_deliverables": ["comparisons", "trends", "statistics"]
  },
  "trends_config": {
    "enabled": true,
    "keywords": ["AI marketing", "marketing automation"],
    "keywords_justification": "These keywords will show search interest trends and help identify optimal publication timing",
    "timeframe": "today 12-m",
    "timeframe_justification": "12 months provides enough data to see trends without being too historical",
    "geo": "US",
    "geo_justification": "US market is most relevant for small business marketing tools",
    "expected_insights": [
      "Search interest trends over the past year",
      "Regional interest distribution (which states/countries show highest interest)",
      "Related topics for content expansion (e.g., 'email marketing automation', 'social media scheduling')",
      "Related queries for FAQ sections (e.g., 'best AI marketing tools for startups')",
      "Optimal publication timing based on interest peaks"
    ]
  }
}
```

### Step 2: IntentConfirmationPanel

**User sees**:
- Intent: make_decision
- Deliverables: [comparisons, trends, statistics]
- Research Queries: [...]
- **Google Trends Analysis** (accordion)
  - Keywords: "AI marketing, marketing automation" (editable)
  - Justification: "These keywords will show search interest trends..."
  - **Expected Insights**:
    - ✅ Search interest trends over the past year
    - ✅ Regional interest distribution
    - ✅ Related topics for content expansion
    - ✅ Related queries for FAQ sections
    - ✅ Optimal publication timing
  - Timeframe: 12 months (with justification tooltip)
  - Region: US (with justification tooltip)

### Step 3: Research Execution

**User clicks "Research"**:
- Research task starts (Exa/Tavily/Google)
- Trends task starts in parallel (Google Trends)
- Both run concurrently

### Step 4: Results Display

**Trends Tab shows**:
- **Interest Over Time** (Line chart)
- **Interest by Region** (Table/Map)
- **Related Topics** (Top & Rising tabs)
- **Related Queries** (Top & Rising tabs)
- **AI-Extracted Trends** (from research results)

---

## ✅ Implementation Checklist

### Backend

- [ ] Create `backend/services/research/trends/google_trends_service.py`
- [ ] Create `backend/services/research/trends/rate_limiter.py`
- [ ] Create `backend/models/research_trends_models.py`
- [ ] Extend `UnifiedResearchAnalyzer._build_unified_prompt()` with trends section
- [ ] Extend `UnifiedResearchAnalyzer._build_unified_schema()` with trends_config
- [ ] Extend `UnifiedResearchAnalyzer._parse_unified_result()` to include trends_config
- [ ] Add `analyze_with_trends()` method to `IntentAwareAnalyzer`
- [ ] Update `/api/research/intent/research` endpoint for parallel execution
- [ ] Add caching for trends data (24-hour TTL)
- [ ] Add error handling and retry logic
- [ ] Add subscription checks (user_id)

### Frontend

- [ ] Update `AnalyzeIntentResponse` type to include `trends_config`
- [ ] Add trends section to `IntentConfirmationPanel`
- [ ] Add trends keywords editing
- [ ] Add expected insights preview
- [ ] Enhance `IntentResultsDisplay` Trends tab
- [ ] Add interest over time chart component
- [ ] Add interest by region table/map component
- [ ] Add related topics/queries display
- [ ] Update `useIntentResearch` hook to handle trends_config

### Testing

- [ ] Test trends service with various keywords
- [ ] Test rate limiting
- [ ] Test caching
- [ ] Test parallel execution
- [ ] Test error handling
- [ ] Test frontend display

---

## 📝 Next Steps

1. **Create Google Trends Service** (Start here)
   - Implement `GoogleTrendsService` class
   - Add rate limiting
   - Add caching
   - Test with sample keywords

2. **Extend UnifiedResearchAnalyzer**
   - Add trends section to prompt
   - Add trends_config to schema
   - Test intent analysis with trends

3. **Integrate Parallel Execution**
   - Update research endpoint
   - Test parallel execution
   - Verify data merging

4. **Frontend Integration**
   - Add trends section to IntentConfirmationPanel
   - Enhance Trends tab
   - Test end-to-end flow

---

**Status**: Ready for Implementation

**Recommended Start**: Create `google_trends_service.py` with proper structure, error handling, and async support.
