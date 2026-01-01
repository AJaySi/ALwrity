import { useState, useMemo, useEffect } from 'react';
import { aiApiClient } from '../../../../../api/client';

export const useVideoBackgroundRemover = () => {
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [videoPreview, setVideoPreview] = useState<string | null>(null);
  const [backgroundImageFile, setBackgroundImageFile] = useState<File | null>(null);
  const [backgroundImagePreview, setBackgroundImagePreview] = useState<string | null>(null);
  const [removing, setRemoving] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{ video_url: string; cost: number; has_background_replacement: boolean } | null>(null);
  const [estimatedDuration, setEstimatedDuration] = useState<number>(10.0);
  const [costEstimate, setCostEstimate] = useState<number | null>(null);

  // Update previews when files change
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

  useEffect(() => {
    if (backgroundImageFile) {
      const url = URL.createObjectURL(backgroundImageFile);
      setBackgroundImagePreview(url);
      return () => URL.revokeObjectURL(url);
    } else {
      setBackgroundImagePreview(null);
    }
  }, [backgroundImageFile]);

  // Fetch cost estimate when duration changes
  useEffect(() => {
    const fetchCostEstimate = async () => {
      if (!videoFile || estimatedDuration < 5) {
        setCostEstimate(null);
        return;
      }

      try {
        const formData = new FormData();
        formData.append('estimated_duration', estimatedDuration.toString());

        const response = await aiApiClient.post('/api/video-studio/video-background-remover/estimate-cost', formData, {
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
        // Pricing: $0.01/second, min $0.05 for ≤5s, max $6.00 for 600s
        const costPerSecond = 0.01;
        let estimatedCost = estimatedDuration * costPerSecond;
        if (estimatedDuration <= 5.0) {
          estimatedCost = 0.05;  // Minimum charge
        } else if (estimatedDuration >= 600.0) {
          estimatedCost = 6.00;  // Maximum charge
        }
        setCostEstimate(estimatedCost);
      }
    };

    fetchCostEstimate();
  }, [videoFile, estimatedDuration]);

  const canRemove = useMemo(() => {
    return videoFile !== null;
  }, [videoFile]);

  const costHint = useMemo(() => {
    if (!videoFile) return 'Upload a video to see cost estimate';
    
    if (costEstimate !== null) {
      return `Est. ~$${costEstimate.toFixed(2)} (${estimatedDuration.toFixed(0)}s)`;
    }
    
    // Fallback calculation
    // Pricing: $0.01/second, min $0.05 for ≤5s, max $6.00 for 600s
    const costPerSecond = 0.01;
    let estimatedCost = estimatedDuration * costPerSecond;
    if (estimatedDuration <= 5.0) {
      estimatedCost = 0.05;  // Minimum charge
    } else if (estimatedDuration >= 600.0) {
      estimatedCost = 6.00;  // Maximum charge
    }
    return `Est. ~$${estimatedCost.toFixed(2)} (${estimatedDuration.toFixed(0)}s)`;
  }, [videoFile, estimatedDuration, costEstimate]);

  const removeBackground = async () => {
    if (!videoFile) return;

    setRemoving(true);
    setError(null);
    setResult(null);
    setProgress(0);

    try {
      const formData = new FormData();
      formData.append('video_file', videoFile);
      if (backgroundImageFile) {
        formData.append('background_image_file', backgroundImageFile);
      }

      // Submit background removal request
      setProgress(10);
      const response = await aiApiClient.post('/api/video-studio/video-background-remover', formData, {
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
          setRemoving(false);
          setResult(response.data);
          setProgress(100);
        } else {
          clearInterval(progressInterval);
          throw new Error(response.data.error || 'Background removal failed');
        }
      } catch (err) {
        clearInterval(progressInterval);
        throw err;
      }
    } catch (err: any) {
      setRemoving(false);
      setProgress(0);
      setError(err.response?.data?.detail || err.message || 'Failed to remove background');
    }
  };

  const reset = () => {
    setRemoving(false);
    setProgress(0);
    setError(null);
    setResult(null);
    setVideoFile(null);
    setBackgroundImageFile(null);
  };

  return {
    // State
    videoFile,
    videoPreview,
    backgroundImageFile,
    backgroundImagePreview,
    removing,
    progress,
    error,
    result,
    estimatedDuration,
    costEstimate,
    // Setters
    setVideoFile,
    setBackgroundImageFile,
    // Computed
    canRemove,
    costHint,
    // Actions
    removeBackground,
    reset,
  };
};
