import React from 'react';
import { Box, Stack, Typography, Chip } from '@mui/material';
import { upscaleSamples } from '../constants';
import { OptimizedImage } from '../utils/OptimizedImage';

export const UpscaleEffectPreview: React.FC = () => (
  <Box
    sx={{
      mt: 2,
      borderRadius: 3,
      border: '1px solid rgba(255,255,255,0.08)',
      background: 'rgba(15,23,42,0.5)',
      p: { xs: 2, md: 3 },
    }}
  >
    <Stack direction="row" spacing={1} alignItems="center" justifyContent="space-between">
      <Box>
        <Typography variant="overline" sx={{ letterSpacing: 2, color: '#f9a8d4' }}>
          4× Upscale Showcase
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Flip the panels to compare the low-res upload with the 4K-ready output.
        </Typography>
      </Box>
      <Chip
        label="Fast vs Creative"
        size="small"
        sx={{ background: 'rgba(236,72,153,0.15)', color: '#f9a8d4', borderRadius: 999 }}
      />
    </Stack>

    <Box
      sx={{
        mt: 2,
        display: 'flex',
        gap: 2,
        justifyContent: 'center',
        flexWrap: 'wrap',
        '&:hover .flip-left': { transform: 'rotateY(-180deg)' },
        '&:hover .flip-right': { transform: 'rotateY(180deg)' },
      }}
    >
      {[
        { key: 'low', label: 'Before 600×400', className: 'flip-left', image: upscaleSamples.lowRes },
        { key: 'high', label: 'After 2400×1600', className: 'flip-right', image: upscaleSamples.hiRes },
      ].map(card => (
        <Box key={card.key} sx={{ perspective: 1000, width: { xs: 140, sm: 180 }, height: { xs: 200, sm: 240 } }}>
          <Box
            className={card.className}
            sx={{ position: 'relative', width: '100%', height: '100%', transition: '0.6s', transformStyle: 'preserve-3d' }}
          >
            <Box
              className="front"
              sx={{
                position: 'absolute',
                inset: 0,
                backfaceVisibility: 'hidden',
                borderRadius: 3,
                border: '1px solid rgba(255,255,255,0.1)',
                background:
                  card.key === 'low'
                    ? 'linear-gradient(135deg,#4c1d95,#9333ea)'
                    : 'linear-gradient(135deg,#0f766e,#14b8a6)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: card.key === 'low' ? 'flex-end' : 'flex-start',
                px: 2,
                color: '#fff',
              }}
            >
              <Box
                sx={{
                  width: 80,
                  height: 80,
                  borderRadius: '50%',
                  background: 'rgba(255,255,255,0.2)',
                  border: '2px solid rgba(255,255,255,0.8)',
                }}
              />
              <Typography variant="caption" sx={{ ml: card.key === 'low' ? -6 : 2, mr: card.key === 'low' ? 2 : -6 }}>
                {card.label}
              </Typography>
            </Box>
            <Box
              className="back"
              sx={{
                position: 'absolute',
                inset: 0,
                backfaceVisibility: 'hidden',
                borderRadius: 3,
                transform: 'rotateY(180deg)',
                overflow: 'hidden',
                border: '1px solid rgba(255,255,255,0.15)',
              }}
            >
              <OptimizedImage
                src={card.image}
                alt={card.label}
                loading="lazy"
                sizes="(max-width: 600px) 140px, 180px"
                sx={{ width: '100%', height: '100%', objectFit: 'cover' }}
              />
            </Box>
          </Box>
        </Box>
      ))}
    </Box>

    <Typography variant="caption" color="text.secondary" sx={{ mt: 1.5 }}>
      Try creative upscaling for texture enhancement, or fast mode for previews.
    </Typography>
  </Box>
);

