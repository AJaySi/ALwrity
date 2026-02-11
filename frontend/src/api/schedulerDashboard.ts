/**
 * Scheduler Dashboard API Client
 * Provides typed functions for fetching scheduler dashboard data.
 */

import { apiClient } from './client';

// TypeScript interfaces for scheduler dashboard data
export interface SchedulerStats {
  total_checks: number;
  tasks_found: number;
  tasks_executed: number;
  tasks_failed: number;
  tasks_skipped: number;
  last_check: string | null;
  last_update: string | null;
  active_executions: number;
  running: boolean;
  check_interval_minutes: number;
  min_check_interval_minutes: number;
  max_check_interval_minutes: number;
  intelligent_scheduling: boolean;
  active_strategies_count: number;
  last_interval_adjustment: string | null;
  registered_types: string[];
  // Cumulative/historical values from database
  cumulative_total_check_cycles: number;
  cumulative_tasks_found: number;
  cumulative_tasks_executed: number;
  cumulative_tasks_failed: number;
}

export interface SchedulerJob {
  id: string;
  trigger_type: string;
  next_run_time: string | null;
  user_id: string | null;
  job_store: string;
  user_job_store: string;
  function_name?: string | null;
  platform?: string; // For OAuth token monitoring tasks and platform insights
  task_id?: number; // For OAuth token monitoring tasks, website analysis, and platform insights
  is_database_task?: boolean; // Flag to indicate DB task vs APScheduler job
  frequency?: string; // For OAuth tasks (e.g., 'Weekly')
  task_type?: string; // For website analysis tasks ('user_website' or 'competitor')
  task_category?: string; // 'website_analysis', 'platform_insights', 'oauth_token_monitoring'
  website_url?: string | null; // For website analysis tasks
  competitor_id?: number | null; // For competitor website analysis tasks
}

export interface UserIsolation {
  enabled: boolean;
  current_user_id: string | null;
}

export interface SchedulerDashboardData {
  stats: SchedulerStats;
  jobs: SchedulerJob[];
  job_count: number;
  recurring_jobs: number;
  one_time_jobs: number;
  user_isolation: UserIsolation;
  last_updated: string;
}

export interface TaskFailurePattern {
  consecutive_failures: number;
  recent_failures: number;
  failure_reason: string;
  last_failure_time: string | null;
  error_patterns: string[];
}

export interface TaskNeedingIntervention {
  task_id: number;
  task_type: string;
  user_id: string;
  platform?: string;
  website_url?: string;
  failure_pattern: TaskFailurePattern;
  failure_reason: string | null;
  last_failure: string | null;
}

export interface TaskInfo {
  id: number;
  task_title: string;
  component_name: string;
  metric: string;
  frequency: string;
}

export interface ExecutionLog {
  id: number;
  task_id: number | null;
  user_id: number | string | null;
  execution_date: string;
  status: 'success' | 'failed' | 'running' | 'skipped';
  error_message: string | null;
  execution_time_ms: number | null;
  result_data: any;
  created_at: string;
  task?: TaskInfo;
  is_scheduler_log?: boolean; // Flag for scheduler logs vs execution logs
  event_type?: string;
  job_id?: string | null;
}

export interface ExecutionLogsResponse {
  logs: ExecutionLog[];
  total_count: number;
  limit: number;
  offset: number;
  has_more: boolean;
  is_scheduler_logs?: boolean; // Flag to indicate if these are scheduler logs
}

export interface SchedulerJobsResponse {
  jobs: SchedulerJob[];
  total_jobs: number;
  recurring_jobs: number;
  one_time_jobs: number;
}

export interface SchedulerEvent {
  id: number;
  event_type: 'check_cycle' | 'interval_adjustment' | 'start' | 'stop' | 'job_scheduled' | 'job_cancelled' | 'job_completed' | 'job_failed';
  event_date: string | null;
  check_cycle_number: number | null;
  check_interval_minutes: number | null;
  previous_interval_minutes: number | null;
  new_interval_minutes: number | null;
  tasks_found: number | null;
  tasks_executed: number | null;
  tasks_failed: number | null;
  tasks_by_type: Record<string, number> | null;
  check_duration_seconds: number | null;
  active_strategies_count: number | null;
  active_executions: number | null;
  job_id: string | null;
  job_type: string | null;
  user_id: string | null;
  event_data: any;
  error_message: string | null;
  created_at: string | null;
}

