import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Alert,
  Divider,
} from '@mui/material';
import { useStoryWriterState } from '../../../hooks/useStoryWriterState';
import { AudioSection } from './AudioSection';
import { VideoSection } from './VideoSection';

interface MultimediaSectionProps {
  state: ReturnType<typeof useStoryWriterState>;
}

export const MultimediaSection: React.FC<MultimediaSectionProps> = ({ state }) => {
  const [error, setError] = useState<string | null>(null);
  const [selectedScenes, setSelectedScenes] = useState<Set<number>>(new Set());
  const [showSceneSelection, setShowSceneSelection] = useState(false);

  const hasScenes = state.isOutlineStructured && state.outlineScenes && state.outlineScenes.length > 0;

  // Initialize selected scenes to all scenes by default
  useEffect(() => {
    if (!state.enableNarration || !state.outlineScenes) {
      setSelectedScenes(new Set());
      return;
    }
    setSelectedScenes((prev) => {
      if (prev.size > 0) return prev;
      const scenes = state.outlineScenes ?? [];
      const allSceneNumbers = new Set(
        scenes.map((scene: any, index: number) => scene.scene_number || index + 1),
      );
      return allSceneNumbers;
    });
  }, [state.enableNarration, state.outlineScenes]);

  if (!hasScenes) {
    return null; // Don't show if no scenes available
  }

  return (
    <>
    <Paper
      sx={{
        p: 3,
        mb: 3,
        backgroundColor: '#FAF9F6',
        boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
      }}
    >
      <Typography variant="h6" gutterBottom sx={{ mb: 2, fontWeight: 600, color: '#1A1611' }}>
        Multimedia Generation
      </Typography>
      <Typography variant="body2" sx={{ mb: 3, color: '#5D4037' }}>
        Generate audio narration and video for your story scenes.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Audio Section */}
      <AudioSection
        state={state}
        selectedScenes={selectedScenes}
        onSelectedScenesChange={setSelectedScenes}
        showSceneSelection={showSceneSelection}
        onShowSceneSelectionChange={setShowSceneSelection}
        error={error}
        onError={setError}
      />

      <Divider sx={{ my: 3 }} />

      {/* Video Section */}
      <VideoSection state={state} error={error} onError={setError} />
    </Paper>
    </>
  );
};

