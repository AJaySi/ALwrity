import React, { useState, useEffect } from 'react';
import { Grid, Box, Button, Typography, Stack, CircularProgress, LinearProgress, Alert, Paper } from '@mui/material';
import { VideoStudioLayout } from '../../VideoStudioLayout';
import { useTransformVideo } from './hooks/useTransformVideo';
import {
  VideoUpload,
  TransformTabs,
  FormatConverter,
  AspectConverter,
  SpeedAdjuster,
  ResolutionScaler,
  Compressor,
} from './components';
import { aiApiClient } from '../../../../api/client';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';

const TransformVideo: React.FC = () => {
  const {
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
    setVideoFile,
    setTransformType,
    setOutputFormat,
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
    canTransform,
    costHint,
  } = useTransformVideo();

  const [transforming, setTransforming] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{ video_url: string; cost: number } | null>(null);

  const handleTransform = async () => {
    if (!videoFile) return;

    setTransforming(true);
    setError(null);
    setResult(null);
    setProgress(0);
    setStatusMessage('Starting video transformation...');

    try {
      // Create FormData
      const formData = new FormData();
      formData.append('file', videoFile);
      formData.append('transform_type', transformType);

      // Add transform-specific parameters
      if (transformType === 'format') {
        formData.append('output_format', outputFormat);
        if (codec) formData.append('codec', codec);
        formData.append('quality', quality);
        if (audioCodec) formData.append('audio_codec', audioCodec);
      } else if (transformType === 'aspect') {
        formData.append('target_aspect', targetAspect);
        formData.append('crop_mode', cropMode);
      } else if (transformType === 'speed') {
        formData.append('speed_factor', speedFactor.toString());
      } else if (transformType === 'resolution') {
        formData.append('target_resolution', targetResolution);
        formData.append('maintain_aspect', maintainAspect.toString());
      } else if (transformType === 'compress') {
        formData.append('compress_quality', compressQuality);
        if (targetSizeMb) {
          formData.append('target_size_mb', targetSizeMb.toString());
        }
      }

      // Submit transformation request
      setStatusMessage('Uploading video...');
      const response = await aiApiClient.post('/api/video-studio/transform', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const uploadProgress = Math.round((progressEvent.loaded * 20) / progressEvent.total);
            setProgress(uploadProgress);
            setStatusMessage(`Uploading video... ${uploadProgress}%`);
          }
        },
        timeout: 600000, // 10 minutes timeout for long videos
      });

      setProgress(30);
      setStatusMessage('Processing video... This may take a few minutes...');

      if (response.data.success) {
        setTransforming(false);
        setResult(response.data);
        setProgress(100);
        setStatusMessage('Video transformation complete!');
      } else {
        throw new Error(response.data.error || 'Transformation failed');
      }
    } catch (err: any) {
      setTransforming(false);
      setError(err.response?.data?.detail || err.message || 'Failed to transform video');
      setStatusMessage('Transformation failed');
    }
  };

  const handleReset = () => {
    setTransforming(false);
    setProgress(0);
    setStatusMessage('');
    setError(null);
    setResult(null);
  };

  const renderTransformSettings = () => {
    switch (transformType) {
      case 'format':
        return (
          <FormatConverter
            outputFormat={outputFormat}
            codec={codec}
            quality={quality}
            audioCodec={audioCodec}
            onOutputFormatChange={setOutputFormat}
            onCodecChange={setCodec}
            onQualityChange={setQuality}
            onAudioCodecChange={setAudioCodec}
          />
        );
      case 'aspect':
        return (
          <AspectConverter
            targetAspect={targetAspect}
            cropMode={cropMode}
            onTargetAspectChange={setTargetAspect}
            onCropModeChange={setCropMode}
          />
        );
      case 'speed':
        return (
          <SpeedAdjuster
            speedFactor={speedFactor}
            onSpeedFactorChange={setSpeedFactor}
          />
        );
      case 'resolution':
        return (
          <ResolutionScaler
            targetResolution={targetResolution}
            maintainAspect={maintainAspect}
            onTargetResolutionChange={setTargetResolution}
            onMaintainAspectChange={setMaintainAspect}
          />
        );
      case 'compress':
        return (
          <Compressor
            targetSizeMb={targetSizeMb}
            compressQuality={compressQuality}
            onTargetSizeMbChange={setTargetSizeMb}
            onCompressQualityChange={setCompressQuality}
          />
        );
      default:
        return null;
    }
  };

  return (
    <VideoStudioLayout
      headerProps={{
        title: 'Transform Studio',
        subtitle: 'Convert formats, change aspect ratios, adjust speed, scale resolution, and compress videos. All transformations use FFmpeg processing (free).',
      }}
    >
      <Grid container spacing={4}>
        {/* Left Panel - Upload & Settings */}
        <Grid item xs={12} lg={5}>
          <Stack spacing={3}>
            <VideoUpload videoPreview={videoPreview} onVideoSelect={setVideoFile} />

            {videoFile && (
              <>
                <TransformTabs
                  transformType={transformType}
                  onTransformTypeChange={setTransformType}
                />

                <Paper
                  elevation={0}
                  sx={{
                    p: 3,
                    borderRadius: 2,
                    border: '1px solid #e2e8f0',
                    backgroundColor: '#ffffff',
                  }}
                >
                  {renderTransformSettings()}
                </Paper>
              </>
            )}

            <Box>
              <Button
                fullWidth
                variant="contained"
                size="large"
                startIcon={transforming ? <CircularProgress size={20} color="inherit" /> : <PlayArrowIcon />}
                onClick={handleTransform}
                disabled={!canTransform || transforming}
                sx={{
                  py: 1.5,
                  backgroundColor: '#3b82f6',
                  '&:hover': {
                    backgroundColor: '#2563eb',
                  },
                  '&:disabled': {
                    backgroundColor: '#cbd5e1',
                    color: '#94a3b8',
                  },
                }}
              >
                {transforming ? 'Transforming...' : 'Transform Video'}
              </Button>
            </Box>

            {videoFile && (
              <Box
                sx={{
                  p: 2,
                  borderRadius: 1,
                  backgroundColor: '#f1f5f9',
                  border: '1px solid #e2e8f0',
                }}
              >
                <Typography variant="body2" color="text.secondary">
                  <strong>Cost:</strong> {costHint}
                </Typography>
              </Box>
            )}

            {transforming && (
              <Box>
                <Stack spacing={1}>
                  <Typography variant="body2" color="text.secondary">
                    {statusMessage}
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={progress}
                    sx={{
                      height: 8,
                      borderRadius: 1,
                      backgroundColor: '#e2e8f0',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: '#3b82f6',
                      },
                    }}
                  />
                </Stack>
              </Box>
            )}

            {error && (
              <Alert severity="error" onClose={() => setError(null)}>
                {error}
              </Alert>
            )}

            {result && (
              <Alert
                severity="success"
                icon={<CheckCircleIcon />}
                action={
                  <Button size="small" onClick={handleReset}>
                    Transform Another
                  </Button>
                }
              >
                Video transformed successfully! Cost: ${result.cost.toFixed(2)}
              </Alert>
            )}
          </Stack>
        </Grid>

        {/* Right Panel - Preview & Results */}
        <Grid item xs={12} lg={7}>
          <Stack spacing={3}>
            <Box>
              <Typography
                variant="h6"
                sx={{
                  mb: 2,
                  color: '#0f172a',
                  fontWeight: 700,
                }}
              >
                Preview
              </Typography>

              {videoPreview && !result && (
                <Box
                  sx={{
                    borderRadius: 2,
                    overflow: 'hidden',
                    border: '2px solid #e2e8f0',
                    backgroundColor: '#000',
                  }}
                >
                  <video
                    src={videoPreview}
                    controls
                    style={{
                      width: '100%',
                      maxHeight: 500,
                      display: 'block',
                    }}
                  />
                  <Box sx={{ p: 2, backgroundColor: '#f8fafc' }}>
                    <Typography variant="caption" color="text.secondary">
                      Original Video
                    </Typography>
                  </Box>
                </Box>
              )}

              {result && (
                <Box>
                  <Box
                    sx={{
                      borderRadius: 2,
                      overflow: 'hidden',
                      border: '2px solid #3b82f6',
                      backgroundColor: '#000',
                      mb: 2,
                    }}
                  >
                    <video
                      src={result.video_url.startsWith('http') ? result.video_url : `${window.location.origin}${result.video_url}`}
                      controls
                      style={{
                        width: '100%',
                        maxHeight: 500,
                        display: 'block',
                      }}
                    />
                    <Box sx={{ p: 2, backgroundColor: '#f0f9ff' }}>
                      <Typography variant="body2" sx={{ fontWeight: 600, color: '#0f172a' }}>
                        Transformed Video ({transformType})
                      </Typography>
                    </Box>
                  </Box>

                  <Stack direction="row" spacing={2}>
                    <Button
                      variant="outlined"
                      fullWidth
                      href={result.video_url.startsWith('http') ? result.video_url : `${window.location.origin}${result.video_url}`}
                      download
                    >
                      Download Transformed Video
                    </Button>
                    <Button variant="outlined" fullWidth onClick={handleReset}>
                      Transform Another Video
                    </Button>
                  </Stack>
                </Box>
              )}

              {!videoPreview && !result && (
                <Box
                  sx={{
                    border: '2px dashed #cbd5e1',
                    borderRadius: 2,
                    p: 6,
                    textAlign: 'center',
                    backgroundColor: '#f8fafc',
                  }}
                >
                  <Typography variant="body2" color="text.secondary">
                    Upload a video to see preview
                  </Typography>
                </Box>
              )}
            </Box>

            {/* Info Box */}
            <Box
              sx={{
                p: 2,
                borderRadius: 2,
                backgroundColor: '#f1f5f9',
                border: '1px solid #e2e8f0',
              }}
            >
              <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600, color: '#0f172a' }}>
                About Transform Studio
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                Transform Studio uses FFmpeg for fast, free video processing:
              </Typography>
              <Stack component="ul" spacing={0.5} sx={{ pl: 2, m: 0 }}>
                <Typography component="li" variant="body2" color="text.secondary">
                  Format conversion: MP4, MOV, WebM, GIF
                </Typography>
                <Typography component="li" variant="body2" color="text.secondary">
                  Aspect ratio conversion with smart cropping
                </Typography>
                <Typography component="li" variant="body2" color="text.secondary">
                  Speed adjustment (0.25x to 4x)
                </Typography>
                <Typography component="li" variant="body2" color="text.secondary">
                  Resolution scaling (480p to 4K)
                </Typography>
                <Typography component="li" variant="body2" color="text.secondary">
                  File size compression
                </Typography>
              </Stack>
            </Box>
          </Stack>
        </Grid>
      </Grid>
    </VideoStudioLayout>
  );
};

export default TransformVideo;
export { TransformVideo };
