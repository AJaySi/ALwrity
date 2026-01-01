/**
 * Custom hook for polling render task status
 */

import { useEffect, useRef, useState } from 'react';
import { youtubeApi, type TaskStatus } from '../../../services/youtubeApi';
import { POLLING_INTERVAL_MS } from '../constants';

interface UseRenderPollingResult {
  renderStatus: TaskStatus | null;
  renderProgress: number;
  error: string | null;
}

export const useRenderPolling = (
  renderTaskId: string | null,
  onSuccess?: () => void,
  onError?: (error: string) => void
): UseRenderPollingResult => {
  const [renderStatus, setRenderStatus] = useState<TaskStatus | null>(null);
  const [renderProgress, setRenderProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    // Clear any existing interval
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    if (!renderTaskId) {
      return;
    }

    // Start polling
    const interval = setInterval(async () => {
      try {
        const status = await youtubeApi.getRenderStatus(renderTaskId);
        
        // Handle null response (task not found) - matches podcast pattern
        if (!status) {
          console.warn(`[YouTubeCreator] Task ${renderTaskId} not found, stopping polling`);
          if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
          }
          const errorMessage = 'Render task not found. This may happen if the server restarted or the task expired. Please try rendering again.';
          setError(errorMessage);
          onError?.(errorMessage);
          return;
        }
        
        setRenderStatus(status);
        setRenderProgress(status.progress || 0);

        // Stop polling if task is completed or failed
        if (status.status === 'completed' || status.status === 'failed') {
          console.log(`[YouTubeCreator] Task ${renderTaskId} finished with status: ${status.status}`);
          
          // Clear interval immediately
          if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
          }
          
          if (status.status === 'completed') {
            onSuccess?.();
          } else if (status.status === 'failed') {
            // Extract error message from status
            const errorMessage = status.error || 
                               status.message || 
                               (typeof status.result === 'object' && status.result?.error) ||
                               'Video rendering failed. Please try again.';
            setError(errorMessage);
            onError?.(errorMessage);
            console.error(`[YouTubeCreator] Render task failed:`, status);
          }
          return;
        }
      } catch (err: any) {
        console.error('Failed to poll render status:', err);
        
        // Handle 404 - task not found
        const is404 = err.response?.status === 404 || 
                     err.message?.includes('Task not found') ||
                     err.response?.data?.detail?.error === 'Task not found';
        
        if (is404) {
          console.warn(`[YouTubeCreator] Task ${renderTaskId} not found, stopping polling`);
          if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
          }
          const errorDetail = err.response?.data?.detail;
          const errorMessage = errorDetail?.message || 
                             errorDetail?.error || 
                             'Render task not found. This may happen if the server restarted or the task expired. Please try rendering again.';
          setError(errorMessage);
          onError?.(errorMessage);
          return;
        }
        
        // For 500 errors (server errors), stop polling
        const is500 = err.response?.status === 500;
        if (is500) {
          console.error(`[YouTubeCreator] Server error while polling, stopping`);
          if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
          }
          const errorMessage = 'Server error occurred while checking render status. Please try rendering again.';
          setError(errorMessage);
          onError?.(errorMessage);
          return;
        }
        
        // For other errors, continue polling but log them
        console.warn(`[YouTubeCreator] Polling error (non-critical), will retry:`, err.message);
      }
    }, POLLING_INTERVAL_MS);

    intervalRef.current = interval;

    // Cleanup function
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [renderTaskId, onSuccess, onError]);

  return {
    renderStatus,
    renderProgress,
    error,
  };
};

