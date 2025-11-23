import React from 'react';
import { Box, Stack, Typography, Chip } from '@mui/material';
import { createExamples } from '../constants';
import { OptimizedImage } from '../utils/OptimizedImage';

export const CreateEffectPreview: React.FC = () => {
  const [textHovered, setTextHovered] = React.useState(false);
  const [exampleIndex, setExampleIndex] = React.useState(0);
  const example = createExamples[exampleIndex];
  const imageWidth = textHovered ? '20%' : '70%';
  const textWidth = textHovered ? '80%' : '30%';

  return (
    <Box
      sx={{
        borderRadius: 3,
        border: '3px solid',
        borderImage:
          'linear-gradient(135deg, rgba(124,58,237,0.8), rgba(14,165,233,0.8), rgba(16,185,129,0.8)) 1',
        overflow: 'hidden',
        height: { xs: 240, md: 280 },
        display: 'flex',
        background: '#0f172a',
        mt: 1,
      }}
    >
      <Box
        sx={{
          flex: '0 0 auto',
          width: imageWidth,
          transition: 'width 0.4s ease, filter 0.4s ease',
          filter: textHovered ? 'saturate(1.1)' : 'saturate(1)',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <OptimizedImage
          src={example.image}
          alt={example.label}
          loading="lazy"
          sizes="(max-width: 600px) 70vw, 50vw"
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
            background: 'rgba(15,23,42,0.8)',
            borderRadius: 999,
            px: 1.5,
            py: 0.5,
            boxShadow: '0 10px 20px rgba(2,6,23,0.45)',
          }}
        >
          {createExamples.map((_, idx) => (
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
            {example.label}
          </Typography>
          <Typography variant="subtitle2" fontWeight={700}>
            Prompt
          </Typography>
          <Typography variant="body2">{example.prompt}</Typography>
          <Typography variant="body2">{example.description}</Typography>
          <Stack direction="row" spacing={1} flexWrap="wrap">
            <Chip
              size="small"
              label={`Price ${example.price}`}
              sx={{ background: '#ede9fe', color: '#4c1d95', borderRadius: 999, fontWeight: 600 }}
            />
            <Chip
              size="small"
              label={`Turnaround ${example.eta}`}
              sx={{ background: '#cffafe', color: '#0f766e', borderRadius: 999, fontWeight: 600 }}
            />
            <Chip
              size="small"
              label={example.provider}
              sx={{ background: '#dcfce7', color: '#166534', borderRadius: 999, fontWeight: 600 }}
            />
          </Stack>
        </Stack>
      </Box>
    </Box>
  );
};

