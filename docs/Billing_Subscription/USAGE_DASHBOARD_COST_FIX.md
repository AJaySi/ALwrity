# Usage Dashboard Cost Display Fix

## Issue
The UsageDashboard component (used in dashboard headers) was showing cost as $0.00 even when there was actual API usage cost.

## Root Cause
The component was reading cost from `dashboardData.summary.total_cost_this_month` instead of `dashboardData.current_usage.total_cost`. While the backend populates both fields, the `current_usage.total_cost` is more reliable because:
1. It's properly coerced in the frontend's `billingService.coerceUsageStats()` 
2. It calculates cost from provider breakdown if backend cost is 0
3. It uses `Math.max(backendTotalCost, calculatedTotalCost)` to ensure accuracy

## Solution
Updated `UsageDashboard.tsx` to:
1. **Primary source**: Use `dashboardData.current_usage.total_cost` 
2. **Fallback**: Use `dashboardData.summary.total_cost_this_month` if current_usage is unavailable
3. **Safety**: Added null coalescing with default value of 0

## Changes Made

### File: `frontend/src/components/shared/UsageDashboard.tsx`

**Before:**
```typescript
const totalCost = dashboardData.summary.total_cost_this_month;
```

**After:**
```typescript
// Use current_usage for accurate cost (properly coerced from provider breakdown)
// Fallback to summary if current_usage is not available
const totalCalls = dashboardData.current_usage?.total_calls ?? dashboardData.summary.total_api_calls_this_month;
const totalCost = dashboardData.current_usage?.total_cost ?? dashboardData.summary.total_cost_this_month ?? 0;
const monthlyLimit = dashboardData.limits.limits.monthly_cost;
const usagePercentage = monthlyLimit > 0 ? (totalCost / monthlyLimit) * 100 : 0;
```

**Also updated:**
- Full dashboard view to use `current_usage.total_cost` with fallback
- Total calls to use `current_usage.total_calls` with fallback
- Added safety check for division by zero in usage percentage calculation

## Components Affected
- `UsageDashboard` - Used in:
  - `DashboardHeader` (main dashboard header)
  - `UserBadge` (user menu dropdown)
  - `WizardHeader` (onboarding wizard header)
  - Various tool headers across the application

## Testing
1. ✅ Verify cost displays correctly in dashboard header
2. ✅ Verify cost displays correctly in user badge menu
3. ✅ Verify cost displays correctly during onboarding
4. ✅ Verify fallback works if current_usage is missing
5. ✅ Verify division by zero protection for usage percentage

## Related Files
- `frontend/src/components/shared/UsageDashboard.tsx` - Fixed component
- `frontend/src/services/billingService.ts` - Cost coercion logic (already correct)
- `backend/api/subscription_api.py` - Backend API endpoint (already correct)
- `backend/services/subscription/usage_tracking_service.py` - Backend cost calculation (already correct)

## Notes
- The backend correctly calculates and returns `total_cost` in both `current_usage` and `summary` fields
- The frontend's `billingService.coerceUsageStats()` properly handles cost calculation from provider breakdown
- The fix ensures we use the most accurate cost value available
