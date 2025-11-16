import React from 'react';
import { Box, Button, CircularProgress } from '@mui/material';
import ImageIcon from '@mui/icons-material/Image';
import VolumeUpIcon from '@mui/icons-material/VolumeUp';
import { outlineActionButtonSx, primaryButtonSx } from './buttonStyles';

interface OutlineActionsBarProps {
  isGenerating: boolean;
  canRegenerateOutline: boolean;
  onRegenerateOutline: () => void;

  showMediaActions: boolean;
  isGeneratingImages: boolean;
  isGeneratingAudio: boolean;
  illustrationEnabled: boolean;
  narrationEnabled: boolean;
  onGenerateImages: () => void;
  onGenerateAudio: () => void;

  canContinue: boolean;
  onContinue: () => void;
}

const OutlineActionsBar: React.FC<OutlineActionsBarProps> = ({
  isGenerating,
  canRegenerateOutline,
  onRegenerateOutline,
  showMediaActions,
  isGeneratingImages,
  isGeneratingAudio,
  illustrationEnabled,
  narrationEnabled,
  onGenerateImages,
  onGenerateAudio,
  canContinue,
  onContinue,
}) => {
  return (
    <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', flexWrap: 'wrap' }}>
      <Button
        variant="outlined"
        onClick={onRegenerateOutline}
        disabled={isGenerating || !canRegenerateOutline}
        sx={outlineActionButtonSx}
      >
        {isGenerating ? (
          <>
            <CircularProgress size={20} sx={{ mr: 1 }} />
            Regenerating...
          </>
        ) : (
          'Regenerate Outline'
        )}
      </Button>
      {showMediaActions && (
        <>
          <span>
            <Button
              variant="outlined"
              startIcon={<ImageIcon />}
              onClick={onGenerateImages}
              disabled={isGeneratingImages || !illustrationEnabled}
              sx={outlineActionButtonSx}
              title={!illustrationEnabled ? 'Enable Illustration in Story Setup to generate images.' : undefined}
            >
              {isGeneratingImages ? (
                <>
                  <CircularProgress size={20} sx={{ mr: 1 }} />
                  Generating Images...
                </>
              ) : (
                'Generate Images'
              )}
            </Button>
          </span>
          <span>
            <Button
              variant="outlined"
              startIcon={<VolumeUpIcon />}
              onClick={onGenerateAudio}
              disabled={isGeneratingAudio || !narrationEnabled}
              sx={outlineActionButtonSx}
              title={!narrationEnabled ? 'Enable Narration in Story Setup to generate audio.' : undefined}
            >
              {isGeneratingAudio ? (
                <>
                  <CircularProgress size={20} sx={{ mr: 1 }} />
                  Generating Audio...
                </>
              ) : (
                'Generate Audio'
              )}
            </Button>
          </span>
        </>
      )}
      <Button
        variant="contained"
        onClick={onContinue}
        disabled={!canContinue}
        sx={primaryButtonSx}
      >
        Continue to Writing
      </Button>
    </Box>
  );
};

export default OutlineActionsBar;

