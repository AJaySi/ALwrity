import React, { useEffect, useMemo, useState, forwardRef, useImperativeHandle } from 'react';
import { Box, Button, MenuItem, Select, TextField, Typography, FormControl, InputLabel, Grid, Card, CardMedia, CircularProgress, LinearProgress, Collapse, IconButton, Tabs, Tab, Tooltip } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import { useImageGeneration, ImageGenerationRequest, fetchPromptSuggestions } from './useImageGeneration';

type Provider = 'gemini' | 'huggingface' | 'stability';

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
  openAdvanced: () => void;
  closeAdvanced: () => void;
}

export const ImageGenerator = React.forwardRef<ImageGeneratorHandle, ImageGeneratorProps>((
  { defaultProvider, defaultModel, defaultPrompt, onImageReady, context },
  ref
) => {
  const [provider, setProvider] = useState<Provider>(defaultProvider || (process.env.NEXT_PUBLIC_GPT_PROVIDER as Provider) || 'huggingface');
  const [model, setModel] = useState<string>(defaultModel || 'black-forest-labs/FLUX.1-Krea-dev');
  const [prompt, setPrompt] = useState<string>(defaultPrompt || '');
  const [negative, setNegative] = useState<string>('');
  const [width, setWidth] = useState<number>(1024);
  const [height, setHeight] = useState<number>(1024);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const { isGenerating, error, result, generate } = useImageGeneration();
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const [suggestions, setSuggestions] = useState<Array<{ prompt: string; negative_prompt?: string; width?: number; height?: number; overlay_text?: string }>>([]);
  const [suggestionIndex, setSuggestionIndex] = useState<number>(0);

  const canGenerate = useMemo(() => prompt.trim().length > 0 && !isGenerating, [prompt, isGenerating]);

  // High-contrast input styling for readability on light backgrounds
  const textInputSx = {
    '& .MuiInputBase-input': { color: '#202124' },
    '& .MuiInputLabel-root': { color: '#5f6368' },
    '& .MuiOutlinedInput-notchedOutline': { borderColor: '#cbd5e1' },
    '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#94a3b8' },
    '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#1976d2' },
    backgroundColor: '#ffffff'
  } as const;

  // Default negative prompts by provider for blog writer use-case
  useEffect(() => {
    if (negative.trim().length > 0) return;
    if (provider === 'huggingface') {
      setNegative('blurry, distorted, cartoon, low quality, bad anatomy, extra limbs, watermark, brand logos, text artifacts, oversaturated, noisy, jpeg artifacts');
    } else if (provider === 'gemini') {
      setNegative('cartoon, clip-art, abstract, noisy, low resolution, artifacts, watermark, brand logos, text artifacts');
    } else {
      setNegative('blurry, distorted, low quality, bad anatomy, extra limbs, watermark, brand logos, jpeg artifacts, oversharpened, text artifacts');
    }
  // run once on mount (and when provider changes if negative is empty)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [provider]);

  // Auto-suggest on open for better defaults (only if no initial prompt)
  useEffect(() => {
    if (!prompt || prompt.trim().length === 0) {
      // fire and forget; UI shows spinner on the button if user clicks again
      suggestPrompt().catch(() => {});
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Provider-specialized prompt suggestions using backend structured response; fallback locally
  const suggestPrompt = async () => {
    setLoadingSuggestions(true);
    try {
      const payload = {
        provider,
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
    generate: () => onGenerate(),
    openAdvanced: () => setShowAdvanced(v => !v),
    closeAdvanced: () => setShowAdvanced(false)
  }));

  return (
    <Box>
      <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, color: '#202124' }}>Generate Blog Section Image</Typography>
      
      {/* Advanced Options in Header Area */}
      <Collapse in={showAdvanced}>
        <Box sx={{ mb: 2, border: '1px solid #e0e0e0', borderRadius: 1, p: 1.5, backgroundColor: '#fafafa', color: '#202124' }}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={3}>
              <Tooltip title="Select the AI image generation provider. Hugging Face offers photorealistic Flux models, Gemini provides brand-safe editorial images, and Stability AI delivers SDXL-quality professional outputs." placement="top" arrow>
                <FormControl fullWidth>
                  <InputLabel>Provider</InputLabel>
                  <Select value={provider} label="Provider" onChange={(e) => setProvider(e.target.value as Provider)} sx={textInputSx} MenuProps={{ PaperProps: { sx: { color: '#202124' } } }}>
                    <MenuItem value="huggingface">Hugging Face</MenuItem>
                    <MenuItem value="gemini">Gemini</MenuItem>
                    <MenuItem value="stability">Stability</MenuItem>
                  </Select>
                </FormControl>
              </Tooltip>
            </Grid>
            <Grid item xs={12} md={5}>
              <Tooltip title="Specify the exact model to use. Leave empty to use the provider's default. For Hugging Face, the default is FLUX.1-Krea-dev, optimized for photorealistic blog images." placement="top" arrow>
                <TextField fullWidth label="Model" value={model} onChange={(e) => setModel(e.target.value)} helperText={provider === 'huggingface' ? 'Default: black-forest-labs/FLUX.1-Krea-dev' : 'Leave empty to use provider default'} sx={textInputSx} />
              </Tooltip>
            </Grid>
            <Grid item xs={6} md={2}>
              <Tooltip title="Image width in pixels. Recommended: 1024 for square images, 1920 for landscape covers. Higher values increase quality but take longer to generate." placement="top" arrow>
                <TextField fullWidth type="number" label="Width" value={width} onChange={(e) => setWidth(parseInt(e.target.value || '0', 10))} sx={textInputSx} />
              </Tooltip>
            </Grid>
            <Grid item xs={6} md={2}>
              <Tooltip title="Image height in pixels. Recommended: 1024 for square images, 1080 for portrait covers. Aspect ratio affects composition and visual appeal." placement="top" arrow>
                <TextField fullWidth type="number" label="Height" value={height} onChange={(e) => setHeight(parseInt(e.target.value || '0', 10))} sx={textInputSx} />
              </Tooltip>
            </Grid>
          </Grid>
        </Box>
      </Collapse>

      {/* Loading indicators */}
      {loadingSuggestions && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="caption" sx={{ mb: 0.5, display: 'block' }}>Loading suggestions...</Typography>
          <LinearProgress />
        </Box>
      )}
      {isGenerating && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="caption" sx={{ mb: 0.5, display: 'block' }}>Generating image...</Typography>
          <LinearProgress />
        </Box>
      )}

      {/* Prompt and Negative Prompt Side by Side - 80/20 split, stack on mobile */}
      <Box sx={{ mb: 2, display: { xs: 'block', md: 'flex' }, gap: 2 }}>
        <Tooltip title="Describe what you want in the image. Be specific: mention style (photorealistic, editorial, cinematic), subjects, composition, lighting, and mood. The AI uses this to generate your image. Tips: Include camera settings (e.g., '50mm lens, f/2.8'), lighting direction, and visual emphasis." placement="top" arrow>
          <TextField 
            sx={{ flex: { md: '0 0 80%' }, width: { xs: '100%' }, mb: { xs: 2, md: 0 } }}
            InputProps={{ sx: { color: '#202124' } }}
            InputLabelProps={{ sx: { color: '#5f6368' } }}
            FormHelperTextProps={{ sx: { color: '#5f6368' } }}
            multiline 
            minRows={3} 
            label="Prompt" 
            value={prompt} 
            onChange={(e) => setPrompt(e.target.value)} 
            placeholder="Describe the image..." 
          />
        </Tooltip>
        <Tooltip title="List elements you want to avoid in the image (e.g., blurry, cartoon, watermark, low quality). This helps the AI exclude unwanted features. Common items: text artifacts, brand logos, distorted anatomy, oversaturation, noise." placement="top" arrow>
          <TextField 
            sx={{ flex: { md: '0 0 20%' }, width: { xs: '100%' } }}
            InputProps={{ sx: { color: '#202124' } }}
            InputLabelProps={{ sx: { color: '#5f6368' } }}
            multiline 
            minRows={3} 
            label="Negative Prompt (optional)" 
            value={negative} 
            onChange={(e) => setNegative(e.target.value)} 
          />
        </Tooltip>
      </Box>

      {/* Action Buttons */}
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Tooltip title="Get AI-generated prompt suggestions tailored to your blog section. Uses your section title, subheadings, key points, keywords, and research data to create hyper-personalized prompts optimized for your chosen provider. Click to see multiple suggestions in tabs." placement="top" arrow>
            <span>
              <Button sx={{ mr: 1 }} variant="outlined" onClick={suggestPrompt} disabled={loadingSuggestions}>{loadingSuggestions ? 'Suggesting…' : 'Suggest prompt'}</Button>
            </span>
          </Tooltip>
          <Tooltip title="Generate the image using your current prompt and settings. The process may take 10-30 seconds depending on provider and image size. Once generated, the image will appear below and can be used for your blog section." placement="top" arrow>
            <span>
              <Button variant="contained" disabled={!canGenerate} onClick={onGenerate} startIcon={isGenerating ? <CircularProgress size={18} /> : undefined}>
                {isGenerating ? 'Generating…' : 'Generate Image'}
              </Button>
            </span>
          </Tooltip>
        </Grid>
        {error && (
          <Grid item xs={12}>
            <Typography color="error" variant="body2">{error}</Typography>
          </Grid>
        )}
        {result && (
          <Grid item xs={12}>
            <Card sx={{ maxWidth: 512 }}>
              <CardMedia component="img" image={`data:image/png;base64,${result.image_base64}`} alt="generated" />
            </Card>
          </Grid>
        )}
        {suggestions.length > 0 && (
          <Grid item xs={12}>
            <Tooltip title="Browse through AI-generated prompt suggestions. Each tab shows a different prompt optimized for your section and provider. Click a tab to preview and auto-fill the prompt fields. You can then modify or use it directly." placement="top" arrow>
              <div>
                <Tabs value={suggestionIndex} onChange={(e, v) => {
                  setSuggestionIndex(v);
                  const s = suggestions[v];
                  if (s) {
                    setPrompt(s.prompt || '');
                    setNegative(s.negative_prompt || '');
                    if (s.width) setWidth(s.width);
                    if (s.height) setHeight(s.height);
                  }
                }} variant="scrollable" scrollButtons allowScrollButtonsMobile>
                  {suggestions.map((_, i) => (
                    <Tab key={i} label={`Prompt ${i + 1}`} />
                  ))}
                </Tabs>
              </div>
            </Tooltip>
            <Tooltip title="Preview of the currently selected prompt suggestion. Shows the main prompt and negative prompt (if any). This preview updates when you click different tabs above." placement="top" arrow>
              <Box sx={{ p: 2, border: '1px solid #e0e0e0', borderTop: 'none', borderRadius: '0 0 8px 8px', background: '#fff' }}>
                <Typography variant="subtitle2" sx={{ mb: 1 }}>Preview</Typography>
                <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', color: '#202124' }}>{suggestions[suggestionIndex]?.prompt}</Typography>
                {suggestions[suggestionIndex]?.negative_prompt && (
                  <Typography variant="caption" sx={{ color: 'text.secondary', display: 'block', mt: 1 }}>Negative: {suggestions[suggestionIndex]?.negative_prompt}</Typography>
                )}
              </Box>
            </Tooltip>
          </Grid>
        )}
      </Grid>
    </Box>
  );
});

export default ImageGenerator;
