# Log Storage and Retention Review

## Executive Summary

This document reviews the storage limits, retention policies, and log management mechanisms for:
1. **API Usage Logs** (`api_usage_logs` table)
2. **Subscription Renewal History** (`subscription_renewal_history` table)

## 1. API Usage Logs

### Current Storage Limits

**Per-User Limit:**
- **Maximum Logs Per User**: `5,000` logs (defined in `LogWrappingService.MAX_LOGS_PER_USER`)
- **Detailed Logs Kept**: `4,000` most recent logs
- **Aggregation Threshold**: Logs older than 30 days OR beyond the 4,000 limit are aggregated

**API Query Limits:**
- **Frontend Default**: 50 logs per page (configurable: 10, 25, 50, 100)
- **Backend Maximum**: 5,000 logs per query (`limit` parameter: `ge=1, le=5000`)
- **Pagination**: Fully supported with `offset` and `limit` parameters

### Log Wrapping/Aggregation Mechanism

**Service**: `LogWrappingService` (`backend/services/subscription/log_wrapping_service.py`)

**How It Works:**
1. **Automatic Check**: Triggered on every `/usage-logs` API call via `check_and_wrap_logs()`
2. **Threshold Detection**: When user exceeds 5,000 logs
3. **Aggregation Strategy**:
   - Keeps most recent 4,000 logs as detailed records
   - Aggregates oldest logs beyond 4,000 limit
   - Groups by provider and billing period
   - Creates aggregated log entries with:
     - Total counts, tokens, costs
     - Average response time
     - Success/failure counts
     - Time range (oldest to newest timestamp)
   - Deletes individual logs that were aggregated

**Aggregated Log Format:**
- `endpoint`: `"[AGGREGATED]"`
- `method`: `"AGGREGATED"`
- `model_used`: `"[{count} calls aggregated]"`
- `error_message`: Contains summary (e.g., "Aggregated 150 calls: 145 success, 5 failed")
- `is_aggregated`: Flag set to `true` in frontend

**Context Preservation:**
- ✅ **Preserved**: Total costs, tokens, call counts, success/failure rates, time ranges
- ✅ **Preserved**: Provider and billing period grouping
- ✅ **Preserved**: Average response time
- ❌ **Lost**: Individual endpoint details, specific error messages, request/response sizes

### Current Implementation Status

**✅ Implemented:**
- Automatic log wrapping when limit exceeded
- Aggregation by provider and billing period
- Context preservation for aggregated data
- Frontend display of aggregated logs with special formatting

**⚠️ Potential Issues:**
1. **No Time-Based Retention**: Only count-based, not age-based cleanup
2. **No Manual Cleanup Script**: No scheduled job to clean very old logs
3. **Database Growth**: Aggregated logs still count toward the 5,000 limit
4. **No Archive Strategy**: No mechanism to move old logs to archive tables

### Recommendations

1. **Add Time-Based Retention**:
   - Archive logs older than 12 months
   - Keep aggregated logs for 24 months
   - Delete logs older than 24 months

2. **Improve Aggregation Strategy**:
   - Consider aggregating by month for logs older than 90 days
   - Create separate archive table for very old logs
   - Implement tiered storage (hot/warm/cold)

3. **Add Cleanup Script**:
   - Scheduled job to run monthly
   - Archive old logs before deletion
   - Maintain audit trail

## 2. Subscription Renewal History

### Current Storage Limits

**Per-User Limit:**
- **No Hard Limit**: Unlimited storage (no cleanup/aggregation)
- **API Query Limit**: Maximum 100 records per query (`limit` parameter: `ge=1, le=100`)
- **Frontend Default**: 20 records per page (configurable: 10, 20, 50, 100)

**Storage Characteristics:**
- One record per renewal/upgrade/downgrade event
- Includes usage snapshot before renewal (`usage_before_renewal` JSON field)
- Includes payment information
- Includes period information (start/end dates)

### Current Implementation Status

**✅ Implemented:**
- Full history tracking for all subscription events
- Usage snapshots preserved in JSON format
- Pagination support
- No automatic cleanup (preserves all history)

**⚠️ Potential Issues:**
1. **Unlimited Growth**: No retention policy - will grow indefinitely
2. **Large JSON Snapshots**: `usage_before_renewal` can be large for active users
3. **No Archive Strategy**: All records kept in primary table
4. **No Cleanup Script**: No mechanism to archive old records

### Recommendations

1. **Add Retention Policy**:
   - Keep detailed records for last 24 months
   - Archive records older than 24 months
   - Keep summary records (without full usage snapshots) for 7 years (tax/audit)

2. **Optimize Storage**:
   - Compress `usage_before_renewal` JSON for old records
   - Create summary table for very old records
   - Remove detailed usage snapshots after 12 months

3. **Add Cleanup Script**:
   - Monthly job to archive records older than 24 months
   - Maintain summary records for compliance
   - Preserve payment information indefinitely

## 3. Log Replay Mechanism

### Current Status

**❌ No Log Replay**: There is no mechanism to replay or reconstruct usage from logs.

