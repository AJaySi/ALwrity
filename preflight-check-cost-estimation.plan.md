# Pre-flight Check with Cost Estimation and Button Enhancement Plan

## Overview
Implement a reusable pre-flight check system that shows estimated costs on buttons and validates operations on hover. This will provide users with cost transparency and prevent unnecessary API calls by showing if operations are allowed before execution.

## Goals
1. Show estimated cost on buttons (e.g., "Generate HD Video $0.21")
2. Perform pre-flight check on hover (debounced to avoid performance issues)
3. Show detailed information (allowed/blocked, limits, remaining quota)
4. Disable buttons with appropriate messaging if limits exceeded
5. Common/reusable solution across all ALwrity tools (blog writer, story, linkedin, etc.)
6. Performance optimized (caching, debouncing, batching)
7. Foundation for billing dashboard insights about operation costs

## Current State Analysis

### Backend Existing Capabilities
- **Pre-flight validation**: `preflight_validator.py` has functions like `validate_video_generation_operations`, `validate_image_generation_operations`
- **Limit checking**: `pricing_service.py` has `check_comprehensive_limits()` and `check_usage_limits()`
- **Pricing lookup**: `get_pricing_for_provider_model()` returns cost information
- **Caching**: `_limits_cache` with TTL to reduce DB reads
- **Operation validation**: Supports multi-operation workflows with token estimation

### Frontend Existing Capabilities
- **Billing service**: `billingService.ts` has API client for subscription endpoints
- **Subscription hooks**: `useSubscriptionGuard`, `useSubscription` for subscription state
- **Button components**: Various buttons but no cost/pre-flight integration
- **Usage dashboard**: Shows usage but not per-operation costs

### Gaps
- No lightweight endpoint for cost estimation + pre-flight check
- No reusable button component with cost/pre-flight integration
- No debouncing/throttling for hover-based checks
- No consistent UX pattern across tools

## Implementation Plan

### Phase 1: Backend API Endpoint

#### 1.1 Create Pre-flight Check Endpoint
**File**: `backend/api/subscription_api.py`

**Endpoint**: `POST /api/subscription/preflight-check`

**Purpose**: Lightweight endpoint that:
- Accepts operation definition (provider, model, tokens_estimated, operation_type)
- Returns cost estimation, limits check result, usage info
- Uses caching to minimize DB load
- Fast response (< 100ms with cache hit)

**Request Format**:
```json
{
  "operations": [
    {
      "provider": "video",
      "model": "tencent/HunyuanVideo",
      "tokens_requested": 0,
      "operation_type": "video_generation",
      "actual_provider_name": "huggingface"
    }
  ]
}
```

**Response Format**:
```json
{
  "success": true,
  "data": {
    "can_proceed": true,
    "estimated_cost": 0.21,
    "operations": [
      {
        "provider": "video",
        "operation_type": "video_generation",
        "cost": 0.21,
        "allowed": true,
        "limit_info": {
          "current_usage": 5,
          "limit": 100,
          "remaining": 95
        },
        "message": null
      }
    ],
    "total_cost": 0.21,
    "usage_summary": {
      "current_calls": 5,
      "limit": 100,
      "remaining": 95
    },
    "cached": false
  }
}
```

**Implementation Details**:
- Use `PricingService.check_comprehensive_limits()` for validation
- Use `PricingService.get_pricing_for_provider_model()` for cost
- Leverage existing `_limits_cache` (5-second TTL)
- Return structured error if blocked with user-friendly message

#### 1.2 Batch Pre-flight Check Endpoint (Optional, for performance)
**Endpoint**: `POST /api/subscription/preflight-check-batch`

**Purpose**: Check multiple operations at once for pages with many buttons

**Performance Considerations**:
- Single DB query for all operations
- Batch cache lookups
- Return results in order matching request

### Phase 2: Frontend Service Layer

#### 2.1 Extend Billing Service
**File**: `frontend/src/services/billingService.ts`

**New Functions**:
```typescript
interface PreflightOperation {
  provider: string;
  model?: string;
  tokens_requested?: number;
  operation_type: string;
  actual_provider_name?: string;
}

interface PreflightCheckResponse {
  can_proceed: boolean;
  estimated_cost: number;
  operations: Array<{
    provider: string;
    operation_type: string;
    cost: number;
    allowed: boolean;
    limit_info: {
      current_usage: number;
      limit: number;
      remaining: number;
    };
    message: string | null;
  }>;
  total_cost: number;
  usage_summary: {
    current_calls: number;
    limit: number;
    remaining: number;
  };
  cached: boolean;
}

// Single operation check
export const checkPreflight = async (
  operation: PreflightOperation
): Promise<PreflightCheckResponse>

// Batch operations check (for pages with many buttons)
export const checkPreflightBatch = async (
  operations: PreflightOperation[]
): Promise<PreflightCheckResponse>
```

**Implementation Details**:
- Use axios with request cancellation support
- Add request debouncing wrapper
- Handle errors gracefully (show cached result if available)
- Return structured error messages for UI display

