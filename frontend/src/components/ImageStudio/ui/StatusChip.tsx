import React from 'react';
import { Chip, type ChipProps } from '@mui/material';

export interface StatusChipProps extends Omit<ChipProps, 'color'> {
  tone?: 'success' | 'warning' | 'info' | 'neutral';
}

const toneStyles: Record<
  NonNullable<StatusChipProps['tone']>,
  { bg: string; color: string }
> = {
  success: { bg: 'rgba(16,185,129,0.15)', color: '#10b981' },
  warning: { bg: 'rgba(245,158,11,0.15)', color: '#f59e0b' },
  info: { bg: 'rgba(59,130,246,0.15)', color: '#3b82f6' },
  neutral: { bg: 'rgba(148,163,184,0.2)', color: '#cbd5f5' },
};

export const StatusChip: React.FC<StatusChipProps> = ({
  tone = 'neutral',
  sx,
  ...rest
}) => (
  <Chip
    size="small"
    sx={{
      backgroundColor: toneStyles[tone].bg,
      color: toneStyles[tone].color,
      fontWeight: 700,
      ...sx,
    }}
    {...rest}
  />
);

