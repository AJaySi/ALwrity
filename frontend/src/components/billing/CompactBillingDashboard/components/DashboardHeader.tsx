import React from 'react';
import { Box, Tooltip, IconButton } from '@mui/material';
import { RefreshCw } from 'lucide-react';
import { TerminalTypography } from '../../../SchedulerDashboard/terminalTheme';
import { terminalColors } from '../../../SchedulerDashboard/terminalTheme';

interface DashboardHeaderProps {
  lastRefreshTime: Date | null;
  onRefresh: () => void;
  loading: boolean;
  terminalTheme?: boolean;
  TypographyComponent: typeof TerminalTypography | React.ComponentType<any>;
}

/**
 * DashboardHeader - Displays last refresh time and refresh button
 */
export const DashboardHeader: React.FC<DashboardHeaderProps> = ({
  lastRefreshTime,
  onRefresh,
  loading,
  terminalTheme = false,
  TypographyComponent
}) => {
  return (
    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
      {lastRefreshTime && (
        <Tooltip title={`Data last refreshed at ${lastRefreshTime.toLocaleTimeString()}`}>
          <TypographyComponent 
            variant="caption" 
            sx={{ 
              color: terminalTheme ? terminalColors.textSecondary : 'rgba(255,255,255,0.6)',
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
          onClick={onRefresh}
          disabled={loading}
          sx={{ 
            color: terminalTheme ? terminalColors.textSecondary : 'rgba(255,255,255,0.7)',
            '&:hover': {
              color: terminalTheme ? terminalColors.text : '#ffffff',
              backgroundColor: terminalTheme ? terminalColors.backgroundLight : 'rgba(255,255,255,0.1)'
            }
          }}
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
        </IconButton>
      </Tooltip>
    </Box>
  );
};
