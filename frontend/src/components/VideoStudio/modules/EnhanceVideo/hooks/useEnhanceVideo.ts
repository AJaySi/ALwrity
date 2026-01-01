import { useState, useMemo, useCallback, useEffect } from 'react';
import { aiApiClient } from '../../../../../api/client';

export type EnhancementResolution = '720p' | '1080p' | '2k' | '4k';
export type EnhancementType = 'upscale';

export const useEnhanceVideo = () => {
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [videoPreview, setVideoPreview] = useState<string | null>(null);
  const [targetResolution, setTargetResolution] = useState<EnhancementResolution>('1080p');
  const [enhancementType, setEnhancementType] = useState<EnhancementType>('upscale');
  const [estimatedDuration, setEstimatedDuration] = useState<number>(10.0);
  const [costEstimate, setCostEstimate] = useState<number | null>(null);

  // Update preview when file changes
  useEffect(() => {
    if (videoFile) {
      const url = URL.createObjectURL(videoFile);
      setVideoPreview(url);
      
      // Rough estimate: 1MB ≈ 1 second at 1080p
      // In production, you'd parse the video to get actual duration
      const estimated = Math.max(5, videoFile.size / (1024 * 1024));
      setEstimatedDuration(estimated);
      
      return () => URL.revokeObjectURL(url);
    } else {
      setVideoPreview(null);
      setEstimatedDuration(10.0);
    }
  }, [videoFile]);

  // Fetch cost estimate when resolution or duration changes
  useEffect(() => {
    const fetchCostEstimate = async () => {
      if (!videoFile || estimatedDuration < 5) {
        setCostEstimate(null);
        return;
      }

      try {
        const formData = new FormData();
        formData.append('target_resolution', targetResolution);
        formData.append('estimated_duration', estimatedDuration.toString());

        const response = await aiApiClient.post('/api/video-studio/enhance/estimate-cost', formData, {
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
        const pricing = {
          '720p': 0.06 / 5,
          '1080p': 0.09 / 5,
          '2k': 0.12 / 5,
          '4k': 0.16 / 5,
        };
        const costPerSecond = pricing[targetResolution];
        setCostEstimate(Math.max(5.0, estimatedDuration) * costPerSecond);
      }
    };

    fetchCostEstimate();
  }, [videoFile, targetResolution, estimatedDuration]);

  // Cost hint for display
  const costHint = useMemo(() => {
    if (!videoFile) return 'Upload a video to see cost estimate';
    
    if (costEstimate !== null) {
      return `Est. ~$${costEstimate.toFixed(2)} (${estimatedDuration.toFixed(0)}s @ ${targetResolution})`;
    }
    
    // Fallback calculation
    const pricing = {
      '720p': 0.06 / 5,
      '1080p': 0.09 / 5,
      '2k': 0.12 / 5,
      '4k': 0.16 / 5,
    };
    const costPerSecond = pricing[targetResolution];
    const estimatedCost = Math.max(5.0, estimatedDuration) * costPerSecond;
    return `Est. ~$${estimatedCost.toFixed(2)} (${estimatedDuration.toFixed(0)}s @ ${targetResolution})`;
  }, [videoFile, targetResolution, estimatedDuration, costEstimate]);

  const canEnhance = useMemo(() => {
    return videoFile !== null;
  }, [videoFile]);

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

  return {
    // State
    videoFile,
    videoPreview,
    targetResolution,
    enhancementType,
    estimatedDuration,
    costEstimate,
    // Setters
    setVideoFile: handleVideoSelect,
    setTargetResolution,
    setEnhancementType,
    // Computed
    canEnhance,
    costHint,
  };
};
