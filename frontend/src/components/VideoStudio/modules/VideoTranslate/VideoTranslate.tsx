import React from 'react';
import { Grid, Box, Button, Typography, Stack, CircularProgress, LinearProgress, Alert, Paper } from '@mui/material';
import { VideoStudioLayout } from '../../VideoStudioLayout';
import { useVideoTranslate } from './hooks/useVideoTranslate';
import { VideoUpload, LanguageSelector } from './components';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import TranslateIcon from '@mui/icons-material/Translate';

const VideoTranslate: React.FC = () => {
  const {
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
  } = useVideoTranslate();

  return (
    <VideoStudioLayout
      headerProps={{
        title: 'Video Translate Studio',
        subtitle: 'Translate videos to 70+ languages and 175+ dialects with AI. Preserves lip-sync and natural voice. Fast, accurate, and affordable at $0.0375/second.',
      }}
    >
      <Grid container spacing={4}>
        {/* Left Panel - Upload & Settings */}
        <Grid item xs={12} lg={5}>
          <Stack spacing={3}>
            <VideoUpload videoPreview={videoPreview} onVideoSelect={setVideoFile} />

            {videoFile && (
              <LanguageSelector
                outputLanguage={outputLanguage}
                supportedLanguages={supportedLanguages}
                onLanguageChange={setOutputLanguage}
              />
            )}

            <Box>
              <Button
                fullWidth
                variant="contained"
                size="large"
                startIcon={translating ? <CircularProgress size={20} color="inherit" /> : <TranslateIcon />}
                onClick={translateVideo}
                disabled={!canTranslate || translating}
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
                {translating ? 'Translating Video...' : 'Translate Video'}
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
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                  Pricing: $0.0375/second
                </Typography>
              </Box>
            )}

            {translating && (
              <Box>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  Progress: {progress}%
                </Typography>
                <LinearProgress variant="determinate" value={progress} />
              </Box>
            )}

            {error && (
              <Alert severity="error" onClose={() => {}}>
                {error}
              </Alert>
            )}
          </Stack>
        </Grid>

        {/* Right Panel - Preview & Result */}
        <Grid item xs={12} lg={7}>
          <Stack spacing={3}>
            {result ? (
              <Paper
                elevation={0}
                sx={{
                  p: 3,
                  borderRadius: 2,
                  border: '2px solid #10b981',
                  backgroundColor: '#f0fdf4',
                }}
              >
                <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
                  <CheckCircleIcon sx={{ color: '#10b981' }} />
                  <Typography variant="h6" sx={{ color: '#065f46', fontWeight: 700 }}>
                    Translation Complete!
                  </Typography>
                </Stack>

                <Box
                  sx={{
                    position: 'relative',
                    borderRadius: 2,
                    overflow: 'hidden',
                    border: '2px solid #e2e8f0',
                    backgroundColor: '#000',
                    mb: 2,
                  }}
                >
                  <video
                    src={result.video_url}
                    controls
                    style={{
                      width: '100%',
                      maxHeight: 500,
                      display: 'block',
                    }}
                  />
                </Box>

                <Stack spacing={1} sx={{ mb: 2 }}>
                  <Typography variant="body2">
                    <strong>Target Language:</strong> {result.output_language}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Cost:</strong> ${result.cost.toFixed(4)}
                  </Typography>
                </Stack>

                <Stack direction="row" spacing={2}>
                  <Button
                    variant="contained"
                    href={result.video_url}
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
                  <Button variant="outlined" onClick={reset}>
                    Translate Another
                  </Button>
                </Stack>
              </Paper>
            ) : videoPreview ? (
              <Paper
                elevation={0}
                sx={{
                  p: 3,
                  borderRadius: 2,
                  border: '1px solid #e2e8f0',
                  backgroundColor: '#ffffff',
                }}
              >
                <Typography
                  variant="subtitle2"
                  sx={{
                    mb: 2,
                    color: '#0f172a',
                    fontWeight: 700,
                  }}
                >
                  Source Video Preview
                </Typography>
                <Box
                  sx={{
                    position: 'relative',
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
                </Box>
              </Paper>
            ) : (
              <Paper
                elevation={0}
                sx={{
                  p: 6,
                  borderRadius: 2,
                  border: '2px dashed #cbd5e1',
                  backgroundColor: '#f8fafc',
                  textAlign: 'center',
                }}
              >
                <TranslateIcon sx={{ fontSize: 64, color: '#cbd5e1', mb: 2 }} />
                <Typography variant="body1" color="text.secondary">
                  Upload a video to get started
                </Typography>
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                  Your translated video will appear here
                </Typography>
              </Paper>
            )}
          </Stack>
        </Grid>
      </Grid>
    </VideoStudioLayout>
  );
};

export { VideoTranslate };
export default VideoTranslate;
