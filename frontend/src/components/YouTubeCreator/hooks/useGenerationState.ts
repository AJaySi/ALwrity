// Hook for managing generation state
import { useState } from 'react';
import { AudioGenerationSettings } from '../../shared/AudioSettingsModal';

export const useGenerationState = () => {
  const [showAudioSettingsModal, setShowAudioSettingsModal] = useState(false);
  const [showImageSettingsModal, setShowImageSettingsModal] = useState(false);

  const [currentAudioSettings, setCurrentAudioSettings] = useState<AudioGenerationSettings>({
    voiceId: "Casual_Guy",
    speed: 1.15,
    volume: 1.0,
    pitch: 0.0,
    emotion: "happy",
    englishNormalization: true,
    bitrate: 128000,
    channel: "1",
    format: "mp3",
    enableSyncMode: true,
  });

  const [imageGenerationProgress, setImageGenerationProgress] = useState(0);
  const [imageGenerationStatus, setImageGenerationStatus] = useState<string>('');
  const [audioGenerationProgress, setAudioGenerationProgress] = useState(0);
  const [audioGenerationStatus, setAudioGenerationStatus] = useState<string>('');

  const resetImageGeneration = () => {
    setImageGenerationStatus('');
    setImageGenerationProgress(0);
  };

  const resetAudioGeneration = () => {
    setAudioGenerationStatus('');
    setAudioGenerationProgress(0);
  };

  return {
    showAudioSettingsModal,
    setShowAudioSettingsModal,
    showImageSettingsModal,
    setShowImageSettingsModal,
    currentAudioSettings,
    setCurrentAudioSettings,
    imageGenerationProgress,
    setImageGenerationProgress,
    imageGenerationStatus,
    setImageGenerationStatus,
    audioGenerationProgress,
    setAudioGenerationProgress,
    audioGenerationStatus,
    setAudioGenerationStatus,
    resetImageGeneration,
    resetAudioGeneration,
  };
};