export interface SchedulerEventHistoryResponse {
  events: SchedulerEvent[];
  total_count: number;
  limit: number;
  offset: number;
  has_more: boolean;
  date_filter?: {
    days: number;
    cutoff_date: string;
    showing_events_since: string;
  };
}

/**
 * Get scheduler dashboard statistics and current state.
 */
export const getSchedulerDashboard = async (): Promise<SchedulerDashboardData> => {
  try {
    const response = await apiClient.get<SchedulerDashboardData>('/api/scheduler/dashboard');
    return response.data;
  } catch (error: any) {
    console.error('Error fetching scheduler dashboard:', error);
    throw new Error(
      error.response?.data?.detail || 
      error.message || 
      'Failed to fetch scheduler dashboard'
    );
  }
};

/**
 * Get task execution logs from database.
 * 
 * @param limit - Number of logs to return (1-500, default: 50)
 * @param offset - Pagination offset (default: 0)
 * @param status - Filter by status (success, failed, running, skipped)
 */
export const getExecutionLogs = async (
  limit: number = 50,
  offset: number = 0,
  status?: 'success' | 'failed' | 'running' | 'skipped'
): Promise<ExecutionLogsResponse> => {
  try {
    const params: any = { limit, offset };
    if (status) {
      params.status = status;
    }
    
    const response = await apiClient.get<ExecutionLogsResponse | { logs: any[], pagination: any }>('/api/scheduler/execution-logs', {
      params
    });
    
    const data = response.data;
    
    // Handle both old (flat) and new (nested) pagination formats
    if ('pagination' in data) {
      // New format: { logs: [], pagination: { limit, offset, total, has_more } }
      return {
        logs: data.logs,
        total_count: data.pagination.total,
        limit: data.pagination.limit,
        offset: data.pagination.offset,
        has_more: data.pagination.has_more
      };
    } else {
      // Old format: { logs: [], total_count, limit, offset, has_more }
      return data as ExecutionLogsResponse;
    }
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
 * Get detailed information about all scheduled jobs.
 */
export const getSchedulerJobs = async (): Promise<SchedulerJobsResponse> => {
  try {
    const response = await apiClient.get<SchedulerJobsResponse>('/api/scheduler/jobs');
    return response.data;
  } catch (error: any) {
    console.error('Error fetching scheduler jobs:', error);
    throw new Error(
      error.response?.data?.detail || 
      error.message || 
      'Failed to fetch scheduler jobs'
    );
  }
};

/**
 * Get scheduler event history from database.
 * 
 * @param limit - Number of events to return (1-500, default: 5 for initial load, expand to 50 on hover)
 * @param offset - Pagination offset (default: 0)
 * @param eventType - Filter by event type (check_cycle, interval_adjustment, start, stop, etc.)
 * @param days - Number of days to look back (1-90, default: 7 days)
 */
export const getSchedulerEventHistory = async (
  limit: number = 5,
  offset: number = 0,
  eventType?: 'check_cycle' | 'interval_adjustment' | 'start' | 'stop' | 'job_scheduled' | 'job_cancelled' | 'job_completed' | 'job_failed',
  days: number = 7
): Promise<SchedulerEventHistoryResponse> => {
  try {
    const params: any = { limit, offset, days };
    if (eventType) {
      params.event_type = eventType;
    }
    
    const response = await apiClient.get<SchedulerEventHistoryResponse | { events: any[], pagination: any }>('/api/scheduler/event-history', {
      params
    });
    
    const data = response.data;
    
    // Handle both old (flat) and new (nested) pagination formats
    if ('pagination' in data) {
      // New format: { events: [], pagination: { limit, offset, total, has_more } }
      return {
        events: data.events,
        total_count: data.pagination.total,
        limit: data.pagination.limit,
        offset: data.pagination.offset,
        has_more: data.pagination.has_more
      };
    } else {
      // Old format: { events: [], total_count, limit, offset, has_more }
      return data as SchedulerEventHistoryResponse;
    }
  } catch (error: any) {
    console.error('Error fetching scheduler event history:', error);
    throw new Error(
      error.response?.data?.detail || 
      error.message || 
      'Failed to fetch scheduler event history'
    );
  }
};

/**
 * Get recent scheduler logs (restoration, job scheduling, etc.) formatted as execution logs.
 * These are shown in Execution Logs section when actual execution logs are not available.
 * Returns only the latest 5 logs (rolling window).
 */
export const getRecentSchedulerLogs = async (): Promise<ExecutionLogsResponse> => {
  try {
    const response = await apiClient.get<ExecutionLogsResponse | { logs: any[], pagination: any }>('/api/scheduler/recent-scheduler-logs');
    
    const data = response.data;
    
    // Handle both old (flat) and new (nested) pagination formats
    if ('pagination' in data) {
      // New format: { logs: [], pagination: { limit, offset, total, has_more } }
      return {
        logs: data.logs,
        total_count: data.pagination.total,
        limit: data.pagination.limit,
        offset: data.pagination.offset,
        has_more: data.pagination.has_more
      };
    } else {
      // Old format: { logs: [], total_count, limit, offset, has_more }
      return data as ExecutionLogsResponse;
    }
  } catch (error: any) {
    console.error('Error fetching recent scheduler logs:', error);
    throw new Error(
      error.response?.data?.detail || 
      error.message || 
      'Failed to fetch recent scheduler logs'
    );
  }
};

/**
 * Get tasks that require manual intervention for a user.
 */
export const getTasksNeedingIntervention = async (userId: string): Promise<TaskNeedingIntervention[]> => {
  try {
    const response = await apiClient.get<{
      success: boolean;
      tasks: TaskNeedingIntervention[];
      count: number;
    }>(`/api/scheduler/tasks-needing-intervention/${userId}`);

    if (!response.data.success) {
      throw new Error('Failed to fetch tasks needing intervention');
    }

    return response.data.tasks || [];
  } catch (error: any) {
    console.error('Error fetching tasks needing intervention:', error);
    throw new Error(
      error.response?.data?.detail ||
      error.message ||
      'Failed to fetch tasks needing intervention'
    );
  }
};

// Event log management interfaces
export interface EventLogCleanupResult {
  success: boolean;
  message: string;
  statistics: {
    total_before_cleanup: number;
    deleted_count: number;
    total_after_cleanup: number;
    retention_days: number;
    cutoff_date: string;
  };
}

export interface EventLogStats {
  total_records: number;
  retention_policy: {
    recommended_days: number;
    minimum_days: number;
    maximum_days: number;
  };
  age_distribution: {
    last_24h: number;
    last_7d: number;
    last_30d: number;
    last_90d: number;
    older_than_90d: number;
    older_than_180d: number;
  };
  event_type_distribution: Record<string, number>;
}

/**
 * Clean up old scheduler event logs based on retention policy.
 */
export const cleanupSchedulerEventLogs = async (daysToKeep: number = 90): Promise<EventLogCleanupResult> => {
  try {
    const response = await apiClient.post<EventLogCleanupResult>('/api/scheduler/cleanup-event-logs', null, {
      params: { days_to_keep: daysToKeep }
    });
    return response.data;
  } catch (error: any) {
    console.error('Error cleaning up scheduler event logs:', error);
    throw new Error(
      error.response?.data?.detail ||
      error.message ||
      'Failed to cleanup scheduler event logs'
    );
  }
};

/**
 * Get statistics about scheduler event logs for monitoring retention.
 */
export const getSchedulerEventLogsStats = async (): Promise<EventLogStats> => {
  try {
    const response = await apiClient.get<EventLogStats>('/api/scheduler/event-logs/stats');
    return response.data;
  } catch (error: any) {
    console.error('Error fetching scheduler event log statistics:', error);
    throw new Error(
      error.response?.data?.detail ||
      error.message ||
      'Failed to fetch scheduler event log statistics'
    );
  }
};
