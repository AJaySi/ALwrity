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
  Clock
} from 'lucide-react';

// Services
import { billingService } from '../../services/billingService';
import { monitoringService } from '../../services/monitoringService';

// Types
import { DashboardData, UsageStats } from '../../types/billing';
import { SystemHealth } from '../../types/monitoring';

// Components (we'll create these next)
import BillingOverview from './BillingOverview';
import CostBreakdown from './CostBreakdown';
import UsageTrends from './UsageTrends';
import SystemHealthIndicator from '../monitoring/SystemHealthIndicator';
import UsageAlerts from './UsageAlerts';

// Animation variants
const containerVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.6,
      staggerChildren: 0.1
    }
  }
};

const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.4 }
  }
};

const BillingDashboard: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  // State management
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  // Fetch dashboard data
  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('🔍 [DASHBOARD DEBUG] Starting data fetch...');
      
      // Fetch billing and monitoring data in parallel
      const [billingData, healthData] = await Promise.all([
        billingService.getDashboardData(),
        monitoringService.getSystemHealth()
      ]);
      
      console.log('🔍 [DASHBOARD DEBUG] Received billing data:', billingData);
      console.log('🔍 [DASHBOARD DEBUG] Received health data:', healthData);
      console.log('🔍 [DASHBOARD DEBUG] Billing data current_usage:', billingData?.current_usage);
      console.log('🔍 [DASHBOARD DEBUG] Billing data summary:', billingData?.summary);
      console.log('🔍 [DASHBOARD DEBUG] Billing data trends:', billingData?.trends);
      
      setDashboardData(billingData);
      setSystemHealth(healthData);
      setLastUpdated(new Date());
      console.log('✅ [DASHBOARD DEBUG] Data set successfully');
    } catch (err) {
      console.error('❌ [DASHBOARD DEBUG] Error fetching dashboard data:', err);
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  // Initial data fetch
  useEffect(() => {
    fetchDashboardData();
  }, []);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      fetchDashboardData();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  // Loading state
  if (loading && !dashboardData) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '400px',
          flexDirection: 'column',
          gap: 2
        }}
      >
        <CircularProgress size={48} />
        <Typography variant="body1" color="text.secondary">
          Loading billing dashboard...
        </Typography>
      </Box>
    );
  }

  // Error state
  if (error && !dashboardData) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert 
          severity="error" 
          action={
            <motion.button
              onClick={fetchDashboardData}
              style={{
                background: 'none',
                border: 'none',
                color: 'inherit',
                cursor: 'pointer',
                textDecoration: 'underline'
              }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Retry
            </motion.button>
          }
        >
          {error}
        </Alert>
      </Box>
    );
  }

  if (!dashboardData) {
    return null;
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <Container maxWidth="xl" sx={{ py: 4 }}>
        {/* Section Header */}
        <motion.div variants={cardVariants}>
          <Box sx={{ mb: 4, textAlign: 'center' }}>
            <Typography 
              variant="h4" 
              component="h2" 
              sx={{ 
                fontWeight: 'bold',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                mb: 1
              }}
            >
              💰 Billing & Usage Dashboard
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Monitor your API usage, costs, and system performance in real-time
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
              Last updated: {lastUpdated.toLocaleTimeString()}
            </Typography>
          </Box>
        </motion.div>

        {/* Main Dashboard Grid */}
        <Grid container spacing={3}>
          {/* Top Row - Overview Cards */}
          <Grid item xs={12} md={4}>
            <motion.div variants={cardVariants}>
              <BillingOverview 
                usageStats={dashboardData.current_usage}
                onRefresh={fetchDashboardData}
              />
            </motion.div>
          </Grid>

          <Grid item xs={12} md={4}>
            <motion.div variants={cardVariants}>
              <SystemHealthIndicator 
                systemHealth={systemHealth}
                onRefresh={fetchDashboardData}
              />
            </motion.div>
          </Grid>

          <Grid item xs={12} md={4}>
            <motion.div variants={cardVariants}>
              <UsageAlerts 
                alerts={dashboardData.alerts}
                onMarkRead={billingService.markAlertRead}
              />
            </motion.div>
          </Grid>

          {/* Middle Row - Cost Breakdown */}
          <Grid item xs={12} lg={6}>
            <motion.div variants={cardVariants}>
              <CostBreakdown 
                providerBreakdown={dashboardData.current_usage.provider_breakdown}
                totalCost={dashboardData.current_usage.total_cost}
              />
            </motion.div>
          </Grid>

          {/* Middle Row - Usage Trends */}
          <Grid item xs={12} lg={6}>
            <motion.div variants={cardVariants}>
              <UsageTrends 
                trends={dashboardData.trends}
                projections={dashboardData.projections}
              />
            </motion.div>
          </Grid>

          {/* Bottom Row - Detailed Metrics */}
          <Grid item xs={12}>
            <motion.div variants={cardVariants}>
              <Card 
                sx={{ 
                  background: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
                  backdropFilter: 'blur(10px)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: 3
                }}
              >
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
                    <BarChart3 size={20} />
                    Detailed Usage Metrics
                  </Typography>
                  
                  <Grid container spacing={3}>
                    {/* Usage Summary */}
                    <Grid item xs={12} sm={6} md={3}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" sx={{ color: 'primary.main', fontWeight: 'bold' }}>
                          {dashboardData.current_usage.total_calls.toLocaleString()}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Total API Calls
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          This month
                        </Typography>
                      </Box>
                    </Grid>

                    {/* Token Usage */}
                    <Grid item xs={12} sm={6} md={3}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" sx={{ color: 'secondary.main', fontWeight: 'bold' }}>
                          {(dashboardData.current_usage.total_tokens / 1000).toFixed(1)}k
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Tokens Used
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          This month
                        </Typography>
                      </Box>
                    </Grid>

                    {/* Average Response Time */}
                    <Grid item xs={12} sm={6} md={3}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" sx={{ color: 'warning.main', fontWeight: 'bold' }}>
                          {dashboardData.current_usage.avg_response_time.toFixed(0)}ms
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Avg Response Time
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Last 24 hours
                        </Typography>
                      </Box>
                    </Grid>

                    {/* Error Rate */}
                    <Grid item xs={12} sm={6} md={3}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography 
                          variant="h4" 
                          sx={{ 
                            color: dashboardData.current_usage.error_rate > 5 ? 'error.main' : 'success.main',
                            fontWeight: 'bold' 
                          }}
                        >
                          {dashboardData.current_usage.error_rate.toFixed(2)}%
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Error Rate
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Last 24 hours
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        </Grid>
      </Container>
    </motion.div>
  );
};

export default BillingDashboard;
