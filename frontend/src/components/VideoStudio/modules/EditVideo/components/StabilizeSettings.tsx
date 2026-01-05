import React from 'react';
import { Box, Typography, Paper, Slider, Stack, Chip } from '@mui/material';
import CameraAltIcon from '@mui/icons-material/CameraAlt';

interface StabilizeSettingsProps {
  smoothing: number;
  onSmoothingChange: (value: number) => void;
}

export const StabilizeSettings: React.FC<StabilizeSettingsProps> = ({
  smoothing,
  onSmoothingChange,
}) => {
  const getStabilizationLevel = (value: number) => {
    if (value <= 5) return { label: 'Light', color: '#10b981' };
    if (value <= 15) return { label: 'Moderate', color: '#3b82f6' };
    if (value <= 30) return { label: 'Strong', color: '#f59e0b' };
    return { label: 'Maximum', color: '#ef4444' };
  };

  const level = getStabilizationLevel(smoothing);

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
        <CameraAltIcon sx={{ color: '#3b82f6' }} />
        <Typography
          variant="subtitle2"
          sx={{
            color: '#0f172a',
            fontWeight: 700,
          }}
        >
          Stabilization Settings
        </Typography>
      </Stack>

      <Stack spacing={3}>
        {/* Smoothing Slider */}
        <Box>
          <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
            <Typography variant="h4" fontWeight={700} color="#0f172a">
              {smoothing}
            </Typography>
            <Chip
              label={level.label}
              size="small"
              sx={{
                backgroundColor: level.color,
                color: '#fff',
              }}
            />
          </Stack>
          <Slider
            value={smoothing}
            onChange={(_, value) => onSmoothingChange(value as number)}
            min={1}
            max={100}
            step={1}
            marks={[
              { value: 1, label: 'Min' },
              { value: 10, label: '10' },
              { value: 30, label: '30' },
              { value: 50, label: '50' },
              { value: 100, label: 'Max' },
            ]}
            valueLabelDisplay="auto"
            sx={{
              color: '#3b82f6',
              '& .MuiSlider-markLabel': {
                fontSize: '0.75rem',
              },
            }}
          />
        </Box>

        {/* Info Box */}
        <Box
          sx={{
            p: 2,
            borderRadius: 2,
            backgroundColor: '#f1f5f9',
            border: '1px solid #e2e8f0',
          }}
        >
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            <strong>Smoothing</strong> controls how aggressively camera shake is corrected.
          </Typography>
          <Stack component="ul" spacing={0.5} sx={{ pl: 2, m: 0 }}>
            <Typography component="li" variant="caption" color="text.secondary">
              <strong>1-5:</strong> Light stabilization, preserves natural motion
            </Typography>
            <Typography component="li" variant="caption" color="text.secondary">
              <strong>10-15:</strong> Recommended for handheld footage
            </Typography>
            <Typography component="li" variant="caption" color="text.secondary">
              <strong>30+:</strong> Strong stabilization, may add slight zoom
            </Typography>
          </Stack>
        </Box>

        {/* Warning */}
        <Box
          sx={{
            p: 2,
            borderRadius: 2,
            backgroundColor: '#fef3c7',
            border: '1px solid #fbbf24',
          }}
        >
          <Typography variant="caption" color="#92400e">
            ⚠️ Stabilization uses FFmpeg's vidstab filter and requires FFmpeg with vidstab support. 
            Processing may take longer for high-resolution or long videos.
          </Typography>
        </Box>
      </Stack>
    </Paper>
  );
};
