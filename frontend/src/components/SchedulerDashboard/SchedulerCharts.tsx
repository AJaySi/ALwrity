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
import { Box, Paper, CircularProgress } from '@mui/material';
import { TerminalTypography, TerminalPaper, terminalColors } from './terminalTheme';
import { getSchedulerEventHistory, SchedulerEvent } from '../../api/schedulerDashboard';

interface SchedulerChartsProps {
  // Optional: can receive events as prop or fetch them internally
  events?: SchedulerEvent[];
}

const SchedulerCharts: React.FC<SchedulerChartsProps> = ({ events: propEvents }) => {
  const [events, setEvents] = useState<SchedulerEvent[]>(propEvents || []);
  const [loading, setLoading] = useState(!propEvents);
  const [error, setError] = useState<string | null>(null);

  // Fetch events if not provided as prop
  useEffect(() => {
    if (!propEvents) {
      const fetchEvents = async () => {
        try {
          setLoading(true);
          setError(null);
          // Fetch all events for visualization (no pagination limit)
          // Pass undefined to get all event types
          console.log('📊 Charts - Fetching event history...');
          const response = await getSchedulerEventHistory(1000, 0, undefined);
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
  }, [propEvents]);

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

  // Custom tooltip with terminal theme
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <Paper
          sx={{
            backgroundColor: terminalColors.background,
            border: `1px solid ${terminalColors.primary}`,
            padding: 1,
            fontFamily: 'monospace'
          }}
        >
          <TerminalTypography variant="body2" sx={{ color: terminalColors.primary, fontWeight: 'bold', mb: 0.5 }}>
            {label}
          </TerminalTypography>
          {payload.map((entry: any, index: number) => (
            <TerminalTypography
              key={index}
              variant="body2"
              sx={{ color: entry.color, fontSize: '0.75rem' }}
            >
              {entry.name}: {entry.value}
            </TerminalTypography>
          ))}
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

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      {/* Summary Stats */}
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 2 }}>
        <TerminalPaper sx={{ p: 2, textAlign: 'center' }}>
          <TerminalTypography variant="h6" sx={{ color: terminalColors.primary, fontSize: '1.5rem' }}>
            {totals.check_cycles}
          </TerminalTypography>
          <TerminalTypography variant="caption" sx={{ color: terminalColors.textSecondary, fontSize: '0.75rem' }}>
            Check Cycles
          </TerminalTypography>
        </TerminalPaper>
        <TerminalPaper sx={{ p: 2, textAlign: 'center' }}>
          <TerminalTypography variant="h6" sx={{ color: terminalColors.primary, fontSize: '1.5rem' }}>
            {totals.tasks_executed}
          </TerminalTypography>
          <TerminalTypography variant="caption" sx={{ color: terminalColors.textSecondary, fontSize: '0.75rem' }}>
            Tasks Executed
          </TerminalTypography>
        </TerminalPaper>
        <TerminalPaper sx={{ p: 2, textAlign: 'center' }}>
          <TerminalTypography variant="h6" sx={{ color: terminalColors.error, fontSize: '1.5rem' }}>
            {totals.tasks_failed}
          </TerminalTypography>
          <TerminalTypography variant="caption" sx={{ color: terminalColors.textSecondary, fontSize: '0.75rem' }}>
            Tasks Failed
          </TerminalTypography>
        </TerminalPaper>
        <TerminalPaper sx={{ p: 2, textAlign: 'center' }}>
          <TerminalTypography variant="h6" sx={{ color: terminalColors.primary, fontSize: '1.5rem' }}>
            {totals.job_completed}
          </TerminalTypography>
          <TerminalTypography variant="caption" sx={{ color: terminalColors.textSecondary, fontSize: '0.75rem' }}>
            Jobs Completed
          </TerminalTypography>
        </TerminalPaper>
        <TerminalPaper sx={{ p: 2, textAlign: 'center' }}>
          <TerminalTypography variant="h6" sx={{ color: terminalColors.error, fontSize: '1.5rem' }}>
            {totals.job_failed}
          </TerminalTypography>
          <TerminalTypography variant="caption" sx={{ color: terminalColors.textSecondary, fontSize: '0.75rem' }}>
            Jobs Failed
          </TerminalTypography>
        </TerminalPaper>
      </Box>

      {/* Task Execution Trends */}
      <TerminalPaper sx={{ p: 3 }}>
        <TerminalTypography variant="h6" sx={{ mb: 2, color: terminalColors.primary }}>
          Task Execution Trends (Last 30 Days)
        </TerminalTypography>
        <ResponsiveContainer width="100%" height={300}>
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
            <Tooltip content={<CustomTooltip />} />
            <Legend 
              wrapperStyle={{ color: terminalColors.primary, fontFamily: 'monospace' }}
            />
            <Line 
              type="monotone" 
              dataKey="tasks_found" 
              stroke={terminalColors.info}
              strokeWidth={2}
              name="Tasks Found"
              dot={{ fill: terminalColors.info, r: 4 }}
            />
            <Line 
              type="monotone" 
              dataKey="tasks_executed" 
              stroke={terminalColors.success}
              strokeWidth={2}
              name="Tasks Executed"
              dot={{ fill: terminalColors.success, r: 4 }}
            />
            <Line 
              type="monotone" 
              dataKey="tasks_failed" 
              stroke={terminalColors.error}
              strokeWidth={2}
              name="Tasks Failed"
              dot={{ fill: terminalColors.error, r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </TerminalPaper>

      {/* Job Status Distribution */}
      <TerminalPaper sx={{ p: 3 }}>
        <TerminalTypography variant="h6" sx={{ mb: 2, color: terminalColors.primary }}>
          Job Status Distribution (Last 30 Days)
        </TerminalTypography>
        <ResponsiveContainer width="100%" height={300}>
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
            <Tooltip content={<CustomTooltip />} />
            <Legend 
              wrapperStyle={{ color: terminalColors.primary, fontFamily: 'monospace' }}
            />
            <Bar 
              dataKey="job_scheduled" 
              fill={terminalColors.info}
              name="Scheduled"
            />
            <Bar 
              dataKey="job_completed" 
              fill={terminalColors.success}
              name="Completed"
            />
            <Bar 
              dataKey="job_failed" 
              fill={terminalColors.error}
              name="Failed"
            />
          </BarChart>
        </ResponsiveContainer>
      </TerminalPaper>

      {/* Check Cycles Over Time */}
      <TerminalPaper sx={{ p: 3 }}>
        <TerminalTypography variant="h6" sx={{ mb: 2, color: terminalColors.primary }}>
          Check Cycles Over Time (Last 30 Days)
        </TerminalTypography>
        <ResponsiveContainer width="100%" height={300}>
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
            <Tooltip content={<CustomTooltip />} />
            <Bar 
              dataKey="check_cycles" 
              fill={terminalColors.primary}
              name="Check Cycles"
            />
          </BarChart>
        </ResponsiveContainer>
      </TerminalPaper>
    </Box>
  );
};

export default SchedulerCharts;