#### 2.2 Create Pre-flight Check Hook
**File**: `frontend/src/hooks/usePreflightCheck.ts`

**Purpose**: Reusable React hook that:
- Manages pre-flight check state (loading, error, result)
- Debounces hover events (300ms delay)
- Caches results per operation (5-second TTL)
- Provides easy-to-use API for components

**API**:
```typescript
interface UsePreflightCheckOptions {
  operation: PreflightOperation;
  enabled?: boolean; // Whether to perform check on hover
  debounceMs?: number; // Debounce delay (default: 300ms)
  cacheTtl?: number; // Cache TTL in ms (default: 5000ms)
}

interface UsePreflightCheckResult {
  canProceed: boolean;
  estimatedCost: number;
  limitInfo: {
    current: number;
    limit: number;
    remaining: number;
  } | null;
  loading: boolean;
  error: string | null;
  checkOnHover: () => void;
  checkNow: () => void; // Immediate check
  reset: () => void;
}

export const usePreflightCheck = (
  options: UsePreflightCheckOptions
): UsePreflightCheckResult
```

**Implementation Details**:
- Use `useState` for state management
- Use `useCallback` for memoized handlers
- Use `useRef` for debounce timers and cache
- Implement request cancellation on unmount

### Phase 3: Reusable Button Component

#### 3.1 Create Enhanced Operation Button Component
**File**: `frontend/src/components/shared/OperationButton.tsx`

**Purpose**: Reusable button component that:
- Shows estimated cost in button label
- Performs pre-flight check on hover
- Shows detailed tooltip with limits/remaining quota
- Disables button with messaging if blocked
- Supports all operation types (video, image, image_edit, text generation, etc.)

**Props**:
```typescript
interface OperationButtonProps {
  // Operation definition
  operation: PreflightOperation;
  
  // Button configuration
  label: string; // Base label (e.g., "Generate HD Video")
  variant?: 'contained' | 'outlined' | 'text';
  size?: 'small' | 'medium' | 'large';
  color?: 'primary' | 'secondary' | 'success' | 'error';
  startIcon?: React.ReactNode;
  endIcon?: React.ReactNode;
  
  // Pre-flight check behavior
  showCost?: boolean; // Show cost in label (default: true)
  checkOnHover?: boolean; // Check on hover (default: true)
  checkOnMount?: boolean; // Check on mount (default: false)
  
  // Callbacks
  onClick: () => void;
  onPreflightResult?: (result: PreflightCheckResponse) => void;
  
  // Customization
  disabled?: boolean; // Additional disabled state
  loading?: boolean; // Loading state override
  tooltipPlacement?: 'top' | 'bottom' | 'left' | 'right';
  
  // Styling
  sx?: SxProps<Theme>;
  fullWidth?: boolean;
}
```

**Features**:
- Cost display: "Generate HD Video $0.21" or "Generate HD Video" if cost unavailable
- Tooltip on hover shows:
  - Operation allowed/blocked status
  - Current usage / limit / remaining
  - Estimated cost breakdown
  - Message if blocked (e.g., "You've reached your video generation limit. Upgrade your plan for more videos.")
- Button disabled if:
  - `disabled` prop is true
  - `loading` prop is true
  - Pre-flight check returned `can_proceed: false`
- Button styling:
  - Normal: standard button
  - Blocked: grayed out with warning icon
  - Loading: spinner with disabled state

**Implementation Details**:
- Use Material-UI `Button` and `Tooltip` components
- Integrate with `usePreflightCheck` hook
- Format cost as currency (e.g., "$0.21" or "$0.00" if free)
- Handle edge cases (no subscription, no limits, etc.)

#### 3.2 Create Operation Type Mappings
**File**: `frontend/src/utils/operationTypes.ts`

**Purpose**: Centralized configuration for operation types:
- Default models per operation type
- Display names
- Icons
- Default token estimates

```typescript
export const OPERATION_TYPES = {
  video_generation: {
    provider: 'video',
    defaultModel: 'tencent/HunyuanVideo',
    displayName: 'Video Generation',
    icon: VideoLibraryIcon,
    defaultTokens: 0,
  },
  image_generation: {
    provider: 'stability',
    defaultModel: 'stability-ai/stable-diffusion-xl',
    displayName: 'Image Generation',
    icon: ImageIcon,
    defaultTokens: 0,
  },
  image_editing: {
    provider: 'image_edit',
    defaultModel: 'Qwen/Qwen-Image-Edit',
    displayName: 'Image Editing',
    icon: EditIcon,
    defaultTokens: 0,
  },
  // ... more operation types
} as const;
```

### Phase 4: Integration Across Tools

#### 4.1 Story Writer Integration
**Files**: 
- `frontend/src/components/StoryWriter/components/HdVideoSection.tsx`
- `frontend/src/components/StoryWriter/components/VideoSection.tsx`
- `frontend/src/components/StoryWriter/components/MultimediaToolbar.tsx`

**Changes**:
- Replace existing buttons with `OperationButton`
- Configure with appropriate operation type
- Pass existing `onClick` handlers

