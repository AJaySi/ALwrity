import { useState, useMemo, useEffect, useCallback } from 'react';
import { aiApiClient } from '../../../../../api/client';

export type EditOperation = 'trim' | 'speed' | 'stabilize' | 'text' | 'volume' | 'normalize' | 'denoise';
export type TrimMode = 'beginning' | 'middle' | 'end';

export const useEditVideo = () => {
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [videoPreview, setVideoPreview] = useState<string | null>(null);
  const [videoDuration, setVideoDuration] = useState<number>(10);
  
  // Edit operation
  const [operation, setOperation] = useState<EditOperation>('trim');
  
  // Trim settings
  const [startTime, setStartTime] = useState<number>(0);
  const [endTime, setEndTime] = useState<number>(10);
  const [maxDuration, setMaxDuration] = useState<number | null>(null);
  const [trimMode, setTrimMode] = useState<TrimMode>('beginning');
  
  // Speed settings
  const [speedFactor, setSpeedFactor] = useState<number>(1.0);
  
  // Stabilization settings
  const [smoothing, setSmoothing] = useState<number>(10);
  
  // Text overlay settings
  const [overlayText, setOverlayText] = useState<string>('');
  const [textPosition, setTextPosition] = useState<string>('center');
  const [fontSize, setFontSize] = useState<number>(48);
  const [fontColor, setFontColor] = useState<string>('white');
  const [backgroundColor, setBackgroundColor] = useState<string>('black@0.5');
  const [textStartTime, setTextStartTime] = useState<number>(0);
  const [textEndTime, setTextEndTime] = useState<number | null>(null);
  
  // Volume settings
  const [volumeFactor, setVolumeFactor] = useState<number>(1.0);
  
  // Normalize settings
  const [targetLevel, setTargetLevel] = useState<number>(-14);
  
  // Denoise settings
  const [denoiseStrength, setDenoiseStrength] = useState<number>(0.5);
  
  // State
  const [editing, setEditing] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{ video_url: string; cost: number; edit_type: string } | null>(null);

  // Update preview when file changes
  useEffect(() => {
    if (videoFile) {
      const url = URL.createObjectURL(videoFile);
      setVideoPreview(url);
      
      const video = document.createElement('video');
      video.preload = 'metadata';
      video.onloadedmetadata = () => {
        setVideoDuration(video.duration);
        setEndTime(video.duration);
        URL.revokeObjectURL(video.src);
      };
      video.src = url;
      
      return () => {
        URL.revokeObjectURL(url);
      };
    } else {
      setVideoPreview(null);
      setVideoDuration(10);
      setEndTime(10);
    }
  }, [videoFile]);

  const canEdit = useMemo(() => {
    if (!videoFile) return false;
    
    switch (operation) {
      case 'trim':
        return startTime < endTime && endTime <= videoDuration;
      case 'speed':
        return speedFactor > 0 && speedFactor <= 4.0;
      case 'stabilize':
        return smoothing >= 1 && smoothing <= 100;
      case 'text':
        return overlayText.trim().length > 0;
      case 'volume':
        return volumeFactor >= 0 && volumeFactor <= 5.0;
      case 'normalize':
        return targetLevel >= -50 && targetLevel <= 0;
      case 'denoise':
        return denoiseStrength >= 0 && denoiseStrength <= 1;
      default:
        return false;
    }
  }, [videoFile, operation, startTime, endTime, videoDuration, speedFactor, smoothing, overlayText, volumeFactor, targetLevel, denoiseStrength]);

  const costHint = useMemo(() => {
    if (!videoFile) return 'Upload a video to see cost';
    return 'Free (FFmpeg processing)';
  }, [videoFile]);

  const operationDescription = useMemo(() => {
    switch (operation) {
      case 'trim':
        return `Trim video from ${startTime.toFixed(1)}s to ${endTime.toFixed(1)}s (${(endTime - startTime).toFixed(1)}s output)`;
      case 'speed':
        const resultDuration = videoDuration / speedFactor;
        return `${speedFactor}x speed -> ${resultDuration.toFixed(1)}s output`;
      case 'stabilize':
        return `Stabilize with smoothing: ${smoothing} (higher = smoother)`;
      case 'text':
        return `Add "${overlayText.substring(0, 20)}${overlayText.length > 20 ? '...' : ''}" at ${textPosition}`;
      case 'volume':
        return `${volumeFactor === 0 ? 'Mute' : volumeFactor < 1 ? 'Reduce' : volumeFactor === 1 ? 'Keep' : 'Boost'} volume to ${Math.round(volumeFactor * 100)}%`;
      case 'normalize':
        return `Normalize audio to ${targetLevel} LUFS`;
      case 'denoise':
        return `Reduce noise at ${Math.round(denoiseStrength * 100)}% strength`;
      default:
        return '';
    }
  }, [operation, startTime, endTime, speedFactor, videoDuration, smoothing, overlayText, textPosition, volumeFactor, targetLevel, denoiseStrength]);

  const processVideo = useCallback(async (): Promise<void> => {
    if (!videoFile || !canEdit) return;

    setEditing(true);
    setProgress(0);
    setError(null);
    setResult(null);

    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 90) return prev;
        return prev + Math.random() * 10;
      });
    }, 1000);

    try {
      const formData = new FormData();
      formData.append('file', videoFile);

      let endpoint = '/api/video-studio/edit/';
      
      switch (operation) {
        case 'trim':
          endpoint += 'trim';
          formData.append('start_time', startTime.toString());
          formData.append('end_time', endTime.toString());
          if (maxDuration !== null) {
            formData.append('max_duration', maxDuration.toString());
          }
          formData.append('trim_mode', trimMode);
          break;
        case 'speed':
          endpoint += 'speed';
          formData.append('speed_factor', speedFactor.toString());
          break;
        case 'stabilize':
          endpoint += 'stabilize';
          formData.append('smoothing', smoothing.toString());
          break;
        case 'text':
          endpoint += 'text';
          formData.append('text', overlayText);
          formData.append('position', textPosition);
          formData.append('font_size', fontSize.toString());
          formData.append('font_color', fontColor);
          formData.append('background_color', backgroundColor);
          formData.append('start_time', textStartTime.toString());
          if (textEndTime !== null) {
            formData.append('end_time', textEndTime.toString());
          }
          break;
        case 'volume':
          endpoint += 'volume';
          formData.append('volume_factor', volumeFactor.toString());
          break;
        case 'normalize':
          endpoint += 'normalize';
          formData.append('target_level', targetLevel.toString());
          break;
        case 'denoise':
          endpoint += 'denoise';
          formData.append('strength', denoiseStrength.toString());
          break;
      }

      const response = await aiApiClient.post(endpoint, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      clearInterval(progressInterval);
      setProgress(100);
      setResult({
        video_url: response.data.video_url,
        cost: response.data.cost || 0,
        edit_type: response.data.edit_type,
      });
    } catch (err: any) {
      clearInterval(progressInterval);
      setError(err.response?.data?.detail || err.message || 'Video editing failed');
    } finally {
      setEditing(false);
    }
  }, [videoFile, canEdit, operation, startTime, endTime, maxDuration, trimMode, speedFactor, smoothing, overlayText, textPosition, fontSize, fontColor, backgroundColor, textStartTime, textEndTime, volumeFactor, targetLevel, denoiseStrength]);

  const reset = useCallback(() => {
    setVideoFile(null);
    setVideoPreview(null);
    setVideoDuration(10);
    setOperation('trim');
    setStartTime(0);
    setEndTime(10);
    setMaxDuration(null);
    setTrimMode('beginning');
    setSpeedFactor(1.0);
    setSmoothing(10);
    setOverlayText('');
    setTextPosition('center');
    setFontSize(48);
    setFontColor('white');
    setBackgroundColor('black@0.5');
    setTextStartTime(0);
    setTextEndTime(null);
    setVolumeFactor(1.0);
    setTargetLevel(-14);
    setDenoiseStrength(0.5);
    setEditing(false);
    setProgress(0);
    setError(null);
    setResult(null);
  }, []);

  return {
    // Video state
    videoFile,
    videoPreview,
    videoDuration,
    setVideoFile,
    
    // Operation
    operation,
    setOperation,
    
    // Trim settings
    startTime,
    endTime,
    maxDuration,
    trimMode,
    setStartTime,
    setEndTime,
    setMaxDuration,
    setTrimMode,
    
    // Speed settings
    speedFactor,
    setSpeedFactor,
    
    // Stabilization settings
    smoothing,
    setSmoothing,
    
    // Text overlay settings
    overlayText,
    textPosition,
    fontSize,
    fontColor,
    backgroundColor,
    textStartTime,
    textEndTime,
    setOverlayText,
    setTextPosition,
    setFontSize,
    setFontColor,
    setBackgroundColor,
    setTextStartTime,
    setTextEndTime,
    
    // Volume settings
    volumeFactor,
    setVolumeFactor,
    
    // Normalize settings
    targetLevel,
    setTargetLevel,
    
    // Denoise settings
    denoiseStrength,
    setDenoiseStrength,
    
    // State
    editing,
    progress,
    error,
    result,
    canEdit,
    costHint,
    operationDescription,
    
    // Actions
    processVideo,
    reset,
  };
};
