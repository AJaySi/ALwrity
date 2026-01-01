import { useState, useMemo, useCallback } from 'react';

export type ExtendResolution = '480p' | '720p' | '1080p';
export type ExtendModel = 'wan-2.5' | 'wan-2.2-spicy' | 'seedance-1.5-pro';

export const useExtendVideo = () => {
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [videoPreview, setVideoPreview] = useState<string | null>(null);
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [audioPreview, setAudioPreview] = useState<string | null>(null);
  const [prompt, setPrompt] = useState('');
  const [negativePrompt, setNegativePrompt] = useState('');
  const [model, setModel] = useState<ExtendModel>('wan-2.5');
  const [resolution, setResolution] = useState<ExtendResolution>('720p');
  const [duration, setDuration] = useState<number>(5);
  const [enablePromptExpansion, setEnablePromptExpansion] = useState(false);
  const [generateAudio, setGenerateAudio] = useState<boolean>(true); // Seedance 1.5 Pro only
  const [cameraFixed, setCameraFixed] = useState<boolean>(false); // Seedance 1.5 Pro only
  const [seed, setSeed] = useState<number | null>(null);

  // Adjust resolution and duration when model changes
  const handleModelChange = useCallback((newModel: ExtendModel) => {
    setModel(newModel);
    // Adjust resolution if needed
    if ((newModel === 'wan-2.2-spicy' || newModel === 'seedance-1.5-pro') && resolution === '1080p') {
      setResolution('720p');
    }
    // Adjust duration if needed
    if (newModel === 'wan-2.2-spicy' && duration !== 5 && duration !== 8) {
      setDuration(5);
    } else if (newModel === 'seedance-1.5-pro' && (duration < 4 || duration > 12)) {
      setDuration(5); // Default to 5s for Seedance
    }
  }, [resolution, duration]);

  // Cost estimation (model-specific pricing)
  const costHint = useMemo(() => {
    if (!videoFile) return 'Upload a video to see cost estimate';
    
    // Model-specific pricing
    let pricing: { [key: string]: number };
    if (model === 'wan-2.2-spicy') {
      // WAN 2.2 Spicy: $0.03/s (480p), $0.06/s (720p)
      pricing = {
        '480p': 0.03,
        '720p': 0.06,
      };
    } else if (model === 'seedance-1.5-pro') {
      // Seedance 1.5 Pro pricing varies by audio generation
      // With audio: $0.024/s (480p), $0.052/s (720p)
      // Without audio: $0.012/s (480p), $0.026/s (720p)
      if (generateAudio) {
        pricing = {
          '480p': 0.024,
          '720p': 0.052,
        };
      } else {
        pricing = {
          '480p': 0.012,
          '720p': 0.026,
        };
      }
    } else {
      // WAN 2.5: $0.05/s (480p), $0.10/s (720p), $0.15/s (1080p)
      pricing = {
        '480p': 0.05,
        '720p': 0.10,
        '1080p': 0.15,
      };
    }
    
    const costPerSecond = pricing[resolution as keyof typeof pricing] || pricing['720p'];
    const estimatedCost = (costPerSecond * duration).toFixed(2);
    
    return `Est. ~$${estimatedCost} (${duration}s @ ${resolution})`;
  }, [videoFile, model, resolution, duration, generateAudio]);

  const canExtend = useMemo(() => {
    return videoFile !== null && prompt.trim().length > 0;
  }, [videoFile, prompt]);

  const handleVideoSelect = useCallback((file: File | null) => {
    setVideoFile(file);
    if (file) {
      // Validate video file
      if (!file.type.startsWith('video/')) {
        alert('Please select a video file');
        return;
      }
      if (file.size > 500 * 1024 * 1024) {
        alert('Video file must be less than 500MB');
        return;
      }
      
      // Create preview URL
      const reader = new FileReader();
      reader.onload = (e) => {
        setVideoPreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    } else {
      setVideoPreview(null);
    }
  }, []);

  const handleAudioSelect = useCallback((file: File | null) => {
    setAudioFile(file);
    if (file) {
      // Validate audio file
      if (!file.type.startsWith('audio/')) {
        alert('Please select an audio file');
        return;
      }
      if (file.size > 50 * 1024 * 1024) {
        alert('Audio file must be less than 50MB');
        return;
      }
      
      // Create preview URL
      const reader = new FileReader();
      reader.onload = (e) => {
        setAudioPreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    } else {
      setAudioPreview(null);
    }
  }, []);

  return {
    // State
    videoFile,
    videoPreview,
    audioFile,
    audioPreview,
    prompt,
    negativePrompt,
    model,
    resolution,
    duration,
    enablePromptExpansion,
    generateAudio,
    cameraFixed,
    seed,
    // Setters
    setVideoFile: handleVideoSelect,
    setAudioFile: handleAudioSelect,
    setPrompt,
    setNegativePrompt,
    setModel: handleModelChange,
    setResolution,
    setDuration,
    setEnablePromptExpansion,
    setGenerateAudio,
    setCameraFixed,
    setSeed,
    // Computed
    canExtend,
    costHint,
  };
};
