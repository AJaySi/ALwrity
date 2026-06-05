# GSC Strategy Insights Service - SEO Dashboard Integration Guide

**Date**: May 27, 2026  
**Phase**: SEO Dashboard Integration (Post-Blog Writer)  
**Status**: ✅ Core Service & API Endpoints Complete

---

## 📚 Overview

The **GSC Strategy Insights Service** adapts the GSC Brainstorm technology for SEO Dashboard use cases. While Blog Writer focuses on "What should I blog about?", the dashboard focuses on "What's my overall SEO status and what should I prioritize?"

### Key Difference from Blog Writer

| Aspect | Blog Writer (GSCBrainstormService) | SEO Dashboard (GSCStrategyInsightsService) |
|--------|-----------------------------------|------------------------------------------|
| Question | "What blog post should I write?" | "What should I prioritize for SEO?" |
| Context | Content creation focus | Strategic monitoring focus |
| Time Horizon | Next post (0-2 weeks) | Ongoing (3-12 months) |
| Audience | Writers | SEO managers, strategists |
| Primary Output | 5 categories of suggestions | ROI-ranked opportunities + health metrics |
| Integration | Modal in Blog Writer | Dashboard panels & widgets |
| Refresh | On-demand | Automated (hourly/daily) |

---

## 🏗️ Architecture

### Service Layer

**File**: `backend/services/seo_tools/gsc_strategy_insights_service.py`

**Main Class**: `GSCStrategyInsightsService`

**Key Methods**:

1. **`get_dashboard_strategy(user_id, site_url, ...)`**
   - Main entry point for dashboard
   - Orchestrates all analysis tasks
   - Returns: Comprehensive strategy data

2. **`_get_ranked_opportunities(site_url, top_n)`**
   - Returns ROI-weighted ranked opportunities
   - Uses formula: 40% traffic + 30% ease + 20% competitive + 10% momentum
   - Severity levels: CRITICAL, HIGH, MEDIUM, LOW, WATCH

3. **`_calculate_health_metrics(site_url)`**
   - Health score (0-100)
   - Position distribution
   - CTR benchmarking
   - Growth indicators

4. **`_generate_quick_summary(site_url)`**
   - Text summary for dashboard display
   - Key metric highlights
   - One-liner insights

5. **`_analyze_performance_trends(site_url)`** [Phase 2]
   - Historical trend analysis
   - Seasonal pattern detection
   - Momentum scoring

6. **`_analyze_competitive_positioning(site_url)`** [Phase 2]
   - Competitor keyword analysis
   - Market gap identification
   - Competitive benchmarks

### API Layer

**File**: `backend/routers/seo_tools.py`

**New Endpoints**:

#### 1. `POST /api/seo/gsc/strategy-insights`
```json
Request:
{
  "site_url": "https://example.com",
  "include_trends": true,
  "include_competitive": false,
  "top_n": 20
}

Response:
{
  "status": "success",
  "data": {
    "opportunities": [...],
    "health_metrics": {...},
    "quick_summary": "..."
  }
}
```

**Purpose**: Get comprehensive dashboard strategy

#### 2. `POST /api/seo/gsc/opportunity-ranking`
```json
Request:
{
  "site_url": "https://example.com",
  "ranking_metric": "roi_score",
  "severity_filter": "critical",
  "limit": 20
}

Response:
{
  "status": "success",
  "data": {
    "opportunities": [
      {
        "type": "quick_win",
        "keyword": "Python async",
        "roi_score": 87.5,
        "priority": 1,
        "effort_hours": 2,
        "timeline_weeks": 1,
        "severity": "critical",
        ...
      }
    ],
    "total_opportunities": 45
  }
}
```

**Purpose**: Get ROI-ranked opportunities (filterable by severity/metric)

#### 3. `POST /api/seo/gsc/health-metrics`
```json
Request:
{
  "site_url": "https://example.com",
  "include_distribution": true,
  "include_trends": true
}

Response:
{
  "status": "success",
  "data": {
    "health_score": 68,
    "health_trend": "stable",
    "total_keywords": 250,
    "page_1_keywords": 145,
    "avg_position": 7.2,
    "avg_ctr": 2.8,
    "ctr_vs_benchmark": -0.3,
    ...
  }
}
```

**Purpose**: Get health metrics for dashboard widget