**Example**:
```tsx
<OperationButton
  operation={{
    provider: 'video',
    model: 'tencent/HunyuanVideo',
    tokens_requested: 0,
    operation_type: 'video_generation',
    actual_provider_name: 'huggingface',
  }}
  label="Generate HD Animation"
  showCost={true}
  checkOnHover={true}
  onClick={handleGenerateHdVideo}
  disabled={isGeneratingHdVideo || state.hdVideoGenerationStatus === 'awaiting_approval'}
  loading={isGeneratingHdVideo}
/>
```

#### 4.2 Blog Writer Integration
**Files**: Various blog writer components with generation buttons

**Changes**: Similar to Story Writer - replace buttons with `OperationButton`

#### 4.3 LinkedIn Writer Integration
**Files**: LinkedIn writer components

**Changes**: Similar pattern

### Phase 5: Performance Optimization

#### 5.1 Caching Strategy
**Backend**:
- Use existing `_limits_cache` (5-second TTL)
- Cache pre-flight check results per user:operation combination
- Invalidate cache on usage updates

**Frontend**:
- In-memory cache per hook instance (5-second TTL)
- Share cache across components using React Context
- Clear cache on subscription changes

#### 5.2 Debouncing/Throttling
**Frontend**:
- Debounce hover events (300ms delay)
- Throttle batch requests (max 1 request per 500ms)
- Cancel in-flight requests on unmount/hover exit

#### 5.3 Request Batching
**Frontend**:
- For pages with many buttons (e.g., story export with multiple operations)
- Batch multiple operations into single request
- Use `checkPreflightBatch` API

#### 5.4 Lazy Loading
**Frontend**:
- Only check on hover (not on mount)
- Optional: Check on mount for primary buttons only
- Defer checks for secondary/tertiary buttons

### Phase 6: Billing Dashboard Integration (Future)

#### 6.1 Operation Cost Tracking
**Backend**: 
- Track operation costs in `APIUsageLog` (already exists)
- Add operation_type field to logs (already exists)

#### 6.2 Cost Insights
**Frontend**:
- Add operation cost breakdown to billing dashboard
- Show most expensive operations
- Show cost trends per operation type
- Add filters by operation type

## Performance Considerations

### Potential Bottlenecks
1. **Many buttons on one page**: Each button hovering could trigger requests
   - **Solution**: Batch requests, debounce, cache aggressively

2. **Rapid hover in/out**: Multiple requests for same operation
   - **Solution**: Debounce (300ms), cancel in-flight requests

3. **Backend DB load**: Each check queries subscription/usage tables
   - **Solution**: Use existing cache (5-second TTL), optimize queries

4. **Frontend render performance**: Many tooltips updating
   - **Solution**: Virtualize if needed, optimize re-renders with React.memo

### Performance Targets
- Pre-flight check API: < 100ms with cache hit, < 300ms without cache
- Frontend hover response: < 50ms (debounced)
- Batch check (10 operations): < 500ms
- Tooltip render: < 16ms (60fps)

## Testing Strategy

### Unit Tests
- `usePreflightCheck` hook: debouncing, caching, error handling
- `OperationButton` component: cost display, tooltip, disabled states
- Billing service: API calls, error handling

### Integration Tests
- Pre-flight check endpoint: validation, cost calculation, caching
- Button hover behavior: tooltip display, disabled states

### E2E Tests
- User hovers over button, sees cost and limits
- User blocked by limits, sees appropriate messaging
- User clicks button, operation executes (or fails with clear error)

## Migration Strategy

### Phase 1: Backend (Week 1)
1. Create pre-flight check endpoint
2. Add unit tests
3. Deploy and monitor performance

### Phase 2: Frontend Core (Week 2)
1. Extend billing service
2. Create `usePreflightCheck` hook
3. Create `OperationButton` component
4. Add unit tests

### Phase 3: Integration (Week 3)
1. Integrate into Story Writer (highest priority - most buttons)
2. Test thoroughly
3. Iterate based on feedback

### Phase 4: Rollout (Week 4+)
1. Integrate into Blog Writer
2. Integrate into LinkedIn Writer
3. Integrate into other tools
4. Monitor performance and user feedback

## Success Metrics

1. **User Experience**:
   - Reduced confusion about operation costs
   - Fewer failed operations due to limits
   - Increased clarity about remaining quota

2. **Performance**:
   - < 100ms API response time (with cache)
   - < 1% increase in backend DB load
   - No noticeable UI lag on pages with many buttons

3. **Adoption**:
   - All major operation buttons using new component
   - Consistent UX across all tools

## Future Enhancements

1. **Cost estimation for multi-operation workflows**: Estimate total cost for complex operations
2. **Usage predictions**: Show projected usage if user continues current pattern
3. **Cost optimization suggestions**: Suggest cheaper alternatives
4. **Batch operation approval**: Show total cost and allow approval for multiple operations
5. **Cost alerts**: Warn users approaching cost limits
6. **Operation history**: Show recent operations and their costs in tooltip

