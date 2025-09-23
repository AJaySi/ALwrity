import React, { useState, useEffect, useRef } from 'react';
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

// Components
import ComprehensiveAPIBreakdown from './ComprehensiveAPIBreakdown';

interface CompactBillingDashboardProps {
  userId?: string;
}

const CompactBillingDashboard: React.FC<CompactBillingDashboardProps> = ({ userId }) => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [billingData, healthData] = await Promise.all([
        billingService.getDashboardData(userId),
        monitoringService.getSystemHealth()
      ]);
      
      setDashboardData(billingData);
      setSystemHealth(healthData);
      setLastUpdated(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
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
  }, []);

  const formatCurrency = (amount: number) => `$${amount.toFixed(4)}`;
  const formatNumber = (num: number) => num.toLocaleString();
  const formatPercentage = (num: number) => `${num.toFixed(1)}%`;

  if (loading && !dashboardData) {
    return (
      <Card sx={{ 
        background: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255,255,255,0.1)',
        borderRadius: 3
      }}>
        <CardContent sx={{ textAlign: 'center', py: 4 }}>
          <Typography sx={{ color: 'rgba(255,255,255,0.8)' }}>Loading billing data...</Typography>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card sx={{ 
        background: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255,255,255,0.1)',
        borderRadius: 3
      }}>
        <CardContent sx={{ textAlign: 'center', py: 4 }}>
          <Typography sx={{ color: '#ff6b6b' }}>Error: {error}</Typography>
          <IconButton onClick={fetchData} sx={{ mt: 1 }}>
            <RefreshCw size={16} />
          </IconButton>
        </CardContent>
      </Card>
    );
  }

  if (!dashboardData) return null;

  const { current_usage, trends, limits, alerts } = dashboardData;
  const activeProviders = Object.entries(current_usage.provider_breakdown)
    .filter(([_, data]) => data.cost > 0);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <Card 
        sx={{ 
          background: 'linear-gradient(135deg, rgba(255,255,255,0.12) 0%, rgba(255,255,255,0.08) 100%)',
          backdropFilter: 'blur(15px)',
          border: '1px solid rgba(255,255,255,0.15)',
          borderRadius: 4,
          position: 'relative',
          overflow: 'hidden',
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
        }}
      >
        {/* Header - Removed to save space */}

        <CardContent sx={{ pt: 2 }}>
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
                }}>
                  <Typography variant="h5" sx={{ 
                    fontWeight: 800, 
                    color: '#ffffff', 
                    textShadow: '0 2px 8px rgba(0,0,0,0.4)',
                    mb: 0.5
                  }}>
                    {formatCurrency(current_usage.total_cost)}
                  </Typography>
                  <Typography variant="body2" sx={{ 
                    color: 'rgba(255,255,255,0.9)',
                    fontWeight: 500,
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                    fontSize: '0.75rem'
                  }}>
                    Total Cost
                  </Typography>
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
                }}>
                  <Typography variant="h5" sx={{ 
                    fontWeight: 800, 
                    color: '#ffffff', 
                    textShadow: '0 2px 8px rgba(0,0,0,0.4)',
                    mb: 0.5
                  }}>
                    {formatNumber(current_usage.total_calls)}
                  </Typography>
                  <Typography variant="body2" sx={{ 
                    color: 'rgba(255,255,255,0.9)',
                    fontWeight: 500,
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                    fontSize: '0.75rem'
                  }}>
                    API Calls
                  </Typography>
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
                }}>
                  <Typography variant="h5" sx={{ 
                    fontWeight: 800, 
                    color: '#ffffff', 
                    textShadow: '0 2px 8px rgba(0,0,0,0.4)',
                    mb: 0.5
                  }}>
                    {(current_usage.total_tokens / 1000).toFixed(1)}k
                  </Typography>
                  <Typography variant="body2" sx={{ 
                    color: 'rgba(255,255,255,0.9)',
                    fontWeight: 500,
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                    fontSize: '0.75rem'
                  }}>
                    Tokens
                  </Typography>
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
                }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5, mb: 0.5 }}>
                    <CheckCircle size={18} color={systemHealth?.status === 'healthy' ? '#4ade80' : '#ff6b6b'} />
                    <Typography variant="body1" sx={{ 
                      color: systemHealth?.status === 'healthy' ? '#4ade80' : '#ff6b6b',
                      fontWeight: 700,
                      textTransform: 'capitalize',
                      textShadow: '0 2px 4px rgba(0,0,0,0.3)'
                    }}>
                      {systemHealth?.status || 'Unknown'}
                    </Typography>
                  </Box>
                  <Typography variant="body2" sx={{ 
                    color: 'rgba(255,255,255,0.9)',
                    fontWeight: 500,
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                    fontSize: '0.75rem'
                  }}>
                    System Health
                  </Typography>
                </Box>
              </Tooltip>
            </Grid>
          </Grid>


          {/* Usage Progress */}
          {limits.limits.monthly_cost > 0 && (
            <Box sx={{ 
              mb: 3, 
              p: 2.5, 
              background: 'linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.04) 100%)',
              borderRadius: 3,
              border: '1px solid rgba(255,255,255,0.1)'
            }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Box>
                  <Typography variant="subtitle2" sx={{ 
                    color: '#ffffff', 
                    fontWeight: 600,
                    mb: 0.5
                  }}>
                    Monthly Budget Usage
                  </Typography>
                  <Typography variant="caption" sx={{ 
                    color: 'rgba(255,255,255,0.7)',
                    display: 'block'
                  }}>
                    Track your AI spending against monthly limits
                  </Typography>
                </Box>
                <Box sx={{ textAlign: 'right' }}>
                  <Typography variant="h6" sx={{ 
                    color: '#ffffff', 
                    fontWeight: 'bold',
                    textShadow: '0 2px 4px rgba(0,0,0,0.3)'
                  }}>
                    {formatCurrency(current_usage.total_cost)}
                  </Typography>
                  <Typography variant="caption" sx={{ 
                    color: 'rgba(255,255,255,0.7)',
                    display: 'block'
                  }}>
                    of {formatCurrency(limits.limits.monthly_cost)}
                  </Typography>
                </Box>
              </Box>
              <LinearProgress
                variant="determinate"
                value={(current_usage.total_cost / limits.limits.monthly_cost) * 100}
                sx={{
                  height: 8,
                  borderRadius: 4,
                  backgroundColor: 'rgba(255,255,255,0.1)',
                  '& .MuiLinearProgress-bar': {
                    background: current_usage.total_cost / limits.limits.monthly_cost > 0.8 
                      ? 'linear-gradient(90deg, #ff6b6b, #ff5252)'
                      : current_usage.total_cost / limits.limits.monthly_cost > 0.6
                      ? 'linear-gradient(90deg, #ffa726, #ff9800)'
                      : 'linear-gradient(90deg, #4ade80, #22c55e)',
                    borderRadius: 4,
                    boxShadow: '0 2px 8px rgba(0,0,0,0.2)'
                  }
                }}
              />
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                <Typography variant="caption" sx={{ 
                  color: current_usage.total_cost / limits.limits.monthly_cost > 0.8 ? '#ff6b6b' : 'rgba(255,255,255,0.7)',
                  fontWeight: current_usage.total_cost / limits.limits.monthly_cost > 0.8 ? 600 : 400
                }}>
                  {current_usage.total_cost / limits.limits.monthly_cost > 0.8 
                    ? '⚠️ Approaching limit' 
                    : current_usage.total_cost / limits.limits.monthly_cost > 0.6
                    ? '⚡ Moderate usage'
                    : '✅ Within budget'
                  }
                </Typography>
                <Typography variant="caption" sx={{ 
                  color: 'rgba(255,255,255,0.7)',
                  fontWeight: 500
                }}>
                  {((current_usage.total_cost / limits.limits.monthly_cost) * 100).toFixed(1)}% used
                </Typography>
              </Box>
            </Box>
          )}

          {/* Alerts */}
          {alerts.length > 0 && (
            <Box sx={{ 
              mb: 3, 
              p: 2.5, 
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
            }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <AlertTriangle size={18} color="#ff6b6b" />
                <Typography variant="subtitle2" sx={{ 
                  fontWeight: 700, 
                  color: '#ff6b6b',
                  textShadow: '0 1px 2px rgba(0,0,0,0.3)'
                }}>
                  System Alerts ({alerts.length})
                </Typography>
              </Box>
              <Typography variant="caption" sx={{ 
                color: 'rgba(255,255,255,0.8)',
                display: 'block',
                mb: 2
              }}>
                Important notifications requiring your attention
              </Typography>
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
                  </Tooltip>
                ))}
                {alerts.length > 3 && (
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
                )}
              </Box>
            </Box>
          )}

        </CardContent>
      </Card>
    </motion.div>
  );
};

export default CompactBillingDashboard;
