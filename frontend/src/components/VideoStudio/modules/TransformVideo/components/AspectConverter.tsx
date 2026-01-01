import React from 'react';
import { Box, Typography, FormControl, InputLabel, Select, MenuItem, Stack, RadioGroup, FormControlLabel, Radio } from '@mui/material';
import type { AspectRatio } from '../hooks/useTransformVideo';

interface AspectConverterProps {
  targetAspect: AspectRatio;
  cropMode: 'center' | 'letterbox';
  onTargetAspectChange: (aspect: AspectRatio) => void;
  onCropModeChange: (mode: 'center' | 'letterbox') => void;
}

export const AspectConverter: React.FC<AspectConverterProps> = ({
  targetAspect,
  cropMode,
  onTargetAspectChange,
  onCropModeChange,
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
        Aspect Ratio Conversion Settings
      </Typography>

      <FormControl fullWidth>
        <InputLabel>Target Aspect Ratio</InputLabel>
        <Select
          value={targetAspect}
          label="Target Aspect Ratio"
          onChange={(e) => onTargetAspectChange(e.target.value as AspectRatio)}
        >
          <MenuItem value="16:9">16:9 (Landscape - YouTube, TV)</MenuItem>
          <MenuItem value="9:16">9:16 (Portrait - Instagram Reels, TikTok)</MenuItem>
          <MenuItem value="1:1">1:1 (Square - Instagram Posts)</MenuItem>
          <MenuItem value="4:5">4:5 (Portrait - Instagram Stories)</MenuItem>
          <MenuItem value="21:9">21:9 (Ultrawide - Cinematic)</MenuItem>
        </Select>
      </FormControl>

      <FormControl component="fieldset">
        <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
          Crop Mode
        </Typography>
        <RadioGroup
          value={cropMode}
          onChange={(e) => onCropModeChange(e.target.value as 'center' | 'letterbox')}
        >
          <FormControlLabel
            value="center"
            control={<Radio />}
            label="Center Crop (Crop to fit, may lose edges)"
          />
          <FormControlLabel
            value="letterbox"
            control={<Radio />}
            label="Letterbox (Add black bars, preserves full video)"
          />
        </RadioGroup>
      </FormControl>

      <Box
        sx={{
          p: 2,
          borderRadius: 1,
          backgroundColor: '#f1f5f9',
          border: '1px solid #e2e8f0',
        }}
      >
        <Typography variant="body2" color="text.secondary">
          <strong>Center Crop:</strong> Crops the video to fit the target aspect ratio. May remove parts of the video.
          <br />
          <strong>Letterbox:</strong> Adds black bars to fit the aspect ratio. Preserves the entire video.
        </Typography>
      </Box>
    </Stack>
  );
};
