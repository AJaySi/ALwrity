import React from 'react';
import { Box, Typography, FormControlLabel, Switch, FormControl, RadioGroup, Radio, Stack, Paper } from '@mui/material';
import { TrimMode } from '../hooks/useSocialVideo';

interface OptimizationOptionsProps {
  autoCrop: boolean;
  generateThumbnails: boolean;
  compress: boolean;
  trimMode: TrimMode;
  onAutoCropChange: (value: boolean) => void;
  onGenerateThumbnailsChange: (value: boolean) => void;
  onCompressChange: (value: boolean) => void;
  onTrimModeChange: (value: TrimMode) => void;
}

export const OptimizationOptions: React.FC<OptimizationOptionsProps> = ({
  autoCrop,
  generateThumbnails,
  compress,
  trimMode,
  onAutoCropChange,
  onGenerateThumbnailsChange,
  onCompressChange,
  onTrimModeChange,
}) => {
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
      <Typography
        variant="subtitle2"
        sx={{
          mb: 2,
          color: '#0f172a',
          fontWeight: 700,
        }}
      >
        Optimization Options
      </Typography>
      <Stack spacing={2}>
        <FormControlLabel
          control={
            <Switch
              checked={autoCrop}
              onChange={(e) => onAutoCropChange(e.target.checked)}
              color="primary"
            />
          }
          label={
            <Box>
              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                Auto-crop to platform ratio
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Automatically crop video to match platform aspect ratio
              </Typography>
            </Box>
          }
        />

        <FormControlLabel
          control={
            <Switch
              checked={generateThumbnails}
              onChange={(e) => onGenerateThumbnailsChange(e.target.checked)}
              color="primary"
            />
          }
          label={
            <Box>
              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                Generate thumbnails
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Create thumbnail images for each platform
              </Typography>
            </Box>
          }
        />

        <FormControlLabel
          control={
            <Switch
              checked={compress}
              onChange={(e) => onCompressChange(e.target.checked)}
              color="primary"
            />
          }
          label={
            <Box>
              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                Compress for file size limits
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Automatically compress videos to meet platform file size requirements
              </Typography>
            </Box>
          }
        />

        <FormControl>
          <Typography variant="body2" sx={{ mb: 1, fontWeight: 500 }}>
            Trim Mode (if video exceeds duration)
          </Typography>
          <RadioGroup
            value={trimMode}
            onChange={(e) => onTrimModeChange(e.target.value as TrimMode)}
          >
            <FormControlLabel
              value="beginning"
              control={<Radio size="small" />}
              label={
                <Typography variant="body2">
                  Keep Beginning - Trim from the end
                </Typography>
              }
            />
            <FormControlLabel
              value="middle"
              control={<Radio size="small" />}
              label={
                <Typography variant="body2">
                  Keep Middle - Trim from both ends
                </Typography>
              }
            />
            <FormControlLabel
              value="end"
              control={<Radio size="small" />}
              label={
                <Typography variant="body2">
                  Keep End - Trim from the beginning
                </Typography>
              }
            />
          </RadioGroup>
        </FormControl>
      </Stack>
    </Paper>
  );
};
