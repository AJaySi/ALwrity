import axios, { AxiosResponse } from 'axios';
import { emitApiEvent } from '../utils/apiEvents';
import {
  DashboardData,
  UsageStats,
  UsageTrends,
  SubscriptionPlan,
  APIPricing,
  UsageAlert,
  DashboardAPIResponse,
  UsageAPIResponse,
  PlansAPIResponse,
  PricingAPIResponse,
  AlertsAPIResponse,
  DashboardDataSchema,
  UsageStatsSchema,
} from '../types/billing';

// API base configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const billingAPI = axios.create({
  baseURL: `${API_BASE_URL}/api/subscription`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for authentication
billingAPI.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add user ID to ALL requests for billing tracking
    const userId = localStorage.getItem('user_id') || 'demo-user';
    
    // Replace {user_id} in URL if present
    if (config.url?.includes('{user_id}')) {
      config.url = config.url.replace('{user_id}', userId);
    }
    
    // Add user_id as query parameter for billing tracking
    if (config.params) {
      config.params.user_id = userId;
    } else {
      config.params = { user_id: userId };
    }
    
    // Also add as header for additional tracking
    config.headers['X-User-ID'] = userId;
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
billingAPI.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error) => {
    console.error('Billing API Error:', error);
    
    // Handle specific error cases
    if (error.response?.status === 401) {
      // Unauthorized - redirect to login
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    } else if (error.response?.status === 429) {
      // Rate limited
      console.warn('Rate limited by billing API');
    }
    
    return Promise.reject(error);
  }
);

// ------------------------------------------------------------
// Response coercion helpers to ensure required fields exist
// ------------------------------------------------------------

const defaultProviderUsage = { calls: 0, tokens: 0, cost: 0 };

const defaultProviderBreakdown = {
  gemini: { ...defaultProviderUsage },
  openai: { ...defaultProviderUsage },
  anthropic: { ...defaultProviderUsage },
  mistral: { ...defaultProviderUsage },
  tavily: { ...defaultProviderUsage },
  serper: { ...defaultProviderUsage },
  metaphor: { ...defaultProviderUsage },
  firecrawl: { ...defaultProviderUsage },
  stability: { ...defaultProviderUsage },
};

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

function coerceUsageStats(raw: any): UsageStats {
  const coerced: UsageStats = {
    billing_period: raw?.billing_period ?? 'unknown',
    usage_status: (raw?.usage_status ?? 'active') as UsageStats['usage_status'],
    total_calls: Number(raw?.total_calls ?? 0),
    total_tokens: Number(raw?.total_tokens ?? 0),
    total_cost: Number(raw?.total_cost ?? 0),
    avg_response_time: Number(raw?.avg_response_time ?? 0),
    error_rate: Number(raw?.error_rate ?? 0),
    limits: raw?.limits ?? defaultLimits,
    provider_breakdown: raw?.provider_breakdown ?? defaultProviderBreakdown,
    alerts: Array.isArray(raw?.alerts) ? raw.alerts : [],
    usage_percentages: raw?.usage_percentages ?? {
      gemini_calls: 0,
      openai_calls: 0,
      anthropic_calls: 0,
      mistral_calls: 0,
      tavily_calls: 0,
      serper_calls: 0,
      metaphor_calls: 0,
      firecrawl_calls: 0,
      stability_calls: 0,
      cost: 0,
    },
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
      
      const coerced: DashboardData = {
        current_usage: coerceUsageStats(raw?.current_usage ?? raw),
        trends: raw?.trends ?? {
          periods: [],
          total_calls: [],
          total_cost: [],
          total_tokens: [],
          provider_trends: {},
        },
        limits: raw?.limits ?? defaultLimits,
        alerts: Array.isArray(raw?.alerts) ? raw.alerts : [],
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

      // Debug logs removed to reduce console noise

      // Validate response data after coercion
      const validatedData = DashboardDataSchema.parse(coerced);
      // Debug logs removed to reduce console noise
      // Notify app that fresh billing data is available
      emitApiEvent({ url: `/dashboard/${actualUserId}`, method: 'GET', source: 'billing' });
      return validatedData;
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
    openai: '🧠',
    anthropic: '🎭',
    mistral: '🌪️',
    tavily: '🔍',
    serper: '🔎',
    metaphor: '🔮',
    firecrawl: '🕷️',
    stability: '🎨',
  };
  return icons[provider.toLowerCase()] || '🔧';
};

export const getProviderColor = (provider: string): string => {
  const colors: { [key: string]: string } = {
    gemini: '#4285f4',
    openai: '#10a37f',
    anthropic: '#d97706',
    mistral: '#7c3aed',
    tavily: '#059669',
    serper: '#dc2626',
    metaphor: '#7c2d12',
    firecrawl: '#ea580c',
    stability: '#0891b2',
  };
  return colors[provider.toLowerCase()] || '#6b7280';
};

export default billingService;
