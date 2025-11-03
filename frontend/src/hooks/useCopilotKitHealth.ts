import { useEffect, useRef, useCallback } from 'react';
import { useCopilotKitHealthContext } from '../contexts/CopilotKitHealthContext';

interface UseCopilotKitHealthOptions {
  /**
   * Initial delay before first health check (milliseconds)
   * @default 1000
   */
  initialDelay?: number;
  /**
   * Interval between health checks when healthy (milliseconds)
   * @default 60000 (1 minute)
   */
  healthyInterval?: number;
  /**
   * Exponential backoff intervals when unhealthy (milliseconds)
   * @default [5000, 10000, 30000, 60000]
   */
  unhealthyIntervals?: number[];
  /**
   * Enable automatic health checking
   * @default true
   */
  enabled?: boolean;
}

/**
 * Hook to monitor CopilotKit health status with automatic polling
 * Uses exponential backoff when unhealthy
 */
export const useCopilotKitHealth = (options: UseCopilotKitHealthOptions = {}) => {
  const {
    initialDelay = 1000,
    healthyInterval = 60000, // 1 minute
    unhealthyIntervals = [5000, 10000, 30000, 60000], // 5s, 10s, 30s, 60s
    enabled = true,
  } = options;

  const {
    isHealthy,
    isChecking,
    lastChecked,
    errorMessage,
    retryCount,
    isAvailable,
    checkHealth,
    markUnhealthy,
  } = useCopilotKitHealthContext();

  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  const scheduleNextCheck = useCallback(() => {
    // Clear any existing timeouts/intervals
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }

    if (!enabled) return;

    // Calculate next check interval based on health status
    let nextInterval: number;
    
    if (isHealthy) {
      // When healthy, use standard interval
      nextInterval = healthyInterval;
    } else {
      // When unhealthy, use exponential backoff
      const intervalIndex = Math.min(retryCount, unhealthyIntervals.length - 1);
      nextInterval = unhealthyIntervals[intervalIndex];
    }

    // Schedule next check
    timeoutRef.current = setTimeout(() => {
      checkHealth();
    }, nextInterval);
  }, [enabled, isHealthy, retryCount, healthyInterval, unhealthyIntervals, checkHealth]);

  // Initial health check on mount
  useEffect(() => {
    if (!enabled) return;

    // Initial delay before first check
    const initialTimeout = setTimeout(() => {
      checkHealth();
    }, initialDelay);

    return () => {
      clearTimeout(initialTimeout);
    };
  }, [enabled, initialDelay, checkHealth]);

  // Schedule next check after health status changes
  useEffect(() => {
    if (!enabled || isChecking) return;

    scheduleNextCheck();

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [enabled, isChecking, scheduleNextCheck]);

  // Also handle CopilotKit runtime errors by listening to window events
  useEffect(() => {
    if (!enabled) return;

    const handleCopilotKitError = (event: Event) => {
      // Check if this is a CopilotKit-related error
      const errorEvent = event as ErrorEvent;
      if (
        errorEvent.message?.includes('copilotkit') ||
        errorEvent.message?.includes('CopilotKit') ||
        errorEvent.filename?.includes('copilotkit')
      ) {
        markUnhealthy(`Runtime error: ${errorEvent.message}`);
      }
    };

    window.addEventListener('error', handleCopilotKitError);
    window.addEventListener('unhandledrejection', (event) => {
      const reason = event.reason;
      if (
        typeof reason === 'string' && (
          reason.includes('copilotkit') ||
          reason.includes('CopilotKit') ||
          reason.includes('ERR_CERT_COMMON_NAME_INVALID') ||
          reason.includes('CORS')
        )
      ) {
        markUnhealthy(`Unhandled promise rejection: ${reason}`);
      }
    });

    return () => {
      window.removeEventListener('error', handleCopilotKitError);
    };
  }, [enabled, markUnhealthy]);

  return {
    isHealthy,
    isAvailable,
    isChecking,
    lastChecked,
    errorMessage,
    retryCount,
    checkHealth,
    markUnhealthy,
  };
};

