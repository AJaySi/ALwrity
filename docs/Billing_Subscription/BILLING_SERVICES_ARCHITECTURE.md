# Billing Services Architecture Documentation

## Overview

The billing services have been completely refactored from a monolithic structure to a modular, secure, and maintainable architecture. This document provides comprehensive guidance for developers working with the billing system.

## 📁 **New Modular Architecture**

### **File Structure**
```
frontend/src/services/billing/
├── index.ts                    # Central export point
├── types.ts                    # All TypeScript interfaces + Zod schemas
├── api.ts                      # Axios instance + interceptors + security
├── utils.ts                    # Validation + formatting + rate limiting
├── subscriptionService.ts      # Subscription operations
├── plansService.ts             # Plans + pricing operations
├── usageService.ts             # Usage data + trends + logs
├── alertsService.ts            # Alert management
└── billingService.ts           # Main aggregator
```

### **Migration Status**
- ✅ **Phase 1**: Modular refactoring complete
- ✅ **Phase 2**: Security enhancements implemented
- ✅ **Phase 3**: Documentation and finalization complete

## 🔧 **API Reference**

### **Core Services**

#### **Subscription Service**
```typescript
import { subscribeToPlan, getUserSubscription, getRenewalHistory } from '@/services/billing';

// Subscribe to a plan with validation
const result = await subscribeToPlan(userId, planId, 'MONTHLY');

// Get user's current subscription
const subscription = await getUserSubscription(userId);

// Get renewal history
const history = await getRenewalHistory(userId);
```

#### **Plans Service**
```typescript
import { getSubscriptionPlans, getAPIPricing } from '@/services/billing';

// Get all available plans
const plans = await getSubscriptionPlans();

// Get API pricing information
const pricing = await getAPIPricing('gemini');
```

#### **Usage Service**
```typescript
import { 
  getDashboardData, 
  getUsageStats, 
  getUsageTrends, 
  getUsageLogs 
} from '@/services/billing';

// Get comprehensive dashboard data
const dashboard = await getDashboardData(userId);

// Get usage statistics with billing period
const stats = await getUsageStats(userId, '2026-02');

// Get usage trends
const trends = await getUsageTrends(userId, 6);

// Get usage logs with filtering
const logs = await getUsageLogs(50, 0, 'gemini', 200, '2026-02');
```

#### **Alerts Service**
```typescript
import { getUsageAlerts, markAlertRead } from '@/services/billing';

// Get user alerts
const alerts = await getUsageAlerts(userId, true); // unread only

// Mark alert as read
await markAlertRead(alertId);
```

### **Utilities**

#### **Validation & Formatting**
```typescript
import { 
  validateBillingPeriod,
  formatCurrency,
  formatNumber,
  formatPercentage,
  getUsageStatusColor,
  getUsageStatusIcon,
  calculateUsagePercentage,
  getProviderIcon,
  getProviderColor
} from '@/services/billing';

// Validate billing period format
const isValid = validateBillingPeriod('2026-02'); // true

// Format currency
const price = formatCurrency(29.99); // "$29.99"

// Format percentage
const percentage = formatPercentage(85.5); // "85.5%"

// Get usage status styling
const color = getUsageStatusColor('active'); // "#22c55e"
const icon = getUsageStatusIcon('warning'); // "⚠️"
```

#### **Rate Limiting**
```typescript
import { checkRateLimit, getRateLimitStatus, clearRateLimit } from '@/services/billing';

// Check if action is allowed
const canProceed = checkRateLimit('subscribe_123', 3, 300000); // 3 requests per 5 minutes

// Get rate limit status
const status = getRateLimitStatus('subscribe_123');
// Returns: { remaining: 2, resetTime: 1234567890, isLimited: false }

// Clear rate limit
clearRateLimit('subscribe_123');
```

## 🔒 **Security Features**

### **Input Validation**
```typescript
// Automatic Zod schema validation for subscription requests
const SubscriptionRequestSchema = z.object({
  plan_id: z.number().positive("Plan ID must be a positive number"),
  billing_cycle: z.enum(['MONTHLY', 'YEARLY']).default('MONTHLY'),
});
```

### **Request Size Limits**
```typescript
// Automatic 1MB limits on all billing API requests
maxContentLength: 1024 * 1024, // 1MB
maxBodyLength: 1024 * 1024, // 1MB
```

### **Error Sanitization**
```typescript
// User-friendly error messages for all HTTP status codes
400 → "Invalid request. Please check your input and try again."
401 → "Authentication required. Please log in again."
429 → "Too many requests. Please wait a moment and try again."
500 → "Server error. Please try again later."
```

### **Rate Limiting**
```typescript
// Client-side protection against API spam
// Subscription operations: 3 requests per 5 minutes
// General operations: 5 requests per minute
```

## 🚀 **Integration Examples**

