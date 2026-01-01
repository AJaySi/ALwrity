import { useState, useMemo, useCallback } from 'react';

export type AvatarResolution = '480p' | '720p';
export type AvatarModel = 'infinitetalk' | 'hunyuan-avatar';

export const useAvatarVideo = () => {
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [audioPreview, setAudioPreview] = useState<string | null>(null);
  const [resolution, setResolution] = useState<AvatarResolution>('720p');
  const [model, setModel] = useState<AvatarModel>('infinitetalk');
  const [prompt, setPrompt] = useState('');
  const [maskImageFile, setMaskImageFile] = useState<File | null>(null);
  const [seed, setSeed] = useState<number | null>(null);

  // Cost estimation
  const costHint = useMemo(() => {
    const estimatedDuration = 10; // TODO: Get actual audio duration
    
    if (model === 'hunyuan-avatar') {
      // Hunyuan Avatar: $0.15/5s (480p) or $0.30/5s (720p)
      const costPer5Seconds = resolution === '480p' ? 0.15 : 0.30;
      const billable5SecondBlocks = Math.ceil(estimatedDuration / 5);
      const estimate = (costPer5Seconds * billable5SecondBlocks).toFixed(2);
      return `Est. ~$${estimate}`;
    } else {
      // InfiniteTalk: $0.03/s (480p) or $0.06/s (720p)
      const costPerSecond = resolution === '480p' ? 0.03 : 0.06;
      const estimate = (costPerSecond * estimatedDuration).toFixed(2);
      return `Est. ~$${estimate}`;
    }
  }, [resolution, model]);

  const canGenerate = useMemo(() => {
    return imageFile !== null && audioFile !== null;
  }, [imageFile, audioFile]);

  const handleImageSelect = useCallback((file: File | null) => {
    setImageFile(file);
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    } else {
      setImagePreview(null);
    }
  }, []);

  const handleAudioSelect = useCallback((file: File | null) => {
    setAudioFile(file);
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setAudioPreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    } else {
      setAudioPreview(null);
    }
  }, []);

  const handleMaskImageSelect = useCallback((file: File | null) => {
    setMaskImageFile(file);
  }, []);

  return {
    // State
    imageFile,
    imagePreview,
    audioFile,
    audioPreview,
    resolution,
    model,
    prompt,
    maskImageFile,
    seed,
    // Setters
    setImageFile: handleImageSelect,
    setAudioFile: handleAudioSelect,
    setResolution,
    setModel,
    setPrompt,
    setMaskImageFile: handleMaskImageSelect,
    setSeed,
    // Computed
    canGenerate,
    costHint,
  };
};
