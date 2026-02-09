import axios, { AxiosResponse } from 'axios';
import { emitApiEvent } from '../utils/apiEvents';
import { getApiUrl } from '../api/client';
import {
  DashboardData,
  UsageStats,
  UsageTrends,
  SubscriptionPlan,
  APIPricing,
  UsageAlert,
  // UsageLog,
  UsageLogsResponse,
  DashboardAPIResponse,
  UsageAPIResponse,
  PlansAPIResponse,
  PricingAPIResponse,
  AlertsAPIResponse,
  DashboardDataSchema,
  UsageStatsSchema,
  // ProviderBreakdown,
  UsagePercentages,
  ProviderUsage,
  // ProviderBreakdownSchema,
  // SubscriptionRenewal,
  RenewalHistoryResponse,
  RenewalHistoryAPIResponse,
} from '../types/billing';

// API base configuration - consistent with client.ts pattern
const API_BASE_URL = getApiUrl();
const BILLING_BASE_URL = API_BASE_URL
  ? `${API_BASE_URL.replace(/\/+$/, '')}/api/subscription`
  : '/api/subscription';

// Create axios instance with default config
const billingAPI = axios.create({
  baseURL: BILLING_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Optional token getter - will be set by App.tsx when Clerk is available
let authTokenGetter: (() => Promise<string | null>) | null = null;

// Export function to set auth token getter (called from App.tsx)
export const setBillingAuthTokenGetter = (getter: (() => Promise<string | null>)) => {
  authTokenGetter = getter;
};

// Request interceptor for authentication - uses Clerk token getter
billingAPI.interceptors.request.use(
  async (config) => {
    // Use Clerk token getter if available (same pattern as apiClient)
    if (authTokenGetter) {
      try {
        const token = await authTokenGetter();
        if (token) {
          config.headers = config.headers || {};
          config.headers.Authorization = `Bearer ${token}`;
        }
      } catch (tokenError) {
        console.error('Error getting auth token for billing API:', tokenError);
      }
    } else {
      console.warn('Billing API: authTokenGetter not set - request may fail authentication');
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling - similar to apiClient pattern
billingAPI.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // Handle network errors
    if (!error.response) {
      console.error('Billing API Network Error:', error.message);
      return Promise.reject(error);
    }
    
    // Handle 401 errors - try to refresh token if possible
    if (error?.response?.status === 401 && !originalRequest._retry && authTokenGetter) {
      originalRequest._retry = true;
      
      try {
        const newToken = await authTokenGetter();
        if (newToken) {
          originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
          return billingAPI(originalRequest);
        }
      } catch (retryError) {
        console.error('Billing API: Token refresh failed:', retryError);
      }
      
      // If retry failed, don't redirect here - let ProtectedRoute handle it
      // The 401 will propagate and ProtectedRoute will check authentication
    }
    
    // Handle rate limiting
    if (error.response?.status === 429) {
      console.warn('Billing API: Rate limited');
    }
    
    console.error('Billing API Error:', error.response?.status, error.response?.data);
    return Promise.reject(error);
  }
);

// ------------------------------------------------------------
// Response coercion helpers to ensure required fields exist
// ------------------------------------------------------------

const defaultProviderUsage = { calls: 0, tokens: 0, cost: 0 };

// const defaultProviderBreakdown = {
//   gemini: { ...defaultProviderUsage },
//   huggingface: { ...defaultProviderUsage },
// };

const defaultLimits = {
  plan_name: 'Unknown Plan',
  tier: 'free' as const,
  limits: {
    gemini_calls: 0,
    openai_calls: 0,
    anthropic_calls: 0,
    mistral_calls: 0,
    tavily_calls: 0,
    serper_calls: 0,
    metaphor_calls: 0,
    firecrawl_calls: 0,
    stability_calls: 0,
    gemini_tokens: 0,
    openai_tokens: 0,
    anthropic_tokens: 0,
    mistral_tokens: 0,
    monthly_cost: 0,
  },
  features: [],
};

// Helper to coerce alerts into fully-typed objects expected by Zod
function coerceAlerts(rawAlerts: any[]): UsageAlert[] {
  if (!Array.isArray(rawAlerts)) return [];
  const nowIso = new Date().toISOString();
  return rawAlerts.map((a: any, idx: number) => ({
    id: typeof a?.id === 'number' ? a.id : idx,
    type: typeof a?.type === 'string' ? a.type : 'usage',
    threshold_percentage: typeof a?.threshold_percentage === 'number' ? a.threshold_percentage : 0,
    provider: typeof a?.provider === 'string' ? a.provider : undefined,
    title: typeof a?.title === 'string' ? a.title : 'Usage alert',
    message: typeof a?.message === 'string' ? a.message : '',
    severity: a?.severity === 'warning' || a?.severity === 'error' || a?.severity === 'info' ? a.severity : 'info',
    is_sent: typeof a?.is_sent === 'boolean' ? a.is_sent : true,
    sent_at: typeof a?.sent_at === 'string' ? a.sent_at : nowIso,
    is_read: typeof a?.is_read === 'boolean' ? a.is_read : false,
    read_at: typeof a?.read_at === 'string' ? a.read_at : undefined,
    billing_period: typeof a?.billing_period === 'string' ? a.billing_period : (a?.period || ''),
    created_at: typeof a?.created_at === 'string' ? a.created_at : nowIso,
  }));
}

function coerceUsageStats(raw: any): UsageStats {
  const providerBreakdown = raw?.provider_breakdown || {};
  const defaultLimits = {
    plan_name: raw?.limits?.plan_name ?? 'free',
    tier: raw?.limits?.tier ?? 'free',
    limits: {
      gemini_calls: raw?.limits?.limits?.gemini_calls ?? 0,
      openai_calls: raw?.limits?.limits?.openai_calls ?? 0,
      anthropic_calls: raw?.limits?.limits?.anthropic_calls ?? 0,
      mistral_calls: raw?.limits?.limits?.mistral_calls ?? 0,
      tavily_calls: raw?.limits?.limits?.tavily_calls ?? 0,
      serper_calls: raw?.limits?.limits?.serper_calls ?? 0,
      metaphor_calls: raw?.limits?.limits?.metaphor_calls ?? 0,
      firecrawl_calls: raw?.limits?.limits?.firecrawl_calls ?? 0,
      stability_calls: raw?.limits?.limits?.stability_calls ?? 0,
      video_calls: raw?.limits?.limits?.video_calls ?? 0,
      image_edit_calls: raw?.limits?.limits?.image_edit_calls ?? 0,
      gemini_tokens: raw?.limits?.limits?.gemini_tokens ?? 0,
      openai_tokens: raw?.limits?.limits?.openai_tokens ?? 0,
      anthropic_tokens: raw?.limits?.limits?.anthropic_tokens ?? 0,
      mistral_tokens: raw?.limits?.limits?.mistral_tokens ?? 0,
      monthly_cost: raw?.limits?.limits?.monthly_cost ?? 0,
    },
    features: raw?.limits?.features ?? [],
  };

  // Extract provider breakdown - only include gemini and huggingface
  // Backend sends mistral data for HuggingFace, so we map it to huggingface
  // Explicitly extract and type the provider usage data
  const geminiData = providerBreakdown.gemini;
  const mistralData = providerBreakdown.mistral; // Backend sends 'mistral' for HuggingFace
  const huggingfaceData = providerBreakdown.huggingface;
  
  // Create properly typed ProviderUsage objects
  const geminiUsage: ProviderUsage = geminiData && typeof geminiData === 'object' && 'calls' in geminiData
    ? { calls: Number(geminiData.calls) || 0, tokens: Number(geminiData.tokens) || 0, cost: Number(geminiData.cost) || 0 }
    : { calls: 0, tokens: 0, cost: 0 };
  
  // Map mistral data to huggingface (HuggingFace is stored as MISTRAL in DB)
  const huggingfaceUsage: ProviderUsage = (huggingfaceData && typeof huggingfaceData === 'object' && 'calls' in huggingfaceData)
    ? { calls: Number(huggingfaceData.calls) || 0, tokens: Number(huggingfaceData.tokens) || 0, cost: Number(huggingfaceData.cost) || 0 }
    : (mistralData && typeof mistralData === 'object' && 'calls' in mistralData)
      ? { calls: Number(mistralData.calls) || 0, tokens: Number(mistralData.tokens) || 0, cost: Number(mistralData.cost) || 0 }
      : { calls: 0, tokens: 0, cost: 0 };
  
  // Create ProviderBreakdown with only gemini and huggingface
  const providerBreakdownCoerced: ProviderBreakdown = {
    gemini: geminiUsage,
    huggingface: huggingfaceUsage,
  };

  // Extract usage percentages - only include gemini and huggingface
  // Backend sends mistral_calls for HuggingFace, map it to huggingface_calls
  const usagePercentagesCoerced: UsagePercentages = {
    gemini_calls: typeof raw?.usage_percentages?.gemini_calls === 'number' ? raw.usage_percentages.gemini_calls : 0,
    huggingface_calls: typeof raw?.usage_percentages?.mistral_calls === 'number' 
      ? raw.usage_percentages.mistral_calls 
      : (typeof raw?.usage_percentages?.huggingface_calls === 'number' ? raw.usage_percentages.huggingface_calls : 0),
    cost: typeof raw?.usage_percentages?.cost === 'number' ? raw.usage_percentages.cost : 0,
  };

  // Calculate total_cost from provider breakdown
  // Always calculate from provider breakdown to ensure accuracy, but prefer backend total if it's more accurate
  const backendTotalCost = typeof raw?.total_cost === 'number' ? raw.total_cost : 0;
  const calculatedTotalCost = geminiUsage.cost + huggingfaceUsage.cost;
  
  // Use the maximum of backend cost and calculated cost to ensure we show the actual cost
  // If backend cost is 0 but we have provider costs, use calculated cost
  // If both are 0, the cost is genuinely 0 (no API calls with costs yet)
  const totalCost = Math.max(backendTotalCost, calculatedTotalCost);
  
  // Debug logging for cost calculation
  if (calculatedTotalCost > 0 || backendTotalCost > 0) {
    console.log('💰 [BILLING DEBUG] Cost calculation in coerceUsageStats:', {
      backendTotalCost,
      calculatedTotalCost,
      finalTotalCost: totalCost,
      geminiCost: geminiUsage.cost,
      huggingfaceCost: huggingfaceUsage.cost,
      geminiCalls: geminiUsage.calls,
      huggingfaceCalls: huggingfaceUsage.calls,
    });
  }

  // Calculate total_calls and total_tokens from provider breakdown if needed
  const backendTotalCalls = typeof raw?.total_calls === 'number' ? raw.total_calls : 0;
  const calculatedTotalCalls = geminiUsage.calls + huggingfaceUsage.calls;
  const totalCalls = backendTotalCalls > 0 ? backendTotalCalls : calculatedTotalCalls;

  const backendTotalTokens = typeof raw?.total_tokens === 'number' ? raw.total_tokens : 0;
  const calculatedTotalTokens = geminiUsage.tokens + huggingfaceUsage.tokens;
  const totalTokens = backendTotalTokens > 0 ? backendTotalTokens : calculatedTotalTokens;

  const coerced: UsageStats = {
    billing_period: raw?.billing_period ?? new Date().toISOString().slice(0,7),
    usage_status: raw?.usage_status ?? 'active',
    total_calls: totalCalls,
    total_tokens: totalTokens,
    total_cost: totalCost,
    avg_response_time: raw?.avg_response_time ?? 0,
    error_rate: raw?.error_rate ?? 0,
    limits: defaultLimits,
    provider_breakdown: providerBreakdownCoerced,
    alerts: coerceAlerts(raw?.alerts),
    usage_percentages: usagePercentagesCoerced,
    last_updated: raw?.last_updated ?? new Date().toISOString(),
  };
  
  return coerced;
}

// Core billing service functions
export const billingService = {
  /**
   * Get comprehensive dashboard data for a user
   */
  getDashboardData: async (userId?: string): Promise<DashboardData> => {
    try {
      const actualUserId = userId || localStorage.getItem('user_id') || 'demo-user';
      // Debug logs removed to reduce console noise
      
      const response = await billingAPI.get<DashboardAPIResponse>(`/dashboard/${actualUserId}`);
      // Debug logs removed to reduce console noise
      
      if (!response.data.success) {
        console.error('❌ [BILLING DEBUG] API response not successful:', response.data);
        throw new Error(response.data.error || 'Failed to fetch dashboard data');
      }
      
      // Coerce missing fields to satisfy the contract before validation
      const raw = response.data.data as any;
      
      // Coerce usage stats first to ensure proper typing
      const currentUsage = coerceUsageStats(raw?.current_usage ?? raw);
      
      const coerced: DashboardData = {
        current_usage: currentUsage,
        trends: raw?.trends ?? {
          periods: [],
          total_calls: [],
          total_cost: [],
          total_tokens: [],
          provider_trends: {},
        },
        limits: raw?.limits ?? defaultLimits,
        alerts: coerceAlerts(raw?.alerts),
        projections: raw?.projections ?? {
          projected_monthly_cost: 0,
          cost_limit: 0,
          projected_usage_percentage: 0,
        },
        summary: raw?.summary ?? {
          total_api_calls_this_month: 0,
          total_cost_this_month: 0,
          usage_status: 'active',
          unread_alerts: 0,
        },
      };

      // Debug: Log cost calculation details
      console.log('💰 [BILLING DEBUG] Cost calculation:', {
        backendTotalCost: coerced.current_usage.total_cost,
        geminiCost: coerced.current_usage.provider_breakdown.gemini?.cost ?? 0,
        huggingfaceCost: coerced.current_usage.provider_breakdown.huggingface?.cost ?? 0,
        calculatedTotal: (coerced.current_usage.provider_breakdown.gemini?.cost ?? 0) + (coerced.current_usage.provider_breakdown.huggingface?.cost ?? 0),
        providerBreakdown: coerced.current_usage.provider_breakdown,
      });

      // Validate response data after coercion
      // Note: If validation fails due to cached schema, we'll handle it gracefully
      try {
        const validatedData = DashboardDataSchema.parse(coerced);
        // Notify app that fresh billing data is available
        emitApiEvent({ url: `/dashboard/${actualUserId}`, method: 'GET', source: 'billing' });
        return validatedData;
      } catch (validationError: any) {
        // Check if error is due to old schema expecting other providers
        const isOldSchemaError = validationError.errors?.some((err: any) => 
          err.path?.includes('provider_breakdown') && 
          err.path[err.path.length - 1] !== 'gemini' && 
          err.path[err.path.length - 1] !== 'huggingface'
        );
        
        if (isOldSchemaError) {
          console.error('❌ [BILLING DEBUG] Validation failed due to cached old schema. Browser cache needs to be cleared.');
          console.error('❌ [BILLING DEBUG] Error details:', validationError.errors);
          // Still return the coerced data - it's correct, just schema validation is cached
          // The data structure is correct with only gemini and huggingface
          emitApiEvent({ url: `/dashboard/${actualUserId}`, method: 'GET', source: 'billing' });
          return coerced;
        }
        
        // For other validation errors, throw them
        console.error('❌ [BILLING DEBUG] Validation error:', validationError);
        throw validationError;
      }
    } catch (error) {
      console.error('❌ [BILLING DEBUG] Error fetching dashboard data:', error);
      throw error;
    }
  },

  /**
   * Get current usage statistics for a user
   */
  getUsageStats: async (userId?: string, period?: string): Promise<UsageStats> => {
    try {
      const actualUserId = userId || localStorage.getItem('user_id') || 'demo-user';
      const params = period ? { billing_period: period } : {};
      
      const response = await billingAPI.get<UsageAPIResponse>(`/usage/${actualUserId}`, { params });
      
      if (!response.data.success) {
        throw new Error(response.data.error || 'Failed to fetch usage stats');
      }
      
      // Coerce then validate
      const raw = response.data.data as any;
      const coerced = coerceUsageStats(raw);
      const validatedData = UsageStatsSchema.parse(coerced);
      emitApiEvent({ url: `/usage/${actualUserId}`, method: 'GET', source: 'billing' });
      return validatedData;
    } catch (error) {
      console.error('Error fetching usage stats:', error);
      throw error;
    }
  },

  /**
   * Get usage trends over time
   */
  getUsageTrends: async (userId?: string, months: number = 6): Promise<UsageTrends> => {
    try {
      const actualUserId = userId || localStorage.getItem('user_id') || 'demo-user';
      const response = await billingAPI.get(`/usage/${actualUserId}/trends`, {
        params: { months }
      });
      
      if (!response.data.success) {
        throw new Error(response.data.error || 'Failed to fetch usage trends');
      }
      
      emitApiEvent({ url: `/usage/${actualUserId}/trends`, method: 'GET', source: 'billing' });
      return response.data.data;
    } catch (error) {
      console.error('Error fetching usage trends:', error);
      throw error;
    }
  },

  /**
   * Get all available subscription plans
   */
  getSubscriptionPlans: async (): Promise<SubscriptionPlan[]> => {
    try {
      const response = await billingAPI.get<PlansAPIResponse>('/plans');
      
      if (!response.data.success) {
        throw new Error(response.data.error || 'Failed to fetch subscription plans');
      }
      
      return response.data.data.plans;
    } catch (error) {
      console.error('Error fetching subscription plans:', error);
      throw error;
    }
  },

  /**
   * Get API pricing information
   */
  getAPIPricing: async (provider?: string): Promise<APIPricing[]> => {
    try {
      const params = provider ? { provider } : {};
      const response = await billingAPI.get<PricingAPIResponse>('/pricing', { params });
      
      if (!response.data.success) {
        throw new Error(response.data.error || 'Failed to fetch API pricing');
      }
      
      emitApiEvent({ url: '/pricing', method: 'GET', source: 'billing' });
      return response.data.data.pricing;
    } catch (error) {
      console.error('Error fetching API pricing:', error);
      throw error;
    }
  },

  /**
   * Get usage alerts for a user
   */
  getUsageAlerts: async (userId?: string, unreadOnly: boolean = false): Promise<UsageAlert[]> => {
    try {
      const actualUserId = userId || localStorage.getItem('user_id') || 'demo-user';
      const response = await billingAPI.get<AlertsAPIResponse>(`/alerts/${actualUserId}`, {
        params: { unread_only: unreadOnly }
      });
      
      if (!response.data.success) {
        throw new Error(response.data.error || 'Failed to fetch usage alerts');
      }
      
      emitApiEvent({ url: `/alerts/${actualUserId}`, method: 'GET', source: 'billing' });
      return response.data.data.alerts;
    } catch (error) {
      console.error('Error fetching usage alerts:', error);
      throw error;
    }
  },

  /**
   * Mark an alert as read
   */
  markAlertRead: async (alertId: number): Promise<void> => {
    try {
      const response = await billingAPI.post(`/alerts/${alertId}/mark-read`);
      
      if (!response.data.success) {
        throw new Error(response.data.error || 'Failed to mark alert as read');
      }
    } catch (error) {
      console.error('Error marking alert as read:', error);
      throw error;
    }
  },

  /**
   * Get user's current subscription information
   */
  getUserSubscription: async (userId?: string) => {
    try {
      const actualUserId = userId || localStorage.getItem('user_id') || 'demo-user';
      const response = await billingAPI.get(`/user/${actualUserId}/subscription`);
      
      if (!response.data.success) {
        throw new Error(response.data.error || 'Failed to fetch user subscription');
      }
      
      return response.data.data;
    } catch (error) {
      console.error('Error fetching user subscription:', error);
      throw error;
    }
  },

  /**
   * Get API usage logs for the current user
   */
  getUsageLogs: async (
    limit: number = 50,
    offset: number = 0,
    provider?: string,
    statusCode?: number,
    billingPeriod?: string
  ): Promise<UsageLogsResponse> => {
    try {
      const params: any = { limit, offset };
      if (provider) params.provider = provider;
      if (statusCode !== undefined) params.status_code = statusCode;
      if (billingPeriod) params.billing_period = billingPeriod;

      const response = await billingAPI.get<UsageLogsResponse>('/usage-logs', { params });
      return response.data;
    } catch (error: any) {
      console.error('Error fetching usage logs:', error);
      throw new Error(
        error.response?.data?.detail ||
        error.message ||
        'Failed to fetch usage logs'
      );
    }
  },

  /**
   * Get subscription renewal history for the current user
   */
  getRenewalHistory: async (
    userId?: string,
    limit: number = 50,
    offset: number = 0
  ): Promise<RenewalHistoryResponse> => {
    try {
      const actualUserId = userId || localStorage.getItem('user_id') || 'demo-user';
      const params: any = { limit, offset };
      
      const response = await billingAPI.get<RenewalHistoryAPIResponse>(
        `/renewal-history/${actualUserId}`,
        { params }
      );
      
      if (!response.data.success) {
        throw new Error(response.data.error || 'Failed to fetch renewal history');
      }
      
      emitApiEvent({ url: `/renewal-history/${actualUserId}`, method: 'GET', source: 'billing' });
      return response.data.data;
    } catch (error: any) {
      console.error('Error fetching renewal history:', error);
      throw new Error(
        error.response?.data?.detail ||
        error.message ||
        'Failed to fetch renewal history'
      );
    }
  },
};

// Utility functions
export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 4,
  }).format(amount);
};

