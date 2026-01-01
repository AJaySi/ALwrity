import { useState, useMemo, useEffect } from 'react';
import { aiApiClient } from '../../../../../api/client';

export type Platform = 'instagram' | 'tiktok' | 'youtube' | 'linkedin' | 'facebook' | 'twitter';
export type TrimMode = 'beginning' | 'middle' | 'end';

export interface PlatformResult {
  platform: string;
  name: string;
  aspect_ratio: string;
  video_url: string;
  thumbnail_url?: string;
  duration: number;
  file_size: number;
  width: number;
  height: number;
}

export const useSocialVideo = () => {
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [videoPreview, setVideoPreview] = useState<string | null>(null);
  const [selectedPlatforms, setSelectedPlatforms] = useState<Platform[]>([]);
  const [autoCrop, setAutoCrop] = useState<boolean>(true);
  const [generateThumbnails, setGenerateThumbnails] = useState<boolean>(true);
  const [compress, setCompress] = useState<boolean>(true);
  const [trimMode, setTrimMode] = useState<TrimMode>('beginning');
  const [optimizing, setOptimizing] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const [results, setResults] = useState<PlatformResult[]>([]);
  const [errors, setErrors] = useState<Array<{ platform: string; error: string }>>([]);
  const [platformSpecs, setPlatformSpecs] = useState<Record<string, any>>({});

  // Update preview when file changes
  useEffect(() => {
    if (videoFile) {
      const url = URL.createObjectURL(videoFile);
      setVideoPreview(url);
      return () => URL.revokeObjectURL(url);
    } else {
      setVideoPreview(null);
    }
  }, [videoFile]);

  // Load platform specifications
  useEffect(() => {
    const loadPlatformSpecs = async () => {
      try {
        const response = await aiApiClient.get('/api/video-studio/social/platforms');
        if (response.data.success) {
          setPlatformSpecs(response.data.platforms);
        }
      } catch (error) {
        console.error('Failed to load platform specs:', error);
      }
    };
    loadPlatformSpecs();
  }, []);

  const togglePlatform = (platform: Platform) => {
    setSelectedPlatforms((prev) =>
      prev.includes(platform)
        ? prev.filter((p) => p !== platform)
        : [...prev, platform]
    );
  };

  const canOptimize = useMemo(() => {
    return videoFile !== null && selectedPlatforms.length > 0;
  }, [videoFile, selectedPlatforms]);

  const costHint = useMemo(() => {
    if (!videoFile) return 'Upload a video to optimize';
    if (selectedPlatforms.length === 0) return 'Select at least one platform';
    return 'Free (FFmpeg processing)';
  }, [videoFile, selectedPlatforms]);

  const optimize = async (): Promise<void> => {
    if (!videoFile || selectedPlatforms.length === 0) return;

    setOptimizing(true);
    setProgress(0);
    setResults([]);
    setErrors([]);

    try {
      const formData = new FormData();
      formData.append('file', videoFile);
      formData.append('platforms', selectedPlatforms.join(','));
      formData.append('auto_crop', autoCrop.toString());
      formData.append('generate_thumbnails', generateThumbnails.toString());
      formData.append('compress', compress.toString());
      formData.append('trim_mode', trimMode);

      setProgress(20);

      const response = await aiApiClient.post('/api/video-studio/social/optimize', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const uploadProgress = Math.round((progressEvent.loaded * 30) / progressEvent.total);
            setProgress(20 + uploadProgress);
          }
        },
        timeout: 600000, // 10 minutes
      });

      setProgress(80);

      if (response.data.success) {
        setResults(response.data.results || []);
        setErrors(response.data.errors || []);
        setProgress(100);
      } else {
        throw new Error(response.data.error || 'Optimization failed');
      }
    } catch (error: any) {
      setErrors([
        {
          platform: 'all',
          error: error.response?.data?.detail || error.message || 'Optimization failed',
        },
      ]);
    } finally {
      setOptimizing(false);
    }
  };

  const reset = () => {
    setVideoFile(null);
    setVideoPreview(null);
    setSelectedPlatforms([]);
    setResults([]);
    setErrors([]);
    setProgress(0);
  };

  return {
    videoFile,
    videoPreview,
    selectedPlatforms,
    autoCrop,
    generateThumbnails,
    compress,
    trimMode,
    optimizing,
    progress,
    results,
    errors,
    platformSpecs,
    setVideoFile,
    togglePlatform,
    setAutoCrop,
    setGenerateThumbnails,
    setCompress,
    setTrimMode,
    canOptimize,
    costHint,
    optimize,
    reset,
  };
};
