import React, { useState, useMemo } from 'react';
import {
  Box,
  Grid,
  Stack,
  Typography,
  Button,
  ToggleButtonGroup,
  ToggleButton,
  TextField,
  MenuItem,
  Alert,
  Slider,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ZoomInIcon from '@mui/icons-material/ZoomIn';
import UpgradeIcon from '@mui/icons-material/Upgrade';

import { ImageStudioLayout } from './ImageStudioLayout';
import { GlassyCard, SectionHeader, AsyncStatusBanner } from './ui';
import { OperationButton } from '../shared/OperationButton';

import { useImageStudio } from '../../hooks/useImageStudio';

const modeOptions = [
  { value: 'fast', label: 'Fast (4x)', description: 'Quick upscale with minimal changes' },
  { value: 'conservative', label: 'Conservative 4K', description: 'Preserve details for print' },
  { value: 'creative', label: 'Creative 4K', description: 'Add artistic enhancements' },
  { value: 'auto', label: 'Auto', description: 'Let AI choose best mode' },
];

const presetOptions = [
  { value: 'web', label: 'Web (2048px)' },
  { value: 'print', label: 'Print (3072px)' },
  { value: 'social', label: 'Social (1080px)' },
];

export const UpscaleStudio: React.FC = () => {
  const {
    processUpscale,
    clearUpscaleResult,
    isUpscaling,
    upscaleResult,
    upscaleError,
  } = useImageStudio();

  const [mode, setMode] = useState<'fast' | 'conservative' | 'creative' | 'auto'>('auto');
  const [preset, setPreset] = useState<string>('web');
  const [prompt, setPrompt] = useState('');
  const [imageBase64, setImageBase64] = useState<string | null>(null);
  const [zoom, setZoom] = useState<number>(1);
  const [localError, setLocalError] = useState<string | null>(null);

  const handleFile = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => setImageBase64(reader.result as string);
    reader.onerror = () => setLocalError('Failed to read image');
    reader.readAsDataURL(file);
  };

  const handleUpscale = async () => {
    setLocalError(null);
    if (!imageBase64) {
      setLocalError('Upload an image to upscale.');
      return;
    }

    clearUpscaleResult();
    try {
      const payload = {
        image_base64: imageBase64,
        mode,
        preset,
        prompt: prompt || undefined,
      };
      await processUpscale(payload);
    } catch {
      // handled via hook state
    }
  };

  const canUpscale = Boolean(imageBase64) && !isUpscaling;
  const upscaleOperation = useMemo(() => ({
    provider: 'stability',
    operation_type: 'image_upscale',
    actual_provider_name: 'stability',
    model: mode,
  }), [mode]);

  return (
    <ImageStudioLayout>
      <Stack spacing={3}>
        <SectionHeader
          title="Upscale Studio"
          subtitle="Enhance resolution with fast 4x or 4K upscales powered by Stability AI."
          status="beta"
        />

        {(localError || upscaleError) && (
          <Alert severity="error" onClose={() => setLocalError(null)}>
            {localError || upscaleError}
          </Alert>
        )}

        <AsyncStatusBanner
          state={
            isUpscaling ? 'running' : upscaleResult ? 'success' : localError || upscaleError ? 'error' : 'idle'
          }
          message={
            isUpscaling
              ? 'Upscaling your image...'
              : upscaleResult
              ? 'Upscale complete!'
              : localError || upscaleError || undefined
          }
        />

        <Grid container spacing={3}>
          <Grid item xs={12} md={5}>
            <GlassyCard sx={{ p: 3 }}>
              <Stack spacing={3}>
                <Stack spacing={1}>
                  <Typography variant="subtitle2">Upload Image</Typography>
                  <Button
                    variant="outlined"
                    component="label"
                    startIcon={<CloudUploadIcon />}
                    sx={{ borderRadius: 2 }}
                  >
                    Select Image
                    <input hidden type="file" accept="image/*" onChange={handleFile} />
                  </Button>
                  {imageBase64 && (
                    <Box
                      sx={{
                        borderRadius: 2,
                        overflow: 'hidden',
                        border: '1px solid rgba(255,255,255,0.1)',
                      }}
                    >
                      <img src={imageBase64} alt="Original" style={{ width: '100%' }} />
                    </Box>
                  )}
                </Stack>

                <Stack spacing={1}>
                  <Typography variant="subtitle2">Mode</Typography>
                  <ToggleButtonGroup
                    exclusive
                    value={mode}
                    onChange={(_, value) => {
                      if (value) setMode(value);
                    }}
                    fullWidth
                    color="primary"
                  >
                    {modeOptions.map(option => (
                      <ToggleButton key={option.value} value={option.value}>
                        {option.label}
                      </ToggleButton>
                    ))}
                  </ToggleButtonGroup>
                </Stack>

                <TextField
                  select
                  label="Preset"
                  value={preset}
                  onChange={e => setPreset(e.target.value)}
                  fullWidth
                >
                  {presetOptions.map(option => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </TextField>

                {(mode === 'conservative' || mode === 'creative') && (
                  <TextField
                    label="Prompt (optional)"
                    fullWidth
                    multiline
                    minRows={2}
                    value={prompt}
                    onChange={e => setPrompt(e.target.value)}
                    placeholder="Describe how you want the upscale to enhance the image"
                  />
                )}

                <OperationButton
                  operation={upscaleOperation}
                  label="Upscale Image"
                  startIcon={<UpgradeIcon />}
                  onClick={handleUpscale}
                  disabled={!canUpscale}
                  loading={isUpscaling}
                  checkOnMount
                  sx={{
                    borderRadius: 999,
                    textTransform: 'none',
                    fontWeight: 700,
                  }}
                />
              </Stack>
            </GlassyCard>
          </Grid>

          <Grid item xs={12} md={7}>
            <GlassyCard sx={{ p: 3 }}>
              <Stack spacing={2}>
                <Stack direction="row" spacing={1} alignItems="center">
                  <ZoomInIcon sx={{ color: '#c4b5fd' }} />
                  <Typography variant="h6" fontWeight={700}>
                    Result Preview
                  </Typography>
                </Stack>

                {!upscaleResult && (
                  <Typography variant="body2" color="text.secondary">
                    Upload an image and click “Upscale Image” to see the results here.
                  </Typography>
                )}

                {upscaleResult && (
                  <Stack spacing={2}>
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={6}>
                        <Typography variant="caption" color="text.secondary">
                          Original
                        </Typography>
                        <Box
                          sx={{
                            mt: 1,
                            borderRadius: 2,
                            overflow: 'hidden',
                            border: '1px solid rgba(255,255,255,0.1)',
                            height: 320,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                          }}
                        >
                          <img
                            src={imageBase64 || ''}
                            alt="Original"
                            style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                          />
                        </Box>
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <Typography variant="caption" color="text.secondary">
                          Upscaled
                        </Typography>
                        <Box
                          sx={{
                            mt: 1,
                            borderRadius: 2,
                            overflow: 'hidden',
                            border: '1px solid rgba(255,255,255,0.1)',
                            height: 320,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            position: 'relative',
                          }}
                        >
                          <Box
                            sx={{
                              transform: `scale(${zoom})`,
                              transformOrigin: 'center',
                              transition: 'transform 0.2s ease',
                            }}
                          >
                            <img
                              src={upscaleResult.image_base64}
                              alt="Upscaled"
                              style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                            />
                          </Box>
                        </Box>
                      </Grid>
                    </Grid>

                    <Stack spacing={1}>
                      <Typography variant="caption" color="text.secondary">
                        Zoom ({Math.round(zoom * 100)}%)
                      </Typography>
                      <Slider
                        value={zoom}
                        min={1}
                        max={3}
                        step={0.1}
                        onChange={(_, value) => setZoom(value as number)}
                      />
                    </Stack>

                    <Stack direction="row" spacing={1} alignItems="center">
                      <CheckCircleIcon sx={{ color: '#10b981' }} />
                      <Typography variant="body2" color="text.secondary">
                        {upscaleResult.width}×{upscaleResult.height} · Mode: {upscaleResult.mode}
                      </Typography>
                    </Stack>
                    <Button
                      variant="outlined"
                      onClick={() => {
                        const link = document.createElement('a');
                        link.href = upscaleResult.image_base64;
                        link.download = `upscaled-${Date.now()}.png`;
                        link.click();
                      }}
                      sx={{ alignSelf: 'flex-start' }}
                    >
                      Download
                    </Button>
                  </Stack>
                )}
              </Stack>
            </GlassyCard>
          </Grid>
        </Grid>
      </Stack>
    </ImageStudioLayout>
  );
};

