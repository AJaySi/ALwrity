# Frontend Integration Guide

Technical specifications and integration guide for implementing the billing dashboard in the ALwrity frontend.

## Overview

The billing dashboard provides enterprise-grade insights and cost transparency for all external API usage. It integrates with the subscription system's backend APIs to display real-time usage, costs, and system health.

## Architecture

### Main Dashboard Integration Points

```
Main Dashboard
├── Header Section
│   ├── System Health Indicator
│   ├── Real-time Usage Summary
│   └── Alert Notifications
├── Billing Overview Section
│   ├── Current Usage vs Limits
│   ├── Cost Breakdown by Provider
│   └── Monthly Projections
├── API Monitoring Section
│   ├── External API Performance
│   ├── Cost per API Call
│   └── Usage Trends
└── Subscription Management
    ├── Plan Comparison
    ├── Usage Optimization Tips
    └── Upgrade/Downgrade Options
```

## Service Layer

### Billing Service (`frontend/src/services/billingService.ts`)

Core functions to implement:

```typescript
export const billingService = {
  // Get comprehensive dashboard data
  getDashboardData: (userId: string) => Promise<DashboardData>
  
  // Get current usage statistics
  getUsageStats: (userId: string, period?: string) => Promise<UsageStats>
  
  // Get usage trends over time
  getUsageTrends: (userId: string, months?: number) => Promise<UsageTrends>
  
  // Get subscription plans
  getSubscriptionPlans: () => Promise<SubscriptionPlan[]>
  
  // Get API pricing information
  getAPIPricing: (provider?: string) => Promise<APIPricing[]>
  
  // Get usage alerts
  getUsageAlerts: (userId: string, unreadOnly?: boolean) => Promise<UsageAlert[]>
  
  // Mark alert as read
  markAlertRead: (alertId: number) => Promise<void>
}
```

### Monitoring Service (`frontend/src/services/monitoringService.ts`)

Core functions to implement:

```typescript
export const monitoringService = {
  // Get system health status
  getSystemHealth: () => Promise<SystemHealth>
  
  // Get API performance statistics
  getAPIStats: (minutes?: number) => Promise<APIStats>
  
  // Get lightweight monitoring stats
  getLightweightStats: () => Promise<LightweightStats>
  
  // Get cache performance metrics
  getCacheStats: () => Promise<CacheStats>
}
```

## Type Definitions

### Core Data Structures (`frontend/src/types/billing.ts`)

```typescript
interface DashboardData {
  current_usage: UsageStats
  trends: UsageTrends
  limits: SubscriptionLimits
  alerts: UsageAlert[]
  projections: CostProjections
  summary: UsageSummary
}

interface UsageStats {
  billing_period: string
  usage_status: 'active' | 'warning' | 'limit_reached'
  total_calls: number
  total_tokens: number
  total_cost: number
  avg_response_time: number
  error_rate: number
  limits: SubscriptionLimits
  provider_breakdown: ProviderBreakdown
  alerts: UsageAlert[]
  usage_percentages: UsagePercentages
  last_updated: string
}

interface ProviderBreakdown {
  gemini: ProviderUsage
  openai: ProviderUsage
  anthropic: ProviderUsage
  mistral: ProviderUsage
  tavily: ProviderUsage
  serper: ProviderUsage
  metaphor: ProviderUsage
  firecrawl: ProviderUsage
  stability: ProviderUsage
}

interface ProviderUsage {
  calls: number
  tokens: number
  cost: number
}
```

## Component Architecture

### BillingOverview Component

**File**: `frontend/src/components/billing/BillingOverview.tsx`

**Key Features**:
- Real-time usage display with animated counters
- Progress bars for usage limits
- Cost breakdown with interactive tooltips
- Quick action buttons for plan management

**State Management**:
```typescript
const [usageData, setUsageData] = useState<UsageStats | null>(null)
const [loading, setLoading] = useState(true)
const [error, setError] = useState<string | null>(null)
```

