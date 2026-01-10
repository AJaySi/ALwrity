import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import { motion } from 'framer-motion';
import { 
  DollarSign, 
  RefreshCw,
  Info
} from 'lucide-react';

// Types
import { UsageStats } from '../../types/billing';

// Utils
import { 
  formatCurrency, 
  formatNumber, 
  formatPercentage,
  getUsageStatusIcon,
  calculateUsagePercentage
} from '../../services/billingService';

// Shared Components
import { AnimatedNumber } from '../shared/AnimatedNumber';
import { AnimatedProgressBar } from '../shared/AnimatedProgressBar';
import LiveCostCounter from './LiveCostCounter';

// Terminal Theme
import {
  TerminalCard,
  TerminalCardContent,
  TerminalTypography,
  TerminalChip,
  TerminalChipSuccess,
  TerminalChipError,
  TerminalChipWarning,
  terminalColors
} from '../SchedulerDashboard/terminalTheme';

interface BillingOverviewProps {
  usageStats: UsageStats;
  onRefresh: () => void;
  terminalTheme?: boolean;
}

const BillingOverview: React.FC<BillingOverviewProps> = ({ 
  usageStats, 
  onRefresh,
  terminalTheme = false
}) => {
  // Conditional component selection based on terminal theme
  const CardComponent = terminalTheme ? TerminalCard : Card;
  const CardContentComponent = terminalTheme ? TerminalCardContent : CardContent;
  const TypographyComponent = terminalTheme ? TerminalTypography : Typography;
  
  const [previousCost, setPreviousCost] = useState<number | undefined>(undefined);
  
  // Track previous cost for velocity calculation
  useEffect(() => {
    if (usageStats.total_cost !== undefined) {
      setPreviousCost(usageStats.total_cost);
    }
  }, [usageStats.total_cost]);
  
  const costUsagePercentage = calculateUsagePercentage(
    usageStats.total_cost, 
    usageStats.limits.limits.monthly_cost || 1
  );

  const getStatusChip = () => {
    const status: string = usageStats.usage_status;
    const icon = getUsageStatusIcon(status);
    
    // Helper function to format status label
    const formatStatusLabel = (statusStr: string): string => {
      return statusStr.charAt(0).toUpperCase() + statusStr.slice(1).replace('_', ' ');
    };
    
    if (terminalTheme) {
      if (status === 'active') {
        return (
          <TerminalChipSuccess
            icon={<span>{icon}</span>}
            label={formatStatusLabel(status)}
            size="small"
            sx={{ fontWeight: 'bold' }}
          />
        );
      } else if (status === 'warning') {
        return (
          <TerminalChipWarning
            icon={<span>{icon}</span>}
            label={formatStatusLabel(status)}
            size="small"
            sx={{ fontWeight: 'bold' }}
          />
        );
      } else if (status === 'limit_reached') {
        return (
          <TerminalChipError
            icon={<span>{icon}</span>}
            label={formatStatusLabel(status)}
            size="small"
            sx={{ fontWeight: 'bold' }}
          />
        );
      }
      return (
        <TerminalChip
          icon={<span>{icon}</span>}
          label={formatStatusLabel(status)}
          size="small"
          sx={{ fontWeight: 'bold' }}
        />
      );
    }
    
    let chipColor: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' = 'default';
    if (status === 'active') chipColor = 'success';
    else if (status === 'warning') chipColor = 'warning';
    else if (status === 'limit_reached') chipColor = 'error';

    return (
      <Chip
        icon={<span>{icon}</span>}
        label={formatStatusLabel(status)}
        color={chipColor}
        size="small"
        sx={{ fontWeight: 'bold' }}
      />
    );
  };

  const cardStyles = terminalTheme
    ? {
        height: '100%',
        backgroundColor: terminalColors.background,
        border: `1px solid ${terminalColors.border}`,
        borderRadius: 3,
        position: 'relative' as const,
        overflow: 'hidden' as const
      }
    : {
        height: '100%',
        background: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255,255,255,0.1)',
        borderRadius: 3,
        position: 'relative' as const,
        overflow: 'hidden' as const
      };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      whileHover={{ scale: 1.02 }}
    >
      <CardComponent sx={cardStyles}>
        {/* Header */}
        <CardContentComponent sx={{ pb: 1 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <TypographyComponent variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, fontWeight: 'bold' }}>
              <DollarSign size={20} color={terminalTheme ? terminalColors.text : undefined} />
              Billing Overview
            </TypographyComponent>
            <Tooltip title="View your current billing status, usage metrics, and subscription plan details">
              <Info size={16} color={terminalTheme ? terminalColors.textSecondary : "rgba(255,255,255,0.7)"} />
            </Tooltip>
            <Tooltip title="Refresh data">
              <IconButton 
                size="small" 
                onClick={onRefresh}
                sx={{ 
                  color: terminalTheme ? terminalColors.text : 'text.secondary',
                  '&:hover': { color: terminalTheme ? terminalColors.secondary : 'primary.main' }
                }}
              >
                <RefreshCw size={16} />
              </IconButton>
            </Tooltip>
          </Box>

          {/* Status Chip */}
          <Box sx={{ mb: 3 }}>
            {getStatusChip()}
          </Box>
        </CardContentComponent>

        <CardContentComponent sx={{ pt: 0 }}>
          {/* Live Cost Counter */}
          <Box sx={{ mb: 3 }}>
            <LiveCostCounter
              currentCost={usageStats.total_cost}
              previousCost={previousCost}
              velocity={0} // TODO: Calculate from trends if available
              terminalTheme={terminalTheme}
              terminalColors={terminalColors}
              TypographyComponent={TypographyComponent}
            />
          </Box>

          {/* Usage Metrics */}
          <Box sx={{ mb: 3 }}>
            <Tooltip title="Total number of API requests made this billing period">
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <TypographyComponent variant="body2" sx={{ color: terminalTheme ? terminalColors.textSecondary : 'rgba(255,255,255,0.7)' }}>
                  API Calls
                </TypographyComponent>
                <TypographyComponent variant="body2" sx={{ fontWeight: 'bold', color: terminalTheme ? terminalColors.text : '#ffffff' }}>
                  <AnimatedNumber 
                    value={usageStats.total_calls}
                    format={(n) => formatNumber(n)}
                  />
                </TypographyComponent>
              </Box>
            </Tooltip>
            
            <Tooltip title="Total tokens processed across all API providers (input + output tokens)">
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <TypographyComponent variant="body2" sx={{ color: terminalTheme ? terminalColors.textSecondary : 'rgba(255,255,255,0.7)' }}>
                  Tokens Used
                </TypographyComponent>
                <TypographyComponent variant="body2" sx={{ fontWeight: 'bold', color: terminalTheme ? terminalColors.text : '#ffffff' }}>
                  <AnimatedNumber 
                    value={usageStats.total_tokens}
                    format={(n) => formatNumber(n)}
                  />
                </TypographyComponent>
              </Box>
            </Tooltip>

            <Tooltip title="Average response time for API requests in the last 24 hours">
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <TypographyComponent variant="body2" sx={{ color: terminalTheme ? terminalColors.textSecondary : 'rgba(255,255,255,0.7)' }}>
                  Avg Response Time
                </TypographyComponent>
                <TypographyComponent variant="body2" sx={{ fontWeight: 'bold', color: terminalTheme ? terminalColors.text : '#ffffff' }}>
                  {usageStats.avg_response_time.toFixed(0)}ms
                </TypographyComponent>
              </Box>
            </Tooltip>
          </Box>

          {/* Cost Usage Progress */}
          {usageStats.limits.limits.monthly_cost > 0 && (
            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <TypographyComponent variant="body2" sx={{ color: terminalTheme ? terminalColors.textSecondary : 'rgba(255,255,255,0.7)' }}>
                  Monthly Cost Limit
                </TypographyComponent>
                <TypographyComponent variant="body2" sx={{ fontWeight: 'bold', color: terminalTheme ? terminalColors.text : '#ffffff' }}>
                  {formatPercentage(costUsagePercentage)}
                </TypographyComponent>
              </Box>
              <AnimatedProgressBar
                value={Math.min(costUsagePercentage, 100)}
                height={8}
                color={terminalTheme
                  ? (costUsagePercentage > 80 ? terminalColors.error : 
                     costUsagePercentage > 60 ? terminalColors.warning : terminalColors.success)
                  : (costUsagePercentage > 80 ? '#ef4444' : 
                     costUsagePercentage > 60 ? '#f59e0b' : '#22c55e')
                }
                showPercentage={false}
              />
              <TypographyComponent variant="caption" sx={{ mt: 0.5, display: 'block', color: terminalTheme ? terminalColors.textSecondary : 'rgba(255,255,255,0.7)' }}>
                {formatCurrency(usageStats.total_cost)} of {formatCurrency(usageStats.limits.limits.monthly_cost)} limit
              </TypographyComponent>
            </Box>
          )}

          {/* Plan Information */}
          <Box 
            sx={{ 
              p: 2, 
              backgroundColor: terminalTheme ? terminalColors.backgroundLight : 'rgba(255,255,255,0.05)',
              borderRadius: 2,
              border: terminalTheme ? `1px solid ${terminalColors.border}` : '1px solid rgba(255,255,255,0.1)'
            }}
          >
            <TypographyComponent variant="body2" sx={{ mb: 1, color: terminalTheme ? terminalColors.textSecondary : 'rgba(255,255,255,0.8)' }}>
              Current Plan
            </TypographyComponent>
            <TypographyComponent variant="h6" sx={{ fontWeight: 'bold', mb: 1, color: terminalTheme ? terminalColors.text : '#ffffff' }}>
              {usageStats.limits.plan_name}
            </TypographyComponent>
            <TypographyComponent variant="caption" sx={{ color: terminalTheme ? terminalColors.textSecondary : 'rgba(255,255,255,0.7)' }}>
              {usageStats.limits.tier.charAt(0).toUpperCase() + usageStats.limits.tier.slice(1)} Tier
            </TypographyComponent>
          </Box>

          {/* Quick Stats */}
          <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-around' }}>
            <Box sx={{ textAlign: 'center' }}>
              <TypographyComponent variant="h6" sx={{ fontWeight: 'bold', color: terminalTheme ? terminalColors.text : 'primary.main' }}>
                {usageStats.usage_percentages.gemini_calls.toFixed(0)}%
              </TypographyComponent>
              <TypographyComponent variant="caption" sx={{ color: terminalTheme ? terminalColors.textSecondary : 'rgba(255,255,255,0.7)' }}>
                Gemini Usage
              </TypographyComponent>
            </Box>
            <Box sx={{ textAlign: 'center' }}>
              <TypographyComponent variant="h6" sx={{ fontWeight: 'bold', color: terminalTheme ? terminalColors.text : 'secondary.main' }}>
                {usageStats.error_rate.toFixed(1)}%
              </TypographyComponent>
              <TypographyComponent variant="caption" sx={{ color: terminalTheme ? terminalColors.textSecondary : 'rgba(255,255,255,0.7)' }}>
                Error Rate
              </TypographyComponent>
            </Box>
          </Box>
        </CardContentComponent>

        {/* Decorative Elements - only show in non-terminal theme */}
        {!terminalTheme && (
          <>
            <Box
              sx={{
                position: 'absolute',
                top: -50,
                right: -50,
                width: 100,
                height: 100,
                background: 'radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 70%)',
                borderRadius: '50%',
                pointerEvents: 'none'
              }}
            />
            <Box
              sx={{
                position: 'absolute',
                bottom: -30,
                left: -30,
                width: 60,
                height: 60,
                background: 'radial-gradient(circle, rgba(118, 75, 162, 0.1) 0%, transparent 70%)',
                borderRadius: '50%',
                pointerEvents: 'none'
              }}
            />
          </>
        )}
      </CardComponent>
    </motion.div>
  );
};

export default BillingOverview;
