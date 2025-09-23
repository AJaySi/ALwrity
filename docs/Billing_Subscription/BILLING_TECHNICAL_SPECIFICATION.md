# Billing Frontend Technical Specification

## 🔧 API Integration Specifications

### 1. Billing Service (`frontend/src/services/billingService.ts`)

```typescript
// Core functions to implement
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

### 2. Monitoring Service (`frontend/src/services/monitoringService.ts`)

```typescript
// Core functions to implement
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

## 📊 Type Definitions (`frontend/src/types/billing.ts`)

```typescript
// Core data structures
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

## 🎨 Component Architecture

### 1. BillingOverview Component
**File**: `frontend/src/components/billing/BillingOverview.tsx`

**Props Interface**:
```typescript
interface BillingOverviewProps {
  userId: string
  onUpgrade?: () => void
  onViewDetails?: () => void
}
```

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

### 2. CostBreakdown Component
**File**: `frontend/src/components/billing/CostBreakdown.tsx`

**Props Interface**:
```typescript
interface CostBreakdownProps {
  providerBreakdown: ProviderBreakdown
  totalCost: number
  onProviderClick?: (provider: string) => void
}
```

**Key Features**:
- Interactive pie chart with provider breakdown
- Hover effects showing detailed costs
- Click to drill down into provider details
- Cost per token calculations

### 3. UsageTrends Component
**File**: `frontend/src/components/billing/UsageTrends.tsx`

**Props Interface**:
```typescript
interface UsageTrendsProps {
  trends: UsageTrends
  timeRange: '3m' | '6m' | '12m'
  onTimeRangeChange: (range: string) => void
}
```

**Key Features**:
- Multi-line chart showing usage over time
- Toggle between cost, calls, and tokens
- Trend analysis with projections
- Peak usage identification

### 4. SystemHealthIndicator Component
**File**: `frontend/src/components/monitoring/SystemHealthIndicator.tsx`

**Props Interface**:
```typescript
interface SystemHealthIndicatorProps {
  health: SystemHealth
  onRefresh?: () => void
}
```

**Key Features**:
- Color-coded health status
- Real-time performance metrics
- Error rate monitoring
- Response time tracking

## 🎭 Animation Specifications

### Framer Motion Variants
```typescript
// Page transitions
const pageVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 }
}

// Card hover effects
const cardVariants = {
  rest: { scale: 1, boxShadow: '0 4px 6px rgba(0,0,0,0.1)' },
  hover: { 
    scale: 1.02, 
    boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
    transition: { duration: 0.2 }
  }
}

// Number animations
const numberVariants = {
  animate: { 
    scale: [1, 1.1, 1],
    transition: { duration: 0.3 }
  }
}
```

### Loading States
```typescript
// Skeleton loaders
const SkeletonCard = () => (
  <div className="animate-pulse bg-gray-200 rounded-lg h-32 w-full" />
)

// Shimmer effects
const ShimmerEffect = () => (
  <div className="animate-pulse bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 h-4 w-full rounded" />
)
```

## 📱 Responsive Design Specifications

### Tailwind CSS Breakpoints
```css
/* Mobile First Approach */
.sm: '640px'   /* Small devices */
.md: '768px'   /* Medium devices */
.lg: '1024px'  /* Large devices */
.xl: '1280px'  /* Extra large devices */
.2xl: '1536px' /* 2X large devices */
```

### Component Responsive Behavior
```typescript
// Responsive grid layout
const gridClasses = {
  mobile: 'grid-cols-1 gap-4',
  tablet: 'md:grid-cols-2 md:gap-6',
  desktop: 'lg:grid-cols-3 lg:gap-8'
}

