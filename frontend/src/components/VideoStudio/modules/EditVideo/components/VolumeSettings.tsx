import React from 'react';
import { Box, Typography, Paper, Slider, Stack, Chip } from '@mui/material';
import VolumeUpIcon from '@mui/icons-material/VolumeUp';
import VolumeOffIcon from '@mui/icons-material/VolumeOff';
import VolumeMuteIcon from '@mui/icons-material/VolumeMute';

interface VolumeSettingsProps {
  volumeFactor: number;
  onVolumeFactorChange: (value: number) => void;
}

const volumeMarks = [
  { value: 0, label: 'Mute' },
  { value: 0.5, label: '50%' },
  { value: 1.0, label: '100%' },
  { value: 2.0, label: '200%' },
  { value: 3.0, label: '300%' },
];

export const VolumeSettings: React.FC<VolumeSettingsProps> = ({
  volumeFactor,
  onVolumeFactorChange,
}) => {
  const getVolumeLabel = (factor: number) => {
    if (factor === 0) return { label: 'Muted', color: '#64748b', icon: <VolumeOffIcon /> };
    if (factor < 1) return { label: 'Reduced', color: '#f59e0b', icon: <VolumeMuteIcon /> };
    if (factor === 1) return { label: 'Original', color: '#10b981', icon: <VolumeUpIcon /> };
    if (factor <= 2) return { label: 'Boosted', color: '#3b82f6', icon: <VolumeUpIcon /> };
    return { label: 'Loud', color: '#ef4444', icon: <VolumeUpIcon /> };
  };

  const info = getVolumeLabel(volumeFactor);

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
        <VolumeUpIcon sx={{ color: '#3b82f6' }} />
        <Typography variant="subtitle2" sx={{ color: '#0f172a', fontWeight: 700 }}>
          Volume Settings
        </Typography>
      </Stack>

      <Stack spacing={3}>
        {/* Volume Display */}
        <Box>
          <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
            <Typography variant="h3" fontWeight={700} color="#0f172a">
              {Math.round(volumeFactor * 100)}%
            </Typography>
            <Chip
              icon={info.icon}
              label={info.label}
              size="small"
              sx={{
                backgroundColor: info.color,
                color: '#fff',
                '& .MuiChip-icon': { color: '#fff' },
              }}
            />
          </Stack>
          <Slider
            value={volumeFactor}
            onChange={(_, value) => onVolumeFactorChange(value as number)}
            min={0}
            max={3}
            step={0.1}
            marks={volumeMarks}
            valueLabelDisplay="auto"
            valueLabelFormat={(value) => `${Math.round(value * 100)}%`}
            sx={{
              color: info.color,
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
          <Typography variant="body2" color="text.secondary">
            <strong>Volume Factor:</strong>
          </Typography>
          <Stack component="ul" spacing={0.5} sx={{ pl: 2, m: 0, mt: 1 }}>
            <Typography component="li" variant="caption" color="text.secondary">
              <strong>0%:</strong> Completely muted (silent video)
            </Typography>
            <Typography component="li" variant="caption" color="text.secondary">
              <strong>50%:</strong> Half volume (quieter)
            </Typography>
            <Typography component="li" variant="caption" color="text.secondary">
              <strong>100%:</strong> Original volume (no change)
            </Typography>
            <Typography component="li" variant="caption" color="text.secondary">
              <strong>200%+:</strong> Boosted (may cause distortion)
            </Typography>
          </Stack>
        </Box>

        {volumeFactor > 2 && (
          <Box
            sx={{
              p: 2,
              borderRadius: 2,
              backgroundColor: '#fef3c7',
              border: '1px solid #fbbf24',
            }}
          >
            <Typography variant="caption" color="#92400e">
              ⚠️ High volume levels may cause audio distortion. Consider normalizing instead.
            </Typography>
          </Box>
        )}
      </Stack>
    </Paper>
  );
};
