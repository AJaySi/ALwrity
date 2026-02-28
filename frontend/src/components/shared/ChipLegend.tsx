import React from 'react';
import { Box, Chip, Tooltip } from '@mui/material';

export interface LegendItem {
  label: string;
  icon?: React.ReactNode;
  tooltip: string;
  sx?: any;
}

interface ChipLegendProps {
  items: LegendItem[];
  sx?: any;
}

const ChipLegend: React.FC<ChipLegendProps> = ({ items, sx }) => {
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1, ...sx }}>
      {items.map((item, idx) => (
        <Tooltip key={`${item.label}-${idx}`} title={item.tooltip}>
          <Chip icon={item.icon as any} label={item.label} size="small" sx={item.sx} />
        </Tooltip>
      ))}
    </Box>
  );
};

export default ChipLegend;
