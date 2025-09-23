import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Alert,
  CircularProgress,
  useTheme,
  useMediaQuery,
  ToggleButton,
  ToggleButtonGroup,
  Tooltip,
  Chip,
  IconButton,
} from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  DollarSign, 
  TrendingUp, 
  AlertTriangle, 
  Activity,
  Zap,
  BarChart3,
  PieChart,
  Clock,
  Grid3X3,
  List,
  Info,
  RefreshCw
} from 'lucide-react';

// Services
import { billingService } from '../../services/billingService';
import { monitoringService } from '../../services/monitoringService';
import { onApiEvent } from '../../utils/apiEvents';

// Types
import { DashboardData } from '../../types/billing';
import { SystemHealth } from '../../types/monitoring';

// Components
import CompactBillingDashboard from './CompactBillingDashboard';
import BillingOverview from './BillingOverview';
import SystemHealthIndicator from '../monitoring/SystemHealthIndicator';
import CostBreakdown from './CostBreakdown';
import UsageTrends from './UsageTrends';
import UsageAlerts from './UsageAlerts';
import ComprehensiveAPIBreakdown from './ComprehensiveAPIBreakdown';

interface EnhancedBillingDashboardProps {
  userId?: string;
}

type ViewMode = 'compact' | 'detailed';

