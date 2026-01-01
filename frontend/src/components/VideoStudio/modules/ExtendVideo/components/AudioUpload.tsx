import React, { useRef } from 'react';
import { Box, Button, Typography, Stack } from '@mui/material';
import AudioFileIcon from '@mui/icons-material/AudioFile';

interface AudioUploadProps {
  audioPreview: string | null;
  onAudioSelect: (file: File | null) => void;
}

export const AudioUpload: React.FC<AudioUploadProps> = ({
  audioPreview,
  onAudioSelect,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate audio file
      if (!file.type.startsWith('audio/')) {
        alert('Please select an audio file');
        return;
      }
      // Validate audio file size (max 15MB per WAN 2.5 documentation)
      if (file.size > 15 * 1024 * 1024) {
        alert('Audio file must be less than 15MB (per WAN 2.5 requirements)');
        return;
      }
      onAudioSelect(file);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleRemove = () => {
    onAudioSelect(null);
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
        Optional Audio Guide
      </Typography>
      <input
        ref={fileInputRef}
        type="file"
        accept="audio/*"
        style={{ display: 'none' }}
        onChange={handleFileSelect}
      />
      {audioPreview ? (
        <Box
          sx={{
            position: 'relative',
            borderRadius: 2,
            overflow: 'hidden',
            border: '2px solid #e2e8f0',
            backgroundColor: '#f8fafc',
            p: 2,
          }}
        >
          <audio
            src={audioPreview}
            controls
            style={{
              width: '100%',
            }}
          />
          <Button
            variant="outlined"
            color="error"
            size="small"
            onClick={handleRemove}
            sx={{
              mt: 1,
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
          <Stack spacing={1} alignItems="center">
            <AudioFileIcon sx={{ fontSize: 36, color: '#94a3b8' }} />
            <Typography variant="body2" color="text.secondary">
              Click to upload audio (optional)
            </Typography>
            <Typography variant="caption" color="text.secondary">
              MP3, WAV up to 15MB (3-30s recommended)
            </Typography>
          </Stack>
        </Box>
      )}
    </Box>
  );
};
