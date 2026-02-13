/**
 * Scheduler Event History Component
 * Displays historical scheduler events (check cycles, interval adjustments, etc.)
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  Typography,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Tooltip,
  Collapse,
  Divider,
  IconButton
} from '@mui/material';
import {
  TerminalPaper,
  TerminalTypography,
  TerminalChipSuccess,
  TerminalChipError,
  TerminalChipWarning,
  TerminalTableCell,
  TerminalTableRow,
  TerminalAlert,
  terminalColors
} from './terminalTheme';
import { ExpandMore as ExpandMoreIcon } from '@mui/icons-material';
import { Info as InfoIcon } from '@mui/icons-material';
import { getSchedulerEventHistory, SchedulerEvent } from '../../api/schedulerDashboard';

interface SchedulerEventHistoryProps {
  limit?: number;
  sharedEvents?: SchedulerEvent[];
}

const SchedulerEventHistory: React.FC<SchedulerEventHistoryProps> = ({ sharedEvents }) => {
  const [events, setEvents] = useState<SchedulerEvent[]>(sharedEvents || []);
  const [loading, setLoading] = useState(!sharedEvents);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [isExpanded, setIsExpanded] = useState(false);
  const [rowsPerPage, setRowsPerPage] = useState(5); // Start with 5, expand to 50 on hover
  const [totalCount, setTotalCount] = useState(0);
  const [eventTypeFilter, setEventTypeFilter] = useState<string>('all');
  const [daysFilter, setDaysFilter] = useState<number>(7);

  // Insights state
  const [insightsExpanded, setInsightsExpanded] = useState(true);
  const [selectedInsightFilter, setSelectedInsightFilter] = useState<string | null>(null);

  const fetchEvents = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await getSchedulerEventHistory(
        rowsPerPage,
        page * rowsPerPage,
        eventTypeFilter !== 'all' ? eventTypeFilter as any : undefined,
        daysFilter
      );
      
      setEvents(response.events);
      setTotalCount(response.total_count);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch scheduler event history');
      console.error('Error fetching scheduler event history:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (sharedEvents) {
      // Use shared events data
      setEvents(sharedEvents);
      setLoading(false);
    } else {
      // Fetch our own data
      fetchEvents();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, rowsPerPage, eventTypeFilter, daysFilter, sharedEvents]); // fetchEvents is stable, no need to include

  // Expand to 50 rows on hover
  const handleMouseEnter = () => {
    if (!isExpanded) {
      setIsExpanded(true);
      setRowsPerPage(50);
      setPage(0); // Reset to first page when expanding
    }
  };

  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const getEventTypeColor = (eventType: string) => {
    switch (eventType) {
      case 'check_cycle':
        return terminalColors.success;
      case 'interval_adjustment':
        return terminalColors.warning;
      case 'start':
        return terminalColors.success;
      case 'stop':
        return terminalColors.error;
      case 'job_scheduled':
        return terminalColors.info;
      case 'job_completed':
        return terminalColors.success;
      case 'job_failed':
        return terminalColors.error;
      default:
        return terminalColors.info;
    }
  };

  const getInsightBorderColor = (severity: string) => {
    switch (severity) {
      case 'error': return terminalColors.error;
      case 'warning': return terminalColors.warning;
      case 'success': return terminalColors.success;
      case 'info': return terminalColors.info;
      default: return terminalColors.primary;
    }
  };

  const getInsightBackgroundColor = (severity: string) => {
    switch (severity) {
      case 'error': return 'rgba(244, 67, 54, 0.05)';
      case 'warning': return 'rgba(255, 152, 0, 0.05)';
      case 'success': return 'rgba(76, 175, 80, 0.05)';
      case 'info': return 'rgba(33, 150, 243, 0.05)';
      default: return 'rgba(0, 255, 0, 0.05)';
    }
  };

  const getInsightHoverColor = (severity: string) => {
    switch (severity) {
      case 'error': return 'rgba(244, 67, 54, 0.1)';
      case 'warning': return 'rgba(255, 152, 0, 0.1)';
      case 'success': return 'rgba(76, 175, 80, 0.1)';
      case 'info': return 'rgba(33, 150, 243, 0.1)';
      default: return 'rgba(0, 255, 0, 0.1)';
    }
  };

  const getInsightTextColor = (severity: string) => {
    switch (severity) {
      case 'error': return terminalColors.error;
      case 'warning': return terminalColors.warning;
      case 'success': return terminalColors.success;
      case 'info': return terminalColors.info;
      default: return terminalColors.primary;
    }
  };

  const formatEventDetails = (event: SchedulerEvent): string => {
    switch (event.event_type) {
      case 'check_cycle':
        return `Cycle #${event.check_cycle_number || 'N/A'} | ${event.tasks_found || 0} found, ${event.tasks_executed || 0} executed, ${event.tasks_failed || 0} failed | ${event.check_duration_seconds?.toFixed(2) || 'N/A'}s`;
      case 'interval_adjustment':
        return `${event.previous_interval_minutes || 'N/A'}min → ${event.new_interval_minutes || 'N/A'}min | ${event.active_strategies_count || 0} active strategies`;
      case 'start':
        return `Started with ${event.check_interval_minutes || 'N/A'}min interval | ${event.active_strategies_count || 0} active strategies`;
      case 'stop':
        return `Stopped gracefully | ${event.event_data?.total_checks || 0} total cycles`;
      case 'job_scheduled':
        const scheduledJob = event.event_data as any;
        return `Job: ${event.job_id || 'N/A'} | Function: ${scheduledJob?.function_name || 'N/A'} | User: ${event.user_id || 'system'}`;
      case 'job_completed':
        const completedJob = event.event_data as any;
        return `Job: ${event.job_id || 'N/A'} | Function: ${completedJob?.job_function || 'N/A'} | User: ${event.user_id || 'system'} | Time: ${completedJob?.execution_time_seconds?.toFixed(2) || 'N/A'}s`;
      case 'job_failed':
        const failedJob = event.event_data as any;
        const expensive = failedJob?.expensive_api_call ? '💰 Expensive API call wasted' : '';
        const errorMsg = event.error_message || failedJob?.exception_message || 'Unknown error';
        return `Job: ${event.job_id || 'N/A'} | Function: ${failedJob?.job_function || 'N/A'} | User: ${event.user_id || 'system'} | Error: ${errorMsg}${expensive ? ` | ${expensive}` : ''}`;
      default:
        return JSON.stringify(event.event_data || {});
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A';
    try {
      const date = new Date(dateString);
      return date.toLocaleString();
    } catch {
      return dateString;
    }
  };

  // Generate insights from event history
  const generateInsights = () => {
    const insights = [];

      // Always show at least basic insights
    insights.push({
      type: 'info',
      icon: '🔍',
      title: 'System Monitoring Active',
      message: 'Scheduler event history is being monitored for performance and reliability insights.',
      severity: 'info',
      tooltip: 'System is actively monitoring scheduler events and performance metrics'
    });

    if (!events.length) return insights;

    const now = new Date();
    const last24h = new Date(now.getTime() - 24 * 60 * 60 * 1000);
    const last7d = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

    // Recent events (last 24h)
    const recentEvents = events.filter(e => e.event_date && new Date(e.event_date) > last24h);
    const recentCheckCycles = recentEvents.filter(e => e.event_type === 'check_cycle');
    const recentFailures = recentEvents.filter(e => e.event_type === 'job_failed');
    const recentCompletions = recentEvents.filter(e => e.event_type === 'job_completed');

    // Performance metrics
    const avgCheckDuration = recentCheckCycles.length > 0
      ? recentCheckCycles.reduce((sum, e) => sum + (e.check_duration_seconds || 0), 0) / recentCheckCycles.length
      : 0;

    const totalTasksExecuted = recentCheckCycles.reduce((sum, e) => sum + (e.tasks_executed || 0), 0);
    const totalTasksFailed = recentCheckCycles.reduce((sum, e) => sum + (e.tasks_failed || 0), 0);
    const successRate = totalTasksExecuted > 0 ? ((totalTasksExecuted - totalTasksFailed) / totalTasksExecuted * 100) : 100;

    // Basic event summary insight
    if (events.length > 0) {
      const oldestEvent = events.reduce((oldest, e) =>
        e.event_date && (!oldest.event_date || new Date(e.event_date) < new Date(oldest.event_date)) ? e : oldest
      );
      const newestEvent = events.reduce((newest, e) =>
        e.event_date && (!newest.event_date || new Date(e.event_date) > new Date(newest.event_date)) ? e : newest
      );

      insights.push({
        type: 'info',
        icon: '📈',
        title: 'Event Tracking Active',
        message: `Monitoring ${events.length} scheduler events from ${oldestEvent.event_date ? new Date(oldestEvent.event_date).toLocaleDateString() : 'unknown'} to ${newestEvent.event_date ? new Date(newestEvent.event_date).toLocaleDateString() : 'now'}`,
        severity: 'info',
        tooltip: `Total events: ${events.length}. Click to see all event types in detail.`
      });
    }

    // System health insights
    if (recentCheckCycles.length === 0 && recentEvents.length === 0) {
      insights.push({
        type: 'warning',
        icon: '⚠️',
        title: 'No Recent Activity',
        message: 'Scheduler hasn\'t run any check cycles in the last 24 hours. System may be paused or experiencing issues.',
        severity: 'warning'
      });
    } else if (recentCheckCycles.length > 0 && successRate < 80) {
      insights.push({
        type: 'error',
        icon: '❌',
        title: 'High Failure Rate',
        message: `Recent task success rate is only ${successRate.toFixed(1)}%. Check for API issues or configuration problems.`,
        severity: 'error',
        tooltip: `Success rate: ${successRate.toFixed(1)}%. ${totalTasksFailed} failures out of ${totalTasksExecuted} tasks. Click to filter failed tasks.`
      });
    } else if (successRate >= 95) {
      insights.push({
        type: 'success',
        icon: '✅',
        title: 'System Operating Normally',
        message: `Task success rate is ${successRate.toFixed(1)}% with ${totalTasksExecuted} tasks executed in the last 24 hours.`,
        severity: 'success',
        tooltip: `Excellent performance! ${successRate.toFixed(1)}% success rate with ${totalTasksExecuted} tasks completed.`
      });
    }

    // Performance insights
    if (avgCheckDuration > 30) {
      insights.push({
        type: 'warning',
        icon: '⏱️',
        title: 'Slow Performance',
        message: `Average check cycle duration is ${avgCheckDuration.toFixed(1)}s. Consider optimizing task execution.`,
        severity: 'warning',
        tooltip: `Check cycles are taking longer than expected (${avgCheckDuration.toFixed(1)}s average). This may indicate performance issues.`
      });
    }

    // Cost optimization insights
    const expensiveFailures = recentFailures.filter(e =>
      e.error_message && (
        e.error_message.toLowerCase().includes('api limit') ||
        e.error_message.toLowerCase().includes('rate limit') ||
        e.error_message.toLowerCase().includes('quota')
      )
    );

    if (expensiveFailures.length > 0) {
      insights.push({
        type: 'error',
        icon: '💰',
        title: 'Cost Alert',
        message: `${expensiveFailures.length} expensive API failures detected. Review usage limits and billing.`,
        severity: 'error',
        tooltip: `${expensiveFailures.length} API failures that wasted expensive resources. Check rate limits, authentication, and quota usage.`,
        filterKey: 'job_failed'
      });
    }

    // Recent highlights
    if (recentFailures.length > 0) {
      insights.push({
        type: 'info',
        icon: '🔍',
        title: 'Recent Issues',
        message: `${recentFailures.length} task failures in the last 24 hours. Check error details below.`,
        severity: 'info',
        tooltip: `${recentFailures.length} tasks failed recently. Click to filter and see failure details.`,
        filterKey: 'job_failed'
      });
    }

    // Interval adjustments
    const intervalChanges = recentEvents.filter(e => e.event_type === 'interval_adjustment');
    if (intervalChanges.length > 0) {
      const latestChange = intervalChanges[intervalChanges.length - 1];
      insights.push({
        type: 'info',
        icon: '⚙️',
        title: 'Auto-Scaling Active',
        message: `Check interval adjusted to ${latestChange.new_interval_minutes}min (${latestChange.previous_interval_minutes}min → ${latestChange.new_interval_minutes}min)`,
        severity: 'info',
        tooltip: `System automatically adjusted check interval from ${latestChange.previous_interval_minutes}min to ${latestChange.new_interval_minutes}min based on load.`,
        filterKey: 'interval_adjustment'
      });
    }

    // Add detailed event type insights
    if (events.length > 0) {
      const eventTypeStats = events.reduce((acc, event) => {
        acc[event.event_type] = (acc[event.event_type] || 0) + 1;
        return acc;
      }, {} as Record<string, number>);

      // Show insights for different event types
      Object.entries(eventTypeStats).forEach(([eventType, count]) => {
        const recentCount = recentEvents.filter(e => e.event_type === eventType).length;
        const sampleEvent = events.find(e => e.event_type === eventType);

        let insight = null;
        switch (eventType) {
          case 'check_cycle':
            insight = {
              type: 'success',
              icon: '📊',
              title: 'Check Cycles Active',
              message: `${count} total cycles, ${recentCount} in last 24h. Last cycle: ${sampleEvent?.tasks_found || 0} found, ${sampleEvent?.tasks_executed || 0} executed, ${sampleEvent?.tasks_failed || 0} failed.`,
              severity: 'success',
              tooltip: `${count} scheduler check cycles completed. Click to filter and see detailed cycle performance.`,
              filterKey: 'check_cycle'
            };
            break;
          case 'job_completed':
            insight = {
              type: 'success',
              icon: '✅',
              title: 'Task Completions',
              message: `${count} tasks completed successfully. Recent: ${recentCount} in last 24h.`,
              severity: 'success',
              tooltip: `${count} tasks completed successfully. Click to filter and see successful task executions.`,
              filterKey: 'job_completed'
            };
            break;
          case 'job_failed':
            insight = {
              type: 'warning',
              icon: '❌',
              title: 'Task Failures',
              message: `${count} task failures detected. Recent: ${recentCount} in last 24h. Check error details below.`,
              severity: 'warning',
              tooltip: `${count} tasks failed. Click to filter and see failure details and error messages.`,
              filterKey: 'job_failed'
            };
            break;
          case 'interval_adjustment':
            insight = {
              type: 'info',
              icon: '⚙️',
              title: 'Auto-Scaling Active',
              message: `${count} interval adjustments made. System adapting to load patterns.`,
              severity: 'info',
              tooltip: `${count} automatic interval adjustments made. Click to see how the system adapts to load.`,
              filterKey: 'interval_adjustment'
            };
            break;
          case 'job_scheduled':
            insight = {
              type: 'info',
              icon: '📅',
              title: 'Task Scheduling',
              message: `${count} tasks scheduled. Recent: ${recentCount} in last 24h.`,
              severity: 'info',
              tooltip: `${count} tasks scheduled for execution. Click to see upcoming and recent scheduling activity.`,
              filterKey: 'job_scheduled'
            };
            break;
        }

        if (insight) {
          insights.push(insight);
        }
      });

      // Limit insights to top 6 most relevant
      insights.sort((a, b) => {
        const priority = { error: 3, warning: 2, success: 1, info: 0 };
        return priority[b.severity as keyof typeof priority] - priority[a.severity as keyof typeof priority];
      });

      return insights.slice(0, 6);
    }

    return insights;
  };

  if (loading && events.length === 0) {
    return (
      <TerminalPaper>
        <Box p={3}>
          <TerminalTypography variant="h6" gutterBottom>
            📜 Scheduler Event History
          </TerminalTypography>
          <TerminalTypography variant="body2" sx={{ color: terminalColors.info }}>
            Loading event history...
          </TerminalTypography>
        </Box>
      </TerminalPaper>
    );
  }

  if (error) {
    return (
      <TerminalPaper>
        <Box p={3}>
          <TerminalTypography variant="h6" gutterBottom>
            📜 Scheduler Event History
          </TerminalTypography>
          <TerminalTypography variant="body2" sx={{ color: terminalColors.error }}>
            Error: {error}
          </TerminalTypography>
        </Box>
      </TerminalPaper>
    );
  }

  // Generate insights from current events
  const insights = generateInsights();

  // Filter events based on selected insight
  const filteredEvents = selectedInsightFilter
    ? events.filter(event => {
        switch (selectedInsightFilter) {
          case 'check_cycle':
            return event.event_type === 'check_cycle';
          case 'job_completed':
            return event.event_type === 'job_completed';
          case 'job_failed':
            return event.event_type === 'job_failed';
          case 'interval_adjustment':
            return event.event_type === 'interval_adjustment';
          case 'job_scheduled':
            return event.event_type === 'job_scheduled';
          default:
            return true;
        }
      })
    : events;

  // Debug logging (remove in production)
  console.log('🔍 Event History Debug:', {
    totalEvents: events.length,
    insightsGenerated: insights.length,
    filteredEventsCount: filteredEvents.length,
    selectedFilter: selectedInsightFilter,
    recentEventsCount: events.filter(e => e.event_date && new Date(e.event_date) > new Date(Date.now() - 24 * 60 * 60 * 1000)).length,
    eventTypes: [...new Set(events.map(e => e.event_type))]
  });

  return (
    <TerminalPaper
      onMouseEnter={handleMouseEnter}
      sx={{
        cursor: isExpanded ? 'default' : 'pointer',
        transition: 'all 0.2s ease-in-out',
        '&:hover': {
          boxShadow: isExpanded ? undefined : '0 4px 8px rgba(0,0,0,0.2)',
        }
      }}
    >
      <Box p={2}>
        {/* Insights Summary Section */}
        <Box mb={3}>
          <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
            <TerminalTypography variant="h6">
              🔍 System Insights
            </TerminalTypography>
            <IconButton
              size="small"
              onClick={() => setInsightsExpanded(!insightsExpanded)}
              sx={{ color: terminalColors.primary }}
            >
              {insightsExpanded ? <ExpandMoreIcon /> : <ExpandMoreIcon sx={{ transform: 'rotate(180deg)' }} />}
            </IconButton>
          </Box>

          <Collapse in={insightsExpanded}>
            {insights.length === 0 ? (
              <TerminalAlert severity="info" icon={<InfoIcon />}>
                No insights available. System operating normally.
              </TerminalAlert>
            ) : (
              <Box>
                {/* Active Filter Indicator */}
                {selectedInsightFilter && (
                  <Box mb={2}>
                    <Chip
                      label={`Filtering: ${selectedInsightFilter.replace('_', ' ').toUpperCase()}`}
                      onDelete={() => setSelectedInsightFilter(null)}
                      sx={{
                        backgroundColor: terminalColors.primary,
                        color: '#000',
                        '& .MuiChip-deleteIcon': {
                          color: '#000',
                        }
                      }}
                      size="small"
                    />
                  </Box>
                )}

                <Box display="grid" gap={1} sx={{
                  gridTemplateColumns: {
                    xs: '1fr',
                    sm: 'repeat(2, 1fr)',
                    md: 'repeat(3, 1fr)'
                  }
                }}>
                  {insights.map((insight: any, index: number) => (
                    <Tooltip
                      key={index}
                      title={`${insight.title}: ${insight.tooltip || 'Click to filter events of this type'}`}
                      arrow
                      placement="top"
                    >
                      <TerminalPaper
                        onClick={() => {
                          if (insight.filterKey) {
                            setSelectedInsightFilter(
                              selectedInsightFilter === insight.filterKey ? null : insight.filterKey
                            );
                          }
                        }}
                        sx={{
                          p: 1.5, // Reduced from p: 2
                          border: `1px solid ${getInsightBorderColor(insight.severity)}`,
                          backgroundColor: getInsightBackgroundColor(insight.severity),
                          cursor: insight.filterKey ? 'pointer' : 'default',
                          transition: 'all 0.2s ease',
                          '&:hover': {
                            backgroundColor: getInsightHoverColor(insight.severity),
                            transform: insight.filterKey ? 'translateY(-2px)' : 'none',
                            boxShadow: insight.filterKey ? '0 4px 8px rgba(0,0,0,0.3)' : 'none',
                          }
                        }}
                      >
                        <Box display="flex" alignItems="center" gap={1}>
                          <Typography variant="body1" sx={{ fontSize: '1rem' }}>
                            {insight.icon}
                          </Typography>
                          <Box flex={1} minWidth={0}>
                            <TerminalTypography variant="body2" sx={{
                              fontWeight: 'bold',
                              color: getInsightTextColor(insight.severity),
                              fontSize: '0.8rem', // Smaller font
                              mb: 0.25,
                              lineHeight: 1.2
                            }}>
                              {insight.title}
                            </TerminalTypography>
                            <TerminalTypography variant="caption" sx={{
                              color: terminalColors.textSecondary,
                              fontSize: '0.7rem', // Smaller font
                              lineHeight: 1.3,
                              display: '-webkit-box',
                              WebkitLineClamp: 2,
                              WebkitBoxOrient: 'vertical',
                              overflow: 'hidden'
                            }}>
                              {insight.message}
                            </TerminalTypography>
                          </Box>
                        </Box>
                      </TerminalPaper>
                    </Tooltip>
                  ))}
                </Box>
              </Box>
            )}
          </Collapse>
        </Box>

        <Divider sx={{ borderColor: terminalColors.primary, opacity: 0.3, mb: 2 }} />

        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2} flexWrap="wrap" gap={2}>
          <TerminalTypography variant="h6">
            📜 Scheduler Event History
            {!isExpanded && (
              <Tooltip title="Hover to expand and see more events with pagination">
                <Typography
                  component="span"
                  sx={{
                    fontSize: '0.7rem',
                    color: terminalColors.info,
                    ml: 1,
                    fontStyle: 'italic'
                  }}
                >
                  (Hover to expand)
                </Typography>
              </Tooltip>
            )}
          </TerminalTypography>
          <Box display="flex" gap={2} flexWrap="wrap">
            <FormControl size="small" sx={{ minWidth: 150 }}>
              <InputLabel sx={{ color: terminalColors.primary }}>Days</InputLabel>
              <Select
                value={daysFilter}
                onChange={(e) => {
                  setDaysFilter(e.target.value as number);
                  setPage(0);
                }}
                sx={{
                  color: terminalColors.primary,
                  '& .MuiOutlinedInput-notchedOutline': {
                    borderColor: terminalColors.primary,
                  },
                  '& .MuiSvgIcon-root': {
                    color: terminalColors.primary,
                  }
                }}
              >
                <MenuItem value={1}>Last 1 day</MenuItem>
                <MenuItem value={3}>Last 3 days</MenuItem>
                <MenuItem value={7}>Last 7 days</MenuItem>
                <MenuItem value={14}>Last 14 days</MenuItem>
                <MenuItem value={30}>Last 30 days</MenuItem>
                <MenuItem value={90}>Last 90 days</MenuItem>
              </Select>
            </FormControl>
            <FormControl size="small" sx={{ minWidth: 200 }}>
              <InputLabel sx={{ color: terminalColors.primary }}>Event Type</InputLabel>
              <Select
                value={eventTypeFilter}
                onChange={(e) => {
                  setEventTypeFilter(e.target.value);
                  setPage(0);
                }}
                sx={{
                  color: terminalColors.primary,
                  '& .MuiOutlinedInput-notchedOutline': {
                    borderColor: terminalColors.primary,
                  },
                  '& .MuiSvgIcon-root': {
                    color: terminalColors.primary,
                  }
                }}
              >
                <MenuItem value="all">All Events</MenuItem>
                <MenuItem value="check_cycle">Check Cycles</MenuItem>
                <MenuItem value="interval_adjustment">Interval Adjustments</MenuItem>
                <MenuItem value="start">Scheduler Start</MenuItem>
                <MenuItem value="stop">Scheduler Stop</MenuItem>
                <MenuItem value="job_scheduled">Job Scheduled</MenuItem>
                <MenuItem value="job_completed">Job Completed</MenuItem>
                <MenuItem value="job_failed">Job Failed</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </Box>

        {events.length === 0 ? (
          <Box p={3} textAlign="center">
            <TerminalTypography variant="body2" sx={{ color: terminalColors.info }}>
              No scheduler events found. Events will appear here as the scheduler runs.
            </TerminalTypography>
          </Box>
        ) : (
          <>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TerminalTableCell>Date</TerminalTableCell>
                    <TerminalTableCell>Event Type</TerminalTableCell>
                    <TerminalTableCell>Details</TerminalTableCell>
                    {(events.some(e => e.event_type === 'job_failed' && e.error_message)) && (
                      <TerminalTableCell>Error</TerminalTableCell>
                    )}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredEvents.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((event) => (
                    <TerminalTableRow key={event.id}>
                      <TerminalTableCell>
                        <TerminalTypography variant="body2" fontSize="0.75rem">
                          {formatDate(event.event_date)}
                        </TerminalTypography>
                      </TerminalTableCell>
                      <TerminalTableCell>
                        <Chip
                          label={event.event_type}
                          size="small"
                          sx={{
                            backgroundColor: getEventTypeColor(event.event_type),
                            color: '#000',
                            fontFamily: 'inherit',
                            fontSize: '0.7rem',
                            fontWeight: 'bold'
                          }}
                        />
                      </TerminalTableCell>
                      <TerminalTableCell>
                        <TerminalTypography variant="body2" fontSize="0.75rem" sx={{ 
                          color: getEventTypeColor(event.event_type),
                          fontFamily: 'monospace'
                        }}>
                          {formatEventDetails(event)}
                        </TerminalTypography>
                      </TerminalTableCell>
                      {event.event_type === 'job_failed' && event.error_message && (
                        <TerminalTableCell>
                          <Tooltip title={event.error_message} arrow>
                            <TerminalTypography variant="body2" fontSize="0.7rem" sx={{ 
                              color: terminalColors.error,
                              fontFamily: 'monospace',
                              maxWidth: '300px',
                              wordBreak: 'break-word',
                              wordWrap: 'break-word',
                              overflowWrap: 'break-word',
                              whiteSpace: 'normal',
                              overflow: 'hidden',
                              display: '-webkit-box',
                              WebkitLineClamp: 3,
                              WebkitBoxOrient: 'vertical'
                            }}>
                              {event.error_message}
                            </TerminalTypography>
                          </Tooltip>
                        </TerminalTableCell>
                      )}
                      {event.event_type !== 'job_failed' && events.some(e => e.event_type === 'job_failed' && e.error_message) && (
                        <TerminalTableCell></TerminalTableCell>
                      )}
                    </TerminalTableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>

            {isExpanded && (
              <TablePagination
                component="div"
                count={filteredEvents.length}
                page={page}
                onPageChange={handleChangePage}
                rowsPerPage={rowsPerPage}
                onRowsPerPageChange={handleChangeRowsPerPage}
                rowsPerPageOptions={[10, 25, 50, 100]}
                sx={{
                  color: terminalColors.primary,
                  '& .MuiTablePagination-selectLabel, & .MuiTablePagination-displayedRows': {
                    color: terminalColors.primary,
                  },
                  '& .MuiIconButton-root': {
                    color: terminalColors.primary,
                  }
                }}
              />
            )}
            {!isExpanded && (
              <Box p={2} textAlign="center">
                <TerminalTypography variant="body2" sx={{ color: terminalColors.info, fontStyle: 'italic' }}>
                  {selectedInsightFilter
                    ? `Showing ${filteredEvents.length} filtered events (${totalCount} total). Hover to expand and see more with pagination.`
                    : `Showing ${Math.min(events.length, 5)} of ${totalCount} events. Hover to expand and see more with pagination.`
                  }
                </TerminalTypography>
              </Box>
            )}
          </>
        )}
      </Box>
    </TerminalPaper>
  );
};

export default SchedulerEventHistory;

