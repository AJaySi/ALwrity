import { useEffect, useRef } from 'react';
import { useAuth } from '@clerk/clerk-react';
import { apiClient } from '../api/client';
import { showToastNotification } from '../utils/toastNotifications';

/**
 * Hook to poll for tasks needing intervention and show toast notifications
 */
export function useSchedulerTaskAlerts(options: {
  enabled?: boolean;
  interval?: number;
} = {}) {
  const { enabled = true, interval = 60000 } = options;
  const { userId, getToken } = useAuth();
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const lastAlertTimeRef = useRef<number>(0);
  const isPollingRef = useRef(false);
  const shownTaskIdsRef = useRef<Set<number>>(new Set());

  useEffect(() => {
    if (!enabled || !userId) {
      return;
    }

    const pollAlerts = async () => {
      if (isPollingRef.current) {
        return;
      }

      try {
        isPollingRef.current = true;

        // Fetch tasks needing intervention
        const response = await apiClient.get<{
          success: boolean;
          tasks: Array<{
            task_id: number;
            task_type: string;
            user_id: string;
            platform?: string;
            website_url?: string;
            failure_pattern: {
              consecutive_failures: number;
              recent_failures: number;
              failure_reason: string;
              last_failure_time: string | null;
              error_patterns: string[];
            };
            failure_reason: string | null;
            last_failure: string | null;
          }>;
          count: number;
        }>(`/api/scheduler/tasks-needing-intervention/${userId}`);

        if (!response.data.success) {
          return;
        }

        const tasks = response.data.tasks || [];

        // Show toast only for critical failures (API limits) - other failures are shown in dedicated section
        for (const task of tasks) {
          // Only show alert once per task
          if (shownTaskIdsRef.current.has(task.task_id)) {
            continue;
          }

          // Only show toast for critical failures (API limits) and if failure is very recent (within last 10 minutes)
          const failureReason = task.failure_pattern?.failure_reason || 'unknown';
          if (task.last_failure && failureReason === 'api_limit') {
            const failureTime = new Date(task.last_failure).getTime();
            const tenMinutesAgo = Date.now() - 10 * 60 * 1000;
            
            if (failureTime > tenMinutesAgo) {
              showTaskAlert(task);
              shownTaskIdsRef.current.add(task.task_id);
              lastAlertTimeRef.current = Math.max(
                lastAlertTimeRef.current,
                failureTime
              );
            }
          }
        }
      } catch (error) {
        console.error('Error polling scheduler task alerts:', error);
        // Don't show error to user - this is background polling
      } finally {
        isPollingRef.current = false;
      }
    };

    // Poll immediately
    pollAlerts();

    // Set up periodic polling
    intervalRef.current = setInterval(pollAlerts, interval);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [enabled, userId, interval]);

  return {
    isPolling: isPollingRef.current
  };
}

function showTaskAlert(task: {
  task_id: number;
  task_type: string;
  platform?: string;
  website_url?: string;
  failure_pattern: {
    consecutive_failures: number;
    failure_reason: string;
  };
}) {
  const failureReason = task.failure_pattern?.failure_reason || 'unknown';
  const consecutiveFailures = task.failure_pattern?.consecutive_failures || 0;

  let message = '';
  let type: 'error' | 'warning' = 'error';

  if (failureReason === 'api_limit') {
    message = `Task "${getTaskDisplayName(task)}" has failed ${consecutiveFailures} times due to API limits. Manual intervention required.`;
    type = 'error';
  } else if (failureReason === 'auth_error') {
    message = `Task "${getTaskDisplayName(task)}" has failed ${consecutiveFailures} times due to authentication issues. Please check your credentials.`;
    type = 'warning';
  } else {
    message = `Task "${getTaskDisplayName(task)}" has failed ${consecutiveFailures} times and needs manual intervention.`;
    type = 'error';
  }

  // Use existing toast function
  showToastNotification(message, type);
}

function getTaskDisplayName(task: {
  task_type: string;
  platform?: string;
  website_url?: string;
}): string {
  if (task.task_type === 'oauth_token_monitoring') {
    return `OAuth ${task.platform?.toUpperCase() || 'Unknown'}`;
  } else if (task.task_type === 'website_analysis') {
    const url = task.website_url || 'Unknown';
    return `Website Analysis (${url.length > 30 ? url.substring(0, 30) + '...' : url})`;
  } else if (task.task_type.includes('_insights')) {
    return `${task.platform?.toUpperCase() || 'Unknown'} Insights`;
  }
  return task.task_type;
}

