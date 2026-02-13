/**
 * Scene Preview Modal
 * 
 * Shows a preview of scene image and audio with playback controls.
 */

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  IconButton,
  Box,
  Typography,
  Stack,
  CircularProgress,
} from '@mui/material';
import {
  Close as CloseIcon,
  PlayArrow,
  Pause,
  VolumeUp,
} from '@mui/icons-material';
import { fetchMediaBlobUrl } from '../../../utils/fetchMediaBlobUrl';

interface ScenePreviewModalProps {
  open: boolean;
  onClose: () => void;
  sceneTitle: string;
  sceneNumber: number;
  imageUrl?: string | null;
  audioUrl?: string | null;
}

export const ScenePreviewModal: React.FC<ScenePreviewModalProps> = ({
  open,
  onClose,
  sceneTitle,
  sceneNumber,
  imageUrl,
  audioUrl,
}) => {
  const [imageBlobUrl, setImageBlobUrl] = useState<string | null>(null);
  const [audioBlobUrl, setAudioBlobUrl] = useState<string | null>(null);
  const [imageLoading, setImageLoading] = useState(false);
  const [audioLoading, setAudioLoading] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioElement, setAudioElement] = useState<HTMLAudioElement | null>(null);

  // Load image blob
  useEffect(() => {
    if (!imageUrl || !open) {
      setImageBlobUrl(null);
      return;
    }

    setImageLoading(true);
    fetchMediaBlobUrl(imageUrl)
      .then(setImageBlobUrl)
      .catch(console.error)
      .finally(() => setImageLoading(false));

    return () => {
      if (imageBlobUrl?.startsWith('blob:')) {
        URL.revokeObjectURL(imageBlobUrl);
      }
    };
  }, [imageUrl, open, imageBlobUrl]);

  // Load audio blob
  useEffect(() => {
    if (!audioUrl || !open) {
      setAudioBlobUrl(null);
      return;
    }

    setAudioLoading(true);
    fetchMediaBlobUrl(audioUrl)
      .then(setAudioBlobUrl)
      .catch(console.error)
      .finally(() => setAudioLoading(false));

    return () => {
      if (audioBlobUrl?.startsWith('blob:')) {
        URL.revokeObjectURL(audioBlobUrl);
      }
    };
  }, [audioUrl, open, audioBlobUrl]);

  // Create audio element
  useEffect(() => {
    if (audioBlobUrl) {
      const audio = new Audio(audioBlobUrl);
      audio.addEventListener('ended', () => setIsPlaying(false));
      setAudioElement(audio);
      return () => {
        audio.pause();
        audio.remove();
      };
    }
  }, [audioBlobUrl]);

  const togglePlayPause = () => {
    if (!audioElement) return;

    if (isPlaying) {
      audioElement.pause();
    } else {
      audioElement.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleClose = () => {
    if (audioElement) {
      audioElement.pause();
      setIsPlaying(false);
    }
    onClose();
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 3,
          bgcolor: '#f8fafc',
        },
      }}
    >
      <DialogTitle>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 700, color: '#1e293b' }}>
              Scene {sceneNumber} Preview
            </Typography>
            <Typography variant="body2" sx={{ color: '#64748b', mt: 0.5 }}>
              {sceneTitle}
            </Typography>
          </Box>
          <IconButton onClick={handleClose} size="small">
            <CloseIcon />
          </IconButton>
        </Stack>
      </DialogTitle>

      <DialogContent>
        <Stack spacing={3}>
          {/* Image Preview */}
          {imageUrl && (
            <Box>
              <Typography variant="subtitle2" sx={{ mb: 1.5, fontWeight: 600, color: '#475569' }}>
                🖼️ Scene Image
              </Typography>
              {imageLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                  <CircularProgress />
                </Box>
              ) : imageBlobUrl ? (
                <Box
                  component="img"
                  src={imageBlobUrl}
                  alt={sceneTitle}
                  sx={{
                    width: '100%',
                    height: 'auto',
                    borderRadius: 2,
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                  }}
                />
              ) : (
                <Typography variant="body2" color="text.secondary">
                  Failed to load image
                </Typography>
              )}
            </Box>
          )}

          {/* Audio Preview */}
          {audioUrl && (
            <Box>
              <Typography variant="subtitle2" sx={{ mb: 1.5, fontWeight: 600, color: '#475569' }}>
                🎤 Scene Audio
              </Typography>
              {audioLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
                  <CircularProgress size={24} />
                </Box>
              ) : audioBlobUrl ? (
                <Box
                  sx={{
                    p: 3,
                    bgcolor: 'white',
                    borderRadius: 2,
                    border: '2px solid #e2e8f0',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 2,
                  }}
                >
                  <IconButton
                    onClick={togglePlayPause}
                    disabled={!audioElement}
                    sx={{
                      bgcolor: '#667eea',
                      color: 'white',
                      '&:hover': {
                        bgcolor: '#5568d3',
                      },
                      '&:disabled': {
                        bgcolor: '#cbd5e1',
                      },
                    }}
                  >
                    {isPlaying ? <Pause /> : <PlayArrow />}
                  </IconButton>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#1e293b' }}>
                      {isPlaying ? 'Playing...' : 'Click to play audio'}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#64748b' }}>
                      Scene narration audio
                    </Typography>
                  </Box>
                  <VolumeUp sx={{ color: '#94a3b8' }} />
                </Box>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  Failed to load audio
                </Typography>
              )}
            </Box>
          )}

          {!imageUrl && !audioUrl && (
            <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', p: 3 }}>
              No assets available for preview
            </Typography>
          )}
        </Stack>
      </DialogContent>
    </Dialog>
  );
};

