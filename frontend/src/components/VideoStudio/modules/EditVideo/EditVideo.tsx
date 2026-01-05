import React from 'react';
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
} from '@mui/material';
import { VideoStudioLayout } from '../../VideoStudioLayout';
import { useEditVideo } from './hooks/useEditVideo';
import {
  VideoUpload,
  OperationSelector,
  TrimSettings,
  SpeedSettings,
  StabilizeSettings,
  TextOverlaySettings,
  VolumeSettings,
  NormalizeSettings,
  DenoiseSettings,
} from './components';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import EditIcon from '@mui/icons-material/Edit';

export const EditVideo: React.FC = () => {
  const {
    videoFile,
    videoPreview,
    videoDuration,
    setVideoFile,
    operation,
    setOperation,
    startTime,
    endTime,
    maxDuration,
    trimMode,
    setStartTime,
    setEndTime,
    setMaxDuration,
    setTrimMode,
    speedFactor,
    setSpeedFactor,
    smoothing,
    setSmoothing,
    overlayText,
    textPosition,
    fontSize,
    fontColor,
    backgroundColor,
    textStartTime,
    textEndTime,
    setOverlayText,
    setTextPosition,
    setFontSize,
    setFontColor,
    setBackgroundColor,
    setTextStartTime,
    setTextEndTime,
    volumeFactor,
    setVolumeFactor,
    targetLevel,
    setTargetLevel,
    denoiseStrength,
    setDenoiseStrength,
    editing,
    progress,
    error,
    result,
    canEdit,
    costHint,
    operationDescription,
    processVideo,
    reset,
  } = useEditVideo();

  return (
    <VideoStudioLayout
      headerProps={{
        title: 'Edit Studio',
        subtitle:
          'Trim, adjust speed, stabilize, add text, and enhance audio. All operations are free using FFmpeg.',
      }}
    >
      <Grid container spacing={3}>
        {/* Left Panel - Upload & Settings */}
        <Grid item xs={12} lg={5}>
          <Stack spacing={2}>
            <VideoUpload
              videoPreview={videoPreview}
              videoDuration={videoDuration}
              onVideoSelect={setVideoFile}
            />

            {videoFile && (
              <>
                <OperationSelector
                  selectedOperation={operation}
                  onOperationChange={setOperation}
                />

                {operation === 'trim' && (
                  <TrimSettings
                    videoDuration={videoDuration}
                    startTime={startTime}
                    endTime={endTime}
                    maxDuration={maxDuration}
                    trimMode={trimMode}
                    onStartTimeChange={setStartTime}
                    onEndTimeChange={setEndTime}
                    onMaxDurationChange={setMaxDuration}
                    onTrimModeChange={setTrimMode}
                  />
                )}

                {operation === 'speed' && (
                  <SpeedSettings
                    videoDuration={videoDuration}
                    speedFactor={speedFactor}
                    onSpeedFactorChange={setSpeedFactor}
                  />
                )}

                {operation === 'stabilize' && (
                  <StabilizeSettings
                    smoothing={smoothing}
                    onSmoothingChange={setSmoothing}
                  />
                )}

                {operation === 'text' && (
                  <TextOverlaySettings
                    text={overlayText}
                    position={textPosition}
                    fontSize={fontSize}
                    fontColor={fontColor}
                    backgroundColor={backgroundColor}
                    startTime={textStartTime}
                    endTime={textEndTime}
                    videoDuration={videoDuration}
                    onTextChange={setOverlayText}
                    onPositionChange={setTextPosition}
                    onFontSizeChange={setFontSize}
                    onFontColorChange={setFontColor}
                    onBackgroundColorChange={setBackgroundColor}
                    onStartTimeChange={setTextStartTime}
                    onEndTimeChange={setTextEndTime}
                  />
                )}

                {operation === 'volume' && (
                  <VolumeSettings
                    volumeFactor={volumeFactor}
                    onVolumeFactorChange={setVolumeFactor}
                  />
                )}

                {operation === 'normalize' && (
                  <NormalizeSettings
                    targetLevel={targetLevel}
                    onTargetLevelChange={setTargetLevel}
                  />
                )}

                {operation === 'denoise' && (
                  <DenoiseSettings
                    strength={denoiseStrength}
                    onStrengthChange={setDenoiseStrength}
                  />
                )}
              </>
            )}

            <Box>
              <Button
                fullWidth
                variant="contained"
                size="large"
                startIcon={
                  editing ? (
                    <CircularProgress size={20} color="inherit" />
                  ) : (
                    <EditIcon />
                  )
                }
                onClick={processVideo}
                disabled={!canEdit || editing}
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
                {editing ? 'Processing...' : 'Process Video'}
              </Button>
            </Box>

            {videoFile && (
              <Box
                sx={{
                  p: 2,
                  borderRadius: 1,
                  backgroundColor: '#f8fafc',
                  border: '1px solid #e2e8f0',
                }}
              >
                <Stack direction="row" justifyContent="space-between" alignItems="center">
                  <Typography variant="body2" color="text.secondary">
                    Cost:
                  </Typography>
                  <Typography variant="body2" fontWeight={600} color="#10b981">
                    {costHint}
                  </Typography>
                </Stack>
                {operationDescription && (
                  <Typography
                    variant="caption"
                    color="text.secondary"
                    sx={{ mt: 1, display: 'block' }}
                  >
                    {operationDescription}
                  </Typography>
                )}
              </Box>
            )}
          </Stack>
        </Grid>

        {/* Right Panel - Preview & Result */}
        <Grid item xs={12} lg={7}>
          <Stack spacing={3}>
            {/* Progress */}
            {editing && (
              <Paper
                elevation={0}
                sx={{
                  p: 3,
                  borderRadius: 2,
                  border: '1px solid #e2e8f0',
                  backgroundColor: '#f8fafc',
                }}
              >
                <Stack spacing={2}>
                  <Stack direction="row" alignItems="center" spacing={1}>
                    <CircularProgress size={20} />
                    <Typography variant="body2" color="text.secondary">
                      Processing video...
                    </Typography>
                  </Stack>
                  <LinearProgress
                    variant="determinate"
                    value={progress}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      backgroundColor: '#e2e8f0',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: '#3b82f6',
                      },
                    }}
                  />
                  <Typography variant="caption" color="text.secondary" textAlign="center">
                    {progress.toFixed(0)}% complete
                  </Typography>
                </Stack>
              </Paper>
            )}

            {/* Error */}
            {error && (
              <Alert
                severity="error"
                icon={<ErrorIcon />}
                onClose={() => reset()}
                sx={{ borderRadius: 2 }}
              >
                {error}
              </Alert>
            )}

            {/* Result */}
            {result && (
              <Paper
                elevation={0}
                sx={{
                  p: 3,
                  borderRadius: 2,
                  border: '2px solid #10b981',
                  backgroundColor: '#f0fdf4',
                }}
              >
                <Stack spacing={2}>
                  <Stack direction="row" alignItems="center" spacing={1}>
                    <CheckCircleIcon sx={{ color: '#10b981' }} />
                    <Typography variant="h6" color="#0f172a" fontWeight={600}>
                      Video Processed Successfully!
                    </Typography>
                  </Stack>

                  <video
                    src={result.video_url}
                    controls
                    style={{
                      width: '100%',
                      maxHeight: '400px',
                      borderRadius: '8px',
                      objectFit: 'contain',
                      backgroundColor: '#000',
                    }}
                  />

                  <Stack direction="row" justifyContent="space-between" alignItems="center">
                    <Typography variant="body2" color="text.secondary">
                      Operation: <strong>{result.edit_type}</strong>
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Cost: <strong>${result.cost.toFixed(4)}</strong>
                    </Typography>
                  </Stack>

                  <Stack direction="row" spacing={2}>
                    <Button
                      variant="contained"
                      href={result.video_url}
                      download
                      sx={{
                        backgroundColor: '#10b981',
                        '&:hover': { backgroundColor: '#059669' },
                      }}
                    >
                      Download Video
                    </Button>
                    <Button variant="outlined" onClick={reset}>
                      Edit Another Video
                    </Button>
                  </Stack>
                </Stack>
              </Paper>
            )}

            {/* Info Box */}
            {!editing && !result && (
              <Paper
                elevation={0}
                sx={{
                  p: 3,
                  borderRadius: 2,
                  border: '1px solid #e2e8f0',
                  backgroundColor: '#f8fafc',
                }}
              >
                <Typography
                  variant="subtitle2"
                  sx={{ mb: 2, fontWeight: 600, color: '#0f172a' }}
                >
                  About Edit Studio
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Edit Studio provides free video editing operations using FFmpeg:
                </Typography>
                
                <Typography variant="caption" color="text.secondary" fontWeight={600} sx={{ mb: 1, display: 'block' }}>
                  Video Processing
                </Typography>
                <Stack spacing={1} sx={{ mb: 2 }}>
                  <Box>
                    <Typography variant="body2" fontWeight={600} color="#0f172a">
                      Trim & Cut
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Cut video to specific time range or limit to a maximum duration.
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" fontWeight={600} color="#0f172a">
                      Speed Control
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Slow motion (0.25x-0.5x) or fast forward (1.5x-4x).
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" fontWeight={600} color="#0f172a">
                      Stabilization
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Reduce camera shake using FFmpeg's vidstab filter.
                    </Typography>
                  </Box>
                </Stack>
                
                <Typography variant="caption" color="text.secondary" fontWeight={600} sx={{ mb: 1, display: 'block' }}>
                  Text & Audio
                </Typography>
                <Stack spacing={1}>
                  <Box>
                    <Typography variant="body2" fontWeight={600} color="#0f172a">
                      Text Overlay
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Add captions, titles, or watermarks with customizable style.
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" fontWeight={600} color="#0f172a">
                      Volume Control
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Mute, reduce, or boost audio volume.
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" fontWeight={600} color="#0f172a">
                      Audio Normalization
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      EBU R128 loudness normalization for streaming platforms.
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" fontWeight={600} color="#0f172a">
                      Noise Reduction
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Remove background noise like AC, hum, or hiss.
                    </Typography>
                  </Box>
                </Stack>
              </Paper>
            )}
          </Stack>
        </Grid>
      </Grid>
    </VideoStudioLayout>
  );
};

export default EditVideo;
