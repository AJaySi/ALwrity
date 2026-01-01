import React from 'react';
import { Grid, Box, Button, Typography, Stack, CircularProgress, LinearProgress, Alert, Paper } from '@mui/material';
import { VideoStudioLayout } from '../../VideoStudioLayout';
import { useSocialVideo } from './hooks/useSocialVideo';
import { VideoUpload, PlatformSelector, OptimizationOptions, PreviewGrid } from './components';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import DownloadIcon from '@mui/icons-material/Download';

const SocialVideo: React.FC = () => {
  const {
    videoFile,
    videoPreview,
    selectedPlatforms,
    autoCrop,
    generateThumbnails,
    compress,
    trimMode,
    optimizing,
    progress,
    results,
    errors,
    platformSpecs,
    setVideoFile,
    togglePlatform,
    setAutoCrop,
    setGenerateThumbnails,
    setCompress,
    setTrimMode,
    canOptimize,
    costHint,
    optimize,
    reset,
  } = useSocialVideo();

  const handleDownload = (result: any) => {
    const videoUrl = result.video_url.startsWith('http')
      ? result.video_url
      : `${window.location.origin}${result.video_url}`;
    window.open(videoUrl, '_blank');
  };

  const handleDownloadAll = () => {
    results.forEach((result) => {
      const videoUrl = result.video_url.startsWith('http')
        ? result.video_url
        : `${window.location.origin}${result.video_url}`;
      window.open(videoUrl, '_blank');
    });
  };

  return (
    <VideoStudioLayout
      headerProps={{
        title: 'Social Optimizer',
        subtitle: 'Optimize videos for Instagram, TikTok, YouTube, LinkedIn, Facebook, and Twitter. One video, multiple platform-ready versions.',
      }}
    >
      <Grid container spacing={4}>
        {/* Left Panel - Upload & Settings */}
        <Grid item xs={12} lg={5}>
          <Stack spacing={3}>
            <VideoUpload videoPreview={videoPreview} onVideoSelect={setVideoFile} />

            {videoFile && (
              <>
                <PlatformSelector
                  selectedPlatforms={selectedPlatforms}
                  platformSpecs={platformSpecs}
                  onTogglePlatform={togglePlatform}
                />

                <OptimizationOptions
                  autoCrop={autoCrop}
                  generateThumbnails={generateThumbnails}
                  compress={compress}
                  trimMode={trimMode}
                  onAutoCropChange={setAutoCrop}
                  onGenerateThumbnailsChange={setGenerateThumbnails}
                  onCompressChange={setCompress}
                  onTrimModeChange={setTrimMode}
                />
              </>
            )}

            <Box>
              <Button
                fullWidth
                variant="contained"
                size="large"
                startIcon={optimizing ? <CircularProgress size={20} color="inherit" /> : <PlayArrowIcon />}
                onClick={optimize}
                disabled={!canOptimize || optimizing}
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
                {optimizing ? 'Optimizing...' : 'Optimize for All Platforms'}
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

            {optimizing && (
              <Box>
                <Stack spacing={1}>
                  <Typography variant="body2" color="text.secondary">
                    Optimizing videos for {selectedPlatforms.length} platform{selectedPlatforms.length !== 1 ? 's' : ''}...
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

            {errors.length > 0 && (
              <Alert severity="error" icon={<ErrorIcon />}>
                <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                  Optimization Errors:
                </Typography>
                {errors.map((error, index) => (
                  <Typography key={index} variant="body2">
                    {error.platform}: {error.error}
                  </Typography>
                ))}
              </Alert>
            )}

            {results.length > 0 && (
              <Alert
                severity="success"
                icon={<CheckCircleIcon />}
                action={
                  <Button size="small" onClick={reset}>
                    Optimize Another
                  </Button>
                }
              >
                Successfully optimized {results.length} video{results.length !== 1 ? 's' : ''}!
              </Alert>
            )}
          </Stack>
        </Grid>

        {/* Right Panel - Preview & Results */}
        <Grid item xs={12} lg={7}>
          <Stack spacing={3}>
            {results.length > 0 ? (
              <PreviewGrid
                results={results}
                optimizing={optimizing}
                onDownload={handleDownload}
                onDownloadAll={handleDownloadAll}
              />
            ) : (
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

                {videoPreview && (
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

                {!videoPreview && (
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
                About Social Optimizer
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                Social Optimizer automatically creates platform-ready versions of your video:
              </Typography>
              <Stack component="ul" spacing={0.5} sx={{ pl: 2, m: 0 }}>
                <Typography component="li" variant="body2" color="text.secondary">
                  Aspect ratio conversion (9:16, 16:9, 1:1)
                </Typography>
                <Typography component="li" variant="body2" color="text.secondary">
                  Duration trimming to platform limits
                </Typography>
                <Typography component="li" variant="body2" color="text.secondary">
                  File size compression for platform requirements
                </Typography>
                <Typography component="li" variant="body2" color="text.secondary">
                  Thumbnail generation for each platform
                </Typography>
              </Stack>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1, fontStyle: 'italic' }}>
                All processing is free using FFmpeg.
              </Typography>
            </Box>
          </Stack>
        </Grid>
      </Grid>
    </VideoStudioLayout>
  );
};

export default SocialVideo;
export { SocialVideo };
