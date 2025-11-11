/**
 * Website Analysis Monitoring API Client
 * Provides typed functions for fetching website analysis monitoring data.
 */

import { apiClient } from './client';

// TypeScript interfaces
export interface WebsiteAnalysisTask {
  id: number;
  website_url: string;
  task_type: 'user_website' | 'competitor';
  competitor_id: string | null;
  status: 'active' | 'failed' | 'paused';
  last_check: string | null;
  last_success: string | null;
  last_failure: string | null;
  failure_reason: string | null;
  next_check: string | null;
  frequency_days: number;
  created_at: string;
  updated_at: string;
}

export interface WebsiteAnalysisStatusResponse {
  success: boolean;
  data: {
    user_id: string;
    user_website_tasks: WebsiteAnalysisTask[];
    competitor_tasks: WebsiteAnalysisTask[];
    total_tasks: number;
    active_tasks: number;
    failed_tasks: number;
  };
}

export interface WebsiteAnalysisExecutionLog {
  id: number;
  task_id: number;
  website_url: string;
  task_type: 'user_website' | 'competitor';
  execution_date: string;
  status: 'success' | 'failed' | 'running' | 'skipped';
  result_data: any;
  error_message: string | null;
  execution_time_ms: number | null;
  created_at: string;
}

export interface WebsiteAnalysisLogsResponse {
  logs: WebsiteAnalysisExecutionLog[];
  total_count: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

export interface RetryWebsiteAnalysisResponse {
  success: boolean;
  message: string;
  task: {
    id: number;
    website_url: string;
    status: string;
    next_check: string | null;
  };
}

/**
 * Get website analysis status for a user
 */
export const getWebsiteAnalysisStatus = async (
  userId: string
): Promise<WebsiteAnalysisStatusResponse> => {
  try {
    const response = await apiClient.get(`/api/scheduler/website-analysis/status/${userId}`);
    return response.data;
  } catch (error: any) {
    console.error('Error fetching website analysis status:', error);
    throw new Error(error.response?.data?.detail || 'Failed to fetch website analysis status');
  }
};

/**
 * Get execution logs for website analysis tasks
 */
export const getWebsiteAnalysisLogs = async (
  userId: string,
  limit: number = 10,
  offset: number = 0,
  taskId?: number
): Promise<WebsiteAnalysisLogsResponse> => {
  try {
    const params: any = { limit, offset };
    if (taskId) {
      params.task_id = taskId;
    }
    const response = await apiClient.get(`/api/scheduler/website-analysis/logs/${userId}`, {
      params
    });
    return response.data;
  } catch (error: any) {
    console.error('Error fetching website analysis logs:', error);
    throw new Error(error.response?.data?.detail || 'Failed to fetch website analysis logs');
  }
};

/**
 * Manually retry a failed website analysis task
 */
export const retryWebsiteAnalysis = async (
  taskId: number
): Promise<RetryWebsiteAnalysisResponse> => {
  try {
    const response = await apiClient.post(`/api/scheduler/website-analysis/retry/${taskId}`);
    return response.data;
  } catch (error: any) {
    console.error('Error retrying website analysis:', error);
    throw new Error(error.response?.data?.detail || 'Failed to retry website analysis');
  }
};

