import React from 'react';
import { Stack, Typography, Chip, type StackProps } from '@mui/material';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';

interface SectionHeaderProps extends StackProps {
  title: string;
  subtitle?: string;
  status?: 'live' | 'beta' | 'coming';
}

const statusStyles: Record<
  NonNullable<SectionHeaderProps['status']>,
  { label: string; color: string; bg: string }
> = {
  live: { label: 'Live', color: '#10b981', bg: 'rgba(16,185,129,0.15)' },
  beta: { label: 'Beta', color: '#f59e0b', bg: 'rgba(245,158,11,0.15)' },
  coming: { label: 'Coming Soon', color: '#94a3b8', bg: 'rgba(148,163,184,0.15)' },
};

export const SectionHeader: React.FC<SectionHeaderProps> = ({
  title,
  subtitle,
  status,
  sx,
  ...rest
}) => (
  <Stack spacing={0.5} sx={{ color: '#f8fafc', ...sx }} {...rest}>
    <Stack direction="row" spacing={1} alignItems="center">
      <AutoAwesomeIcon sx={{ color: '#c4b5fd' }} fontSize="small" />
      <Typography variant="h5" fontWeight={800}>
        {title}
      </Typography>
      {status && (
        <Chip
          size="small"
          label={statusStyles[status].label}
          sx={{
            backgroundColor: statusStyles[status].bg,
            color: statusStyles[status].color,
            fontWeight: 700,
          }}
        />
      )}
    </Stack>
    {subtitle && (
      <Typography variant="body2" color="text.secondary">
        {subtitle}
      </Typography>
    )}
  </Stack>
);