const EnhancedBillingDashboard: React.FC<EnhancedBillingDashboardProps> = ({ userId }) => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>('compact');
  
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const fetchDashboardData = async () => {
    try {
      const [billingData, healthData] = await Promise.all([
        billingService.getDashboardData(),
        monitoringService.getSystemHealth()
      ]);
      setDashboardData(billingData);
      setSystemHealth(healthData);
      setLastUpdated(new Date());
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to fetch dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [userId]);

  // Event-driven refresh: refresh only when non-billing/monitoring APIs complete
  useEffect(() => {
    const unsubscribe = onApiEvent((detail) => {
      if (detail.source && detail.source !== 'other') return;
      Promise.all([billingService.getDashboardData(), monitoringService.getSystemHealth()])
        .then(([billingData, health]) => {
          setDashboardData(billingData);
          setSystemHealth(health);
          setLastUpdated(new Date());
        })
        .catch(() => {/* ignore */});
    });
    return unsubscribe;
  }, []);

  // Refetch when tab becomes visible again (cheap, avoids polling)
  useEffect(() => {
    const onVisible = () => {
      if (document.visibilityState === 'visible') {
        fetchDashboardData();
      }
    };
    document.addEventListener('visibilitychange', onVisible);
    return () => document.removeEventListener('visibilitychange', onVisible);
  }, []);

  const handleViewModeChange = (
    event: React.MouseEvent<HTMLElement>,
    newViewMode: ViewMode | null,
  ) => {
    if (newViewMode !== null) {
      setViewMode(newViewMode);
    }
  };

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
          <CircularProgress sx={{ color: 'primary.main' }} />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      </Container>
    );
  }

  if (!dashboardData) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Alert severity="warning">
          No billing data available. Please check your subscription status.
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flex: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography
                        variant="h4"
                        sx={{
                          fontWeight: 800,
                          mb: 1.5,
                          fontSize: '1.1rem',
                          color: 'rgba(255,255,255,0.95)',
                        }}
                      >
                        Billing & Usage Dashboard
                      </Typography>
                      <Tooltip 
                        title={
                          <Box>
                            <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                              AI Usage Monitoring
                            </Typography>
                            <Typography variant="body2" sx={{ opacity: 0.9 }}>
                              Track your AI API costs, usage patterns, and system performance in real-time
                            </Typography>
                          </Box>
                        }
                        arrow
                        placement="top"
                      >
                        <Info size={16} color="rgba(255,255,255,0.6)" style={{ cursor: 'help' }} />
                      </Tooltip>
                    </Box>
              
              {/* Active Providers Chips */}
              {dashboardData && (
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  {Object.entries(dashboardData.current_usage.provider_breakdown)
                    .filter(([_, data]) => data.cost > 0)
                    .map(([provider, data]) => (
                      <Tooltip
                        key={provider}
                        title={
                          <Box>
                            <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                              {provider.toUpperCase()} Usage
                            </Typography>
                            <Typography variant="body2" sx={{ opacity: 0.9 }}>
                              Cost: ${data.cost.toFixed(4)}
                            </Typography>
                            <Typography variant="body2" sx={{ opacity: 0.9 }}>
                              Calls: {data.calls.toLocaleString()}
                            </Typography>
                            <Typography variant="body2" sx={{ opacity: 0.9 }}>
                              Tokens: {data.tokens.toLocaleString()}
                            </Typography>
                          </Box>
                        }
                        arrow
                        placement="top"
                      >
                        <Chip
                          label={`${provider}: $${data.cost.toFixed(4)}`}
                          size="small"
                          sx={{
                            backgroundColor: 'rgba(74, 222, 128, 0.2)',
                            color: '#4ade80',
                            border: '1px solid rgba(74, 222, 128, 0.3)',
                            fontSize: '0.7rem',
                            height: 24,
                            fontWeight: 500,
                            '&:hover': {
                              backgroundColor: 'rgba(74, 222, 128, 0.3)',
                              transform: 'translateY(-1px)',
                              boxShadow: '0 4px 12px rgba(74, 222, 128, 0.2)'
                            },
                            transition: 'all 0.2s ease'
                          }}
                        />
                      </Tooltip>
                    ))}
                </Box>
              )}
            </Box>
            
            {/* View Mode Toggle and Refresh */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Tooltip title="Refresh billing data">
                <IconButton 
                  size="small" 
                  onClick={fetchDashboardData}
                  disabled={loading}
                  sx={{ 
                    color: 'rgba(255,255,255,0.7)',
                    '&:hover': {
                      color: '#ffffff',
                      backgroundColor: 'rgba(255,255,255,0.1)'
                    }
                  }}
                >
                  <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
                </IconButton>
              </Tooltip>
              <Tooltip 
                title={
                  <Box>
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                      View Modes
                    </Typography>
                    <Typography variant="body2" sx={{ opacity: 0.9 }}>
                      <strong>Compact:</strong> Essential metrics only
                    </Typography>
                    <Typography variant="body2" sx={{ opacity: 0.9 }}>
                      <strong>Detailed:</strong> Full breakdown with charts
                    </Typography>
                  </Box>
                }
                arrow
                placement="top"
              >
                <Info size={16} color="rgba(255,255,255,0.7)" style={{ cursor: 'help' }} />
              </Tooltip>
              <ToggleButtonGroup
                value={viewMode}
                exclusive
                onChange={handleViewModeChange}
                size="small"
                sx={{
                  backgroundColor: 'rgba(255,255,255,0.1)',
                  border: '1px solid rgba(255,255,255,0.2)',
                  '& .MuiToggleButton-root': {
                    color: 'rgba(255,255,255,0.7)',
                    border: 'none',
                    '&.Mui-selected': {
                      backgroundColor: 'rgba(255,255,255,0.2)',
                      color: '#ffffff'
                    }
                  }
                }}
              >
                <ToggleButton value="compact">
                  <Grid3X3 size={16} style={{ marginRight: 8 }} />
                  Compact
                </ToggleButton>
                <ToggleButton value="detailed">
                  <List size={16} style={{ marginRight: 8 }} />
                  Detailed
                </ToggleButton>
              </ToggleButtonGroup>
            </Box>
          </Box>
        </Box>
      </motion.div>

      {/* Dashboard Content */}
      <AnimatePresence mode="wait">
        {viewMode === 'compact' ? (
          <motion.div
            key="compact"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            transition={{ duration: 0.3 }}
          >
            <CompactBillingDashboard userId={userId} />
          </motion.div>
        ) : (
          <motion.div
            key="detailed"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
          >
            <Grid container spacing={3}>
              {/* Top Row */}
              <Grid item xs={12} md={4}>
                <BillingOverview 
                  usageStats={dashboardData.current_usage}
                  onRefresh={fetchDashboardData}
                />
              </Grid>
              
              <Grid item xs={12} md={4}>
                <SystemHealthIndicator 
                  systemHealth={systemHealth}
                  onRefresh={fetchDashboardData}
                />
              </Grid>
              
              <Grid item xs={12} md={4}>
                <UsageAlerts 
                  alerts={dashboardData.alerts}
                  onMarkRead={async (alertId) => {
                    // TODO: Implement mark as read functionality
                    console.log('Mark alert as read:', alertId);
                  }}
                />
              </Grid>

              {/* Middle Row */}
              <Grid item xs={12} md={6}>
                <CostBreakdown 
                  providerBreakdown={dashboardData.current_usage.provider_breakdown}
                  totalCost={dashboardData.current_usage.total_cost}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <UsageTrends 
                  trends={dashboardData.trends}
                  projections={dashboardData.projections}
                />
              </Grid>

              {/* Bottom Row - Comprehensive API Breakdown */}
              <Grid item xs={12}>
                <ComprehensiveAPIBreakdown 
                  providerBreakdown={dashboardData.current_usage.provider_breakdown}
                  totalCost={dashboardData.current_usage.total_cost}
                />
              </Grid>
            </Grid>
          </motion.div>
        )}
      </AnimatePresence>
    </Container>
  );
};

export default EnhancedBillingDashboard;
