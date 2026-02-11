/**
 * Usage Service
 * Handles usage statistics, trends, and logs with validation
 */

import axios from 'axios';
import { billingAPI } from './api';
import { 
  UsageStats,
  UsageLogsResponse,
  UsageTrends,
  UsageAPIResponse,
  TrendsAPIResponse,
  DashboardData,
  DashboardAPIResponse,
  DashboardDataSchema
} from './types';
import { validateBillingPeriod } from './utils';
import { emitApiEvent } from '../../utils/apiEvents';

/**
 * Get comprehensive dashboard data for a user
 */
export const getDashboardData = async (userId?: string): Promise<DashboardData> => {
  try {
    const actualUserId = userId || localStorage.getItem('user_id') || 'demo-user';
    
    const response = await billingAPI.get<DashboardAPIResponse>(`/dashboard/${actualUserId}`);
    
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to fetch dashboard data');
    }
    
    // Validate response data with proper type casting
    const validatedData = DashboardDataSchema.parse(response.data.data) as DashboardData;
    emitApiEvent({ url: `/dashboard/${actualUserId}`, method: 'GET', source: 'billing' });
    return validatedData;
  } catch (error) {
    console.error('Error fetching dashboard data:', error);
    throw error;
  }
};

/**
 * Get current usage statistics for a user
 */
export const getUsageStats = async (userId?: string, period?: string): Promise<UsageStats> => {
  try {
    const actualUserId = userId || localStorage.getItem('user_id') || 'demo-user';
    const params = period ? { billing_period: period } : {};
    
    const response = await billingAPI.get<UsageAPIResponse>(`/usage/${actualUserId}`, { params });
    
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to fetch usage stats');
    }
    
    emitApiEvent({ url: `/usage/${actualUserId}`, method: 'GET', source: 'billing' });
    return response.data.data;
  } catch (error) {
    console.error('Error fetching usage stats:', error);
    throw error;
  }
};

/**
 * Get usage trends over time
 */
export const getUsageTrends = async (userId?: string, months: number = 6): Promise<UsageTrends> => {
  try {
    const actualUserId = userId || localStorage.getItem('user_id') || 'demo-user';
    const response = await billingAPI.get<TrendsAPIResponse>(`/usage/${actualUserId}/trends`, {
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
};

/**
 * Get API usage logs for current user with billing period validation
 */
export const getUsageLogs = async (
  limit: number = 50,
  offset: number = 0,
  provider?: string,
  statusCode?: number,
  billingPeriod?: string
): Promise<UsageLogsResponse> => {
  try {
    // Validate billing period format if provided
    if (billingPeriod && !validateBillingPeriod(billingPeriod)) {
      throw new Error('Billing period must be in YYYY-MM format (e.g., 2026-02)');
    }

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
};

// Export validateBillingPeriod for use in other services
export { validateBillingPeriod };

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
