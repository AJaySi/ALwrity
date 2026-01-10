# Time-Based Retention Implementation for API Usage Logs

## Overview

Implemented time-based retention for API usage logs in addition to the existing count-based retention. This ensures that logs older than a specified retention period are automatically aggregated, regardless of the total log count.

## Implementation Details

### Changes Made

**File**: `backend/services/subscription/log_wrapping_service.py`

#### 1. Added Time-Based Retention Constant

```python
RETENTION_DAYS = 90  # Time-based retention: aggregate logs older than 90 days
```

#### 2. Enhanced `check_and_wrap_logs()` Method

**Before**: Only checked count-based limit (5,000 logs)

**After**: Checks both:
- **Count-based**: If user has more than 5,000 logs
- **Time-based**: If user has logs older than 90 days

**Key Features**:
- Detects logs older than retention period
- Excludes already aggregated logs from time-based checks
- Provides detailed trigger reasons in response
- Reports how many old logs were aggregated

#### 3. Enhanced `_wrap_old_logs()` Method

**New Parameters**:
- `time_based`: Boolean flag to prioritize time-based retention

**Aggregation Strategy**:
1. **Time-based mode**: Aggregates ALL logs older than 90 days (excluding already aggregated)
2. **Count-based mode**: Aggregates oldest logs beyond 4,000 limit
3. **Combined mode**: When count-based is primary, also includes old logs to prevent keeping very old logs just because they're within count limit

**Key Improvements**:
- Prevents re-aggregation of already aggregated logs (`endpoint != '[AGGREGATED]'`)
- Prioritizes old logs even in count-based mode
- Better logging for debugging and monitoring

## How It Works

### Automatic Triggering

The log wrapping is automatically triggered on every `/usage-logs` API call:

```python
# In backend/api/subscription/routes/logs.py
wrapping_service = LogWrappingService(db)
wrap_result = wrapping_service.check_and_wrap_logs(user_id)
```

### Retention Logic Flow

```
1. Check total log count
   ├─ If > 5,000 → Count-based trigger
   └─ If ≤ 5,000 → Continue

2. Check for old logs (> 90 days)
   ├─ If found → Time-based trigger
   └─ If none → No action needed

3. If either trigger active:
   ├─ Time-based: Aggregate ALL logs older than 90 days
   ├─ Count-based: Aggregate oldest logs beyond 4,000 limit
   └─ Combined: Merge both sets (prioritize old logs)

4. Create aggregated records
   ├─ Group by provider + billing period
   ├─ Preserve: costs, tokens, counts, success rates
   └─ Delete individual logs that were aggregated
```

### Example Scenarios

**Scenario 1: Time-Based Only**
- User has 3,000 logs
- 500 logs are older than 90 days
- **Result**: 500 old logs aggregated, 2,500 detailed logs kept

**Scenario 2: Count-Based Only**
- User has 6,000 logs (all recent)
- **Result**: 2,000 oldest logs aggregated, 4,000 detailed logs kept

**Scenario 3: Both Triggers**
- User has 6,000 logs
- 1,000 logs are older than 90 days
- **Result**: All 1,000 old logs + 1,000 additional oldest logs aggregated, 4,000 detailed logs kept

## Configuration

### Retention Period

Currently set to **90 days**. To change:

```python
# In LogWrappingService class
RETENTION_DAYS = 90  # Change this value
```

**Recommended Values**:
- **90 days** (current): Good balance for most use cases
- **60 days**: More aggressive, faster aggregation
- **180 days**: Less aggressive, keeps more detailed history

### Count Limits

```python
MAX_LOGS_PER_USER = 5000  # Total logs per user
logs_to_keep = 4000       # Detailed logs to keep
```

## Response Format

The `check_and_wrap_logs()` method now returns enhanced information:

```python
{
    'wrapped': True,
    'total_logs_before': 6000,
    'total_logs_after': 4500,
    'aggregated_logs': 1500,
    'aggregated_periods': [...],
    'trigger_reasons': [
        'count limit (6000 > 5000)',
        'time-based retention (500 logs older than 90 days)'
    ],
    'old_logs_aggregated': 500,
    'message': 'Wrapped 1500 logs into 12 aggregated records'
}
```

## Benefits

1. **Automatic Cleanup**: Old logs are automatically aggregated without manual intervention
2. **Storage Efficiency**: Prevents indefinite growth of detailed logs
3. **Context Preservation**: Aggregated logs maintain all important metrics
4. **Dual Protection**: Both count and time limits ensure efficient storage
5. **No Data Loss**: Historical data is preserved in aggregated form

## Testing

### Manual Testing

1. **Create old logs** (for testing, you can manually update timestamps in database):
   ```sql
   UPDATE api_usage_logs 
   SET timestamp = datetime('now', '-100 days')
   WHERE user_id = 'test_user' AND id IN (SELECT id FROM api_usage_logs LIMIT 10);
   ```

2. **Trigger wrapping** by calling `/api/subscription/usage-logs`

3. **Verify**:
   - Old logs are aggregated
   - Aggregated logs have `endpoint = '[AGGREGATED]'`
   - Total log count reduced
   - Costs and tokens preserved in aggregated records

### Expected Behavior

- Logs older than 90 days are automatically aggregated
- Aggregated logs are not re-aggregated
- Most recent 4,000 logs remain detailed
- All historical data is preserved in aggregated form

## Monitoring

The service logs detailed information:

```
[LogWrapping] User {user_id} needs log wrapping. Total: 6000, Old logs: 500. Triggers: count limit, time-based retention
[LogWrapping] Time-based aggregation: Found 500 logs older than 90 days
[LogWrapping] Wrapped 1500 logs into 12 aggregated records. Remaining logs: 4500
```

## Future Enhancements

1. **Configurable Retention**: Make `RETENTION_DAYS` configurable via environment variable
2. **Tiered Retention**: Different retention periods for different log types
3. **Archive Tables**: Move very old aggregated logs to separate archive tables
4. **Scheduled Jobs**: Run aggregation on a schedule instead of on-demand
5. **Metrics**: Track aggregation statistics over time

## Backward Compatibility

✅ **Fully backward compatible**:
- Existing count-based logic still works
- No breaking changes to API responses
- Old logs without `actual_provider_name` are handled correctly
- Aggregated logs are properly identified and displayed

## Related Files

- `backend/services/subscription/log_wrapping_service.py` - Main implementation
- `backend/api/subscription/routes/logs.py` - API endpoint that triggers wrapping
- `frontend/src/components/billing/UsageLogsTable.tsx` - Frontend display
- `docs/Billing_Subscription/LOG_STORAGE_AND_RETENTION_REVIEW.md` - Review document