#### 4. `POST /api/seo/gsc/trend-analysis`
```json
Request:
{
  "site_url": "https://example.com",
  "metric": "all",
  "days_back": 90
}

Response:
{
  "status": "pending",
  "message": "Trend analysis requires historical data collection",
  "note": "To be implemented in Phase 2"
}
```

**Purpose**: Analyze performance trends (Phase 2 feature)

---

## 📊 Data Models

### Request Models

```python
class GSCStrategyInsightsRequest(BaseModel):
    site_url: HttpUrl
    include_trends: bool = True
    include_competitive: bool = False
    top_n: int = 20  # 5-100

class GSCOpportunityRankingRequest(BaseModel):
    site_url: HttpUrl
    ranking_metric: str = "roi_score"  # roi_score/effort/impact/timeline
    severity_filter: Optional[str] = None  # critical/high/medium/low/watch
    limit: int = 20  # 5-100

class GSCHealthMetricsRequest(BaseModel):
    site_url: HttpUrl
    include_distribution: bool = True
    include_trends: bool = True

class GSCTrendAnalysisRequest(BaseModel):
    site_url: HttpUrl
    metric: str = "all"  # position/impressions/clicks/ctr/all
    days_back: int = 90  # 7-365
```

### Response Models

```python
@dataclass
class StrategyOpportunity:
    type: StrategyType  # quick_win, keyword_gap, content_opportunity, etc.
    keyword: str
    description: str
    roi_score: float  # 0-100
    priority: int  # 1-10
    effort_hours: float
    timeline_weeks: int
    current_position: float
    impressions: int
    current_ctr: float
    estimated_impact: float  # Monthly clicks gained
    severity: OpportunitySeverity  # CRITICAL, HIGH, MEDIUM, LOW, WATCH
    recommendations: List[str]
    related_keywords: List[str]
    timestamp: datetime

@dataclass
class HealthMetrics:
    health_score: int  # 0-100
    score_trend: str  # up/down/stable
    score_change: float  # Percentage
    total_keywords: int
    page_1_keywords: int
    avg_position: float
    avg_ctr: float
    total_impressions: int
    total_clicks: int
    opportunities_count: int
    timestamp: datetime
```

---

## 🎯 ROI Scoring Formula

```
ROI_Score = 0.40 × traffic_impact + 
            0.30 × ease_of_implementation + 
            0.20 × competitive_advantage + 
            0.10 × momentum_score

where:
  traffic_impact = (estimated_clicks_gained / max_possible) × 100
  ease_of_implementation = 100 × (inverse of effort hours)
  competitive_advantage = keyword relevance to market gaps
  momentum_score = current_trend direction and acceleration
```

### Severity Levels

| Severity | ROI Score | Priority | Timeline |
|----------|-----------|----------|----------|
| CRITICAL | 80-100 | 1-2 (immediate) | 0-2 weeks |
| HIGH | 60-79 | 3-4 (high) | 1-4 weeks |
| MEDIUM | 40-59 | 5-6 (medium) | 2-8 weeks |
| LOW | 20-39 | 7-8 (low) | 1-3 months |
| WATCH | <20 | 9-10 (monitoring) | 3+ months |

---

## 🔌 Frontend Integration

### Hook: `useGSCStrategyInsights()`

```typescript
const {
  // State
  strategyInsights,
  healthMetrics,
  opportunities,
  isLoading,
  error,
  
  // Methods
  fetchStrategyInsights,
  fetchOpportunities,
  fetchHealthMetrics,
  refetchInsights,
  
  // Helpers
  getOpportunitiesBySeverity,
  filterByMetric,
  calculateROI,
} = useGSCStrategyInsights({
  siteUrl: 'https://example.com',
  autoRefresh: true,
  refreshInterval: 3600000, // 1 hour
});
```

### Components

#### 1. StrategyInsightsPanel
```typescript
<StrategyInsightsPanel
  opportunities={opportunities}
  healthMetrics={healthMetrics}
  onOpportunityClick={(opp) => navigateToDetails(opp)}
  isLoading={isLoading}
/>
```

#### 2. HealthMetricsWidget
```typescript
<HealthMetricsWidget
  score={healthMetrics.health_score}
  trend={healthMetrics.score_trend}
  keywords={{
    total: healthMetrics.total_keywords,
    page1: healthMetrics.page_1_keywords,
  }}
/>
```

#### 3. OpportunitiesList
```typescript
<OpportunitiesList
  opportunities={opportunities}
  ranking="roi_score"
  filterBySeverity="critical"
  onSelectOpportunity={(opp) => showDetails(opp)}
/>
```

