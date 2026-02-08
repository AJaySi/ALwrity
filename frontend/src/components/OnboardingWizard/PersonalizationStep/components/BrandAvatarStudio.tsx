import React, { useState, useRef } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Grid,
  Paper,
  Stack,
  RadioGroup,
  FormControlLabel,
  Radio,
  CircularProgress,
  Tooltip,
  IconButton,
  Alert,
  Chip,
  Divider,
  Modal,
  Fade,
  Backdrop
} from '@mui/material';
import { keyframes } from '@mui/system';
import {
  AutoAwesome,
  CloudUpload,
  Refresh,
  PhotoCamera,
  AutoFixHigh,
  InfoOutlined,
  Close,
  PlayArrow,
  HelpOutline,
  Palette,
  Psychology,
  AutoFixNormal
} from '@mui/icons-material';
import { OperationButton } from '../../../shared/OperationButton';
import {
  generateBrandAvatar,
  createAvatarVariation,
  enhanceBrandAvatar,
  optimizeAvatarPrompt,
  setBrandAvatar,
  AssetResponse
} from '../../../../api/brandAssets';

type GenerationMode = 'generate' | 'variation' | 'enhance';

const pulse = keyframes`
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
`;

export const BrandAvatarStudio: React.FC<{ domainName?: string }> = ({ domainName }) => {
  const [mode, setMode] = useState<GenerationMode>('generate');
  const [prompt, setPrompt] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [resultImage, setResultImage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [optimizing, setOptimizing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [showInfoModal, setShowInfoModal] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      setResultImage(null);
      setError(null);
      setSuccessMessage(null);
    }
  };

  const handleClearFile = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleOptimizePrompt = async () => {
    if (!prompt) return;
    setOptimizing(true);
    try {
      const response = await optimizeAvatarPrompt(prompt);
      if (response.success && response.optimized_prompt) {
        setPrompt(response.optimized_prompt);
      }
    } catch (e) {
      console.error('Failed to optimize prompt', e);
    } finally {
      setOptimizing(false);
    }
  };

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    setSuccessMessage(null);
    try {
      let response: AssetResponse;
      if (mode === 'generate') {
        response = await generateBrandAvatar(prompt);
      } else if (mode === 'variation') {
        if (!selectedFile) throw new Error('Please upload an image first');
        response = await createAvatarVariation(prompt, selectedFile);
      } else {
        if (!selectedFile) throw new Error('Please upload an image first');
        response = await enhanceBrandAvatar(selectedFile);
      }

      if (response.success && response.image_base64) {
        setResultImage(response.image_base64);
      } else {
        setError(response.error || 'Operation failed');
      }
    } catch (e: any) {
      setError(e.message || 'An error occurred during generation');
    } finally {
      setLoading(false);
    }
  };

  const handleSetAsBrandAvatar = async () => {
    if (!resultImage) return;
    setSaving(true);
    setError(null);
    setSuccessMessage(null);
    try {
      const labelDomain = domainName ? domainName.replace(/^www\./i, '') : undefined;
      const resp = await setBrandAvatar({
        image_base64: resultImage,
        domain_name: labelDomain,
        title: labelDomain ? `Brand Avatar (${labelDomain})` : 'Brand Avatar',
      });
      if (resp.success) {
        setSuccessMessage(resp.message || 'Brand avatar saved');
      } else {
        setError(resp.error || 'Failed to save brand avatar');
      }
    } catch (e: any) {
      setError(e.message || 'Failed to save brand avatar');
    } finally {
      setSaving(false);
    }
  };

  const inputSx = {
    '& .MuiInputLabel-root': { 
      color: '#374151', 
      fontSize: '12px', 
      fontWeight: 600,
      mb: 0.5,
    },
    '& .MuiOutlinedInput-root': { 
      height: '34px', 
      bgcolor: '#FFFFFF',
      borderRadius: '8px',
      fontSize: '13px',
      color: '#111827',
      '& fieldset': { borderColor: '#D1D5DB', borderWidth: '1px' },
      '&:hover fieldset': { borderColor: '#7C3AED' },
      '&.Mui-focused fieldset': { borderColor: '#7C3AED', borderWidth: '2px' },
    },
    '& .MuiInputBase-input': { 
      height: '34px', 
      color: '#111827', 
      fontWeight: 400,
      padding: '0 10px',
      '&::placeholder': { color: '#6B7280', opacity: 1 }
    },
  };

  const cardSx = {
    p: 1.5,
    borderRadius: '12px',
    bgcolor: '#FFFFFF',
    border: '1px solid #E5E7EB',
    boxShadow: '0 2px 12px rgba(0,0,0,0.06)',
    height: '100%'
  };

  const gradientAccent = 'linear-gradient(135deg, #7C3AED 0%, #EC4899 100%)';

  return (
    <Box sx={{ py: 1.5, px: 0, minHeight: '100%' }}>
      <Stack spacing={1.5}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6" sx={{ color: '#111827', fontWeight: 800, letterSpacing: '-0.02em', fontSize: '1.1rem' }}>
            Brand Avatar {domainName ? domainName : ''}
          </Typography>
          <Stack direction="row" spacing={1}>
            <Button
              startIcon={<HelpOutline sx={{ fontSize: 16 }} />}
              onClick={() => setShowInfoModal(true)}
              size="small"
              sx={{ 
                color: '#7C3AED', 
                fontWeight: 700, 
                textTransform: 'none',
                fontSize: '0.75rem',
                '&:hover': { bgcolor: 'rgba(124, 58, 237, 0.05)' }
              }}
            >
              What, How & Why
            </Button>
            <Tooltip 
              title={
                <Box sx={{ p: 1 }}>
                  <Typography variant="subtitle2" fontWeight="bold" gutterBottom>Avatar Design Guidance</Typography>
                  <Typography variant="body2" component="div" sx={{ opacity: 0.9, fontSize: '0.75rem' }}>
                    • Detailed prompts yield consistent brand aesthetics.<br/>
                    • Mention style (e.g., minimalist, 3D, sketch).<br/>
                    • Specify lighting and color palette for better alignment.<br/>
                    • High-resolution reference images improve variations.
                  </Typography>
                </Box>
              }
              arrow
              placement="left"
            >
              <Chip
                icon={<InfoOutlined sx={{ color: '#FFFFFF !important', fontSize: '14px' }} />}
                label="Quality Tips"
                size="small"
                sx={{
                  background: gradientAccent,
                  color: '#FFFFFF',
                  fontWeight: 'bold',
                  borderRadius: '6px',
                  height: '24px',
                  fontSize: '0.7rem',
                  boxShadow: '0 4px 10px rgba(124, 58, 237, 0.2)',
                  cursor: 'help'
                }}
              />
            </Tooltip>
          </Stack>
        </Box>

        <Grid container spacing={1.5}>
          <Grid item xs={12} md={7}>
            <Paper sx={cardSx} elevation={0}>
              <Stack spacing={1.5}>
                <Box>
                  <Typography variant="subtitle2" fontWeight="800" sx={{ color: 'text.primary', mb: 0.5, display: 'flex', alignItems: 'center', gap: 1, fontSize: '0.9rem' }}>
                    <PhotoCamera sx={{ color: '#7C3AED', fontSize: 18 }} />
                    Avatar Configuration
                  </Typography>
                  <Typography variant="caption" sx={{ color: 'text.secondary', mb: 1.5, display: 'block' }}>
                    Design your brand's digital face. Choose your generation mode below.
                  </Typography>

                  <RadioGroup
                    value={mode}
                    onChange={(e) => setMode(e.target.value as GenerationMode)}
                    sx={{ 
                      mb: 1.5, 
                      display: 'flex', 
                      flexDirection: 'row', 
                      gap: 1,
                      '& .MuiFormControlLabel-label': { color: 'text.primary', fontWeight: 600, fontSize: '0.75rem' }
                    }}
                  >
                    {[
                      { value: 'generate', label: 'Create Your AI Model', tip: 'Synthesize a completely new brand avatar from text' },
                      { value: 'variation', label: 'Your Look-Alike Avatar', tip: 'Create variations based on a reference photo' },
                      { value: 'enhance', label: 'AI enhance Your Photo', tip: 'Upscale and refine an existing brand image' }
                    ].map((m) => (
                      <Tooltip key={m.value} title={m.tip} arrow>
                        <FormControlLabel 
                          value={m.value} 
                          control={<Radio size="small" sx={{ p: 0.5, color: '#7C3AED', '&.Mui-checked': { color: '#EC4899' } }} />} 
                          label={m.label} 
                        />
                      </Tooltip>
                    ))}
                  </RadioGroup>
                </Box>

                {(mode === 'variation' || mode === 'enhance') && (
                  <Box>
                    <Tooltip title="Upload the base image for AI processing" arrow>
                      <Typography sx={inputSx['& .MuiInputLabel-root']}>
                        {mode === 'variation' ? 'Reference Image' : 'Source Image'}
                      </Typography>
                    </Tooltip>
                    {!previewUrl ? (
                      <Button
                        variant="outlined"
                        component="label"
                        fullWidth
                        startIcon={<CloudUpload sx={{ fontSize: 20 }} />}
                        sx={{ 
                          py: 1.5, 
                          borderStyle: 'dashed', 
                          borderRadius: '8px',
                          borderColor: '#E0E0E0',
                          color: 'text.primary',
                          fontSize: '0.8rem',
                          '&:hover': { borderColor: '#7C3AED', bgcolor: 'rgba(124, 58, 237, 0.05)' }
                        }}
                      >
                        Upload Image
                        <input type="file" hidden accept="image/*" onChange={handleFileSelect} ref={fileInputRef} />
                      </Button>
                    ) : (
                      <Box sx={{ position: 'relative', width: 'fit-content' }}>
                        <Box
                          component="img"
                          src={previewUrl}
                          sx={{ width: 80, height: 80, borderRadius: '8px', objectFit: 'cover', border: '2px solid #FFFFFF', boxShadow: '0 4px 10px rgba(0,0,0,0.1)' }}
                        />
                        <IconButton
                          size="small"
                          onClick={handleClearFile}
                          sx={{
                            position: 'absolute',
                            top: -6,
                            right: -6,
                            bgcolor: '#FFFFFF',
                            boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
                            p: 0.5,
                            '&:hover': { bgcolor: '#F5F5F5' }
                          }}
                        >
                          <Close sx={{ fontSize: 14, color: 'text.primary' }} />
                        </IconButton>
                      </Box>
                    )}
                  </Box>
                )}

                {(mode === 'generate' || mode === 'variation') && (
                  <Box>
                    <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 0.5 }}>
                      <Tooltip title="Describe the visual appearance of your brand avatar" arrow>
                        <Typography sx={inputSx['& .MuiInputLabel-root']}>
                          Creative Prompt
                        </Typography>
                      </Tooltip>
                      <Button
                        size="small"
                        startIcon={optimizing ? <CircularProgress size={10} /> : <AutoFixHigh sx={{ fontSize: 14 }} />}
                        onClick={handleOptimizePrompt}
                        disabled={!prompt || optimizing}
                        sx={{ 
                          textTransform: 'none', 
                          fontWeight: '700',
                          color: '#EC4899',
                          fontSize: '0.7rem',
                          minWidth: 'auto',
                          p: 0.5,
                          '&:hover': { bgcolor: 'transparent', opacity: 0.8 }
                        }}
                      >
                        AI Optimize
                      </Button>
                    </Stack>
                    <TextField
                      fullWidth
                      multiline
                      rows={2}
                      value={prompt}
                      onChange={(e) => setPrompt(e.target.value)}
                      placeholder={mode === 'generate' 
                        ? "e.g., A professional female entrepreneur, minimalist aesthetic..." 
                        : "e.g., Maintain the same person but change background..."}
                      sx={{...inputSx, '& .MuiOutlinedInput-root': { ...inputSx['& .MuiOutlinedInput-root'], height: 'auto', fontSize: '0.8rem' }}}
                      inputProps={{ 'aria-label': 'Avatar Description' }}
                    />
                  </Box>
                )}

                {error && <Alert severity="error" sx={{ borderRadius: '8px', py: 0, fontSize: '0.8rem' }}>{error}</Alert>}
                {successMessage && <Alert severity="success" sx={{ borderRadius: '8px', py: 0, fontSize: '0.8rem' }}>{successMessage}</Alert>}

                <OperationButton
                  operation={{
                    provider: 'stability',
                    operation_type: 'image_generation',
                    actual_provider_name: 'fal-ai',
                    model: 'fal-ai/flux-pro/v1.1-ultra',
                    tokens_requested: 1
                  }}
                  label={mode === 'generate' ? 'Generate Avatar' : mode === 'variation' ? 'Create Variation' : 'Enhance Quality'}
                  onClick={handleGenerate}
                  loading={loading}
                  disabled={loading || (mode !== 'generate' && !selectedFile)}
                  fullWidth
                  sx={{
                    background: gradientAccent,
                    color: '#FFFFFF',
                    textTransform: 'none',
                    fontWeight: '800',
                    borderRadius: '8px',
                    py: 0.75,
                    fontSize: '0.875rem',
                    '&:hover': { opacity: 0.9, transform: 'translateY(-1px)' },
                    '&:disabled': { background: '#E0E0E0', color: '#9CA3AF' }
                  }}
                />
              </Stack>
            </Paper>
          </Grid>

          <Grid item xs={12} md={5}>
            <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <Paper
                sx={{
                  flexGrow: 1,
                  borderRadius: '12px',
                  border: '2px dashed #E0E0E0',
                  bgcolor: '#FFFFFF',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  overflow: 'hidden',
                  position: 'relative',
                  minHeight: 200,
                  boxShadow: 'inset 0 2px 10px rgba(0,0,0,0.02)'
                }}
                elevation={0}
              >
                {loading ? (
                  <Stack alignItems="center" spacing={2}>
                    <CircularProgress size={32} sx={{ color: '#7C3AED' }} />
                    <Typography variant="body2" fontWeight="700" sx={{ color: 'text.secondary', animation: `${pulse} 1.5s infinite`, fontSize: '0.8125rem' }}>
                      Synthesizing assets...
                    </Typography>
                  </Stack>
                ) : resultImage ? (
                  <Box sx={{ width: '100%', height: '100%', position: 'relative' }}>
                    <Box
                      component="img"
                      src={resultImage}
                      sx={{ width: '100%', height: '100%', objectFit: 'contain', p: 1 }}
                    />
                    <Stack direction="row" spacing={1} sx={{ position: 'absolute', bottom: 12, right: 12, left: 12 }}>
                      <Button
                        fullWidth
                        size="small"
                        variant="contained"
                        onClick={handleSetAsBrandAvatar}
                        disabled={saving}
                        sx={{
                          background: gradientAccent,
                          color: '#FFFFFF',
                          textTransform: 'none',
                          fontWeight: '800',
                          borderRadius: '8px',
                          fontSize: '0.8125rem',
                          boxShadow: '0 4px 12px rgba(124, 58, 237, 0.3)'
                        }}
                      >
                        {saving ? 'Saving...' : 'Set as Avatar'}
                      </Button>
                      <IconButton
                        size="small"
                        onClick={() => setResultImage(null)}
                        sx={{
                          bgcolor: 'rgba(255,255,255,0.9)',
                          color: 'text.primary',
                          '&:hover': { bgcolor: '#FFFFFF' }
                        }}
                      >
                        <Refresh fontSize="small" />
                      </IconButton>
                    </Stack>
                  </Box>
                ) : (
                  <Stack alignItems="center" spacing={1.5} sx={{ color: '#9CA3AF' }}>
                    <AutoAwesome sx={{ fontSize: 48, opacity: 0.3, color: '#7C3AED' }} />
                    <Typography variant="body2" fontWeight="600" sx={{ fontSize: '0.8125rem' }}>Masterpiece will appear here</Typography>
                  </Stack>
                )}
              </Paper>
            </Box>
          </Grid>
        </Grid>
      </Stack>
      <Modal
        open={showInfoModal}
        onClose={() => setShowInfoModal(false)}
        closeAfterTransition
        BackdropComponent={Backdrop}
        BackdropProps={{ timeout: 500 }}
      >
        <Fade in={showInfoModal}>
          <Box sx={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            width: { xs: '90%', md: 600 },
            bgcolor: 'background.paper',
            borderRadius: '24px',
            boxShadow: 24,
            p: 4,
            outline: 'none'
          }}>
            <Stack spacing={3}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                <Box sx={{ p: 1.5, borderRadius: '12px', bgcolor: 'rgba(124, 58, 237, 0.1)', color: '#7C3AED' }}>
                  <AutoAwesome fontSize="large" />
                </Box>
                <Box>
                  <Typography variant="h5" fontWeight="800" sx={{ color: '#111827' }}>
                    Brand Avatar: What, How & Why
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Your digital face in the AI world
                  </Typography>
                </Box>
              </Box>

              <Divider />

              <Stack spacing={2}>
                <Box>
                  <Typography variant="subtitle1" fontWeight="800" sx={{ color: '#111827', display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Psychology sx={{ color: '#7C3AED' }} /> What is it?
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5, lineHeight: 1.6 }}>
                    A Brand Avatar is an AI-generated visual representation of your business or persona. It's more than just a logo; it's a consistent, high-fidelity image that gives your brand a recognizable "face."
                  </Typography>
                </Box>

                <Box>
                  <Typography variant="subtitle1" fontWeight="800" sx={{ color: '#111827', display: 'flex', alignItems: 'center', gap: 1 }}>
                    <AutoFixNormal sx={{ color: '#EC4899' }} /> How does it work?
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5, lineHeight: 1.6 }}>
                    You provide a detailed description (or a reference image), and our neural networks synthesize a unique, professional avatar. You can further refine it through variations or upscale it for professional use.
                  </Typography>
                </Box>

                <Box>
                  <Typography variant="subtitle1" fontWeight="800" sx={{ color: '#111827', display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Palette sx={{ color: '#F59E0B' }} /> Why use it?
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5, lineHeight: 1.6 }}>
                    • <b>Brand Recognition:</b> Use your avatar across all marketing materials for a cohesive look.<br/>
                    • <b>Social Media:</b> Perfect for profile pictures, thumbnails, and interactive avatars.<br/>
                    • <b>Video Integration:</b> ALwrity tools use this avatar to represent your brand in automated video narrations.
                  </Typography>
                </Box>
              </Stack>

              <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
                <Button 
                  variant="contained" 
                  onClick={() => setShowInfoModal(false)}
                  sx={{ 
                    borderRadius: '10px', 
                    textTransform: 'none', 
                    fontWeight: 'bold',
                    background: gradientAccent
                  }}
                >
                  Got it, let's design!
                </Button>
              </Box>
            </Stack>
          </Box>
        </Fade>
      </Modal>
    </Box>
  );
};
