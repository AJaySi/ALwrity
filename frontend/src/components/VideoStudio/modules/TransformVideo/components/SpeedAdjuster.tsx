import React from 'react';
import { Box, Typography, Slider, Stack, Chip } from '@mui/material';

interface SpeedAdjusterProps {
  speedFactor: number;
  onSpeedFactorChange: (factor: number) => void;
}

const speedPresets = [
  { label: '0.25x', value: 0.25, description: 'Very Slow' },
  { label: '0.5x', value: 0.5, description: 'Slow Motion' },
  { label: '1x', value: 1.0, description: 'Normal' },
  { label: '1.5x', value: 1.5, description: 'Fast' },
  { label: '2x', value: 2.0, description: '2x Speed' },
  { label: '4x', value: 4.0, description: 'Time-lapse' },
];

export const SpeedAdjuster: React.FC<SpeedAdjusterProps> = ({
  speedFactor,
  onSpeedFactorChange,
}) => {
  return (
    <Stack spacing={3}>
      <Typography
        variant="subtitle1"
        sx={{
          color: '#0f172a',
          fontWeight: 700,
        }}
      >
        Speed Adjustment Settings
      </Typography>

      <Box>
        <Typography variant="body2" sx={{ mb: 2, color: 'text.secondary' }}>
          Select a preset or use the slider for custom speed:
        </Typography>
        <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ mb: 3 }}>
          {speedPresets.map((preset) => (
            <Chip
              key={preset.value}
              label={`${preset.label} (${preset.description})`}
              onClick={() => onSpeedFactorChange(preset.value)}
              color={speedFactor === preset.value ? 'primary' : 'default'}
              sx={{
                cursor: 'pointer',
                fontWeight: speedFactor === preset.value ? 700 : 400,
              }}
            />
          ))}
        </Stack>

        <Typography variant="body2" sx={{ mb: 1, fontWeight: 600 }}>
          Custom Speed: {speedFactor}x
        </Typography>
        <Slider
          value={speedFactor}
          onChange={(_, value) => onSpeedFactorChange(value as number)}
          min={0.25}
          max={4.0}
          step={0.25}
          marks={[
            { value: 0.25, label: '0.25x' },
            { value: 1.0, label: '1x' },
            { value: 2.0, label: '2x' },
            { value: 4.0, label: '4x' },
          ]}
          sx={{
            '& .MuiSlider-markLabel': {
              fontSize: '0.75rem',
            },
          }}
        />
      </Box>

      <Box
        sx={{
          p: 2,
          borderRadius: 1,
          backgroundColor: '#f1f5f9',
          border: '1px solid #e2e8f0',
        }}
      >
        <Typography variant="body2" color="text.secondary">
          Speed adjustment affects both video and audio. Values below 1x create slow motion, values above 1x create fast-forward or time-lapse effects.
        </Typography>
      </Box>
    </Stack>
  );
};
