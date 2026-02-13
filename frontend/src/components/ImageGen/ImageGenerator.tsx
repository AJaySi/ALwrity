import React, { useEffect, useMemo, useState, forwardRef, useImperativeHandle } from 'react';
import { 
  Box, Button, MenuItem, Select, TextField, Typography, FormControl, InputLabel, Grid, 
  Card, CardMedia, CircularProgress, LinearProgress, Tabs, Tab, 
  Tooltip, Alert, Chip
} from '@mui/material';
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import InfoIcon from '@mui/icons-material/Info';
import { useImageGeneration, ImageGenerationRequest, fetchPromptSuggestions } from './useImageGeneration';

type Provider = 'huggingface' | 'stability' | 'wavespeed';
type ImageType = 'realistic' | 'chart' | 'conceptual' | 'diagram' | 'illustration' | 'background';

interface ImageGeneratorProps {
  defaultProvider?: Provider;
  defaultModel?: string;
  defaultPrompt?: string;
  onImageReady?: (base64: string) => void;
  // Optional context to build SME, provider-tailored prompts
  context?: {
    title?: string | null;
    outline?: any[];
    research?: any;
    persona?: { audience?: string; tone?: string; industry?: string } | any;
    section?: {
      heading?: string;
      subheadings?: string[];
      key_points?: string[];
      keywords?: string[];
      [key: string]: any;
    };
  };
}

export interface ImageGeneratorHandle {
  suggest: () => Promise<void> | void;
  generate: () => Promise<void> | void;
}

