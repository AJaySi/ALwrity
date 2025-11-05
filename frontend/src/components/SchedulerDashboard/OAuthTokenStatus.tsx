/**
 * OAuth Token Status Component
 * Compact terminal-themed component for displaying OAuth token monitoring status
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
} from '@mui/material';
import {
  RefreshCw,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Info,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { useAuth } from '@clerk/clerk-react';
import {
  getOAuthTokenStatus,
  manualRefreshToken,
  OAuthTokenStatusResponse,
  ManualRefreshResponse,
} from '../../api/oauthTokenMonitoring';
import {
  TerminalPaper,
  TerminalTypography,
  TerminalChip,
  TerminalChipSuccess,
  TerminalChipError,
  TerminalChipWarning,
  TerminalAlert,
  terminalColors,
} from './terminalTheme';

interface OAuthTokenStatusProps {
  compact?: boolean;
}

const OAuthTokenStatus: React.FC<OAuthTokenStatusProps> = ({ compact = true }) => {
  const { userId } = useAuth();
  const [status, setStatus] = useState<OAuthTokenStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [expandedPlatform, setExpandedPlatform] = useState<string | null>(null);
  
  const fetchStatus = async () => {
    if (!userId) return;
    
    try {
      setLoading(true);
      setError(null);
      const response = await getOAuthTokenStatus(userId);
      setStatus(response);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch token status');
      console.error('Error fetching OAuth token status:', err);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchStatus();
    
    // Poll for status updates every 2 minutes
    const interval = setInterval(fetchStatus, 120000);
    return () => clearInterval(interval);
  }, [userId]);
  
  const handleRefresh = async (platform: string) => {
    if (!userId) return;
    
    try {
      setRefreshing(platform);
      setError(null);
      const response: ManualRefreshResponse = await manualRefreshToken(userId, platform);
      
      // Refresh status after manual refresh
      await fetchStatus();
      
      if (response.success) {
        console.log(`Token refresh successful for ${platform}`);
      } else {
        console.error(`Token refresh failed for ${platform}:`, response.data.execution_result.error_message);
      }
    } catch (err: any) {
      setError(err.message || `Failed to refresh ${platform} token`);
      console.error(`Error refreshing ${platform} token:`, err);
    } finally {
      setRefreshing(null);
    }
  };
  
  const getStatusIcon = (taskStatus: string | null, connected: boolean) => {
    if (!connected) {
      return <XCircle size={16} color={terminalColors.error} />;
    }
    
    if (!taskStatus || taskStatus === 'not_created') {
      return <Info size={16} color={terminalColors.info} />;
    }
    
    switch (taskStatus) {
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
  
  const getStatusChip = (taskStatus: string | null, connected: boolean) => {
    if (!connected) {
      return <TerminalChipError label="Not Connected" size="small" />;
    }
    
    if (!taskStatus || taskStatus === 'not_created') {
      return <TerminalChip label={taskStatus || 'Not Created'} size="small" />;
    }
    
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
  
  const getPlatformDisplayName = (platform: string) => {
    const names: { [key: string]: string } = {
      gsc: 'GSC',
      bing: 'Bing',
      wordpress: 'WP',
      wix: 'Wix',
    };
    return names[platform] || platform.toUpperCase();
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
  
  const platforms = ['gsc', 'bing', 'wordpress', 'wix'];
  
  return (
    <TerminalPaper sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <TerminalTypography variant="h6" component="h3">
          OAuth Token Status
        </TerminalTypography>
        <Tooltip title="Refresh status">
          <IconButton
            size="small"
            onClick={fetchStatus}
            disabled={loading}
            sx={{
              color: terminalColors.primary,
              border: `1px solid ${terminalColors.primary}`,
              '&:hover': {
                backgroundColor: 'rgba(0, 255, 0, 0.1)',
              },
              '&:disabled': {
                color: '#004400',
                borderColor: '#004400',
              }
            }}
          >
            <RefreshCw size={16} />
          </IconButton>
        </Tooltip>
      </Box>
      
      {error && (
        <TerminalAlert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </TerminalAlert>
      )}
      
      <Box sx={{ flex: 1, overflow: 'auto', minHeight: 0 }}>
        <Table size="small" sx={{ '& .MuiTableCell-root': { color: terminalColors.primary, borderColor: terminalColors.primary + '40' } }}>
          <TableHead>
            <TableRow>
              <TableCell>Platform</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Last Check</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {platforms.map((platform) => {
              const platformStatus = status.data.platform_status[platform];
              const task = platformStatus?.monitoring_task;
              const isExpanded = expandedPlatform === platform;
              
              return (
                <React.Fragment key={platform}>
                  <TableRow
                    sx={{
                      cursor: 'pointer',
                      '&:hover': {
                        backgroundColor: 'rgba(0, 255, 0, 0.05)',
                      }
                    }}
                  >
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={1}>
                        {getStatusIcon(task?.status || null, platformStatus?.connected || false)}
                        <TerminalTypography variant="body2" fontWeight="medium">
                          {getPlatformDisplayName(platform)}
                        </TerminalTypography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      {getStatusChip(task?.status || null, platformStatus?.connected || false)}
                    </TableCell>
                    <TableCell>
                      <TerminalTypography variant="caption" color={terminalColors.textSecondary}>
                        {formatDate(task?.last_check || null)}
                      </TerminalTypography>
                    </TableCell>
                    <TableCell align="right">
                      <Box display="flex" gap={0.5} justifyContent="flex-end">
                        <Tooltip title={isExpanded ? "Hide details" : "Show details"}>
                          <IconButton
                            size="small"
                            onClick={() => setExpandedPlatform(isExpanded ? null : platform)}
                            sx={{
                              color: terminalColors.primary,
                              '&:hover': {
                                backgroundColor: 'rgba(0, 255, 0, 0.1)',
                              }
                            }}
                          >
                            {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                          </IconButton>
                        </Tooltip>
                        {platformStatus?.connected && (
                          <Tooltip title="Manually refresh token">
                            <IconButton
                              size="small"
                              onClick={() => handleRefresh(platform)}
                              disabled={refreshing === platform}
                              sx={{
                                color: terminalColors.primary,
                                '&:hover': {
                                  backgroundColor: 'rgba(0, 255, 0, 0.1)',
                                },
                                '&:disabled': {
                                  color: '#004400',
                                }
                              }}
                            >
                              {refreshing === platform ? (
                                <CircularProgress size={14} sx={{ color: terminalColors.primary }} />
                              ) : (
                                <RefreshCw size={14} />
                              )}
                            </IconButton>
                          </Tooltip>
                        )}
                      </Box>
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell colSpan={4} sx={{ py: 0, border: 0 }}>
                      <Collapse in={isExpanded}>
                        <Box p={2} sx={{ backgroundColor: 'rgba(0, 255, 0, 0.05)', borderLeft: `2px solid ${terminalColors.primary}` }}>
                          {task?.failure_reason && (
                            <TerminalAlert severity="error" sx={{ mb: 1 }}>
                              <TerminalTypography variant="body2" fontWeight="bold">
                                Last Failure:
                              </TerminalTypography>
                              <TerminalTypography variant="body2">
                                {task.failure_reason}
                              </TerminalTypography>
                              <TerminalTypography variant="caption" color={terminalColors.textSecondary}>
                                {formatDate(task.last_failure || null)}
                              </TerminalTypography>
                            </TerminalAlert>
                          )}
                          {task?.last_success && (
                            <TerminalAlert severity="success" sx={{ mb: 1 }}>
                              <TerminalTypography variant="body2">
                                Last successful: {formatDate(task.last_success)}
                              </TerminalTypography>
                            </TerminalAlert>
                          )}
                          {task?.next_check && (
                            <Box mt={1}>
                              <TerminalTypography variant="caption" color={terminalColors.textSecondary}>
                                Next check: {formatDate(task.next_check)}
                              </TerminalTypography>
                            </Box>
                          )}
                          {!task && platformStatus?.connected && (
                            <TerminalAlert severity="info">
                              <TerminalTypography variant="body2">
                                Connected but no monitoring task. Create one manually or wait for onboarding completion.
                              </TerminalTypography>
                            </TerminalAlert>
                          )}
                          {!platformStatus?.connected && (
                            <TerminalAlert severity="warning">
                              <TerminalTypography variant="body2">
                                Not connected. Connect in onboarding step 5.
                              </TerminalTypography>
                            </TerminalAlert>
                          )}
                        </Box>
                      </Collapse>
                    </TableCell>
                  </TableRow>
                </React.Fragment>
              );
            })}
          </TableBody>
        </Table>
      </Box>
    </TerminalPaper>
  );
};

export default OAuthTokenStatus;

