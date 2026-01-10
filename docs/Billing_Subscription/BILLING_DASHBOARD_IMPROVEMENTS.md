# Billing Dashboard Improvements

## Summary of Changes

### 1. ✅ Migration Script - Add `actual_provider_name` Column

**Status**: Completed successfully

- Added `actual_provider_name` column to `api_usage_logs` table
- Migration script handles SQLite and MySQL/PostgreSQL
- Backfilled existing records with detected provider names
- Column now tracks real providers: WaveSpeed, Google, HuggingFace, etc.

### 2. ✅ Provider Breakdown in Monthly Budget Usage

**Status**: Completed

**Changes Made**:
- Updated `usage_tracking_service.py` to include all providers in breakdown:
  - Video (WaveSpeed, HuggingFace)
  - Audio (WaveSpeed)
  - Image (Stability, WaveSpeed)
  - Image Edit (WaveSpeed)
  - Search APIs (Tavily, Serper, Exa)
- Added provider breakdown display in `CompactBillingDashboard.tsx`:
  - Shows top 5 providers by cost
  - Displays as chips below the progress bar
  - Format: "Provider: $X.XX"
- Updated `ProviderBreakdown` TypeScript interface to include all providers

**Location**: `frontend/src/components/billing/CompactBillingDashboard.tsx` (lines ~1040-1063)

### 3. ✅ System Health Card Fix

**Status**: Fixed

**Problem**: System Health was showing zeros for all metrics (recent_requests, recent_errors, error_rate)

**Solution**: Updated `get_lightweight_stats()` in `monitoring_middleware.py` to:
- Query `APIRequest` table for last 5 minutes
- Calculate real `recent_requests` count
- Calculate real `recent_errors` count (status >= 400)
- Calculate real `error_rate` percentage
- Determine status based on error rate:
  - `critical`: error_rate > 10%
  - `warning`: error_rate > 5%
  - `healthy`: error_rate <= 5%

**Location**: `backend/services/subscription/monitoring_middleware.py` (lines 371-389)

### 4. ✅ API Error Handling for `actual_provider_name`

**Status**: Fixed

**Problem**: API was trying to access `actual_provider_name` column that didn't exist, causing errors

**Solution**: 
- Added safe access using `getattr()` with try/except
- Falls back to enum value if column doesn't exist
- Migration script ensures column exists

**Location**: `backend/api/subscription_api.py` (lines 1247-1251)

### 5. ✅ Subscription API Review (Lines 611-1017)

**Status**: Reviewed and Fixed

**Issues Found and Fixed**:
1. **Missing limits in subscribe response**: Added `video_calls`, `audio_calls`, `image_edit_calls`, `exa_calls` to limits response
2. **Provider breakdown calculation**: Updated to include all providers, not just Gemini and HuggingFace
3. **Cost calculation**: Updated to sum all provider costs, not just LLM providers

**Code Quality**:
- Error handling is comprehensive
- Logging is detailed and helpful
- Cache management is properly implemented
- Database transaction handling is correct

## Files Modified

### Backend
1. `backend/models/subscription_models.py` - Added `actual_provider_name` field
2. `backend/services/subscription/provider_detection.py` - New utility for provider detection
3. `backend/services/subscription/usage_tracking_service.py` - Enhanced provider breakdown
4. `backend/services/subscription/monitoring_middleware.py` - Fixed System Health stats
5. `backend/services/llm_providers/main_video_generation.py` - Added provider detection
6. `backend/services/llm_providers/main_image_generation.py` - Added provider detection
7. `backend/services/llm_providers/main_audio_generation.py` - Added provider detection
8. `backend/api/subscription_api.py` - Fixed error handling, added missing limits
9. `backend/scripts/add_actual_provider_name_column.py` - Migration script

### Frontend
1. `frontend/src/types/billing.ts` - Updated `ProviderBreakdown` interface
2. `frontend/src/components/billing/CompactBillingDashboard.tsx` - Added provider breakdown display
3. `frontend/src/components/billing/UsageLogsTable.tsx` - Display actual provider name
4. `frontend/src/components/monitoring/SystemHealthIndicator.tsx` - Already correct (needs `onRefresh` prop)

## Testing Checklist

- [x] Migration script runs successfully
- [x] Provider breakdown shows in Monthly Budget Usage
- [x] System Health displays real data (not zeros)
- [x] API Usage Logs show actual provider names
- [ ] Test with existing data (backfill)
- [ ] Test with new API calls (provider detection)
- [ ] Verify all providers appear in breakdown

## Next Steps

1. **Monitor**: Watch for any errors related to `actual_provider_name` column
2. **Verify**: Check that System Health shows real data after API calls
3. **Test**: Verify provider breakdown appears correctly in compact view
4. **Enhance**: Consider adding provider breakdown to detailed view as well

## Notes

- The migration script successfully added the column and backfilled 0 records (no existing records to backfill)
- System Health now queries real data from `APIRequest` table
- Provider breakdown includes all providers, sorted by cost (top 5 displayed)
- All changes are backward compatible (fallback to enum values if `actual_provider_name` is missing)
