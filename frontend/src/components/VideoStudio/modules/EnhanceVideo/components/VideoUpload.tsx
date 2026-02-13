import React, { useRef } from 'react';
import { Box, Button, Typography, Stack } from '@mui/material';
import VideocamIcon from '@mui/icons-material/Videocam';

interface VideoUploadProps {
  videoPreview: string | null;
  onVideoSelect: (file: File | null) => void;
}

export const VideoUpload: React.FC<VideoUploadProps> = ({
  videoPreview,
  onVideoSelect,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate video file
      if (!file.type.startsWith('video/')) {
        alert('Please select a video file');
        return;
      }
      if (file.size > 500 * 1024 * 1024) {
        alert('Video file must be less than 500MB');
        return;
      }
      onVideoSelect(file);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleRemove = () => {
    onVideoSelect(null);
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
        Upload Video
      </Typography>
      <input
        ref={fileInputRef}
        type="file"
        accept="video/*"
        style={{ display: 'none' }}
        onChange={handleFileSelect}
      />
      {videoPreview ? (
        <Box
          sx={{
            position: 'relative',
            borderRadius: 2,
            overflow: 'hidden',
            border: '2px solid #e2e8f0',
            backgroundColor: '#000',
          }}
        >
          <video
            src={videoPreview}
            controls
            style={{
              width: '100%',
              maxHeight: 400,
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
            <VideocamIcon sx={{ fontSize: 48, color: '#94a3b8' }} />
            <Typography variant="body2" color="text.secondary">
              Click to upload a video
            </Typography>
            <Typography variant="caption" color="text.secondary">
              MP4, WebM up to 500MB (max 10 minutes)
            </Typography>
          </Stack>
        </Box>
      )}
    </Box>
  );
};
