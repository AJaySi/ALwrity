import React, { useRef } from 'react';
import { Box, Button, Typography, Stack, Chip } from '@mui/material';
import ImageIcon from '@mui/icons-material/Image';
import CloseIcon from '@mui/icons-material/Close';

interface BackgroundImageUploadProps {
  imagePreview: string | null;
  onImageSelect: (file: File | null) => void;
}

export const BackgroundImageUpload: React.FC<BackgroundImageUploadProps> = ({
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
      <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
        <Typography
          variant="subtitle2"
          sx={{
            color: '#0f172a',
            fontWeight: 700,
          }}
        >
          Background Image (Optional)
        </Typography>
        <Chip label="Optional" size="small" color="info" />
      </Stack>
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
            backgroundColor: '#f8fafc',
          }}
        >
          <Box
            component="img"
            src={imagePreview}
            alt="Background image"
            sx={{
              width: '100%',
              maxHeight: 300,
              objectFit: 'contain',
              display: 'block',
            }}
          />
          <Button
            variant="outlined"
            color="error"
            size="small"
            onClick={handleRemove}
            startIcon={<CloseIcon />}
            sx={{
              position: 'absolute',
              top: 8,
              right: 8,
              backgroundColor: 'rgba(255, 255, 255, 0.9)',
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
            p: 3,
            textAlign: 'center',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            '&:hover': {
              borderColor: '#3b82f6',
              backgroundColor: '#f8fafc',
            },
          }}
        >
          <Stack spacing={1.5} alignItems="center">
            <ImageIcon sx={{ fontSize: 40, color: '#94a3b8' }} />
            <Typography variant="body2" color="text.secondary">
              Click to upload background image
            </Typography>
            <Typography variant="caption" color="text.secondary">
              JPG, PNG up to 10MB
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ fontStyle: 'italic' }}>
              Leave empty to remove background (transparent)
            </Typography>
          </Stack>
        </Box>
      )}
    </Box>
  );
};
