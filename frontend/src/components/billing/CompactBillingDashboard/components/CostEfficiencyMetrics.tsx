import React from 'react';
import { Grid, Box, Tooltip } from '@mui/material';
import { TerminalTypography } from '../../../SchedulerDashboard/terminalTheme';
import { terminalColors } from '../../../SchedulerDashboard/terminalTheme';
import { formatCurrency } from '../utils/formatting';
import { DashboardData } from '../../../../types/billing';

interface CostEfficiencyMetricsProps {
  currentUsage: DashboardData['current_usage'];
  terminalTheme?: boolean;
  TypographyComponent: typeof TerminalTypography | React.ComponentType<any>;
}

/**
 * CostEfficiencyMetrics - Displays cost efficiency metrics (Avg Cost/Call, Cost/1K Tokens, Efficiency Score)
 */
export const CostEfficiencyMetrics: React.FC<CostEfficiencyMetricsProps> = ({
  currentUsage,
  terminalTheme = false,
  TypographyComponent
}) => {
  if (currentUsage.total_calls === 0) return null;

  const avgCostPerCall = currentUsage.total_cost / currentUsage.total_calls;
  const costPer1KTokens = currentUsage.total_tokens > 0 
    ? (currentUsage.total_cost / currentUsage.total_tokens) * 1000 
    : 0;

  const getEfficiencyScore = () => {
    if (avgCostPerCall < 0.01) return '⭐ Excellent';
    if (avgCostPerCall < 0.05) return '✅ Good';
    if (avgCostPerCall < 0.10) return '⚡ Fair';
    return '⚠️ High';
  };

  return (
    <Grid container spacing={2} sx={{ mb: 2 }}>
      {/* Average Cost Per Call */}
      <Grid item xs={6} sm={4}>
        <Tooltip 
          title={
            <Box>
              <TypographyComponent variant="subtitle2" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                Average Cost Per API Call
              </TypographyComponent>
              <TypographyComponent variant="body2" sx={{ opacity: 0.9 }}>
                Calculated as total cost divided by total API calls this month
              </TypographyComponent>
              <TypographyComponent variant="caption" sx={{ opacity: 0.7, mt: 1, display: 'block' }}>
                Lower values indicate more cost-efficient usage
              </TypographyComponent>
            </Box>
          }
          arrow
          placement="top"
        >
          <Box sx={{ 
            textAlign: 'center', 
            p: 2, 
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
                boxShadow: `0 0 10px ${terminalColors.border}30`,
                borderColor: terminalColors.secondary
              }
            } : {
              background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(79, 70, 229, 0.08) 100%)',
              borderRadius: 3,
              border: '1px solid rgba(99, 102, 241, 0.25)',
              position: 'relative',
              overflow: 'hidden',
              cursor: 'help',
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'translateY(-2px)',
                boxShadow: '0 6px 20px rgba(99, 102, 241, 0.2)',
                border: '1px solid rgba(99, 102, 241, 0.4)'
              }
            })
          }}>
            <TypographyComponent variant="h6" sx={{ 
              fontWeight: 700, 
              color: terminalTheme ? terminalColors.text : '#ffffff', 
              textShadow: terminalTheme ? 'none' : '0 2px 4px rgba(0,0,0,0.3)',
              mb: 0.5
            }}>
              {formatCurrency(avgCostPerCall)}
            </TypographyComponent>
            <TypographyComponent variant="body2" sx={{ 
              color: terminalTheme ? terminalColors.textSecondary : 'rgba(255,255,255,0.9)',
              fontWeight: 500,
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              fontSize: '0.7rem'
            }}>
              Avg Cost/Call
            </TypographyComponent>
          </Box>
        </Tooltip>
      </Grid>

      {/* Cost Per 1K Tokens */}
      {currentUsage.total_tokens > 0 && (
        <Grid item xs={6} sm={4}>
          <Tooltip 
            title={
              <Box>
                <TypographyComponent variant="subtitle2" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                  Cost Per 1,000 Tokens
                </TypographyComponent>
                <TypographyComponent variant="body2" sx={{ opacity: 0.9 }}>
                  Average cost for processing 1,000 tokens (input + output)
                </TypographyComponent>
                <TypographyComponent variant="caption" sx={{ opacity: 0.7, mt: 1, display: 'block' }}>
                  Useful for estimating costs of future operations
                </TypographyComponent>
              </Box>
            }
            arrow
            placement="top"
          >
            <Box sx={{ 
              textAlign: 'center', 
              p: 2, 
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
                  boxShadow: `0 0 10px ${terminalColors.border}30`,
                  borderColor: terminalColors.secondary
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
                  boxShadow: '0 6px 20px rgba(168, 85, 247, 0.2)',
                  border: '1px solid rgba(168, 85, 247, 0.4)'
                }
              })
            }}>
              <TypographyComponent variant="h6" sx={{ 
                fontWeight: 700, 
                color: terminalTheme ? terminalColors.text : '#ffffff', 
                textShadow: terminalTheme ? 'none' : '0 2px 4px rgba(0,0,0,0.3)',
                mb: 0.5
              }}>
                {formatCurrency(costPer1KTokens)}
              </TypographyComponent>
              <TypographyComponent variant="body2" sx={{ 
                color: terminalTheme ? terminalColors.textSecondary : 'rgba(255,255,255,0.9)',
                fontWeight: 500,
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                fontSize: '0.7rem'
              }}>
                Cost/1K Tokens
              </TypographyComponent>
            </Box>
          </Tooltip>
        </Grid>
      )}

      {/* Cost Efficiency Score */}
      <Grid item xs={6} sm={4}>
        <Tooltip 
          title={
            <Box>
              <TypographyComponent variant="subtitle2" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                Cost Efficiency Indicator
              </TypographyComponent>
              <TypographyComponent variant="body2" sx={{ opacity: 0.9 }}>
                Based on average cost per call and token usage
              </TypographyComponent>
              <TypographyComponent variant="caption" sx={{ opacity: 0.7, mt: 1, display: 'block' }}>
                Lower cost per call = Higher efficiency
              </TypographyComponent>
            </Box>
          }
          arrow
          placement="top"
        >
          <Box sx={{ 
            textAlign: 'center', 
            p: 2, 
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
                boxShadow: `0 0 10px ${terminalColors.border}30`,
                borderColor: terminalColors.secondary
              }
            } : {
              background: 'linear-gradient(135deg, rgba(34, 197, 94, 0.12) 0%, rgba(22, 163, 74, 0.08) 100%)',
              borderRadius: 3,
              border: '1px solid rgba(34, 197, 94, 0.25)',
              position: 'relative',
              overflow: 'hidden',
              cursor: 'help',
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'translateY(-2px)',
                boxShadow: '0 6px 20px rgba(34, 197, 94, 0.2)',
                border: '1px solid rgba(34, 197, 94, 0.4)'
              }
            })
          }}>
            <TypographyComponent variant="h6" sx={{ 
              fontWeight: 700, 
              color: terminalTheme ? terminalColors.text : '#ffffff', 
              textShadow: terminalTheme ? 'none' : '0 2px 4px rgba(0,0,0,0.3)',
              mb: 0.5
            }}>
              {getEfficiencyScore()}
            </TypographyComponent>
            <TypographyComponent variant="body2" sx={{ 
              color: terminalTheme ? terminalColors.textSecondary : 'rgba(255,255,255,0.9)',
              fontWeight: 500,
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              fontSize: '0.7rem'
            }}>
              Efficiency
            </TypographyComponent>
          </Box>
        </Tooltip>
      </Grid>
    </Grid>
  );
};
