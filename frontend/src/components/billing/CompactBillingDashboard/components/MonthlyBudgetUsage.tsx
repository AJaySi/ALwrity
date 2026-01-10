import React from 'react';
import { Box, Tooltip } from '@mui/material';
import { AlertTriangle } from 'lucide-react';
import { TerminalTypography } from '../../../SchedulerDashboard/terminalTheme';
import { terminalColors } from '../../../SchedulerDashboard/terminalTheme';
import { AnimatedProgressBar } from '../../../shared/AnimatedProgressBar';
import ProviderCostComparison from '../../ProviderCostComparison';
import { formatCurrency } from '../utils/formatting';
import { DashboardData } from '../../../../types/billing';

interface MonthlyBudgetUsageProps {
  currentUsage: DashboardData['current_usage'];
  limits: DashboardData['limits'];
  terminalTheme?: boolean;
  TypographyComponent: typeof TerminalTypography | React.ComponentType<any>;
}

/**
 * MonthlyBudgetUsage - Displays monthly budget usage with progress bar and provider breakdown
 */
export const MonthlyBudgetUsage: React.FC<MonthlyBudgetUsageProps> = ({
  currentUsage,
  limits,
  terminalTheme = false,
  TypographyComponent
}) => {
  if (limits.limits.monthly_cost <= 0) return null;

  const usagePercentage = (currentUsage.total_cost / limits.limits.monthly_cost) * 100;
  const remainingBudget = limits.limits.monthly_cost - currentUsage.total_cost;
  const daysInMonth = new Date(new Date().getFullYear(), new Date().getMonth() + 1, 0).getDate();
  const currentDay = new Date().getDate();
  const daysRemaining = daysInMonth - currentDay;
  const avgDailyCost = currentUsage.total_cost / currentDay;
  const estimatedDaysUntilExhaustion = avgDailyCost > 0 ? Math.ceil(remainingBudget / avgDailyCost) : daysRemaining;
  
  // Determine warning level
  const isCritical = usagePercentage >= 95;
  const isWarning = usagePercentage >= 80;
  const isModerate = usagePercentage >= 50;

  return (
    <Box sx={{ mb: 3 }}>
      {/* Enhanced Warning Banner */}
      {(isCritical || isWarning || isModerate) && (
        <Box sx={{ 
          mb: 2, 
          p: 2.5, 
          ...(terminalTheme ? {
            backgroundColor: isCritical 
              ? terminalColors.error + '20'
              : isWarning 
              ? terminalColors.warning + '20'
              : terminalColors.secondary + '20',
            borderRadius: 3,
            border: `2px solid ${isCritical 
              ? terminalColors.error
              : isWarning 
              ? terminalColors.warning
              : terminalColors.secondary}`,
            position: 'relative',
            overflow: 'hidden',
            '&::before': {
              content: '""',
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: '4px',
              background: isCritical 
                ? terminalColors.error
                : isWarning 
                ? terminalColors.warning
                : terminalColors.secondary,
              zIndex: 1
            }
          } : {
            background: isCritical 
              ? 'linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(220, 38, 38, 0.15) 100%)'
              : isWarning 
              ? 'linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(217, 119, 6, 0.15) 100%)'
              : 'linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(37, 99, 235, 0.15) 100%)',
            borderRadius: 3,
            border: `2px solid ${isCritical 
              ? 'rgba(239, 68, 68, 0.5)'
              : isWarning 
              ? 'rgba(245, 158, 11, 0.5)'
              : 'rgba(59, 130, 246, 0.5)'}`,
            position: 'relative',
            overflow: 'hidden',
            '&::before': {
              content: '""',
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: '4px',
              background: isCritical 
                ? 'linear-gradient(90deg, #ef4444, #dc2626)'
                : isWarning 
                ? 'linear-gradient(90deg, #f59e0b, #d97706)'
                : 'linear-gradient(90deg, #3b82f6, #2563eb)',
              zIndex: 1
            }
          })
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
            <AlertTriangle 
              size={24} 
              color={terminalTheme 
                ? (isCritical ? terminalColors.error : isWarning ? terminalColors.warning : terminalColors.secondary)
                : (isCritical ? '#ef4444' : isWarning ? '#f59e0b' : '#3b82f6')
              } 
            />
            <Box sx={{ flex: 1 }}>
              <TypographyComponent variant="subtitle1" sx={{ 
                fontWeight: 700, 
                color: terminalTheme 
                  ? (isCritical ? terminalColors.error : isWarning ? terminalColors.warning : terminalColors.text)
                  : (isCritical ? '#ef4444' : isWarning ? '#f59e0b' : '#ffffff'),
                mb: 0.5
              }}>
                {isCritical 
                  ? '🚨 Critical: Approaching Budget Limit'
                  : isWarning 
                  ? '⚠️ Warning: High Budget Usage'
                  : 'ℹ️ Notice: 50% of Budget Used'
                }
              </TypographyComponent>
              <TypographyComponent variant="body2" sx={{ 
                color: terminalTheme ? terminalColors.textSecondary : 'rgba(255,255,255,0.9)',
                mb: 1
              }}>
                {isCritical 
                  ? `You've used ${usagePercentage.toFixed(1)}% of your monthly budget. Only ${formatCurrency(remainingBudget)} remaining.`
                  : isWarning 
                  ? `You've used ${usagePercentage.toFixed(1)}% of your monthly budget. ${formatCurrency(remainingBudget)} remaining.`
                  : `You've used ${usagePercentage.toFixed(1)}% of your monthly budget. ${formatCurrency(remainingBudget)} remaining.`
                }
              </TypographyComponent>
              {avgDailyCost > 0 && estimatedDaysUntilExhaustion > 0 && (
                <TypographyComponent variant="caption" sx={{ 
                  color: terminalTheme ? terminalColors.textSecondary : 'rgba(255,255,255,0.8)',
                  display: 'block',
                  fontStyle: 'italic'
                }}>
                  {estimatedDaysUntilExhaustion <= daysRemaining 
                    ? `At current spending rate, budget will be exhausted in ~${estimatedDaysUntilExhaustion} day${estimatedDaysUntilExhaustion !== 1 ? 's' : ''}.`
                    : `Current spending rate is sustainable for the remainder of the month.`
                  }
                </TypographyComponent>
              )}
            </Box>
          </Box>
        </Box>
      )}

      {/* Budget Progress Bar */}
      <Box sx={{ 
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
              {formatCurrency(currentUsage.total_cost)}
            </TypographyComponent>
            <TypographyComponent variant="caption" sx={{ 
              color: terminalTheme ? terminalColors.textSecondary : 'rgba(255,255,255,0.7)',
              display: 'block'
            }}>
              of {formatCurrency(limits.limits.monthly_cost)}
            </TypographyComponent>
          </Box>
        </Box>
        <AnimatedProgressBar
          value={Math.min(usagePercentage, 100)}
          height={10}
          color={terminalTheme
            ? (isCritical 
                ? terminalColors.error
                : isWarning 
                ? terminalColors.warning
                : isModerate
                ? terminalColors.secondary
                : terminalColors.success)
            : (isCritical 
                ? '#ef4444'
                : isWarning 
                ? '#f59e0b'
                : isModerate
                ? '#3b82f6'
                : '#4ade80')
          }
          showPercentage={false}
        />
        
        {/* Provider Cost Comparison Chart */}
        {currentUsage.provider_breakdown && Object.keys(currentUsage.provider_breakdown).length > 0 && (
          <ProviderCostComparison 
            providerBreakdown={currentUsage.provider_breakdown}
            terminalTheme={terminalTheme}
            terminalColors={terminalColors}
          />
        )}
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1.5 }}>
          <TypographyComponent variant="caption" sx={{ 
            color: terminalTheme 
              ? (isCritical ? terminalColors.error : isWarning ? terminalColors.warning : terminalColors.textSecondary)
              : (isCritical ? '#ef4444' : isWarning ? '#f59e0b' : 'rgba(255,255,255,0.7)'),
            fontWeight: (isCritical || isWarning) ? 600 : 400
          }}>
            {isCritical 
              ? '🚨 Critical: Approaching limit' 
              : isWarning 
              ? '⚠️ Warning: High usage'
              : isModerate
              ? 'ℹ️ Moderate usage'
              : '✅ Within budget'
            }
          </TypographyComponent>
          <TypographyComponent variant="caption" sx={{ 
            color: terminalTheme ? terminalColors.textSecondary : 'rgba(255,255,255,0.7)',
            fontWeight: 600
          }}>
            {usagePercentage.toFixed(1)}% used • {formatCurrency(remainingBudget)} remaining
          </TypographyComponent>
        </Box>
      </Box>
    </Box>
  );
};
