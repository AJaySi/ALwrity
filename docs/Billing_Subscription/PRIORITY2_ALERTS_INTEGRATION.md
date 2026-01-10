# Priority 2 Alerts Integration Guide

## Overview

This guide explains how to integrate **Priority 2 features** from the cost transparency review as alerts in the main dashboard and individual tool components.

**Priority 2 Features** (from `BILLING_DASHBOARD_COST_TRANSPARENCY_REVIEW.md`):
1. **Dynamic Pricing Display** - Show pricing changes and OSS model recommendations
2. **Cost Estimation Before Operations** - Warn users before expensive operations
3. **Historical Cost Trends** - Alert on high spending velocity and budget projections

---

## Architecture

### Components

1. **`usePriority2Alerts` Hook** (`frontend/src/hooks/usePriority2Alerts.ts`)
   - Fetches dashboard data and generates Priority 2 alerts
   - Monitors cost trends, spending velocity, and OSS recommendations
   - Auto-refreshes at configurable intervals

2. **`Priority2AlertBanner` Component** (`frontend/src/components/shared/Priority2AlertBanner.tsx`)
   - Displays alerts in a prominent banner format
   - Supports dismissible alerts with localStorage persistence
   - Shows action buttons for alerts

3. **Tool-Specific Alert Components**:
   - `BlogWriterCostAlerts` - Blog Writer integration
   - `CreateStudioCostAlerts` - Image Studio integration

---

## Main Dashboard Integration

### Step 1: Add Priority 2 Alerts to Main Dashboard

```typescript
// In your main dashboard component (e.g., MainDashboard.tsx or Dashboard.tsx)
import React from 'react';
import { usePriority2Alerts } from '../hooks/usePriority2Alerts';
import Priority2AlertBanner from '../components/shared/Priority2AlertBanner';
import { useSubscription } from '../contexts/SubscriptionContext';

const MainDashboard: React.FC = () => {
  const { subscription } = useSubscription();
  const userId = subscription?.user_id; // Get from your auth context

  const { alerts, refreshAlerts, dismissAlert } = usePriority2Alerts({
    userId,
    enabled: !!userId && subscription?.active,
    checkInterval: 120000, // Check every 2 minutes
  });

  return (
    <Box>
      {/* Priority 2 Alert Banner - Show at top of dashboard */}
      <Priority2AlertBanner
        alerts={alerts}
        onDismiss={dismissAlert}
        maxAlerts={3}
      />

      {/* Rest of dashboard content */}
      {/* ... */}
    </Box>
  );
};
```

### Step 2: Integrate with Existing Alert System

The Priority 2 alerts complement the existing `UsageAlerts` component:

```typescript
// In EnhancedBillingDashboard or CompactBillingDashboard
import Priority2AlertBanner from '../shared/Priority2AlertBanner';
import UsageAlerts from '../billing/UsageAlerts';

// Show both alert types
<Grid container spacing={3}>
  <Grid item xs={12}>
    {/* Priority 2 Alerts (cost trends, OSS recommendations) */}
    <Priority2AlertBanner
      alerts={priority2Alerts}
      onDismiss={dismissPriority2Alert}
    />
  </Grid>
  
  <Grid item xs={12} md={4}>
    {/* Existing Usage Alerts (limit warnings) */}
    <UsageAlerts
      alerts={dashboardData.alerts}
      onMarkRead={handleMarkRead}
    />
  </Grid>
</Grid>
```

---

## Blog Writer Integration Example

### Full Integration

```typescript
// In BlogWriter.tsx
import React from 'react';
import { BlogWriterCostAlerts, useBlogWriterCostEstimation } from './BlogWriterUtils/BlogWriterCostAlerts';
import { useSubscription } from '../../contexts/SubscriptionContext';

export const BlogWriter: React.FC = () => {
  const { subscription } = useSubscription();
  const userId = subscription?.user_id;
  const { estimateAndProceed } = useBlogWriterCostEstimation();

  // Wrap research action with cost estimation
  const handleResearchAction = async () => {
    await estimateAndProceed('research', () => {
      // Your actual research logic here
      blogWriterApi.startResearch(payload);
    }, userId);
  };

  // Wrap outline generation with cost estimation
  const handleOutlineGeneration = async () => {
    await estimateAndProceed('outline', () => {
      // Your actual outline generation logic here
      outlineGenRef.current?.generateNow();
    }, userId);
  };

  // Wrap content generation with cost estimation
  const handleContentGeneration = async () => {
    await estimateAndProceed('content', () => {
      // Your actual content generation logic here
      generateContent();
    }, userId);
  };

  return (
    <div>
      {/* Priority 2 Alerts Banner */}
      <BlogWriterCostAlerts
        userId={userId}
        onResearchStart={handleResearchAction}
        onOutlineStart={handleOutlineGeneration}
        onContentStart={handleContentGeneration}
      />

      {/* Rest of Blog Writer UI */}
      {/* ... */}
    </div>
  );
};
```

