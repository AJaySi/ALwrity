import React, { useState } from 'react';
import { Grid, Box, Button, Typography, Stack, CircularProgress, LinearProgress, Alert } from '@mui/material';
import { VideoStudioLayout } from '../../VideoStudioLayout';
import { useExtendVideo } from './hooks/useExtendVideo';
import { VideoUpload, AudioUpload, ExtendSettings } from './components';
import { aiApiClient } from '../../../../api/client';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';

const ExtendVideo: React.FC = () => {
  const {
    videoFile,
    videoPreview,
    audioFile,
    prompt,
    negativePrompt,
    model,
    resolution,
    duration,
    enablePromptExpansion,
    generateAudio,
    cameraFixed,
    seed,
    setVideoFile,
    setAudioFile,
    setPrompt,
    setNegativePrompt,
    setModel,
    setResolution,
    setDuration,
    setEnablePromptExpansion,
    setGenerateAudio,
    setCameraFixed,
    setSeed,
    canExtend,
    costHint,
  } = useExtendVideo();

  const [extending, setExtending] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{ video_url: string; cost: number; duration: number } | null>(null);

  const handleExtend = async () => {
    if (!videoFile || !prompt.trim()) return;

    setExtending(true);
    setError(null);
    setResult(null);
    setProgress(0);
    setStatusMessage('Starting video extension...');

    try {
      // Create FormData
      const formData = new FormData();
      formData.append('file', videoFile);
      formData.append('prompt', prompt);
      formData.append('model', model);
      if (negativePrompt && model === 'wan-2.5') {
        formData.append('negative_prompt', negativePrompt);
      }
      if (audioFile && model === 'wan-2.5') {
        formData.append('audio', audioFile);
      }
      formData.append('resolution', resolution);
      formData.append('duration', duration.toString());
      if (model === 'wan-2.5') {
        formData.append('enable_prompt_expansion', enablePromptExpansion.toString());
      }
      if (model === 'seedance-1.5-pro') {
        formData.append('generate_audio', generateAudio.toString());
        formData.append('camera_fixed', cameraFixed.toString());
      }
      if (seed !== null) {
        formData.append('seed', seed.toString());
      }

      // Submit extension request
      setStatusMessage('Uploading video...');
      const response = await aiApiClient.post('/api/video-studio/extend', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const uploadProgress = Math.round((progressEvent.loaded * 30) / progressEvent.total);
            setProgress(uploadProgress);
            setStatusMessage(`Uploading... ${uploadProgress}%`);
          }
        },
        timeout: 600000, // 10 minutes timeout
      });

      setProgress(40);
      setStatusMessage('Extending video with WAN 2.5... This may take a few minutes...');

      if (response.data.success) {
        setExtending(false);
        setResult(response.data);
        setProgress(100);
        setStatusMessage('Video extension complete!');
      } else {
        throw new Error(response.data.error || 'Extension failed');
      }
    } catch (err: any) {
      setExtending(false);
      setError(err.response?.data?.detail || err.message || 'Failed to extend video');
      setStatusMessage('Extension failed');
    }
  };

  const handleReset = () => {
    setExtending(false);
    setProgress(0);
    setStatusMessage('');
    setError(null);
    setResult(null);
  };

  return (
    <VideoStudioLayout
      headerProps={{
        title: 'Extend Studio',
        subtitle: 'Extend your short video clips into longer videos with motion and audio continuity. Perfect for creating seamless extended scenes from existing footage.',
      }}
    >
      <Grid container spacing={4}>
        {/* Left Panel - Upload & Settings */}
        <Grid item xs={12} lg={5}>
          <Stack spacing={3}>
            <VideoUpload videoPreview={videoPreview} onVideoSelect={setVideoFile} />

            {model === 'wan-2.5' && (
              <AudioUpload audioPreview={null} onAudioSelect={setAudioFile} />
            )}

            <ExtendSettings
              model={model}
              prompt={prompt}
              negativePrompt={negativePrompt}
              resolution={resolution}
              duration={duration}
              enablePromptExpansion={enablePromptExpansion}
              generateAudio={generateAudio}
              cameraFixed={cameraFixed}
              seed={seed}
              costHint={costHint}
              onModelChange={setModel}
              onPromptChange={setPrompt}
              onNegativePromptChange={setNegativePrompt}
              onResolutionChange={setResolution}
              onDurationChange={setDuration}
              onEnablePromptExpansionChange={setEnablePromptExpansion}
              onGenerateAudioChange={setGenerateAudio}
              onCameraFixedChange={setCameraFixed}
              onSeedChange={setSeed}
            />

            <Box>
              <Button
                fullWidth
                variant="contained"
                size="large"
                startIcon={extending ? <CircularProgress size={20} color="inherit" /> : <PlayArrowIcon />}
                onClick={handleExtend}
                disabled={!canExtend || extending}
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
                {extending ? 'Extending...' : 'Extend Video'}
              </Button>
            </Box>

            {extending && (
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
                    Extend Another
                  </Button>
                }
              >
                Video extended successfully! Cost: ${result.cost.toFixed(2)} ({result.duration}s)
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
                        Extended Video ({result.duration}s @ {resolution.toUpperCase()})
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
                      Download Extended Video
                    </Button>
                    <Button variant="outlined" fullWidth onClick={handleReset}>
                      Extend Another Video
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
                About Video Extension
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                WAN 2.5 Video-Extend creates seamless extensions of your videos with:
              </Typography>
              <Stack component="ul" spacing={0.5} sx={{ pl: 2, m: 0 }}>
                <Typography component="li" variant="body2" color="text.secondary">
                  Motion continuity for smooth transitions
                </Typography>
                <Typography component="li" variant="body2" color="text.secondary">
                  Audio synchronization when audio is provided (3-30s, ≤15MB)
                </Typography>
                <Typography component="li" variant="body2" color="text.secondary">
                  Natural scene continuation with preserved style
                </Typography>
                <Typography component="li" variant="body2" color="text.secondary">
                  Multilingual support (Chinese and English prompts)
                </Typography>
                <Typography component="li" variant="body2" color="text.secondary">
                  Auto-generated audio if no audio is provided
                </Typography>
              </Stack>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block', fontStyle: 'italic' }}>
                Note: If audio is longer than video duration, only the first segment is used. If audio is shorter, remaining video plays silently.
              </Typography>
            </Box>
          </Stack>
        </Grid>
      </Grid>
    </VideoStudioLayout>
  );
};

export default ExtendVideo;
export { ExtendVideo };
