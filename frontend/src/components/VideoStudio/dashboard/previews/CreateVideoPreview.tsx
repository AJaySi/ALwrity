import React from 'react';
import { Box, Stack, Typography, Chip } from '@mui/material';
import { createVideoExamples } from '../constants';
import { OptimizedVideo } from '../../../ImageStudio/dashboard/utils/OptimizedVideo';

export const CreateVideoPreview: React.FC = () => {
  const [textHovered, setTextHovered] = React.useState(false);
  const [exampleIndex, setExampleIndex] = React.useState(0);
  const example = createVideoExamples[exampleIndex];
  const videoWidth = textHovered ? '20%' : '70%';
  const textWidth = textHovered ? '80%' : '30%';

  return (
    <Box
      sx={{
        borderRadius: 3,
        border: '3px solid',
        borderImage:
          'linear-gradient(135deg, rgba(124,58,237,0.8), rgba(14,165,233,0.8), rgba(16,185,129,0.8)) 1',
        overflow: 'hidden',
        height: { xs: 260, md: 300 },
        display: 'flex',
        background: '#0f172a',
        mt: 1,
      }}
    >
      <Box
        sx={{
          flex: '0 0 auto',
          width: videoWidth,
          transition: 'width 0.4s ease, filter 0.4s ease',
          filter: textHovered ? 'saturate(1.1)' : 'saturate(1)',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <OptimizedVideo
          src={example.video}
          alt={example.label}
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
        <Stack
          direction="row"
          spacing={1}
          sx={{
            position: 'absolute',
            bottom: 16,
            left: '50%',
            transform: 'translateX(-50%)',
            background: 'rgba(15,23,42,0.85)',
            borderRadius: 999,
            px: 1.5,
            py: 0.5,
            boxShadow: '0 10px 20px rgba(2,6,23,0.45)',
          }}
        >
          {createVideoExamples.map((_, idx) => (
            <Box
              key={_.id}
              onClick={() => setExampleIndex(idx)}
              sx={{
                width: 32,
                height: 10,
                borderRadius: 999,
                background: idx === exampleIndex ? '#c4b5fd' : 'rgba(255,255,255,0.3)',
                cursor: 'pointer',
                transition: 'background 0.2s ease',
              }}
            />
          ))}
        </Stack>
      </Box>
      <Box
        sx={{
          flex: '0 0 auto',
          width: textWidth,
          background: 'rgba(248,250,252,0.95)',
          color: '#0f172a',
          p: 3,
          display: 'flex',
          flexDirection: 'column',
          gap: 1,
          boxShadow: '-12px 0 24px rgba(15,23,42,0.25)',
          transition: 'width 0.4s ease',
        }}
        onMouseEnter={() => setTextHovered(true)}
        onMouseLeave={() => setTextHovered(false)}
      >
        <Stack spacing={0.5} sx={{ overflowY: textHovered ? 'auto' : 'hidden', pr: 1 }}>
          <Typography variant="overline" sx={{ letterSpacing: 1.5, color: '#818cf8' }}>
            Step 1: Enter Your Video Requirements
          </Typography>
          <Typography variant="subtitle2" fontWeight={700}>
            Example Prompt
          </Typography>
          <Typography variant="body2">{example.prompt}</Typography>
          <Typography variant="body2" sx={{ fontStyle: 'italic', color: '#475569' }}>
            {example.description}
          </Typography>
          <Stack direction="row" spacing={1} flexWrap="wrap">
            <Chip
              size="small"
              label={`Price ${example.price}`}
              sx={{ background: '#ede9fe', color: '#4c1d95', borderRadius: 999, fontWeight: 600 }}
            />
            <Chip
              size="small"
              label={`Ready in ${example.eta}`}
              sx={{ background: '#cffafe', color: '#0f766e', borderRadius: 999, fontWeight: 600 }}
            />
            <Chip
              size="small"
              label={example.platform}
              sx={{ background: '#dcfce7', color: '#166534', borderRadius: 999, fontWeight: 600 }}
            />
          </Stack>
          <Typography variant="caption" sx={{ color: '#64748b', mt: 0.5 }}>
            Best for: {example.useCase}
          </Typography>
        </Stack>
      </Box>
    </Box>
  );
};
