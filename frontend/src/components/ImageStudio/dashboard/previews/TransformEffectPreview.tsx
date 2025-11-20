import React from 'react';
import { Box, Stack, Typography, Chip, Button } from '@mui/material';
import { transformAssets } from '../constants';

export const TransformEffectPreview: React.FC = () => {
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
            background: 'linear-gradient(135deg,#0ea5e9,#6366f1)',
            color: '#e0f2fe',
            p: 2,
            minHeight: 260,
            display: 'flex',
            flexDirection: 'column',
            gap: 1.2,
          }}
        >
          <Typography variant="overline" sx={{ letterSpacing: 2, color: '#cffafe' }}>
            Storyboard Prompt
          </Typography>
          <Typography variant="body2">{transformAssets.script}</Typography>
          <Stack direction="row" spacing={1} flexWrap="wrap">
            {['Image-to-video', 'WAN 2.5', '10s duration'].map(label => (
              <Chip
                key={label}
                size="small"
                label={label}
                sx={{ background: 'rgba(255,255,255,0.2)', color: '#0f172a', borderRadius: 999 }}
              />
            ))}
          </Stack>
          <Box
            sx={{
              mt: 'auto',
              borderRadius: 2,
              overflow: 'hidden',
              border: '1px solid rgba(255,255,255,0.25)',
              boxShadow: '0 20px 45px rgba(2,6,23,0.45)',
            }}
          >
            <Box component="img" src={transformAssets.storyboard} alt="Storyboard still" sx={{ width: '100%', display: 'block' }} />
          </Box>
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
            <Typography variant="overline" sx={{ letterSpacing: 2, color: '#38bdf8' }}>
              Render Preview
            </Typography>
            <Chip
              label="1080p"
              size="small"
              sx={{ background: 'rgba(56,189,248,0.15)', color: '#38bdf8', borderRadius: 999 }}
            />
            <Button size="small" onClick={() => setVideoKey(prev => prev + 1)} sx={{ ml: 'auto', color: '#38bdf8', textTransform: 'none' }}>
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
            <video key={videoKey} controls poster={transformAssets.storyboard} style={{ width: '100%', display: 'block' }} src={transformAssets.video} />
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
              Scene 1 · Cloud Kitchen
            </Box>
          </Box>
        </Box>
      </Stack>
      <Typography variant="caption" color="text.secondary" sx={{ mt: 1.5 }}>
        Convert hero images into narrated clips with motion presets, subtitles, and audio uploads.
      </Typography>
    </Box>
  );
};

