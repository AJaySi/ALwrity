import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  Chip,
  Tooltip,
  LinearProgress,
  IconButton,
} from '@mui/material';
import { motion } from 'framer-motion';
import { 
  AlertTriangle,
  CheckCircle,
  RefreshCw
} from 'lucide-react';

// Types
import { DashboardData } from '../../types/billing';
import { SystemHealth } from '../../types/monitoring';

// Services
import { billingService } from '../../services/billingService';
import { monitoringService } from '../../services/monitoringService';
import { onApiEvent } from '../../utils/apiEvents';
import { showToastNotification } from '../../utils/toastNotifications';

// Terminal Theme
import {
  TerminalCard,
  TerminalCardContent,
  TerminalTypography,
  TerminalChip,
  TerminalChipError,
  TerminalChipWarning,
  terminalColors
} from '../SchedulerDashboard/terminalTheme';

interface CompactBillingDashboardProps {
  userId?: string;
  terminalTheme?: boolean;
}

const CompactBillingDashboard: React.FC<CompactBillingDashboardProps> = ({ userId, terminalTheme = false }) => {
  // Conditional component selection based on terminal theme
  const CardComponent = terminalTheme ? TerminalCard : Card;
  const CardContentComponent = terminalTheme ? TerminalCardContent : CardContent;
  const TypographyComponent = terminalTheme ? TerminalTypography : Typography;
  const ChipComponent = terminalTheme ? TerminalChip : Chip;
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async (showSuccessToast: boolean = false) => {
    try {
      setLoading(true);
      setError(null);
      
      const [billingData, healthData] = await Promise.all([
        billingService.getDashboardData(userId),
        monitoringService.getSystemHealth()
      ]);
      
      setDashboardData(billingData);
      setSystemHealth(healthData);
      
      // Show success toast only if explicitly requested (user-initiated refresh)
      if (showSuccessToast && billingData && healthData) {
        showToastNotification(
          'Billing data refreshed successfully',
          'success',
          { duration: 3000 }
        );
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch data';
      setError(errorMessage);
      
      // Always show error toast for failures
      showToastNotification(errorMessage, 'error', { duration: 5000 });
    } finally {
      setLoading(false);
    }
  };

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
      fetchData();
    });
    return unsubscribe;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const formatCurrency = (amount: number) => `$${amount.toFixed(4)}`;
  const formatNumber = (num: number) => num.toLocaleString();

  if (loading && !dashboardData) {
    const loadingCardStyles = terminalTheme
      ? {
          backgroundColor: terminalColors.background,
          border: `1px solid ${terminalColors.border}`,
          borderRadius: 3
        }
      : {
          background: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255,255,255,0.1)',
          borderRadius: 3
        };

    return (
      <CardComponent sx={loadingCardStyles}>
        <CardContentComponent sx={{ textAlign: 'center', py: 4 }}>
          <TypographyComponent sx={{ color: terminalTheme ? terminalColors.text : 'rgba(255,255,255,0.8)' }}>
            Loading billing data...
          </TypographyComponent>
        </CardContentComponent>
      </CardComponent>
    );
  }

  if (error) {
    const errorCardStyles = terminalTheme
      ? {
          backgroundColor: terminalColors.background,
          border: `1px solid ${terminalColors.error}`,
          borderRadius: 3
        }
      : {
          background: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255,255,255,0.1)',
          borderRadius: 3
        };

    return (
      <CardComponent sx={errorCardStyles}>
        <CardContentComponent sx={{ textAlign: 'center', py: 4 }}>
          <TypographyComponent sx={{ color: terminalTheme ? terminalColors.error : '#ff6b6b' }}>
            Error: {error}
          </TypographyComponent>
          <IconButton onClick={() => fetchData(true)} sx={{ mt: 1, color: terminalTheme ? terminalColors.text : 'inherit' }}>
            <RefreshCw size={16} />
          </IconButton>
        </CardContentComponent>
      </CardComponent>
    );
  }

  if (!dashboardData) return null;

  const { current_usage, limits, alerts } = dashboardData;

  const mainCardStyles = terminalTheme
    ? {
        backgroundColor: terminalColors.background,
        border: `1px solid ${terminalColors.border}`,
        borderRadius: 4,
        position: 'relative' as const,
        overflow: 'hidden' as const,
        boxShadow: '0 0 15px rgba(0, 255, 0, 0.2)',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '1px',
          background: `linear-gradient(90deg, transparent, ${terminalColors.border}, transparent)`,
          zIndex: 1
        }
      }
    : {
        background: 'linear-gradient(135deg, rgba(255,255,255,0.12) 0%, rgba(255,255,255,0.08) 100%)',
        backdropFilter: 'blur(15px)',
        border: '1px solid rgba(255,255,255,0.15)',
        borderRadius: 4,
        position: 'relative' as const,
        overflow: 'hidden' as const,
        boxShadow: '0 8px 32px rgba(0,0,0,0.2), 0 0 0 1px rgba(255,255,255,0.1)',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '1px',
          background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent)',
          zIndex: 1
        }
      };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <CardComponent sx={mainCardStyles}>
        {/* Header - Removed to save space */}

        <CardContentComponent sx={{ pt: 2 }}>
          {/* Compact Overview */}
          <Grid container spacing={2} sx={{ mb: 2 }}>
            {/* Total Cost */}
            <Grid item xs={6} sm={3}>
              <Tooltip 
                title={
                  <Box>
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                      Monthly API Usage Cost
                    </Typography>
                    <Typography variant="body2" sx={{ opacity: 0.9 }}>
                      Total spending across all AI providers this month
                    </Typography>
                    <Typography variant="caption" sx={{ opacity: 0.7, mt: 1, display: 'block' }}>
                      Includes: Gemini, OpenAI, Anthropic, Mistral
                    </Typography>
                  </Box>
                }
                arrow
                placement="top"
              >
                <Box sx={{ 
                  textAlign: 'center', 
                  p: 2.5, 
                  ...(terminalTheme ? {
                    backgroundColor: terminalColors.backgroundLight,
                    borderRadius: 3,
                    border: `1px solid ${terminalColors.border}`,
                    position: 'relative',
                    overflow: 'hidden',
                    cursor: 'help',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: `0 0 15px ${terminalColors.border}40`,
                      borderColor: terminalColors.secondary
                    },
                    '&::before': {
                      content: '""',
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      height: '3px',
                      background: terminalColors.border,
                      zIndex: 1
                    }
                  } : {
                    background: 'linear-gradient(135deg, rgba(74, 222, 128, 0.12) 0%, rgba(34, 197, 94, 0.08) 100%)',
                    borderRadius: 3,
                    border: '1px solid rgba(74, 222, 128, 0.25)',
                    position: 'relative',
                    overflow: 'hidden',
                    cursor: 'help',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: '0 8px 25px rgba(74, 222, 128, 0.2)',
                      border: '1px solid rgba(74, 222, 128, 0.4)'
                    },
                    '&::before': {
                      content: '""',
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      height: '3px',
                      background: 'linear-gradient(90deg, #4ade80, #22c55e)',
                      zIndex: 1
                    }
                  })
                }}>
                  <TypographyComponent variant="h5" sx={{ 
                    fontWeight: 800, 
                    color: terminalTheme ? terminalColors.text : '#ffffff', 
                    textShadow: terminalTheme ? 'none' : '0 2px 8px rgba(0,0,0,0.4)',
                    mb: 0.5
                  }}>
                    {formatCurrency(current_usage.total_cost)}
                  </TypographyComponent>
                  <TypographyComponent variant="body2" sx={{ 
                    color: terminalTheme ? terminalColors.textSecondary : 'rgba(255,255,255,0.9)',
                    fontWeight: 500,
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                    fontSize: '0.75rem'
                  }}>
                    Total Cost
                  </TypographyComponent>
                </Box>
              </Tooltip>
            </Grid>

            {/* API Calls */}
            <Grid item xs={6} sm={3}>
              <Tooltip 
                title={
                  <Box>
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                      API Request Volume
                    </Typography>
                    <Typography variant="body2" sx={{ opacity: 0.9 }}>
                      Total number of AI API requests made this month
                    </Typography>
                    <Typography variant="caption" sx={{ opacity: 0.7, mt: 1, display: 'block' }}>
                      Each request generates content, analyzes data, or processes information
                    </Typography>
                  </Box>
                }
                arrow
                placement="top"
              >
                <Box sx={{ 
                  textAlign: 'center', 
                  p: 2.5, 
                  ...(terminalTheme ? {
                    backgroundColor: terminalColors.backgroundLight,
                    borderRadius: 3,
                    border: `1px solid ${terminalColors.border}`,
                    position: 'relative',
                    overflow: 'hidden',
                    cursor: 'help',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: `0 0 15px ${terminalColors.border}40`,
                      borderColor: terminalColors.secondary
                    },
                    '&::before': {
                      content: '""',
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      height: '3px',
                      background: terminalColors.border,
                      zIndex: 1
                    }
                  } : {
                    background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.12) 0%, rgba(37, 99, 235, 0.08) 100%)',
                    borderRadius: 3,
                    border: '1px solid rgba(59, 130, 246, 0.25)',
                    position: 'relative',
                    overflow: 'hidden',
                    cursor: 'help',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: '0 8px 25px rgba(59, 130, 246, 0.2)',
                      border: '1px solid rgba(59, 130, 246, 0.4)'
                    },
                    '&::before': {
                      content: '""',
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      height: '3px',
                      background: 'linear-gradient(90deg, #3b82f6, #2563eb)',
                      zIndex: 1
                    }
                  })
                }}>
                  <TypographyComponent variant="h5" sx={{ 
                    fontWeight: 800, 
                    color: terminalTheme ? terminalColors.text : '#ffffff', 
                    textShadow: terminalTheme ? 'none' : '0 2px 8px rgba(0,0,0,0.4)',
                    mb: 0.5
                  }}>
                    {formatNumber(current_usage.total_calls)}
                  </TypographyComponent>
                  <TypographyComponent variant="body2" sx={{ 
                    color: terminalTheme ? terminalColors.textSecondary : 'rgba(255,255,255,0.9)',
                    fontWeight: 500,
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                    fontSize: '0.75rem'
                  }}>
                    API Calls
                  </TypographyComponent>
                </Box>
              </Tooltip>
            </Grid>

            {/* Tokens */}
            <Grid item xs={6} sm={3}>
              <Tooltip 
                title={
                  <Box>
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                      AI Processing Units
                    </Typography>
                    <Typography variant="body2" sx={{ opacity: 0.9 }}>
                      Total tokens processed by AI models this month
                    </Typography>
                    <Typography variant="caption" sx={{ opacity: 0.7, mt: 1, display: 'block' }}>
                      Tokens represent words, characters, and data processed by AI
                    </Typography>
                  </Box>
                }
                arrow
                placement="top"
              >
                <Box sx={{ 
                  textAlign: 'center', 
                  p: 2.5, 
                  ...(terminalTheme ? {
                    backgroundColor: terminalColors.backgroundLight,
                    borderRadius: 3,
                    border: `1px solid ${terminalColors.border}`,
                    position: 'relative',
                    overflow: 'hidden',
                    cursor: 'help',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: `0 0 15px ${terminalColors.border}40`,
                      borderColor: terminalColors.secondary
                    },
                    '&::before': {
                      content: '""',
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      height: '3px',
                      background: terminalColors.border,
                      zIndex: 1
                    }
                  } : {
                    background: 'linear-gradient(135deg, rgba(168, 85, 247, 0.12) 0%, rgba(147, 51, 234, 0.08) 100%)',
                    borderRadius: 3,
                    border: '1px solid rgba(168, 85, 247, 0.25)',
                    position: 'relative',
                    overflow: 'hidden',
                    cursor: 'help',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: '0 8px 25px rgba(168, 85, 247, 0.2)',
                      border: '1px solid rgba(168, 85, 247, 0.4)'
                    },
                    '&::before': {
                      content: '""',
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      height: '3px',
                      background: 'linear-gradient(90deg, #a855f7, #9333ea)',
                      zIndex: 1
                    }
                  })
                }}>
                  <TypographyComponent variant="h5" sx={{ 
                    fontWeight: 800, 
                    color: terminalTheme ? terminalColors.text : '#ffffff', 
                    textShadow: terminalTheme ? 'none' : '0 2px 8px rgba(0,0,0,0.4)',
                    mb: 0.5
                  }}>
                    {(current_usage.total_tokens / 1000).toFixed(1)}k
                  </TypographyComponent>
                  <TypographyComponent variant="body2" sx={{ 
                    color: terminalTheme ? terminalColors.textSecondary : 'rgba(255,255,255,0.9)',
                    fontWeight: 500,
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                    fontSize: '0.75rem'
                  }}>
                    Tokens
                  </TypographyComponent>
                </Box>
              </Tooltip>
            </Grid>

            {/* System Health */}
            <Grid item xs={6} sm={3}>
              <Tooltip 
                title={
                  <Box>
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                      System Performance Status
                    </Typography>
                    <Typography variant="body2" sx={{ opacity: 0.9 }}>
                      Real-time monitoring of API services and system performance
                    </Typography>
                    <Typography variant="caption" sx={{ opacity: 0.7, mt: 1, display: 'block' }}>
                      {systemHealth?.status === 'healthy' 
                        ? 'All systems operational and responding normally'
                        : 'Some services may be experiencing issues'
                      }
                    </Typography>
                  </Box>
                }
                arrow
                placement="top"
              >
                <Box sx={{ 
                  textAlign: 'center', 
                  p: 2.5, 
                  ...(terminalTheme ? {
                    backgroundColor: terminalColors.backgroundLight,
                    borderRadius: 3,
                    border: `1px solid ${systemHealth?.status === 'healthy' ? terminalColors.success : terminalColors.error}`,
                    position: 'relative',
                    overflow: 'hidden',
                    cursor: 'help',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: `0 0 15px ${systemHealth?.status === 'healthy' ? terminalColors.success : terminalColors.error}40`,
                      borderColor: systemHealth?.status === 'healthy' ? terminalColors.secondary : terminalColors.error
                    },
                    '&::before': {
                      content: '""',
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      height: '3px',
                      background: systemHealth?.status === 'healthy' ? terminalColors.success : terminalColors.error,
                      zIndex: 1
                    }
                  } : {
                    background: systemHealth?.status === 'healthy' 
                      ? 'linear-gradient(135deg, rgba(34, 197, 94, 0.12) 0%, rgba(22, 163, 74, 0.08) 100%)'
                      : 'linear-gradient(135deg, rgba(239, 68, 68, 0.12) 0%, rgba(220, 38, 38, 0.08) 100%)',
                    borderRadius: 3,
                    border: systemHealth?.status === 'healthy' 
                      ? '1px solid rgba(34, 197, 94, 0.25)'
                      : '1px solid rgba(239, 68, 68, 0.25)',
                    position: 'relative',
                    overflow: 'hidden',
                    cursor: 'help',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: systemHealth?.status === 'healthy' 
                        ? '0 8px 25px rgba(34, 197, 94, 0.2)'
                        : '0 8px 25px rgba(239, 68, 68, 0.2)',
                      border: systemHealth?.status === 'healthy' 
                        ? '1px solid rgba(34, 197, 94, 0.4)'
                        : '1px solid rgba(239, 68, 68, 0.4)'
                    },
                    '&::before': {
                      content: '""',
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      height: '3px',
                      background: systemHealth?.status === 'healthy' 
                        ? 'linear-gradient(90deg, #22c55e, #16a34a)'
                        : 'linear-gradient(90deg, #ef4444, #dc2626)',
                      zIndex: 1
                    }
                  })
                }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5, mb: 0.5 }}>
                    <CheckCircle size={18} color={terminalTheme 
                      ? (systemHealth?.status === 'healthy' ? terminalColors.success : terminalColors.error)
                      : (systemHealth?.status === 'healthy' ? '#4ade80' : '#ff6b6b')
                    } />
                    <TypographyComponent variant="body1" sx={{ 
                      color: terminalTheme 
                        ? (systemHealth?.status === 'healthy' ? terminalColors.success : terminalColors.error)
                        : (systemHealth?.status === 'healthy' ? '#4ade80' : '#ff6b6b'),
                      fontWeight: 700,
                      textTransform: 'capitalize',
                      textShadow: terminalTheme ? 'none' : '0 2px 4px rgba(0,0,0,0.3)'
                    }}>
                      {systemHealth?.status || 'Unknown'}
                    </TypographyComponent>
                  </Box>
                  <TypographyComponent variant="body2" sx={{ 
                    color: terminalTheme ? terminalColors.textSecondary : 'rgba(255,255,255,0.9)',
                    fontWeight: 500,
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                    fontSize: '0.75rem'
                  }}>
                    System Health
                  </TypographyComponent>
                </Box>
              </Tooltip>
            </Grid>
          </Grid>


          {/* Usage Progress */}
          {limits.limits.monthly_cost > 0 && (
            <Box sx={{ 
              mb: 3, 
              p: 2.5, 
              ...(terminalTheme ? {
                backgroundColor: terminalColors.backgroundLight,
                borderRadius: 3,
                border: `1px solid ${terminalColors.border}`
              } : {
                background: 'linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.04) 100%)',
                borderRadius: 3,
                border: '1px solid rgba(255,255,255,0.1)'
              })
            }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Box>
                  <TypographyComponent variant="subtitle2" sx={{ 
                    color: terminalTheme ? terminalColors.text : '#ffffff', 
                    fontWeight: 600,
                    mb: 0.5
                  }}>
                    Monthly Budget Usage
                  </TypographyComponent>
                  <TypographyComponent variant="caption" sx={{ 
                    color: terminalTheme ? terminalColors.textSecondary : 'rgba(255,255,255,0.7)',
                    display: 'block'
                  }}>
                    Track your AI spending against monthly limits
                  </TypographyComponent>
                </Box>
                <Box sx={{ textAlign: 'right' }}>
                  <TypographyComponent variant="h6" sx={{ 
                    color: terminalTheme ? terminalColors.text : '#ffffff', 
                    fontWeight: 'bold',
                    textShadow: terminalTheme ? 'none' : '0 2px 4px rgba(0,0,0,0.3)'
                  }}>
                    {formatCurrency(current_usage.total_cost)}
                  </TypographyComponent>
                  <TypographyComponent variant="caption" sx={{ 
                    color: terminalTheme ? terminalColors.textSecondary : 'rgba(255,255,255,0.7)',
                    display: 'block'
                  }}>
                    of {formatCurrency(limits.limits.monthly_cost)}
                  </TypographyComponent>
                </Box>
              </Box>
              <LinearProgress
                variant="determinate"
                value={(current_usage.total_cost / limits.limits.monthly_cost) * 100}
                sx={{
                  height: 8,
                  borderRadius: 4,
                  backgroundColor: terminalTheme ? terminalColors.backgroundLight : 'rgba(255,255,255,0.1)',
                  '& .MuiLinearProgress-bar': {
                    background: terminalTheme
                      ? (current_usage.total_cost / limits.limits.monthly_cost > 0.8 
                          ? terminalColors.error
                          : current_usage.total_cost / limits.limits.monthly_cost > 0.6
                          ? terminalColors.warning
                          : terminalColors.success)
                      : (current_usage.total_cost / limits.limits.monthly_cost > 0.8 
                          ? 'linear-gradient(90deg, #ff6b6b, #ff5252)'
                          : current_usage.total_cost / limits.limits.monthly_cost > 0.6
                          ? 'linear-gradient(90deg, #ffa726, #ff9800)'
                          : 'linear-gradient(90deg, #4ade80, #22c55e)'),
                    borderRadius: 4,
                    boxShadow: terminalTheme ? 'none' : '0 2px 8px rgba(0,0,0,0.2)'
                  }
                }}
              />
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                <TypographyComponent variant="caption" sx={{ 
                  color: terminalTheme 
                    ? (current_usage.total_cost / limits.limits.monthly_cost > 0.8 ? terminalColors.error : terminalColors.textSecondary)
                    : (current_usage.total_cost / limits.limits.monthly_cost > 0.8 ? '#ff6b6b' : 'rgba(255,255,255,0.7)'),
                  fontWeight: current_usage.total_cost / limits.limits.monthly_cost > 0.8 ? 600 : 400
                }}>
                  {current_usage.total_cost / limits.limits.monthly_cost > 0.8 
                    ? '⚠️ Approaching limit' 
                    : current_usage.total_cost / limits.limits.monthly_cost > 0.6
                    ? '⚡ Moderate usage'
                    : '✅ Within budget'
                  }
                </TypographyComponent>
                <TypographyComponent variant="caption" sx={{ 
                  color: terminalTheme ? terminalColors.textSecondary : 'rgba(255,255,255,0.7)',
                  fontWeight: 500
                }}>
                  {((current_usage.total_cost / limits.limits.monthly_cost) * 100).toFixed(1)}% used
                </TypographyComponent>
              </Box>
            </Box>
          )}

          {/* Alerts */}
          {alerts.length > 0 && (
            <Box sx={{ 
              mb: 3, 
              p: 2.5, 
              ...(terminalTheme ? {
                backgroundColor: terminalColors.backgroundLight,
                borderRadius: 3,
                border: `1px solid ${terminalColors.error}`,
                position: 'relative',
                '&::before': {
                  content: '""',
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  height: '3px',
                  background: terminalColors.error,
                  borderRadius: '3px 3px 0 0'
                }
              } : {
                background: 'linear-gradient(135deg, rgba(255, 107, 107, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%)',
                borderRadius: 3,
                border: '1px solid rgba(255, 107, 107, 0.2)',
                position: 'relative',
                '&::before': {
                  content: '""',
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  height: '3px',
                  background: 'linear-gradient(90deg, #ff6b6b, #ef4444)',
                  borderRadius: '3px 3px 0 0'
                }
              })
            }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <AlertTriangle size={18} color={terminalTheme ? terminalColors.error : "#ff6b6b"} />
                <TypographyComponent variant="subtitle2" sx={{ 
                  fontWeight: 700, 
                  color: terminalTheme ? terminalColors.error : '#ff6b6b',
                  textShadow: terminalTheme ? 'none' : '0 1px 2px rgba(0,0,0,0.3)'
                }}>
                  System Alerts ({alerts.length})
                </TypographyComponent>
              </Box>
              <TypographyComponent variant="caption" sx={{ 
                color: terminalTheme ? terminalColors.textSecondary : 'rgba(255,255,255,0.8)',
                display: 'block',
                mb: 2
              }}>
                Important notifications requiring your attention
              </TypographyComponent>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {alerts.slice(0, 3).map((alert) => (
                  <Tooltip 
                    key={alert.id} 
                    title={
                      <Box>
                        <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                          {alert.title}
                        </Typography>
                        <Typography variant="body2" sx={{ opacity: 0.9 }}>
                          {alert.message}
                        </Typography>
                      </Box>
                    }
                    arrow
                    placement="top"
                  >
                    {terminalTheme ? (
                      <TerminalChipError
                        label={alert.title}
                        size="small"
                        icon={<AlertTriangle size={14} />}
                        sx={{
                          fontWeight: 500,
                          '&:hover': {
                            transform: 'translateY(-1px)'
                          },
                          transition: 'all 0.2s ease'
                        }}
                      />
                    ) : (
                      <Chip
                        label={alert.title}
                        size="small"
                        icon={<AlertTriangle size={14} />}
                        sx={{
                          backgroundColor: 'rgba(255, 107, 107, 0.2)',
                          color: '#ff6b6b',
                          border: '1px solid rgba(255, 107, 107, 0.3)',
                          fontWeight: 500,
                          '&:hover': {
                            backgroundColor: 'rgba(255, 107, 107, 0.3)',
                            transform: 'translateY(-1px)'
                          },
                          transition: 'all 0.2s ease'
                        }}
                      />
                    )}
                  </Tooltip>
                ))}
                {alerts.length > 3 && (
                  terminalTheme ? (
                    <TerminalChip
                      label={`+${alerts.length - 3} more`}
                      size="small"
                      sx={{ fontWeight: 500 }}
                    />
                  ) : (
                    <Chip
                      label={`+${alerts.length - 3} more`}
                      size="small"
                      sx={{
                        backgroundColor: 'rgba(255,255,255,0.1)',
                        color: 'rgba(255,255,255,0.8)',
                        border: '1px solid rgba(255,255,255,0.2)',
                        fontWeight: 500
                      }}
                    />
                  )
                )}
              </Box>
            </Box>
          )}

        </CardContentComponent>
      </CardComponent>
    </motion.div>
  );
};

export default CompactBillingDashboard;
