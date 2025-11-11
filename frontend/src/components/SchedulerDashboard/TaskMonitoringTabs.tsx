/**
 * Task Monitoring Tabs Component
 * Organizes OAuth Token Status, Website Analysis Status, and Platform Insights in tabs
 */

import React, { useState } from 'react';
import { Box, Tabs, Tab } from '@mui/material';
import { styled } from '@mui/material/styles';
import OAuthTokenStatus from './OAuthTokenStatus';
import WebsiteAnalysisStatus from './WebsiteAnalysisStatus';
import PlatformInsightsStatus from './PlatformInsightsStatus';
import { TerminalPaper, terminalColors } from './terminalTheme';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`task-monitoring-tabpanel-${index}`}
      aria-labelledby={`task-monitoring-tab-${index}`}
    >
      <Box sx={{ pt: 3, display: value === index ? 'block' : 'none' }}>{children}</Box>
    </div>
  );
};

// Terminal-themed button-like tab styling
const TerminalTab = styled(Tab)({
  minHeight: 48,
  padding: '8px 16px',
  textTransform: 'none',
  fontFamily: 'monospace',
  fontSize: '0.875rem',
  fontWeight: 400,
  color: terminalColors.textSecondary,
  backgroundColor: 'transparent',
  border: `1px solid ${terminalColors.border}`,
  borderBottom: 'none',
  borderRadius: '4px 4px 0 0',
  marginRight: '4px',
  transition: 'all 0.2s ease',
  '&:hover': {
    backgroundColor: terminalColors.backgroundHover,
    color: terminalColors.primary,
    borderColor: terminalColors.primary,
  },
  '&.Mui-selected': {
    color: terminalColors.primary,
    backgroundColor: terminalColors.background,
    borderColor: terminalColors.primary,
    fontWeight: 600,
  },
  '&:focus': {
    outline: `2px solid ${terminalColors.primary}`,
    outlineOffset: '-2px',
  },
});

const TaskMonitoringTabs: React.FC = () => {
  const [value, setValue] = useState(0);

  const handleChange = (_event: React.SyntheticEvent, newValue: number) => {
    setValue(newValue);
  };

  return (
    <TerminalPaper sx={{ p: 0 }}>
      <Box sx={{ borderBottom: 1, borderColor: terminalColors.border, px: 2, pt: 2 }}>
        <Tabs
          value={value}
          onChange={handleChange}
          aria-label="task monitoring tabs"
          sx={{
            minHeight: 48,
            '& .MuiTabs-indicator': {
              display: 'none', // Hide default indicator, we use border styling instead
            },
            '& .MuiTabs-flexContainer': {
              gap: 1,
            },
          }}
        >
          <TerminalTab 
            label="OAuth Token Status" 
            id="task-monitoring-tab-0" 
            aria-controls="task-monitoring-tabpanel-0"
          />
          <TerminalTab 
            label="Website Analysis" 
            id="task-monitoring-tab-1" 
            aria-controls="task-monitoring-tabpanel-1"
          />
          <TerminalTab 
            label="Platform Insights" 
            id="task-monitoring-tab-2" 
            aria-controls="task-monitoring-tabpanel-2"
          />
        </Tabs>
      </Box>
      <TabPanel value={value} index={0}>
        <Box sx={{ p: 2 }}>
          <OAuthTokenStatus compact={true} />
        </Box>
      </TabPanel>
      <TabPanel value={value} index={1}>
        <Box sx={{ p: 2 }}>
          <WebsiteAnalysisStatus compact={true} />
        </Box>
      </TabPanel>
      <TabPanel value={value} index={2}>
        <Box sx={{ p: 2 }}>
          <PlatformInsightsStatus compact={true} />
        </Box>
      </TabPanel>
    </TerminalPaper>
  );
};

export default TaskMonitoringTabs;

