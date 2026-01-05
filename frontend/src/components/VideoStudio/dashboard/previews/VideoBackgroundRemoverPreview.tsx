import React from 'react';
import { Box, Stack, Typography, Chip } from '@mui/material';
import { OptimizedVideo } from '../../../ImageStudio/dashboard/utils/OptimizedVideo';

export const VideoBackgroundRemoverPreview: React.FC = () => {
  return (
    <Box
      sx={{
        mt: 2,
        borderRadius: 3,
        border: '3px solid',
        borderImage: 'linear-gradient(135deg, rgba(239,68,68,0.8), rgba(249,115,22,0.8), rgba(251,191,36,0.8)) 1',
        overflow: 'hidden',
        height: { xs: 260, md: 300 },
        display: 'flex',
        background: '#0f172a',
      }}
    >
      <Box
        sx={{
          flex: '0 0 auto',
          width: '50%',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <OptimizedVideo
          src="/videos/scene_1_user_33Gz1FPI86V_0a5d0d71.mp4"
          alt="Original video with background"
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
            background: 'rgba(239,68,68,0.9)',
            color: '#fff',
            px: 2,
            py: 1,
            borderRadius: 2,
            fontWeight: 700,
            fontSize: '0.85rem',
          }}
        >
          Original
        </Box>
      </Box>
      <Box
        sx={{
          flex: '0 0 auto',
          width: '50%',
          position: 'relative',
          overflow: 'hidden',
          background: 'linear-gradient(135deg, #1e293b, #334155)',
        }}
      >
        <OptimizedVideo
          src="/videos/text-video-voiceover.mp4"
          alt="Background removed video"
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
            right: 16,
            background: 'rgba(16,185,129,0.9)',
            color: '#fff',
            px: 2,
            py: 1,
            borderRadius: 2,
            fontWeight: 700,
            fontSize: '0.85rem',
          }}
        >
          Background Removed
        </Box>
        <Box
          sx={{
            position: 'absolute',
            bottom: 16,
            left: 16,
            right: 16,
            background: 'rgba(15,23,42,0.9)',
            color: '#fff',
            p: 1.5,
            borderRadius: 2,
          }}
        >
          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
            <Chip
              size="small"
              label="Clean Matting"
              sx={{ background: '#10b981', color: '#fff', fontWeight: 600, fontSize: '0.7rem' }}
            />
            <Chip
              size="small"
              label="$0.01/s"
              sx={{ background: '#3b82f6', color: '#fff', fontWeight: 600, fontSize: '0.7rem' }}
            />
          </Stack>
        </Box>
      </Box>
    </Box>
  );
};
