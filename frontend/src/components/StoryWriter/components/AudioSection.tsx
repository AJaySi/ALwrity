import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Alert,
  LinearProgress,
  CircularProgress,
  Chip,
} from '@mui/material';
import VolumeUpIcon from '@mui/icons-material/VolumeUp';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { useStoryWriterState } from '../../../hooks/useStoryWriterState';
import { storyWriterApi } from '../../../services/storyWriterApi';
import { triggerSubscriptionError } from '../../../api/client';
import { SceneSelection } from './SceneSelection';
import { AudioPlayerList } from './AudioPlayerList';

interface AudioSectionProps {
  state: ReturnType<typeof useStoryWriterState>;
  selectedScenes: Set<number>;
  onSelectedScenesChange: (scenes: Set<number>) => void;
  showSceneSelection: boolean;
  onShowSceneSelectionChange: (show: boolean) => void;
  error: string | null;
  onError: (error: string | null) => void;
}

export const AudioSection: React.FC<AudioSectionProps> = ({
  state,
  selectedScenes,
  onSelectedScenesChange,
  showSceneSelection,
  onShowSceneSelectionChange,
  error,
  onError,
}) => {
  const [isGeneratingAudio, setIsGeneratingAudio] = useState(false);
  const [audioProgress, setAudioProgress] = useState(0);

  const hasScenes = state.isOutlineStructured && state.outlineScenes && state.outlineScenes.length > 0;
  const narrationEnabled = state.enableNarration;
  const hasAudio = narrationEnabled && state.sceneAudio && state.sceneAudio.size > 0;
  const canGenerateAudio = hasScenes && selectedScenes.size > 0 && !isGeneratingAudio;

  const handleGenerateAudio = async () => {
    if (!state.outlineScenes || state.outlineScenes.length === 0) {
      onError('Please generate a structured outline first');
      return;
    }
    if (!narrationEnabled) {
      onError('Narration feature is disabled in Story Setup.');
      return;
    }

    if (selectedScenes.size === 0) {
      onError('Please select at least one scene to generate audio for');
      return;
    }

    setIsGeneratingAudio(true);
    onError(null);
    setAudioProgress(0);

    try {
      const scenesToGenerate = state.outlineScenes.filter((scene: any, index: number) => {
        const sceneNumber = scene.scene_number || index + 1;
        return selectedScenes.has(sceneNumber);
      });

      const response = await storyWriterApi.generateSceneAudio({
        scenes: scenesToGenerate,
        provider: state.audioProvider,
        lang: state.audioLang,
        slow: state.audioSlow,
        rate: state.audioRate,
      });

      if (response.success && response.audio_files) {
        const audioMap = new Map<number, string>();
        response.audio_files.forEach((audio) => {
          if (audio.audio_url && !audio.error) {
            audioMap.set(audio.scene_number, audio.audio_url);
          }
        });
        state.setSceneAudio(audioMap);
        state.setError(null);
        setAudioProgress(100);
      } else {
        throw new Error('Failed to generate audio');
      }
    } catch (err: any) {
      console.error('Audio generation failed:', err);

      const status = err?.response?.status;
      if (status === 429 || status === 402) {
        const handled = await triggerSubscriptionError(err);
        if (handled) {
          setIsGeneratingAudio(false);
          return;
        }
      }

      const errorMessage = err.response?.data?.detail || err.message || 'Failed to generate audio';
      onError(errorMessage);
      state.setError(errorMessage);
    } finally {
      setIsGeneratingAudio(false);
    }
  };

  if (!narrationEnabled) {
    return (
      <Alert severity="info" sx={{ mb: 3 }}>
        Narration is disabled in Story Setup. Enable it to generate or listen to audio narration.
      </Alert>
    );
  }

  return (
    <Box sx={{ mb: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <VolumeUpIcon sx={{ color: hasAudio ? '#4caf50' : '#5D4037' }} />
          <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#1A1611' }}>
            Audio Narration
          </Typography>
          {hasAudio && (
            <Chip
              icon={<CheckCircleIcon />}
              label="Generated"
              size="small"
              color="success"
              sx={{ ml: 1 }}
            />
          )}
        </Box>
        <Button
          variant={hasAudio ? 'outlined' : 'contained'}
          startIcon={isGeneratingAudio ? <CircularProgress size={16} /> : <VolumeUpIcon />}
          onClick={handleGenerateAudio}
          disabled={!canGenerateAudio || isGeneratingAudio}
        >
          {hasAudio
            ? 'Regenerate Selected'
            : `Generate Audio (${selectedScenes.size} scene${selectedScenes.size !== 1 ? 's' : ''})`}
        </Button>
      </Box>

      {hasScenes && state.outlineScenes && (
        <SceneSelection
          scenes={state.outlineScenes}
          selectedScenes={selectedScenes}
          onSelectedScenesChange={onSelectedScenesChange}
          sceneAudioMap={state.sceneAudio}
          showSceneSelection={showSceneSelection}
          onShowSceneSelectionChange={onShowSceneSelectionChange}
        />
      )}

      {isGeneratingAudio && (
        <Box sx={{ mt: 1 }}>
          <LinearProgress variant="indeterminate" />
          <Typography variant="caption" sx={{ mt: 0.5, color: '#5D4037', display: 'block' }}>
            Generating audio for {selectedScenes.size} selected scene
            {selectedScenes.size !== 1 ? 's' : ''}...
          </Typography>
        </Box>
      )}

      {hasAudio && state.sceneAudio && state.outlineScenes && (
        <AudioPlayerList scenes={state.outlineScenes} sceneAudioMap={state.sceneAudio} />
      )}
    </Box>
  );
};

