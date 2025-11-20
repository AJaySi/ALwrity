import React from 'react';
import { Paper, Stack, Typography, Divider } from '@mui/material';
import { ModuleConfig } from './types';

export const ModuleInfoCard: React.FC<{ module: ModuleConfig }> = ({ module }) => (
  <Paper
    variant="outlined"
    sx={{
      mt: 1.5,
      borderRadius: 3,
      borderColor: 'rgba(255,255,255,0.12)',
      backgroundColor: 'rgba(15,23,42,0.65)',
      p: 2,
    }}
  >
    <Stack spacing={1}>
      <Typography variant="caption" sx={{ color: '#a5b4fc', letterSpacing: 1 }}>
        Pricing & Workflow
      </Typography>
      <Typography variant="body2" fontWeight={600}>
        {module.pricing.estimate}
      </Typography>
      <Typography variant="caption" color="text.secondary">
        {module.pricing.notes}
      </Typography>
      <Divider sx={{ borderColor: 'rgba(255,255,255,0.08)' }} />
      <Typography variant="subtitle2" fontWeight={700}>
        {module.example.title}
      </Typography>
      <Stack component="ul" spacing={0.5} sx={{ pl: 2, m: 0 }}>
        {module.example.steps.map(step => (
          <Typography key={step} component="li" variant="body2" color="text.secondary">
            {step}
          </Typography>
        ))}
      </Stack>
      <Typography variant="caption" color="text.secondary">
        ETA: {module.example.eta}
      </Typography>
    </Stack>
  </Paper>
);

