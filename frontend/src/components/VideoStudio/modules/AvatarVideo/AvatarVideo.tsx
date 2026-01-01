import React, { useState } from 'react';
import { Grid, Box, Button, Typography, Stack, CircularProgress } from '@mui/material';
import { VideoStudioLayout } from '../../VideoStudioLayout';
import { useAvatarVideo } from './hooks/useAvatarVideo';
import { ImageUpload, AudioUpload, AvatarSettings } from './components';
import { aiApiClient } from '../../../../api/client';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';

export const AvatarVideo: React.FC = () => {
  const {
    imageFile,
    imagePreview,
    audioFile,
    audioPreview,
    resolution,
    model,
    prompt,
    seed,
    setImageFile,
    setAudioFile,
    setResolution,
    setModel,
    setPrompt,
    setSeed,
    canGenerate,
    costHint,
  } = useAvatarVideo();

  const [generating, setGenerating] = useState(false);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{ video_url: string; cost: number } | null>(null);

  const handleGenerate = async () => {
    if (!imageFile || !audioFile) return;

    setGenerating(true);
    setError(null);
    setResult(null);
    setProgress(0);
    setStatusMessage('Starting avatar generation...');

    try {
      // Create FormData
      const formData = new FormData();
      formData.append('image', imageFile);
      formData.append('audio', audioFile);
      formData.append('resolution', resolution);
      formData.append('model', model);
      if (prompt) {
        formData.append('prompt', prompt);
      }
      if (seed !== null) {
        formData.append('seed', seed.toString());
      }

      // Submit generation request
      const response = await aiApiClient.post('/api/video-studio/avatar/create-async', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const { task_id } = response.data;
      setTaskId(task_id);
      setStatusMessage('Avatar generation started. Polling for updates...');

      // Poll for status
      const pollInterval = setInterval(async () => {
        try {
          const statusResponse = await aiApiClient.get(`/api/video-studio/task/${task_id}/status`);
          const status = statusResponse.data;

          setProgress(status.progress || 0);
          setStatusMessage(status.message || 'Processing...');

          if (status.status === 'completed') {
            clearInterval(pollInterval);
            setGenerating(false);
            setResult(status.result);
            setStatusMessage('Avatar generation complete!');
          } else if (status.status === 'failed') {
            clearInterval(pollInterval);
            setGenerating(false);
            setError(status.error || 'Avatar generation failed');
            setStatusMessage('Generation failed');
          }
        } catch (err: any) {
          console.error('Polling error:', err);
          // Continue polling on transient errors
        }
      }, 2000); // Poll every 2 seconds

      // Cleanup on unmount
      return () => clearInterval(pollInterval);
    } catch (err: any) {
      setGenerating(false);
      setError(err.response?.data?.detail || err.message || 'Failed to start avatar generation');
      setStatusMessage('Failed to start generation');
    }
  };

  return (
    <VideoStudioLayout
      headerProps={{
        title: "Avatar Studio",
        subtitle: "Create talking videos from photos",
      }}
    >
      <Grid container spacing={4}>
        {/* Left Panel: Uploads and Settings */}
        <Grid item xs={12} md={6}>
          <Stack spacing={3}>
            <ImageUpload
              imagePreview={imagePreview}
              onImageSelect={setImageFile}
            />

            <AudioUpload
              audioPreview={audioPreview}
              onAudioSelect={setAudioFile}
            />

            <AvatarSettings
              resolution={resolution}
              model={model}
              prompt={prompt}
              seed={seed}
              onResolutionChange={setResolution}
              onModelChange={setModel}
              onPromptChange={setPrompt}
              onSeedChange={setSeed}
            />

            {/* Cost and Generate */}
            <Box
              sx={{
                p: 3,
                borderRadius: 2,
                backgroundColor: '#f8fafc',
                border: '1px solid #e2e8f0',
              }}
            >
              <Stack spacing={2}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="body2" color="text.secondary">
                    Estimated Cost
                  </Typography>
                  <Typography variant="h6" fontWeight={700} color="#3b82f6">
                    {costHint}
                  </Typography>
                </Box>

                {error && (
                  <Typography variant="body2" color="error">
                    {error}
                  </Typography>
                )}

                {generating && (
                  <Box>
                    <Stack direction="row" spacing={2} alignItems="center">
                      <CircularProgress size={20} />
                      <Typography variant="body2" color="text.secondary">
                        {statusMessage}
                      </Typography>
                    </Stack>
                    {progress > 0 && (
                      <Box sx={{ mt: 1 }}>
                        <Typography variant="caption" color="text.secondary">
                          Progress: {progress.toFixed(0)}%
                        </Typography>
                      </Box>
                    )}
                  </Box>
                )}

                <Button
                  variant="contained"
                  size="large"
                  fullWidth
                  startIcon={generating ? <CircularProgress size={20} color="inherit" /> : <PlayArrowIcon />}
                  onClick={handleGenerate}
                  disabled={!canGenerate || generating}
                  sx={{
                    py: 1.5,
                    borderRadius: 2,
                    backgroundColor: '#3b82f6',
                    '&:hover': {
                      backgroundColor: '#2563eb',
                    },
                  }}
                >
                  {generating ? 'Generating...' : 'Create Avatar'}
                </Button>
              </Stack>
            </Box>
          </Stack>
        </Grid>

        {/* Right Panel: Preview/Result */}
        <Grid item xs={12} md={6}>
          <Box
            sx={{
              p: 3,
              borderRadius: 2,
              backgroundColor: '#f8fafc',
              border: '1px solid #e2e8f0',
              minHeight: 400,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {result ? (
              <Stack spacing={2} alignItems="center">
                <Typography variant="h6" fontWeight={700}>
                  Avatar Generated!
                </Typography>
                <video
                  src={result.video_url}
                  controls
                  style={{
                    maxWidth: '100%',
                    maxHeight: 500,
                    borderRadius: 8,
                  }}
                />
                <Typography variant="body2" color="text.secondary">
                  Cost: ${result.cost.toFixed(2)}
                </Typography>
              </Stack>
            ) : (
              <Typography variant="body2" color="text.secondary" textAlign="center">
                {imagePreview && audioPreview
                  ? 'Upload your photo and audio, then click "Create Avatar" to generate your talking avatar.'
                  : 'Upload a photo and audio to create your talking avatar.'}
              </Typography>
            )}
          </Box>
        </Grid>
      </Grid>
    </VideoStudioLayout>
  );
};

export default AvatarVideo;
