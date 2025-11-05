/**
 * Scheduler Dashboard Page
 * Main page displaying scheduler status, jobs, execution logs, and insights.
 * Terminal-themed UI with high readability.
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Box,
  Container,
  Typography,
  IconButton,
  Tooltip,
  Alert,
  CircularProgress,
  Chip
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Schedule as ScheduleIcon,
  CheckCircle as CheckCircleIcon,
  PlayArrow as PlayArrowIcon,
  Pause as PauseIcon,
  TrendingUp as TrendingUpIcon,
  AccessTime as AccessTimeIcon
} from '@mui/icons-material';
import { useAuth } from '@clerk/clerk-react';
import { styled } from '@mui/material/styles';

import { getSchedulerDashboard, SchedulerDashboardData } from '../api/schedulerDashboard';
// Removed SchedulerStatsCards - metrics moved to header
import SchedulerJobsTree from '../components/SchedulerDashboard/SchedulerJobsTree';
import ExecutionLogsTable from '../components/SchedulerDashboard/ExecutionLogsTable';
import FailuresInsights from '../components/SchedulerDashboard/FailuresInsights';
import SchedulerEventHistory from '../components/SchedulerDashboard/SchedulerEventHistory';
import SchedulerCharts from '../components/SchedulerDashboard/SchedulerCharts';
import OAuthTokenStatus from '../components/SchedulerDashboard/OAuthTokenStatus';
import { TerminalTypography, terminalColors } from '../components/SchedulerDashboard/terminalTheme';

// Terminal-themed styled components
const TerminalContainer = styled(Container)(({ theme }) => ({
  backgroundColor: '#0a0a0a',
  minHeight: '100vh',
  color: '#00ff00',
  fontFamily: '"Courier New", "Monaco", "Consolas", "Fira Code", monospace',
  padding: theme.spacing(3),
  '& *': {
    fontFamily: 'inherit',
  }
}));

const TerminalHeader = styled(Box)({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  marginBottom: 24,
  paddingBottom: 16,
  borderBottom: '2px solid #00ff00',
});

const TerminalTitle = styled(Typography)<{ component?: React.ElementType }>(({ theme }) => ({
  color: '#00ff00',
  fontFamily: 'inherit',
  fontSize: '1.75rem',
  fontWeight: 'bold',
  textShadow: '0 0 10px rgba(0, 255, 0, 0.5)',
  letterSpacing: '2px',
}));

const TerminalSubtitle = styled(Typography)({
  color: '#00ff88',
  fontFamily: 'inherit',
  fontSize: '0.875rem',
  marginTop: 4,
  opacity: 0.8,
});

const TerminalChip = styled(Chip)({
  backgroundColor: '#1a1a1a',
  color: '#00ff00',
  border: '1px solid #00ff00',
  fontFamily: 'inherit',
  fontSize: '0.75rem',
  '& .MuiChip-label': {
    padding: '4px 8px',
  }
});

const TerminalIconButton = styled(IconButton)({
  color: '#00ff00',
  border: '1px solid #00ff00',
  '&:hover': {
    backgroundColor: 'rgba(0, 255, 0, 0.1)',
    boxShadow: '0 0 10px rgba(0, 255, 0, 0.3)',
  },
  '&:disabled': {
    color: '#004400',
    borderColor: '#004400',
  }
});

// Metric bubble style for header - Ultra modern terminal aesthetic
const MetricBubble = styled(Box)({
  display: 'flex',
  alignItems: 'center',
  gap: '8px',
  padding: '8px 14px',
  backgroundColor: 'rgba(10, 10, 10, 0.8)',
  border: '1px solid #00ff00',
  borderRadius: '20px',
  fontFamily: '"Courier New", "Monaco", "Consolas", "Fira Code", monospace',
  fontSize: '0.875rem',
  color: '#00ff00',
  cursor: 'default',
  position: 'relative',
  overflow: 'hidden',
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  boxShadow: '0 0 0 rgba(0, 255, 0, 0)',
  textShadow: '0 0 5px rgba(0, 255, 0, 0.3)',
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: '-100%',
    width: '100%',
    height: '100%',
    background: 'linear-gradient(90deg, transparent, rgba(0, 255, 0, 0.1), transparent)',
    transition: 'left 0.5s ease',
  },
  '&:hover': {
    backgroundColor: 'rgba(0, 255, 0, 0.15)',
    borderColor: '#00ff88',
    boxShadow: '0 0 20px rgba(0, 255, 0, 0.4), inset 0 0 10px rgba(0, 255, 0, 0.1)',
    transform: 'translateY(-2px) scale(1.02)',
    textShadow: '0 0 8px rgba(0, 255, 0, 0.6)',
    '&::before': {
      left: '100%',
    },
  },
  '& .metric-icon': {
    fontSize: '18px',
    display: 'flex',
    alignItems: 'center',
    filter: 'drop-shadow(0 0 3px rgba(0, 255, 0, 0.5))',
    transition: 'all 0.3s ease',
  },
  '&:hover .metric-icon': {
    transform: 'scale(1.1) rotate(5deg)',
    filter: 'drop-shadow(0 0 6px rgba(0, 255, 0, 0.8))',
  },
  '& .metric-value': {
    fontWeight: 700,
    fontSize: '0.9rem',
    letterSpacing: '0.5px',
    background: 'linear-gradient(135deg, #00ff00 0%, #00ff88 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
  },
  '& .metric-label': {
    fontSize: '0.7rem',
    opacity: 0.7,
    marginLeft: '2px',
    letterSpacing: '0.3px',
    textTransform: 'uppercase',
    fontWeight: 500,
  }
});

const TerminalAlert = styled(Alert)({
  backgroundColor: '#1a1a1a',
  color: '#ff4444',
  border: '1px solid #ff4444',
  fontFamily: 'inherit',
  '& .MuiAlert-icon': {
    color: '#ff4444',
  }
});

const TerminalLoading = styled(Box)({
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  minHeight: '400px',
  '& .MuiCircularProgress-root': {
    color: '#00ff00',
  }
});

const SchedulerDashboard: React.FC = () => {
  const { isSignedIn, isLoaded } = useAuth();
  const [dashboardData, setDashboardData] = useState<SchedulerDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [autoRefreshInterval, setAutoRefreshInterval] = useState<NodeJS.Timeout | null>(null);
  const [lastUpdateTimestamp, setLastUpdateTimestamp] = useState<string | null>(null);
  
  // Use refs to track loading state without causing re-renders
  const loadingRef = useRef(false);
  const refreshingRef = useRef(false);

  const fetchDashboardData = useCallback(async (isManualRefresh = false) => {
    // Prevent multiple simultaneous fetches using refs
    if (loadingRef.current || refreshingRef.current) {
      return;
    }

    try {
      loadingRef.current = !isManualRefresh;
      refreshingRef.current = isManualRefresh;
      
      if (isManualRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      setError(null);
      
      const data = await getSchedulerDashboard();
      
      // Always update state to ensure metrics are updated
      // The comparison was preventing updates when cumulative stats changed
      setDashboardData(data);
      
      setLastUpdated(new Date());
      setLastUpdateTimestamp(data.stats.last_update || null);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch scheduler dashboard');
      console.error('Error fetching scheduler dashboard:', err);
    } finally {
      loadingRef.current = false;
      refreshingRef.current = false;
      setLoading(false);
      setRefreshing(false);
    }
  }, []); // Empty deps - function is stable

  // Initial load - only once
  useEffect(() => {
    if (isLoaded && isSignedIn && !dashboardData) {
      fetchDashboardData();
    }
  }, [isLoaded, isSignedIn]); // Removed fetchDashboardData to prevent re-renders

  // Smart auto-refresh: Poll based on scheduler's check interval or next job execution
  useEffect(() => {
    if (!isSignedIn || !isLoaded || !dashboardData) return;

    // Calculate polling interval based on scheduler's check interval
    const checkIntervalMinutes = dashboardData.stats?.check_interval_minutes || 60;
    // Poll slightly before the scheduler's next check (at 90% of interval)
    // Convert to milliseconds and add some buffer
    const pollingIntervalMs = Math.max(
      (checkIntervalMinutes * 60 * 1000 * 0.9), // 90% of check interval
      60000 // Minimum 60 seconds
    );

    // Alternatively, calculate based on next job execution time
    let nextJobTime: Date | null = null;
    if (dashboardData.jobs && dashboardData.jobs.length > 0) {
      // Find the earliest next run time (only future jobs)
      const now = Date.now();
      const nextRunTimes = dashboardData.jobs
        .map(job => {
          if (!job.next_run_time) return null;
          const jobTime = new Date(job.next_run_time);
          // Only include future jobs
          return jobTime.getTime() > now ? jobTime : null;
        })
        .filter((time): time is Date => time !== null && !isNaN(time.getTime()))
        .sort((a, b) => a.getTime() - b.getTime());
      
      if (nextRunTimes.length > 0) {
        nextJobTime = nextRunTimes[0];
      }
    }

    // Use next job time if it's sooner than the check interval
    let finalIntervalMs = pollingIntervalMs;
    if (nextJobTime) {
      const msUntilNextJob = nextJobTime.getTime() - Date.now();
      // Poll slightly before next job (at 90% of time remaining, min 10s before, max 2min before)
      if (msUntilNextJob > 10000) { // At least 10 seconds in the future
        // Poll 10 seconds before job, or 10% of time remaining, whichever is smaller
        const pollBeforeJob = Math.min(
          Math.max(msUntilNextJob * 0.1, 10000), // 10% of time or 10s minimum
          msUntilNextJob - 10000 // But no more than 10s before
        );
        finalIntervalMs = Math.min(finalIntervalMs, pollBeforeJob);
      } else if (msUntilNextJob > 0) {
        // Job is very soon (< 10s), poll immediately (1 second)
        finalIntervalMs = 1000;
      }
    }

    // Cap at reasonable maximum (10 minutes) and minimum (10 seconds)
    finalIntervalMs = Math.max(10000, Math.min(finalIntervalMs, 600000)); // 10s min, 10min max

    const interval = setInterval(() => {
      // Only fetch if we're not already loading/refreshing (using refs)
      if (!loadingRef.current && !refreshingRef.current) {
        fetchDashboardData();
      }
    }, finalIntervalMs);

    setAutoRefreshInterval(interval);

    // Log the polling interval for debugging
    if (process.env.NODE_ENV === 'development') {
      console.log(
        `📊 Scheduler polling: ${Math.round(finalIntervalMs / 1000)}s ` +
        `(check interval: ${checkIntervalMinutes}min, next job: ${nextJobTime ? nextJobTime.toLocaleTimeString() : 'none'})`
      );
    }

    return () => {
      clearInterval(interval);
    };
  }, [isSignedIn, isLoaded, dashboardData, fetchDashboardData]); // Re-run when dashboard data changes

  // Format time ago
  const formatTimeAgo = (date: Date | null) => {
    if (!date) return 'Never';
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSecs = Math.floor(diffMs / 1000);
    const diffMins = Math.floor(diffSecs / 60);

    if (diffSecs < 10) return 'Just now';
    if (diffSecs < 60) return `${diffSecs}s ago`;
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    return `${diffHours}h ago`;
  };

  const handleManualRefresh = () => {
    if (!refreshing && !loading) {
      fetchDashboardData(true);
    }
  };

  if (!isLoaded) {
    return (
      <TerminalContainer maxWidth="xl">
        <TerminalLoading>
          <CircularProgress />
        </TerminalLoading>
      </TerminalContainer>
    );
  }

  if (!isSignedIn) {
    return (
      <TerminalContainer maxWidth="xl">
        <TerminalAlert severity="warning">
          Please sign in to view the scheduler dashboard.
        </TerminalAlert>
      </TerminalContainer>
    );
  }

  return (
    <TerminalContainer maxWidth="xl">
      {/* Header */}
      <TerminalHeader>
        <Box display="flex" flexDirection="column" gap={2} flex={1}>
          {/* Title Row */}
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box display="flex" alignItems="center" gap={2}>
              <ScheduleIcon sx={{ color: '#00ff00', fontSize: 32 }} />
              <Box>
                <TerminalTitle component="h1">
                  SCHEDULER DASHBOARD
                </TerminalTitle>
                <TerminalSubtitle>
                  Monitor task execution, jobs, and system status
                </TerminalSubtitle>
              </Box>
            </Box>
            <Box display="flex" alignItems="center" gap={2}>
              {lastUpdated && (
                <TerminalChip
                  label={`Last updated: ${formatTimeAgo(lastUpdated)}`}
                  size="small"
                  icon={<CheckCircleIcon sx={{ color: '#00ff00', fontSize: 14 }} />}
                />
              )}
              <Tooltip 
                title={
                  <Box>
                    <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                      Dashboard Status
                    </Typography>
                    {dashboardData && (
                      <>
                        <Typography variant="caption" component="div" sx={{ mb: 0.5 }}>
                          <strong>Jobs:</strong> {dashboardData.jobs?.length || 0} total 
                          (Recurring: {dashboardData.recurring_jobs || 0}, One-Time: {dashboardData.one_time_jobs || 0})
                        </Typography>
                        <Typography variant="caption" component="div" sx={{ mb: 0.5 }}>
                          <strong>Check Cycles:</strong> {
                            dashboardData.stats?.total_checks === 0 
                              ? '0 (First check pending - scheduler waiting for interval)'
                              : `${dashboardData.stats?.total_checks || 0} (${dashboardData.stats?.cumulative_total_check_cycles || 0} total)`
                          }
                        </Typography>
                        <Typography variant="caption" component="div" sx={{ mb: 0.5 }}>
                          <strong>Scheduler:</strong> {dashboardData.stats?.running ? 'Running' : 'Stopped'} | 
                          <strong> Interval:</strong> {dashboardData.stats?.check_interval_minutes || 0} min
                        </Typography>
                        {dashboardData.stats && dashboardData.stats.tasks_found > 0 && (
                          <Typography variant="caption" component="div">
                            <strong>Tasks:</strong> {dashboardData.stats.tasks_found} found, {dashboardData.stats.tasks_executed} executed, {dashboardData.stats.tasks_failed} failed
                          </Typography>
                        )}
                      </>
                    )}
                    {!dashboardData && (
                      <Typography variant="caption">
                        Click to refresh dashboard data
                      </Typography>
                    )}
                  </Box>
                }
                arrow
              >
                <span>
                  <TerminalIconButton
                    onClick={handleManualRefresh}
                    disabled={refreshing || loading}
                  >
                    <RefreshIcon 
                      sx={{
                        animation: refreshing ? 'spin 1s linear infinite' : 'none',
                        '@keyframes spin': {
                          '0%': { transform: 'rotate(0deg)' },
                          '100%': { transform: 'rotate(360deg)' }
                        }
                      }}
                    />
                  </TerminalIconButton>
                </span>
              </Tooltip>
            </Box>
          </Box>
          
          {/* Metrics Bubbles Row */}
          {dashboardData?.stats && (
            <Box display="flex" alignItems="center" gap={1.5} flexWrap="wrap">
              {/* Scheduler Status */}
              <Tooltip 
                title={
                  <Box>
                    <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                      Scheduler Status
                    </Typography>
                    <Typography variant="caption">
                      {dashboardData.stats.running 
                        ? 'The scheduler is currently running and actively checking for due tasks.'
                        : 'The scheduler is stopped and not processing any tasks.'}
                    </Typography>
                  </Box>
                }
                arrow
              >
                <MetricBubble>
                  <Box className="metric-icon" sx={{ color: dashboardData.stats.running ? '#00ff00' : '#ff4444' }}>
                    {dashboardData.stats.running ? <PlayArrowIcon fontSize="small" /> : <PauseIcon fontSize="small" />}
                  </Box>
                  <Box className="metric-value">
                    {dashboardData.stats.running ? 'Running' : 'Stopped'}
                  </Box>
                </MetricBubble>
              </Tooltip>

              {/* Total Check Cycles */}
              <Tooltip
                title={
                  <Box>
                    <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                      Total Check Cycles
                    </Typography>
                    <Typography variant="caption">
                      {dashboardData.stats.cumulative_total_check_cycles > 0
                        ? `Total check cycles: ${dashboardData.stats.cumulative_total_check_cycles.toLocaleString()} (${dashboardData.stats.total_checks} this session). The scheduler periodically checks for due tasks.`
                        : `No check cycles yet. The scheduler will run its first check cycle after the interval expires (${dashboardData.stats.check_interval_minutes} minutes).`}
                    </Typography>
                  </Box>
                }
                arrow
              >
                <MetricBubble>
                  <Box className="metric-icon">
                    <CheckCircleIcon fontSize="small" />
                  </Box>
                  <Box className="metric-value">
                    {(dashboardData.stats.cumulative_total_check_cycles !== undefined && dashboardData.stats.cumulative_total_check_cycles !== null)
                      ? dashboardData.stats.cumulative_total_check_cycles.toLocaleString()
                      : dashboardData.stats.total_checks.toLocaleString()}
                  </Box>
                  <Box className="metric-label">Cycles</Box>
                </MetricBubble>
              </Tooltip>

              {/* Tasks Executed */}
              <Tooltip
                title={
                  <Box>
                    <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                      Tasks Executed
                    </Typography>
                    <Typography variant="caption">
                      {dashboardData.stats.cumulative_tasks_executed > 0
                        ? `Total tasks executed: ${dashboardData.stats.cumulative_tasks_executed.toLocaleString()} (${dashboardData.stats.tasks_executed} this session). ${dashboardData.stats.tasks_failed > 0 ? `${dashboardData.stats.tasks_failed} failed.` : 'All successful.'}`
                        : 'No tasks have been executed yet. Tasks will appear here once the scheduler starts processing them.'}
                    </Typography>
                  </Box>
                }
                arrow
              >
                <MetricBubble>
                  <Box className="metric-icon">
                    <TrendingUpIcon fontSize="small" />
                  </Box>
                  <Box className="metric-value">
                    {(dashboardData.stats.cumulative_tasks_executed !== undefined && dashboardData.stats.cumulative_tasks_executed !== null)
                      ? dashboardData.stats.cumulative_tasks_executed.toLocaleString()
                      : dashboardData.stats.tasks_executed.toLocaleString()}
                  </Box>
                  <Box className="metric-label">Executed</Box>
                </MetricBubble>
              </Tooltip>

              {/* Tasks Found */}
              <Tooltip
                title={
                  <Box>
                    <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                      Tasks Found
                    </Typography>
                    <Typography variant="caption">
                      {dashboardData.stats.cumulative_tasks_found > 0
                        ? `Total tasks found: ${dashboardData.stats.cumulative_tasks_found.toLocaleString()} (${dashboardData.stats.tasks_found} this session). ${dashboardData.stats.tasks_executed} executed, ${dashboardData.stats.tasks_failed} failed.`
                        : 'No tasks have been found yet. Tasks will appear here once they are scheduled and due for execution.'}
                    </Typography>
                  </Box>
                }
                arrow
              >
                <MetricBubble>
                  <Box className="metric-icon">
                    <ScheduleIcon fontSize="small" />
                  </Box>
                  <Box className="metric-value">
                    {(dashboardData.stats.cumulative_tasks_found !== undefined && dashboardData.stats.cumulative_tasks_found !== null)
                      ? dashboardData.stats.cumulative_tasks_found.toLocaleString()
                      : dashboardData.stats.tasks_found.toLocaleString()}
                  </Box>
                  <Box className="metric-label">Found</Box>
                </MetricBubble>
              </Tooltip>

              {/* Check Interval */}
              <Tooltip
                title={
                  <Box>
                    <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                      Check Interval
                    </Typography>
                    <Typography variant="caption">
                      {dashboardData.stats.intelligent_scheduling
                        ? `Intelligent scheduling is enabled. The scheduler adjusts its check interval based on active strategies: ${dashboardData.stats.active_strategies_count > 0 ? '15-30 minutes when strategies are active' : '60 minutes when no active strategies'}. Current interval: ${dashboardData.stats.check_interval_minutes} minutes.`
                        : `Fixed check interval: ${dashboardData.stats.check_interval_minutes} minutes. The scheduler checks for due tasks at this interval.`}
                    </Typography>
                  </Box>
                }
                arrow
              >
                <MetricBubble>
                  <Box className="metric-icon">
                    <AccessTimeIcon fontSize="small" />
                  </Box>
                  <Box className="metric-value">
                    {dashboardData.stats.check_interval_minutes >= 60
                      ? `${Math.floor(dashboardData.stats.check_interval_minutes / 60)}h`
                      : `${dashboardData.stats.check_interval_minutes}m`}
                  </Box>
                  <Box className="metric-label">Interval</Box>
                </MetricBubble>
              </Tooltip>

              {/* Active Strategies */}
              <Tooltip
                title={
                  <Box>
                    <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                      Active Strategies
                    </Typography>
                    <Typography variant="caption">
                      {dashboardData.stats.active_strategies_count > 0
                        ? `There are ${dashboardData.stats.active_strategies_count} active content strategy(ies) with monitoring tasks. The scheduler will check more frequently when strategies are active.`
                        : 'No active content strategies with monitoring tasks. The scheduler will check less frequently (every 60 minutes) to conserve resources.'}
                    </Typography>
                  </Box>
                }
                arrow
              >
                <MetricBubble>
                  <Box className="metric-icon" sx={{ color: dashboardData.stats.active_strategies_count > 0 ? '#00ff00' : '#888' }}>
                    <TrendingUpIcon fontSize="small" />
                  </Box>
                  <Box className="metric-value">
                    {dashboardData.stats.active_strategies_count}
                  </Box>
                  <Box className="metric-label">Strategies</Box>
                </MetricBubble>
              </Tooltip>
            </Box>
          )}
        </Box>
      </TerminalHeader>

      {/* Error Alert */}
      {error && (
        <TerminalAlert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </TerminalAlert>
      )}

      {/* Loading State */}
      {loading && !dashboardData ? (
        <TerminalLoading>
          <CircularProgress />
        </TerminalLoading>
      ) : dashboardData ? (
        <>
          {/* Debug Info removed - status moved to refresh icon tooltip */}
          
          {/* Stats Cards removed - metrics moved to header as bubbles */}

          {/* Jobs Tree and Failures/Insights Side by Side */}
          <Box display="flex" gap={3} flexDirection={{ xs: 'column', lg: 'row' }} mb={4} alignItems="stretch">
            <Box flex={2} sx={{ display: 'flex', flexDirection: 'column' }}>
              {dashboardData.jobs && dashboardData.jobs.length > 0 ? (
                <SchedulerJobsTree
                  jobs={dashboardData.jobs}
                  recurringJobs={dashboardData.recurring_jobs || 0}
                  oneTimeJobs={dashboardData.one_time_jobs || 0}
                />
              ) : (
                <TerminalAlert severity="info">No jobs scheduled</TerminalAlert>
              )}
            </Box>
            <Box flex={1} sx={{ display: 'flex', flexDirection: 'column' }}>
              <FailuresInsights stats={dashboardData.stats} />
            </Box>
          </Box>

          {/* OAuth Token Status */}
          <Box mb={4}>
            <OAuthTokenStatus compact={true} />
          </Box>

          {/* Execution Logs */}
          <Box mb={4}>
            <ExecutionLogsTable initialLimit={50} />
          </Box>

          {/* Scheduler Event History */}
          <Box mb={4}>
            <SchedulerEventHistory limit={50} />
          </Box>

          {/* Scheduler Charts Visualization */}
          <Box mb={4}>
            <SchedulerCharts />
          </Box>
        </>
      ) : (
        <TerminalAlert severity="info">
          No scheduler data available. The scheduler may not be running.
        </TerminalAlert>
      )}

      {/* Auto-refresh indicator */}
      {autoRefreshInterval && dashboardData?.stats && (
        <Box mt={2} display="flex" justifyContent="center">
          <TerminalChip
            icon={<CheckCircleIcon sx={{ color: '#00ff00', fontSize: 14 }} />}
            label={`Auto-refresh: ${dashboardData.stats.check_interval_minutes}min interval`}
            size="small"
          />
        </Box>
      )}
    </TerminalContainer>
  );
};

export default SchedulerDashboard;
