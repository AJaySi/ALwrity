import React from 'react';
import { Alert, LinearProgress, Stack, Typography } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/ErrorOutline';
import HourglassTopIcon from '@mui/icons-material/HourglassTop';

interface AsyncStatusBannerProps {
  state: 'idle' | 'running' | 'success' | 'error';
  message?: string;
}

export const AsyncStatusBanner: React.FC<AsyncStatusBannerProps> = ({
  state,
  message,
}) => {
  if (state === 'idle') return null;

  if (state === 'running') {
    return (
      <Stack spacing={1}>
        <LinearProgress
          sx={{
            height: 6,
            borderRadius: 999,
            '& .MuiLinearProgress-bar': {
              background: 'linear-gradient(90deg,#7c3aed,#2563eb)',
            },
          }}
        />
        <Stack direction="row" alignItems="center" spacing={1}>
          <HourglassTopIcon sx={{ color: '#93c5fd' }} fontSize="small" />
          <Typography variant="caption" color="text.secondary">
            {message || 'Processing request…'}
          </Typography>
        </Stack>
      </Stack>
    );
  }

  if (state === 'success') {
    return (
      <Alert
        icon={<CheckCircleIcon />}
        severity="success"
        sx={{ borderRadius: 2 }}
      >
        {message || 'Completed successfully.'}
      </Alert>
    );
  }

  return (
    <Alert
      icon={<ErrorIcon />}
      severity="error"
      sx={{ borderRadius: 2 }}
    >
      {message || 'Something went wrong.'}
    </Alert>
  );
};

