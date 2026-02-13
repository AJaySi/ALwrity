import React from 'react';
import { Grid, Box, Button, Typography, Stack, CircularProgress, LinearProgress, Alert, Paper, Chip } from '@mui/material';
import { VideoStudioLayout } from '../../VideoStudioLayout';
import { useVideoBackgroundRemover } from './hooks/useVideoBackgroundRemover';
import { VideoUpload, BackgroundImageUpload } from './components';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import WallpaperIcon from '@mui/icons-material/Wallpaper';

const VideoBackgroundRemover: React.FC = () => {
  const {
    videoPreview,
    backgroundImageFile,
    backgroundImagePreview,
    removing,
    progress,
    error,
    result,
    setVideoFile,
    setBackgroundImageFile,
    canRemove,
    costHint,
    removeBackground,
    reset,
  } = useVideoBackgroundRemover();

  return (
    <VideoStudioLayout
      headerProps={{
        title: 'Background Remover Studio',
        subtitle: 'Remove or replace video backgrounds with clean matting and edge-aware blending. Upload a background image to replace, or leave empty for transparent background.',
      }}
    >
      <Grid container spacing={4}>
        {/* Left Panel - Upload & Settings */}
        <Grid item xs={12} lg={5}>
          <Stack spacing={3}>
            <VideoUpload videoPreview={videoPreview} onVideoSelect={setVideoFile} />

            <BackgroundImageUpload
              imagePreview={backgroundImagePreview}
              onImageSelect={setBackgroundImageFile}
            />

            <Paper
              elevation={0}
              sx={{
                p: 2,
                borderRadius: 2,
                backgroundColor: '#f1f5f9',
                border: '1px solid #e2e8f0',
              }}
            >
              <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                <Typography variant="body2" sx={{ fontWeight: 600, color: '#0f172a' }}>
                  Estimated Cost:
                </Typography>
                <Chip
                  label={costHint}
                  size="small"
                  sx={{
                    backgroundColor: '#3b82f6',
                    color: '#fff',
                    fontWeight: 600,
                  }}
                />
              </Stack>
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                Pricing: $0.01/second (min $0.05 for ≤5s, max $6.00 for 600s)
              </Typography>
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                Minimum: $0.05 | Maximum: $6.00 (10 minutes / 600 seconds)
              </Typography>
            </Paper>

            <Box>
              <Button
                fullWidth
                variant="contained"
                size="large"
                startIcon={removing ? <CircularProgress size={20} color="inherit" /> : <WallpaperIcon />}
                onClick={removeBackground}
                disabled={!canRemove || removing}
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
                {removing ? 'Processing...' : backgroundImageFile ? 'Replace Background' : 'Remove Background'}
              </Button>
            </Box>

            {removing && (
              <Box>
                <Stack spacing={1}>
                  <Typography variant="body2" color="text.secondary">
                    Processing video... This may take a few minutes...
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
                Background {result.has_background_replacement ? 'replaced' : 'removed'} successfully! Cost: ${result.cost.toFixed(4)}
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
                  Processed Video
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
                      {result.has_background_replacement ? 'Background Replaced' : 'Background Removed'}
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
                      Upload a video and optionally add a background image to get started
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
                  Your processed video will appear here
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
                About Background Removal
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                WaveSpeed Video Background Remover provides:
              </Typography>
              <Stack component="ul" spacing={0.5} sx={{ pl: 2, m: 0, mb: 2 }}>
                <Typography component="li" variant="body2" color="text.secondary">
                  Automatic background detection and removal
                </Typography>
                <Typography component="li" variant="body2" color="text.secondary">
                  Custom background replacement with your own images
                </Typography>
                <Typography component="li" variant="body2" color="text.secondary">
                  Transparent background support for further editing
                </Typography>
                <Typography component="li" variant="body2" color="text.secondary">
                  Production-ready quality with high-quality edge detection
                </Typography>
              </Stack>
              <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600, color: '#0f172a', fontSize: '0.875rem' }}>
                Tips for Best Results:
              </Typography>
              <Stack component="ul" spacing={0.5} sx={{ pl: 2, m: 0 }}>
                <Typography component="li" variant="body2" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                  Use videos with clear subject-background separation
                </Typography>
                <Typography component="li" variant="body2" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                  Ensure adequate lighting for better edge detection
                </Typography>
                <Typography component="li" variant="body2" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                  Use high-resolution images for replacement backgrounds
                </Typography>
                <Typography component="li" variant="body2" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                  Best results with landscape videos (16:9 ratio)
                </Typography>
              </Stack>
            </Box>
          </Stack>
        </Grid>
      </Grid>
    </VideoStudioLayout>
  );
};

export { VideoBackgroundRemover };
export default VideoBackgroundRemover;
