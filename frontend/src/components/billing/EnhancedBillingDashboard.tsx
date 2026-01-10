import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Typography,
  Alert,
  CircularProgress,
  ToggleButton,
  ToggleButtonGroup,
  Tooltip,
  Chip,
  IconButton,
} from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Grid3X3,
  List,
  Info,
  RefreshCw
} from 'lucide-react';

// Services
import { billingService } from '../../services/billingService';
import { monitoringService } from '../../services/monitoringService';
import { onApiEvent } from '../../utils/apiEvents';
import { showToastNotification } from '../../utils/toastNotifications';

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
import ToolCostBreakdown from './ToolCostBreakdown';
import CostOptimizationRecommendations from './CostOptimizationRecommendations';
import AdvancedCostAnalytics from './AdvancedCostAnalytics';
import DailyCostHeatmap from './DailyCostHeatmap';
import LiveCostCounter from './LiveCostCounter';
import ErrorRateGauge from './ErrorRateGauge';
import MultiSeriesCostChart from './MultiSeriesCostChart';

// Terminal Theme
import {
  TerminalTypography,
  TerminalAlert,
  terminalColors
} from '../SchedulerDashboard/terminalTheme';

interface EnhancedBillingDashboardProps {
  userId?: string;
  terminalTheme?: boolean;
}

type ViewMode = 'compact' | 'detailed';