**What Would Be Needed:**
1. **Event Sourcing Pattern**: Store events that can be replayed
2. **Replay Service**: Service to process logs and rebuild state
3. **State Reconstruction**: Ability to rebuild `UsageSummary` from `APIUsageLog` entries

### Current Data Flow

```
API Call → monitoring_middleware → UsageTrackingService.track_api_usage()
  ↓
APIUsageLog (individual record)
  ↓
UsageSummary (aggregated by billing period)
```

**Issue**: If `UsageSummary` is corrupted or lost, it cannot be fully reconstructed from `APIUsageLog` because:
- Aggregation happens in real-time
- No event sourcing pattern
- No replay mechanism

### Recommendations

1. **Add Replay Capability**:
   - Create `replay_usage_logs()` function in `UsageTrackingService`
   - Rebuild `UsageSummary` from `APIUsageLog` entries
   - Support replay for specific billing periods

2. **Add Validation**:
   - Periodic job to validate `UsageSummary` against `APIUsageLog`
   - Detect discrepancies and auto-correct
   - Alert on data inconsistencies

3. **Consider Event Sourcing** (Future):
   - Store events instead of just logs
   - Enable full state reconstruction
   - Support time-travel queries

## 4. Summary and Action Items

### Current State

| Metric | API Usage Logs | Renewal History |
|--------|---------------|----------------|
| **Per-User Limit** | 5,000 logs | Unlimited |
| **Aggregation** | ✅ Yes (automatic) | ❌ No |
| **Retention Policy** | ⚠️ Count-based only | ❌ None |
| **Cleanup Script** | ❌ No | ❌ No |
| **Log Replay** | ❌ No | ❌ No |
| **Archive Strategy** | ❌ No | ❌ No |

### Priority Actions

**High Priority:**
1. ✅ **Log Wrapping Works**: Already implemented and functional
2. ⚠️ **Add Time-Based Retention**: Implement age-based cleanup for API logs
3. ⚠️ **Add Renewal History Retention**: Implement retention policy for renewal history

**Medium Priority:**
4. **Add Cleanup Scripts**: Create scheduled jobs for both tables
5. **Add Archive Tables**: Create archive tables for old data
6. **Add Replay Capability**: Enable reconstruction of UsageSummary from logs

**Low Priority:**
7. **Optimize Storage**: Compress JSON fields, optimize indexes
8. **Add Monitoring**: Alert on storage growth, aggregation events
9. **Documentation**: Document retention policies for users

### Code Locations

**Log Wrapping:**
- `backend/services/subscription/log_wrapping_service.py`
- Triggered in: `backend/api/subscription/routes/logs.py` (line 86-89)

**Usage Logs API:**
- `backend/api/subscription/routes/logs.py`
- Frontend: `frontend/src/components/billing/UsageLogsTable.tsx`

**Renewal History API:**
- `backend/api/subscription/routes/subscriptions.py` (line 519-586)
- Frontend: `frontend/src/components/billing/SubscriptionRenewalHistory.tsx`

**Models:**
- `backend/models/subscription_models.py`
  - `APIUsageLog` (line 127-173)
  - `SubscriptionRenewalHistory` (line 341-389)

## 5. Recommended Retention Policies

### API Usage Logs

```
┌─────────────────────────────────────────────────────────────┐
│ Retention Policy: API Usage Logs                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ 0-30 days:     Detailed logs (all fields)                   │
│ 30-90 days:    Detailed logs (keep 4,000 most recent)       │
│ 90-365 days:   Aggregated by month                          │
│ 365-730 days:  Aggregated by quarter                       │
│ 730+ days:     Archive to separate table                    │
│                                                              │
│ Max per user:  5,000 records (detailed + aggregated)        │
│ Archive table: Unlimited (for compliance/audit)            │
└─────────────────────────────────────────────────────────────┘
```

### Subscription Renewal History

```
┌─────────────────────────────────────────────────────────────┐
│ Retention Policy: Renewal History                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ 0-12 months:   Full records with usage snapshots             │
│ 12-24 months:  Full records (compressed snapshots)          │
│ 24-84 months:  Summary records (no usage snapshots)        │
│ 84+ months:    Archive to separate table                    │
│                                                              │
│ Payment data:  Keep indefinitely (tax/audit compliance)    │
│ Usage snapshots: Remove after 12 months                     │
└─────────────────────────────────────────────────────────────┘
```

## 6. Implementation Plan

### Phase 1: Immediate (No Breaking Changes)
1. Document current behavior
2. Add monitoring/alerts for log counts
3. Add database indexes for performance

### Phase 2: Retention Policies (Backward Compatible)
1. Add time-based retention to log wrapping
2. Create archive tables
3. Add cleanup scripts (manual execution)

### Phase 3: Automation
1. Schedule cleanup jobs (cron/scheduler)
2. Add replay capability
3. Add validation/audit jobs

### Phase 4: Optimization
1. Compress JSON fields
2. Optimize queries with better indexes
3. Add caching for frequently accessed data
