import React from 'react';
import { Box, Button, CircularProgress, Typography } from '@mui/material';
import ImageIcon from '@mui/icons-material/Image';

interface SceneGenerationPanelProps {
  provider?: string | null;
  width: number;
  height: number;
  model?: string | null;
  enabled: boolean;
  regenerating: boolean;
  onRegenerate: () => void;
}

const SceneGenerationPanel: React.FC<SceneGenerationPanelProps> = ({
  provider,
  width,
  height,
  model,
  enabled,
  regenerating,
  onRegenerate,
}) => {
  return (
    <Box sx={{ mt: 1.5, p: 2, border: '1px dashed rgba(120,90,60,0.35)', borderRadius: 1.5, backgroundColor: 'rgba(255,255,255,0.6)' }}>
      <Typography variant="caption" sx={{ color: '#7a5335', display: 'block', mb: 1 }}>
        Scene generation controls (uses Setup settings)
      </Typography>
      <Typography variant="caption" sx={{ color: '#5D4037', display: 'block', mb: 1 }}>
        Provider: {provider || 'Auto'} · Size: {width}x{height}{model ? ` · Model: ${model}` : ''}
      </Typography>
      <Button
        size="small"
        variant="outlined"
        startIcon={regenerating ? <CircularProgress size={16} /> : <ImageIcon />}
        onClick={onRegenerate}
        disabled={regenerating || !enabled}
      >
        {regenerating ? 'Regenerating...' : 'Regenerate Image (Scene)'}
      </Button>
      {!enabled && (
        <Typography variant="caption" sx={{ display: 'block', mt: 1, color: '#a37b55' }}>
          Enable Illustration in Story Setup to generate images.
        </Typography>
      )}
    </Box>
  );
};

export default SceneGenerationPanel;

