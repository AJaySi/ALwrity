import React from 'react';
import { Box, Typography, Paper, Slider, Stack, Chip } from '@mui/material';
import SpeedIcon from '@mui/icons-material/Speed';

interface SpeedSettingsProps {
  videoDuration: number;
  speedFactor: number;
  onSpeedFactorChange: (value: number) => void;
}

const speedMarks = [
  { value: 0.25, label: '0.25x' },
  { value: 0.5, label: '0.5x' },
  { value: 1.0, label: '1x' },
  { value: 1.5, label: '1.5x' },
  { value: 2.0, label: '2x' },
  { value: 4.0, label: '4x' },
];

export const SpeedSettings: React.FC<SpeedSettingsProps> = ({
  videoDuration,
  speedFactor,
  onSpeedFactorChange,
}) => {
  const resultDuration = videoDuration / speedFactor;
  
  const getSpeedLabel = (factor: number) => {
    if (factor < 1) return 'Slow Motion';
    if (factor === 1) return 'Normal';
    return 'Fast Forward';
  };

  return (
    <Paper
      elevation={0}
      sx={{
        p: 3,
        borderRadius: 2,
        border: '1px solid #e2e8f0',
        backgroundColor: '#ffffff',
      }}
    >
      <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
        <SpeedIcon sx={{ color: '#3b82f6' }} />
        <Typography
          variant="subtitle2"
          sx={{
            color: '#0f172a',
            fontWeight: 700,
          }}
        >
          Speed Settings
        </Typography>
      </Stack>

      <Stack spacing={3}>
        {/* Speed Slider */}
        <Box>
          <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
            <Typography variant="h4" fontWeight={700} color="#0f172a">
              {speedFactor}x
            </Typography>
            <Chip
              label={getSpeedLabel(speedFactor)}
              size="small"
              sx={{
                backgroundColor: speedFactor < 1 ? '#6366f1' : speedFactor > 1 ? '#f59e0b' : '#10b981',
                color: '#fff',
              }}
            />
          </Stack>
          <Slider
            value={speedFactor}
            onChange={(_, value) => onSpeedFactorChange(value as number)}
            min={0.25}
            max={4.0}
            step={0.25}
            marks={speedMarks}
            valueLabelDisplay="auto"
            valueLabelFormat={(value) => `${value}x`}
            sx={{
              color: '#3b82f6',
              '& .MuiSlider-markLabel': {
                fontSize: '0.75rem',
              },
            }}
          />
        </Box>

        {/* Duration Preview */}
        <Box
          sx={{
            p: 2,
            borderRadius: 2,
            backgroundColor: '#f1f5f9',
            border: '1px solid #e2e8f0',
          }}
        >
          <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Box>
              <Typography variant="caption" color="text.secondary">
                Original Duration
              </Typography>
              <Typography variant="body1" fontWeight={600} color="#0f172a">
                {videoDuration.toFixed(1)}s
              </Typography>
            </Box>
            <Typography variant="h5" color="#64748b">
              →
            </Typography>
            <Box>
              <Typography variant="caption" color="text.secondary">
                Result Duration
              </Typography>
              <Typography variant="body1" fontWeight={600} color="#3b82f6">
                {resultDuration.toFixed(1)}s
              </Typography>
            </Box>
          </Stack>
        </Box>

        {/* Tips */}
        <Typography variant="caption" color="text.secondary">
          {speedFactor < 1
            ? '💡 Slow motion is great for dramatic effect or analyzing motion'
            : speedFactor > 1
            ? '💡 Fast forward can help condense long clips or create time-lapse effect'
            : '💡 Normal speed keeps the video unchanged'}
        </Typography>
      </Stack>
    </Paper>
  );
};
