import { useState, useMemo, useEffect } from 'react';
import { aiApiClient } from '../../../../../api/client';

export type AudioModel = 'hunyuan-video-foley' | 'think-sound';

export const useAddAudioToVideo = () => {
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [videoPreview, setVideoPreview] = useState<string | null>(null);
  const [model, setModel] = useState<AudioModel>('hunyuan-video-foley');
  const [prompt, setPrompt] = useState<string>('');
  const [seed, setSeed] = useState<number | null>(null);
  const [processing, setProcessing] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{ video_url: string; cost: number; model_used: string } | null>(null);
  const [estimatedDuration, setEstimatedDuration] = useState<number>(10.0);
  const [costEstimate, setCostEstimate] = useState<number | null>(null);

  // Update preview when file changes
  useEffect(() => {
    if (videoFile) {
      const url = URL.createObjectURL(videoFile);
      setVideoPreview(url);
      
      // Rough estimate: 1MB ≈ 1 second at 1080p
      const estimated = Math.max(5, videoFile.size / (1024 * 1024));
      setEstimatedDuration(estimated);
      
      return () => URL.revokeObjectURL(url);
    } else {
      setVideoPreview(null);
      setEstimatedDuration(10.0);
    }
  }, [videoFile]);

  // Fetch cost estimate when model or duration changes
  useEffect(() => {
    const fetchCostEstimate = async () => {
      if (!videoFile || estimatedDuration < 5) {
        setCostEstimate(null);
        return;
      }

      try {
        const formData = new FormData();
        formData.append('model', model);
        formData.append('estimated_duration', estimatedDuration.toString());

        const response = await aiApiClient.post('/api/video-studio/add-audio-to-video/estimate-cost', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        if (response.data.estimated_cost) {
          setCostEstimate(response.data.estimated_cost);
        }
      } catch (err) {
        console.error('Failed to fetch cost estimate:', err);
        // Fallback to client-side calculation
        if (model === 'think-sound') {
          setCostEstimate(0.05);  // Flat rate per video
        } else {
          const costPerSecond = 0.02;
          setCostEstimate(Math.max(5.0, estimatedDuration) * costPerSecond);
        }
      }
    };

    fetchCostEstimate();
  }, [videoFile, model, estimatedDuration]);

  const canAddAudio = useMemo(() => {
    return videoFile !== null;
  }, [videoFile]);

  const costHint = useMemo(() => {
    if (!videoFile) return 'Upload a video to see cost estimate';
    
    if (costEstimate !== null) {
      return `Est. ~$${costEstimate.toFixed(2)} (${estimatedDuration.toFixed(0)}s)`;
    }
    
    // Fallback calculation
    if (model === 'think-sound') {
      return `Est. ~$0.05 (flat rate per video)`;
    } else {
      const costPerSecond = 0.02;
      const estimatedCost = Math.max(5.0, estimatedDuration) * costPerSecond;
      return `Est. ~$${estimatedCost.toFixed(2)} (${estimatedDuration.toFixed(0)}s)`;
    }
  }, [videoFile, estimatedDuration, costEstimate]);

  const addAudio = async () => {
    if (!videoFile) return;

    setProcessing(true);
    setError(null);
    setResult(null);
    setProgress(0);

    try {
      const formData = new FormData();
      formData.append('video_file', videoFile);
      formData.append('model', model);
      if (prompt) {
        formData.append('prompt', prompt);
      }
      if (seed !== null) {
        formData.append('seed', seed.toString());
      }

      // Submit audio addition request
      setProgress(10);
      const response = await aiApiClient.post('/api/video-studio/add-audio-to-video', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const uploadProgress = Math.round((progressEvent.loaded * 30) / progressEvent.total);
            setProgress(uploadProgress);
          }
        },
        timeout: 600000, // 10 minutes timeout
      });

      setProgress(40);
      
      // Simulate progress updates
      let simulatedProgress = 40;
      const progressInterval = setInterval(() => {
        simulatedProgress = Math.min(90, simulatedProgress + 5);
        setProgress(simulatedProgress);
      }, 2000);

      try {
        if (response.data.success) {
          clearInterval(progressInterval);
          setProcessing(false);
          setResult(response.data);
          setProgress(100);
        } else {
          clearInterval(progressInterval);
          throw new Error(response.data.error || 'Adding audio failed');
        }
      } catch (err) {
        clearInterval(progressInterval);
        throw err;
      }
    } catch (err: any) {
      setProcessing(false);
      setProgress(0);
      setError(err.response?.data?.detail || err.message || 'Failed to add audio');
    }
  };

  const reset = () => {
    setProcessing(false);
    setProgress(0);
    setError(null);
    setResult(null);
    setVideoFile(null);
    setPrompt('');
    setSeed(null);
  };

  return {
    // State
    videoFile,
    videoPreview,
    model,
    prompt,
    seed,
    processing,
    progress,
    error,
    result,
    estimatedDuration,
    costEstimate,
    // Setters
    setVideoFile,
    setModel,
    setPrompt,
    setSeed,
    // Computed
    canAddAudio,
    costHint,
    // Actions
    addAudio,
    reset,
  };
};
