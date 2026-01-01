import React from 'react';
import { Box, Stack, Typography, Chip } from '@mui/material';
import { enhanceVideoExamples } from '../constants';
import { OptimizedVideo } from '../../../ImageStudio/dashboard/utils/OptimizedVideo';

export const EnhanceVideoPreview: React.FC = () => {
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
            background: 'linear-gradient(135deg,#ef4444,#f97316)',
            color: '#fee2e2',
            p: 2,
            minHeight: 260,
            display: 'flex',
            flexDirection: 'column',
            gap: 1.2,
          }}
        >
          <Typography variant="overline" sx={{ letterSpacing: 2, color: '#fecaca' }}>
            Before: 480p @ 24fps
          </Typography>
          <Typography variant="body2">{enhanceVideoExamples.description}</Typography>
          <Stack direction="row" spacing={1} flexWrap="wrap">
            {['480p', '24fps', 'Standard'].map(label => (
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
            <OptimizedVideo
              src={enhanceVideoExamples.before}
              alt="Before enhancement"
              controls
              preload="metadata"
              muted
              loop
              playsInline
              sx={{ width: '100%', display: 'block' }}
            />
          </Box>
        </Box>
        <Box
          sx={{
            flex: 1,
            borderRadius: 3,
            border: '1px solid rgba(255,255,255,0.12)',
            background: 'linear-gradient(135deg,#10b981,#059669)',
            color: '#d1fae5',
            p: 2,
            minHeight: 260,
            display: 'flex',
            flexDirection: 'column',
            gap: 1.2,
          }}
        >
          <Typography variant="overline" sx={{ letterSpacing: 2, color: '#a7f3d0' }}>
            After: 1080p @ 60fps
          </Typography>
          <Typography variant="body2">Enhanced quality ready for professional use</Typography>
          <Stack direction="row" spacing={1} flexWrap="wrap">
            {['1080p', '60fps', 'Enhanced'].map(label => (
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
            <OptimizedVideo
              src={enhanceVideoExamples.after}
              alt="After enhancement"
              controls
              preload="metadata"
              muted
              loop
              playsInline
              sx={{ width: '100%', display: 'block' }}
            />
          </Box>
        </Box>
      </Stack>
      <Typography variant="caption" color="text.secondary" sx={{ mt: 1.5 }}>
        Transform low-resolution videos into professional-quality content. Perfect for upgrading social media content or preparing videos for YouTube and other platforms.
      </Typography>
    </Box>
  );
};
