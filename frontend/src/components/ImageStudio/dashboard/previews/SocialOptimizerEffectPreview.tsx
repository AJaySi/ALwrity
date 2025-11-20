import React from 'react';
import { Box, Stack, Typography, Chip } from '@mui/material';
import { transformAssets, platformPresets } from '../constants';

export const SocialOptimizerEffectPreview: React.FC = () => (
  <Box
    sx={{
      mt: 2,
      borderRadius: 3,
      border: '1px solid rgba(255,255,255,0.08)',
      background: 'rgba(15,23,42,0.5)',
      p: { xs: 2, md: 3 },
    }}
  >
    <Typography variant="overline" sx={{ letterSpacing: 2, color: '#fcd34d' }}>
      Platform Auto-Crop
    </Typography>
    <Typography variant="body2" color="text.secondary">
      Smart resize finds the focal point and generates safe-zone aware crops for every surface.
    </Typography>
    <Box
      sx={{
        mt: 2,
        borderRadius: 3,
        border: '1px solid rgba(255,255,255,0.1)',
        background: '#020617',
        p: 2,
        position: 'relative',
        minHeight: 280,
        overflow: 'hidden',
      }}
    >
      <Box
        component="img"
        src={transformAssets.storyboard}
        alt="Source creative"
        sx={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: 2, filter: 'brightness(0.8)' }}
      />
      {platformPresets.map(frame => (
        <Box
          key={frame.label}
          sx={{
            position: 'absolute',
            border: '2px solid rgba(248,250,252,0.8)',
            borderRadius: 2,
            boxShadow: '0 10px 20px rgba(2,6,23,0.45)',
            transition: 'transform 0.2s ease',
            cursor: 'pointer',
            '&:hover': { transform: 'scale(1.05)' },
            ...frame,
          }}
        >
          <Box
            sx={{
              position: 'absolute',
              top: -24,
              left: 0,
              background: 'rgba(15,23,42,0.85)',
              color: '#f8fafc',
              px: 1,
              py: 0.25,
              borderRadius: 999,
              fontSize: 11,
            }}
          >
            {frame.label}
          </Box>
        </Box>
      ))}
    </Box>
    <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ mt: 2 }}>
      {['Safe zones', 'Focal cropping', 'Batch export'].map(label => (
        <Chip key={label} size="small" label={label} sx={{ background: 'rgba(15,118,110,0.2)', color: '#5eead4', borderRadius: 999 }} />
      ))}
    </Stack>
  </Box>
);

