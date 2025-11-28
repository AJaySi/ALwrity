import React from 'react';
import {
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Typography,
  Chip,
  Stack,
} from '@mui/material';
import { Palette, LightMode, Style as StyleIcon, PhotoCamera } from '@mui/icons-material';

interface StyleSelectorProps {
  environment: string;
  backgroundStyle: string;
  lighting: string;
  style: string;
  onEnvironmentChange: (value: string) => void;
  onBackgroundStyleChange: (value: string) => void;
  onLightingChange: (value: string) => void;
  onStyleChange: (value: string) => void;
}

const ENVIRONMENTS = [
  { value: 'studio', label: 'Studio', icon: '🏛️', description: 'Clean, professional studio photography' },
  { value: 'lifestyle', label: 'Lifestyle', icon: '🏠', description: 'Product in use, relatable settings' },
  { value: 'outdoor', label: 'Outdoor', icon: '🌲', description: 'Natural outdoor environments' },
  { value: 'minimalist', label: 'Minimalist', icon: '✨', description: 'Simple, clean aesthetic' },
  { value: 'luxury', label: 'Luxury', icon: '💎', description: 'Premium, high-end feel' },
];

const BACKGROUND_STYLES = [
  { value: 'white', label: 'White Background', description: 'Clean white backdrop' },
  { value: 'transparent', label: 'Transparent', description: 'Isolated product' },
  { value: 'lifestyle', label: 'Lifestyle', description: 'Contextual environment' },
  { value: 'branded', label: 'Branded', description: 'Brand colors/background' },
];

const LIGHTING_STYLES = [
  { value: 'natural', label: 'Natural', description: 'Soft, balanced lighting' },
  { value: 'studio', label: 'Studio', description: 'Even, professional lighting' },
  { value: 'dramatic', label: 'Dramatic', description: 'High contrast, artistic' },
  { value: 'soft', label: 'Soft', description: 'Gentle, diffused lighting' },
];

const IMAGE_STYLES = [
  { value: 'photorealistic', label: 'Photorealistic', description: 'Highly detailed, professional' },
  { value: 'minimalist', label: 'Minimalist', description: 'Clean, simple composition' },
  { value: 'luxury', label: 'Luxury', description: 'Sophisticated, refined' },
  { value: 'technical', label: 'Technical', description: 'Feature-focused documentation' },
];

export const StyleSelector: React.FC<StyleSelectorProps> = ({
  environment,
  backgroundStyle,
  lighting,
  style,
  onEnvironmentChange,
  onBackgroundStyleChange,
  onLightingChange,
  onStyleChange,
}) => {
  return (
    <Stack spacing={3}>
      <Box display="flex" alignItems="center" gap={1}>
        <StyleIcon sx={{ color: '#c4b5fd' }} />
        <Typography variant="h6" fontWeight={600}>
          Style & Environment
        </Typography>
      </Box>

      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Environment</InputLabel>
            <Select
              value={environment}
              label="Environment"
              onChange={(e) => onEnvironmentChange(e.target.value)}
              sx={{
                '& .MuiOutlinedInput-root': {
                  background: 'rgba(255, 255, 255, 0.05)',
                },
              }}
            >
              {ENVIRONMENTS.map((env) => (
                <MenuItem key={env.value} value={env.value}>
                  <Box>
                    <Typography variant="body1">
                      {env.icon} {env.label}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {env.description}
                    </Typography>
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Background Style</InputLabel>
            <Select
              value={backgroundStyle}
              label="Background Style"
              onChange={(e) => onBackgroundStyleChange(e.target.value)}
              sx={{
                '& .MuiOutlinedInput-root': {
                  background: 'rgba(255, 255, 255, 0.05)',
                },
              }}
            >
              {BACKGROUND_STYLES.map((bg) => (
                <MenuItem key={bg.value} value={bg.value}>
                  <Box>
                    <Typography variant="body1">{bg.label}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {bg.description}
                    </Typography>
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Lighting</InputLabel>
            <Select
              value={lighting}
              label="Lighting"
              onChange={(e) => onLightingChange(e.target.value)}
              sx={{
                '& .MuiOutlinedInput-root': {
                  background: 'rgba(255, 255, 255, 0.05)',
                },
              }}
            >
              {LIGHTING_STYLES.map((light) => (
                <MenuItem key={light.value} value={light.value}>
                  <Box>
                    <Typography variant="body1">{light.label}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {light.description}
                    </Typography>
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Image Style</InputLabel>
            <Select
              value={style}
              label="Image Style"
              onChange={(e) => onStyleChange(e.target.value)}
              sx={{
                '& .MuiOutlinedInput-root': {
                  background: 'rgba(255, 255, 255, 0.05)',
                },
              }}
            >
              {IMAGE_STYLES.map((imgStyle) => (
                <MenuItem key={imgStyle.value} value={imgStyle.value}>
                  <Box>
                    <Typography variant="body1">{imgStyle.label}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {imgStyle.description}
                    </Typography>
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
      </Grid>
    </Stack>
  );
};

