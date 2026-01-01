import React from 'react';
import { Grid, Box, Button, Typography, Stack, CircularProgress, LinearProgress, Alert, Paper } from '@mui/material';
import { VideoStudioLayout } from '../../VideoStudioLayout';
import { useFaceSwap } from './hooks/useFaceSwap';
import { ImageUpload, VideoUpload, SettingsPanel, ModelSelector } from './components';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';

const FaceSwap: React.FC = () => {
  const {
    imageFile,
    imagePreview,
    videoFile,
    videoPreview,
    model,
    prompt,
    resolution,
    seed,
    targetGender,
    targetIndex,
    swapping,
    progress,
    error,
    result,
    setImageFile,
    setVideoFile,
    setModel,
    setPrompt,
    setResolution,
    setSeed,
    setTargetGender,
    setTargetIndex,
    canSwap,
    costHint,
    swapFace,
    reset,
  } = useFaceSwap();

  return (
    <VideoStudioLayout
      headerProps={{
        title: 'Face Swap Studio',
        subtitle: 'Swap faces in videos using AI. Choose between MoCha (premium character replacement) or Video Face Swap (affordable multi-face support).',
      }}
    >
      <Grid container spacing={4}>
        {/* Left Panel - Upload & Settings */}
        <Grid item xs={12} lg={5}>
          <Stack spacing={3}>
            <ModelSelector selectedModel={model} onModelChange={setModel} />
            
            <ImageUpload imagePreview={imagePreview} onImageSelect={setImageFile} />
            <VideoUpload videoPreview={videoPreview} onVideoSelect={setVideoFile} />

            {imageFile && videoFile && (
              <SettingsPanel
                model={model}
                prompt={prompt}
                resolution={resolution}
                seed={seed}
                targetGender={targetGender}
                targetIndex={targetIndex}
                onPromptChange={setPrompt}
                onResolutionChange={setResolution}
                onSeedChange={setSeed}
                onTargetGenderChange={setTargetGender}
                onTargetIndexChange={setTargetIndex}
              />
            )}

            <Box>
              <Button
                fullWidth
                variant="contained"
                size="large"
                startIcon={swapping ? <CircularProgress size={20} color="inherit" /> : <PlayArrowIcon />}
                onClick={swapFace}
                disabled={!canSwap || swapping}
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
                {swapping ? 'Swapping Face...' : 'Swap Face'}
              </Button>
            </Box>

            {imageFile && videoFile && (
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
                  {model === 'mocha'
                    ? 'Minimum charge: 5 seconds | Maximum billed: 120 seconds'
                    : 'Minimum charge: 5 seconds | Maximum billed: 600 seconds (10 minutes)'}
                </Typography>
              </Box>
            )}

            {swapping && (
              <Box>
                <Stack spacing={1}>
                  <Typography variant="body2" color="text.secondary">
                    Processing face swap... This may take a few minutes...
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
                    Swap Another
                  </Button>
                }
              >
                Face swap successful! Cost: ${result.cost.toFixed(2)}
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

              {result ? (
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
                        Face-Swapped Video
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
                      Download Video
                    </Button>
                    <Button variant="outlined" fullWidth onClick={reset}>
                      Swap Another
                    </Button>
                  </Stack>
                </Box>
              ) : (
                <Stack spacing={2}>
                  {imagePreview && (
                    <Box>
                      <Typography variant="body2" sx={{ mb: 1, fontWeight: 500 }}>
                        Reference Image:
                      </Typography>
                      <Box
                        sx={{
                          borderRadius: 2,
                          overflow: 'hidden',
                          border: '2px solid #e2e8f0',
                          backgroundColor: '#f8fafc',
                        }}
                      >
                        <Box
                          component="img"
                          src={imagePreview}
                          alt="Reference"
                          sx={{
                            width: '100%',
                            maxHeight: 200,
                            objectFit: 'contain',
                            display: 'block',
                          }}
                        />
                      </Box>
                    </Box>
                  )}

                  {videoPreview && (
                    <Box>
                      <Typography variant="body2" sx={{ mb: 1, fontWeight: 500 }}>
                        Source Video:
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
                            maxHeight: 400,
                            display: 'block',
                          }}
                        />
                      </Box>
                    </Box>
                  )}

                  {!imagePreview && !videoPreview && (
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
                        Upload image and video to see preview
                      </Typography>
                    </Box>
                  )}
                </Stack>
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
                About Face Swap Studio
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                MoCha performs seamless character replacement in videos:
              </Typography>
              <Stack component="ul" spacing={0.5} sx={{ pl: 2, m: 0 }}>
                <Typography component="li" variant="body2" color="text.secondary">
                  Structure-free replacement - no pose or depth maps needed
                </Typography>
                <Typography component="li" variant="body2" color="text.secondary">
                  Preserves motion, emotion, and camera perspective
                </Typography>
                <Typography component="li" variant="body2" color="text.secondary">
                  Maintains identity consistency across frames
                </Typography>
                <Typography component="li" variant="body2" color="text.secondary">
                  Works with a single reference image and source video
                </Typography>
              </Stack>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1, fontStyle: 'italic' }}>
                <strong>Tips:</strong> Match pose & composition, keep aspect ratios consistent, limit video length to 60s for best results.
              </Typography>
            </Box>
          </Stack>
        </Grid>
      </Grid>
    </VideoStudioLayout>
  );
};

export default FaceSwap;
export { FaceSwap };
