# GSC and Bing Analytics Integration Summary

## Overview
Google Search Console (GSC) and Bing Webmaster Tools analytics data are now integrated into the Content Strategy autofill system, providing real analytics data for performance metrics, engagement metrics, and traffic sources.

## Changes Made

### 1. Fixed Import Error ✅
- **File**: `transparency.py`
- **Issue**: `List` type not imported from `typing`
- **Fix**: Added `List, Optional` to imports

### 2. Data Integration Service (`data_integration.py`)

#### Added Methods:
- **`_get_gsc_analytics(user_id)`**: Fetches GSC analytics data via `SEODashboardService`
  - Returns: `{data, metrics, date_range, data_freshness, confidence_level}`
  - Handles disconnected/error states gracefully

- **`_get_bing_analytics(user_id)`**: Fetches Bing analytics data via `SEODashboardService` and `BingAnalyticsStorageService`
  - Returns: `{data, metrics, summary, date_range, data_freshness, confidence_level}`
  - Falls back to stored analytics if API is disconnected
  - Attempts to get site URL from onboarding session

#### Updated Methods:
- **`process_onboarding_data()`**: Now includes GSC and Bing analytics fetching
- **`_assess_data_quality()`**: Includes GSC and Bing analytics in quality assessment
  - GSC/Bing data increases relevance score (0.15 and 0.10 respectively)
  - Included in completeness calculation

### 3. Analytics Normalizer (`analytics_normalizer.py`) - NEW

#### Functions:
- **`normalize_gsc_analytics(gsc_data)`**: Normalizes GSC data structure
  - Extracts: traffic_metrics, top_queries, top_pages, traffic_sources, performance_metrics, engagement_metrics
  - Maps GSC metrics to standard format

- **`normalize_bing_analytics(bing_data)`**: Normalizes Bing data structure
  - Extracts: traffic_metrics, top_queries, traffic_sources, performance_metrics, engagement_metrics
  - Uses summary data from storage if API data unavailable
  - Maps Bing metrics to standard format

- **`normalize_analytics_combined(gsc_data, bing_data)`**: Combines both analytics sources
  - Merges traffic sources (combines organic search data)
  - Averages engagement metrics when both available
  - Deduplicates and aggregates top queries
  - Tracks data sources used

### 4. Transformer Updates (`transformer.py`)

#### Updated Fields:
- **`performance_metrics`**: Now uses analytics data when available
  - Priority: Analytics data > Website analysis data
  - Merges traffic from analytics with conversion/bounce from website

- **`engagement_metrics`**: Now uses analytics data when available
  - Uses CTR from GSC/Bing as engagement rate proxy
  - Maps: clicks, impressions, click_through_rate, avg_position
  - Note: Likes, shares, comments not available from GSC/Bing (set to 0)

- **`traffic_sources`**: Now uses analytics data when available
  - Adds "Organic Search" data from GSC/Bing
  - Merges with existing website traffic sources
  - Provides real click/impression/CTR data

- **`conversion_rates`**: Still uses website data (analytics don't provide conversion data)

### 5. Autofill Service Updates (`autofill_service.py`)

- Added imports for analytics normalizers
- Fetches GSC and Bing raw data from integrated data
- Normalizes GSC and Bing data separately
- Combines analytics data using `normalize_analytics_combined()`
- Passes combined analytics to transformer
- Includes analytics in transparency maps

### 6. Transparency Updates (`transparency.py`)

- **`build_data_sources_map()`**: 
  - Added `analytics` parameter
  - Maps `performance_metrics`, `engagement_metrics`, `traffic_sources` to `analytics_data` source when available

- **`build_input_data_points()`**:
  - Added `gsc_raw` and `bing_raw` parameters
  - Includes GSC and Bing analytics in input data points for transparency
  - Shows which analytics sources were used

## Data Flow

```
Onboarding Database / Analytics Services
    ↓
data_integration.py
  - _get_gsc_analytics() → SEODashboardService.get_gsc_data()
  - _get_bing_analytics() → SEODashboardService.get_bing_data() + BingAnalyticsStorageService
    ↓
analytics_normalizer.py
  - normalize_gsc_analytics()
  - normalize_bing_analytics()
  - normalize_analytics_combined()
    ↓
transformer.py
  - Uses analytics data for:
    * performance_metrics (traffic)
    * engagement_metrics (CTR, clicks, impressions)
    * traffic_sources (organic search)
    ↓
Frontend (30 Strategic Fields)
```

## Field Mapping

### Performance Metrics
- **traffic**: From GSC/Bing total_clicks
- **conversion_rate**: From website (analytics don't provide)
- **bounce_rate**: From website (analytics don't provide)
- **avg_session_duration**: From website (analytics don't provide)

### Engagement Metrics
- **clicks**: From GSC/Bing total_clicks
- **impressions**: From GSC/Bing total_impressions
- **click_through_rate**: From GSC/Bing avg_ctr
- **time_on_page**: From website avg_session_duration
- **engagement_rate**: Uses CTR as proxy
- **likes/shares/comments**: Not available (set to 0)

### Traffic Sources
- **Organic Search**: From GSC/Bing analytics
  - clicks, impressions, ctr
- **Other sources**: From website analysis if available

## Data Quality Impact

- **Completeness**: +2 fields (GSC and Bing analytics)
- **Relevance**: +0.25 (0.15 for GSC, 0.10 for Bing)
- **Confidence**: Higher confidence (0.9) for analytics-derived fields
- **Freshness**: Analytics data typically fresh (1.0)

## Testing Checklist

- [ ] Test with GSC connected - verify performance_metrics and traffic_sources populated
- [ ] Test with Bing connected - verify engagement_metrics populated
- [ ] Test with both GSC and Bing - verify data is combined correctly
- [ ] Test with neither connected - verify fallback to website data
- [ ] Test data source transparency - verify correct sources displayed
- [ ] Test with stored Bing data (API disconnected) - verify fallback works
