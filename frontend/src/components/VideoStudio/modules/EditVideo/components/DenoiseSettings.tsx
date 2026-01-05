import React from 'react';
import { Box, Typography, Paper, Slider, Stack, Chip } from '@mui/material';
import NoiseAwareIcon from '@mui/icons-material/NoiseAware';

interface DenoiseSettingsProps {
  strength: number;
  onStrengthChange: (value: number) => void;
}

export const DenoiseSettings: React.FC<DenoiseSettingsProps> = ({
  strength,
  onStrengthChange,
}) => {
  const getStrengthLevel = (value: number) => {
    if (value <= 0.3) return { label: 'Light', color: '#10b981', description: 'Subtle cleanup, preserves original audio quality' };
    if (value <= 0.6) return { label: 'Moderate', color: '#3b82f6', description: 'Good for background noise like AC, fans' };
    return { label: 'Strong', color: '#f59e0b', description: 'Heavy noise, may affect voice clarity' };
  };

  const level = getStrengthLevel(strength);

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
        <NoiseAwareIcon sx={{ color: '#3b82f6' }} />
        <Typography variant="subtitle2" sx={{ color: '#0f172a', fontWeight: 700 }}>
          Noise Reduction Settings
        </Typography>
      </Stack>

      <Stack spacing={3}>
        {/* Strength Display */}
        <Box>
          <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
            <Typography variant="h4" fontWeight={700} color="#0f172a">
              {Math.round(strength * 100)}%
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
            value={strength}
            onChange={(_, value) => onStrengthChange(value as number)}
            min={0}
            max={1}
            step={0.1}
            marks={[
              { value: 0, label: '0%' },
              { value: 0.3, label: '30%' },
              { value: 0.5, label: '50%' },
              { value: 0.7, label: '70%' },
              { value: 1, label: '100%' },
            ]}
            sx={{
              color: level.color,
              '& .MuiSlider-markLabel': {
                fontSize: '0.75rem',
              },
            }}
          />
        </Box>

        {/* Current Level Description */}
        <Box
          sx={{
            p: 2,
            borderRadius: 2,
            backgroundColor: '#f1f5f9',
            border: '1px solid #e2e8f0',
          }}
        >
          <Typography variant="body2" color="text.secondary">
            <strong>{level.label} Reduction:</strong> {level.description}
          </Typography>
        </Box>

        {/* Tips */}
        <Box
          sx={{
            p: 2,
            borderRadius: 2,
            backgroundColor: '#dbeafe',
            border: '1px solid #93c5fd',
          }}
        >
          <Typography variant="body2" color="#1e40af" sx={{ mb: 1 }}>
            <strong>💡 Tips for Best Results</strong>
          </Typography>
          <Stack component="ul" spacing={0.5} sx={{ pl: 2, m: 0 }}>
            <Typography component="li" variant="caption" color="#1e40af">
              Start with light reduction and increase if needed
            </Typography>
            <Typography component="li" variant="caption" color="#1e40af">
              High values may make voices sound muffled
            </Typography>
            <Typography component="li" variant="caption" color="#1e40af">
              Works best on constant background noise (AC, hum)
            </Typography>
            <Typography component="li" variant="caption" color="#1e40af">
              May not remove intermittent noises (clicks, pops)
            </Typography>
          </Stack>
        </Box>

        {strength > 0.7 && (
          <Box
            sx={{
              p: 2,
              borderRadius: 2,
              backgroundColor: '#fef3c7',
              border: '1px solid #fbbf24',
            }}
          >
            <Typography variant="caption" color="#92400e">
              ⚠️ High strength may affect audio quality. Consider using a lower setting and applying
              normalization after.
            </Typography>
          </Box>
        )}
      </Stack>
    </Paper>
  );
};