#### 4. TrendChart
```typescript
<TrendChart
  metric="position"
  data={trendData}
  timeRange={90}
  onPeriodSelect={(period) => updateChart(period)}
/>
```

---

## 📈 Dashboard Layout

### SEO Dashboard - GSC Insights Tab

```
┌─────────────────────────────────────────────────────────────────┐
│ GSC Strategy Insights                      🔄 Refresh | ⚙️ Filter │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│ ┌──────────────────────┬──────────────────────┬─────────────────┐ │
│ │ Health Score         │ Opportunities        │ Top Keywords    │ │
│ │                      │ CRITICAL: 3          │ 1. Python async │ │
│ │   68/100            │ HIGH: 7              │ 2. FastAPI      │ │
│ │   ↓ 5% (was 73)     │ MEDIUM: 12           │ 3. Async/await  │ │
│ │                      │ LOW: 8               │ 4. LLM tutorial │ │
│ └──────────────────────┴──────────────────────┴─────────────────┘ │
│                                                                   │
│ ┌─────────────────────────────────────────────────────────────┐  │
│ │ Quick Wins (Positions 4-10) - Click to expand            │  │
│ ├─────────────────────────────────────────────────────────────┤  │
│ │ 🔴 CRITICAL - Python productivity tools (Pos 7)          │  │
│ │    ROI: 87 | Effort: 2h | Impact: +45/mo                 │  │
│ │    → Update title & meta description                      │  │
│ │                                                           │  │
│ │ 🔴 CRITICAL - FastAPI tutorial (Pos 6)                    │  │
│ │    ROI: 84 | Effort: 3h | Impact: +32/mo                │  │
│ │    → Improve content depth                                │  │
│ │                                                           │  │
│ │ 🟠 HIGH - JavaScript promises (Pos 5)                    │  │
│ │    ROI: 72 | Effort: 4h | Impact: +28/mo                 │  │
│ │    → Enhance examples and explanations                    │  │
│ └─────────────────────────────────────────────────────────────┘  │
│                                                                   │
│ ┌─────────────────────────────────────────────────────────────┐  │
│ │ Keyword Gaps (Positions 11-20) - Click to expand         │  │
│ ├─────────────────────────────────────────────────────────────┤  │
│ │ 🟠 HIGH - Machine learning basics (Pos 15)               │  │
│ │    ROI: 76 | Effort: 12h | Impact: +120/mo               │  │
│ │    → Create comprehensive beginner's guide                │  │
│ │                                                           │  │
│ │ 🟡 MEDIUM - Python concurrency (Pos 18)                  │  │
│ │    ROI: 58 | Effort: 20h | Impact: +85/mo                │  │
│ │    → Build topical authority                              │  │
│ └─────────────────────────────────────────────────────────────┘  │
│                                                                   │
│ ┌─────────────────────────────────────────────────────────────┐  │
│ │ Performance Trend (Last 90 days) [Phase 2]               │  │
│ │ [Chart: Position trend, Impressions, Clicks, CTR]        │  │
│ └─────────────────────────────────────────────────────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Color Coding

- 🔴 CRITICAL (80-100 ROI): Red, highest priority
- 🟠 HIGH (60-79 ROI): Orange, important
- 🟡 MEDIUM (40-59 ROI): Yellow, should do
- 🟢 LOW (20-39 ROI): Green, nice to have
- ⚪ WATCH (<20 ROI): Gray, monitoring

---

## 🔄 Data Flow

```
User Opens SEO Dashboard (GSC Insights Tab)
  ↓
useGSCStrategyInsights() Hook
  ↓
POST /api/seo/gsc/strategy-insights
  ↓
GSCStrategyInsightsService.get_dashboard_strategy()
  ├─ GSCBrainstormService.brainstorm_topics() [reuse existing]
  ├─ _get_ranked_opportunities() [ROI ranking]
  ├─ _calculate_health_metrics() [Health score]
  └─ _generate_quick_summary() [Text summary]
  ↓
Response with:
  - Ranked opportunities
  - Health metrics
  - Quick summary
  ↓
Frontend Components Update:
  - StrategyInsightsPanel
  - HealthMetricsWidget
  - OpportunitiesList
  ↓
User selects opportunity or filters
  ↓