const EnhancedBillingDashboard: React.FC<EnhancedBillingDashboardProps> = ({ userId, terminalTheme = false }) => {
  // Conditional component selection based on terminal theme
  const TypographyComponent = terminalTheme ? TerminalTypography : Typography;
  const AlertComponent = terminalTheme ? TerminalAlert : Alert;
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>('compact');
  const [lastRefreshTime, setLastRefreshTime] = useState<Date | null>(null);
  const [healthError, setHealthError] = useState<string | null>(null);

  const fetchDashboardData = async (showSuccessToast: boolean = false) => {
    try {
      // Use Promise.allSettled to prevent health check timeout from blocking dashboard
      const results = await Promise.allSettled([
        billingService.getDashboardData(),
        monitoringService.getSystemHealth()
      ]);
      
      // Handle billing data (required)
      if (results[0].status === 'fulfilled') {
        setDashboardData(results[0].value);
        setLastRefreshTime(new Date());
        setError(null); // Clear any previous errors
      } else {
        // Billing data is critical - show error
        const errorMessage = results[0].reason instanceof Error 
          ? results[0].reason.message 
          : 'Failed to fetch dashboard data';
        setError(errorMessage);
        showToastNotification(
          `Unable to fetch latest billing data: ${errorMessage}. Showing last known values.`,
          'error',
          { duration: 7000 }
        );
        setLoading(false);
        return;
      }
      
      // Handle health data (optional - don't block dashboard if it fails)
      if (results[1].status === 'fulfilled') {
        setSystemHealth(results[1].value);
        setHealthError(null); // Clear health error on success
      } else {
        // Health check failed - keep last successful value, show error toast
        const healthErrorMessage = results[1].reason instanceof Error
          ? results[1].reason.message
          : 'System health check timed out or failed';
        setHealthError(healthErrorMessage);
        showToastNotification(
          `Unable to fetch latest system health data: ${healthErrorMessage}. Showing last known values.`,
          'warning',
          { duration: 6000 }
        );
        // Don't update systemHealth - keep last successful value
        // Only set to null if we never had a successful fetch
        if (!systemHealth) {
          setSystemHealth(null);
        }
      }
      
      // Show success toast only if explicitly requested (user-initiated refresh)
      if (showSuccessToast && results[0].status === 'fulfilled' && results[1].status === 'fulfilled') {
        showToastNotification(
          'Billing data refreshed successfully',
          'success',
          { duration: 3000 }
        );
      } else if (showSuccessToast && results[0].status === 'fulfilled' && results[1].status === 'rejected') {
        showToastNotification(
          'Billing data refreshed, but system health check failed',
          'warning',
          { duration: 4000 }
        );
      }
    } catch (error) {
      // Fallback error handling (shouldn't reach here with allSettled)
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch dashboard data';
      setError(errorMessage);
      showToastNotification(errorMessage, 'error', { duration: 5000 });
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
      Promise.allSettled([billingService.getDashboardData(), monitoringService.getSystemHealth()])
        .then((results) => {
          if (results[0].status === 'fulfilled') {
            setDashboardData(results[0].value);
            setLastRefreshTime(new Date());
            setError(null);
          }
          if (results[1].status === 'fulfilled') {
            setSystemHealth(results[1].value);
            setHealthError(null);
          } else {
            // Keep last successful health value, don't set fake defaults
            const healthErrorMessage = results[1].reason instanceof Error
              ? results[1].reason.message
              : 'System health check failed';
            setHealthError(healthErrorMessage);
            // Don't update systemHealth - keep last successful value
          }
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

  // Listen for billing refresh requests (e.g., when subscription limits are exceeded)
  useEffect(() => {
    const handleBillingRefresh = () => {
      console.log('EnhancedBillingDashboard: Billing refresh requested, refreshing data...');
      // Use allSettled to prevent health check from blocking refresh
      Promise.allSettled([billingService.getDashboardData(), monitoringService.getSystemHealth()])
        .then((results) => {
          if (results[0].status === 'fulfilled') {
            setDashboardData(results[0].value);
            setLastRefreshTime(new Date());
            setError(null);
          } else {
            const errorMessage = results[0].reason instanceof Error 
              ? results[0].reason.message 
              : 'Failed to refresh billing data';
            setError(errorMessage);
            showToastNotification(
              `Unable to refresh billing data: ${errorMessage}. Showing last known values.`,
              'error',
              { duration: 6000 }
            );
            console.error('Error refreshing billing data:', results[0].reason);
          }
          if (results[1].status === 'fulfilled') {
            setSystemHealth(results[1].value);
            setHealthError(null);
          } else {
            // Keep last successful health value, don't set fake defaults
            const healthErrorMessage = results[1].reason instanceof Error
              ? results[1].reason.message
              : 'System health check failed';
            setHealthError(healthErrorMessage);
            // Don't update systemHealth - keep last successful value
          }
        })
        .catch((error) => {
          console.error('Unexpected error in billing refresh:', error);
        });
    };
    
    window.addEventListener('billing-refresh-requested', handleBillingRefresh);
    return () => {
      window.removeEventListener('billing-refresh-requested', handleBillingRefresh);
    };
  }, []); // Empty deps - handler doesn't depend on component state

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
        <AlertComponent severity="error" sx={{ mb: 3 }}>
          {error}
        </AlertComponent>
      </Container>
    );
  }

  if (!dashboardData) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <AlertComponent severity="warning">
          No billing data available. Please check your subscription status.
        </AlertComponent>
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
                      <TypographyComponent
                        variant="h4"
                        sx={{
                          fontWeight: 800,
                          mb: 1.5,
                          fontSize: '1.1rem',
                          color: terminalTheme ? terminalColors.text : 'rgba(255,255,255,0.95)',
                        }}
                      >
                        Billing & Usage Dashboard
                      </TypographyComponent>
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
                    .filter(([_, data]) => data && data.cost > 0)
                    .map(([provider, data]) => {
                      const providerData = data!; // Safe after filter
                      return (
                        <Tooltip
                          key={provider}
                          title={
                            <Box>
                              <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                                {provider.toUpperCase()} Usage
                              </Typography>
                              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                                Cost: ${(providerData.cost ?? 0).toFixed(4)}
                              </Typography>
                              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                                Calls: {(providerData.calls ?? 0).toLocaleString()}
                              </Typography>
                              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                                Tokens: {(providerData.tokens ?? 0).toLocaleString()}
                              </Typography>
                            </Box>
                          }
                          arrow
                          placement="top"
                        >
                          <Chip
                            label={`${provider}: $${(providerData.cost ?? 0).toFixed(4)}`}
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
                      );
                    })}
                </Box>
              )}
            </Box>
            
            {/* View Mode Toggle and Refresh */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              {/* Last Refresh Timestamp */}
              {lastRefreshTime && (
                <Tooltip title={`Data last refreshed at ${lastRefreshTime.toLocaleTimeString()}`}>
                  <TypographyComponent 
                    variant="caption" 
                    sx={{ 
                      color: 'rgba(255,255,255,0.6)',
                      fontSize: '0.7rem',
                      fontStyle: 'italic'
                    }}
                  >
                    Last updated: {lastRefreshTime.toLocaleTimeString()}
                  </TypographyComponent>
                </Tooltip>
              )}
              <Tooltip title="Refresh billing data">
                <IconButton 
                  size="small" 
                  onClick={() => fetchDashboardData(true)}
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
            <CompactBillingDashboard userId={userId} terminalTheme={terminalTheme} />
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
                  terminalTheme={terminalTheme}
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

              {/* Tool-Level Cost Breakdown */}
              <Grid item xs={12} md={6}>
                <ToolCostBreakdown 
                  userId={userId}
                  terminalTheme={terminalTheme}
                />
              </Grid>

              {/* Bottom Row - Comprehensive API Breakdown */}
              <Grid item xs={12} md={6}>
                <ComprehensiveAPIBreakdown 
                  providerBreakdown={dashboardData.current_usage.provider_breakdown}
                  totalCost={dashboardData.current_usage.total_cost}
                />
              </Grid>

              {/* Priority 3: Cost Optimization Recommendations */}
              <Grid item xs={12} md={6}>
                <CostOptimizationRecommendations 
                  userId={userId}
                  terminalTheme={terminalTheme}
                />
              </Grid>

              {/* Priority 3: Advanced Cost Analytics */}
              <Grid item xs={12}>
                <AdvancedCostAnalytics 
                  userId={userId}
                  terminalTheme={terminalTheme}
                />
              </Grid>

              {/* Phase 3: Multi-Series Cost Chart */}
              <Grid item xs={12} md={6}>
                <MultiSeriesCostChart 
                  trends={dashboardData.trends}
                  monthlyLimit={dashboardData.projections.cost_limit || 0}
                />
              </Grid>

              {/* Phase 3: Error Rate Gauge */}
              <Grid item xs={12} md={6}>
                <ErrorRateGauge 
                  systemHealth={systemHealth}
                  terminalTheme={terminalTheme}
                  terminalColors={terminalColors}
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
