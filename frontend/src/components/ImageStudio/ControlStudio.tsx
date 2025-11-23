import React, { useEffect, useMemo, useState } from 'react';
import {
  Box,
  Grid,
  Paper,
  Stack,
  Typography,
  TextField,
  Alert,
  Slider,
  Divider,
  Chip,
  Button,
  Card,
  CardContent,
  IconButton,
  Tooltip,
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import EditNoteIcon from '@mui/icons-material/EditNote';
import DeleteIcon from '@mui/icons-material/DeleteOutline';
import UploadIcon from '@mui/icons-material/CloudUpload';
import { motion, type Variants, type Easing } from 'framer-motion';
import {
  useImageStudio,
  ControlOperationMeta,
  ControlImageRequestPayload,
} from '../../hooks/useImageStudio';
import { ImageStudioLayout } from './ImageStudioLayout';
import { OperationButton } from '../shared/OperationButton';
import { EditResultViewer } from './EditResultViewer';

const MotionPaper = motion(Paper);
const fadeEase: Easing = [0.4, 0, 0.2, 1];

const cardVariants: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.4, ease: fadeEase },
  },
};

const readFileAsDataURL = (file: File): Promise<string> =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });

const ImageUploadSlot: React.FC<{
  label: string;
  helper?: string;
  value?: string | null;
  onChange: (value: string | null) => void;
}> = ({ label, helper, value, onChange }) => {
  const handleFile = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const dataUrl = await readFileAsDataURL(file);
    onChange(dataUrl);
  };

  return (
    <Card
      variant="outlined"
      sx={{
        borderRadius: 3,
        borderStyle: value ? 'solid' : 'dashed',
        borderColor: value ? alpha('#667eea', 0.4) : alpha('#cbd5f5', 0.8),
        background: value ? alpha('#667eea', 0.08) : alpha('#667eea', 0.02),
        position: 'relative',
      }}
    >
      <CardContent>
        <Stack spacing={1.5}>
          <Stack direction="row" alignItems="center" justifyContent="space-between">
            <Box>
              <Typography variant="subtitle2" fontWeight={700}>
                {label}
              </Typography>
              {helper && (
                <Typography variant="caption" color="text.secondary">
                  {helper}
                </Typography>
              )}
            </Box>
            {value && (
              <Tooltip title="Remove image">
                <IconButton size="small" onClick={() => onChange(null)}>
                  <DeleteIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
          </Stack>
          {value ? (
            <Box
              sx={{
                borderRadius: 2,
                overflow: 'hidden',
                border: '1px solid rgba(255,255,255,0.2)',
              }}
            >
              <img
                src={value}
                alt={`${label} preview`}
                style={{ width: '100%', display: 'block', objectFit: 'cover' }}
              />
            </Box>
          ) : (
            <Button
              component="label"
              variant="outlined"
              startIcon={<UploadIcon />}
              fullWidth
              sx={{
                borderStyle: 'dashed',
                borderColor: alpha('#667eea', 0.5),
                color: 'text.secondary',
                '&:hover': {
                  borderColor: alpha('#667eea', 0.8),
                  background: alpha('#667eea', 0.05),
                },
              }}
            >
              Upload {label}
              <input type="file" accept="image/*" hidden onChange={handleFile} />
            </Button>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
};

export const ControlStudio: React.FC = () => {
  const {
    loadControlOperations,
    controlOperations,
    isLoadingControlOps,
    processControl,
    isProcessingControl,
    controlResult,
    controlError,
    clearControlResult,
  } = useImageStudio();

  const [operation, setOperation] = useState<string>('sketch');
  const [controlImage, setControlImage] = useState<string | null>(null);
  const [styleImage, setStyleImage] = useState<string | null>(null);
  const [prompt, setPrompt] = useState('');
  const [negativePrompt, setNegativePrompt] = useState('');
  const [controlStrength, setControlStrength] = useState(0.7);
  const [fidelity, setFidelity] = useState(0.5);
  const [styleStrength, setStyleStrength] = useState(1.0);
  const [compositionFidelity, setCompositionFidelity] = useState(0.9);
  const [changeStrength, setChangeStrength] = useState(0.9);
  const [aspectRatio, setAspectRatio] = useState('1:1');
  const [localError, setLocalError] = useState<string | null>(null);

  useEffect(() => {
    loadControlOperations();
  }, [loadControlOperations]);

  useEffect(() => {
    const keys = Object.keys(controlOperations);
    if (keys.length && !keys.includes(operation)) {
      setOperation(keys[0]);
    }
  }, [controlOperations, operation]);

  // Reset state when operation changes
  useEffect(() => {
    // Reset sliders to defaults based on operation
    if (operation === 'style_transfer') {
      setStyleStrength(1.0);
      setCompositionFidelity(0.9);
      setChangeStrength(0.9);
    } else if (operation === 'style') {
      setFidelity(0.5);
    } else if (operation === 'sketch' || operation === 'structure') {
      setControlStrength(0.7);
    }
    // Clear result when switching operations
    clearControlResult();
    setLocalError(null);
  }, [operation, clearControlResult]);

  const operationMeta: ControlOperationMeta | undefined = controlOperations[operation];
  const fields = operationMeta?.fields || {};

  const canSubmit = useMemo(() => {
    if (!controlImage) return false;
    if (!prompt.trim()) return false;
    if (fields.style_image && !styleImage) return false;
    return true;
  }, [controlImage, prompt, fields.style_image, styleImage]);

  // Use same operation type as image generation for consistency
  const controlOperation = useMemo(() => ({
    provider: 'stability',
    operation_type: 'image_generation',  // Control ops use image generation limits
    actual_provider_name: 'stability',
    model: 'core',  // Default model for cost estimation
  }), []);

  const buildPayload = (): ControlImageRequestPayload | null => {
    if (!controlImage) {
      setLocalError('Please upload a control image.');
      return null;
    }
    if (!prompt.trim()) {
      setLocalError('Please provide a prompt.');
      return null;
    }
    if (fields.style_image && !styleImage) {
      setLocalError('Style image is required for style transfer.');
      return null;
    }

    const payload: ControlImageRequestPayload = {
      control_image_base64: controlImage,
      operation: operation as 'sketch' | 'structure' | 'style' | 'style_transfer',
      prompt: prompt.trim(),
      style_image_base64: fields.style_image ? styleImage || undefined : undefined,
      negative_prompt: negativePrompt || undefined,
      control_strength: fields.control_strength ? controlStrength : undefined,
      fidelity: fields.fidelity ? fidelity : undefined,
      style_strength: fields.style_strength ? styleStrength : undefined,
      composition_fidelity: operation === 'style_transfer' ? compositionFidelity : undefined,
      change_strength: operation === 'style_transfer' ? changeStrength : undefined,
      aspect_ratio: fields.aspect_ratio ? aspectRatio : undefined,
      output_format: 'png',
    };
    return payload;
  };

  const handleGenerate = async () => {
    setLocalError(null);
    try {
      const payload = buildPayload();
      if (!payload) return;
      await processControl(payload);
    } catch {
      // errors handled in hook
    }
  };

  const operationLabels: Record<string, string> = {
    sketch: 'Sketch to Image',
    structure: 'Structure Control',
    style: 'Style Control',
    style_transfer: 'Style Transfer',
  };

  return (
    <ImageStudioLayout>
      <MotionPaper
        variants={cardVariants}
        initial="hidden"
        animate="visible"
        elevation={0}
        sx={{
          maxWidth: 1400,
          mx: 'auto',
          background: 'rgba(15,23,42,0.7)',
          borderRadius: 4,
          border: '1px solid rgba(255,255,255,0.08)',
          p: { xs: 3, md: 4 },
          backdropFilter: 'blur(20px)',
        }}
      >
        <Stack spacing={0.5} mb={3}>
          <Typography
            variant="h4"
            fontWeight={800}
            sx={{
              background: 'linear-gradient(90deg, #ede9fe, #c7d2fe)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            Control Studio
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Advanced control for precise image generation. Transform sketches, maintain structure, apply styles, and transfer visual characteristics.
          </Typography>
        </Stack>

        {(localError || controlError) && (
          <Alert
            severity="error"
            sx={{ mb: 3 }}
            onClose={() => {
              setLocalError(null);
            }}
          >
            {localError || controlError}
          </Alert>
        )}

        <Grid container spacing={3}>
          <Grid item xs={12} md={5}>
            <Stack spacing={3}>
              <Stack spacing={1.5}>
                <Stack direction="row" spacing={1} alignItems="center">
                  <EditNoteIcon sx={{ color: '#a78bfa' }} />
                  <Typography variant="subtitle1" fontWeight={700}>
                    Operation
                  </Typography>
                </Stack>
                <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                  {(Object.keys(controlOperations) as Array<keyof typeof controlOperations>).map((key) => (
                    <Chip
                      key={key}
                      label={controlOperations[key]?.label || operationLabels[key] || key}
                      onClick={() => {
                        setOperation(key);
                      }}
                      sx={{
                        bgcolor: operation === key ? alpha('#667eea', 0.2) : 'transparent',
                        border: `1px solid ${operation === key ? '#667eea' : 'rgba(255,255,255,0.1)'}`,
                        color: operation === key ? '#c7d2fe' : 'text.secondary',
                        cursor: 'pointer',
                        '&:hover': {
                          bgcolor: alpha('#667eea', 0.1),
                        },
                      }}
                    />
                  ))}
                </Stack>
                {operationMeta && (
                  <Typography variant="caption" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                    {operationMeta.description}
                  </Typography>
                )}
              </Stack>

              <Divider sx={{ borderColor: 'rgba(255,255,255,0.08)' }} />

              <ImageUploadSlot
                label={operation === 'style_transfer' ? 'Initial Image' : 'Control Image'}
                helper={
                  operation === 'sketch'
                    ? 'Upload a sketch or line drawing'
                    : operation === 'structure'
                    ? 'Upload an image whose structure to maintain'
                    : operation === 'style'
                    ? 'Upload a style reference image'
                    : 'Upload the image to restyle'
                }
                value={controlImage}
                onChange={setControlImage}
              />

              {fields.style_image && (
                <ImageUploadSlot
                  label="Style Image"
                  helper="Upload a style reference image"
                  value={styleImage}
                  onChange={setStyleImage}
                />
              )}
            </Stack>
          </Grid>

          <Grid item xs={12} md={7}>
            <Stack spacing={3}>
              <Paper
                variant="outlined"
                sx={{
                  borderRadius: 3,
                  background: alpha('#0f172a', 0.7),
                  borderColor: 'rgba(255,255,255,0.05)',
                  p: 3,
                }}
              >
                <Stack spacing={2}>
                  <TextField
                    multiline
                    minRows={3}
                    label="Prompt"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="Describe what you want to generate..."
                    fullWidth
                    required
                  />
                  <TextField
                    label="Negative Prompt"
                    value={negativePrompt}
                    onChange={(e) => setNegativePrompt(e.target.value)}
                    placeholder="Elements to avoid..."
                    fullWidth
                  />

                  {fields.control_strength && (
                    <Box>
                      <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
                        Control Strength: {Math.round(controlStrength * 100)}%
                      </Typography>
                      <Slider
                        value={controlStrength}
                        min={0}
                        max={1}
                        step={0.05}
                        onChange={(_, value) => setControlStrength(value as number)}
                        valueLabelDisplay="auto"
                        valueLabelFormat={(value) => `${Math.round(value * 100)}%`}
                      />
                    </Box>
                  )}

                  {fields.fidelity && (
                    <Box>
                      <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
                        Style Fidelity: {Math.round(fidelity * 100)}%
                      </Typography>
                      <Slider
                        value={fidelity}
                        min={0}
                        max={1}
                        step={0.05}
                        onChange={(_, value) => setFidelity(value as number)}
                        valueLabelDisplay="auto"
                        valueLabelFormat={(value) => `${Math.round(value * 100)}%`}
                      />
                    </Box>
                  )}

                  {fields.style_strength && (
                    <>
                      <Box>
                        <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
                          Style Strength: {Math.round(styleStrength * 100)}%
                        </Typography>
                        <Slider
                          value={styleStrength}
                          min={0}
                          max={1}
                          step={0.05}
                          onChange={(_, value) => setStyleStrength(value as number)}
                          valueLabelDisplay="auto"
                          valueLabelFormat={(value) => `${Math.round(value * 100)}%`}
                        />
                      </Box>
                      <Box>
                        <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
                          Composition Fidelity: {Math.round(compositionFidelity * 100)}%
                        </Typography>
                        <Slider
                          value={compositionFidelity}
                          min={0}
                          max={1}
                          step={0.05}
                          onChange={(_, value) => setCompositionFidelity(value as number)}
                          valueLabelDisplay="auto"
                          valueLabelFormat={(value) => `${Math.round(value * 100)}%`}
                        />
                      </Box>
                      <Box>
                        <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
                          Change Strength: {Math.round(changeStrength * 100)}%
                        </Typography>
                        <Slider
                          value={changeStrength}
                          min={0}
                          max={1}
                          step={0.05}
                          onChange={(_, value) => setChangeStrength(value as number)}
                          valueLabelDisplay="auto"
                          valueLabelFormat={(value) => `${Math.round(value * 100)}%`}
                        />
                      </Box>
                    </>
                  )}

                  {fields.aspect_ratio && (
                    <TextField
                      select
                      label="Aspect Ratio"
                      value={aspectRatio}
                      onChange={(e) => setAspectRatio(e.target.value)}
                      fullWidth
                      SelectProps={{
                        native: true,
                      }}
                    >
                      <option value="1:1">1:1 (Square)</option>
                      <option value="16:9">16:9 (Landscape)</option>
                      <option value="9:16">9:16 (Portrait)</option>
                      <option value="4:3">4:3 (Standard)</option>
                      <option value="3:4">3:4 (Portrait)</option>
                    </TextField>
                  )}
                </Stack>
              </Paper>

              <OperationButton
                operation={controlOperation}
                label="Generate"
                startIcon={<EditNoteIcon />}
                onClick={handleGenerate}
                disabled={!canSubmit}
                loading={isProcessingControl}
                checkOnMount
                sx={{
                  borderRadius: 999,
                  alignSelf: 'flex-start',
                  px: 4,
                  py: 1.5,
                  textTransform: 'none',
                  fontWeight: 700,
                  background: 'linear-gradient(90deg, #7c3aed, #2563eb)',
                }}
              />

              <EditResultViewer
                originalImage={controlImage}
                result={controlResult ? {
                  success: controlResult.success,
                  operation: controlResult.operation,
                  provider: controlResult.provider,
                  image_base64: controlResult.image_base64,
                  width: controlResult.width,
                  height: controlResult.height,
                  metadata: controlResult.metadata,
                } : null}
                isProcessing={isProcessingControl}
                onReset={() => {
                  clearControlResult();
                  setPrompt('');
                  setNegativePrompt('');
                }}
              />
            </Stack>
          </Grid>
        </Grid>
      </MotionPaper>
    </ImageStudioLayout>
  );
};

