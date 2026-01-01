import React from 'react';
import { Box, Paper, Stack, Typography, Chip } from '@mui/material';
import { VideoStudioLayout } from './VideoStudioLayout';

interface ModulePlaceholderProps {
  title: string;
  subtitle: string;
  status?: 'live' | 'beta' | 'coming soon';
  description?: string;
  bullets?: string[];
}

const statusColor: Record<string, { bg: string; color: string }> = {
  live: { bg: 'rgba(16,185,129,0.18)', color: '#10b981' },
  beta: { bg: 'rgba(59,130,246,0.18)', color: '#3b82f6' },
  'coming soon': { bg: 'rgba(249,115,22,0.18)', color: '#f97316' },
};

export const ModulePlaceholder: React.FC<ModulePlaceholderProps> = ({
  title,
  subtitle,
  status = 'coming soon',
  description,
  bullets = [],
}) => {
  const style = statusColor[status] || statusColor['coming soon'];

  return (
    <VideoStudioLayout headerProps={{ title, subtitle }}>
      <Paper
        elevation={0}
        sx={{
          maxWidth: 1100,
          mx: 'auto',
          borderRadius: 4,
          border: '1px solid rgba(255,255,255,0.08)',
          background: 'rgba(15,23,42,0.78)',
          p: { xs: 3, md: 4 },
          backdropFilter: 'blur(18px)',
        }}
      >
        <Stack spacing={2}>
          <Chip
            label={status.toUpperCase()}
            sx={{
              alignSelf: 'flex-start',
              backgroundColor: style.bg,
              color: style.color,
              fontWeight: 700,
            }}
          />
          {description && (
            <Typography variant="body1" color="text.secondary">
              {description}
            </Typography>
          )}
          {bullets.length > 0 && (
            <Stack spacing={1}>
              {bullets.map(item => (
                <Box
                  key={item}
                  sx={{
                    border: '1px solid rgba(255,255,255,0.08)',
                    borderRadius: 2,
                    px: 2,
                    py: 1.25,
                    background: 'rgba(255,255,255,0.02)',
                  }}
                >
                  <Typography variant="body2" color="text.secondary">
                    {item}
                  </Typography>
                </Box>
              ))}
            </Stack>
          )}
          <Typography variant="body2" color="text.secondary">
            We’ll surface cost estimates, provider choices, and templates here as the module goes live.
          </Typography>
        </Stack>
      </Paper>
    </VideoStudioLayout>
  );
};

export default ModulePlaceholder;
