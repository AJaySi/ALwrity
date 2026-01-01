import { useState, useMemo, useCallback } from 'react';
import { useContentAssets, type ContentAsset } from '../../../../../hooks/useContentAssets';
import { getModelInfo } from '../models/videoModels';
import type { Mode, Duration, Resolution, AspectPreset, MotionPreset } from '../types';

export const useCreateVideo = () => {
  const [mode, setMode] = useState<Mode>('t2v');
  const [prompt, setPrompt] = useState('');
  const [negativePrompt, setNegativePrompt] = useState('');
  const [duration, setDuration] = useState<Duration>(8);
  const [resolution, setResolution] = useState<Resolution>('720p');
  const [aspect, setAspect] = useState<AspectPreset>('9:16');
  const [motion, setMotion] = useState<MotionPreset>('Medium');
  const [audioAttached, setAudioAttached] = useState(false);
  const [selectedModel, setSelectedModel] = useState<string>('hunyuan-video-1.5'); // Default model
  const [selectedExample, setSelectedExample] = useState<number | null>(null);
  const [selectedAssetId, setSelectedAssetId] = useState<number | null>(null);
  const [promptPlaceholderIndex, setPromptPlaceholderIndex] = useState(0);
  const [negativePlaceholderIndex, setNegativePlaceholderIndex] = useState(0);
  const [promptFocused, setPromptFocused] = useState(false);
  const [negativeFocused, setNegativeFocused] = useState(false);

  // Fetch videos from asset library
  const { assets: libraryVideos, loading: loadingLibraryVideos } = useContentAssets({
    asset_type: 'video',
    limit: 6,
  });

  const canGenerate = useMemo(() => prompt.trim().length > 5, [prompt]);

  const costHint = useMemo(() => {
    // Get model-specific pricing
    const modelInfo = getModelInfo(selectedModel);
    if (modelInfo) {
      const costPerSecond = modelInfo.costPerSecond[resolution] || modelInfo.costPerSecond[Object.keys(modelInfo.costPerSecond)[0]];
      const estimate = (costPerSecond * duration).toFixed(2);
      return `Est. ~$${estimate}`;
    }
    // Fallback to default pricing
    const base = resolution === '480p' ? 0.02 : resolution === '720p' ? 0.04 : 0.06;
    const estimate = (base * duration).toFixed(2);
    return `Est. ~$${estimate}`;
  }, [duration, resolution, selectedModel]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (mode === 'i2v' && e.target.files?.length) {
      // Placeholder: in later phases, we'll upload/preview
    }
  }, [mode]);

  return {
    // State
    mode,
    setMode,
    prompt,
    setPrompt,
    negativePrompt,
    setNegativePrompt,
    duration,
    setDuration,
    resolution,
    setResolution,
    aspect,
    setAspect,
    motion,
    setMotion,
    audioAttached,
    setAudioAttached,
    selectedModel,
    setSelectedModel,
    selectedExample,
    setSelectedExample,
    selectedAssetId,
    setSelectedAssetId,
    promptPlaceholderIndex,
    setPromptPlaceholderIndex,
    negativePlaceholderIndex,
    setNegativePlaceholderIndex,
    promptFocused,
    setPromptFocused,
    negativeFocused,
    setNegativeFocused,
    // Computed
    canGenerate,
    costHint,
    libraryVideos,
    loadingLibraryVideos,
    // Handlers
    handleFileSelect,
  };
};
