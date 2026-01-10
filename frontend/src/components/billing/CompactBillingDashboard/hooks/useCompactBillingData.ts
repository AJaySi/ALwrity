import { useState, useEffect, useMemo } from 'react';
import { DashboardData } from '../../../../types/billing';
import { SystemHealth } from '../../../../types/monitoring';
import { billingService } from '../../../../services/billingService';
import { monitoringService } from '../../../../services/monitoringService';
import { onApiEvent } from '../../../../utils/apiEvents';
import { showToastNotification } from '../../../../utils/toastNotifications';

interface UseCompactBillingDataReturn {
  dashboardData: DashboardData | null;
  systemHealth: SystemHealth | null;
  loading: boolean;
  error: string | null;
  lastRefreshTime: Date | null;
  healthError: string | null;
  sparklineData: {
    cost: Array<{ date: string; value: number }>;
    calls: Array<{ date: string; value: number }>;
    tokens: Array<{ date: string; value: number }>;
  };
  refresh: (showSuccessToast?: boolean) => Promise<void>;
}

/**
 * Custom hook for managing CompactBillingDashboard data fetching and state
 */
export const useCompactBillingData = (userId?: string): UseCompactBillingDataReturn => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefreshTime, setLastRefreshTime] = useState<Date | null>(null);
  const [healthError, setHealthError] = useState<string | null>(null);

  const fetchData = async (showSuccessToast: boolean = false) => {
    try {
      setLoading(true);
      setError(null);
      
      // Use Promise.allSettled to prevent health check timeout from blocking dashboard
      const results = await Promise.allSettled([
        billingService.getDashboardData(userId),
        monitoringService.getSystemHealth()
      ]);
      
      // Handle billing data (required)
      if (results[0].status === 'fulfilled') {
        setDashboardData(results[0].value);
        setLastRefreshTime(new Date());
        setError(null); // Clear any previous errors
      } else {
        // Billing data is critical - show error
        const errorMessage = results[0].reason instanceof Error 
          ? results[0].reason.message 
          : 'Failed to fetch data';
        setError(errorMessage);
        showToastNotification(
          `Unable to fetch latest billing data: ${errorMessage}. Showing last known values.`,
          'error',
          { duration: 7000 }
        );
        setLoading(false);
        return;
      }
      
      // Handle health data (optional - don't block dashboard if it fails)
      if (results[1].status === 'fulfilled') {
        setSystemHealth(results[1].value);
        setHealthError(null); // Clear health error on success
      } else {
        // Health check failed - keep last successful value, show error toast
        const healthErrorMessage = results[1].reason instanceof Error
          ? results[1].reason.message
          : 'System health check timed out or failed';
        setHealthError(healthErrorMessage);
        showToastNotification(
          `Unable to fetch latest system health data: ${healthErrorMessage}. Showing last known values.`,
          'warning',
          { duration: 6000 }
        );
        // Don't update systemHealth - keep last successful value
        // Only set to null if we never had a successful fetch
        if (!systemHealth) {
          setSystemHealth(null);
        }
      }
      
      // Show success toast only if explicitly requested (user-initiated refresh)
      if (showSuccessToast && results[0].status === 'fulfilled' && results[1].status === 'fulfilled') {
        showToastNotification(
          'Billing data refreshed successfully',
          'success',
          { duration: 3000 }
        );
      } else if (showSuccessToast && results[0].status === 'fulfilled' && results[1].status === 'rejected') {
        showToastNotification(
          'Billing data refreshed, but system health check failed',
          'warning',
          { duration: 4000 }
        );
      }
    } catch (err) {
      // Fallback error handling (shouldn't reach here with allSettled)
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch data';
      setError(errorMessage);
      showToastNotification(errorMessage, 'error', { duration: 5000 });
    } finally {
      setLoading(false);
    }
  };

  // Initial fetch
  useEffect(() => {
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]);

  // Event-driven refresh
  useEffect(() => {
    const lastRefreshRef = { current: 0 } as { current: number };
    const MIN_REFRESH_INTERVAL_MS = 4000;
    const unsubscribe = onApiEvent((detail) => {
      // Only react to non-billing/monitoring events to avoid feedback loops
      if (detail.source && detail.source !== 'other') return;
      const now = Date.now();
      if (now - lastRefreshRef.current < MIN_REFRESH_INTERVAL_MS) return;
      lastRefreshRef.current = now;
      Promise.allSettled([billingService.getDashboardData(userId), monitoringService.getSystemHealth()])
        .then((results) => {
          if (results[0].status === 'fulfilled') {
            setDashboardData(results[0].value);
            setLastRefreshTime(new Date());
            setError(null);
          }
          if (results[1].status === 'fulfilled') {
            setSystemHealth(results[1].value);
            setHealthError(null);
          } else {
            // Keep last successful health value, don't set fake defaults
            const healthErrorMessage = results[1].reason instanceof Error
              ? results[1].reason.message
              : 'System health check failed';
            setHealthError(healthErrorMessage);
            // Don't update systemHealth - keep last successful value
          }
        })
        .catch(() => {/* ignore */});
    });
    return unsubscribe;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Prepare sparkline data for last 7 days (or available data)
  const sparklineData = useMemo(() => {
    if (!dashboardData || !dashboardData.trends || !dashboardData.trends.periods || dashboardData.trends.periods.length === 0) {
      return {
        cost: [],
        calls: [],
        tokens: []
      };
    }
    
    const { trends } = dashboardData;

    // Get last 7 periods (or all if less than 7)
    const last7Periods = trends.periods.slice(-7);
    const last7Costs = trends.total_cost.slice(-7);
    const last7Calls = trends.total_calls.slice(-7);
    const last7Tokens = trends.total_tokens.slice(-7);

    return {
      cost: last7Periods.map((period, index) => ({
        date: period,
        value: last7Costs[index] || 0
      })),
      calls: last7Periods.map((period, index) => ({
        date: period,
        value: last7Calls[index] || 0
      })),
      tokens: last7Periods.map((period, index) => ({
        date: period,
        value: (last7Tokens[index] || 0) / 1000 // Convert to thousands
      }))
    };
  }, [dashboardData]);

  return {
    dashboardData,
    systemHealth,
    loading,
    error,
    lastRefreshTime,
    healthError,
    sparklineData,
    refresh: fetchData
  };
};