### Minimal Integration (Just Alerts)

```typescript
// Simple integration - just show alerts, no cost estimation
import { BlogWriterCostAlerts } from './BlogWriterUtils/BlogWriterCostAlerts';

// In your Blog Writer component
<BlogWriterCostAlerts userId={userId} />
```

---

## Image Studio Integration Example

### Full Integration

```typescript
// In CreateStudio.tsx
import React, { useState } from 'react';
import { CreateStudioCostAlerts, useImageStudioCostEstimation } from './CreateStudioCostAlerts';
import { useSubscription } from '../../contexts/SubscriptionContext';

export const CreateStudio: React.FC = () => {
  const { subscription } = useSubscription();
  const userId = subscription?.user_id;
  const [provider, setProvider] = useState('wavespeed');
  const [model, setModel] = useState('qwen-image');
  const [numVariations, setNumVariations] = useState(1);
  
  const { estimateAndGenerate } = useImageStudioCostEstimation();

  const handleGenerate = async () => {
    await estimateAndGenerate(
      provider,
      model,
      numVariations,
      () => {
        // Your actual image generation logic
        generateImage(prompt, { provider, model, numVariations });
      },
      userId
    );
  };

  return (
    <Box>
      {/* Priority 2 Alerts with Cost Estimation */}
      <CreateStudioCostAlerts
        userId={userId}
        provider={provider}
        model={model}
        numVariations={numVariations}
        onGenerate={handleGenerate}
      />

      {/* Image generation form */}
      {/* ... */}
    </Box>
  );
};
```

---

## Operation Type Examples

### Blog Writer Operations

```typescript
// Research Phase
const researchOperations: PreflightOperation[] = [
  {
    provider: 'exa',
    operation_type: 'research',
    tokens_requested: 0, // Exa is per-search, not token-based
  },
  {
    provider: 'exa',
    operation_type: 'research',
    tokens_requested: 0,
  },
  {
    provider: 'gemini',
    model: 'gemini-2.5-flash',
    operation_type: 'research',
    tokens_requested: 2000, // Analysis tokens
  }
];

// Outline Generation
const outlineOperations: PreflightOperation[] = [
  {
    provider: 'gemini',
    model: 'gemini-2.5-flash',
    operation_type: 'outline_generation',
    tokens_requested: 1500,
  }
];

// Content Generation (per section)
const contentOperations: PreflightOperation[] = [
  {
    provider: 'gemini',
    model: 'gemini-2.5-flash',
    operation_type: 'content_generation',
    tokens_requested: 3000, // Per section
  },
  {
    provider: 'gemini',
    model: 'gemini-2.5-flash',
    operation_type: 'content_generation',
    tokens_requested: 3000,
  }
];
```

### Image Studio Operations

```typescript
// Single Image Generation (OSS Model)
const singleImageOperation: PreflightOperation[] = [
  {
    provider: 'stability', // WaveSpeed OSS models use 'stability' provider
    model: 'qwen-image', // OSS model
    operation_type: 'image_generation',
    tokens_requested: 0, // Not token-based
  }
];

// Multiple Images (Batch)
const batchImageOperations: PreflightOperation[] = Array(5).fill(null).map(() => ({
  provider: 'stability',
  model: 'ideogram-v3-turbo', // Premium OSS model
  operation_type: 'image_generation',
  tokens_requested: 0,
}));

// Image Editing
const imageEditOperation: PreflightOperation[] = [
  {
    provider: 'image_edit',
    model: 'qwen-edit', // OSS model
    operation_type: 'image_editing',
    tokens_requested: 0,
  }
];
```

### Story Writer Operations