### CostBreakdown Component

**File**: `frontend/src/components/billing/CostBreakdown.tsx`

**Key Features**:
- Interactive pie chart with provider breakdown
- Hover effects showing detailed costs
- Click to drill down into provider details
- Cost per token calculations

### UsageTrends Component

**File**: `frontend/src/components/billing/UsageTrends.tsx`

**Key Features**:
- Multi-line chart showing usage over time
- Toggle between cost, calls, and tokens
- Trend analysis with projections
- Peak usage identification

### SystemHealthIndicator Component

**File**: `frontend/src/components/monitoring/SystemHealthIndicator.tsx`

**Key Features**:
- Color-coded health status
- Real-time performance metrics
- Error rate monitoring
- Response time tracking

## Design System

### Color Palette

```typescript
const colors = {
  primary: {
    50: '#eff6ff',
    500: '#3b82f6',
    900: '#1e3a8a'
  },
  success: {
    50: '#f0fdf4',
    500: '#22c55e',
    900: '#14532d'
  },
  warning: {
    50: '#fffbeb',
    500: '#f59e0b',
    900: '#78350f'
  },
  danger: {
    50: '#fef2f2',
    500: '#ef4444',
    900: '#7f1d1d'
  }
}
```

### Responsive Design

**Breakpoints**:
- Mobile: `640px`
- Tablet: `768px`
- Desktop: `1024px`
- Large: `1280px`

## Real-Time Updates

### Polling Strategy

Intelligent polling based on user activity:

```typescript
const useIntelligentPolling = (userId: string) => {
  const [isActive, setIsActive] = useState(true)
  
  useEffect(() => {
    const interval = setInterval(() => {
      if (isActive) {
        fetchUsageData(userId)
      }
    }, isActive ? 30000 : 300000) // 30s when active, 5m when inactive
    
    return () => clearInterval(interval)
  }, [isActive, userId])
}
```

## Chart Configuration

### Recharts Theme

```typescript
const chartTheme = {
  colors: ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6'],
  grid: {
    stroke: '#e5e7eb',
    strokeWidth: 1,
    strokeDasharray: '3 3'
  }
}
```

## Security Implementation

### API Security

Secure API calls with authentication:

```typescript
const secureApiCall = async (endpoint: string, options: RequestInit = {}) => {
  const token = await getAuthToken()
  
  return fetch(endpoint, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  })
}
```

## Performance Optimization

### Code Splitting

Lazy load heavy components:

```typescript
const BillingDashboard = lazy(() => import('./BillingDashboard'))
const UsageTrends = lazy(() => import('./UsageTrends'))
```

### Memoization

Memoize expensive calculations:

```typescript
const MemoizedCostBreakdown = memo(({ data }: { data: ProviderData[] }) => {
  const processedData = useMemo(() => 
    data.map(item => ({
      ...item,
      percentage: (item.cost / totalCost) * 100
    }))
  , [data, totalCost])
  
  return <CostBreakdownChart data={processedData} />
})
```

## Dependencies

Required packages:

```bash
npm install recharts framer-motion lucide-react
npm install @tanstack/react-query axios
npm install zod
```

## Integration Status

### ✅ Completed
- Type definitions and validation schemas
- Service layer with all API functions
- Core components (BillingOverview, CostBreakdown, UsageTrends, UsageAlerts)
- SystemHealthIndicator component
- Main dashboard integration
- Real-time data fetching with auto-refresh

### 🔄 Ready for Enhancement
- WebSocket integration for instant updates
- Advanced analytics and optimization suggestions
- Export functionality for reports
- Mobile app optimization

## Next Steps

- [API Reference](api-reference.md) - Backend endpoint documentation
- [Implementation Status](implementation-status.md) - Current features and metrics
- [Roadmap](roadmap.md) - Future enhancements

---

**Last Updated**: January 2025

