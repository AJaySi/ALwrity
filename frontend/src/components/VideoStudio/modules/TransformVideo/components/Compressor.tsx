import React from 'react';
import { Box, Typography, FormControl, InputLabel, Select, MenuItem, Stack, TextField } from '@mui/material';
import type { Quality } from '../hooks/useTransformVideo';

interface CompressorProps {
  targetSizeMb: number | null;
  compressQuality: Quality;
  onTargetSizeMbChange: (size: number | null) => void;
  onCompressQualityChange: (quality: Quality) => void;
}

export const Compressor: React.FC<CompressorProps> = ({
  targetSizeMb,
  compressQuality,
  onTargetSizeMbChange,
  onCompressQualityChange,
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
        Compression Settings
      </Typography>

      <FormControl fullWidth>
        <InputLabel>Quality Preset</InputLabel>
        <Select
          value={compressQuality}
          label="Quality Preset"
          onChange={(e) => onCompressQualityChange(e.target.value as Quality)}
        >
          <MenuItem value="high">High (Best Quality, Larger File)</MenuItem>
          <MenuItem value="medium">Medium (Balanced)</MenuItem>
          <MenuItem value="low">Low (Smaller File, Lower Quality)</MenuItem>
        </Select>
      </FormControl>

      <TextField
        fullWidth
        label="Target File Size (MB)"
        type="number"
        value={targetSizeMb || ''}
        onChange={(e) => {
          const value = e.target.value;
          onTargetSizeMbChange(value ? parseFloat(value) : null);
        }}
        helperText="Optional: Specify target file size. If not set, quality preset will be used."
        inputProps={{ min: 1, step: 0.1 }}
      />

      <Box
        sx={{
          p: 2,
          borderRadius: 1,
          backgroundColor: '#f1f5f9',
          border: '1px solid #e2e8f0',
        }}
      >
        <Typography variant="body2" color="text.secondary">
          <strong>Quality Preset:</strong> Uses optimized bitrate settings for the selected quality level.
          <br />
          <strong>Target Size:</strong> Calculates bitrate to achieve the specified file size. Overrides quality preset if set.
        </Typography>
      </Box>
    </Stack>
  );
};