```typescript
// Complete Story Generation (with images, audio, video)
const storyOperations: PreflightOperation[] = [
  // Outline
  {
    provider: 'gemini',
    model: 'gemini-2.5-flash',
    operation_type: 'outline_generation',
    tokens_requested: 1500,
  },
  // Script
  {
    provider: 'gemini',
    model: 'gemini-2.5-flash',
    operation_type: 'content_generation',
    tokens_requested: 2000,
  },
  // Images (5 scenes)
  ...Array(5).fill(null).map(() => ({
    provider: 'stability',
    model: 'qwen-image',
    operation_type: 'image_generation',
    tokens_requested: 0,
  })),
  // Audio (5 scenes)
  ...Array(5).fill(null).map(() => ({
    provider: 'audio',
    model: 'minimax-speech-02-hd',
    operation_type: 'audio_generation',
    tokens_requested: 2000, // ~2000 characters per scene
  })),
  // Videos (5 scenes)
  ...Array(5).fill(null).map(() => ({
    provider: 'video',
    model: 'wan-2.5',
    operation_type: 'video_generation',
    tokens_requested: 0,
  })),
];
```

### Podcast Maker Operations

```typescript
// Podcast Generation Workflow
const podcastOperations: PreflightOperation[] = [
  // Research
  {
    provider: 'exa',
    operation_type: 'research',
    tokens_requested: 0,
  },
  {
    provider: 'gemini',
    model: 'gemini-2.5-flash',
    operation_type: 'research',
    tokens_requested: 2000,
  },
  // Script Generation
  {
    provider: 'gemini',
    model: 'gemini-2.5-flash',
    operation_type: 'content_generation',
    tokens_requested: 5000, // Longer script
  },
  // Audio Generation (10 minutes = ~1500 words = ~7500 characters)
  {
    provider: 'audio',
    model: 'minimax-speech-02-hd',
    operation_type: 'audio_generation',
    tokens_requested: 7500, // Characters = tokens for audio
  },
  // Optional: Video Generation (5 scenes)
  ...Array(5).fill(null).map(() => ({
    provider: 'video',
    model: 'wan-2.5',
    operation_type: 'video_generation',
    tokens_requested: 0,
  })),
];
```

### Video Studio Operations

```typescript
// Text-to-Video Generation
const textToVideoOperation: PreflightOperation[] = [
  {
    provider: 'video',
    model: 'wan-2.5', // OSS model (default)
    operation_type: 'video_generation',
    tokens_requested: 0,
  }
];

// Image-to-Video Generation
const imageToVideoOperation: PreflightOperation[] = [
  {
    provider: 'video',
    model: 'wan-2.5',
    operation_type: 'video_generation',
    tokens_requested: 0,
  }
];

// Premium Video (Longer Duration)
const premiumVideoOperation: PreflightOperation[] = [
  {
    provider: 'video',
    model: 'seedance-1.5-pro', // OSS model for longer videos
    operation_type: 'video_generation',
    tokens_requested: 0,
  }
];
```

### Social Media Writer Operations

```typescript
// Facebook/LinkedIn Post Generation
const socialPostOperations: PreflightOperation[] = [
  {
    provider: 'gemini',
    model: 'gemini-2.5-flash',
    operation_type: 'content_generation',
    tokens_requested: 1000, // Short post
  },
  // Optional: Image Generation
  {
    provider: 'stability',
    model: 'qwen-image',
    operation_type: 'image_generation',
    tokens_requested: 0,
  }
];

// Twitter Thread Generation
const twitterThreadOperations: PreflightOperation[] = [
  {
    provider: 'gemini',
    model: 'gemini-2.5-flash',
    operation_type: 'content_generation',
    tokens_requested: 2000, // Multiple tweets
  }
];
```

### SEO Tools Operations

```typescript
// SEO Analysis
const seoAnalysisOperations: PreflightOperation[] = [
  {
    provider: 'gemini',
    model: 'gemini-2.5-flash',
    operation_type: 'seo_analysis',
    tokens_requested: 2500, // Comprehensive analysis
  }
];

// Content Gap Analysis
const contentGapOperations: PreflightOperation[] = [
  {
    provider: 'exa',
    operation_type: 'research',
    tokens_requested: 0,
  },
  {
    provider: 'gemini',
    model: 'gemini-2.5-flash',
    operation_type: 'research',
    tokens_requested: 3000,
  }
];
```

---

## Alert Types Generated

### 1. Cost Trend Alerts

**Triggered When**:
- Spending velocity projects budget exhaustion
- Projected cost exceeds 95% of monthly limit
- Daily spending rate is unusually high

