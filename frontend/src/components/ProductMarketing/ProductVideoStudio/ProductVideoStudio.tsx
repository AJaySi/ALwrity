import React, { useState, useCallback } from 'react';
import {
  Grid,
  Box,
  Button,
  Typography,
  Stack,
  CircularProgress,
  LinearProgress,
  Alert,
  Paper,
  TextField,
  MenuItem,
  Card,
  CardContent,
} from '@mui/material';
import { ImageStudioLayout } from '../../ImageStudio/ImageStudioLayout';
import { useProductMarketing } from '../../../hooks/useProductMarketing';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import VideoLibraryIcon from '@mui/icons-material/VideoLibrary';

const ProductVideoStudio: React.FC = () => {
  const { generateProductVideo, isGeneratingVideo, generatedVideo, videoError } = useProductMarketing();

  const [productName, setProductName] = useState('');
  const [productDescription, setProductDescription] = useState('');
  const [videoType, setVideoType] = useState('demo');
  const [resolution, setResolution] = useState('720p');
  const [duration, setDuration] = useState(10);
  const [additionalContext, setAdditionalContext] = useState('');
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState('');

  const handleGenerate = async () => {
    if (!productName.trim() || !productDescription.trim()) {
      return;
    }

    setProgress(0);
    setStatusMessage('Starting video generation...');

    try {
      setProgress(20);
      setStatusMessage('Submitting video request...');

      const result = await generateProductVideo({
        product_name: productName,
        product_description: productDescription,
        video_type: videoType,
        resolution: resolution as '480p' | '720p' | '1080p',
        duration: duration,
        additional_context: additionalContext || undefined,
      });

      setProgress(100);
      setStatusMessage('Video generated successfully!');
    } catch (err: any) {
      console.error('Video generation error:', err);
    }
  };

  const canGenerate = productName.trim() !== '' && productDescription.trim() !== '';

  const costEstimate = useCallback(() => {
    // WAN 2.5 Text-to-Video pricing: $0.05/s (480p), $0.10/s (720p), $0.15/s (1080p)
    const costPerSecond = resolution === '480p' ? 0.05 : resolution === '720p' ? 0.10 : 0.15;
    return (costPerSecond * duration).toFixed(2);
  }, [resolution, duration]);

  return (
    <ImageStudioLayout
      headerProps={{
        title: 'Product Video Studio',
        subtitle:
          'Create product demo videos from text descriptions using WAN 2.5 Text-to-Video. Generate demo videos, storytelling content, feature highlights, and launch videos.',
      }}
    >
      <Grid container spacing={4}>
        {/* Left Panel - Settings */}
        <Grid item xs={12} lg={5}>
          <Stack spacing={3}>
            {/* Product Information */}
            <Paper sx={{ p: 3, background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.08)' }}>
              <Typography variant="h6" gutterBottom>
                Product Information
              </Typography>
              <Stack spacing={2}>
                <TextField
                  label="Product Name"
                  value={productName}
                  onChange={(e) => setProductName(e.target.value)}
                  fullWidth
                  required
                />
                <TextField
                  label="Product Description"
                  value={productDescription}
                  onChange={(e) => setProductDescription(e.target.value)}
                  fullWidth
                  multiline
                  rows={5}
                  required
                  placeholder="Describe your product, its features, and benefits. This will be used to generate the video."
                />
              </Stack>
            </Paper>

            {/* Video Settings */}
            <Paper sx={{ p: 3, background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.08)' }}>
              <Typography variant="h6" gutterBottom>
                Video Settings
              </Typography>
              <Stack spacing={2}>
                <TextField
                  select
                  label="Video Type"
                  value={videoType}
                  onChange={(e) => setVideoType(e.target.value)}
                  fullWidth
                >
                  <MenuItem value="demo">Demo - Product in use, demonstrating features</MenuItem>
                  <MenuItem value="storytelling">Storytelling - Narrative-driven product showcase</MenuItem>
                  <MenuItem value="feature_highlight">Feature Highlight - Close-up shots of key features</MenuItem>
                  <MenuItem value="launch">Launch - Product launch reveal, exciting unveiling</MenuItem>
                </TextField>

                <TextField
                  select
                  label="Resolution"
                  value={resolution}
                  onChange={(e) => setResolution(e.target.value)}
                  fullWidth
                >
                  <MenuItem value="480p">480p - $0.05/second</MenuItem>
                  <MenuItem value="720p">720p - $0.10/second</MenuItem>
                  <MenuItem value="1080p">1080p - $0.15/second</MenuItem>
                </TextField>

                <TextField
                  select
                  label="Duration"
                  value={duration}
                  onChange={(e) => setDuration(Number(e.target.value))}
                  fullWidth
                >
                  <MenuItem value={5}>5 seconds</MenuItem>
                  <MenuItem value={10}>10 seconds</MenuItem>
                </TextField>

                <TextField
                  label="Additional Context (Optional)"
                  value={additionalContext}
                  onChange={(e) => setAdditionalContext(e.target.value)}
                  fullWidth
                  multiline
                  rows={2}
                  placeholder="e.g., 'modern aesthetic', 'professional setting'"
                />
              </Stack>
            </Paper>

            {/* Cost Estimate */}
            <Card sx={{ background: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.3)' }}>
              <CardContent>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Estimated Cost
                </Typography>
                <Typography variant="h6" color="primary">
                  ${costEstimate()}
                </Typography>
              </CardContent>
            </Card>

            {/* Generate Button */}
            <Button
              fullWidth
              variant="contained"
              size="large"
              startIcon={isGeneratingVideo ? <CircularProgress size={20} color="inherit" /> : <VideoLibraryIcon />}
              onClick={handleGenerate}
              disabled={!canGenerate || isGeneratingVideo}
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
              {isGeneratingVideo ? 'Generating Video...' : 'Generate Video'}
            </Button>

            {/* Progress */}
            {isGeneratingVideo && (
              <Box>
                <LinearProgress variant="determinate" value={progress} sx={{ mb: 1 }} />
                <Typography variant="caption" color="text.secondary">
                  {statusMessage}
                </Typography>
              </Box>
            )}

            {/* Error */}
            {videoError && (
              <Alert severity="error" icon={<ErrorIcon />}>
                {videoError}
              </Alert>
            )}
          </Stack>
        </Grid>

        {/* Right Panel - Preview & Result */}
        <Grid item xs={12} lg={7}>
          <Paper sx={{ p: 3, background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.08)' }}>
            <Typography variant="h6" gutterBottom>
              Preview & Result
            </Typography>

            {generatedVideo ? (
              <Box>
                <Alert severity="success" icon={<CheckCircleIcon />} sx={{ mb: 2 }}>
                  Video generated successfully!
                </Alert>
                <Box sx={{ mb: 2 }}>
                  <video
                    src={generatedVideo.video_url?.startsWith('http') ? generatedVideo.video_url : `${window.location.origin}${generatedVideo.video_url}`}
                    controls
                    style={{ width: '100%', borderRadius: 8 }}
                  />
                </Box>
                <Stack spacing={1}>
                  <Typography variant="body2">
                    <strong>Cost:</strong> ${generatedVideo.cost?.toFixed(2) || '0.00'}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Video Type:</strong> {generatedVideo.video_type}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Resolution:</strong> {generatedVideo.resolution || resolution}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Duration:</strong> {generatedVideo.duration || duration} seconds
                  </Typography>
                </Stack>
              </Box>
            ) : (
              <Box
                sx={{
                  border: '2px dashed rgba(255,255,255,0.2)',
                  borderRadius: 2,
                  p: 6,
                  textAlign: 'center',
                }}
              >
                <PlayArrowIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                <Typography variant="body1" color="text.secondary">
                  Generated video will appear here
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </ImageStudioLayout>
  );
};

export default ProductVideoStudio;
