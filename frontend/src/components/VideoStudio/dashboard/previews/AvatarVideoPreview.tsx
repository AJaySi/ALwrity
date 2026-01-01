import React from 'react';
import { Box, Stack, Typography, Chip } from '@mui/material';
import { avatarExamples } from '../constants';
import { OptimizedImage } from '../../../ImageStudio/dashboard/utils/OptimizedImage';
import { OptimizedVideo } from '../../../ImageStudio/dashboard/utils/OptimizedVideo';

export const AvatarVideoPreview: React.FC = () => {
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
            Step 1: Upload Photo + Audio
          </Typography>
          <Typography variant="body2">{avatarExamples.description}</Typography>
          <Stack direction="row" spacing={1} flexWrap="wrap">
            {['Photo upload', 'Audio upload', 'Lip-sync'].map(label => (
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
            <OptimizedImage
              src={avatarExamples.image}
              alt="Avatar photo example"
              loading="lazy"
              sizes="(max-width: 600px) 100vw, 50vw"
              sx={{ width: '100%', display: 'block' }}
            />
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
              Result: Talking Avatar
            </Typography>
            <Chip
              label="720p"
              size="small"
              sx={{ background: 'rgba(56,189,248,0.15)', color: '#38bdf8', borderRadius: 999 }}
            />
          </Stack>
          <Box
            sx={{
              borderRadius: 2,
              overflow: 'hidden',
              border: '1px solid rgba(255,255,255,0.08)',
              position: 'relative',
            }}
          >
            <OptimizedVideo
              src={avatarExamples.video}
              poster={avatarExamples.image}
              alt="Avatar video preview"
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
        Perfect for explainer videos, tutorials, personalized messages, and social media content. Your photo comes to life with perfect lip-sync.
      </Typography>
    </Box>
  );
};
