# Renewal History Retention Policy Implementation

## Overview

Implemented tiered retention policy for subscription renewal history records. This ensures efficient storage while preserving critical payment and subscription data for tax/audit compliance.

## Retention Policy

### Tiered Retention Strategy

```
┌─────────────────────────────────────────────────────────────┐
│ Retention Policy: Subscription Renewal History             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ 0-12 months:   Full records with usage snapshots            │
│                - Complete usage_before_renewal JSON         │
│                - All subscription and payment data          │
│                                                              │
│ 12-24 months:  Compressed records                           │
│                - Compressed usage snapshot (key metrics)    │
│                - All subscription and payment data          │
│                                                              │
│ 24-84 months:  Summary records                              │
│                - No usage snapshots                         │
│                - All subscription and payment data          │
│                                                              │
│ 84+ months:    Archive-ready records                        │
│                - No usage snapshots                         │
│                - Payment data preserved (tax/audit)        │
│                                                              │
│ Payment Data:  Preserved indefinitely (compliance)        │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Details

### New Service

**File**: `backend/services/subscription/renewal_history_retention.py`

**Class**: `RenewalHistoryRetentionService`

### Key Methods

#### 1. `check_and_apply_retention(user_id: str)`

Main method that applies retention policies automatically.

**Process**:
1. Identifies records in each retention tier
2. Compresses usage snapshots for 12-24 month old records
3. Removes usage snapshots for 24-84 month old records
4. Ensures 84+ month old records have no snapshots
5. Returns statistics about processed records

**Returns**:
```python
{
    'retention_applied': True,
    'total_records': 150,
    'compressed_count': 10,
    'summarized_count': 5,
    'archived_count': 2,
    'total_processed': 17,
    'message': 'Processed 17 records: 10 compressed, 5 summarized, 2 archived'
}
```

#### 2. `_compress_usage_snapshots(records)`

Compresses detailed usage snapshots to key metrics only.

**Before Compression**:
```json
{
    "total_calls": 1500,
    "total_tokens": 500000,
    "total_cost": 45.50,
    "provider_breakdown": {...},
    "detailed_metrics": {...},
    "trends": {...}
}
```

**After Compression**:
```json
{
    "total_calls": 1500,
    "total_tokens": 500000,
    "total_cost": 45.50,
    "compressed_at": "2025-01-15T10:30:00",
    "note": "Usage snapshot compressed after 12 months"
}
```

#### 3. `_create_summary_records(records)`

Removes usage snapshots entirely, keeping only subscription and payment data.

#### 4. `_mark_for_archive(records)`

Ensures very old records have no snapshots (should already be done by previous stages).

#### 5. `get_retention_stats(user_id: str)`

Returns statistics about records in each retention tier.

**Returns**:
```python
{
    'total_records': 150,
    'recent_records': 120,  # 0-12 months
    'records_to_compress': 15,  # 12-24 months
    'records_to_summarize': 10,  # 24-84 months
    'records_to_archive': 5,  # 84+ months
    'retention_policy': {
        'compress_after_days': 365,
        'summarize_after_days': 730,
        'archive_after_days': 2555
    }
}
```

## Integration

### Automatic Application

Retention is automatically applied when fetching renewal history:

```python
# In backend/api/subscription/routes/subscriptions.py
@router.get("/renewal-history/{user_id}")
async def get_renewal_history(...):
    # Apply retention before fetching
    retention_service = RenewalHistoryRetentionService(db)
    retention_service.check_and_apply_retention(user_id)
    # ... fetch and return records
```

### New Endpoint

Added endpoint to get retention statistics:

```
GET /api/subscription/renewal-history/{user_id}/retention-stats
```

Returns breakdown of records by retention tier.

## Configuration

### Retention Periods

Currently set to:
- **Compress after**: 365 days (12 months)
- **Summarize after**: 730 days (24 months)
- **Archive after**: 2555 days (84 months / 7 years)

To change:

```python
# In RenewalHistoryRetentionService class
COMPRESS_SNAPSHOT_DAYS = 365  # Change this value
SUMMARY_RECORDS_DAYS = 730    # Change this value
ARCHIVE_DAYS = 2555           # Change this value
```

## Data Preservation

### What's Preserved

✅ **Always Preserved**:
- Payment amount
- Payment status
- Payment date
- Stripe invoice ID
- Plan name and tier
- Billing cycle
- Period start/end dates
- Renewal type and count

✅ **Preserved for 12-24 months**:
- Compressed usage snapshot (key metrics only)

❌ **Removed after 12 months**:
- Detailed usage breakdowns
- Provider-specific metrics
- Trend data
- Detailed usage snapshots

### Compliance

- **Payment Data**: Preserved indefinitely for tax/audit compliance
- **Subscription Data**: Preserved indefinitely for billing history
- **Usage Snapshots**: Removed after 12 months (not required for compliance)

## Benefits

1. **Storage Efficiency**: Reduces database size by removing large JSON snapshots
2. **Compliance**: Preserves all payment data for tax/audit requirements
3. **Performance**: Smaller records = faster queries
4. **Automatic**: No manual intervention required
5. **Gradual**: Applies retention in stages, not all at once

## Example Scenarios

### Scenario 1: New User (0-12 months)
- 5 renewal records, all recent
- **Result**: All records kept with full usage snapshots

### Scenario 2: Active User (12-24 months)
- 20 renewal records
- 3 records are 13 months old
- **Result**: 3 records get compressed snapshots, 17 remain full

### Scenario 3: Long-term User (24+ months)
- 50 renewal records
- 10 records are 25 months old
- **Result**: 10 records have snapshots removed, payment data preserved

### Scenario 4: Very Old Records (84+ months)
- 100 renewal records
- 5 records are 7+ years old
- **Result**: 5 records have no snapshots, ready for archive

## Testing

### Manual Testing

1. **Create test records with old timestamps**:
   ```sql
   UPDATE subscription_renewal_history 
   SET created_at = datetime('now', '-400 days')
   WHERE user_id = 'test_user' AND id IN (SELECT id FROM subscription_renewal_history LIMIT 5);
   ```

2. **Trigger retention** by calling `/api/subscription/renewal-history/{user_id}`

3. **Verify**:
   - Records 12-24 months old have compressed snapshots
   - Records 24+ months old have no snapshots
   - Payment data is preserved in all records

### Expected Behavior

- Records are processed automatically on history queries
- Usage snapshots are compressed/removed based on age
- Payment data is never removed
- All subscription data is preserved

## Monitoring

The service logs detailed information:

```
[RenewalRetention] Applied retention for user {user_id}: 10 compressed, 5 summarized, 2 archived
```

## Future Enhancements

1. **Archive Table**: Move very old records to separate archive table
2. **Scheduled Jobs**: Run retention on a schedule instead of on-demand
3. **Configurable Periods**: Make retention periods configurable via environment variables
4. **Metrics Dashboard**: Show retention statistics in admin dashboard
5. **Export Functionality**: Allow export of old records before archive

## Backward Compatibility

✅ **Fully backward compatible**:
- Existing records are processed automatically
- No breaking changes to API responses
- Old records without snapshots are handled correctly
- Payment data is always preserved

## Related Files

- `backend/services/subscription/renewal_history_retention.py` - Main implementation
- `backend/api/subscription/routes/subscriptions.py` - API endpoint integration
- `frontend/src/components/billing/SubscriptionRenewalHistory.tsx` - Frontend display
- `docs/Billing_Subscription/LOG_STORAGE_AND_RETENTION_REVIEW.md` - Review document