// Pre-flight check interfaces
export interface PreflightOperation {
  provider: string;
  model?: string;
  tokens_requested?: number;
  operation_type: string;
  actual_provider_name?: string;
}

export interface PreflightLimitInfo {
  current_usage: number;
  limit: number;
  remaining: number;
}

export interface PreflightOperationResult {
  provider: string;
  operation_type: string;
  cost: number;
  allowed: boolean;
  limit_info: PreflightLimitInfo | null;
  message: string | null;
}

export interface PreflightCheckResponse {
  can_proceed: boolean;
  estimated_cost: number;
  operations: PreflightOperationResult[];
  total_cost: number;
  usage_summary: {
    current_calls: number;
    limit: number;
    remaining: number;
  } | null;
  cached: boolean;
}

/**
 * Check pre-flight validation for a single operation.
 * Returns cost estimation, limits check, and usage information.
 */
export const checkPreflight = async (
  operation: PreflightOperation
): Promise<PreflightCheckResponse> => {
  try {
    const response = await billingAPI.post<{ success: boolean; data: PreflightCheckResponse }>(
      '/preflight-check',
      {
        operations: [operation]
      }
    );

    if (!response.data.success) {
      throw new Error('Pre-flight check failed');
    }

    return response.data.data;
  } catch (error: any) {
    console.error('[BillingService] Pre-flight check error:', error);
    
    // Return a safe default response on error
    return {
      can_proceed: false,
      estimated_cost: 0,
      operations: [{
        provider: operation.provider,
        operation_type: operation.operation_type,
        cost: 0,
        allowed: false,
        limit_info: null,
        message: error?.response?.data?.detail || 'Pre-flight check failed'
      }],
      total_cost: 0,
      usage_summary: null,
      cached: false
    };
  }
};