**Example Alert**:
```typescript
{
  id: 'cost-velocity-high',
  type: 'cost_trend',
  severity: 'warning',
  title: 'High Spending Velocity Detected',
  message: 'Your current spending rate projects to $42.50 this month (94% of limit). At this rate, you'll exhaust your budget in ~8 days.',
  action: {
    label: 'View Cost Trends',
    onClick: () => window.location.href = '/billing'
  }
}
```

### 2. OSS Recommendation Alerts

**Triggered When**:
- User is using expensive models when cheaper OSS alternatives exist
- Significant cost savings available by switching models

**Example Alert**:
```typescript
{
  id: 'oss-image-recommendation',
  type: 'oss_recommendation',
  severity: 'info',
  title: '💡 Cost Savings Opportunity',
  message: 'You've spent $2.00 on image generation. Switch to Qwen Image OSS model to save ~$0.50 (25% cheaper at $0.03/image vs $0.04/image).',
  action: {
    label: 'Learn More',
    onClick: () => showToastNotification('OSS models are automatically used as defaults in Basic tier', 'info')
  }
}
```

### 3. Cost Estimation Alerts

**Triggered When**:
- User is about to perform an expensive operation (>$0.01)
- Operation represents significant portion of monthly budget (>5%)

**Example Alert**:
```typescript
{
  id: 'cost-estimation-high',
  type: 'cost_estimation',
  severity: 'warning',
  title: 'High-Cost Operation Warning',
  message: 'This video generation will cost approximately $1.25. This represents 2.8% of your monthly budget.',
  action: {
    label: 'Proceed',
    onClick: () => performOperation()
  }
}
```

---

## Integration Checklist

### Main Dashboard
- [ ] Import `usePriority2Alerts` hook
- [ ] Import `Priority2AlertBanner` component
- [ ] Add alert banner at top of dashboard
- [ ] Configure refresh interval (default: 2 minutes)
- [ ] Test alert generation and dismissal

### Blog Writer
- [ ] Import `BlogWriterCostAlerts` component
- [ ] Add component to Blog Writer layout
- [ ] Wrap research/outline/content actions with cost estimation
- [ ] Test cost estimation before operations
- [ ] Verify OSS recommendations appear

### Image Studio
- [ ] Import `CreateStudioCostAlerts` component
- [ ] Add component to Create Studio layout
- [ ] Pass provider/model/numVariations props
- [ ] Integrate cost estimation with generate button
- [ ] Test OSS model recommendations

### Other Tools
- [ ] Story Writer: Add cost alerts for story generation
- [ ] Podcast Maker: Add cost alerts for podcast generation
- [ ] Video Studio: Add cost alerts for video generation
- [ ] Social Media Writers: Add cost alerts for post generation

---

## Testing

### Test Cases

1. **Cost Trend Alerts**
   - [ ] High spending velocity detected
   - [ ] Budget exhaustion projection shown
   - [ ] Alert appears at correct thresholds

2. **OSS Recommendations**
   - [ ] Recommendation appears when using expensive models
   - [ ] Savings calculation is accurate
   - [ ] Alert is dismissible

3. **Cost Estimation**
   - [ ] Estimation shown before expensive operations
   - [ ] User can proceed or cancel
   - [ ] Estimation is accurate (±10%)

4. **Alert Persistence**
   - [ ] Dismissed alerts don't reappear
   - [ ] Alerts refresh at configured interval
   - [ ] Critical alerts cannot be dismissed

---

## Best Practices

1. **Don't Block Users**: Always allow operations to proceed even if estimation fails
2. **Cache Alerts**: Use localStorage to prevent showing same alert repeatedly
3. **Progressive Enhancement**: Alerts enhance UX but shouldn't break functionality
4. **Clear Actions**: Provide actionable buttons in alerts (e.g., "View Billing", "Upgrade Plan")
5. **Contextual Alerts**: Show alerts relevant to current tool/operation
6. **Respect User Preferences**: Allow users to dismiss non-critical alerts

---

## Next Steps

1. **Integrate into Main Dashboard**: Add `Priority2AlertBanner` to main dashboard
2. **Add to Blog Writer**: Integrate `BlogWriterCostAlerts` component
3. **Add to Image Studio**: Integrate `CreateStudioCostAlerts` component
4. **Extend to Other Tools**: Add similar integrations to Story Writer, Podcast Maker, etc.
5. **Monitor Performance**: Track alert generation performance and user engagement

---

**Last Updated**: January 2026
