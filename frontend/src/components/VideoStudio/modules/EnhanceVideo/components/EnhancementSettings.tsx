import React from 'react';
import { Box, Stack, Typography, FormControl, InputLabel, Select, MenuItem, Chip, Paper } from '@mui/material';
import HighQualityIcon from '@mui/icons-material/HighQuality';
import type { EnhancementResolution, EnhancementType } from '../hooks/useEnhanceVideo';

interface EnhancementSettingsProps {
  targetResolution: EnhancementResolution;
  enhancementType: EnhancementType;
  costHint: string;
  onTargetResolutionChange: (resolution: EnhancementResolution) => void;
  onEnhancementTypeChange: (type: EnhancementType) => void;
}

export const EnhancementSettings: React.FC<EnhancementSettingsProps> = ({
  targetResolution,
  enhancementType,
  costHint,
  onTargetResolutionChange,
  onEnhancementTypeChange,
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
      <Stack spacing={3}>
        <Box>
          <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
            <HighQualityIcon sx={{ color: '#3b82f6' }} />
            <Typography
              variant="subtitle2"
              sx={{
                color: '#0f172a',
                fontWeight: 700,
              }}
            >
              Enhancement Settings
            </Typography>
          </Stack>
        </Box>

        <Box>
          <Typography
            variant="subtitle2"
            sx={{
              mb: 1,
              color: '#0f172a',
              fontWeight: 600,
            }}
          >
            Enhancement Type
          </Typography>
          <FormControl fullWidth>
            <Select
              value={enhancementType}
              onChange={(e) => onEnhancementTypeChange(e.target.value as EnhancementType)}
              sx={{
                backgroundColor: '#fff',
                '& .MuiOutlinedInput-notchedOutline': {
                  borderColor: '#e2e8f0',
                },
              }}
            >
              <MenuItem value="upscale">Upscale (FlashVSR)</MenuItem>
              {/* Future enhancement types */}
              {/* <MenuItem value="stabilize">Stabilize</MenuItem>
              <MenuItem value="colorize">Colorize</MenuItem> */}
            </Select>
          </FormControl>
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            FlashVSR upscales videos with temporal consistency and detail reconstruction
          </Typography>
        </Box>

      <Box>
        <Typography
          variant="subtitle2"
          sx={{
            mb: 1,
            color: '#0f172a',
            fontWeight: 700,
          }}
        >
          Target Resolution
        </Typography>
        <FormControl fullWidth>
          <InputLabel>Resolution</InputLabel>
          <Select
            value={targetResolution}
            onChange={(e) => onTargetResolutionChange(e.target.value as EnhancementResolution)}
            label="Resolution"
            sx={{
              backgroundColor: '#fff',
              '& .MuiOutlinedInput-notchedOutline': {
                borderColor: '#e2e8f0',
              },
            }}
          >
            <MenuItem value="720p">720p HD ($0.06/5s)</MenuItem>
            <MenuItem value="1080p">1080p Full HD ($0.09/5s)</MenuItem>
            <MenuItem value="2k">2K ($0.12/5s)</MenuItem>
            <MenuItem value="4k">4K Ultra HD ($0.16/5s)</MenuItem>
          </Select>
        </FormControl>
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            Higher resolution = better quality but higher cost
          </Typography>
        </Box>

        <Box
          sx={{
            p: 2,
            borderRadius: 2,
            backgroundColor: '#f1f5f9',
            border: '1px solid #e2e8f0',
          }}
        >
          <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
            <Typography variant="body2" sx={{ fontWeight: 600, color: '#0f172a' }}>
              Estimated Cost:
            </Typography>
            <Chip
              label={costHint}
              size="small"
              sx={{
                backgroundColor: '#3b82f6',
                color: '#fff',
                fontWeight: 600,
              }}
            />
          </Stack>
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
            FlashVSR pricing: $0.012-$0.032/second (based on resolution)
          </Typography>
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
            Minimum charge: 5 seconds | Maximum: 10 minutes (600 seconds)
          </Typography>
        </Box>
      </Stack>
    </Paper>
  );
};
