import React from 'react';
import { Box, Stack, Typography, Chip, Button } from '@mui/material';
import { controlAssets } from '../constants';

export const ControlEffectPreview: React.FC = () => {
  const [videoKey, setVideoKey] = React.useState(0);

  return (
    <Box
      sx={{
        mt: 2,
        borderRadius: 3,
        border: '1px solid rgba(255,255,255,0.08)',
        background: 'rgba(15,23,42,0.5)',
        p: { xs: 2, md: 3 },
      }}
    >
      <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems="stretch">
        <Box
          sx={{
            flex: 1,
            borderRadius: 3,
            border: '1px solid rgba(255,255,255,0.12)',
            background: 'linear-gradient(135deg,#8b5cf6,#a855f7)',
            color: '#f3e8ff',
            p: 2,
            display: 'flex',
            flexDirection: 'column',
            gap: 1.5,
          }}
        >
          <Typography variant="overline" sx={{ letterSpacing: 2, color: '#e9d5ff' }}>
            Control Input
          </Typography>
          <Box
            component="img"
            src={controlAssets.inputImage}
            alt="Control reference"
            sx={{ width: '100%', borderRadius: 2, border: '2px solid rgba(255,255,255,0.2)', boxShadow: '0 10px 25px rgba(139,92,246,0.3)' }}
          />
          <Stack spacing={1}>
            <Typography variant="caption" sx={{ color: '#e9d5ff', fontWeight: 600 }}>
              Prompt
            </Typography>
            <Typography variant="body2" sx={{ fontSize: '0.875rem', lineHeight: 1.5 }}>
              {controlAssets.prompt}
            </Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap">
              <Chip
                size="small"
                label={`Seed ${controlAssets.seed}`}
                sx={{ background: 'rgba(255,255,255,0.2)', color: '#0f172a', borderRadius: 999 }}
              />
              <Chip
                size="small"
                label={controlAssets.resolution}
                sx={{ background: 'rgba(255,255,255,0.2)', color: '#0f172a', borderRadius: 999 }}
              />
              <Chip
                size="small"
                label={`${controlAssets.duration}s`}
                sx={{ background: 'rgba(255,255,255,0.2)', color: '#0f172a', borderRadius: 999 }}
              />
            </Stack>
          </Stack>
        </Box>
        <Box
          sx={{
            flex: 1.5,
            borderRadius: 3,
            border: '1px solid rgba(255,255,255,0.12)',
            background: '#020617',
            p: { xs: 1, md: 2 },
          }}
        >
          <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
            <Typography variant="overline" sx={{ letterSpacing: 2, color: '#a78bfa' }}>
              Generated Output
            </Typography>
            <Chip
              label="WAN 2.5"
              size="small"
              sx={{ background: 'rgba(167,139,250,0.15)', color: '#a78bfa', borderRadius: 999 }}
            />
            <Button size="small" onClick={() => setVideoKey(prev => prev + 1)} sx={{ ml: 'auto', color: '#a78bfa', textTransform: 'none' }}>
              Reset preview
            </Button>
          </Stack>
          <Box
            sx={{
              borderRadius: 2,
              overflow: 'hidden',
              border: '1px solid rgba(255,255,255,0.08)',
              position: 'relative',
            }}
          >
            <video key={videoKey} controls poster={controlAssets.inputImage} style={{ width: '100%', display: 'block' }} src={controlAssets.outputVideo} />
            <Box
              sx={{
                position: 'absolute',
                top: 12,
                left: 12,
                background: 'rgba(15,23,42,0.7)',
                borderRadius: 999,
                px: 1.5,
                py: 0.5,
                color: '#f8fafc',
                fontSize: 12,
              }}
            >
              Voiceover · {controlAssets.duration}s
            </Box>
          </Box>
        </Box>
      </Stack>
      <Typography variant="caption" color="text.secondary" sx={{ mt: 1.5 }}>
        Alibaba WAN 2.5 converts text or images into videos (480p/720p/1080p) with synced audio, faster and more affordable than Google Veo3.
      </Typography>
    </Box>
  );
};

