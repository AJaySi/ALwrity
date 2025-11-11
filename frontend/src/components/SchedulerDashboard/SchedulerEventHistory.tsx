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
  Tooltip
} from '@mui/material';
import {
  TerminalPaper,
  TerminalTypography,
  TerminalChipSuccess,
  TerminalChipError,
  TerminalChipWarning,
  TerminalTableCell,
  TerminalTableRow,
  terminalColors
} from './terminalTheme';
import { getSchedulerEventHistory, SchedulerEvent } from '../../api/schedulerDashboard';

interface SchedulerEventHistoryProps {
  limit?: number;
}

const SchedulerEventHistory: React.FC<SchedulerEventHistoryProps> = () => {
  const [events, setEvents] = useState<SchedulerEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [isExpanded, setIsExpanded] = useState(false);
  const [rowsPerPage, setRowsPerPage] = useState(5); // Start with 5, expand to 50 on hover
  const [totalCount, setTotalCount] = useState(0);
  const [eventTypeFilter, setEventTypeFilter] = useState<string>('all');
  const [daysFilter, setDaysFilter] = useState<number>(7);

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
    fetchEvents();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, rowsPerPage, eventTypeFilter, daysFilter]); // fetchEvents is stable, no need to include

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
                  {events.map((event) => (
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
                count={totalCount}
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
            {!isExpanded && totalCount > events.length && (
              <Box p={2} textAlign="center">
                <TerminalTypography variant="body2" sx={{ color: terminalColors.info, fontStyle: 'italic' }}>
                  Showing {events.length} of {totalCount} events. Hover to expand and see more with pagination.
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

