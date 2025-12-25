import React from 'react';
import {
  Box,
  Button,
  Typography,
  LinearProgress,
  CircularProgress,
} from '@mui/material';
import { Image as ImageIcon, VolumeUp } from '@mui/icons-material';
import { Scene } from '../../../../services/youtubeApi';
import { AudioGenerationSettings } from '../../../../components/shared/AudioSettingsModal';
import { YouTubeImageGenerationSettings } from '../../shared/YouTubeImageGenerationModal';

interface GenerationButtonsProps {
  scene: Scene;
  isEditing: boolean;
  loading: boolean;
  onGenerateImage?: (scene: Scene, imageSettings?: YouTubeImageGenerationSettings) => Promise<void>;
  generatingImage?: boolean;
  onGenerateAudio?: (scene: Scene, audioSettings?: AudioGenerationSettings) => Promise<void>;
  generatingAudio?: boolean;
  imageGenerationStatus?: string;
  imageGenerationProgress?: number;
  audioGenerationStatus?: string;
  audioGenerationProgress?: number;
  onAudioModalOpen: () => void;
  onImageModalOpen: () => void;
}

export const GenerationButtons: React.FC<GenerationButtonsProps> = ({
  scene,
  isEditing,
  loading,
  onGenerateImage,
  generatingImage = false,
  onGenerateAudio,
  generatingAudio = false,
  imageGenerationStatus = '',
  imageGenerationProgress = 0,
  audioGenerationStatus = '',
  audioGenerationProgress = 0,
  onAudioModalOpen,
  onImageModalOpen,
}) => {
  if (isEditing) return null;

  return (
    <>
      {/* Audio Generation Button */}
      {onGenerateAudio && (
        <Box sx={{ mt: 2 }}>
          <Button
            variant={scene.audioUrl ? 'outlined' : 'contained'}
            color="primary"
            startIcon={
              generatingAudio ? (
                <CircularProgress size={16} sx={{ color: 'inherit' }} />
              ) : (
                <VolumeUp />
              )
            }
            onClick={onAudioModalOpen}
            disabled={generatingAudio || loading}
            sx={{
              textTransform: 'none',
              fontWeight: 600,
              py: 1.5,
              width: '100%',
            }}
          >
            {generatingAudio
              ? 'Generating Audio...'
              : scene.audioUrl
              ? 'Regenerate Audio'
              : 'Generate Audio'}
          </Button>
          {audioGenerationStatus && (
            <Box sx={{ mt: 1.5 }}>
              <Typography
                variant="caption"
                sx={{
                  display: 'block',
                  mb: 0.5,
                  color: audioGenerationStatus.startsWith('Error') ? 'error.main' : 'text.secondary',
                  fontSize: '0.75rem',
                }}
              >
                {audioGenerationStatus}
              </Typography>
              {audioGenerationProgress > 0 && audioGenerationProgress < 100 && (
                <LinearProgress
                  variant="determinate"
                  value={audioGenerationProgress}
                  sx={{
                    height: 4,
                    borderRadius: 2,
                    bgcolor: '#e5e7eb',
                  }}
                />
              )}
            </Box>
          )}
        </Box>
      )}

      {/* Image Generation Button */}
      {onGenerateImage && (
        <Box sx={{ mt: 2 }}>
          <Button
            variant={scene.imageUrl ? 'outlined' : 'contained'}
            color="primary"
            startIcon={
              generatingImage ? (
                <CircularProgress size={16} sx={{ color: 'inherit' }} />
              ) : (
                <ImageIcon />
              )
            }
            onClick={onImageModalOpen}
            disabled={generatingImage || loading}
            fullWidth
            sx={{
              textTransform: 'none',
              fontWeight: 600,
              py: 1.5,
            }}
          >
            {generatingImage
              ? 'Generating Image...'
              : scene.imageUrl
              ? 'Regenerate Image'
              : 'Generate Image'}
          </Button>
          {imageGenerationStatus && (
            <Box sx={{ mt: 1.5 }}>
              <Typography
                variant="caption"
                sx={{
                  display: 'block',
                  mb: 0.5,
                  color: imageGenerationStatus.startsWith('Error') ? 'error.main' : 'text.secondary',
                  fontSize: '0.75rem',
                }}
              >
                {imageGenerationStatus}
              </Typography>
              {imageGenerationProgress > 0 && imageGenerationProgress < 100 && (
                <LinearProgress
                  variant="determinate"
                  value={imageGenerationProgress}
                  sx={{
                    height: 4,
                    borderRadius: 2,
                    bgcolor: '#e5e7eb',
                  }}
                />
              )}
            </Box>
          )}
        </Box>
      )}
    </>
  );
};
