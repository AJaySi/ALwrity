import React from 'react';
import { Box, TextField, Stack, Typography, Tooltip, IconButton } from '@mui/material';
import { Inventory2 as ProductIcon, Info as InfoIcon } from '@mui/icons-material';
import { getTooltipText } from '../../../utils/terminology';

interface ProductInfoFormProps {
  productName: string;
  productDescription: string;
  onProductNameChange: (value: string) => void;
  onProductDescriptionChange: (value: string) => void;
}

export const ProductInfoForm: React.FC<ProductInfoFormProps> = ({
  productName,
  productDescription,
  onProductNameChange,
  onProductDescriptionChange,
}) => {
  return (
    <Stack spacing={3}>
      <Box display="flex" alignItems="center" gap={1}>
        <ProductIcon sx={{ color: '#c4b5fd' }} />
        <Typography variant="h6" fontWeight={600}>
          Product Information
        </Typography>
      </Box>

      <TextField
        label="Product Name"
        value={productName}
        onChange={(e) => onProductNameChange(e.target.value)}
        fullWidth
        required
        placeholder="e.g., Premium Wireless Headphones"
        helperText="Enter the name of your product"
        InputProps={{
          endAdornment: (
            <Tooltip title="The name of your product as it will appear in photos and marketing materials">
              <IconButton size="small" edge="end">
                <InfoIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          ),
        }}
        sx={{
          '& .MuiOutlinedInput-root': {
            background: 'rgba(255, 255, 255, 0.05)',
            '&:hover': {
              background: 'rgba(255, 255, 255, 0.08)',
            },
          },
        }}
      />

      <TextField
        label="Product Description"
        value={productDescription}
        onChange={(e) => onProductDescriptionChange(e.target.value)}
        fullWidth
        required
        multiline
        rows={4}
        placeholder="Describe your product: features, benefits, target audience..."
        helperText="Provide details about your product to help AI generate accurate images"
        InputProps={{
          endAdornment: (
            <Tooltip title="Describe your product's key features, benefits, and who it's for. The more details you provide, the better the AI can create accurate product photos.">
              <IconButton size="small" edge="end" sx={{ alignSelf: 'flex-start', mt: 1 }}>
                <InfoIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          ),
        }}
        sx={{
          '& .MuiOutlinedInput-root': {
            background: 'rgba(255, 255, 255, 0.05)',
            '&:hover': {
              background: 'rgba(255, 255, 255, 0.08)',
            },
          },
        }}
      />
    </Stack>
  );
};

