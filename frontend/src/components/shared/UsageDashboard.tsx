import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Chip,
  Typography,
  Tooltip,
  CircularProgress,
  Alert,
  IconButton,
  Menu,
  MenuItem,
  LinearProgress
} from '@mui/material';
import {
  TrendingUp,
  Warning,
  CheckCircle,
  Refresh,
  MoreVert,
  Dashboard
} from '@mui/icons-material';
import { useUser } from '@clerk/clerk-react';
import { apiClient } from '../../api/client';
import { useSubscription } from '../../contexts/SubscriptionContext';
import { usePriority2Alerts } from '../../hooks/usePriority2Alerts';
import Priority2AlertBanner from './Priority2AlertBanner';

interface UsageStats {
  total_calls: number;
  total_cost: number;
  usage_status: string;
  provider_breakdown: Record<string, {
    calls: number;
    tokens: number;
    cost: number;
  }>;
}

interface UsageLimits {
  limits: {
    gemini_calls: number;
    openai_calls: number;
    anthropic_calls: number;
    mistral_calls: number;
    tavily_calls: number;
    serper_calls: number;
    metaphor_calls: number;
    firecrawl_calls: number;
    stability_calls: number;
    monthly_cost: number;
  };
}

interface DashboardData {
  current_usage: UsageStats;
  limits: UsageLimits;
  projections: {
    projected_monthly_cost: number;
    cost_limit: number;
    projected_usage_percentage: number;
  };
  summary: {
    total_api_calls_this_month: number;
    total_cost_this_month: number;
    usage_status: string;
    unread_alerts: number;
  };
}

interface UsageDashboardProps {
  compact?: boolean;
  showFullDashboard?: boolean;
}

