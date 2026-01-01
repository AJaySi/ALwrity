import { useState, useMemo, useEffect } from 'react';
import { aiApiClient } from '../../../../../api/client';

export type Resolution = '480p' | '720p';
export type FaceSwapModel = 'mocha' | 'video-face-swap';
export type TargetGender = 'all' | 'female' | 'male';

export const useFaceSwap = () => {
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [videoPreview, setVideoPreview] = useState<string | null>(null);
  const [model, setModel] = useState<FaceSwapModel>('mocha');
  const [prompt, setPrompt] = useState<string>('');
  const [resolution, setResolution] = useState<Resolution>('480p');
  const [seed, setSeed] = useState<number | null>(null);
  const [targetGender, setTargetGender] = useState<TargetGender>('all');
  const [targetIndex, setTargetIndex] = useState<number>(0);
  const [swapping, setSwapping] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{ video_url: string; cost: number; model: string } | null>(null);

  // Update previews when files change
  useEffect(() => {
    if (imageFile) {
      const url = URL.createObjectURL(imageFile);
      setImagePreview(url);
      return () => URL.revokeObjectURL(url);
    } else {
      setImagePreview(null);
    }
  }, [imageFile]);

  useEffect(() => {
    if (videoFile) {
      const url = URL.createObjectURL(videoFile);
      setVideoPreview(url);
      return () => URL.revokeObjectURL(url);
    } else {
      setVideoPreview(null);
    }
  }, [videoFile]);

  const canSwap = useMemo(() => {
    return imageFile !== null && videoFile !== null;
  }, [imageFile, videoFile]);

  const costHint = useMemo(() => {
    if (!imageFile || !videoFile) return 'Upload image and video to see cost';
    
    // MoCha pricing: $0.04/s (480p), $0.08/s (720p)
    // Video Face Swap pricing: $0.01/s
    // Minimum charge: 5 seconds for both
    // We'll estimate based on a default duration (actual cost calculated on backend)
    let costPerSecond: number;
    if (model === 'mocha') {
      costPerSecond = resolution === '480p' ? 0.04 : 0.08;
    } else {
      costPerSecond = 0.01;
    }
    const estimatedCost = costPerSecond * 10; // Estimate 10 seconds
    return `~$${estimatedCost.toFixed(2)} (estimated, based on video duration)`;
  }, [imageFile, videoFile, model, resolution]);

  const swapFace = async (): Promise<void> => {
    if (!imageFile || !videoFile) return;

    setSwapping(true);
    setProgress(0);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('image_file', imageFile);
      formData.append('video_file', videoFile);
      formData.append('model', model);
      
      if (model === 'mocha') {
        if (prompt) {
          formData.append('prompt', prompt);
        }
        formData.append('resolution', resolution);
        if (seed !== null) {
          formData.append('seed', seed.toString());
        }
      } else {
        formData.append('target_gender', targetGender);
        formData.append('target_index', targetIndex.toString());
      }

      setProgress(10);

      const response = await aiApiClient.post('/api/video-studio/face-swap', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const uploadProgress = Math.round((progressEvent.loaded * 20) / progressEvent.total);
            setProgress(10 + uploadProgress);
          }
        },
        timeout: 600000, // 10 minutes
      });

      setProgress(50);

      if (response.data.success) {
        setResult(response.data);
        setProgress(100);
      } else {
        throw new Error(response.data.error || 'Face swap failed');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to swap face');
      setProgress(0);
    } finally {
      setSwapping(false);
    }
  };

  const reset = () => {
    setImageFile(null);
    setImagePreview(null);
    setVideoFile(null);
    setVideoPreview(null);
    setModel('mocha');
    setPrompt('');
    setResolution('480p');
    setSeed(null);
    setTargetGender('all');
    setTargetIndex(0);
    setResult(null);
    setError(null);
    setProgress(0);
  };

  return {
    imageFile,
    imagePreview,
    videoFile,
    videoPreview,
    model,
    prompt,
    resolution,
    seed,
    targetGender,
    targetIndex,
    swapping,
    progress,
    error,
    result,
    setImageFile,
    setVideoFile,
    setModel,
    setPrompt,
    setResolution,
    setSeed,
    setTargetGender,
    setTargetIndex,
    canSwap,
    costHint,
    swapFace,
    reset,
  };
};
