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
  LinearProgress,
  Select,
  FormControl,
  InputLabel,
  SelectChangeEvent
} from '@mui/material';
import {
  TrendingUp,
  Warning,
  CheckCircle,
  Refresh,
  MoreVert,
  Dashboard,
  CalendarMonth
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
  billing_period?: string;
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
  trends?: { periods: string[] };
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
  const [selectedPeriod, setSelectedPeriod] = useState<string>('');
  const [availablePeriods, setAvailablePeriods] = useState<string[]>([]);

  const { user } = useUser();
  const userId = localStorage.getItem('user_id') || user?.id;

  // Priority 2 Alerts - automatically appears in all tool headers
  const { alerts: priority2Alerts, dismissAlert: dismissPriority2Alert } = usePriority2Alerts({
    userId: userId || undefined,
    enabled: !!userId && subscription?.active,
    checkInterval: 120000, // Check every 2 minutes
  });

  const fetchUsageData = useCallback(async (period?: string) => {
    if (!userId) return;
    
    setLoading(true);
    setError(null);
    try {
      const url = period 
        ? `/api/subscription/dashboard/${userId}?billing_period=${period}`
        : `/api/subscription/dashboard/${userId}`;
        
      const response = await apiClient.get<any>(url);
      
      if (response.data && response.data.success) {
        setDashboardData(response.data.data);
        setLastUpdated(new Date());
        
        // Extract available periods from trends if not set
        if (!period && response.data.data.trends?.periods) {
          setAvailablePeriods(response.data.data.trends.periods);
          // Set current period if not selected
          if (!selectedPeriod) {
            const current = new Date().toISOString().slice(0, 7); // YYYY-MM
            setSelectedPeriod(current);
          }
        }
      } else {
        throw new Error(response.data?.error || 'Failed to fetch usage data');
      }
    } catch (err: any) {
      console.error('Error fetching usage data:', err);
      setError(err.message || 'Failed to load usage statistics');
    } finally {
      setLoading(false);
    }
  }, [userId]);

  const handlePeriodChange = (event: SelectChangeEvent) => {
    const period = event.target.value;
    setSelectedPeriod(period);
    fetchUsageData(period);
  };

  useEffect(() => {
    // Initial fetch
    if (userId) {
      fetchUsageData();
    }
  }, [userId, fetchUsageData]); // Added fetchUsageData to deps since it's memoized

  const handleRefresh = () => {
    fetchUsageData(selectedPeriod);
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleViewFullDashboard = () => {
    handleMenuClose();
    window.location.href = '/dashboard';
  };

  const getUsageColor = (current: number, max: number) => {
    if (max === 0) return '#757575';
    const percentage = (current / max) * 100;
    if (percentage >= 100) return '#d32f2f'; // error
    if (percentage >= 80) return '#ed6c02'; // warning
    return '#2e7d32'; // success
  };

  const getProviderDisplayName = (provider: string) => {
    // Map internal provider names to display names
    const displayNames: Record<string, string> = {
      'gemini': 'Google Gemini',
      'openai': 'OpenAI GPT-4',
      'anthropic': 'Anthropic Claude',
      'mistral': 'HuggingFace (Mistral)',
      'tavily': 'Tavily Search',
      'serper': 'Serper Google',
      'metaphor': 'Exa Search', // Metaphor is now Exa
      'exa': 'Exa Search',
      'firecrawl': 'Firecrawl',
      'stability': 'Stability AI',
      'video': 'Video Gen',
      'audio': 'Audio Gen',
      'image_edit': 'Image Edit',
      'wavespeed': 'WaveSpeed'
    };
    return displayNames[provider] || provider.charAt(0).toUpperCase() + provider.slice(1);
  };

  if (!dashboardData && loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
        <CircularProgress size={24} />
      </Box>
    );
  }

  if (error && !dashboardData) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
        <IconButton size="small" onClick={() => fetchUsageData(selectedPeriod)}>
          <Refresh fontSize="small" />
        </IconButton>
      </Alert>
    );
  }

  if (!dashboardData) return null;

  const currentUsage = dashboardData.current_usage;
  const limits = dashboardData.limits;

  if (compact) {
    // Compact view - show key metrics as chips
    // Use current_usage for accurate cost (properly coerced from provider breakdown)
    // Fallback to summary if current_usage is not available
    const usageData = dashboardData?.current_usage || {
        total_calls: dashboardData?.summary?.total_api_calls_this_month || 0,
        total_cost: dashboardData?.summary?.total_cost_this_month || 0,
        usage_status: dashboardData?.summary?.usage_status || 'active',
        provider_breakdown: {}
    };
    
    const totalCalls = usageData.total_calls;
    const totalCost = usageData.total_cost;
    const monthlyLimit = dashboardData?.limits?.limits?.monthly_cost || 0;
    const usagePercentage = monthlyLimit > 0 ? (totalCost / monthlyLimit) * 100 : 0;

    return (
      <Box sx={{ width: '100%' }}>
        {/* Priority 2 Alert Banner (Usage limits) */}
        {priority2Alerts.length > 0 && (
          <Box sx={{ mb: 1 }}>
            <Priority2AlertBanner 
              alerts={[priority2Alerts[0]]} 
              onDismiss={() => dismissPriority2Alert(priority2Alerts[0].id)} 
            />
          </Box>
        )}
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
        
        {/* Month Selector for Compact View */}
        {availablePeriods.length > 1 && (
          <FormControl variant="standard" size="small" sx={{ minWidth: 100, mr: 1 }}>
            <Select
              value={selectedPeriod}
              onChange={handlePeriodChange}
              disableUnderline
              sx={{ 
                fontSize: '0.875rem', 
                fontWeight: 500,
                color: 'text.secondary',
                '& .MuiSelect-select': { py: 0.5 }
              }}
              IconComponent={() => <CalendarMonth sx={{ fontSize: 16, color: 'action.active', ml: 0.5 }} />}
            >
              {availablePeriods.map((period) => (
                <MenuItem key={period} value={period} dense>
                  {period}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        )}

        {/* Status Chip */}
        <Tooltip title={`Status: ${usageData.usage_status}`}>
          <Chip
            icon={usageData.usage_status === 'active' ? <CheckCircle sx={{ fontSize: 14 }} /> : <Warning sx={{ fontSize: 14 }} />}
            label={usageData.usage_status === 'limit_reached' ? 'Limit Reached' : 'Active'}
            size="small"
            color={usageData.usage_status === 'limit_reached' ? 'error' : usageData.usage_status === 'warning' ? 'warning' : 'success'}
            variant="outlined"
            sx={{ fontWeight: 600 }}
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
  const usageData = dashboardData?.current_usage || {
    total_calls: dashboardData?.summary?.total_api_calls_this_month || 0,
    total_cost: dashboardData?.summary?.total_cost_this_month || 0,
    provider_breakdown: {}
  };
  
  return (
    <Box sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          Usage Dashboard
        </Typography>
        
        {/* Month Selector for Full View */}
        {availablePeriods.length > 1 && (
          <FormControl variant="outlined" size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Billing Period</InputLabel>
            <Select
              value={selectedPeriod}
              onChange={handlePeriodChange}
              label="Billing Period"
              startAdornment={<CalendarMonth sx={{ fontSize: 18, mr: 1, color: 'action.active' }} />}
            >
              {availablePeriods.map((period) => (
                <MenuItem key={period} value={period}>
                  {period}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        )}
      </Box>
      
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 2 }}>
        {/* Total Calls */}
        <Box sx={{ p: 2, border: '1px solid #e0e0e0', borderRadius: 2 }}>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Total API Calls
          </Typography>
          <Typography variant="h4" color="primary">
            {usageData.total_calls.toLocaleString()}
          </Typography>
        </Box>

        {/* Total Cost */}
        <Box sx={{ p: 2, border: '1px solid #e0e0e0', borderRadius: 2 }}>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Monthly Cost
          </Typography>
          <Typography variant="h4" color="secondary">
            ${usageData.total_cost.toFixed(2)}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            of ${dashboardData?.limits?.limits?.monthly_cost || 0} limit
          </Typography>
        </Box>

        {/* Usage by Provider */}
        <Box sx={{ p: 2, border: '1px solid #e0e0e0', borderRadius: 2 }}>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Usage by Provider
          </Typography>
          {Object.entries(usageData.provider_breakdown || {}).map(([provider, stats]) => (
            <Box key={provider} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2">
                {getProviderDisplayName(provider)}
              </Typography>
              <Typography variant="body2" fontWeight={600}>
                {(stats as any).calls?.toLocaleString() || 0}
              </Typography>
            </Box>
          ))}
          {Object.keys(usageData.provider_breakdown || {}).length === 0 && (
            <Typography variant="body2" color="text.secondary" fontStyle="italic">
              No usage this period
            </Typography>
          )}
        </Box>
      </Box>
    </Box>
  );
};

export default UsageDashboard;