### **React Component Integration**
```typescript
import React, { useState, useEffect } from 'react';
import { 
  getDashboardData, 
  subscribeToPlan, 
  checkRateLimit,
  formatCurrency 
} from '@/services/billing';

const BillingDashboard = () => {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        const data = await getDashboardData();
        setDashboard(data);
      } catch (error) {
        console.error('Failed to load dashboard:', error);
      } finally {
        setLoading(false);
      }
    };
    loadDashboard();
  }, []);

  const handleSubscribe = async (planId: number) => {
    const userId = localStorage.getItem('user_id');
    const rateLimitKey = `subscribe_${userId}`;
    
    if (!checkRateLimit(rateLimitKey, 3, 300000)) {
      alert('Too many subscription attempts. Please wait a few minutes.');
      return;
    }

    try {
      await subscribeToPlan(userId, planId, 'MONTHLY');
      alert('Subscription successful!');
      // Refresh dashboard
      const data = await getDashboardData();
      setDashboard(data);
    } catch (error) {
      alert(`Subscription failed: ${error.message}`);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h2>Billing Dashboard</h2>
      <p>Current Cost: {formatCurrency(dashboard.current_usage.total_cost)}</p>
      <p>Usage Status: {dashboard.current_usage.usage_status}</p>
      <button onClick={() => handleSubscribe(1)}>
        Subscribe to Basic Plan
      </button>
    </div>
  );
};
```

### **Error Handling Pattern**
```typescript
import { getUsageStats } from '@/services/billing';

const fetchUsageStats = async () => {
  try {
    const stats = await getUsageStats('user123', '2026-02');
    return stats;
  } catch (error) {
    // Error is already sanitized by the service
    if (error.message.includes('Authentication required')) {
      // Redirect to login
      window.location.href = '/login';
    } else if (error.message.includes('Too many requests')) {
      // Show rate limit message
      setTimeout(() => fetchUsageStats(), 60000); // Retry after 1 minute
    } else {
      // Show generic error
      console.error('Failed to fetch usage stats:', error.message);
    }
    throw error;
  }
};
```

## 📊 **Type Safety**

### **Available Types**
```typescript
// Core data structures
interface DashboardData {
  current_usage: UsageStats;
  trends: UsageTrends;
  limits: SubscriptionLimits;
  alerts: UsageAlert[];
  projections: CostProjections;
  summary: UsageSummary;
}

// Usage statistics
interface UsageStats {
  billing_period: string;
  usage_status: 'active' | 'warning' | 'limit_reached';
  total_calls: number;
  total_tokens: number;
  total_cost: number;
  // ... more fields
}

// Subscription request with validation
interface SubscriptionRequest {
  plan_id: number; // Must be positive
  billing_cycle: 'MONTHLY' | 'YEARLY';
}
```

### **Zod Schemas**
```typescript
// Automatic validation for API requests
const SubscriptionRequestSchema = z.object({
  plan_id: z.number().positive("Plan ID must be a positive number"),
  billing_cycle: z.enum(['MONTHLY', 'YEARLY']).default('MONTHLY'),
});

const DashboardDataSchema = z.object({
  current_usage: UsageStatsSchema,
  trends: z.object({
    periods: z.array(z.string()),
    total_calls: z.array(z.number()),
    // ... more validation
  }),
  // ... more fields
});
```

## 🔧 **Migration Guide**

### **From Old Service**
```typescript
// OLD WAY (deprecated)
import billingService from '@/services/billingService';
const data = await billingService.getDashboardData();

// NEW WAY (recommended)
import { getDashboardData } from '@/services/billing';
const data = await getDashboardData();
```

### **Backward Compatibility**
The old import pattern still works but will be deprecated in future versions:

```typescript
// Still works but deprecated
import billingService from '@/services/billingService';
const result = await billingService.subscribeToPlan(userId, planId);

// Recommended new pattern
import { subscribeToPlan } from '@/services/billing';
const result = await subscribeToPlan(userId, planId);
```

## 🛠️ **Development Guidelines**

### **Adding New Features**
1. Create new service file in `frontend/src/services/billing/`
2. Export functions from the service file
3. Add exports to `index.ts` for central access
4. Update types in `types.ts` if needed
5. Add validation schemas for new API requests

### **Error Handling**
- All services automatically sanitize errors
- Use try-catch blocks for specific handling
- Check for specific error messages for user feedback
- Implement retry logic for rate-limited requests

### **Security Considerations**
- Always validate inputs on both client and server
- Use rate limiting for user-initiated actions
- Never expose sensitive information in error messages
- Implement proper authentication checks

## 📈 **Performance Optimizations**

### **Built-in Optimizations**
- Request size limits (1MB max)
- Client-side rate limiting
- Automatic token refresh
- Request deduplication in interceptors
- Efficient error handling with early returns

### **Best Practices**
- Use specific imports instead of importing everything
- Implement proper loading states
- Cache frequently accessed data
- Use debouncing for user inputs
- Handle network errors gracefully

## 🔍 **Debugging**

### **Common Issues**
1. **Authentication Errors**: Check if user is logged in and token is valid
2. **Rate Limiting**: Wait for the reset time before retrying
3. **Validation Errors**: Check input formats and required fields
4. **Network Errors**: Verify backend connectivity

### **Debug Tools**
```typescript
// Enable debug logging
localStorage.setItem('debug_billing', 'true');

// Check rate limit status
import { getRateLimitStatus } from '@/services/billing';
console.log(getRateLimitStatus('subscribe_123'));

// Validate billing period
import { validateBillingPeriod } from '@/services/billing';
console.log('Period valid:', validateBillingPeriod('2026-02'));
```

## 📞 **Support**

For questions about the billing services:
1. Check this documentation first
2. Review the security SSOT document
3. Look at existing integration examples
4. Contact the development team for complex issues

---

**Last Updated**: February 11, 2026  
**Version**: 3.0.0  
**Status**: Production Ready ✅
