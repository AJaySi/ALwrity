import React, { useRef } from 'react';
import { Box, Button, Typography, Stack } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import ImageIcon from '@mui/icons-material/Image';

interface ImageUploadProps {
  imagePreview: string | null;
  onImageSelect: (file: File | null) => void;
}

export const ImageUpload: React.FC<ImageUploadProps> = ({
  imagePreview,
  onImageSelect,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate image file
      if (!file.type.startsWith('image/')) {
        alert('Please select an image file');
        return;
      }
      if (file.size > 10 * 1024 * 1024) {
        alert('Image file must be less than 10MB');
        return;
      }
      onImageSelect(file);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleRemove = () => {
    onImageSelect(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <Box>
      <Typography
        variant="subtitle2"
        sx={{
          mb: 1,
          color: '#0f172a',
          fontWeight: 700,
        }}
      >
        Upload Photo
      </Typography>
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        style={{ display: 'none' }}
        onChange={handleFileSelect}
      />
      {imagePreview ? (
        <Box
          sx={{
            position: 'relative',
            borderRadius: 2,
            overflow: 'hidden',
            border: '2px solid #e2e8f0',
          }}
        >
          <img
            src={imagePreview}
            alt="Preview"
            style={{
              width: '100%',
              height: 'auto',
              maxHeight: 400,
              objectFit: 'contain',
              display: 'block',
            }}
          />
          <Button
            variant="outlined"
            color="error"
            size="small"
            onClick={handleRemove}
            sx={{
              position: 'absolute',
              top: 8,
              right: 8,
            }}
          >
            Remove
          </Button>
        </Box>
      ) : (
        <Box
          onClick={handleClick}
          sx={{
            border: '2px dashed #cbd5e1',
            borderRadius: 2,
            p: 4,
            textAlign: 'center',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            '&:hover': {
              borderColor: '#3b82f6',
              backgroundColor: '#f8fafc',
            },
          }}
        >
          <Stack spacing={2} alignItems="center">
            <ImageIcon sx={{ fontSize: 48, color: '#94a3b8' }} />
            <Typography variant="body2" color="text.secondary">
              Click to upload a photo
            </Typography>
            <Typography variant="caption" color="text.secondary">
              PNG, JPG up to 10MB
            </Typography>
          </Stack>
        </Box>
      )}
    </Box>
  );
};
