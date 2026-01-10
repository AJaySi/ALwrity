# Priority 2 Alerts Architecture Explanation

## Why Both Common and Tool-Specific Integrations?

You're absolutely right that **common components should be updated once** and automatically picked up everywhere. Here's the architecture:

### Common Component Integration (UsageDashboard)

**Location**: `frontend/src/components/shared/UsageDashboard.tsx`

**Used In**:
- `UserBadge` (in `HeaderControls`) - appears in ALL tool headers
- `WizardHeader` (onboarding)
- Various tool headers directly

**What It Should Show**:
- ✅ **Global cost trends** (spending velocity, budget projections)
- ✅ **Overall OSS recommendations** (general cost savings opportunities)
- ✅ **Usage statistics** (current cost, calls, limits)

**Update Once**: Add Priority 2 alerts here → automatically appears in ALL tool headers

### Tool-Specific Integrations (Optional)

**Purpose**: Contextual alerts and pre-operation cost estimation

**When Needed**:
1. **Pre-Operation Cost Estimation**: Before clicking "Generate Blog" or "Generate Image", show cost estimate
2. **Contextual Recommendations**: In Image Studio, recommend OSS models based on selected provider/model
3. **Workflow-Specific Alerts**: Blog Writer showing cost breakdown for the entire blog generation workflow

**Example**:
- **Common**: "You're spending at a high rate" (shown everywhere)
- **Tool-Specific**: "This blog generation will cost ~$0.05" (shown only in Blog Writer before generation)

## Recommended Architecture

### ✅ **Primary Integration: UsageDashboard**

Add Priority 2 alerts to `UsageDashboard.tsx`:
- Shows cost trends, spending velocity, OSS recommendations
- Automatically appears in all tool headers via `UserBadge`/`HeaderControls`
- **One update, everywhere**

### ✅ **Optional: Tool-Specific Hooks**

Keep tool-specific hooks for:
- Pre-operation cost estimation (before expensive operations)
- Contextual recommendations (based on user's current selection)

**Example Flow**:
1. User opens Blog Writer
2. `UsageDashboard` (in header) shows: "High spending velocity detected"
3. User clicks "Generate Blog"
4. Tool-specific hook shows: "This will cost ~$0.05. Proceed?"

## Implementation Plan

### Phase 1: Common Integration (Recommended)

**Add to `UsageDashboard.tsx`**:
```typescript
import { usePriority2Alerts } from '../../hooks/usePriority2Alerts';
import Priority2AlertBanner from '../shared/Priority2AlertBanner';

// In UsageDashboard component
const { alerts, dismissAlert } = usePriority2Alerts({
  userId,
  enabled: !!userId && subscription?.active,
});

// Show alerts above usage stats
{alerts.length > 0 && (
  <Priority2AlertBanner
    alerts={alerts}
    onDismiss={dismissAlert}
    maxAlerts={2}
  />
)}
```

**Result**: Priority 2 alerts appear in ALL tool headers automatically!

### Phase 2: Tool-Specific (Optional)

Only add tool-specific integrations where you need:
- Pre-operation cost estimation
- Contextual recommendations

**Example**: Blog Writer
```typescript
// Only for pre-operation cost estimation
const { estimateAndProceed } = useBlogWriterCostEstimation();

const handleGenerate = () => {
  estimateAndProceed('content', () => {
    // Actual generation logic
  }, userId);
};
```

## Summary

- **Common Integration**: ✅ Add to `UsageDashboard` → appears everywhere
- **Tool-Specific**: ⚠️ Only for pre-operation estimation and contextual recommendations
- **Best Practice**: Start with common integration, add tool-specific only when needed
