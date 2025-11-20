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
  Dialog,
  DialogContent,
  IconButton,
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import CloseIcon from '@mui/icons-material/Close';
import { motion, type Variants, type Easing } from 'framer-motion';
import {
  useImageStudio,
  EditOperationMeta,
  EditImageRequestPayload,
} from '../../hooks/useImageStudio';
import { EditImageUploader } from './EditImageUploader';
import { EditOperationsToolbar } from './EditOperationsToolbar';
import { EditResultViewer } from './EditResultViewer';
import { ImageStudioLayout } from './ImageStudioLayout';
import { OperationButton } from '../shared/OperationButton';
import { ImageMaskEditor } from './ImageMaskEditor';

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

export const EditStudio: React.FC = () => {
  const {
    loadEditOperations,
    editOperations,
    isLoadingEditOps,
    processEdit,
    isProcessingEdit,
    editResult,
    editError,
    clearEditResult,
  } = useImageStudio();

  const [operation, setOperation] = useState<string>('remove_background');
  const [baseImage, setBaseImage] = useState<string | null>(null);
  const [maskImage, setMaskImage] = useState<string | null>(null);
  const [backgroundImage, setBackgroundImage] = useState<string | null>(null);
  const [lightingImage, setLightingImage] = useState<string | null>(null);
  const [prompt, setPrompt] = useState('');
  const [negativePrompt, setNegativePrompt] = useState('');
  const [searchPrompt, setSearchPrompt] = useState('');
  const [selectPrompt, setSelectPrompt] = useState('');
  const [expansion, setExpansion] = useState({
    left: 0,
    right: 0,
    up: 0,
    down: 0,
  });
  const [localError, setLocalError] = useState<string | null>(null);
  const [showMaskEditor, setShowMaskEditor] = useState(false);

  useEffect(() => {
    loadEditOperations();
  }, [loadEditOperations]);

  useEffect(() => {
    const keys = Object.keys(editOperations);
    if (keys.length && !keys.includes(operation)) {
      setOperation(keys[0]);
    }
  }, [editOperations, operation]);

  const operationMeta: EditOperationMeta | undefined = editOperations[operation];
  const fields = operationMeta?.fields || {};

  const canSubmit = useMemo(() => {
    if (!baseImage) return false;
    if (fields.prompt && !prompt.trim()) return false;
    if (fields.search_prompt && !searchPrompt.trim()) return false;
    if (fields.select_prompt && !selectPrompt.trim()) return false;
    if (fields.background && !backgroundImage && fields.lighting && !lightingImage) return false;
    return true;
  }, [baseImage, fields, prompt, searchPrompt, selectPrompt, backgroundImage, lightingImage]);

  const editOperation = useMemo(() => ({
    provider: 'stability',
    operation_type: 'image_editing',
    actual_provider_name: 'stability',
  }), []);

  const handleExpansionChange = (key: keyof typeof expansion, value: number) => {
    setExpansion(prev => ({ ...prev, [key]: value }));
  };

  const buildPayload = (): EditImageRequestPayload | null => {
    if (!baseImage) {
      setLocalError('Please upload an image to edit.');
      return null;
    }
    if (fields.prompt && !prompt.trim()) {
      setLocalError('This operation requires a prompt.');
      return null;
    }
    if (fields.search_prompt && !searchPrompt.trim()) {
      setLocalError('Please provide a search prompt.');
      return null;
    }
    if (fields.select_prompt && !selectPrompt.trim()) {
      setLocalError('Please provide a selection prompt.');
      return null;
    }
    if (fields.background && !backgroundImage && fields.lighting && !lightingImage) {
      setLocalError('Provide at least a background or lighting reference.');
      return null;
    }

    const payload: EditImageRequestPayload = {
      image_base64: baseImage,
      operation,
      prompt: prompt || undefined,
      negative_prompt: negativePrompt || undefined,
      mask_base64: fields.mask ? maskImage || undefined : undefined,
      search_prompt: fields.search_prompt ? searchPrompt || undefined : undefined,
      select_prompt: fields.select_prompt ? selectPrompt || undefined : undefined,
      background_image_base64: fields.background ? backgroundImage || undefined : undefined,
      lighting_image_base64: fields.lighting ? lightingImage || undefined : undefined,
      expand_left: fields.expansion ? expansion.left : undefined,
      expand_right: fields.expansion ? expansion.right : undefined,
      expand_up: fields.expansion ? expansion.up : undefined,
      expand_down: fields.expansion ? expansion.down : undefined,
      output_format: 'png',
      options: {},
    };
    return payload;
  };

  const handleApply = async () => {
    setLocalError(null);
    try {
      const payload = buildPayload();
      if (!payload) return;
      await processEdit(payload);
    } catch {
      // errors handled in hook
    }
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
            Edit Studio
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Advanced AI editing for marketers and content teams. Remove backgrounds, inpaint, recolor,
            and relight assets in one flow.
          </Typography>
        </Stack>

        {(localError || editError) && (
          <Alert
            severity="error"
            sx={{ mb: 3 }}
            onClose={() => {
              setLocalError(null);
            }}
          >
            {localError || editError}
          </Alert>
        )}

        <Grid container spacing={3}>
          <Grid item xs={12} md={5}>
            <Stack spacing={3}>
              <EditImageUploader
                baseImage={baseImage}
                maskImage={maskImage}
                backgroundImage={backgroundImage}
                lightingImage={lightingImage}
                requiresMask={fields.mask}
                requiresBackground={fields.background}
                requiresLighting={fields.lighting}
                onBaseImageChange={setBaseImage}
                onMaskImageChange={setMaskImage}
                onBackgroundImageChange={setBackgroundImage}
                onLightingImageChange={setLightingImage}
                onOpenMaskEditor={() => setShowMaskEditor(true)}
              />
              <Divider sx={{ borderColor: 'rgba(255,255,255,0.08)' }} />
              <Stack spacing={1.5}>
                <Stack direction="row" spacing={1} alignItems="center">
                  <AutoFixHighIcon sx={{ color: '#a78bfa' }} />
                  <Typography variant="subtitle1" fontWeight={700}>
                    Operations
                  </Typography>
                </Stack>
                <EditOperationsToolbar
                  operations={editOperations}
                  selectedOperation={operation}
                  onSelect={key => {
                    setOperation(key);
                    setLocalError(null);
                    clearEditResult();
                  }}
                  loading={isLoadingEditOps}
                />
              </Stack>
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
                  {fields.prompt && (
                    <TextField
                      multiline
                      minRows={3}
                      label="Prompt"
                      value={prompt}
                      onChange={e => setPrompt(e.target.value)}
                      placeholder="Describe what you want to change..."
                      fullWidth
                    />
                  )}
                  {fields.negative_prompt && (
                    <TextField
                      label="Negative Prompt"
                      value={negativePrompt}
                      onChange={e => setNegativePrompt(e.target.value)}
                      placeholder="Elements to avoid..."
                      fullWidth
                    />
                  )}
                  {fields.search_prompt && (
                    <TextField
                      label="Search Prompt"
                      value={searchPrompt}
                      onChange={e => setSearchPrompt(e.target.value)}
                      placeholder="What should be replaced?"
                      fullWidth
                    />
                  )}
                  {fields.select_prompt && (
                    <TextField
                      label="Select Prompt"
                      value={selectPrompt}
                      onChange={e => setSelectPrompt(e.target.value)}
                      placeholder="Describe what should be recolored"
                      fullWidth
                    />
                  )}

                  {fields.expansion && (
                    <Box>
                      <Stack direction="row" spacing={1} alignItems="center" mb={1}>
                        <Typography variant="subtitle2" fontWeight={700}>
                          Canvas Expansion (px)
                        </Typography>
                        <Chip size="small" label="Outpaint" />
                      </Stack>
                      {(['left', 'right', 'up', 'down'] as const).map(dir => (
                        <Box key={dir} sx={{ mb: 1.5 }}>
                          <Typography variant="caption" color="text.secondary">
                            {dir.toUpperCase()}
                          </Typography>
                          <Slider
                            value={expansion[dir]}
                            onChange={(_, value) =>
                              handleExpansionChange(dir, value as number)
                            }
                            step={10}
                            min={0}
                            max={512}
                            valueLabelDisplay="auto"
                          />
                        </Box>
                      ))}
                    </Box>
                  )}
                </Stack>
              </Paper>

              <OperationButton
                operation={editOperation}
                label="Apply Edit"
                startIcon={<AutoFixHighIcon />}
                onClick={handleApply}
                disabled={!canSubmit}
                loading={isProcessingEdit}
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
                originalImage={baseImage}
                result={editResult}
                isProcessing={isProcessingEdit}
                onReset={() => {
                  clearEditResult();
                  setPrompt('');
                  setNegativePrompt('');
                  setSearchPrompt('');
                  setSelectPrompt('');
                  setMaskImage(null);
                  setBackgroundImage(null);
                  setLightingImage(null);
                }}
              />
            </Stack>
          </Grid>
        </Grid>

        {/* Mask Editor Dialog */}
        <Dialog
          open={showMaskEditor}
          onClose={() => setShowMaskEditor(false)}
          maxWidth="lg"
          fullWidth
          PaperProps={{
            sx: {
              background: alpha('#0f172a', 0.95),
              backdropFilter: 'blur(20px)',
            },
          }}
        >
          <DialogContent sx={{ p: 0 }}>
            <Box sx={{ position: 'relative' }}>
              <IconButton
                onClick={() => setShowMaskEditor(false)}
                sx={{
                  position: 'absolute',
                  top: 8,
                  right: 8,
                  zIndex: 1,
                  bgcolor: alpha('#000', 0.5),
                  color: '#fff',
                  '&:hover': {
                    bgcolor: alpha('#000', 0.7),
                  },
                }}
              >
                <CloseIcon />
              </IconButton>
              <ImageMaskEditor
                baseImage={baseImage}
                maskImage={maskImage}
                onMaskChange={(mask) => {
                  setMaskImage(mask);
                  setShowMaskEditor(false);
                }}
                onClose={() => setShowMaskEditor(false)}
              />
            </Box>
          </DialogContent>
        </Dialog>
      </MotionPaper>
    </ImageStudioLayout>
  );
};