// Responsive chart sizing
const chartDimensions = {
  mobile: { width: 300, height: 200 },
  tablet: { width: 500, height: 300 },
  desktop: { width: 800, height: 400 }
}
```

## 🔄 Real-Time Updates Implementation

### WebSocket Integration
```typescript
// WebSocket connection for real-time updates
const useRealtimeUpdates = (userId: string) => {
  const [socket, setSocket] = useState<WebSocket | null>(null)
  
  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/billing/${userId}`)
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      // Update local state with real-time data
      updateUsageData(data)
    }
    
    setSocket(ws)
    return () => ws.close()
  }, [userId])
}
```

### Polling Strategy
```typescript
// Intelligent polling based on user activity
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

## 🎨 Design System Implementation

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

### Typography Scale
```typescript
const typography = {
  heading: 'text-2xl font-bold text-gray-900',
  subheading: 'text-lg font-semibold text-gray-800',
  body: 'text-base text-gray-700',
  caption: 'text-sm text-gray-500',
  metric: 'text-3xl font-bold text-blue-600'
}
```

## 📊 Chart Configuration

### Recharts Theme
```typescript
const chartTheme = {
  colors: ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6'],
  grid: {
    stroke: '#e5e7eb',
    strokeWidth: 1,
    strokeDasharray: '3 3'
  },
  axis: {
    stroke: '#6b7280',
    fontSize: 12,
    fontWeight: 500
  },
  tooltip: {
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    border: 'none',
    borderRadius: 8,
    color: 'white'
  }
}
```

### Chart Components
```typescript
// Usage trend chart
const UsageTrendChart = ({ data, type }: { data: TrendData[], type: 'cost' | 'calls' | 'tokens' }) => (
  <ResponsiveContainer width="100%" height={400}>
    <LineChart data={data}>
      <XAxis dataKey="period" />
      <YAxis />
      <Tooltip content={<CustomTooltip />} />
      <Line type="monotone" dataKey={type} stroke="#3b82f6" strokeWidth={2} />
    </LineChart>
  </ResponsiveContainer>
)

// Cost breakdown pie chart
const CostBreakdownChart = ({ data }: { data: ProviderData[] }) => (
  <ResponsiveContainer width="100%" height={300}>
    <PieChart>
      <Pie
        data={data}
        cx="50%"
        cy="50%"
        outerRadius={100}
        fill="#8884d8"
        dataKey="cost"
        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
      >
        {data.map((entry, index) => (
          <Cell key={`cell-${index}`} fill={chartTheme.colors[index % chartTheme.colors.length]} />
        ))}
      </Pie>
      <Tooltip formatter={(value) => [`$${value.toFixed(2)}`, 'Cost']} />
    </PieChart>
  </ResponsiveContainer>
)
```

## 🔒 Security Implementation

### API Security
```typescript
// Secure API calls with authentication
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

### Data Validation
```typescript
// Runtime type checking for API responses
const validateUsageStats = (data: unknown): UsageStats => {
  const schema = z.object({
    billing_period: z.string(),
    total_calls: z.number(),
    total_cost: z.number(),
    // ... other fields
  })
  
  return schema.parse(data)
}
```

## 🧪 Testing Strategy

### Component Testing
```typescript
// Test file structure
__tests__/
├── components/
│   ├── BillingOverview.test.tsx
│   ├── CostBreakdown.test.tsx
│   └── UsageTrends.test.tsx
├── services/
│   ├── billingService.test.ts
│   └── monitoringService.test.ts
└── integration/
    └── billing-dashboard.test.tsx
```

### Test Scenarios
- **Loading States**: Test skeleton loaders and spinners
- **Error Handling**: Test API failure scenarios
- **Responsive Design**: Test across different screen sizes
- **Real-time Updates**: Test WebSocket connections
- **User Interactions**: Test hover effects and animations

## 📈 Performance Optimization

### Code Splitting
```typescript
// Lazy load heavy components
const BillingDashboard = lazy(() => import('./BillingDashboard'))
const UsageTrends = lazy(() => import('./UsageTrends'))

// Route-based code splitting
const BillingRoutes = () => (
  <Suspense fallback={<LoadingSpinner />}>
    <Routes>
      <Route path="/billing" element={<BillingDashboard />} />
      <Route path="/billing/trends" element={<UsageTrends />} />
    </Routes>
  </Suspense>
)
```

### Memoization
```typescript
// Memoize expensive calculations
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

## 🚀 Deployment Considerations

### Environment Configuration
```typescript
// Environment-specific API endpoints
const API_ENDPOINTS = {
  development: 'http://localhost:8000/api',
  staging: 'https://staging-api.alwrity.com/api',
  production: 'https://api.alwrity.com/api'
}
```

### Feature Flags
```typescript
// Feature flag for gradual rollout
const useFeatureFlag = (flag: string) => {
  const [enabled, setEnabled] = useState(false)
  
  useEffect(() => {
    fetchFeatureFlags().then(flags => {
      setEnabled(flags[flag] || false)
    })
  }, [flag])
  
  return enabled
}
```

---

This technical specification provides the foundation for implementing enterprise-grade billing and monitoring features in the ALwrity dashboard, ensuring cost transparency, real-time monitoring, and excellent user experience.