export const ImageGenerator = React.forwardRef<ImageGeneratorHandle, ImageGeneratorProps>((
  { defaultProvider, defaultModel, defaultPrompt, onImageReady, context },
  ref
) => {
  // Default to wavespeed for cost-effective blog images
  const initialProvider = defaultProvider || 'wavespeed';
  const [provider, setProvider] = useState<Provider>(initialProvider);
  
  // Initialize model based on the actual provider
  const getDefaultModelForProvider = (prov: Provider): string => {
    if (prov === 'wavespeed') return 'qwen-image';
    if (prov === 'huggingface') return 'black-forest-labs/FLUX.1-Krea-dev';
    if (prov === 'stability') return 'stable-diffusion-xl-1024-v1-0';
    return '';
  };

  const getAvailableModelsForProvider = (prov: Provider): string[] => {
    if (prov === 'wavespeed') return ['qwen-image', 'ideogram-v3-turbo', 'flux-kontext-pro'];
    if (prov === 'huggingface') return ['black-forest-labs/FLUX.1-Krea-dev', 'black-forest-labs/FLUX.1-dev', 'runwayml/flux-dev'];
    if (prov === 'stability') return ['stable-diffusion-xl-1024-v1-0', 'stable-diffusion-xl-base-1.0'];
    return [];
  };

  // Get max dimensions for a model
  const getMaxDimensionsForModel = (modelName: string): { maxWidth: number; maxHeight: number } => {
    const modelLower = modelName.toLowerCase();
    // Wavespeed models have 1024x1024 max
    if (modelLower === 'qwen-image' || modelLower === 'ideogram-v3-turbo' || modelLower === 'flux-kontext-pro') {
      return { maxWidth: 1024, maxHeight: 1024 };
    }
    // HuggingFace and Stability models typically support higher resolutions
    return { maxWidth: 2048, maxHeight: 2048 };
  };

  // Get model-specific tips and warnings
  const getModelGuidance = (modelName: string, imgType: ImageType): { tips: string[]; warnings: string[]; recommendations: string } => {
    const modelLower = modelName.toLowerCase();
    const tips: string[] = [];
    const warnings: string[] = [];
    let recommendations = '';

    if (modelLower === 'ideogram-v3-turbo') {
      tips.push('Best for images with simple text overlays (3-5 words max)');
      tips.push('Excellent photorealistic quality');
      tips.push('Superior text rendering compared to other models');
      if (imgType === 'chart' || imgType === 'diagram') {
        warnings.push('Avoid complex infographics - use simple charts with designated text overlay areas');
        recommendations = 'Create clean backgrounds with high-contrast zones for text placement, not embedded text';
      }
      if (imgType === 'conceptual' || imgType === 'background') {
        recommendations = 'Design with text overlay zones in mind (top 20% or bottom 20% of image)';
      }
    } else if (modelLower === 'qwen-image') {
      tips.push('Fast and cost-effective generation');
      tips.push('Best for abstract concepts and simple compositions');
      warnings.push('⚠️ Does NOT render readable text well - design for text overlay areas only');
      warnings.push('Avoid requesting text, words, or labels in the image itself');
      if (imgType === 'chart' || imgType === 'diagram') {
        warnings.push('Use abstract representations of data, not actual charts with text');
        recommendations = 'Create visual metaphors and patterns that represent data concepts';
      }
      recommendations = 'Design clean backgrounds with space for text overlays (never embed text)';
    } else if (modelLower === 'flux-kontext-pro') {
      tips.push('Excellent typography and text rendering capabilities');
      tips.push('Improved prompt adherence for consistent results');
      tips.push('Best for images with text elements, typography, and professional designs');
      tips.push('Cost-effective at $0.04 per image');
      if (imgType === 'chart' || imgType === 'diagram') {
        tips.push('Can render simple charts with text labels effectively');
        recommendations = 'Use for data visualizations that require clear text labels and typography';
      } else if (imgType === 'realistic' || imgType === 'illustration') {
        recommendations = 'Great for professional designs with text overlays or embedded typography';
      } else {
        recommendations = 'Ideal for blog images that need clear, readable text elements';
      }
    }

    // Image type specific warnings
    if (imgType === 'chart') {
      warnings.push('Complex infographics are too difficult for current AI models');
      recommendations = 'Use simple visual representations with designated text overlay areas';
    }

    return { tips, warnings, recommendations };
  };

  // Initialize model - ensure it's valid for the initial provider
  const initialModel = defaultModel || getDefaultModelForProvider(initialProvider);
  const [model, setModel] = useState<string>(initialModel);
  const [imageType, setImageType] = useState<ImageType>('conceptual');
  const [prompt, setPrompt] = useState<string>(defaultPrompt || '');
  const [negative, setNegative] = useState<string>('');
  const [width, setWidth] = useState<number>(1024);
  const [height, setHeight] = useState<number>(1024);
  const { isGenerating, error, result, generate } = useImageGeneration();
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const [suggestions, setSuggestions] = useState<Array<{ prompt: string; negative_prompt?: string; width?: number; height?: number; overlay_text?: string }>>([]);
  const [suggestionIndex, setSuggestionIndex] = useState<number>(0);

  const canGenerate = useMemo(() => prompt.trim().length > 0 && !isGenerating, [prompt, isGenerating]);
  const canOptimize = useMemo(() => prompt.trim().length > 0 && !loadingSuggestions, [prompt, loadingSuggestions]);

  // Sync model when provider changes - ensure model is always valid for current provider
  useEffect(() => {
    const availableModels = getAvailableModelsForProvider(provider);
    // Check if current model is valid for the new provider
    if (!availableModels.includes(model)) {
      // Model is not valid for this provider, set to default
      const defaultModelForProvider = getDefaultModelForProvider(provider);
      if (defaultModelForProvider) {
        setModel(defaultModelForProvider);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [provider]); // Only depend on provider to avoid loops

  // Clamp dimensions when model changes to ensure they don't exceed model limits
  useEffect(() => {
    const { maxWidth, maxHeight } = getMaxDimensionsForModel(model);
    if (width > maxWidth) {
      setWidth(maxWidth);
    }
    if (height > maxHeight) {
      setHeight(maxHeight);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [model]); // Only depend on model to avoid loops

  // Get current model guidance for display
  const modelGuidance = useMemo(() => getModelGuidance(model, imageType), [model, imageType]);

  // Professional styling with improved contrast and readability
  const textInputSx = {
    '& .MuiInputBase-input': { 
      color: '#1a1a1a',
      fontSize: '14px',
      lineHeight: '1.5'
    },
    '& .MuiInputLabel-root': { 
      color: '#5f6368',
      fontSize: '14px',
      fontWeight: 500
    },
    '& .MuiOutlinedInput-notchedOutline': { 
      borderColor: '#dadce0',
      borderWidth: '1.5px'
    },
    '&:hover .MuiOutlinedInput-notchedOutline': { 
      borderColor: '#80868b'
    },
    '&.Mui-focused .MuiOutlinedInput-notchedOutline': { 
      borderColor: '#1976d2',
      borderWidth: '2px'
    },
    backgroundColor: '#ffffff',
    '& .MuiFormHelperText-root': {
      fontSize: '12px',
      color: '#5f6368',
      marginTop: '4px'
    }
  } as const;

  // Default negative prompts by provider for blog writer use-case
  useEffect(() => {
    if (negative.trim().length > 0) return;
    if (provider === 'wavespeed') {
      setNegative('people posing, social media graphics, posters, text rendered as images, busy compositions, watermarks, brand logos, random people, cartoon, low quality, blurry, distorted');
    } else if (provider === 'huggingface') {
      setNegative('blurry, distorted, cartoon, low quality, bad anatomy, extra limbs, watermark, brand logos, text artifacts, oversaturated, noisy, jpeg artifacts');
    } else {
      setNegative('blurry, distorted, low quality, bad anatomy, extra limbs, watermark, brand logos, jpeg artifacts, oversharpened, text artifacts');
    }
  }, [provider, negative]);

  // Provider-specialized prompt suggestions using backend structured response; fallback locally
  const suggestPrompt = async () => {
    setLoadingSuggestions(true);
    try {
      const payload = {
        provider,
        model,
        image_type: imageType,
        title: context?.title || context?.section?.heading || defaultPrompt || '',
        section: context?.section || undefined,
        research: context?.research || undefined,
        persona: context?.persona || undefined,
      };
      const suggs = await fetchPromptSuggestions(payload);
      setSuggestions(suggs);
      if (suggs.length > 0) {
        setPrompt(suggs[0].prompt || '');
        if (suggs[0].negative_prompt) setNegative(suggs[0].negative_prompt);
        if (suggs[0].width) setWidth(suggs[0].width);
        if (suggs[0].height) setHeight(suggs[0].height);
        setSuggestionIndex(0);
      }
    } catch (e) {
      // fallback to local heuristic
      const title = (context?.section?.heading || context?.title || '').trim();
      const subheads: string[] = context?.section?.subheadings || [];
      const keyPoints: string[] = context?.section?.key_points || [];
      const keywords: string[] = Array.isArray(context?.section?.keywords)
        ? context?.section?.keywords
        : (Array.isArray(context?.research?.keywords?.primary_keywords)
            ? context?.research?.keywords?.primary_keywords
            : (context?.research?.keywords?.primary || []));
      const primary = keywords?.slice(0, 5).filter(Boolean).join(', ');
      const audience = context?.persona?.audience || 'content creators and digital marketers';
      const industry = context?.persona?.industry || context?.research?.domain || 'your industry';
      const tone = context?.persona?.tone || 'professional, trustworthy';
      const narrativeHints = [
        subheads?.length ? `Subheadings: ${subheads.slice(0,3).join(' | ')}` : null,
        keyPoints?.length ? `Key points: ${keyPoints.slice(0,3).join(' | ')}` : null,
      ].filter(Boolean).join('. ');
      setPrompt(`${title} — ${narrativeHints}. Emphasis: ${primary}. Audience: ${audience}. Industry: ${industry}. Tone: ${tone}.`);
    } finally {
      setLoadingSuggestions(false);
    }
  };

  const onGenerate = async () => {
    // Validate dimensions against model limits
    const { maxWidth, maxHeight } = getMaxDimensionsForModel(model);
    if (width > maxWidth || height > maxHeight) {
      alert(`Resolution ${width}x${height} exceeds maximum ${maxWidth}x${maxHeight} for model ${model}. Please adjust the dimensions.`);
      return;
    }
    
    const req: ImageGenerationRequest = { prompt, negative_prompt: negative, provider, model, width, height };
    const res = await generate(req);
    if (res && onImageReady) onImageReady(res.image_base64);
    // publish to image bus for downstream consumers (e.g., SEO metadata modal)
    try {
      const { publishImage } = await import('../../utils/imageBus');
      publishImage({ base64: res.image_base64, provider: res.provider, model: res.model });
    } catch {}
  };

  useImperativeHandle(ref, () => ({
    suggest: () => suggestPrompt(),
    generate: () => onGenerate()
  }));

  // Get cost info for display
  const getCostInfo = () => {
    if (provider === 'wavespeed') {
      if (model === 'qwen-image') return { cost: '$0.05', description: 'Fast generation, optimized for blog content' };
      if (model === 'ideogram-v3-turbo') return { cost: '$0.10', description: 'Superior text rendering, photorealistic' };
      if (model === 'flux-kontext-pro') return { cost: '$0.04', description: 'Professional typography, improved prompt adherence' };
      return { cost: '$0.05', description: 'Cost-effective blog images' };
    }
    if (provider === 'huggingface') {
      return { cost: '~$0.08', description: 'Photorealistic Flux models' };
    }
    if (provider === 'stability') {
      return { cost: '$0.04', description: 'SDXL-quality professional outputs' };
    }
    return { cost: 'Varies', description: 'Check provider pricing' };
  };

  const costInfo = getCostInfo();

  return (
    <Box sx={{ 
      maxWidth: '900px', 
      mx: 'auto',
      p: 3,
      backgroundColor: '#ffffff',
      borderRadius: '8px'
    }}>
      {/* Removed header - title is in modal header */}

      {/* Cost Information Alert */}
      {provider === 'wavespeed' && (
        <Alert 
          severity="info" 
          icon={<InfoIcon />}
          sx={{ 
            mb: 2,
            backgroundColor: '#e3f2fd',
            '& .MuiAlert-icon': { color: '#1976d2' },
            '& .MuiAlert-message': { color: '#1565c0' }
          }}
        >
          <Typography variant="body2" sx={{ fontWeight: 500, mb: 0.5 }}>
            💰 WaveSpeed Pricing (Cost-Effective for Blog Images)
          </Typography>
          <Grid container spacing={1} sx={{ mt: 0.5 }}>
            <Grid item xs={4}>
              <Typography variant="body2" sx={{ fontSize: '13px' }}>
                <strong>Qwen Image:</strong> $0.05/image
              </Typography>
              <Typography variant="caption" sx={{ display: 'block', color: '#5f6368' }}>
                Fast generation, optimized for blog content
              </Typography>
            </Grid>
            <Grid item xs={4}>
              <Typography variant="body2" sx={{ fontSize: '13px' }}>
                <strong>Ideogram V3 Turbo:</strong> $0.10/image
              </Typography>
              <Typography variant="caption" sx={{ display: 'block', color: '#5f6368' }}>
                Superior text rendering, photorealistic
              </Typography>
            </Grid>
            <Grid item xs={4}>
              <Typography variant="body2" sx={{ fontSize: '13px' }}>
                <strong>FLUX Kontext Pro:</strong> $0.04/image
              </Typography>
              <Typography variant="caption" sx={{ display: 'block', color: '#5f6368' }}>
                Professional typography, improved prompt adherence
              </Typography>
            </Grid>
          </Grid>
        </Alert>
      )}

      {/* Advanced Options - Always Visible */}
      <Box sx={{ 
        mb: 2, 
        p: 2, 
        border: '1.5px solid #e8eaed', 
        borderRadius: '6px', 
        backgroundColor: '#f8f9fa'
      }}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel id="provider-select-label" sx={{ fontSize: '14px' }}>Provider</InputLabel>
                <Select 
                  labelId="provider-select-label"
                  value={provider} 
                  label="Provider"
                  onChange={(e) => {
                    const newProvider = e.target.value as Provider;
                    setProvider(newProvider);
                    setModel(getDefaultModelForProvider(newProvider));
                  }} 
                  sx={{
                    ...textInputSx,
                    '& .MuiSelect-select': {
                      cursor: 'pointer'
                    }
                  }}
                  MenuProps={{ 
                    disablePortal: true,
                    PaperProps: { 
                      sx: { 
                        zIndex: 2200,
                        color: '#202124',
                        maxHeight: 300,
                        '& .MuiMenuItem-root': {
                          cursor: 'pointer',
                          '&:hover': {
                            backgroundColor: '#f5f5f5'
                          }
                        }
                      } 
                    },
                    anchorOrigin: {
                      vertical: 'bottom',
                      horizontal: 'left',
                    },
                    transformOrigin: {
                      vertical: 'top',
                      horizontal: 'left',
                    }
                  }}
                >
                  <MenuItem value="wavespeed">WaveSpeed AI</MenuItem>
                  <MenuItem value="huggingface">Hugging Face</MenuItem>
                  <MenuItem value="stability">Stability AI</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={5}>
              <FormControl fullWidth>
                <InputLabel id="model-select-label" sx={{ fontSize: '14px' }}>Model</InputLabel>
                <Select 
                  labelId="model-select-label"
                  value={model} 
                  label="Model"
                  onChange={(e) => setModel(e.target.value)}
                  sx={{
                    ...textInputSx,
                    '& .MuiSelect-select': {
                      cursor: 'pointer'
                    }
                  }}
                  MenuProps={{ 
                    disablePortal: true,
                    PaperProps: { 
                      sx: { 
                        zIndex: 2200,
                        color: '#202124',
                        maxHeight: 300,
                        '& .MuiMenuItem-root': {
                          cursor: 'pointer',
                          '&:hover': {
                            backgroundColor: '#f5f5f5'
                          }
                        }
                      } 
                    },
                    anchorOrigin: {
                      vertical: 'bottom',
                      horizontal: 'left',
                    },
                    transformOrigin: {
                      vertical: 'top',
                      horizontal: 'left',
                    }
                  }}
                >
                  {getAvailableModelsForProvider(provider).map((m) => (
                    <MenuItem key={m} value={m}>{m}</MenuItem>
                  ))}
                </Select>
                <Typography variant="caption" sx={{ mt: 0.5, display: 'block', color: '#5f6368', fontSize: '12px' }}>
                  {provider === 'wavespeed' 
                    ? 'qwen-image ($0.05), ideogram-v3-turbo ($0.10), or flux-kontext-pro ($0.04)'
                    : provider === 'huggingface'
                    ? 'Default: black-forest-labs/FLUX.1-Krea-dev'
                    : 'Default: stable-diffusion-xl-1024-v1-0'}
                </Typography>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel id="image-type-select-label" sx={{ fontSize: '14px' }}>Image Type</InputLabel>
                <Select 
                  labelId="image-type-select-label"
                  value={imageType} 
                  label="Image Type"
                  onChange={(e) => setImageType(e.target.value as ImageType)}
                  sx={{
                    ...textInputSx,
                    '& .MuiSelect-select': {
                      cursor: 'pointer'
                    }
                  }}
                  MenuProps={{ 
                    disablePortal: true,
                    PaperProps: { 
                      sx: { 
                        zIndex: 2200,
                        color: '#202124',
                        maxHeight: 300,
                        '& .MuiMenuItem-root': {
                          cursor: 'pointer',
                          '&:hover': {
                            backgroundColor: '#f5f5f5'
                          }
                        }
                      } 
                    }
                  }}
                >
                  <MenuItem value="realistic">Realistic (Photography)</MenuItem>
                  <MenuItem value="chart">Chart/Data Visualization</MenuItem>
                  <MenuItem value="conceptual">Conceptual (Abstract)</MenuItem>
                  <MenuItem value="diagram">Diagram (Technical)</MenuItem>
                  <MenuItem value="illustration">Illustration (Stylized)</MenuItem>
                  <MenuItem value="background">Background (Text Overlay)</MenuItem>
                </Select>
                <Typography variant="caption" sx={{ mt: 0.5, display: 'block', color: '#5f6368', fontSize: '12px' }}>
                  Select the type of image you want to generate
                </Typography>
              </FormControl>
            </Grid>
            <Grid item xs={6} md={1.5}>
              <Tooltip 
                title={`Image width in pixels. Max for ${model}: ${getMaxDimensionsForModel(model).maxWidth}px. Recommended: 1024 for square images, 1920 for landscape covers.`} 
                placement="top" 
                arrow
              >
                <TextField 
                  fullWidth 
                  type="number" 
                  label="Width" 
                  value={width} 
                  onChange={(e) => {
                    const newWidth = parseInt(e.target.value || '0', 10);
                    const { maxWidth } = getMaxDimensionsForModel(model);
                    setWidth(Math.min(newWidth, maxWidth));
                  }} 
                  inputProps={{ min: 64, max: getMaxDimensionsForModel(model).maxWidth }}
                  sx={textInputSx} 
                  error={width > getMaxDimensionsForModel(model).maxWidth}
                  helperText={width > getMaxDimensionsForModel(model).maxWidth ? `Max: ${getMaxDimensionsForModel(model).maxWidth}px` : ''}
                />
              </Tooltip>
            </Grid>
            <Grid item xs={6} md={1.5}>
              <Tooltip 
                title={`Image height in pixels. Max for ${model}: ${getMaxDimensionsForModel(model).maxHeight}px. Recommended: 1024 for square images, 1080 for portrait covers.`} 
                placement="top" 
                arrow
              >
                <TextField 
                  fullWidth 
                  type="number" 
                  label="Height" 
                  value={height} 
                  onChange={(e) => {
                    const newHeight = parseInt(e.target.value || '0', 10);
                    const { maxHeight } = getMaxDimensionsForModel(model);
                    setHeight(Math.min(newHeight, maxHeight));
                  }} 
                  inputProps={{ min: 64, max: getMaxDimensionsForModel(model).maxHeight }}
                  sx={textInputSx} 
                  error={height > getMaxDimensionsForModel(model).maxHeight}
                  helperText={height > getMaxDimensionsForModel(model).maxHeight ? `Max: ${getMaxDimensionsForModel(model).maxHeight}px` : ''}
                />
              </Tooltip>
            </Grid>
          </Grid>
          
          {/* Cost Chip */}
          <Box sx={{ mt: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
            <Chip 
              label={`Estimated Cost: ${costInfo.cost}/image`} 
              size="small" 
              color="primary" 
              variant="outlined"
              sx={{ fontSize: '12px', fontWeight: 500 }}
            />
            <Typography variant="caption" sx={{ color: '#5f6368' }}>
              {costInfo.description}
            </Typography>
          </Box>
        </Box>

        {/* Model-Specific Guidance */}
        {(() => {
          const guidance = modelGuidance;
          if (guidance.tips.length === 0 && guidance.warnings.length === 0 && !guidance.recommendations) return null;
          
          return (
            <Box sx={{ mb: 2 }}>
              {guidance.warnings.length > 0 && (
                <Alert 
                  severity="warning" 
                  icon={<InfoIcon />}
                  sx={{ 
                    mb: 1,
                    backgroundColor: '#fff3cd',
                    '& .MuiAlert-icon': { color: '#856404' },
                    '& .MuiAlert-message': { color: '#856404' }
                  }}
                >
                  <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                    Important Notes:
                  </Typography>
                  {guidance.warnings.map((warning, idx) => (
                    <Typography key={idx} variant="body2" sx={{ fontSize: '13px', mb: 0.5 }}>
                      • {warning}
                    </Typography>
                  ))}
                </Alert>
              )}
              
              {guidance.tips.length > 0 && (
                <Alert 
                  severity="info" 
                  icon={<InfoIcon />}
                  sx={{ 
                    mb: guidance.recommendations ? 1 : 0,
                    backgroundColor: '#e3f2fd',
                    '& .MuiAlert-icon': { color: '#1976d2' },
                    '& .MuiAlert-message': { color: '#1565c0' }
                  }}
                >
                  <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                    💡 Best Practices for {model}:
                  </Typography>
                  {guidance.tips.map((tip, idx) => (
                    <Typography key={idx} variant="body2" sx={{ fontSize: '13px', mb: 0.5 }}>
                      • {tip}
                    </Typography>
                  ))}
                </Alert>
              )}
              
              {guidance.recommendations && (
                <Alert 
                  severity="success" 
                  icon={<InfoIcon />}
                  sx={{ 
                    backgroundColor: '#d4edda',
                    '& .MuiAlert-icon': { color: '#155724' },
                    '& .MuiAlert-message': { color: '#155724' }
                  }}
                >
                  <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                    ✅ Recommendation:
                  </Typography>
                  <Typography variant="body2" sx={{ fontSize: '13px' }}>
                    {guidance.recommendations}
                  </Typography>
                </Alert>
              )}
            </Box>
          );
        })()}

      {/* Loading indicators */}
      {loadingSuggestions && (
        <Box sx={{ mb: 2 }}>
          <LinearProgress sx={{ height: 4, borderRadius: 2 }} />
          <Typography variant="caption" sx={{ mt: 0.5, display: 'block', color: '#5f6368' }}>
            Optimizing prompt...
          </Typography>
        </Box>
      )}
      {isGenerating && (
        <Box sx={{ mb: 2 }}>
          <LinearProgress sx={{ height: 4, borderRadius: 2 }} />
          <Typography variant="caption" sx={{ mt: 0.5, display: 'block', color: '#5f6368' }}>
            Generating image... This may take 10-30 seconds
          </Typography>
        </Box>
      )}

      {/* Prompt Input with Optimize Button Inside */}
      <Box sx={{ mb: 2, position: 'relative' }}>
        <Tooltip 
          title="Describe what you want in the image. Be specific: mention style (photorealistic, editorial, cinematic), subjects, composition, lighting, and mood. The AI uses this to generate your image." 
          placement="top" 
          arrow
        >
          <TextField 
            fullWidth
            multiline 
            minRows={4}
            maxRows={8}
            label="Prompt" 
            value={prompt} 
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe the image you want to generate. Be specific about style, composition, and mood..."
            sx={{
              ...textInputSx,
              '& .MuiInputBase-root': {
                paddingRight: '140px', // Make room for button
                paddingBottom: '8px'
              }
            }}
            helperText="Tip: Include camera settings (e.g., '50mm lens, f/2.8'), lighting direction, and visual emphasis for better results."
          />
        </Tooltip>
        {/* Optimize Prompt Button - Positioned inside textarea */}
        <Box sx={{
          position: 'absolute',
          bottom: '32px', // Position above helper text
          right: '14px',
          zIndex: 1
        }}>
          <Tooltip 
            title="Get AI-generated prompt suggestions optimized for blog images. Focuses on data visualization, infographics, clean layouts with text overlay areas, and conceptual illustrations." 
            placement="left" 
            arrow
          >
            <span>
                      <Button
                        variant="outlined"
                        size="small"
                        startIcon={loadingSuggestions ? <CircularProgress size={14} /> : <AutoFixHighIcon />}
                        onClick={suggestPrompt}
                        disabled={!canOptimize}
                        sx={{
                          minWidth: 'auto',
                          px: 1.5,
                          py: 0.5,
                          fontSize: '12px',
                          textTransform: 'none',
                          background: canOptimize 
                            ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                            : '#f5f5f5',
                          border: 'none',
                          color: canOptimize ? '#ffffff' : '#9aa0a6',
                          boxShadow: canOptimize 
                            ? '0 2px 8px rgba(102, 126, 234, 0.3)'
                            : 'none',
                          '&:hover': {
                            background: canOptimize
                              ? 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)'
                              : '#f5f5f5',
                            boxShadow: canOptimize
                              ? '0 4px 12px rgba(102, 126, 234, 0.4)'
                              : 'none',
                            transform: canOptimize ? 'translateY(-1px)' : 'none'
                          },
                          '&:disabled': {
                            background: '#f5f5f5',
                            color: '#9aa0a6',
                            border: 'none'
                          },
                          transition: 'all 0.3s ease'
                        }}
                      >
                        {loadingSuggestions ? 'Optimizing...' : 'Optimize Prompt'}
                      </Button>
            </span>
          </Tooltip>
        </Box>
      </Box>

      {/* Negative Prompt */}
      <Box sx={{ mb: 3 }}>
        <Tooltip 
          title="List elements you want to avoid in the image (e.g., blurry, cartoon, watermark, low quality). This helps the AI exclude unwanted features." 
          placement="top" 
          arrow
        >
          <TextField 
            fullWidth
            multiline 
            minRows={2}
            maxRows={4}
            label="Negative Prompt (optional)" 
            value={negative} 
            onChange={(e) => setNegative(e.target.value)}
            placeholder="Elements to avoid: blurry, distorted, watermark, low quality..."
            sx={textInputSx}
            helperText="Common exclusions: text artifacts, brand logos, distorted anatomy, oversaturation, noise"
          />
        </Tooltip>
      </Box>

      {/* Generate Button */}
      <Box sx={{ mb: 2, display: 'flex', justifyContent: 'flex-end' }}>
        <Tooltip 
          title="Generate the image using your current prompt and settings. The process may take 10-30 seconds depending on provider and image size." 
          placement="top" 
          arrow
        >
          <span>
            <Button 
              variant="contained" 
              disabled={!canGenerate} 
              onClick={onGenerate} 
              startIcon={isGenerating ? <CircularProgress size={18} color="inherit" /> : undefined}
              sx={{
                px: 3,
                py: 1.2,
                fontSize: '14px',
                fontWeight: 600,
                textTransform: 'none',
                background: canGenerate
                  ? 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)'
                  : 'linear-gradient(135deg, #e0e0e0 0%, #bdbdbd 100%)',
                border: 'none',
                color: canGenerate ? '#ffffff' : '#9e9e9e',
                boxShadow: canGenerate
                  ? '0 4px 15px rgba(102, 126, 234, 0.4)'
                  : 'none',
                '&:hover': {
                  background: canGenerate
                    ? 'linear-gradient(135deg, #764ba2 0%, #667eea 50%, #f093fb 100%)'
                    : 'linear-gradient(135deg, #e0e0e0 0%, #bdbdbd 100%)',
                  boxShadow: canGenerate
                    ? '0 6px 20px rgba(102, 126, 234, 0.5)'
                    : 'none',
                  transform: canGenerate ? 'translateY(-2px)' : 'none'
                },
                '&:disabled': {
                  background: 'linear-gradient(135deg, #e0e0e0 0%, #bdbdbd 100%)',
                  color: '#9e9e9e',
                  boxShadow: 'none'
                },
                transition: 'all 0.3s ease'
              }}
            >
              {isGenerating ? 'Generating…' : 'Generate Image'}
            </Button>
          </span>
        </Tooltip>
      </Box>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          <Typography variant="body2">{error}</Typography>
        </Alert>
      )}

      {/* Generated Image */}
      {result && (
        <Box sx={{ mb: 2 }}>
          <Card sx={{ 
            maxWidth: 512, 
            mx: 'auto',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            borderRadius: '8px',
            overflow: 'hidden'
          }}>
            <CardMedia 
              component="img" 
              image={`data:image/png;base64,${result.image_base64}`} 
              alt="Generated image"
              sx={{ width: '100%', height: 'auto' }}
            />
          </Card>
        </Box>
      )}

      {/* Prompt Suggestions Tabs */}
      {suggestions.length > 0 && (
        <Box sx={{ mt: 3 }}>
          <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600, color: '#202124' }}>
            Optimized Prompt Suggestions
          </Typography>
          <Tooltip 
            title="Browse through AI-generated prompt suggestions. Each tab shows a different prompt optimized for your section and provider. Click a tab to preview and auto-fill the prompt fields." 
            placement="top" 
            arrow
          >
            <Tabs 
              value={suggestionIndex} 
              onChange={(e, v) => {
                setSuggestionIndex(v);
                const s = suggestions[v];
                if (s) {
                  setPrompt(s.prompt || '');
                  setNegative(s.negative_prompt || '');
                  if (s.width) setWidth(s.width);
                  if (s.height) setHeight(s.height);
                }
              }} 
              variant="scrollable" 
              scrollButtons="auto"
              sx={{
                borderBottom: '1px solid #e8eaed',
                '& .MuiTab-root': {
                  textTransform: 'none',
                  fontSize: '13px',
                  fontWeight: 500,
                  minHeight: 40
                }
              }}
            >
              {suggestions.map((_, i) => (
                <Tab key={i} label={`Suggestion ${i + 1}`} />
              ))}
            </Tabs>
          </Tooltip>
          <Box sx={{ 
            p: 2, 
            border: '1px solid #e8eaed', 
            borderTop: 'none', 
            borderRadius: '0 0 8px 8px', 
            backgroundColor: '#f8f9fa'
          }}>
            <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', color: '#202124', mb: 1 }}>
              {suggestions[suggestionIndex]?.prompt}
            </Typography>
            {suggestions[suggestionIndex]?.negative_prompt && (
              <Box sx={{ mt: 1.5, pt: 1.5, borderTop: '1px solid #e8eaed' }}>
                <Typography variant="caption" sx={{ fontWeight: 600, color: '#5f6368', display: 'block', mb: 0.5 }}>
                  Negative Prompt:
                </Typography>
                <Typography variant="caption" sx={{ color: '#5f6368' }}>
                  {suggestions[suggestionIndex]?.negative_prompt}
                </Typography>
              </Box>
            )}
          </Box>
        </Box>
      )}
    </Box>
  );
});

export default ImageGenerator;
