import React from 'react';
import { Box, Stack, Typography, Chip } from '@mui/material';
import { OptimizedVideo } from '../../../ImageStudio/dashboard/utils/OptimizedVideo';

export const VideoTranslatePreview: React.FC = () => {
  return (
    <Box
      sx={{
        mt: 2,
        borderRadius: 3,
        border: '3px solid',
        borderImage: 'linear-gradient(135deg, rgba(14,165,233,0.8), rgba(99,102,241,0.8), rgba(139,92,246,0.8)) 1',
        overflow: 'hidden',
        height: { xs: 260, md: 300 },
        display: 'flex',
        background: '#0f172a',
      }}
    >
      <Box
        sx={{
          flex: '0 0 auto',
          width: '70%',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <OptimizedVideo
          src="/videos/text-video-voiceover.mp4"
          alt="Video translation example"
          controls
          muted
          loop
          playsInline
          preload="metadata"
          sx={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
          }}
        />
        <Box
          sx={{
            position: 'absolute',
            top: 16,
            left: 16,
            background: 'rgba(14,165,233,0.9)',
            color: '#fff',
            px: 2,
            py: 1,
            borderRadius: 2,
            fontWeight: 700,
            fontSize: '0.85rem',
          }}
        >
          Original: English
        </Box>
      </Box>
      <Box
        sx={{
          flex: '0 0 auto',
          width: '30%',
          background: 'rgba(248,250,252,0.95)',
          color: '#0f172a',
          p: 3,
          display: 'flex',
          flexDirection: 'column',
          gap: 1.5,
          boxShadow: '-12px 0 24px rgba(15,23,42,0.25)',
        }}
      >
        <Typography variant="overline" sx={{ letterSpacing: 1.5, color: '#0ea5e9', fontWeight: 700 }}>
          Translate to 70+ Languages
        </Typography>
        <Typography variant="subtitle2" fontWeight={700}>
          AI Video Translation
        </Typography>
        <Typography variant="body2" sx={{ fontSize: '0.85rem' }}>
          Preserves lip-sync and natural voice. Perfect for global content, localization, and reaching international audiences.
        </Typography>
        <Stack direction="row" spacing={1} flexWrap="wrap">
          <Chip
            size="small"
            label="70+ Languages"
            sx={{ background: '#cffafe', color: '#0f766e', borderRadius: 999, fontWeight: 600 }}
          />
          <Chip
            size="small"
            label="Lip-sync"
            sx={{ background: '#ede9fe', color: '#4c1d95', borderRadius: 999, fontWeight: 600 }}
          />
          <Chip
            size="small"
            label="$0.0375/s"
            sx={{ background: '#dcfce7', color: '#166534', borderRadius: 999, fontWeight: 600 }}
          />
        </Stack>
        <Typography variant="caption" sx={{ color: '#64748b', mt: 0.5 }}>
          Best for: Global content creators, localization, international marketing
        </Typography>
      </Box>
    </Box>
  );
};