const UsageDashboard: React.FC<UsageDashboardProps> = ({ 
  compact = true, 
  showFullDashboard = false 
}) => {
  const { subscription } = useSubscription();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const { user } = useUser();
  const userId = localStorage.getItem('user_id') || user?.id;

  // Priority 2 Alerts - automatically appears in all tool headers
  const { alerts: priority2Alerts, dismissAlert: dismissPriority2Alert } = usePriority2Alerts({
    userId: userId || undefined,
    enabled: !!userId && subscription?.active,
    checkInterval: 120000, // Check every 2 minutes
  });

  const fetchUsageData = useCallback(async () => {
    if (!userId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiClient.get(`/api/subscription/dashboard/${userId}`);
      setDashboardData(response.data.data);
      setLastUpdated(new Date());
    } catch (err) {
      console.error('Error fetching usage data:', err);
      setError('Failed to load usage data');
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    fetchUsageData();

    // Listen for custom event to refresh usage data
    const handleUsageRefresh = () => {
      console.log('UsageDashboard: Refreshing usage data due to event');
      fetchUsageData();
    };

    window.addEventListener('alwrity:refresh-usage', handleUsageRefresh);

    return () => {
      window.removeEventListener('alwrity:refresh-usage', handleUsageRefresh);
    };
  }, [fetchUsageData, userId]);

  const handleRefresh = () => {
    fetchUsageData();
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleViewFullDashboard = () => {
    handleMenuClose();
    window.open('/billing', '_blank');
  };

  const getUsageColor = (used: number, limit: number) => {
    const percentage = (used / limit) * 100;
    if (percentage >= 90) return '#f44336'; // Red
    if (percentage >= 75) return '#ff9800'; // Orange
    if (percentage >= 50) return '#ffeb3b'; // Yellow
    return '#4caf50'; // Green
  };

  const getUsageStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle sx={{ fontSize: 16, color: '#4caf50' }} />;
      case 'warning': return <Warning sx={{ fontSize: 16, color: '#ff9800' }} />;
      case 'limit_exceeded': return <Warning sx={{ fontSize: 16, color: '#f44336' }} />;
      default: return <CheckCircle sx={{ fontSize: 16, color: '#4caf50' }} />;
    }
  };

  const getProviderDisplayName = (provider: string) => {
    const names: Record<string, string> = {
      'gemini': 'Gemini',
      'openai': 'OpenAI',
      'anthropic': 'Claude',
      'mistral': 'Mistral',
      'tavily': 'Tavily',
      'serper': 'Serper',
      'metaphor': 'Metaphor',
      'firecrawl': 'Firecrawl',
      'stability': 'Stability',
      'wavespeed': 'WaveSpeed'
    };
    return names[provider] || provider;
  };

  if (!dashboardData) {
    if (loading) {
      return (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <CircularProgress size={16} />
          <Typography variant="caption" color="text.secondary">
            Loading usage...
          </Typography>
        </Box>
      );
    }
    
    if (error) {
      return (
        <Alert severity="error" sx={{ py: 0.5 }}>
          <Typography variant="caption">{error}</Typography>
        </Alert>
      );
    }
    
    // If no data and not loading/error, try to fetch again or show placeholder
    if (userId && !dashboardData) {
       // Optional: could auto-trigger another fetch here if needed, but useEffect handles it
       return <Box />;
    }
    
    return <Box />;
  }

  if (compact) {
    // Compact view - show key metrics as chips
    // Use current_usage for accurate cost (properly coerced from provider breakdown)
    // Fallback to summary if current_usage is not available
    const totalCalls = dashboardData.current_usage?.total_calls ?? dashboardData.summary.total_api_calls_this_month;
    const totalCost = dashboardData.current_usage?.total_cost ?? dashboardData.summary.total_cost_this_month ?? 0;
    const monthlyLimit = dashboardData.limits.limits.monthly_cost;
    const usagePercentage = monthlyLimit > 0 ? (totalCost / monthlyLimit) * 100 : 0;

    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
        {/* Priority 2 Alerts - Shows cost trends, OSS recommendations, spending velocity */}
        {priority2Alerts.length > 0 && (
          <Box sx={{ mb: 0.5 }}>
            <Priority2AlertBanner
              alerts={priority2Alerts}
              onDismiss={dismissPriority2Alert}
              maxAlerts={1} // Show only 1 alert in compact view
            />
          </Box>
        )}
        
        {/* Usage Statistics */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {/* Total API Calls */}
        <Tooltip title={`${totalCalls.toLocaleString()} API calls this month`}>
          <Chip
            icon={getUsageStatusIcon(dashboardData.summary.usage_status)}
            label={`${totalCalls.toLocaleString()}`}
            size="small"
            variant="outlined"
            sx={{
              bgcolor: 'rgba(33, 150, 243, 0.1)',
              borderColor: '#2196f3',
              color: '#1976d2',
              fontWeight: 600,
              '& .MuiChip-icon': {
                color: '#2196f3'
              }
            }}
          />
        </Tooltip>

        {/* Monthly Cost */}
        <Tooltip title={`$${totalCost.toFixed(2)} of $${monthlyLimit} monthly limit`}>
          <Chip
            icon={<TrendingUp sx={{ fontSize: 14 }} />}
            label={`$${totalCost.toFixed(2)}`}
            size="small"
            variant="outlined"
            sx={{
              bgcolor: `${getUsageColor(totalCost, monthlyLimit)}20`,
              borderColor: getUsageColor(totalCost, monthlyLimit),
              color: getUsageColor(totalCost, monthlyLimit),
              fontWeight: 600,
              '& .MuiChip-icon': {
                color: getUsageColor(totalCost, monthlyLimit)
              }
            }}
          />
        </Tooltip>

        {/* Usage Progress */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, minWidth: 60 }}>
          <LinearProgress
            variant="determinate"
            value={Math.min(usagePercentage, 100)}
            sx={{
              width: 40,
              height: 6,
              borderRadius: 3,
              bgcolor: 'rgba(0,0,0,0.1)',
              '& .MuiLinearProgress-bar': {
                bgcolor: getUsageColor(totalCost, monthlyLimit),
                borderRadius: 3
              }
            }}
          />
          <Typography variant="caption" sx={{ fontSize: '0.7rem', fontWeight: 600 }}>
            {usagePercentage.toFixed(0)}%
          </Typography>
        </Box>

        {/* Refresh Button */}
        <Tooltip title="Refresh usage data">
          <IconButton
            size="small"
            onClick={handleRefresh}
            disabled={loading}
            sx={{ 
              p: 0.5,
              '&:hover': { bgcolor: 'rgba(0,0,0,0.04)' }
            }}
          >
            <Refresh sx={{ fontSize: 16 }} />
          </IconButton>
        </Tooltip>

        {/* More Options */}
        <Tooltip title="Usage options">
          <IconButton
            size="small"
            onClick={handleMenuOpen}
            sx={{ 
              p: 0.5,
              '&:hover': { bgcolor: 'rgba(0,0,0,0.04)' }
            }}
          >
            <MoreVert sx={{ fontSize: 16 }} />
          </IconButton>
        </Tooltip>

        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
          transformOrigin={{ vertical: 'top', horizontal: 'right' }}
        >
          <MenuItem onClick={handleViewFullDashboard}>
            <Dashboard sx={{ mr: 1, fontSize: 18 }} />
            View Full Dashboard
          </MenuItem>
          <MenuItem onClick={handleRefresh}>
            <Refresh sx={{ mr: 1, fontSize: 18 }} />
            Refresh Data
          </MenuItem>
          {lastUpdated && (
            <Box sx={{ px: 2, py: 1 }}>
              <Typography variant="caption" color="text.secondary">
                Last updated: {lastUpdated.toLocaleTimeString()}
              </Typography>
            </Box>
          )}
        </Menu>
        </Box>
      </Box>
    );
  }

  // Full dashboard view (for dedicated usage page)
  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Usage Dashboard
      </Typography>
      
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 2 }}>
        {/* Total Calls */}
        <Box sx={{ p: 2, border: '1px solid #e0e0e0', borderRadius: 2 }}>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Total API Calls
          </Typography>
          <Typography variant="h4" color="primary">
            {(dashboardData.current_usage?.total_calls ?? dashboardData.summary.total_api_calls_this_month).toLocaleString()}
          </Typography>
        </Box>

        {/* Total Cost */}
        <Box sx={{ p: 2, border: '1px solid #e0e0e0', borderRadius: 2 }}>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Monthly Cost
          </Typography>
          <Typography variant="h4" color="secondary">
            ${(dashboardData.current_usage?.total_cost ?? dashboardData.summary.total_cost_this_month ?? 0).toFixed(2)}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            of ${dashboardData.limits.limits.monthly_cost} limit
          </Typography>
        </Box>

        {/* Usage by Provider */}
        <Box sx={{ p: 2, border: '1px solid #e0e0e0', borderRadius: 2 }}>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Usage by Provider
          </Typography>
          {Object.entries(dashboardData.current_usage.provider_breakdown).map(([provider, stats]) => (
            <Box key={provider} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2">
                {getProviderDisplayName(provider)}
              </Typography>
              <Typography variant="body2" fontWeight={600}>
                {stats.calls.toLocaleString()}
              </Typography>
            </Box>
          ))}
        </Box>
      </Box>
    </Box>
  );
};

export default UsageDashboard;
