import React, { useRef } from 'react';
import { Box, Button, Typography, Stack } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
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
      if (file.size > 50 * 1024 * 1024) {
        alert('Audio file must be less than 50MB');
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
        Upload Audio
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
            border: '2px solid #e2e8f0',
            borderRadius: 2,
            p: 2,
          }}
        >
          <Stack direction="row" spacing={2} alignItems="center">
            <AudioFileIcon sx={{ color: '#3b82f6' }} />
            <Box sx={{ flex: 1 }}>
              <Typography variant="body2" fontWeight={600}>
                Audio file selected
              </Typography>
              <audio
                src={audioPreview}
                controls
                style={{ width: '100%', marginTop: 8 }}
              />
            </Box>
            <Button
              variant="outlined"
              color="error"
              size="small"
              onClick={handleRemove}
            >
              Remove
            </Button>
          </Stack>
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
            <AudioFileIcon sx={{ fontSize: 48, color: '#94a3b8' }} />
            <Typography variant="body2" color="text.secondary">
              Click to upload audio
            </Typography>
            <Typography variant="caption" color="text.secondary">
              MP3, WAV up to 50MB (max 10 minutes)
            </Typography>
          </Stack>
        </Box>
      )}
    </Box>
  );
};
