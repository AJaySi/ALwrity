/**
 * Website Analysis Status Component
 * Compact terminal-themed component for displaying website analysis task status
 * with execution logs in expanded sections
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  IconButton,
  Tooltip,
  CircularProgress,
  Collapse,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Chip,
  Divider,
  Button,
} from '@mui/material';
import {
  RefreshCw,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Info,
  ChevronDown,
  ChevronUp,
  Globe,
  Users,
} from 'lucide-react';
import { useAuth } from '@clerk/clerk-react';
import {
  getWebsiteAnalysisStatus,
  retryWebsiteAnalysis,
  getWebsiteAnalysisLogs,
  WebsiteAnalysisStatusResponse,
  WebsiteAnalysisTask,
  WebsiteAnalysisExecutionLog,
  WebsiteAnalysisLogsResponse,
} from '../../api/websiteAnalysisMonitoring';
import {
  TerminalPaper,
  TerminalTypography,
  TerminalChip,
  TerminalChipSuccess,
  TerminalChipError,
  TerminalChipWarning,
  TerminalAlert,
  TerminalTableCell,
  TerminalTableRow,
  terminalColors,
} from './terminalTheme';

interface WebsiteAnalysisStatusProps {
  compact?: boolean;
}

interface TaskLogs {
  [taskId: number]: {
    logs: WebsiteAnalysisExecutionLog[];
    loading: boolean;
    error: string | null;
  };
}

const WebsiteAnalysisStatus: React.FC<WebsiteAnalysisStatusProps> = ({ compact = true }) => {
  const { userId } = useAuth();
  const [status, setStatus] = useState<WebsiteAnalysisStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [expandedTaskId, setExpandedTaskId] = useState<number | null>(null);
  const [taskLogs, setTaskLogs] = useState<TaskLogs>({});
  const [hoveredLogId, setHoveredLogId] = useState<number | null>(null);
  
  const fetchStatus = async () => {
    if (!userId) return;
    
    try {
      setLoading(true);
      setError(null);
      const response = await getWebsiteAnalysisStatus(userId);
      setStatus(response);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch website analysis status');
      console.error('Error fetching website analysis status:', err);
    } finally {
      setLoading(false);
    }
  };
  
  const fetchTaskLogs = async (taskId: number) => {
    if (!userId) return;
    
    // Initialize task logs state if not exists
    if (!taskLogs[taskId]) {
      setTaskLogs(prev => ({
        ...prev,
        [taskId]: { logs: [], loading: false, error: null }
      }));
    }
    
    // Check if already loading
    if (taskLogs[taskId]?.loading) return;
    
    setTaskLogs(prev => ({
      ...prev,
      [taskId]: { ...prev[taskId], loading: true, error: null }
    }));
    
    try {
      console.log(`[WebsiteAnalysis] Fetching logs for task ${taskId}...`);
      const response = await getWebsiteAnalysisLogs(userId, 10, 0, taskId);
      console.log(`[WebsiteAnalysis] Received logs response:`, {
        logsCount: response.logs?.length || 0,
        totalCount: response.total_count,
        hasLogs: !!(response.logs && response.logs.length > 0),
        firstLog: response.logs?.[0] || null
      });
      
      if (response.logs && Array.isArray(response.logs)) {
        setTaskLogs(prev => ({
          ...prev,
          [taskId]: { logs: response.logs, loading: false, error: null }
        }));
      } else {
        console.warn(`[WebsiteAnalysis] Invalid logs response structure:`, response);
        setTaskLogs(prev => ({
          ...prev,
          [taskId]: { logs: [], loading: false, error: 'Invalid response structure' }
        }));
      }
    } catch (err: any) {
      console.error(`[WebsiteAnalysis] Error fetching logs for task ${taskId}:`, err);
      setTaskLogs(prev => ({
        ...prev,
        [taskId]: { ...prev[taskId], loading: false, error: err.message || 'Failed to fetch logs' }
      }));
    }
  };
  
  const handleRetry = async (taskId: number) => {
    if (!userId) return;
    
    try {
      setRefreshing(taskId);
      await retryWebsiteAnalysis(taskId);
      await fetchStatus(); // Refresh status
    } catch (err: any) {
      console.error('Error retrying website analysis:', err);
      alert(err.message || 'Failed to retry website analysis');
    } finally {
      setRefreshing(null);
    }
  };
  
  const handleToggleExpand = (taskId: number) => {
    if (expandedTaskId === taskId) {
      setExpandedTaskId(null);
    } else {
      setExpandedTaskId(taskId);
      // Always fetch logs when expanding to get latest data
      fetchTaskLogs(taskId);
    }
  };
  
  useEffect(() => {
    fetchStatus();
    // Refresh every 5 minutes (same as other dashboard components)
    // Tasks run on schedule (every 10 days for competitors, etc.), so frequent polling is unnecessary
    const interval = setInterval(fetchStatus, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [userId]);

  // Fetch logs when task is expanded (similar to OAuth pattern)
  useEffect(() => {
    if (expandedTaskId && userId) {
      fetchTaskLogs(expandedTaskId);
    }
  }, [expandedTaskId, userId]);
  
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle size={16} color={terminalColors.success} />;
      case 'failed':
        return <XCircle size={16} color={terminalColors.error} />;
      case 'paused':
        return <AlertTriangle size={16} color={terminalColors.warning} />;
      default:
        return <Info size={16} color={terminalColors.primary} />;
    }
  };
  
  const getStatusChip = (taskStatus: string) => {
    switch (taskStatus) {
      case 'active':
        return <TerminalChipSuccess label="Active" size="small" />;
      case 'failed':
        return <TerminalChipError label="Failed" size="small" />;
      case 'paused':
        return <TerminalChipWarning label="Paused" size="small" />;
      default:
        return <TerminalChip label={taskStatus} size="small" />;
    }
  };
  
  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Never';
    try {
      const date = new Date(dateString);
      return date.toLocaleString();
    } catch {
      return dateString;
    }
  };
  
  const getLogStatusChip = (logStatus: string) => {
    switch (logStatus) {
      case 'success':
        return <TerminalChipSuccess label="Success" size="small" />;
      case 'failed':
        return <TerminalChipError label="Failed" size="small" />;
      case 'running':
        return <TerminalChipWarning label="Running" size="small" />;
      default:
        return <Chip label={logStatus} size="small" />;
    }
  };
  
  const formatLogResult = (resultData: any): string => {
    if (!resultData) return 'N/A';
    if (typeof resultData === 'string') {
      try {
        resultData = JSON.parse(resultData);
      } catch {
        return resultData.substring(0, 50);
      }
    }
    
    if (resultData.style_analysis) {
      return 'Analysis completed';
    }
    if (resultData.crawl_result) {
      return 'Crawl completed';
    }
    const str = JSON.stringify(resultData);
    return str.length > 60 ? str.substring(0, 60) + '...' : str;
  };
  
  if (loading && !status) {
    return (
      <TerminalPaper sx={{ p: 2 }}>
        <Box display="flex" justifyContent="center" alignItems="center" p={2}>
          <CircularProgress size={20} sx={{ color: terminalColors.primary }} />
        </Box>
      </TerminalPaper>
    );
  }
  
  if (!status) {
    return null;
  }
  
  const allTasks = [
    ...status.data.user_website_tasks,
    ...status.data.competitor_tasks
  ];
  
  const renderTaskRow = (task: WebsiteAnalysisTask) => {
    const isExpanded = expandedTaskId === task.id;
    const logs = taskLogs[task.id]?.logs || [];
    const logsLoading = taskLogs[task.id]?.loading || false;
    const logsError = taskLogs[task.id]?.error;
    
    return (
      <React.Fragment key={task.id}>
        <TerminalTableRow
          sx={{
            cursor: 'pointer',
            '&:hover': { backgroundColor: terminalColors.backgroundHover }
          }}
          onClick={() => handleToggleExpand(task.id)}
        >
          <TerminalTableCell>
            <Box display="flex" alignItems="center" gap={1}>
              {task.task_type === 'user_website' ? (
                <Globe size={16} color={terminalColors.primary} />
              ) : (
                <Users size={16} color={terminalColors.secondary} />
              )}
              <TerminalTypography variant="body2" sx={{ fontWeight: 500 }}>
                {task.website_url}
              </TerminalTypography>
            </Box>
          </TerminalTableCell>
          <TerminalTableCell>
            <Box display="flex" alignItems="center" gap={1}>
              {getStatusIcon(task.status)}
              {getStatusChip(task.status)}
            </Box>
          </TerminalTableCell>
          <TerminalTableCell>
            <Box display="flex" alignItems="center" gap={0.5} flexWrap="wrap">
              {task.last_success && (
                <Tooltip title={`Last successful: ${formatDate(task.last_success)}`}>
                  <Chip
                    label={`Last: ${formatDate(task.last_success).split(',')[0]}`}
                    size="small"
                    sx={{
                      height: 20,
                      fontSize: '0.7rem',
                      border: `1px solid ${terminalColors.border}`,
                      backgroundColor: terminalColors.background,
                    }}
                  />
                </Tooltip>
              )}
              {task.next_check && (
                <Tooltip title={`Next check: ${formatDate(task.next_check)}`}>
                  <Chip
                    label={`Next: ${formatDate(task.next_check).split(',')[0]}`}
                    size="small"
                    sx={{
                      height: 20,
                      fontSize: '0.7rem',
                      border: `1px solid ${terminalColors.border}`,
                      backgroundColor: terminalColors.background,
                    }}
                  />
                </Tooltip>
              )}
            </Box>
          </TerminalTableCell>
          <TerminalTableCell>
            <Box display="flex" alignItems="center" gap={1}>
              {task.status === 'failed' && (
                <Button
                  size="small"
                  variant="outlined"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleRetry(task.id);
                  }}
                  disabled={refreshing === task.id}
                  sx={{
                    minWidth: 'auto',
                    px: 1,
                    py: 0.5,
                    fontSize: '0.7rem',
                    borderColor: terminalColors.border,
                    color: terminalColors.text,
                    '&:hover': {
                      borderColor: terminalColors.primary,
                      backgroundColor: terminalColors.backgroundHover,
                    },
                  }}
                >
                  {refreshing === task.id ? <CircularProgress size={12} /> : 'Retry'}
                </Button>
              )}
              <IconButton
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  handleToggleExpand(task.id);
                }}
                sx={{ color: terminalColors.text }}
              >
                {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
              </IconButton>
            </Box>
          </TerminalTableCell>
        </TerminalTableRow>
        
        <TableRow>
          <TableCell colSpan={4} sx={{ py: 0, border: 0 }}>
            <Collapse in={isExpanded} timeout="auto" unmountOnExit>
              <Box sx={{ p: 2, backgroundColor: terminalColors.backgroundSecondary }}>
                {task.failure_reason && (
                  <TerminalAlert severity="error" sx={{ mb: 2 }}>
                    Error: {task.failure_reason}
                  </TerminalAlert>
                )}
                
                <Typography variant="h6" sx={{ mb: 1, color: terminalColors.text, fontSize: '0.9rem' }}>
                  Monitoring Logs
                </Typography>
                
                {logsLoading ? (
                  <Box display="flex" justifyContent="center" p={2}>
                    <CircularProgress size={16} sx={{ color: terminalColors.primary }} />
                  </Box>
                ) : logsError ? (
                  <TerminalAlert severity="error">{logsError}</TerminalAlert>
                ) : logs.length === 0 ? (
                  <Typography variant="body2" sx={{ color: terminalColors.textSecondary }}>
                    No execution logs yet
                  </Typography>
                ) : (
                  <Box
                    sx={{
                      maxHeight: '300px',
                      overflowY: 'auto',
                      border: `1px solid ${terminalColors.border}`,
                      borderRadius: 1,
                      '&::-webkit-scrollbar': {
                        width: '8px',
                      },
                      '&::-webkit-scrollbar-track': {
                        backgroundColor: terminalColors.background,
                      },
                      '&::-webkit-scrollbar-thumb': {
                        backgroundColor: terminalColors.border,
                        borderRadius: '4px',
                      },
                    }}
                  >
                    <Table size="small" stickyHeader>
                      <TableHead>
                        <TableRow>
                          <TableCell sx={{ backgroundColor: terminalColors.background, color: terminalColors.text, fontSize: '0.75rem', py: 1 }}>
                            Date
                          </TableCell>
                          <TableCell sx={{ backgroundColor: terminalColors.background, color: terminalColors.text, fontSize: '0.75rem', py: 1 }}>
                            Status
                          </TableCell>
                          <TableCell sx={{ backgroundColor: terminalColors.background, color: terminalColors.text, fontSize: '0.75rem', py: 1 }}>
                            Result
                          </TableCell>
                          <TableCell sx={{ backgroundColor: terminalColors.background, color: terminalColors.text, fontSize: '0.75rem', py: 1 }}>
                            Duration
                          </TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {logs.map((log) => (
                          <React.Fragment key={log.id}>
                            <TableRow
                              sx={{
                                '&:hover': { backgroundColor: terminalColors.backgroundHover },
                                cursor: 'pointer',
                              }}
                              onMouseEnter={() => setHoveredLogId(log.id)}
                              onMouseLeave={() => setHoveredLogId(null)}
                            >
                              <TerminalTableCell sx={{ fontSize: '0.75rem' }}>
                                {formatDate(log.execution_date)}
                              </TerminalTableCell>
                              <TerminalTableCell sx={{ fontSize: '0.75rem' }}>
                                {getLogStatusChip(log.status)}
                              </TerminalTableCell>
                              <TerminalTableCell sx={{ fontSize: '0.75rem' }}>
                                {formatLogResult(log.result_data)}
                              </TerminalTableCell>
                              <TerminalTableCell sx={{ fontSize: '0.75rem' }}>
                                {log.execution_time_ms ? `${log.execution_time_ms}ms` : 'N/A'}
                              </TerminalTableCell>
                            </TableRow>
                            {hoveredLogId === log.id && (
                              <TableRow>
                                <TableCell colSpan={4} sx={{ py: 1, border: 0, backgroundColor: terminalColors.backgroundSecondary }}>
                                  {log.error_message && (
                                    <Box sx={{ mb: 1 }}>
                                      <Typography variant="caption" sx={{ color: terminalColors.error, fontWeight: 'bold' }}>
                                        Error:
                                      </Typography>
                                      <Typography variant="caption" sx={{ color: terminalColors.text, display: 'block', ml: 1 }}>
                                        {log.error_message}
                                      </Typography>
                                    </Box>
                                  )}
                                  {log.result_data && (
                                    <Box>
                                      <Typography variant="caption" sx={{ color: terminalColors.textSecondary, fontWeight: 'bold' }}>
                                        Result Data:
                                      </Typography>
                                      <pre style={{ 
                                        fontSize: '0.7rem', 
                                        color: terminalColors.text, 
                                        margin: '4px 0 0 0',
                                        whiteSpace: 'pre-wrap',
                                        wordBreak: 'break-word'
                                      }}>
                                        {JSON.stringify(log.result_data, null, 2)}
                                      </pre>
                                    </Box>
                                  )}
                                </TableCell>
                              </TableRow>
                            )}
                          </React.Fragment>
                        ))}
                      </TableBody>
                    </Table>
                  </Box>
                )}
              </Box>
            </Collapse>
          </TableCell>
        </TableRow>
      </React.Fragment>
    );
  };
  
  return (
    <TerminalPaper sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <TerminalTypography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Globe size={20} />
          Website Analysis Status
        </TerminalTypography>
        <Box display="flex" alignItems="center" gap={1}>
          {status && (
            <TerminalChip
              label={`${status.data.active_tasks} Active`}
              size="small"
            />
          )}
          {status && status.data.failed_tasks > 0 && (
            <TerminalChipError
              label={`${status.data.failed_tasks} Failed`}
              size="small"
            />
          )}
          <IconButton
            size="small"
            onClick={fetchStatus}
            disabled={loading}
            sx={{ color: terminalColors.text }}
          >
            <RefreshCw size={16} />
          </IconButton>
        </Box>
      </Box>
      
      {error && (
        <TerminalAlert severity="error" sx={{ mb: 2 }}>
          {error}
        </TerminalAlert>
      )}
      
      {status && (
        <>
          {status.data.user_website_tasks.length > 0 && (
            <Box mb={2}>
              <TerminalTypography variant="subtitle2" sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                <Globe size={14} />
                User Website ({status.data.user_website_tasks.length})
              </TerminalTypography>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TerminalTableCell sx={{ fontSize: '0.75rem' }}>Website</TerminalTableCell>
                    <TerminalTableCell sx={{ fontSize: '0.75rem' }}>Status</TerminalTableCell>
                    <TerminalTableCell sx={{ fontSize: '0.75rem' }}>Timing</TerminalTableCell>
                    <TerminalTableCell sx={{ fontSize: '0.75rem' }}>Actions</TerminalTableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {status.data.user_website_tasks.map(renderTaskRow)}
                </TableBody>
              </Table>
            </Box>
          )}
          
          {status.data.competitor_tasks.length > 0 && (
            <Box>
              <TerminalTypography variant="subtitle2" sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                <Users size={14} />
                Competitors ({status.data.competitor_tasks.length})
              </TerminalTypography>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TerminalTableCell sx={{ fontSize: '0.75rem' }}>Website</TerminalTableCell>
                    <TerminalTableCell sx={{ fontSize: '0.75rem' }}>Status</TerminalTableCell>
                    <TerminalTableCell sx={{ fontSize: '0.75rem' }}>Timing</TerminalTableCell>
                    <TerminalTableCell sx={{ fontSize: '0.75rem' }}>Actions</TerminalTableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {status.data.competitor_tasks.map(renderTaskRow)}
                </TableBody>
              </Table>
            </Box>
          )}
          
          {allTasks.length === 0 && (
            <Box p={2} textAlign="center">
              <TerminalTypography variant="body2" sx={{ color: terminalColors.textSecondary }}>
                No website analysis tasks found. Complete onboarding to create tasks.
              </TerminalTypography>
            </Box>
          )}
        </>
      )}
    </TerminalPaper>
  );
};

export default WebsiteAnalysisStatus;

