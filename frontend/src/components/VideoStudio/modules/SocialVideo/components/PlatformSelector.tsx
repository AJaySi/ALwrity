import React from 'react';
import { Box, Typography, FormControlLabel, Checkbox, Stack, Chip, Paper } from '@mui/material';
import { Platform } from '../hooks/useSocialVideo';

interface PlatformSelectorProps {
  selectedPlatforms: Platform[];
  platformSpecs: Record<string, any>;
  onTogglePlatform: (platform: Platform) => void;
}

const platformInfo: Record<Platform, { label: string; icon: string; color: string }> = {
  instagram: { label: 'Instagram Reels', icon: '📷', color: '#E4405F' },
  tiktok: { label: 'TikTok', icon: '🎵', color: '#000000' },
  youtube: { label: 'YouTube Shorts', icon: '▶️', color: '#FF0000' },
  linkedin: { label: 'LinkedIn', icon: '💼', color: '#0077B5' },
  facebook: { label: 'Facebook', icon: '👥', color: '#1877F2' },
  twitter: { label: 'Twitter/X', icon: '🐦', color: '#1DA1F2' },
};

export const PlatformSelector: React.FC<PlatformSelectorProps> = ({
  selectedPlatforms,
  platformSpecs,
  onTogglePlatform,
}) => {
  const getPlatformSpec = (platform: Platform) => {
    const specs = platformSpecs[platform];
    if (!specs || specs.length === 0) return null;
    return specs[0]; // Get first format
  };

  return (
    <Box>
      <Typography
        variant="subtitle2"
        sx={{
          mb: 2,
          color: '#0f172a',
          fontWeight: 700,
        }}
      >
        Select Platforms
      </Typography>
      <Stack spacing={1.5}>
        {(Object.keys(platformInfo) as Platform[]).map((platform) => {
          const info = platformInfo[platform];
          const spec = getPlatformSpec(platform);
          const isSelected = selectedPlatforms.includes(platform);

          return (
            <Paper
              key={platform}
              elevation={0}
              sx={{
                p: 2,
                borderRadius: 2,
                border: `2px solid ${isSelected ? info.color : '#e2e8f0'}`,
                backgroundColor: isSelected ? `${info.color}08` : '#ffffff',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                '&:hover': {
                  borderColor: info.color,
                  backgroundColor: `${info.color}08`,
                },
              }}
              onClick={() => onTogglePlatform(platform)}
            >
              <Stack direction="row" spacing={2} alignItems="center">
                <Checkbox
                  checked={isSelected}
                  onChange={() => onTogglePlatform(platform)}
                  sx={{
                    color: info.color,
                    '&.Mui-checked': {
                      color: info.color,
                    },
                  }}
                />
                <Box sx={{ flex: 1 }}>
                  <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 0.5 }}>
                    <Typography variant="body1" sx={{ fontWeight: 600 }}>
                      {info.icon} {info.label}
                    </Typography>
                  </Stack>
                  {spec && (
                    <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ mt: 0.5 }}>
                      <Chip
                        label={spec.aspect_ratio}
                        size="small"
                        sx={{ height: 20, fontSize: '0.7rem' }}
                      />
                      <Chip
                        label={`Max ${spec.max_duration}s`}
                        size="small"
                        sx={{ height: 20, fontSize: '0.7rem' }}
                      />
                      <Chip
                        label={`${spec.width}x${spec.height}`}
                        size="small"
                        sx={{ height: 20, fontSize: '0.7rem' }}
                      />
                    </Stack>
                  )}
                </Box>
              </Stack>
            </Paper>
          );
        })}
      </Stack>
    </Box>
  );
};
