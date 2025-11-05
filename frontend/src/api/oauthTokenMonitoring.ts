/**
 * OAuth Token Monitoring API Client
 * Functions for interacting with OAuth token monitoring endpoints
 */

import { apiClient } from './client';

export interface OAuthTokenStatus {
  connected: boolean;
  monitoring_task: {
    id: number | null;
    status: string;
    last_check: string | null;
    last_success: string | null;
    last_failure: string | null;
    failure_reason: string | null;
    next_check: string | null;
  } | null;
}

export interface PlatformStatus {
  [platform: string]: OAuthTokenStatus;
}

export interface OAuthTokenStatusResponse {
  success: boolean;
  data: {
    user_id: string;
    platform_status: PlatformStatus;
    connected_platforms: string[];
  };
}

export interface ManualRefreshResponse {
  success: boolean;
  message: string;
  data: {
    platform: string;
    status: string;
    last_check: string | null;
    last_success: string | null;
    last_failure: string | null;
    failure_reason: string | null;
    next_check: string | null;
    execution_result: {
      success: boolean;
      error_message: string | null;
      execution_time_ms: number | null;
      result_data: any;
    };
  };
}

export interface ExecutionLog {
  id: number;
  task_id: number;
  platform: string;
  execution_date: string;
  status: string;
  result_data: any;
  error_message: string | null;
  execution_time_ms: number | null;
  created_at: string;
}

export interface ExecutionLogsResponse {
  success: boolean;
  data: {
    logs: ExecutionLog[];
    total_count: number;
    limit: number;
    offset: number;
  };
}

export interface CreateTasksResponse {
  success: boolean;
  message: string;
  data: {
    tasks_created: number;
    tasks: Array<{
      id: number;
      platform: string;
      status: string;
      next_check: string | null;
    }>;
  };
}

/**
 * Get OAuth token monitoring status for all platforms
 */
export const getOAuthTokenStatus = async (userId: string): Promise<OAuthTokenStatusResponse> => {
  try {
    const response = await apiClient.get<OAuthTokenStatusResponse>(`/api/oauth-tokens/status/${userId}`);
    return response.data;
  } catch (error: any) {
    console.error('Error fetching OAuth token status:', error);
    throw new Error(
      error.response?.data?.detail || 
      error.message || 
      'Failed to fetch OAuth token status'
    );
  }
};

/**
 * Manually trigger token refresh for a specific platform
 */
export const manualRefreshToken = async (
  userId: string, 
  platform: string
): Promise<ManualRefreshResponse> => {
  try {
    const response = await apiClient.post<ManualRefreshResponse>(
      `/api/oauth-tokens/refresh/${userId}/${platform}`
    );
    return response.data;
  } catch (error: any) {
    console.error('Error manually refreshing token:', error);
    throw new Error(
      error.response?.data?.detail || 
      error.message || 
      'Failed to refresh token'
    );
  }
};

/**
 * Get execution logs for OAuth token monitoring
 */
export const getOAuthTokenExecutionLogs = async (
  userId: string,
  platform?: string,
  limit: number = 50,
  offset: number = 0
): Promise<ExecutionLogsResponse> => {
  try {
    const params: any = { limit, offset };
    if (platform) {
      params.platform = platform;
    }
    
    const response = await apiClient.get<ExecutionLogsResponse>(
      `/api/oauth-tokens/execution-logs/${userId}`,
      { params }
    );
    return response.data;
  } catch (error: any) {
    console.error('Error fetching execution logs:', error);
    throw new Error(
      error.response?.data?.detail || 
      error.message || 
      'Failed to fetch execution logs'
    );
  }
};

/**
 * Create OAuth token monitoring tasks
 */
export const createOAuthMonitoringTasks = async (
  userId: string,
  platforms?: string[]
): Promise<CreateTasksResponse> => {
  try {
    const response = await apiClient.post<CreateTasksResponse>(
      `/api/oauth-tokens/create-tasks/${userId}`,
      platforms ? { platforms } : {}
    );
    return response.data;
  } catch (error: any) {
    console.error('Error creating monitoring tasks:', error);
    throw new Error(
      error.response?.data?.detail || 
      error.message || 
      'Failed to create monitoring tasks'
    );
  }
};

