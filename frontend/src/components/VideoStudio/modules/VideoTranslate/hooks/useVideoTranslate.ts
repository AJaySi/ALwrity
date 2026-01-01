import { useState, useMemo, useEffect } from 'react';
import { aiApiClient } from '../../../../../api/client';

export const useVideoTranslate = () => {
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [videoPreview, setVideoPreview] = useState<string | null>(null);
  const [outputLanguage, setOutputLanguage] = useState<string>('English');
  const [translating, setTranslating] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{ video_url: string; cost: number; output_language: string } | null>(null);
  const [supportedLanguages, setSupportedLanguages] = useState<string[]>([]);

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

  // Load supported languages on mount
  useEffect(() => {
    const loadLanguages = async () => {
      try {
        const response = await aiApiClient.get('/api/video-studio/video-translate/languages');
        if (response.data.languages) {
          setSupportedLanguages(response.data.languages);
        }
      } catch (err) {
        console.error('Failed to load languages:', err);
        // Use default list if API fails
        setSupportedLanguages([
          'English',
          'English (United States)',
          'English (UK)',
          'Spanish',
          'Spanish (Spain)',
          'Spanish (Mexico)',
          'French',
          'French (France)',
          'German',
          'German (Germany)',
          'Italian',
          'Portuguese',
          'Portuguese (Brazil)',
          'Chinese',
          'Chinese (Mandarin, Simplified)',
          'Japanese',
          'Korean',
          'Hindi',
          'Arabic',
          'Russian',
        ]);
      }
    };
    loadLanguages();
  }, []);

  const canTranslate = useMemo(() => {
    return videoFile !== null && outputLanguage !== '';
  }, [videoFile, outputLanguage]);

  const costHint = useMemo(() => {
    if (!videoFile) return 'Upload video to see cost';
    
    // HeyGen Video Translate pricing: $0.0375/s
    // We'll estimate based on a default duration (actual cost calculated on backend)
    const costPerSecond = 0.0375;
    const estimatedCost = costPerSecond * 10; // Estimate 10 seconds
    return `~$${estimatedCost.toFixed(2)} (estimated, based on video duration)`;
  }, [videoFile]);

  const translateVideo = async (): Promise<void> => {
    if (!videoFile) return;

    setTranslating(true);
    setProgress(0);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('video_file', videoFile);
      formData.append('output_language', outputLanguage);

      setProgress(10);

      const response = await aiApiClient.post('/api/video-studio/video-translate', formData, {
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
        throw new Error(response.data.error || 'Video translation failed');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to translate video');
      setProgress(0);
    } finally {
      setTranslating(false);
    }
  };

  const reset = () => {
    setVideoFile(null);
    setVideoPreview(null);
    setOutputLanguage('English');
    setResult(null);
    setError(null);
    setProgress(0);
  };

  return {
    videoFile,
    videoPreview,
    outputLanguage,
    translating,
    progress,
    error,
    result,
    supportedLanguages,
    setVideoFile,
    setOutputLanguage,
    canTranslate,
    costHint,
    translateVideo,
    reset,
  };
};
