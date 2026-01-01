import React from 'react';
import { Box, Typography, FormControl, InputLabel, Select, MenuItem, Stack, FormControlLabel, Checkbox } from '@mui/material';
import type { Resolution } from '../hooks/useTransformVideo';

interface ResolutionScalerProps {
  targetResolution: Resolution;
  maintainAspect: boolean;
  onTargetResolutionChange: (resolution: Resolution) => void;
  onMaintainAspectChange: (maintain: boolean) => void;
}

export const ResolutionScaler: React.FC<ResolutionScalerProps> = ({
  targetResolution,
  maintainAspect,
  onTargetResolutionChange,
  onMaintainAspectChange,
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
        Resolution Scaling Settings
      </Typography>

      <FormControl fullWidth>
        <InputLabel>Target Resolution</InputLabel>
        <Select
          value={targetResolution}
          label="Target Resolution"
          onChange={(e) => onTargetResolutionChange(e.target.value as Resolution)}
        >
          <MenuItem value="480p">480p (SD - 854x480)</MenuItem>
          <MenuItem value="720p">720p (HD - 1280x720)</MenuItem>
          <MenuItem value="1080p">1080p (Full HD - 1920x1080)</MenuItem>
          <MenuItem value="1440p">1440p (2K - 2560x1440)</MenuItem>
          <MenuItem value="4k">4K (UHD - 3840x2160)</MenuItem>
        </Select>
      </FormControl>

      <FormControlLabel
        control={
          <Checkbox
            checked={maintainAspect}
            onChange={(e) => onMaintainAspectChange(e.target.checked)}
          />
        }
        label="Maintain Aspect Ratio"
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
          {maintainAspect
            ? 'The video will be scaled to match the target resolution while preserving the original aspect ratio. This may add letterboxing or pillarboxing.'
            : 'The video will be stretched or compressed to exactly match the target resolution. This may distort the video if aspect ratios differ.'}
        </Typography>
      </Box>
    </Stack>
  );
};
