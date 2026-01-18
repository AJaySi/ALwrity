/**
 * Performance Summary Component
 * Displays compact performance metrics as chips or cards
 */

import React, { useMemo } from 'react';
import { Chip, Box, Tooltip } from '@mui/material';
import { TerminalTypography, TerminalPaper, terminalColors } from '../terminalTheme';
import { SchedulerEvent } from '../../../api/schedulerDashboard';

interface PerformanceSummaryProps {
  events: SchedulerEvent[];
  compact?: boolean;
}

export const PerformanceSummary: React.FC<PerformanceSummaryProps> = ({ events, compact = true }) => {
  // Calculate metrics from events
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

  const metrics = useMemo(() => {
    const totalTasksProcessed = totals.tasks_found || (totals.tasks_executed + totals.tasks_failed);
    const successRate = totalTasksProcessed > 0 ?
      ((totals.tasks_executed) / totalTasksProcessed * 100) : 100;

    const avgTasksPerCycle = totals.check_cycles > 0 ?
      totalTasksProcessed / totals.check_cycles : 0;

    return {
      totalTasksProcessed,
      successRate,
      tasksFailed: totals.tasks_failed,
      checkCycles: totals.check_cycles,
      avgTasksPerCycle
    };
  }, [totals]);

  if (compact) {
    return (
      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center' }}>
        <Chip
          label={`${metrics.totalTasksProcessed.toLocaleString()} Tasks`}
          size="small"
          sx={{
            backgroundColor: 'rgba(0, 255, 0, 0.1)',
            border: '1px solid #00ff00',
            color: '#00ff00',
            fontFamily: 'monospace',
            fontSize: '0.75rem',
            fontWeight: 'bold',
            '& .MuiChip-label': {
              padding: '2px 8px',
            },
          }}
        />
        <Chip
          label={`${metrics.successRate.toFixed(0)}% Success`}
          size="small"
          sx={{
            backgroundColor: metrics.successRate >= 95 ? 'rgba(0, 255, 0, 0.1)' :
                          metrics.successRate >= 80 ? 'rgba(255, 152, 0, 0.1)' : 'rgba(244, 67, 54, 0.1)',
            border: `1px solid ${metrics.successRate >= 95 ? '#00ff00' :
                               metrics.successRate >= 80 ? '#ff9800' : '#f44336'}`,
            color: metrics.successRate >= 95 ? '#00ff00' :
                   metrics.successRate >= 80 ? '#ff9800' : '#f44336',
            fontFamily: 'monospace',
            fontSize: '0.75rem',
            fontWeight: 'bold',
            '& .MuiChip-label': {
              padding: '2px 8px',
            },
          }}
        />
        {metrics.tasksFailed > 0 && (
          <Chip
            label={`${metrics.tasksFailed} Failed`}
            size="small"
            sx={{
              backgroundColor: 'rgba(244, 67, 54, 0.1)',
              border: '1px solid #f44336',
              color: '#f44336',
              fontFamily: 'monospace',
              fontSize: '0.75rem',
              fontWeight: 'bold',
              '& .MuiChip-label': {
                padding: '2px 8px',
              },
            }}
          />
        )}
        <Chip
          label={`${metrics.checkCycles} Cycles`}
          size="small"
          sx={{
            backgroundColor: 'rgba(33, 150, 243, 0.1)',
            border: '1px solid #2196f3',
            color: '#2196f3',
            fontFamily: 'monospace',
            fontSize: '0.75rem',
            fontWeight: 'bold',
            '& .MuiChip-label': {
              padding: '2px 8px',
            },
          }}
        />
      </div>
    );
  }

  // Full summary with neon terminal chips (when compact=false)
  return (
    <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center', justifyContent: 'center' }}>
      <Tooltip
        title={
          <Box sx={{ p: 1, maxWidth: 300 }}>
            <TerminalTypography variant="subtitle2" sx={{ color: terminalColors.primary, fontWeight: 'bold', mb: 1 }}>
              📊 Tasks Processed
            </TerminalTypography>
            <TerminalTypography variant="body2" sx={{ color: terminalColors.textSecondary, mb: 1 }}>
              Total tasks discovered and attempted by the scheduler across all check cycles in the selected time period.
            </TerminalTypography>
            <TerminalTypography variant="caption" sx={{ color: terminalColors.info }}>
              • Discovered: {totals.tasks_found} tasks found by scheduler
              <br />
              • Executed: {totals.tasks_executed} tasks successfully completed
              <br />
              • Failed: {totals.tasks_failed} tasks encountered errors
              <br />
              • Check Cycles: {totals.check_cycles} scheduler runs
            </TerminalTypography>
          </Box>
        }
        arrow
        placement="top"
      >
        <Chip
          label={`${metrics.totalTasksProcessed.toLocaleString()} Tasks Processed`}
          sx={{
            backgroundColor: 'rgba(0, 255, 0, 0.15)',
            border: '2px solid #00ff00',
            color: '#00ff00',
            fontFamily: 'monospace',
            fontSize: '0.9rem',
            fontWeight: 'bold',
            boxShadow: '0 0 10px rgba(0, 255, 0, 0.3)',
            '& .MuiChip-label': {
              padding: '8px 12px',
            },
            '&:hover': {
              boxShadow: '0 0 15px rgba(0, 255, 0, 0.5)',
            },
            cursor: 'help',
          }}
        />
      </Tooltip>

      <Tooltip
        title={
          <Box sx={{ p: 1, maxWidth: 300 }}>
            <TerminalTypography variant="subtitle2" sx={{ color: terminalColors.primary, fontWeight: 'bold', mb: 1 }}>
              🎯 Success Rate
            </TerminalTypography>
            <TerminalTypography variant="body2" sx={{ color: terminalColors.textSecondary, mb: 1 }}>
              Percentage of discovered tasks that were successfully executed without errors.
            </TerminalTypography>
            <TerminalTypography variant="caption" sx={{ color: terminalColors.info }}>
              • Formula: (Successfully Executed ÷ Total Discovered) × 100
              <br />
              • Executed: {totals.tasks_executed} tasks completed successfully
              <br />
              • Total: {metrics.totalTasksProcessed} tasks discovered
              <br />
              • Failed: {totals.tasks_failed} tasks had errors
              <br />
              • Target: ≥95% indicates excellent system performance
              <br />
              • Current: {metrics.successRate.toFixed(1)}% {metrics.successRate >= 95 ? '(Excellent)' : metrics.successRate >= 80 ? '(Good)' : '(Needs Attention)'}
            </TerminalTypography>
          </Box>
        }
        arrow
        placement="top"
      >
        <Chip
          label={`${metrics.successRate.toFixed(1)}% Success Rate`}
          sx={{
            backgroundColor: metrics.successRate >= 95 ? 'rgba(0, 255, 0, 0.15)' :
                          metrics.successRate >= 80 ? 'rgba(255, 152, 0, 0.15)' : 'rgba(244, 67, 54, 0.15)',
            border: `2px solid ${metrics.successRate >= 95 ? '#00ff00' :
                               metrics.successRate >= 80 ? '#ff9800' : '#f44336'}`,
            color: metrics.successRate >= 95 ? '#00ff00' :
                   metrics.successRate >= 80 ? '#ff9800' : '#f44336',
            fontFamily: 'monospace',
            fontSize: '0.9rem',
            fontWeight: 'bold',
            boxShadow: `0 0 10px ${metrics.successRate >= 95 ? 'rgba(0, 255, 0, 0.3)' :
                                 metrics.successRate >= 80 ? 'rgba(255, 152, 0, 0.3)' : 'rgba(244, 67, 54, 0.3)'}`,
            '& .MuiChip-label': {
              padding: '8px 12px',
            },
            '&:hover': {
              boxShadow: `0 0 15px ${metrics.successRate >= 95 ? 'rgba(0, 255, 0, 0.5)' :
                                     metrics.successRate >= 80 ? 'rgba(255, 152, 0, 0.5)' : 'rgba(244, 67, 54, 0.5)'}`,
            },
            cursor: 'help',
          }}
        />
      </Tooltip>

      {metrics.tasksFailed > 0 && (
        <Tooltip
          title={
            <Box sx={{ p: 1, maxWidth: 300 }}>
              <TerminalTypography variant="subtitle2" sx={{ color: terminalColors.primary, fontWeight: 'bold', mb: 1 }}>
                ⚠️ Tasks Failed
              </TerminalTypography>
              <TerminalTypography variant="body2" sx={{ color: terminalColors.textSecondary, mb: 1 }}>
                Tasks that encountered errors during execution and may require manual intervention.
              </TerminalTypography>
              <TerminalTypography variant="caption" sx={{ color: terminalColors.info }}>
                • Total Failed: {totals.tasks_failed} tasks with errors
                <br />
                • Check Cycles: {totals.check_cycles} scheduler runs
                <br />
                • Average per Cycle: {(totals.tasks_failed / Math.max(totals.check_cycles, 1)).toFixed(1)} failures per cycle
                <br />
                • Impact: {(totals.tasks_failed / Math.max(metrics.totalTasksProcessed, 1) * 100).toFixed(1)}% of all discovered tasks
                <br />
                • Status: {totals.tasks_failed === 0 ? 'All systems operating normally' : 'Some tasks need attention - check Failures & Insights'}
              </TerminalTypography>
            </Box>
          }
          arrow
          placement="top"
        >
          <Chip
            label={`${metrics.tasksFailed} Tasks Failed`}
            sx={{
              backgroundColor: 'rgba(244, 67, 54, 0.15)',
              border: '2px solid #f44336',
              color: '#f44336',
              fontFamily: 'monospace',
              fontSize: '0.9rem',
              fontWeight: 'bold',
              boxShadow: '0 0 10px rgba(244, 67, 54, 0.3)',
              '& .MuiChip-label': {
                padding: '8px 12px',
              },
              '&:hover': {
                boxShadow: '0 0 15px rgba(244, 67, 54, 0.5)',
              },
              cursor: 'help',
            }}
          />
        </Tooltip>
      )}

      <Tooltip
        title={
          <Box sx={{ p: 1, maxWidth: 300 }}>
            <TerminalTypography variant="subtitle2" sx={{ color: terminalColors.primary, fontWeight: 'bold', mb: 1 }}>
              🔄 System Activity
            </TerminalTypography>
            <TerminalTypography variant="body2" sx={{ color: terminalColors.textSecondary, mb: 1 }}>
              Number of times the scheduler has checked for tasks to execute. Higher numbers indicate more active monitoring.
            </TerminalTypography>
            <TerminalTypography variant="caption" sx={{ color: terminalColors.info }}>
              • Check Cycles: {totals.check_cycles} monitoring runs
              <br />
              • Time Period: Last 30 days of data
              <br />
              • Tasks per Cycle: {metrics.avgTasksPerCycle.toFixed(1)} tasks discovered per check
              <br />
              • Frequency: Every 10-60 minutes (adapts to load)
              <br />
              • Purpose: Regularly scans for tasks needing execution
            </TerminalTypography>
          </Box>
        }
        arrow
        placement="top"
      >
        <Chip
          label={`${metrics.checkCycles} Check Cycles`}
          sx={{
            backgroundColor: 'rgba(33, 150, 243, 0.15)',
            border: '2px solid #2196f3',
            color: '#2196f3',
            fontFamily: 'monospace',
            fontSize: '0.9rem',
            fontWeight: 'bold',
            boxShadow: '0 0 10px rgba(33, 150, 243, 0.3)',
            '& .MuiChip-label': {
              padding: '8px 12px',
            },
            '&:hover': {
              boxShadow: '0 0 15px rgba(33, 150, 243, 0.5)',
            },
            cursor: 'help',
          }}
        />
      </Tooltip>
    </Box>
  );
};