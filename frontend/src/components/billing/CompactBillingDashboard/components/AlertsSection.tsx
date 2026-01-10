import React from 'react';
import { Box, Tooltip } from '@mui/material';
import { AlertTriangle } from 'lucide-react';
import { Chip } from '@mui/material';
import { TerminalTypography, TerminalChip, TerminalChipError } from '../../../SchedulerDashboard/terminalTheme';
import { terminalColors } from '../../../SchedulerDashboard/terminalTheme';
import { DashboardData } from '../../../../types/billing';

interface AlertsSectionProps {
  alerts: DashboardData['alerts'];
  terminalTheme?: boolean;
  TypographyComponent: typeof TerminalTypography | React.ComponentType<any>;
  ChipComponent: typeof TerminalChip | typeof Chip;
}

/**
 * AlertsSection - Displays system alerts
 */
export const AlertsSection: React.FC<AlertsSectionProps> = ({
  alerts,
  terminalTheme = false,
  TypographyComponent,
  ChipComponent
}) => {
  if (alerts.length === 0) return null;

  return (
    <Box sx={{ 
      mb: 3, 
      p: 2.5, 
      ...(terminalTheme ? {
        backgroundColor: terminalColors.backgroundLight,
        borderRadius: 3,
        border: `1px solid ${terminalColors.error}`,
        position: 'relative',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '3px',
          background: terminalColors.error,
          borderRadius: '3px 3px 0 0'
        }
      } : {
        background: 'linear-gradient(135deg, rgba(255, 107, 107, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%)',
        borderRadius: 3,
        border: '1px solid rgba(255, 107, 107, 0.2)',
        position: 'relative',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '3px',
          background: 'linear-gradient(90deg, #ff6b6b, #ef4444)',
          borderRadius: '3px 3px 0 0'
        }
      })
    }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <AlertTriangle size={18} color={terminalTheme ? terminalColors.error : "#ff6b6b"} />
        <TypographyComponent variant="subtitle2" sx={{ 
          fontWeight: 700, 
          color: terminalTheme ? terminalColors.error : '#ff6b6b',
          textShadow: terminalTheme ? 'none' : '0 1px 2px rgba(0,0,0,0.3)'
        }}>
          System Alerts ({alerts.length})
        </TypographyComponent>
      </Box>
      <TypographyComponent variant="caption" sx={{ 
        color: terminalTheme ? terminalColors.textSecondary : 'rgba(255,255,255,0.8)',
        display: 'block',
        mb: 2
      }}>
        Important notifications requiring your attention
      </TypographyComponent>
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
        {alerts.slice(0, 3).map((alert) => (
          <Tooltip 
            key={alert.id} 
            title={
              <Box>
                <TypographyComponent variant="subtitle2" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                  {alert.title}
                </TypographyComponent>
                <TypographyComponent variant="body2" sx={{ opacity: 0.9 }}>
                  {alert.message}
                </TypographyComponent>
              </Box>
            }
            arrow
            placement="top"
          >
            {terminalTheme ? (
              <TerminalChipError
                label={alert.title}
                size="small"
                icon={<AlertTriangle size={14} />}
                sx={{
                  fontWeight: 500,
                  '&:hover': {
                    transform: 'translateY(-1px)'
                  },
                  transition: 'all 0.2s ease'
                }}
              />
            ) : (
              <Chip
                label={alert.title}
                size="small"
                icon={<AlertTriangle size={14} />}
                sx={{
                  backgroundColor: 'rgba(255, 107, 107, 0.2)',
                  color: '#ff6b6b',
                  border: '1px solid rgba(255, 107, 107, 0.3)',
                  fontWeight: 500,
                  '&:hover': {
                    backgroundColor: 'rgba(255, 107, 107, 0.3)',
                    transform: 'translateY(-1px)'
                  },
                  transition: 'all 0.2s ease'
                }}
              />
            )}
          </Tooltip>
        ))}
        {alerts.length > 3 && (
          terminalTheme ? (
            <TerminalChip
              label={`+${alerts.length - 3} more`}
              size="small"
              sx={{ fontWeight: 500 }}
            />
          ) : (
            <Chip
              label={`+${alerts.length - 3} more`}
              size="small"
              sx={{
                backgroundColor: 'rgba(255,255,255,0.1)',
                color: 'rgba(255,255,255,0.8)',
                border: '1px solid rgba(255,255,255,0.2)',
                fontWeight: 500
              }}
            />
          )
        )}
      </Box>
    </Box>
  );
};
