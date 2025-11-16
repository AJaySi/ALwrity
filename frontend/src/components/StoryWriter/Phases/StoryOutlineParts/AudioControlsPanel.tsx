import React from 'react';
import { Box, Button, CircularProgress, Typography } from '@mui/material';
import VolumeUpIcon from '@mui/icons-material/VolumeUp';

interface AudioControlsPanelProps {
  enabled: boolean;
  regenerating: boolean;
  onRegenerate: () => void;
}

const AudioControlsPanel: React.FC<AudioControlsPanelProps> = ({
  enabled,
  regenerating,
  onRegenerate,
}) => {
  return (
    <Box sx={{ mt: 1.5, p: 2, border: '1px dashed rgba(120,90,60,0.35)', borderRadius: 1.5, backgroundColor: 'rgba(255,255,255,0.6)' }}>
      <Typography variant="caption" sx={{ color: '#7a5335', display: 'block', mb: 1 }}>
        Audio controls (uses Setup settings)
      </Typography>
      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
        <Button
          size="small"
          variant="outlined"
          startIcon={regenerating ? <CircularProgress size={16} /> : <VolumeUpIcon />}
          onClick={onRegenerate}
          disabled={regenerating || !enabled}
        >
          {regenerating ? 'Regenerating...' : 'Regenerate Audio (Scene)'}
        </Button>
      </Box>
      {!enabled && (
        <Typography variant="caption" sx={{ display: 'block', mt: 1, color: '#a37b55' }}>
          Enable Narration in Story Setup to generate audio.
        </Typography>
      )}
    </Box>
  );
};

export default AudioControlsPanel;

