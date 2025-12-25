import React from 'react';
import {
  Alert,
  Typography,
} from '@mui/material';
import { Info } from '@mui/icons-material';
import { Scene } from '../../../../services/youtubeApi';

interface InfoAlertProps {
  scene: Scene;
  isEditing: boolean;
  onGenerateImage?: boolean;
  onGenerateAudio?: boolean;
}

export const InfoAlert: React.FC<InfoAlertProps> = ({
  scene,
  isEditing,
  onGenerateImage = false,
  onGenerateAudio = false,
}) => {
  if (isEditing) return null;

  return (
    <Alert
      severity="info"
      icon={<Info fontSize="small" />}
      sx={{
        mt: 2,
        bgcolor: '#eff6ff',
        border: '1px solid #bfdbfe',
        '& .MuiAlert-icon': {
          color: '#3b82f6',
        },
        '& .MuiAlert-message': {
          color: '#1e40af',
        },
      }}
    >
      <Typography variant="caption" sx={{ fontSize: '0.75rem', lineHeight: 1.5 }}>
        <strong>Tip:</strong> Click the edit icon above to modify narration, visual prompt, or duration.
        {onGenerateImage && !scene.imageUrl && ' Generate an image for this scene before rendering the video.'}
        {onGenerateAudio && !scene.audioUrl && ' Generate audio narration for this scene before rendering the video.'}
        Disable scenes you don't need to reduce rendering cost.
      </Typography>
    </Alert>
  );
};
