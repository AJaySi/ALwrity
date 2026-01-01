import React from 'react';
import { Box, Paper, Stack, Typography, FormControl, Select, MenuItem, Chip, Divider } from '@mui/material';
import { FaceSwapModel } from '../hooks/useFaceSwap';

interface ModelSelectorProps {
  selectedModel: FaceSwapModel;
  onModelChange: (model: FaceSwapModel) => void;
}

const MODEL_INFO = {
  mocha: {
    name: 'MoCha',
    tagline: 'Character Replacement with Motion Preservation',
    description: 'Advanced character replacement that preserves motion, emotion, and camera perspective. Perfect for film, advertising, and creative character transformation.',
    pricing: '$0.04/s (480p) or $0.08/s (720p)',
    maxLength: '120 seconds',
    features: ['Motion preservation', 'Expression transfer', 'Prompt guidance', 'Seed control', 'High quality output'],
  },
  'video-face-swap': {
    name: 'Video Face Swap',
    tagline: 'Simple Face Swap with Multi-Face Support',
    description: 'Affordable face swap with gender filtering and face index selection. Ideal for content creation, memes, and social media.',
    pricing: '$0.01/s',
    maxLength: '10 minutes (600 seconds)',
    features: ['Multi-face support', 'Gender filter', 'Face index selection', 'Affordable pricing', 'Long video support'],
  },
};

export const ModelSelector: React.FC<ModelSelectorProps> = ({ selectedModel, onModelChange }) => {
  const selectedInfo = MODEL_INFO[selectedModel];

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
        AI Model
      </Typography>

      <FormControl fullWidth sx={{ mb: 2 }}>
        <Select
          value={selectedModel}
          onChange={(e) => onModelChange(e.target.value as FaceSwapModel)}
          sx={{
            '& .MuiSelect-select': {
              py: 1.5,
            },
          }}
        >
          <MenuItem value="mocha">
            <Stack direction="row" spacing={1} alignItems="center">
              <Typography>MoCha</Typography>
              <Chip label="Premium" size="small" color="primary" />
            </Stack>
          </MenuItem>
          <MenuItem value="video-face-swap">
            <Stack direction="row" spacing={1} alignItems="center">
              <Typography>Video Face Swap</Typography>
              <Chip label="Affordable" size="small" color="success" />
            </Stack>
          </MenuItem>
        </Select>
      </FormControl>

      <Box
        sx={{
          p: 2,
          borderRadius: 1,
          backgroundColor: '#f8fafc',
          border: '1px solid #e2e8f0',
        }}
      >
        <Typography variant="body2" sx={{ fontWeight: 600, mb: 1, color: '#0f172a' }}>
          {selectedInfo.tagline}
        </Typography>
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1.5 }}>
          {selectedInfo.description}
        </Typography>

        <Divider sx={{ my: 1.5 }} />

        <Stack spacing={1}>
          <Stack direction="row" justifyContent="space-between">
            <Typography variant="caption" color="text.secondary">
              Pricing:
            </Typography>
            <Typography variant="caption" sx={{ fontWeight: 600 }}>
              {selectedInfo.pricing}
            </Typography>
          </Stack>
          <Stack direction="row" justifyContent="space-between">
            <Typography variant="caption" color="text.secondary">
              Max Length:
            </Typography>
            <Typography variant="caption" sx={{ fontWeight: 600 }}>
              {selectedInfo.maxLength}
            </Typography>
          </Stack>
        </Stack>

        <Divider sx={{ my: 1.5 }} />

        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
          Features:
        </Typography>
        <Stack direction="row" flexWrap="wrap" gap={0.5}>
          {selectedInfo.features.map((feature, idx) => (
            <Chip
              key={idx}
              label={feature}
              size="small"
              variant="outlined"
              sx={{
                fontSize: '0.7rem',
                height: '20px',
                borderColor: '#cbd5e1',
                color: '#475569',
              }}
            />
          ))}
        </Stack>
      </Box>
    </Paper>
  );
};