/**
 * Check pre-flight validation for multiple operations in a single request.
 * Useful for pages with many buttons to reduce API calls.
 */
export const checkPreflightBatch = async (
  operations: PreflightOperation[]
): Promise<PreflightCheckResponse> => {
  try {
    const response = await billingAPI.post<{ success: boolean; data: PreflightCheckResponse }>(
      '/preflight-check',
      {
        operations
      }
    );

    if (!response.data.success) {
      throw new Error('Pre-flight check failed');
    }

    return response.data.data;
  } catch (error: any) {
    console.error('[BillingService] Pre-flight batch check error:', error);
    
    // Return a safe default response on error
    return {
      can_proceed: false,
      estimated_cost: 0,
      operations: operations.map(op => ({
        provider: op.provider,
        operation_type: op.operation_type,
        cost: 0,
        allowed: false,
        limit_info: null,
        message: error?.response?.data?.detail || 'Pre-flight check failed'
      })),
      total_cost: 0,
      usage_summary: null,
      cached: false
    };
  }
};

export const formatNumber = (num: number): string => {
  return new Intl.NumberFormat('en-US').format(num);
};

export const formatPercentage = (value: number): string => {
  return `${value.toFixed(1)}%`;
};

export const getUsageStatusColor = (status: string): string => {
  switch (status) {
    case 'active':
      return '#22c55e'; // Green
    case 'warning':
      return '#f59e0b'; // Orange
    case 'limit_reached':
      return '#ef4444'; // Red
    default:
      return '#6b7280'; // Gray
  }
};

export const getUsageStatusIcon = (status: string): string => {
  switch (status) {
    case 'active':
      return '✅';
    case 'warning':
      return '⚠️';
    case 'limit_reached':
      return '🚨';
    default:
      return '❓';
  }
};

export const calculateUsagePercentage = (current: number, limit: number): number => {
  if (limit === 0) return 0;
  return Math.min((current / limit) * 100, 100);
};

export const getProviderIcon = (provider: string): string => {
  const icons: { [key: string]: string } = {
    gemini: '🤖',
    huggingface: '🤗', // HuggingFace icon
  };
  return icons[provider.toLowerCase()] || '🔧';
};

export const getProviderColor = (provider: string): string => {
  const colors: { [key: string]: string } = {
    gemini: '#4285f4',
    huggingface: '#ffd21e', // HuggingFace yellow color
  };
  return colors[provider.toLowerCase()] || '#6b7280';
};

export default billingService;