Frontend state updates or new API call
```

---

## ✅ Implementation Status

### Phase 1: Core Service ✅ COMPLETE

- [x] GSCStrategyInsightsService class
- [x] ROI scoring formula
- [x] Opportunity ranking
- [x] Health metrics calculation
- [x] Service initialization & error handling
- [x] API endpoint integration
- [x] Request/response models

### Phase 2: Frontend (This Sprint)

- [ ] useGSCStrategyInsights() hook
- [ ] StrategyInsightsPanel component
- [ ] HealthMetricsWidget component
- [ ] OpportunitiesList component
- [ ] TrendChart component (Phase 2B)
- [ ] Mobile responsive views
- [ ] Integration with SEO Dashboard tabs

### Phase 3: Advanced Features (Future)

- [ ] Trend analysis with historical data
- [ ] Competitive positioning analysis
- [ ] Impact forecasting
- [ ] Smart alerts & notifications
- [ ] Export functionality
- [ ] Scheduled reports

---

## 🧪 Testing

### Unit Tests
```python
# Test ROI scoring formula
def test_roi_score_calculation():
    service = GSCStrategyInsightsService()
    roi = service._calculate_roi_score(
        traffic_impact=80,
        ease=70,
        competitive=60,
        momentum=50
    )
    assert 0 <= roi <= 100
    assert roi == expected_value

# Test severity classification
def test_severity_classification():
    assert service._get_severity(85) == OpportunitySeverity.CRITICAL
    assert service._get_severity(70) == OpportunitySeverity.HIGH
    assert service._get_severity(50) == OpportunitySeverity.MEDIUM
    assert service._get_severity(25) == OpportunitySeverity.LOW
    assert service._get_severity(10) == OpportunitySeverity.WATCH
```

### Integration Tests
```python
# Test full strategy insights flow
async def test_get_dashboard_strategy():
    service = GSCStrategyInsightsService()
    result = await service.get_dashboard_strategy(
        user_id="test_user",
        site_url="https://example.com",
        top_n=20
    )
    assert result['status'] == 'success'
    assert 'opportunities' in result['data']
    assert 'health_metrics' in result['data']
```

### API Tests
```python
# Test endpoint
def test_strategy_insights_endpoint(client):
    response = client.post(
        "/api/seo/gsc/strategy-insights",
        json={"site_url": "https://example.com"}
    )
    assert response.status_code == 200
    assert response.json()['success'] == True
```

---

## 📋 API Reference

### Endpoints Summary

| Endpoint | Method | Purpose | Response Time |
|----------|--------|---------|----------------|
| `/gsc/strategy-insights` | POST | Dashboard strategy | 4-8s |
| `/gsc/opportunity-ranking` | POST | ROI-ranked opportunities | 4-8s |
| `/gsc/health-metrics` | POST | Health metrics | 2-4s |
| `/gsc/trend-analysis` | POST | Trend analysis (Phase 2) | 3-6s |

### Error Responses

```json
{
  "success": false,
  "message": "Error in get_gsc_strategy_insights: ...",
  "error_type": "ValueError",
  "error_details": "Site URL not valid",
  "timestamp": "2026-05-27T10:30:45.123Z"
}
```

---

## 🎓 Usage Examples

### Example 1: Get Strategy Insights

```bash
curl -X POST http://localhost:8000/api/seo/gsc/strategy-insights \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "site_url": "https://example.com",
    "include_trends": true,
    "top_n": 20
  }'
```

### Example 2: Filter Critical Opportunities

```bash
curl -X POST http://localhost:8000/api/seo/gsc/opportunity-ranking \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "site_url": "https://example.com",
    "severity_filter": "critical",
    "limit": 10
  }'
```

### Example 3: Get Health Metrics

```bash
curl -X POST http://localhost:8000/api/seo/gsc/health-metrics \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "site_url": "https://example.com",
    "include_distribution": true
  }'
```

---

## 🚀 Deployment Checklist

- [x] Service class created
- [x] API endpoints implemented
- [x] Request/response models defined
- [ ] Frontend hook created
- [ ] Frontend components built
- [ ] Integration tests written
- [ ] Documentation complete
- [ ] Performance tested
- [ ] Error handling verified
- [ ] Deployed to staging
- [ ] User acceptance testing
- [ ] Deployed to production

---

## 📞 Support & Questions

**Service Location**: `backend/services/seo_tools/gsc_strategy_insights_service.py`  
**Router Location**: `backend/routers/seo_tools.py`  
**Documentation**: [This file]  

---

**Status**: ✅ Core Implementation Complete  
**Next Step**: Frontend Hook & Components Development
