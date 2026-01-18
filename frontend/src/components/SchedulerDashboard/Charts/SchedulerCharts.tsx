/**
 * Scheduler Charts Component
 * Visualizes scheduler event history data using Recharts
 */

import React, { useMemo, useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { Box, Paper, CircularProgress, IconButton, Tooltip as MuiTooltip } from '@mui/material';
import { OpenInFull as MaximizeIcon } from '@mui/icons-material';
import { TerminalTypography, TerminalPaper, terminalColors } from '../terminalTheme';
import { getSchedulerEventHistory, SchedulerEvent } from '../../../api/schedulerDashboard';
import { ChartModal } from './ChartModal';
import { PerformanceSummary } from './PerformanceSummary';

interface SchedulerChartsProps {
  // Optional: can receive events as prop or fetch them internally
  events?: SchedulerEvent[];
  compactMode?: boolean; // For header display
}

const SchedulerCharts: React.FC<SchedulerChartsProps> = ({ events: propEvents, compactMode = false }) => {
  const [events, setEvents] = useState<SchedulerEvent[]>(propEvents || []);
  const [loading, setLoading] = useState(!propEvents);

  // Update events when propEvents changes
  useEffect(() => {
    if (propEvents !== undefined) {
      setEvents(propEvents);
      setLoading(false);
    }
  }, [propEvents]);

  const [error, setError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState<string | null>(null);

  // Fetch events if not provided as prop
  useEffect(() => {
    if (!propEvents && !events.length) {
      const fetchEvents = async () => {
        try {
          setLoading(true);
          setError(null);
          // Fetch events for visualization (max 500 per backend API limit)
          // Pass undefined to get all event types, use 30 days for charts
          console.log('📊 Charts - Fetching event history...');
          const response = await getSchedulerEventHistory(500, 0, undefined, 30);
          console.log('📊 Charts - Fetched events:', {
            totalEvents: response.events?.length || 0,
            totalCount: response.total_count,
            hasEvents: !!(response.events && response.events.length > 0),
            sampleEvent: response.events?.[0]
          });
          setEvents(response.events || []);
        } catch (err: any) {
          console.error('❌ Charts - Error fetching events:', err);
          console.error('❌ Charts - Error details:', {
            message: err?.message,
            response: err?.response,
            responseData: err?.response?.data,
            stack: err?.stack
          });
          const errorMessage = err?.response?.data?.detail || err?.response?.data?.message || err?.message || String(err) || 'Failed to fetch event history';
          setError(errorMessage);
        } finally {
          setLoading(false);
        }
      };
      fetchEvents();
    }
  }, [propEvents, events.length]);

  // Process events for charting
  const chartData = useMemo(() => {
    if (!events || events.length === 0) return [];

    // Group events by date (day)
    const eventsByDate: Record<string, {
      date: string;
      check_cycles: number;
      tasks_found: number;
      tasks_executed: number;
      tasks_failed: number;
      job_scheduled: number;
      job_completed: number;
      job_failed: number;
    }> = {};

    events.forEach(event => {
      const date = event.event_date ? new Date(event.event_date).toLocaleDateString() : 'Unknown';

      if (!eventsByDate[date]) {
        eventsByDate[date] = {
          date,
          check_cycles: 0,
          tasks_found: 0,
          tasks_executed: 0,
          tasks_failed: 0,
          job_scheduled: 0,
          job_completed: 0,
          job_failed: 0,
        };
      }

      switch (event.event_type) {
        case 'check_cycle':
          eventsByDate[date].check_cycles++;
          eventsByDate[date].tasks_found += event.tasks_found || 0;
          eventsByDate[date].tasks_executed += event.tasks_executed || 0;
          eventsByDate[date].tasks_failed += event.tasks_failed || 0;
          break;
        case 'job_scheduled':
          eventsByDate[date].job_scheduled++;
          break;
        case 'job_completed':
          eventsByDate[date].job_completed++;
          break;
        case 'job_failed':
          eventsByDate[date].job_failed++;
          break;
      }
    });

    // Convert to array and sort by date
    return Object.values(eventsByDate).sort((a, b) => {
      return new Date(a.date).getTime() - new Date(b.date).getTime();
    }).slice(-30); // Last 30 days
  }, [events]);

  // Calculate totals for summary
  const totals = useMemo(() => {
    return events.reduce((acc, event) => {
      switch (event.event_type) {
        case 'check_cycle':
          acc.check_cycles++;
          acc.tasks_found += event.tasks_found || 0;
          acc.tasks_executed += event.tasks_executed || 0;
          acc.tasks_failed += event.tasks_failed || 0;
          break;
        case 'job_scheduled':
          acc.job_scheduled++;
          break;
        case 'job_completed':
          acc.job_completed++;
          break;
        case 'job_failed':
          acc.job_failed++;
          break;
      }
      return acc;
    }, {
      check_cycles: 0,
      tasks_found: 0,
      tasks_executed: 0,
      tasks_failed: 0,
      job_scheduled: 0,
      job_completed: 0,
      job_failed: 0,
    });
  }, [events]);

  // Calculate additional metrics for better insights
  const metrics = useMemo(() => {
    // Tasks processed = tasks found by scheduler (or executed + failed as fallback)
    const totalTasksProcessed = totals.tasks_found || (totals.tasks_executed + totals.tasks_failed);
    const successRate = totalTasksProcessed > 0 ?
      ((totals.tasks_executed) / totalTasksProcessed * 100) : 100;

    const avgTasksPerCycle = totals.check_cycles > 0 ?
      totalTasksProcessed / totals.check_cycles : 0;

    const recentData = chartData.slice(-7); // Last 7 days
    const recentAvgTasks = recentData.length > 0 ?
      recentData.reduce((sum, day) => sum + (day.tasks_found || 0), 0) / recentData.length : 0;

    return {
      totalTasksProcessed,
      successRate,
      tasksFailed: totals.tasks_failed,
      checkCycles: totals.check_cycles,
      avgTasksPerCycle,
      recentAvgTasks,
      trendDirection: recentAvgTasks > avgTasksPerCycle ? 'up' : recentAvgTasks < avgTasksPerCycle ? 'down' : 'stable'
    };
  }, [totals, chartData]);

  // Custom tooltip with user-friendly messages
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <Paper
          sx={{
            backgroundColor: terminalColors.background,
            border: `1px solid ${terminalColors.primary}`,
            padding: 1.5,
            fontFamily: 'monospace',
            maxWidth: '280px'
          }}
        >
          <TerminalTypography variant="body2" sx={{ color: terminalColors.primary, fontWeight: 'bold', mb: 1 }}>
            📅 {label}
          </TerminalTypography>
          {payload.map((entry: any, index: number) => {
            let displayName = entry.name;
            let displayValue = entry.value;
            let explanation = '';

            // Make the tooltips more user-friendly
            switch (entry.dataKey) {
              case 'tasks_found':
                displayName = 'Tasks Found';
                explanation = 'Tasks discovered by scheduler';
                break;
              case 'tasks_executed':
                displayName = 'Tasks Completed';
                explanation = 'Successfully processed tasks';
                break;
              case 'tasks_failed':
                displayName = 'Tasks Failed';
                explanation = 'Tasks that encountered errors';
                break;
              case 'job_completed':
                displayName = 'Jobs Completed';
                explanation = 'Individual job executions finished';
                break;
              case 'job_failed':
                displayName = 'Jobs Failed';
                explanation = 'Individual job executions failed';
                break;
              case 'check_cycles':
                displayName = 'Check Cycles';
                explanation = 'Times scheduler checked for work';
                break;
            }

            return (
              <Box key={index} sx={{ mb: 0.5 }}>
                <TerminalTypography
                  variant="body2"
                  sx={{ color: entry.color, fontSize: '0.8rem', fontWeight: 'bold' }}
                >
                  {displayName}: {displayValue}
                </TerminalTypography>
                {explanation && (
                  <TerminalTypography
                    variant="caption"
                    sx={{ color: terminalColors.textSecondary, fontSize: '0.7rem' }}
                  >
                    {explanation}
                  </TerminalTypography>
                )}
              </Box>
            );
          })}
        </Paper>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <TerminalPaper sx={{ p: 3, textAlign: 'center' }}>
        <CircularProgress sx={{ color: terminalColors.primary, mb: 2 }} />
        <TerminalTypography variant="body2" sx={{ color: terminalColors.textSecondary }}>
          Loading chart data...
        </TerminalTypography>
      </TerminalPaper>
    );
  }

  if (error) {
    return (
      <TerminalPaper sx={{ p: 3, textAlign: 'center' }}>
        <TerminalTypography variant="body2" sx={{ color: terminalColors.error }}>
          Error loading charts: {error}
        </TerminalTypography>
      </TerminalPaper>
    );
  }

  if (events.length === 0) {
    return (
      <TerminalPaper sx={{ p: 3, textAlign: 'center' }}>
        <TerminalTypography variant="body2" sx={{ color: terminalColors.textSecondary }}>
          No event history data available yet. Charts will appear once scheduler events are logged.
        </TerminalTypography>
      </TerminalPaper>
    );
  }

  const handleChartClick = (chartId: string) => {
    setModalOpen(chartId);
  };

  const handleModalClose = () => {
    setModalOpen(null);
  };

  // Compact mode for header integration
  if (compactMode) {
    return (
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 2, mt: 1 }}>
        {/* Tasks Processed */}
        <TerminalPaper sx={{ p: 2, textAlign: 'center' }}>
          <TerminalTypography variant="h6" sx={{ color: terminalColors.success, fontSize: '1.5rem', fontWeight: 'bold' }}>
            {metrics.totalTasksProcessed.toLocaleString()}
          </TerminalTypography>
          <TerminalTypography variant="body2" sx={{ color: terminalColors.textSecondary, fontSize: '0.8rem' }}>
            Tasks Processed
          </TerminalTypography>
        </TerminalPaper>

        {/* Success Rate */}
        <TerminalPaper sx={{ p: 2, textAlign: 'center' }}>
          <TerminalTypography variant="h6" sx={{
            color: metrics.successRate >= 95 ? terminalColors.success :
                   metrics.successRate >= 80 ? terminalColors.warning : terminalColors.error,
            fontSize: '1.5rem',
            fontWeight: 'bold'
          }}>
            {metrics.successRate.toFixed(0)}%
          </TerminalTypography>
          <TerminalTypography variant="body2" sx={{ color: terminalColors.textSecondary, fontSize: '0.8rem' }}>
            Success Rate
          </TerminalTypography>
        </TerminalPaper>

        {/* Tasks Failed */}
        {metrics.tasksFailed > 0 && (
          <TerminalPaper sx={{ p: 2, textAlign: 'center' }}>
            <TerminalTypography variant="h6" sx={{ color: terminalColors.error, fontSize: '1.5rem', fontWeight: 'bold' }}>
              {metrics.tasksFailed}
            </TerminalTypography>
            <TerminalTypography variant="body2" sx={{ color: terminalColors.textSecondary, fontSize: '0.8rem' }}>
              Tasks Failed
            </TerminalTypography>
          </TerminalPaper>
        )}

        {/* Active Cycles */}
        <TerminalPaper sx={{ p: 2, textAlign: 'center' }}>
          <TerminalTypography variant="h6" sx={{ color: terminalColors.info, fontSize: '1.5rem', fontWeight: 'bold' }}>
            {metrics.checkCycles}
          </TerminalTypography>
          <TerminalTypography variant="body2" sx={{ color: terminalColors.textSecondary, fontSize: '0.8rem' }}>
            Check Cycles
          </TerminalTypography>
        </TerminalPaper>
      </Box>
    );
  }

  return (
    <Box>
      {/* Compact Charts in Single Row */}
      <Box sx={{ display: 'flex', gap: 2, overflowX: 'auto', pb: 2 }}>
        {/* Task Execution Trends - Compact */}
        <Box
          sx={{
            flex: '0 0 300px',
            cursor: 'pointer',
            transition: 'transform 0.2s',
            '&:hover': {
              transform: 'scale(1.05)',
            },
          }}
          onClick={() => handleChartClick('task-execution')}
        >
          <TerminalPaper sx={{ p: 2, position: 'relative' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <TerminalTypography variant="body2" sx={{ color: terminalColors.primary, fontSize: '0.875rem' }}>
                📈 Daily Task Activity
              </TerminalTypography>
              <MaximizeIcon sx={{ fontSize: 16, color: terminalColors.primary }} />
            </Box>
            <ResponsiveContainer width="100%" height={150}>
              <LineChart data={chartData.slice(-7)}>
                <CartesianGrid strokeDasharray="3 3" stroke={terminalColors.border} />
                <XAxis
                  dataKey="date"
                  stroke={terminalColors.primary}
                  tick={{ fill: terminalColors.primary, fontSize: 10 }}
                  interval="preserveStartEnd"
                />
                <YAxis
                  stroke={terminalColors.primary}
                  tick={{ fill: terminalColors.primary, fontSize: 10 }}
                  width={30}
                />
                <Tooltip content={CustomTooltip} />
                <Line
                  type="monotone"
                  dataKey="tasks_executed"
                  stroke={terminalColors.success}
                  strokeWidth={2}
                  name="✅ Tasks Completed"
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="tasks_failed"
                  stroke={terminalColors.error}
                  strokeWidth={2}
                  name="❌ Tasks Failed"
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </TerminalPaper>
        </Box>

        {/* Job Status Distribution - Compact */}
        <Box
          sx={{
            flex: '0 0 300px',
            cursor: 'pointer',
            transition: 'transform 0.2s',
            '&:hover': {
              transform: 'scale(1.05)',
            },
          }}
          onClick={() => handleChartClick('job-status')}
        >
          <TerminalPaper sx={{ p: 2, position: 'relative' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <TerminalTypography variant="body2" sx={{ color: terminalColors.primary, fontSize: '0.875rem' }}>
                ✅ Task Completion Status
              </TerminalTypography>
              <MaximizeIcon sx={{ fontSize: 16, color: terminalColors.primary }} />
            </Box>
            <ResponsiveContainer width="100%" height={150}>
              <BarChart data={chartData.slice(-7)}>
                <CartesianGrid strokeDasharray="3 3" stroke={terminalColors.border} />
                <XAxis
                  dataKey="date"
                  stroke={terminalColors.primary}
                  tick={{ fill: terminalColors.primary, fontSize: 10 }}
                  interval="preserveStartEnd"
                />
                <YAxis
                  stroke={terminalColors.primary}
                  tick={{ fill: terminalColors.primary, fontSize: 10 }}
                  width={30}
                />
                <Tooltip content={CustomTooltip} />
                <Bar
                  dataKey="job_completed"
                  fill={terminalColors.success}
                  name="✅ Jobs Completed"
                  radius={[4, 4, 0, 0]}
                />
                <Bar
                  dataKey="job_failed"
                  fill={terminalColors.error}
                  name="❌ Jobs Failed"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </TerminalPaper>
        </Box>

        {/* Check Cycles - Compact */}
        <Box
          sx={{
            flex: '0 0 300px',
            cursor: 'pointer',
            transition: 'transform 0.2s',
            '&:hover': {
              transform: 'scale(1.05)',
            },
          }}
          onClick={() => handleChartClick('check-cycles')}
        >
          <TerminalPaper sx={{ p: 2, position: 'relative' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <TerminalTypography variant="body2" sx={{ color: terminalColors.primary, fontSize: '0.875rem' }}>
                🔄 System Activity
              </TerminalTypography>
              <MaximizeIcon sx={{ fontSize: 16, color: terminalColors.primary }} />
            </Box>
            <ResponsiveContainer width="100%" height={150}>
              <BarChart data={chartData.slice(-7)}>
                <CartesianGrid strokeDasharray="3 3" stroke={terminalColors.border} />
                <XAxis
                  dataKey="date"
                  stroke={terminalColors.primary}
                  tick={{ fill: terminalColors.primary, fontSize: 10 }}
                  interval="preserveStartEnd"
                />
                <YAxis
                  stroke={terminalColors.primary}
                  tick={{ fill: terminalColors.primary, fontSize: 10 }}
                  width={30}
                />
                <Tooltip content={CustomTooltip} />
                <Bar
                  dataKey="check_cycles"
                  fill={terminalColors.primary}
                  name="🔄 System Checks"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </TerminalPaper>
        </Box>
      </Box>

      {/* Modals for Expanded Charts */}
      <ChartModal
        open={modalOpen === 'task-execution'}
        onClose={handleModalClose}
        title="📈 Task Activity Details (Last 30 Days)"
      >
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke={terminalColors.border} />
            <XAxis
              dataKey="date"
              stroke={terminalColors.primary}
              tick={{ fill: terminalColors.primary, fontSize: 12 }}
            />
            <YAxis
              stroke={terminalColors.primary}
              tick={{ fill: terminalColors.primary, fontSize: 12 }}
            />
            <Tooltip content={CustomTooltip} />
            <Legend
              wrapperStyle={{ color: terminalColors.primary, fontFamily: 'monospace' }}
            />
            <Line
              type="monotone"
              dataKey="tasks_found"
              stroke={terminalColors.info}
              strokeWidth={2}
              name="📋 Tasks Discovered"
              dot={{ fill: terminalColors.info, r: 4 }}
            />
            <Line
              type="monotone"
              dataKey="tasks_executed"
              stroke={terminalColors.success}
              strokeWidth={2}
              name="✅ Tasks Completed"
              dot={{ fill: terminalColors.success, r: 4 }}
            />
            <Line
              type="monotone"
              dataKey="tasks_failed"
              stroke={terminalColors.error}
              strokeWidth={2}
              name="❌ Tasks Failed"
              dot={{ fill: terminalColors.error, r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </ChartModal>

      <ChartModal
        open={modalOpen === 'job-status'}
        onClose={handleModalClose}
        title="✅ Task Completion Overview (Last 30 Days)"
      >
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke={terminalColors.border} />
            <XAxis
              dataKey="date"
              stroke={terminalColors.primary}
              tick={{ fill: terminalColors.primary, fontSize: 12 }}
            />
            <YAxis
              stroke={terminalColors.primary}
              tick={{ fill: terminalColors.primary, fontSize: 12 }}
            />
            <Tooltip content={CustomTooltip} />
            <Legend
              wrapperStyle={{ color: terminalColors.primary, fontFamily: 'monospace' }}
            />
            <Bar
              dataKey="job_scheduled"
              fill={terminalColors.info}
              name="📅 Jobs Scheduled"
            />
            <Bar
              dataKey="job_completed"
              fill={terminalColors.success}
              name="✅ Jobs Completed"
            />
            <Bar
              dataKey="job_failed"
              fill={terminalColors.error}
              name="❌ Jobs Failed"
            />
          </BarChart>
        </ResponsiveContainer>
      </ChartModal>

      <ChartModal
        open={modalOpen === 'check-cycles'}
        onClose={handleModalClose}
        title="🔄 System Activity Trends (Last 30 Days)"
      >
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke={terminalColors.border} />
            <XAxis
              dataKey="date"
              stroke={terminalColors.primary}
              tick={{ fill: terminalColors.primary, fontSize: 12 }}
            />
            <YAxis
              stroke={terminalColors.primary}
              tick={{ fill: terminalColors.primary, fontSize: 12 }}
            />
            <Tooltip content={CustomTooltip} />
            <Bar
              dataKey="check_cycles"
              fill={terminalColors.primary}
              name="🔄 System Checks"
            />
          </BarChart>
        </ResponsiveContainer>
      </ChartModal>

      {/* Summary Stats - User-Friendly */}
      <Box sx={{ mt: 3 }}>
        <TerminalTypography variant="h6" sx={{ color: terminalColors.primary, mb: 2, fontSize: '1rem' }}>
          📊 System Performance Summary
        </TerminalTypography>

        <PerformanceSummary events={events} compact={false} />

        {/* Performance Insights */}
        <Box sx={{ mt: 2 }}>
          <TerminalTypography variant="body2" sx={{ color: terminalColors.textSecondary, fontSize: '0.8rem', textAlign: 'center' }}>
            {metrics.successRate >= 95
              ? `🎯 Your automation is working excellently! ${metrics.totalTasksProcessed} tasks processed successfully.`
              : metrics.successRate >= 80
              ? `👍 Good performance! ${metrics.totalTasksProcessed} tasks processed with ${totals.tasks_failed} issues to review.`
              : `⚠️ Some tasks need attention. ${totals.tasks_failed} failures out of ${metrics.totalTasksProcessed} tasks processed.`
            }
          </TerminalTypography>
        </Box>
      </Box>
    </Box>
  );
};

export default SchedulerCharts;