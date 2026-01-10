import React from 'react';
import { Card, CardContent, Typography, Chip } from '@mui/material';
import { motion } from 'framer-motion';
import {
  TerminalCard,
  TerminalCardContent,
  TerminalTypography,
  TerminalChip,
  terminalColors
} from '../../SchedulerDashboard/terminalTheme';

// Hooks
import { useCompactBillingData } from './hooks/useCompactBillingData';

// Components
import { DashboardHeader } from './components/DashboardHeader';
import { MainMetricsGrid } from './components/MainMetricsGrid';
import { CostEfficiencyMetrics } from './components/CostEfficiencyMetrics';
import { UsageLimitRings } from './components/UsageLimitRings';
import { MonthlyBudgetUsage } from './components/MonthlyBudgetUsage';
import { AlertsSection } from './components/AlertsSection';

interface CompactBillingDashboardProps {
  userId?: string;
  terminalTheme?: boolean;
}

/**
 * CompactBillingDashboard - Main orchestrator component
 * 
 * Refactored from monolithic component into modular structure:
 * - Data fetching: useCompactBillingData hook
 * - UI Components: Separated into focused, reusable components
 * - Utils: Formatting utilities extracted
 */
const CompactBillingDashboard: React.FC<CompactBillingDashboardProps> = ({ 
  userId, 
  terminalTheme = false 
}) => {
  // Conditional component selection based on terminal theme
  const CardComponent = terminalTheme ? TerminalCard : Card;
  const CardContentComponent = terminalTheme ? TerminalCardContent : CardContent;
  const TypographyComponent = terminalTheme ? TerminalTypography : Typography;
  const ChipComponent = terminalTheme ? TerminalChip : Chip;

  // Data fetching hook
  const {
    dashboardData,
    systemHealth,
    loading,
    error,
    lastRefreshTime,
    healthError,
    sparklineData,
    refresh
  } = useCompactBillingData(userId);

  // Loading state
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

  // Error state
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
        <CardContentComponent sx={{ pt: 2 }}>
          {/* Header */}
          <DashboardHeader
            lastRefreshTime={lastRefreshTime}
            onRefresh={() => refresh(true)}
            loading={loading}
            terminalTheme={terminalTheme}
            TypographyComponent={TypographyComponent}
          />
          
          {/* Main Metrics Grid */}
          <MainMetricsGrid
            currentUsage={current_usage}
            systemHealth={systemHealth}
            healthError={healthError}
            sparklineData={sparklineData}
            terminalTheme={terminalTheme}
            TypographyComponent={TypographyComponent}
          />

          {/* Cost Efficiency Metrics */}
          <CostEfficiencyMetrics
            currentUsage={current_usage}
            terminalTheme={terminalTheme}
            TypographyComponent={TypographyComponent}
          />

          {/* Usage Limit Rings */}
          <UsageLimitRings
            currentUsage={current_usage}
            limits={limits}
            terminalTheme={terminalTheme}
            TypographyComponent={TypographyComponent}
          />

          {/* Monthly Budget Usage */}
          <MonthlyBudgetUsage
            currentUsage={current_usage}
            limits={limits}
            terminalTheme={terminalTheme}
            TypographyComponent={TypographyComponent}
          />

          {/* Alerts Section */}
          <AlertsSection
            alerts={alerts}
            terminalTheme={terminalTheme}
            TypographyComponent={TypographyComponent}
            ChipComponent={ChipComponent}
          />
        </CardContentComponent>
      </CardComponent>
    </motion.div>
  );
};

export default CompactBillingDashboard;
