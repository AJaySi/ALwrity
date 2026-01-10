import React from 'react';
import { Grid, Box, Tooltip, Typography } from '@mui/material';
import { motion } from 'framer-motion';
import { CheckCircle } from 'lucide-react';
import { TerminalTypography } from '../../../SchedulerDashboard/terminalTheme';
import { terminalColors } from '../../../SchedulerDashboard/terminalTheme';
import { MetricCard } from './MetricCard';
import { formatCurrency, formatNumber } from '../utils/formatting';
import { DashboardData } from '../../../../types/billing';
import { SystemHealth } from '../../../../types/monitoring';

interface MainMetricsGridProps {
  currentUsage: DashboardData['current_usage'];
  systemHealth: SystemHealth | null;
  healthError: string | null;
  sparklineData: {
    cost: Array<{ date: string; value: number }>;
    calls: Array<{ date: string; value: number }>;
    tokens: Array<{ date: string; value: number }>;
  };
  terminalTheme?: boolean;
  TypographyComponent: typeof TerminalTypography | React.ComponentType<any>;
}

/**
 * MainMetricsGrid - Displays the 4 main metric cards (Cost, Calls, Tokens, System Health)
 */
export const MainMetricsGrid: React.FC<MainMetricsGridProps> = ({
  currentUsage,
  systemHealth,
  healthError,
  sparklineData,
  terminalTheme = false,
  TypographyComponent
}) => {
  return (
    <Grid container spacing={2} sx={{ mb: 2 }}>
      {/* Total Cost */}
      <Grid item xs={6} sm={3}>
        <MetricCard
          title="Total Cost"
          value={currentUsage.total_cost}
          formatValue={formatCurrency}
          decimals={4}
          tooltip={
            <Box>
              <TypographyComponent variant="subtitle2" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                Monthly API Usage Cost
              </TypographyComponent>
              <TypographyComponent variant="body2" sx={{ opacity: 0.9 }}>
                Total spending across all AI providers this month
              </TypographyComponent>
              <TypographyComponent variant="caption" sx={{ opacity: 0.7, mt: 1, display: 'block' }}>
                Includes: Gemini, OpenAI, Anthropic, Mistral
              </TypographyComponent>
            </Box>
          }
          sparklineData={sparklineData.cost}
          sparklineColor={terminalTheme ? terminalColors.success : '#4ade80'}
          sparklineFormatValue={formatCurrency}
          sparklineLabel="Cost"
          gradientColors={{
            start: 'rgba(74, 222, 128, 0.12)',
            end: 'rgba(34, 197, 94, 0.08)',
            border: 'rgba(74, 222, 128, 0.25)',
            hoverBorder: 'rgba(74, 222, 128, 0.4)',
            topBar: 'linear-gradient(90deg, #4ade80, #22c55e)'
          }}
          animationDelay={0}
          terminalTheme={terminalTheme}
          TypographyComponent={TypographyComponent}
        />
      </Grid>

      {/* API Calls */}
      <Grid item xs={6} sm={3}>
        <MetricCard
          title="API Calls"
          value={currentUsage.total_calls}
          formatValue={formatNumber}
          tooltip={
            <Box>
              <TypographyComponent variant="subtitle2" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                API Request Volume
              </TypographyComponent>
              <TypographyComponent variant="body2" sx={{ opacity: 0.9 }}>
                Total number of AI API requests made this month
              </TypographyComponent>
              <TypographyComponent variant="caption" sx={{ opacity: 0.7, mt: 1, display: 'block' }}>
                Each request generates content, analyzes data, or processes information
              </TypographyComponent>
            </Box>
          }
          sparklineData={sparklineData.calls}
          sparklineColor={terminalTheme ? terminalColors.secondary : '#3b82f6'}
          sparklineFormatValue={formatNumber}
          sparklineLabel="API Calls"
          gradientColors={{
            start: 'rgba(59, 130, 246, 0.12)',
            end: 'rgba(37, 99, 235, 0.08)',
            border: 'rgba(59, 130, 246, 0.25)',
            hoverBorder: 'rgba(59, 130, 246, 0.4)',
            topBar: 'linear-gradient(90deg, #3b82f6, #2563eb)'
          }}
          animationDelay={0.1}
          terminalTheme={terminalTheme}
          TypographyComponent={TypographyComponent}
        />
      </Grid>

      {/* Tokens */}
      <Grid item xs={6} sm={3}>
        <MetricCard
          title="Tokens"
          value={currentUsage.total_tokens / 1000}
          formatValue={(n) => `${n.toFixed(1)}k`}
          decimals={1}
          tooltip={
            <Box>
              <TypographyComponent variant="subtitle2" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                AI Processing Units
              </TypographyComponent>
              <TypographyComponent variant="body2" sx={{ opacity: 0.9 }}>
                Total tokens processed by AI models this month
              </TypographyComponent>
              <TypographyComponent variant="caption" sx={{ opacity: 0.7, mt: 1, display: 'block' }}>
                Tokens represent words, characters, and data processed by AI
              </TypographyComponent>
            </Box>
          }
          sparklineData={sparklineData.tokens}
          sparklineColor={terminalTheme ? terminalColors.warning : '#a855f7'}
          sparklineFormatValue={(n) => `${n.toFixed(1)}k`}
          sparklineLabel="Tokens (k)"
          gradientColors={{
            start: 'rgba(168, 85, 247, 0.12)',
            end: 'rgba(147, 51, 234, 0.08)',
            border: 'rgba(168, 85, 247, 0.25)',
            hoverBorder: 'rgba(168, 85, 247, 0.4)',
            topBar: 'linear-gradient(90deg, #a855f7, #9333ea)'
          }}
          animationDelay={0.2}
          terminalTheme={terminalTheme}
          TypographyComponent={TypographyComponent}
        />
      </Grid>

      {/* System Health */}
      <Grid item xs={6} sm={3}>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.4, ease: "easeOut" }}
        >
          <Tooltip 
            title={
              <Box>
                <TypographyComponent variant="subtitle2" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                  System Performance Status
                </TypographyComponent>
                <TypographyComponent variant="body2" sx={{ opacity: 0.9 }}>
                  Real-time monitoring of API services and system performance
                </TypographyComponent>
                {healthError && (
                  <TypographyComponent variant="caption" sx={{ color: '#ff9800', mt: 1, display: 'block', fontWeight: 'bold' }}>
                    ⚠️ Showing last known values - Unable to fetch latest data
                  </TypographyComponent>
                )}
                <TypographyComponent variant="caption" sx={{ opacity: 0.7, mt: 1, display: 'block' }}>
                  {systemHealth?.status === 'healthy' 
                    ? 'All systems operational and responding normally'
                    : systemHealth?.status === 'warning'
                    ? 'Some services may be experiencing issues'
                    : systemHealth?.status === 'critical'
                    ? 'Critical issues detected'
                    : 'Status unknown'
                  }
                </TypographyComponent>
                {systemHealth?.timestamp && (
                  <TypographyComponent variant="caption" sx={{ opacity: 0.6, mt: 0.5, display: 'block', fontSize: '0.65rem' }}>
                    Last updated: {new Date(systemHealth.timestamp).toLocaleTimeString()}
                  </TypographyComponent>
                )}
              </Box>
            }
            arrow
            placement="top"
          >
            <Box sx={{ 
              textAlign: 'center', 
              p: 2.5, 
              ...(terminalTheme ? {
                backgroundColor: terminalColors.backgroundLight,
                borderRadius: 3,
                border: `1px solid ${systemHealth?.status === 'healthy' ? terminalColors.success : terminalColors.error}`,
                position: 'relative',
                overflow: 'hidden',
                cursor: 'help',
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-2px)',
                  boxShadow: `0 0 15px ${systemHealth?.status === 'healthy' ? terminalColors.success : terminalColors.error}40`,
                  borderColor: systemHealth?.status === 'healthy' ? terminalColors.secondary : terminalColors.error
                },
                '&::before': {
                  content: '""',
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  height: '3px',
                  background: systemHealth?.status === 'healthy' ? terminalColors.success : terminalColors.error,
                  zIndex: 1
                }
              } : {
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
              })
            }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5, mb: 0.5 }}>
                <CheckCircle size={18} color={terminalTheme 
                  ? (systemHealth?.status === 'healthy' ? terminalColors.success : terminalColors.error)
                  : (systemHealth?.status === 'healthy' ? '#4ade80' : '#ff6b6b')
                } />
                <TypographyComponent variant="body1" sx={{ 
                  color: terminalTheme 
                    ? (systemHealth?.status === 'healthy' ? terminalColors.success : terminalColors.error)
                    : (systemHealth?.status === 'healthy' ? '#4ade80' : '#ff6b6b'),
                  fontWeight: 700,
                  textTransform: 'capitalize',
                  textShadow: terminalTheme ? 'none' : '0 2px 4px rgba(0,0,0,0.3)'
                }}>
                  {systemHealth?.status || 'Unknown'}
                </TypographyComponent>
              </Box>
              <TypographyComponent variant="body2" sx={{ 
                color: terminalTheme ? terminalColors.textSecondary : 'rgba(255,255,255,0.9)',
                fontWeight: 500,
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                fontSize: '0.75rem'
              }}>
                System Health
              </TypographyComponent>
            </Box>
          </Tooltip>
        </motion.div>
      </Grid>
    </Grid>
  );
};
