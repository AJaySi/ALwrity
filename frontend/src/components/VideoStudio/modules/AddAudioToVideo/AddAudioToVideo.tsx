import React from 'react';
import { Grid, Box, Button, Typography, Stack, CircularProgress, LinearProgress, Alert, Paper } from '@mui/material';
import { VideoStudioLayout } from '../../VideoStudioLayout';
import { useAddAudioToVideo } from './hooks/useAddAudioToVideo';
import { VideoUpload, AudioSettings } from './components';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import MusicNoteIcon from '@mui/icons-material/MusicNote';

const AddAudioToVideo: React.FC = () => {
  const {
    videoFile,
    videoPreview,
    model,
    prompt,
    seed,
    processing,
    progress,
    error,
    result,
    setVideoFile,
    setModel,
    setPrompt,
    setSeed,
    canAddAudio,
    costHint,
    addAudio,
    reset,
  } = useAddAudioToVideo();

  return (
    <VideoStudioLayout
      headerProps={{
        title: 'Add Audio to Video Studio',
        subtitle: 'Generate realistic Foley and ambient audio directly from video using Tencent Hunyuan\'s video-to-audio model. Aligns on-screen actions and scene context to produce timing-accurate, high-quality audio tracks with 48 kHz hi-fi output.',
      }}
    >
      <Grid container spacing={4}>
        {/* Left Panel - Upload & Settings */}
        <Grid item xs={12} lg={5}>
          <Stack spacing={3}>
            <VideoUpload videoPreview={videoPreview} onVideoSelect={setVideoFile} />

            <AudioSettings
              model={model}
              prompt={prompt}
              seed={seed}
              costHint={costHint}
              onModelChange={setModel}
              onPromptChange={setPrompt}
              onSeedChange={setSeed}
            />

            <Box>
              <Button
                fullWidth
                variant="contained"
                size="large"
                startIcon={processing ? <CircularProgress size={20} color="inherit" /> : <MusicNoteIcon />}
                onClick={addAudio}
                disabled={!canAddAudio || processing}
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
                {processing ? 'Processing...' : 'Add Audio to Video'}
              </Button>
            </Box>

            {processing && (
              <Box>
                <Stack spacing={1}>
                  <Typography variant="body2" color="text.secondary">
                    Generating audio... This may take a few minutes...
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
              <Alert severity="error" onClose={() => {}} icon={<ErrorIcon />}>
                {error}
              </Alert>
            )}

            {result && (
              <Alert
                severity="success"
                icon={<CheckCircleIcon />}
                action={
                  <Button size="small" onClick={reset}>
                    Process Another
                  </Button>
                }
              >
                Audio added successfully! Cost: ${result.cost.toFixed(4)}
              </Alert>
            )}
          </Stack>
        </Grid>

        {/* Right Panel - Preview & Results */}
        <Grid item xs={12} lg={7}>
          <Stack spacing={3}>
            {result ? (
              // Result view
              <Box>
                <Typography
                  variant="h6"
                  sx={{
                    mb: 2,
                    color: '#0f172a',
                    fontWeight: 700,
                  }}
                >
                  Video with Audio
                </Typography>
                <Box
                  sx={{
                    borderRadius: 2,
                    overflow: 'hidden',
                    border: '2px solid #10b981',
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
                  <Box sx={{ p: 2, backgroundColor: '#f0fdf4' }}>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#059669' }}>
                      Audio Added ({result.model_used})
                    </Typography>
                  </Box>
                </Box>

                <Stack direction="row" spacing={2}>
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
                    Download Video
                  </Button>
                  <Button variant="outlined" fullWidth onClick={reset}>
                    Process Another
                  </Button>
                </Stack>
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
                      Upload a video and configure audio settings to get started
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
                  Your video with audio will appear here
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
                About Audio Generation Models
              </Typography>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" sx={{ fontWeight: 600, color: '#0f172a', mb: 0.5 }}>
                  Hunyuan Video Foley:
                </Typography>
                <Stack component="ul" spacing={0.5} sx={{ pl: 2, m: 0 }}>
                  <Typography component="li" variant="body2" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                    Multi-scene synchronization – Audio aligned to complex, fast-cut visuals
                  </Typography>
                  <Typography component="li" variant="body2" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                    48 kHz hi-fi output – Professional clarity with low noise
                  </Typography>
                  <Typography component="li" variant="body2" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                    Pricing: $0.02/second
                  </Typography>
                </Stack>
              </Box>

              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" sx={{ fontWeight: 600, color: '#0f172a', mb: 0.5 }}>
                  Think Sound:
                </Typography>
                <Stack component="ul" spacing={0.5} sx={{ pl: 2, m: 0 }}>
                  <Typography component="li" variant="body2" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                    Context-aware sound – Analyzes visual elements to generate matching audio
                  </Typography>
                  <Typography component="li" variant="body2" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                    Prompt-guided output with built-in Prompt Enhancer for AI-assisted optimization
                  </Typography>
                  <Typography component="li" variant="body2" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                    High-quality output with clear, realistic audio
                  </Typography>
                  <Typography component="li" variant="body2" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                    Pricing: $0.05 per video (flat rate)
                  </Typography>
                </Stack>
              </Box>

              <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600, color: '#0f172a', fontSize: '0.875rem' }}>
                Pro Tips for Best Quality:
              </Typography>
              <Stack component="ul" spacing={0.5} sx={{ pl: 2, m: 0 }}>
                <Typography component="li" variant="body2" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                  Use videos with clear visuals and distinct actions for best audio matching
                </Typography>
                <Typography component="li" variant="body2" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                  Add prompts to specify the type of sound (e.g., "engine roaring", "footsteps on gravel")
                </Typography>
                <Typography component="li" variant="body2" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                  Ensure videos have visible sound-producing elements like movement or impacts
                </Typography>
                <Typography component="li" variant="body2" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                  Fix the seed when iterating to compare different prompt variations
                </Typography>
              </Stack>
            </Box>
          </Stack>
        </Grid>
      </Grid>
    </VideoStudioLayout>
  );
};

export { AddAudioToVideo };
export default AddAudioToVideo;
