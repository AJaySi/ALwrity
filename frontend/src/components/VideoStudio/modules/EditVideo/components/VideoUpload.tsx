import React, { useRef, useState, useCallback } from 'react';
import { Box, Typography, Paper, Stack, IconButton } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import CloseIcon from '@mui/icons-material/Close';

interface VideoUploadProps {
  videoPreview: string | null;
  videoDuration: number;
  onVideoSelect: (file: File | null) => void;
}

export const VideoUpload: React.FC<VideoUploadProps> = ({
  videoPreview,
  videoDuration,
  onVideoSelect,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragActive, setIsDragActive] = useState(false);

  const handleFileSelect = (file: File) => {
    if (!file.type.startsWith('video/')) {
      alert('Please select a video file');
      return;
    }
    if (file.size > 500 * 1024 * 1024) {
      alert('Video file must be less than 500MB');
      return;
    }
    onVideoSelect(file);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation();
    onVideoSelect(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragActive(false);

      const file = e.dataTransfer.files?.[0];
      if (file) {
        handleFileSelect(file);
      }
    },
    [handleFileSelect]
  );

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
        Source Video
      </Typography>

      <input
        ref={fileInputRef}
        type="file"
        accept="video/*"
        style={{ display: 'none' }}
        onChange={handleInputChange}
      />

      {videoPreview ? (
        <Box sx={{ position: 'relative' }}>
          <video
            src={videoPreview}
            controls
            style={{
              width: '100%',
              maxHeight: '300px',
              borderRadius: '8px',
              objectFit: 'contain',
              backgroundColor: '#000',
            }}
          />
          <IconButton
            onClick={handleClear}
            sx={{
              position: 'absolute',
              top: 8,
              right: 8,
              backgroundColor: 'rgba(0, 0, 0, 0.6)',
              color: '#fff',
              '&:hover': {
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
              },
            }}
            size="small"
          >
            <CloseIcon fontSize="small" />
          </IconButton>
          <Typography
            variant="caption"
            sx={{
              display: 'block',
              mt: 1,
              color: '#64748b',
              textAlign: 'center',
            }}
          >
            Duration: {videoDuration.toFixed(1)}s
          </Typography>
        </Box>
      ) : (
        <Box
          onClick={handleClick}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          sx={{
            p: 4,
            borderRadius: 2,
            border: '2px dashed',
            borderColor: isDragActive ? '#3b82f6' : '#e2e8f0',
            backgroundColor: isDragActive ? '#eff6ff' : '#f8fafc',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            '&:hover': {
              borderColor: '#3b82f6',
              backgroundColor: '#eff6ff',
            },
          }}
        >
          <Stack spacing={2} alignItems="center">
            <CloudUploadIcon sx={{ fontSize: 48, color: '#94a3b8' }} />
            <Typography variant="body2" color="text.secondary" textAlign="center">
              {isDragActive
                ? 'Drop the video here...'
                : 'Drag and drop a video file, or click to select'}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Supported: MP4, MOV, AVI, WebM, MKV
            </Typography>
          </Stack>
        </Box>
      )}
    </Paper>
  );
};
