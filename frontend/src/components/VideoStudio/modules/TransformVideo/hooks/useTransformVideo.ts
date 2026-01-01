import { useState, useMemo, useCallback } from 'react';

export type TransformType = 'format' | 'aspect' | 'speed' | 'resolution' | 'compress';
export type OutputFormat = 'mp4' | 'mov' | 'webm' | 'gif';
export type AspectRatio = '16:9' | '9:16' | '1:1' | '4:5' | '21:9';
export type Quality = 'high' | 'medium' | 'low';
export type Resolution = '480p' | '720p' | '1080p' | '1440p' | '4k';

export const useTransformVideo = () => {
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [videoPreview, setVideoPreview] = useState<string | null>(null);
  const [transformType, setTransformType] = useState<TransformType>('format');
  
  // Format conversion state
  const [outputFormat, setOutputFormat] = useState<OutputFormat>('mp4');
  const [codec, setCodec] = useState<string>('libx264');
  const [quality, setQuality] = useState<Quality>('medium');
  const [audioCodec, setAudioCodec] = useState<string>('aac');
  
  // Aspect ratio state
  const [targetAspect, setTargetAspect] = useState<AspectRatio>('16:9');
  const [cropMode, setCropMode] = useState<'center' | 'letterbox'>('center');
  
  // Speed state
  const [speedFactor, setSpeedFactor] = useState<number>(1.0);
  
  // Resolution state
  const [targetResolution, setTargetResolution] = useState<Resolution>('720p');
  const [maintainAspect, setMaintainAspect] = useState<boolean>(true);
  
  // Compression state
  const [targetSizeMb, setTargetSizeMb] = useState<number | null>(null);
  const [compressQuality, setCompressQuality] = useState<Quality>('medium');

  // Cost hint (FFmpeg operations are free)
  const costHint = useMemo(() => {
    if (!videoFile) return 'Upload a video to transform';
    return 'Free (FFmpeg processing)';
  }, [videoFile]);

  const canTransform = useMemo(() => {
    if (!videoFile) return false;
    
    // Validate based on transform type
    switch (transformType) {
      case 'format':
        return !!outputFormat;
      case 'aspect':
        return !!targetAspect;
      case 'speed':
        return speedFactor > 0 && speedFactor <= 4.0;
      case 'resolution':
        return !!targetResolution;
      case 'compress':
        return true; // Always valid
      default:
        return false;
    }
  }, [videoFile, transformType, outputFormat, targetAspect, speedFactor, targetResolution]);

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

  // Update codec based on format
  const handleFormatChange = useCallback((format: OutputFormat) => {
    setOutputFormat(format);
    // Auto-select appropriate codec
    if (format === 'webm') {
      setCodec('libvpx-vp9');
      setAudioCodec('libopus');
    } else if (format === 'gif') {
      setCodec('');
      setAudioCodec('');
    } else {
      setCodec('libx264');
      setAudioCodec('aac');
    }
  }, []);

  return {
    // State
    videoFile,
    videoPreview,
    transformType,
    outputFormat,
    codec,
    quality,
    audioCodec,
    targetAspect,
    cropMode,
    speedFactor,
    targetResolution,
    maintainAspect,
    targetSizeMb,
    compressQuality,
    // Setters
    setVideoFile: handleVideoSelect,
    setTransformType,
    setOutputFormat: handleFormatChange,
    setCodec,
    setQuality,
    setAudioCodec,
    setTargetAspect,
    setCropMode,
    setSpeedFactor,
    setTargetResolution,
    setMaintainAspect,
    setTargetSizeMb,
    setCompressQuality,
    // Computed
    canTransform,
    costHint,
  };
};
