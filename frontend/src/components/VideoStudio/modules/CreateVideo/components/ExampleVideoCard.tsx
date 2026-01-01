import React from 'react';
import { Box, Card, CardContent, Stack, Typography, Chip } from '@mui/material';
import PlayCircleOutlineIcon from '@mui/icons-material/PlayCircleOutline';
import { motion as framerMotion } from 'framer-motion';
import { OptimizedVideo } from '../../../../ImageStudio/dashboard/utils/OptimizedVideo';
import type { ExampleVideo } from '../types';

interface ExampleVideoCardProps {
  example: ExampleVideo;
  index: number;
  isSelected: boolean;
  onClick: () => void;
}

export const ExampleVideoCard: React.FC<ExampleVideoCardProps> = ({
  example,
  index,
  isSelected,
  onClick,
}) => {
  return (
    <framerMotion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <Card
        sx={{
          cursor: 'pointer',
          border: isSelected ? '2px solid #667eea' : '1px solid #e2e8f0',
          borderRadius: 2,
          overflow: 'hidden',
          transition: 'all 0.2s',
          '&:hover': {
            boxShadow: '0 8px 24px rgba(102, 126, 234, 0.2)',
          },
        }}
        onClick={onClick}
      >
        <Box
          sx={{
            position: 'relative',
            width: '100%',
            paddingTop: '56.25%', // 16:9 aspect ratio
            backgroundColor: '#0f172a',
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
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              objectFit: 'cover',
            }}
          />
          {isSelected && (
            <Box
              sx={{
                position: 'absolute',
                top: 8,
                right: 8,
                background: '#667eea',
                borderRadius: '50%',
                p: 0.5,
              }}
            >
              <PlayCircleOutlineIcon sx={{ color: '#fff', fontSize: 20 }} />
            </Box>
          )}
        </Box>
        <CardContent sx={{ p: 2 }}>
          <Stack spacing={1}>
            <Stack direction="row" justifyContent="space-between" alignItems="center">
              <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#0f172a' }}>
                {example.label}
              </Typography>
              <Chip
                label={example.platform}
                size="small"
                sx={{
                  background: 'rgba(102, 126, 234, 0.1)',
                  color: '#667eea',
                  fontWeight: 600,
                  fontSize: 10,
                }}
              />
            </Stack>
            <Typography variant="caption" sx={{ color: '#475569', fontSize: 11 }}>
              {example.description}
            </Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap">
              <Chip
                label={example.price}
                size="small"
                sx={{
                  background: 'rgba(16, 185, 129, 0.1)',
                  color: '#047857',
                  fontWeight: 600,
                  fontSize: 10,
                }}
              />
              <Chip
                label={example.eta}
                size="small"
                sx={{
                  background: 'rgba(59, 130, 246, 0.1)',
                  color: '#1e40af',
                  fontWeight: 600,
                  fontSize: 10,
                }}
              />
            </Stack>
          </Stack>
        </CardContent>
      </Card>
    </framerMotion.div>
  );
};
