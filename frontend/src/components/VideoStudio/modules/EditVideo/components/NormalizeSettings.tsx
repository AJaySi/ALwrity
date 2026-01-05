import React from 'react';
import { Box, Typography, Paper, Slider, Stack, Chip, Select, MenuItem, FormControl, InputLabel } from '@mui/material';
import TuneIcon from '@mui/icons-material/Tune';

interface NormalizeSettingsProps {
  targetLevel: number;
  onTargetLevelChange: (value: number) => void;
}

const presets = [
  { value: -14, label: 'Streaming (YouTube, Spotify)', description: '-14 LUFS' },
  { value: -16, label: 'Podcasts', description: '-16 LUFS' },
  { value: -23, label: 'TV Broadcast (EBU R128)', description: '-23 LUFS' },
  { value: -24, label: 'US Broadcast (ATSC A/85)', description: '-24 LUFS' },
];

export const NormalizeSettings: React.FC<NormalizeSettingsProps> = ({
  targetLevel,
  onTargetLevelChange,
}) => {
  const currentPreset = presets.find((p) => p.value === targetLevel);

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
        <TuneIcon sx={{ color: '#3b82f6' }} />
        <Typography variant="subtitle2" sx={{ color: '#0f172a', fontWeight: 700 }}>
          Audio Normalization Settings
        </Typography>
      </Stack>

      <Stack spacing={3}>
        {/* Preset Selection */}
        <FormControl fullWidth size="small">
          <InputLabel>Preset</InputLabel>
          <Select
            value={targetLevel}
            label="Preset"
            onChange={(e) => onTargetLevelChange(e.target.value as number)}
          >
            {presets.map((preset) => (
              <MenuItem key={preset.value} value={preset.value}>
                <Stack direction="row" spacing={1} alignItems="center" justifyContent="space-between" width="100%">
                  <span>{preset.label}</span>
                  <Chip label={preset.description} size="small" variant="outlined" />
                </Stack>
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {/* Manual Slider */}
        <Box>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Target Level: {targetLevel} LUFS
          </Typography>
          <Slider
            value={targetLevel}
            onChange={(_, value) => onTargetLevelChange(value as number)}
            min={-30}
            max={-10}
            step={1}
            marks={[
              { value: -30, label: '-30' },
              { value: -23, label: '-23' },
              { value: -16, label: '-16' },
              { value: -14, label: '-14' },
              { value: -10, label: '-10' },
            ]}
            sx={{ color: '#3b82f6' }}
          />
        </Box>

        {/* Info Box */}
        <Box
          sx={{
            p: 2,
            borderRadius: 2,
            backgroundColor: '#dbeafe',
            border: '1px solid #93c5fd',
          }}
        >
          <Typography variant="body2" color="#1e40af" sx={{ mb: 1 }}>
            <strong>EBU R128 Normalization</strong>
          </Typography>
          <Typography variant="caption" color="#1e40af">
            {currentPreset
              ? `Using ${currentPreset.label} preset (${currentPreset.description}). This ensures consistent audio levels across your content.`
              : `Custom level: ${targetLevel} LUFS. Lower values = quieter, higher values = louder.`}
          </Typography>
        </Box>

        {/* LUFS Explanation */}
        <Box
          sx={{
            p: 2,
            borderRadius: 2,
            backgroundColor: '#f1f5f9',
            border: '1px solid #e2e8f0',
          }}
        >
          <Typography variant="caption" color="text.secondary">
            <strong>What is LUFS?</strong> Loudness Units relative to Full Scale (LUFS) is the
            industry standard for measuring audio loudness. It accounts for human perception,
            making volume levels consistent across different content.
          </Typography>
        </Box>
      </Stack>
    </Paper>
  );
};
