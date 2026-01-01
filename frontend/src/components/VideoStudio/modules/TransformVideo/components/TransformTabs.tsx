import React from 'react';
import { Tabs, Tab, Box } from '@mui/material';
import type { TransformType } from '../hooks/useTransformVideo';

interface TransformTabsProps {
  transformType: TransformType;
  onTransformTypeChange: (type: TransformType) => void;
}

export const TransformTabs: React.FC<TransformTabsProps> = ({
  transformType,
  onTransformTypeChange,
}) => {
  const handleChange = (_event: React.SyntheticEvent, newValue: TransformType) => {
    onTransformTypeChange(newValue);
  };

  return (
    <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
      <Tabs
        value={transformType}
        onChange={handleChange}
        variant="scrollable"
        scrollButtons="auto"
        sx={{
          '& .MuiTab-root': {
            textTransform: 'none',
            fontWeight: 600,
            minWidth: 120,
          },
        }}
      >
        <Tab label="Format" value="format" />
        <Tab label="Aspect Ratio" value="aspect" />
        <Tab label="Speed" value="speed" />
        <Tab label="Resolution" value="resolution" />
        <Tab label="Compress" value="compress" />
      </Tabs>
    </Box>
  );
};
