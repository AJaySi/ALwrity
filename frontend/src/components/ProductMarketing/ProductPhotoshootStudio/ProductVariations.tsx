import React from 'react';
import {
  Box,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Typography,
  Stack,
} from '@mui/material';
import { AspectRatio, Colorize } from '@mui/icons-material';

interface ProductVariationsProps {
  productVariant: string;
  angle: string;
  resolution: string;
  numVariations: number;
  onProductVariantChange: (value: string) => void;
  onAngleChange: (value: string) => void;
  onResolutionChange: (value: string) => void;
  onNumVariationsChange: (value: number) => void;
}

const ANGLES = [
  { value: 'front', label: 'Front View', description: 'Centered composition' },
  { value: 'side', label: 'Side View', description: 'Profile showing depth' },
  { value: 'top', label: 'Top Down', description: 'Flat lay style' },
  { value: '360', label: '3/4 Angle', description: 'Showing multiple sides' },
];

const RESOLUTIONS = [
  { value: '1024x1024', label: 'Square (1024×1024)', description: 'Instagram, social media' },
  { value: '1280x720', label: 'Landscape (1280×720)', description: 'Website, banners' },
  { value: '720x1280', label: 'Portrait (720×1280)', description: 'Mobile, stories' },
  { value: 'square', label: 'Square Default', description: '1:1 aspect ratio' },
  { value: 'landscape', label: 'Landscape Default', description: '16:9 aspect ratio' },
  { value: 'portrait', label: 'Portrait Default', description: '9:16 aspect ratio' },
];

export const ProductVariations: React.FC<ProductVariationsProps> = ({
  productVariant,
  angle,
  resolution,
  numVariations,
  onProductVariantChange,
  onAngleChange,
  onResolutionChange,
  onNumVariationsChange,
}) => {
  return (
    <Stack spacing={3}>
      <Box display="flex" alignItems="center" gap={1}>
        <Colorize sx={{ color: '#c4b5fd' }} />
        <Typography variant="h6" fontWeight={600}>
          Product Variations & Settings
        </Typography>
      </Box>

      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <TextField
            label="Product Variant (Optional)"
            value={productVariant}
            onChange={(e) => onProductVariantChange(e.target.value)}
            fullWidth
            placeholder="e.g., Black, Large, Pro Model"
            helperText="Color, size, model variant, etc."
            sx={{
              '& .MuiOutlinedInput-root': {
                background: 'rgba(255, 255, 255, 0.05)',
                '&:hover': {
                  background: 'rgba(255, 255, 255, 0.08)',
                },
              },
            }}
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Product Angle</InputLabel>
            <Select
              value={angle}
              label="Product Angle"
              onChange={(e) => onAngleChange(e.target.value)}
              sx={{
                '& .MuiOutlinedInput-root': {
                  background: 'rgba(255, 255, 255, 0.05)',
                },
              }}
            >
              <MenuItem value="">
                <em>Default (Auto)</em>
              </MenuItem>
              {ANGLES.map((ang) => (
                <MenuItem key={ang.value} value={ang.value}>
                  <Box>
                    <Typography variant="body1">{ang.label}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {ang.description}
                    </Typography>
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Resolution</InputLabel>
            <Select
              value={resolution}
              label="Resolution"
              onChange={(e) => onResolutionChange(e.target.value)}
              sx={{
                '& .MuiOutlinedInput-root': {
                  background: 'rgba(255, 255, 255, 0.05)',
                },
              }}
            >
              {RESOLUTIONS.map((res) => (
                <MenuItem key={res.value} value={res.value}>
                  <Box>
                    <Typography variant="body1">{res.label}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {res.description}
                    </Typography>
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Number of Variations</InputLabel>
            <Select
              value={numVariations}
              label="Number of Variations"
              onChange={(e) => onNumVariationsChange(Number(e.target.value))}
              sx={{
                '& .MuiOutlinedInput-root': {
                  background: 'rgba(255, 255, 255, 0.05)',
                },
              }}
            >
              {[1, 2, 3, 4, 5].map((num) => (
                <MenuItem key={num} value={num}>
                  {num} {num === 1 ? 'variation' : 'variations'}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
      </Grid>
    </Stack>
  );
};

