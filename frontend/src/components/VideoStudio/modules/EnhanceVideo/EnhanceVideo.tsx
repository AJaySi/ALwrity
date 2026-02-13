import React, { useState, useEffect } from 'react';
import { Grid, Box, Button, Typography, Stack, CircularProgress, LinearProgress, Alert } from '@mui/material';
import { VideoStudioLayout } from '../../VideoStudioLayout';
import { useEnhanceVideo } from './hooks/useEnhanceVideo';
import { VideoUpload, EnhancementSettings } from './components';
import { aiApiClient } from '../../../../api/client';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';

const EnhanceVideo: React.FC = () => {
  const {
    videoFile,
    videoPreview,
    targetResolution,
    enhancementType,
    setVideoFile,
    setTargetResolution,
    setEnhancementType,
    canEnhance,
    costHint,
  } = useEnhanceVideo();

  const [enhancing, setEnhancing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{ video_url: string; cost: number } | null>(null);
  const [progressInterval, setProgressInterval] = useState<NodeJS.Timeout | null>(null);

  // Cleanup progress interval on unmount
  useEffect(() => {
    return () => {
      if (progressInterval) {
        clearInterval(progressInterval);
      }
    };
  }, [progressInterval]);

  const handleEnhance = async () => {
    if (!videoFile) return;

    setEnhancing(true);
    setError(null);
    setResult(null);
    setProgress(0);
    setStatusMessage('Starting video enhancement...');

    try {
      // Create FormData
      const formData = new FormData();
      formData.append('file', videoFile);
      formData.append('enhancement_type', enhancementType);
      formData.append('target_resolution', targetResolution);
      formData.append('provider', 'wavespeed');
      formData.append('model', 'flashvsr');

      // Submit enhancement request
      setStatusMessage('Uploading video...');
      const response = await aiApiClient.post('/api/video-studio/enhance', formData, {
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
      setStatusMessage('Processing video with FlashVSR... This may take a few minutes...');

      // FlashVSR processing can take 3-20 seconds per 1 second of video
      // Simulate progress updates while waiting for response
      let simulatedProgress = 30;
      const interval = setInterval(() => {
        simulatedProgress = Math.min(90, simulatedProgress + 5);
        setProgress(simulatedProgress);
        setStatusMessage(`Processing... ${simulatedProgress}% (This may take several minutes for long videos)`);
      }, 2000);
      setProgressInterval(interval);

      try {
        if (response.data.success) {
          clearInterval(interval);
          setProgressInterval(null);
          setEnhancing(false);
          setResult(response.data);
          setProgress(100);
          setStatusMessage('Video enhancement complete!');
        } else {
          clearInterval(interval);
          setProgressInterval(null);
          throw new Error(response.data.error || 'Enhancement failed');
        }
      } catch (err) {
        clearInterval(interval);
        setProgressInterval(null);
        throw err;
      }
    } catch (err: any) {
      if (progressInterval) {
        clearInterval(progressInterval);
        setProgressInterval(null);
      }
      setEnhancing(false);
      setProgress(0);
      setError(err.response?.data?.detail || err.message || 'Failed to enhance video');
      setStatusMessage('Enhancement failed');
    }
  };

  const handleReset = () => {
    setEnhancing(false);
    setProgress(0);
    setStatusMessage('');
    setError(null);
    setResult(null);
    if (progressInterval) {
      clearInterval(progressInterval);
      setProgressInterval(null);
    }
  };

  return (
    <VideoStudioLayout
      headerProps={{
        title: 'Enhance Studio',
        subtitle: 'Upscale your videos to higher resolutions with FlashVSR. Improve video quality, restore clarity, and prepare content for professional delivery.',
      }}
    >
      <Grid container spacing={4}>
        {/* Left Panel - Upload & Settings */}
        <Grid item xs={12} lg={5}>
          <Stack spacing={3}>
            <VideoUpload videoPreview={videoPreview} onVideoSelect={setVideoFile} />

            <EnhancementSettings
              targetResolution={targetResolution}
              enhancementType={enhancementType}
              costHint={costHint}
              onTargetResolutionChange={setTargetResolution}
              onEnhancementTypeChange={setEnhancementType}
            />

            <Box>
              <Button
                fullWidth
                variant="contained"
                size="large"
                startIcon={enhancing ? <CircularProgress size={20} color="inherit" /> : <PlayArrowIcon />}
                onClick={handleEnhance}
                disabled={!canEnhance || enhancing}
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
                {enhancing ? 'Enhancing...' : 'Enhance Video'}
              </Button>
            </Box>

            {enhancing && (
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

          </Stack>
        </Grid>

        {/* Right Panel - Preview & Results */}
        <Grid item xs={12} lg={7}>
          <Stack spacing={3}>
            {result ? (
              // Side-by-side comparison view
              <Box>
                <Typography
                  variant="h6"
                  sx={{
                    mb: 2,
                    color: '#0f172a',
                    fontWeight: 700,
                  }}
                >
                  Comparison
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Box
                      sx={{
                        borderRadius: 2,
                        overflow: 'hidden',
                        border: '2px solid #e2e8f0',
                        backgroundColor: '#000',
                      }}
                    >
                      <video
                        src={videoPreview || ''}
                        controls
                        style={{
                          width: '100%',
                          maxHeight: 400,
                          display: 'block',
                        }}
                      />
                      <Box sx={{ p: 1.5, backgroundColor: '#f8fafc' }}>
                        <Typography variant="caption" sx={{ fontWeight: 600, color: '#64748b' }}>
                          Original Video
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Box
                      sx={{
                        borderRadius: 2,
                        overflow: 'hidden',
                        border: '2px solid #10b981',
                        backgroundColor: '#000',
                      }}
                    >
                      <video
                        src={result.video_url.startsWith('http') ? result.video_url : `${window.location.origin}${result.video_url}`}
                        controls
                        style={{
                          width: '100%',
                          maxHeight: 400,
                          display: 'block',
                        }}
                      />
                      <Box sx={{ p: 1.5, backgroundColor: '#f0fdf4' }}>
                        <Typography variant="caption" sx={{ fontWeight: 600, color: '#059669' }}>
                          Enhanced ({targetResolution.toUpperCase()})
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                </Grid>

                <Stack direction="row" spacing={2} sx={{ mt: 2 }}>
                  <Button
                    variant="contained"
                    fullWidth
                    href={result.video_url.startsWith('http') ? result.video_url : `${window.location.origin}${result.video_url}`}
                    download
                    sx={{
                      backgroundColor: '#10b981',
                      '&:hover': {
                        backgroundColor: '#059669',
                      },
                    }}
                  >
                    Download Enhanced Video
                  </Button>
                  <Button variant="outlined" fullWidth onClick={handleReset}>
                    Enhance Another
                  </Button>
                </Stack>

                <Box
                  sx={{
                    mt: 2,
                    p: 2,
                    borderRadius: 2,
                    backgroundColor: '#f0fdf4',
                    border: '1px solid #10b981',
                  }}
                >
                  <Stack spacing={1}>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#065f46' }}>
                      Enhancement Complete!
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Cost: ${result.cost.toFixed(4)} | Resolution: {targetResolution.toUpperCase()}
                    </Typography>
                  </Stack>
                </Box>
              </Box>
            ) : videoPreview ? (
              // Original video preview
              <Box>
                <Typography
                  variant="h6"
                  sx={{
                    mb: 2,
                    color: '#0f172a',
                    fontWeight: 700,
                  }}
                >
                  Original Video Preview
                </Typography>
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
                    <Typography variant="body2" color="text.secondary">
                      Upload a video and select enhancement options to get started
                    </Typography>
                  </Box>
                </Box>
              </Box>
            ) : (
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
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                  Your enhanced video will appear here
                </Typography>
              </Box>
            )}

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
                About FlashVSR
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                FlashVSR is the most advanced video upscaler, delivering:
              </Typography>
              <Stack component="ul" spacing={0.5} sx={{ pl: 2, m: 0 }}>
                <Typography component="li" variant="body2" color="text.secondary">
                  Temporal consistency for stable motion
                </Typography>
                <Typography component="li" variant="body2" color="text.secondary">
                  Detail reconstruction for fine textures
                </Typography>
                <Typography component="li" variant="body2" color="text.secondary">
                  Artifact cleanup for compression blocks
                </Typography>
                <Typography component="li" variant="body2" color="text.secondary">
                  Natural look without overprocessing
                </Typography>
              </Stack>
            </Box>
          </Stack>
        </Grid>
      </Grid>
    </VideoStudioLayout>
  );
};

export default EnhanceVideo;
export { EnhanceVideo };
