import { useState, useEffect, useCallback, useRef } from 'react';
import { blogWriterApi, TaskStatusResponse } from '../services/blogWriterApi';

export interface UsePollingOptions {
  interval?: number; // Polling interval in milliseconds
  maxAttempts?: number; // Maximum number of polling attempts
  onProgress?: (message: string) => void; // Callback for progress updates
  onComplete?: (result: any) => void; // Callback when task completes
  onError?: (error: string) => void; // Callback when task fails
}

export interface UsePollingReturn {
  isPolling: boolean;
  currentStatus: string;
  progressMessages: Array<{ timestamp: string; message: string }>;
  result: any;
  error: string | null;
  startPolling: (taskId: string) => void;
  stopPolling: () => void;
}

export function usePolling(
  pollFunction: (taskId: string) => Promise<TaskStatusResponse>,
  options: UsePollingOptions = {}
): UsePollingReturn {
  const {
    interval = 5000, // 5 seconds default - increased to reduce load
    onProgress,
    onComplete,
    onError
  } = options;

  const [isPolling, setIsPolling] = useState(false);
  const [currentStatus, setCurrentStatus] = useState<string>('idle');
  const [progressMessages, setProgressMessages] = useState<Array<{ timestamp: string; message: string }>>([]);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  // Debug state changes
  useEffect(() => {
    console.log('Polling state changed:', { isPolling, currentStatus, progressCount: progressMessages.length });
  }, [isPolling, currentStatus, progressMessages.length]);


  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const attemptsRef = useRef(0);
  const currentTaskIdRef = useRef<string | null>(null);

  const stopPolling = useCallback(() => {
    console.log('stopPolling called');
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    console.log('Setting isPolling to false');
    setIsPolling(false);
    attemptsRef.current = 0;
    currentTaskIdRef.current = null;
  }, []);

  const startPolling = useCallback((taskId: string) => {
    console.log('startPolling called with taskId:', taskId);
    if (isPolling) {
      console.log('Already polling, stopping first');
      stopPolling();
    }

    currentTaskIdRef.current = taskId;
    console.log('Setting isPolling to true');
    setIsPolling(true);
    setCurrentStatus('pending');
    setProgressMessages([]);
    setResult(null);
    setError(null);
    attemptsRef.current = 0;

    const poll = async () => {
      if (!currentTaskIdRef.current) {
        stopPolling();
        return;
      }

      try {
        const status = await pollFunction(currentTaskIdRef.current);
        console.log('Polling status update:', status);
        setCurrentStatus(status.status);

        // Update progress messages
        if (status.progress_messages && status.progress_messages.length > 0) {
          console.log('Progress messages received:', status.progress_messages);
          console.log('Previous progress messages count:', progressMessages.length);
          setProgressMessages(status.progress_messages);
          console.log('Progress messages state updated to:', status.progress_messages.length, 'messages');
          
          // Call onProgress with the latest message for backward compatibility
          const latestMessage = status.progress_messages[status.progress_messages.length - 1];
          console.log('Latest progress message:', latestMessage.message);
          onProgress?.(latestMessage.message);
        }

        if (status.status === 'completed') {
          console.log('✅ Task completed - stopping polling immediately');
          setResult(status.result);
          onComplete?.(status.result);
          stopPolling();
          return; // Exit early to prevent further processing
        } else if (status.status === 'failed') {
          console.log('❌ Task failed - stopping polling immediately');
          setError(status.error || 'Task failed');
          onError?.(status.error || 'Task failed');
          stopPolling();
          return; // Exit early to prevent further processing
        }

        attemptsRef.current++;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
        console.error('Polling error:', errorMessage);
        
        // Stop polling for task failures and rate limiting
        if (errorMessage.includes('404') || errorMessage.includes('Task not found')) {
          setError('Task not found - it may have expired or been cleaned up');
          onError?.('Task not found - it may have expired or been cleaned up');
          stopPolling();
        } else if (errorMessage.includes('429') || errorMessage.includes('Too Many Requests')) {
          console.warn('Rate limited - stopping polling to prevent further issues');
          setError('Rate limited - please try again later');
          onError?.('Rate limited - please try again later');
          stopPolling();
        }
        // For other errors (timeouts, network issues), continue polling
        // The backend will eventually complete or fail, and we'll catch it
      }
    };

    // Start polling immediately, then at intervals
    poll();
    intervalRef.current = setInterval(poll, interval);
  }, [isPolling, interval, onProgress, onComplete, onError, pollFunction, stopPolling, progressMessages.length]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopPolling();
    };
  }, [stopPolling]);

  return {
    isPolling,
    currentStatus,
    progressMessages,
    result,
    error,
    startPolling,
    stopPolling
  };
}

// Specialized hooks for specific operations
export function useResearchPolling(options: UsePollingOptions = {}) {
  return usePolling(blogWriterApi.pollResearchStatus, options);
}

export function useOutlinePolling(options: UsePollingOptions = {}) {
  return usePolling(blogWriterApi.pollOutlineStatus, options);
}

export function useMediumGenerationPolling(options: UsePollingOptions = {}) {
  // Lazy import to avoid circular: poll function from mediumBlogApi
  const pollFn = (taskId: string) => import('../services/blogWriterApi').then(m => m.mediumBlogApi.pollMediumGeneration(taskId));
  // Wrap to satisfy type
  const wrapped = (taskId: string) => pollFn(taskId) as unknown as Promise<TaskStatusResponse>;
  // eslint-disable-next-line react-hooks/rules-of-hooks
  return usePolling(wrapped, options);
}

export function useRewritePolling(options: UsePollingOptions = {}) {
  // Lazy import to avoid circular: poll function from blogWriterApi
  const pollFn = (taskId: string) => import('../services/blogWriterApi').then(m => m.blogWriterApi.pollRewriteStatus(taskId));
  // Wrap to satisfy type
  const wrapped = (taskId: string) => pollFn(taskId) as unknown as Promise<TaskStatusResponse>;
  // eslint-disable-next-line react-hooks/rules-of-hooks
  return usePolling(wrapped, options);
}
