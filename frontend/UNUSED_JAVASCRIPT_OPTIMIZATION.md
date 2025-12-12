# Unused JavaScript Optimization Guide

## Current Issue
Lighthouse reports **980 KiB of unused JavaScript**. This guide helps identify and fix it.

## Strategy

### 1. Bundle Analysis
First, analyze what's taking up space:

```bash
cd frontend
npm install  # Install source-map-explorer if needed
npm run analyze
```

This creates `bundle-report.html` - open it in a browser to see:
- Which packages are largest
- Which files import them
- Unused code within packages

### 2. Lazy Load Heavy Dependencies

#### A. Recharts (Charts Library)
**Size**: ~200+ KiB  
**Usage**: Only in billing, analytics, and scheduler dashboards

**Before**:
```typescript
import { LineChart, Line } from 'recharts';
```

**After**:
```typescript
import { LazyLineChart, Line } from '../../utils/lazyRecharts';
import { Suspense } from 'react';

<Suspense fallback={<ChartSkeleton />}>
  <LazyLineChart>
    <Line />
  </LazyLineChart>
</Suspense>
```

**Files to update**:
- `frontend/src/components/billing/UsageTrends.tsx`
- `frontend/src/components/SchedulerDashboard/SchedulerCharts.tsx`
- `frontend/src/components/ContentPlanningDashboard/components/MonitoringCharts.tsx`
- `frontend/src/components/shared/charts/AdvancedChartComponents.tsx`

#### B. Wix SDK
**Size**: ~100+ KiB  
**Usage**: Only in WixTestPage and WixCallbackPage

**Before**:
```typescript
import { createClient } from '@wix/sdk';
```

**After**:
```typescript
const { createClient } = await import('@wix/sdk');
// Or use lazy loading in component
```

**Files to update**:
- `frontend/src/components/WixTestPage/WixTestPage.tsx`
- `frontend/src/components/WixCallbackPage/WixCallbackPage.tsx`
- `frontend/src/components/OnboardingWizard/common/usePlatformConnections.ts`

#### C. Framer Motion (Animations)
**Size**: ~246 KiB  
**Usage**: Used extensively but can be optimized

**Strategy**:
1. Use CSS animations for simple transitions
2. Lazy load framer-motion for non-critical animations
3. Use `will-change` CSS property instead of complex animations

**Example**:
```typescript
// Instead of complex framer-motion for simple fade
// Use CSS:
const fadeIn = {
  animation: 'fadeIn 0.3s ease-in'
};
```

### 3. Tree Shaking Optimization

#### A. Material-UI Icons
**Issue**: Importing entire icon set

**Before**:
```typescript
import { TrendingUp, TrendingDown } from '@mui/icons-material';
```

**After** (already optimized, but verify):
```typescript
// React Scripts should tree-shake automatically
// But verify imports are specific
```

#### B. Lucide React Icons
**Issue**: Large icon library, some can be replaced with MUI icons

**Strategy**: Replace lucide-react icons with MUI icons where possible

**Before**:
```typescript
import { TrendingUp } from 'lucide-react';
```

**After**:
```typescript
import { TrendingUp } from '@mui/icons-material';
```

### 4. Remove Unused Dependencies

Check if these are actually used:
- `@wix/blog` - Only in WixTestPage
- `lucide-react` - Can be replaced with MUI icons in many places
- `zod` - Verify if all schemas are used

### 5. Code Splitting Improvements

#### A. Route-Level Splitting (Already Done ✅)
Routes are already lazy-loaded.

#### B. Component-Level Splitting
Lazy load heavy components within routes:

```typescript
// In MainDashboard.tsx
const EnhancedBillingDashboard = lazy(() => 
  import('../billing/EnhancedBillingDashboard')
);
```

### 6. Dynamic Imports for Heavy Features

#### A. Charts
Only load charts when dashboard is viewed:

```typescript
const loadCharts = () => import('recharts');
```

#### B. Analytics
Only load analytics when analytics tab is opened:

```typescript
const loadAnalytics = () => import('./components/AnalyticsInsights');
```

## Implementation Steps

### Step 1: Analyze Bundle
```bash
npm run analyze
# Open bundle-report.html
```

### Step 2: Identify Large Dependencies
Look for:
- Packages > 50 KiB
- Packages used in < 3 places
- Packages that can be lazy-loaded

### Step 3: Lazy Load Heavy Dependencies
1. Create lazy wrappers (see `lazyRecharts.tsx`)
2. Update imports to use lazy versions
3. Add Suspense boundaries

### Step 4: Replace Icons
1. Find lucide-react imports
2. Replace with MUI icons where possible
3. Remove lucide-react if not needed

### Step 5: Test
```bash
npm run build
npm run analyze  # Check if bundle size decreased
```

## Expected Results

### Before
- Unused JavaScript: 980 KiB
- Bundle size: Large initial load

### After
- Unused JavaScript: < 200 KiB (estimated)
- Bundle size: Reduced by ~500-700 KiB
- Performance: Improved initial load time

## Files to Update

### High Priority (Large Impact)
1. ✅ `frontend/src/utils/lazyRecharts.tsx` - Created
2. ✅ `frontend/src/utils/lazyWix.ts` - Created
3. `frontend/src/components/billing/UsageTrends.tsx` - Use lazy recharts
4. `frontend/src/components/SchedulerDashboard/SchedulerCharts.tsx` - Use lazy recharts
5. `frontend/src/components/WixTestPage/WixTestPage.tsx` - Use lazy Wix SDK

### Medium Priority
6. `frontend/src/components/ContentPlanningDashboard/components/MonitoringCharts.tsx`
7. `frontend/src/components/shared/charts/AdvancedChartComponents.tsx`
8. Replace lucide-react with MUI icons in billing components

### Low Priority (Optimization)
9. Optimize framer-motion usage
10. Further code splitting within components

## Monitoring

After changes, verify:
1. Bundle size decreased
2. Lighthouse "Reduce unused JavaScript" improved
3. No broken functionality
4. Charts still work (with loading states)

## Next Steps

1. Run `npm run analyze` to see current bundle
2. Update components to use lazy-loaded dependencies
3. Test functionality
4. Re-run Lighthouse audit

