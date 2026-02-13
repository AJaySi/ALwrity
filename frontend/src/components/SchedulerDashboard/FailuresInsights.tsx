/**
 * Failures & Insights Component
 * Displays recent failures, error messages, and scheduler insights.
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  AccordionSummary,
  AccordionDetails,
  Divider,
  CircularProgress
} from '@mui/material';
import {
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import { useAuth } from '@clerk/clerk-react';
import {
  getExecutionLogs,
  getRecentSchedulerLogs,
  ExecutionLog,
  getTasksNeedingIntervention
} from '../../api/schedulerDashboard';
import { SchedulerStats } from '../../api/schedulerDashboard';
import { 
  TerminalPaper, 
  TerminalTypography, 
  TerminalAlert,
  TerminalAccordion,
  terminalColors 
} from './terminalTheme';

interface FailuresInsightsProps {
  stats: SchedulerStats;
}

const FailuresInsights: React.FC<FailuresInsightsProps> = ({ stats }) => {
  const { userId } = useAuth();
  const [recentFailures, setRecentFailures] = useState<ExecutionLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchFailures = async () => {
      try {
        setLoading(true);

        // Get tasks needing intervention (includes failed OAuth, website analysis, platform insights tasks)
        // Note: This API only returns tasks marked as "needs_intervention", not all failed tasks
        const tasksNeedingIntervention = await getTasksNeedingIntervention(userId || '');

        // Get execution logs with failed status (general monitoring tasks)
        const executionLogsResponse = await getExecutionLogs(10, 0, 'failed');

        // Get scheduler logs (which include job_failed events)
        const schedulerLogsResponse = await getRecentSchedulerLogs();

        // Convert tasks needing intervention to ExecutionLog-like format
        const interventionFailures: ExecutionLog[] = tasksNeedingIntervention.map(task => ({
          id: task.task_id,
          task_id: task.task_id,
          user_id: task.user_id,
          execution_date: task.last_failure || new Date().toISOString(),
          status: 'failed' as const,
          error_message: task.failure_reason || `Task failed: ${task.failure_pattern.failure_reason}`,
          execution_time_ms: null,
          result_data: null,
          created_at: task.last_failure || new Date().toISOString(),
          task: {
            id: task.task_id,
            task_title: task.task_type,
            component_name: task.platform || 'Monitoring',
            metric: task.task_type,
            frequency: 'recurring'
          },
          is_scheduler_log: false
        }));

        // Combine all failure sources with unique identifiers for React keys
        const allFailures: (ExecutionLog & { reactKey: string })[] = [
          // Add source prefix to avoid key conflicts
          ...interventionFailures.map(log => ({ ...log, reactKey: `intervention_${log.id}` })),
          ...executionLogsResponse.logs.filter(log => log.status === 'failed').map(log => ({ ...log, reactKey: `execution_${log.id}` })),
          ...(schedulerLogsResponse.logs || []).filter(log => log.status === 'failed').map(log => ({ ...log, reactKey: `scheduler_${log.id}` }))
        ];

        // Sort by execution_date descending (most recent first) and limit to 10
        allFailures.sort((a, b) => {
          const dateA = new Date(a.execution_date).getTime();
          const dateB = new Date(b.execution_date).getTime();
          return dateB - dateA;
        });

        setRecentFailures(allFailures.slice(0, 10));
      } catch (err: any) {
        setError(err.message || 'Failed to fetch failures');
        console.error('Error fetching failures:', err);
      } finally {
        setLoading(false);
      }
    };

    if (userId) {
      fetchFailures();
    }
  }, [userId]);

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString();
    } catch {
      return dateString;
    }
  };

  // Generate insights based on stats
  const generateInsights = () => {
    const insights: Array<{ type: 'info' | 'warning' | 'error' | 'success'; message: string }> = [];

    // Scheduler status insight
    if (!stats.running) {
      insights.push({
        type: 'error',
        message: 'Scheduler is stopped. Tasks will not be executed until scheduler is restarted.'
      });
    } else {
      insights.push({
        type: 'success',
        message: 'Scheduler is running and processing tasks normally.'
      });
    }

    // Active strategies insight
    if (stats.active_strategies_count === 0) {
      insights.push({
        type: 'info',
        message: `No active strategies detected. Using ${stats.max_check_interval_minutes}min check interval (idle mode).`
      });
    } else {
      insights.push({
        type: 'info',
        message: `${stats.active_strategies_count} active strategy(ies) with monitoring tasks. Using ${stats.min_check_interval_minutes}min check interval.`
      });
    }

    // Failure rate insight
    const totalExecutions = stats.tasks_executed + stats.tasks_failed;
    if (totalExecutions > 0) {
      const failureRate = (stats.tasks_failed / totalExecutions) * 100;
      if (failureRate > 20) {
        insights.push({
          type: 'error',
          message: `High failure rate: ${failureRate.toFixed(1)}% of tasks are failing. Review error logs for details.`
        });
      } else if (failureRate > 10) {
        insights.push({
          type: 'warning',
          message: `Moderate failure rate: ${failureRate.toFixed(1)}% of tasks are failing. Monitor for patterns.`
        });
      } else if (stats.tasks_failed > 0) {
        insights.push({
          type: 'info',
          message: `Low failure rate: ${failureRate.toFixed(1)}% of tasks are failing. System is healthy.`
        });
      }
    }

    // Check interval insight
    if (stats.intelligent_scheduling) {
      insights.push({
        type: 'success',
        message: `Intelligent scheduling enabled. Interval automatically adjusts based on active strategies (${stats.min_check_interval_minutes}-${stats.max_check_interval_minutes}min range).`
      });
    }

    // Last check insight
    if (stats.last_check) {
      try {
        const lastCheck = new Date(stats.last_check);
        const now = new Date();
        const diffMins = Math.floor((now.getTime() - lastCheck.getTime()) / 60000);
        
        if (diffMins > stats.check_interval_minutes * 2) {
          insights.push({
            type: 'warning',
            message: `Last check was ${diffMins} minutes ago. Expected interval is ${stats.check_interval_minutes} minutes. Scheduler may be delayed.`
          });
        }
      } catch {
        // Ignore date parsing errors
      }
    }

    return insights;
  };

  const insights = generateInsights();

  return (
    <TerminalPaper sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box display="flex" alignItems="center" gap={1} mb={2}>
        <InfoIcon sx={{ color: terminalColors.primary }} />
        <TerminalTypography variant="h6" component="h2" sx={{ fontSize: '1.25rem', fontWeight: 'bold' }}>
          Failures & Insights
        </TerminalTypography>
      </Box>
      
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>

      {/* Recent Failures */}
      <Box mb={3} sx={{ flexShrink: 0 }}>
        <TerminalTypography variant="subtitle1" fontWeight="medium" mb={1} sx={{ fontSize: '1rem', color: terminalColors.textSecondary }}>
          Recent Failures ({recentFailures.length})
        </TerminalTypography>
        {loading ? (
          <Box display="flex" justifyContent="center" p={2}>
            <CircularProgress size={24} sx={{ color: terminalColors.primary }} />
          </Box>
        ) : error ? (
          <TerminalAlert severity="error">{error}</TerminalAlert>
        ) : recentFailures.length === 0 ? (
          <TerminalAlert severity="success" icon={<CheckCircleIcon />}>
            No recent failures. All tasks are executing successfully.
          </TerminalAlert>
        ) : (
          <List>
            {recentFailures.map((log, index) => (
              <React.Fragment key={(log as any).reactKey || log.id}>
                <TerminalAccordion>
                  <AccordionSummary 
                    expandIcon={<ExpandMoreIcon sx={{ color: terminalColors.primary }} />}
                    sx={{ 
                      '&:hover': {
                        backgroundColor: 'rgba(0, 255, 0, 0.05)',
                      }
                    }}
                  >
                    <Box display="flex" alignItems="center" gap={1} width="100%">
                      <ErrorIcon sx={{ color: terminalColors.error }} fontSize="small" />
                      <TerminalTypography variant="body2" sx={{ flexGrow: 1, fontSize: '0.875rem' }}>
                        {log.task?.task_title || `Task #${log.task_id}`}
                      </TerminalTypography>
                      <TerminalTypography variant="caption" sx={{ color: terminalColors.textSecondary, fontSize: '0.75rem' }}>
                        {formatDate(log.execution_date)}
                      </TerminalTypography>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails sx={{ backgroundColor: terminalColors.background }}>
                    <Box>
                      <TerminalTypography variant="body2" gutterBottom sx={{ color: terminalColors.textSecondary, fontSize: '0.875rem' }}>
                        <strong style={{ color: terminalColors.primary }}>Component:</strong> {log.task?.component_name || 'Unknown'}
                      </TerminalTypography>
                      {log.error_message && (
                        <Box sx={{ mt: 1, p: 1, border: `1px solid ${terminalColors.error}`, borderRadius: 1, backgroundColor: terminalColors.backgroundLight }}>
                          <TerminalTypography variant="body2" fontWeight="bold" gutterBottom sx={{ color: terminalColors.error, fontSize: '0.875rem' }}>
                            Error Message
                          </TerminalTypography>
                          <TerminalTypography variant="body2" sx={{ color: terminalColors.error, fontSize: '0.875rem', fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}>
                            {log.error_message}
                          </TerminalTypography>
                        </Box>
                      )}
                      {log.execution_time_ms && (
                        <TerminalTypography variant="caption" sx={{ mt: 1, display: 'block', color: terminalColors.textSecondary, fontSize: '0.75rem' }}>
                          Execution time: {log.execution_time_ms}ms
                        </TerminalTypography>
                      )}
                      {log.user_id && (
                        <TerminalTypography variant="caption" sx={{ mt: 0.5, display: 'block', color: terminalColors.textSecondary, fontSize: '0.75rem' }}>
                          User ID: {log.user_id}
                        </TerminalTypography>
                      )}
                    </Box>
                  </AccordionDetails>
                </TerminalAccordion>
                {index < recentFailures.length - 1 && <Divider sx={{ borderColor: terminalColors.border }} />}
              </React.Fragment>
            ))}
          </List>
        )}
      </Box>

      <Divider sx={{ my: 3, borderColor: terminalColors.border, flexShrink: 0 }} />

      {/* Scheduler Insights */}
      <Box sx={{ flex: 1, overflow: 'auto', minHeight: 0, flexShrink: 1 }}>
        <TerminalTypography variant="subtitle1" fontWeight="medium" mb={1} sx={{ fontSize: '1rem', color: terminalColors.textSecondary }}>
          Scheduler Insights
        </TerminalTypography>
        <List>
          {insights.map((insight, index) => (
            <React.Fragment key={index}>
              <ListItem>
                <ListItemIcon>
                  {insight.type === 'error' && <ErrorIcon sx={{ color: terminalColors.error }} />}
                  {insight.type === 'warning' && <WarningIcon sx={{ color: terminalColors.warning }} />}
                  {insight.type === 'info' && <InfoIcon sx={{ color: terminalColors.info }} />}
                  {insight.type === 'success' && <CheckCircleIcon sx={{ color: terminalColors.success }} />}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <TerminalTypography
                      variant="body2"
                      sx={{
                        fontSize: '0.875rem',
                        color: insight.type === 'error' ? terminalColors.error : terminalColors.text
                      }}
                    >
                      {insight.message}
                    </TerminalTypography>
                  }
                />
              </ListItem>
              {index < insights.length - 1 && <Divider component="li" sx={{ borderColor: terminalColors.border }} />}
            </React.Fragment>
          ))}
        </List>
      </Box>
      </Box>
    </TerminalPaper>
  );
};

export default FailuresInsights;

