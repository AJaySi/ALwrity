import React, { useState, useEffect, useRef } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Typography,
  Alert,
  Box,
  CircularProgress,
  RadioGroup,
  Radio,
  Card,
  CardContent,
  Tooltip,
  IconButton,
  InputAdornment,
  Switch,
  FormControlLabel,
} from '@mui/material';
import { InfoOutlined } from '@mui/icons-material';
import {
  storyWriterApi,
  StorySetupOption,
  StoryIdeaEnhanceSuggestion,
} from '../../../../services/storyWriterApi';
import { triggerSubscriptionError } from '../../../../api/client';
import { useStoryWriterState } from '../../../../hooks/useStoryWriterState';
import { STORY_IDEA_PLACEHOLDERS, STORY_IDEA_PLACEHOLDERS_BY_COMBINATION } from './constants';
import { textFieldStyles, cardStyles } from './styles';
import {
  WRITING_STYLES,
  STORY_TONES,
  NARRATIVE_POVS,
  AUDIENCE_AGE_GROUPS,
  CONTENT_RATINGS,
  ENDING_PREFERENCES,
} from './constants';
import { CustomValuesSetters } from './types';

interface AIStorySetupModalProps {
  open: boolean;
  onClose: () => void;
  state: ReturnType<typeof useStoryWriterState>;
  customValuesSetters: CustomValuesSetters;
  originMode?: 'marketing' | 'pure' | null;
  originTemplate?: string | null;
  onApplied?: () => void;
}

const FICTION_VARIANT_OPTIONS: Record<
  string,
  {
    value: string;
    label: string;
  }[]
> = {
  short_fiction: [
    { value: 'High-concept twist short story', label: 'High-concept twist' },
    { value: 'Character-driven emotional short story', label: 'Character-driven emotional' },
    { value: 'Atmospheric literary vignette', label: 'Atmospheric vignette' },
  ],
  long_fiction: [
    { value: 'Epic multi-arc saga', label: 'Epic saga' },
    { value: 'Slow-burn character drama', label: 'Slow-burn character drama' },
    { value: 'Idea-driven speculative fiction', label: 'Idea-driven speculative' },
  ],
  anime_fiction: [
    { value: 'Shonen-style high-energy anime action', label: 'Shonen action' },
    { value: 'Slice-of-life anime character drama', label: 'Slice of life' },
    { value: 'Dark fantasy anime story', label: 'Dark fantasy' },
    { value: 'Sci-fi mecha anime story', label: 'Sci-fi mecha' },
  ],
  experimental_fiction: [
    { value: 'Nonlinear experimental narrative', label: 'Nonlinear' },
    { value: 'Second-person immersive experimental story', label: 'Second-person' },
    { value: 'Multi-POV fragmented narrative', label: 'Multi-POV fragmented' },
  ],
};

export const AIStorySetupModal: React.FC<AIStorySetupModalProps> = ({
  open,
  onClose,
  state,
  customValuesSetters,
  originMode,
  originTemplate,
  onApplied,
}) => {
  const [storyIdea, setStoryIdea] = useState('');
  const [isGeneratingSetup, setIsGeneratingSetup] = useState(false);
  const [setupError, setSetupError] = useState<string | null>(null);
  const [placeholderIndex, setPlaceholderIndex] = useState(0);
  const [currentPlaceholder, setCurrentPlaceholder] = useState('');
  const [brandContext, setBrandContext] = useState<{
    brand_name?: string | null;
    writing_tone?: string | null;
    audience_description?: string | null;
  } | null>(null);
  const [brandAvatarUrl, setBrandAvatarUrl] = useState<string | null>(null);
  const [brandVoicePreviewUrl, setBrandVoicePreviewUrl] = useState<string | null>(null);
  const [isLoadingContext, setIsLoadingContext] = useState(false);
  const [personaEnabled, setPersonaEnabled] = useState(false);
  const [usePersonaContext, setUsePersonaContext] = useState(false);
  const typingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const charIndexRef = useRef(0);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const storyIdeaInputRef = useRef<HTMLTextAreaElement | null>(null);
  const [isEnhancingIdea, setIsEnhancingIdea] = useState(false);
  const [ideaSuggestions, setIdeaSuggestions] = useState<StoryIdeaEnhanceSuggestion[]>([]);
  const [fictionVariant, setFictionVariant] = useState<string | null>(null);
  const [narrativeEnergy, setNarrativeEnergy] = useState<string>('balanced');
  const [selectedSuggestionIndex, setSelectedSuggestionIndex] = useState<number | null>(null);

  const effectiveMode = (originMode ?? state.storyMode ?? 'pure') as 'marketing' | 'pure';
  const effectiveTemplate = originTemplate ?? state.storyTemplate ?? null;
  const isFictionTemplate =
    effectiveMode === 'pure' &&
    (effectiveTemplate === 'short_fiction' ||
      effectiveTemplate === 'long_fiction' ||
      effectiveTemplate === 'anime_fiction' ||
      effectiveTemplate === 'experimental_fiction');

  // Rotating placeholder effect for story idea textarea
  useEffect(() => {
    // Cleanup function
    const cleanup = () => {
      if (typingIntervalRef.current) {
        clearInterval(typingIntervalRef.current);
        typingIntervalRef.current = null;
      }
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
    };

    const resolvePlaceholders = () => {
      const key = `${effectiveMode}:${effectiveTemplate}`;
      const wildcardKey = `${effectiveMode}:*`;
      if (effectiveMode && effectiveTemplate && STORY_IDEA_PLACEHOLDERS_BY_COMBINATION[key]) {
        return STORY_IDEA_PLACEHOLDERS_BY_COMBINATION[key];
      }
      if (effectiveMode && STORY_IDEA_PLACEHOLDERS_BY_COMBINATION[wildcardKey]) {
        return STORY_IDEA_PLACEHOLDERS_BY_COMBINATION[wildcardKey];
      }
      return STORY_IDEA_PLACEHOLDERS;
    };

    const activePlaceholders = resolvePlaceholders();
    if (!activePlaceholders.length) {
      cleanup();
      setCurrentPlaceholder('');
      charIndexRef.current = 0;
      return cleanup;
    }

    if (!open || storyIdea.trim() !== '') {
      cleanup();
      setCurrentPlaceholder('');
      charIndexRef.current = 0;
      return cleanup;
    }

    // Start typing animation for current placeholder
    const placeholder =
      activePlaceholders[placeholderIndex % activePlaceholders.length];
    charIndexRef.current = 0;
    setCurrentPlaceholder('');

    // Type out characters one by one
    typingIntervalRef.current = setInterval(() => {
      // Check if we should stop
      if (storyIdea.trim() !== '' || !open) {
        cleanup();
        setCurrentPlaceholder('');
        return;
      }

      // Continue typing
      if (charIndexRef.current < placeholder.length) {
        setCurrentPlaceholder(placeholder.substring(0, charIndexRef.current + 1));
        charIndexRef.current += 1;
      } else {
        // Finished typing current placeholder
        cleanup();

        // Wait 4 seconds then move to next placeholder
        timeoutRef.current = setTimeout(() => {
          if (storyIdea.trim() === '' && open) {
            setPlaceholderIndex((prev) => prev + 1);
          }
        }, 4000);
      }
    }, 30);

    return cleanup;
  }, [open, placeholderIndex, storyIdea, effectiveMode, effectiveTemplate]);

  useEffect(() => {
    if (open) {
      setPlaceholderIndex(0);
    }
  }, [effectiveMode, effectiveTemplate, open]);

  useEffect(() => {
    const loadContext = async () => {
      if (!open) return;
      try {
        setIsLoadingContext(true);
        const context = await storyWriterApi.getStoryContext();
        const personaAvailable =
          context && (context.persona_enabled ?? context.has_persona_context ?? false);

        setPersonaEnabled(!!personaAvailable);

        if (personaAvailable && context && context.brand_context) {
          const audienceDescription =
            context.brand_context.audience_description ||
            (context.brand_context as any)?.target_audience ||
            null;
          setBrandContext({
            brand_name: context.brand_context.brand_name ?? null,
            writing_tone: context.brand_context.writing_tone ?? null,
            audience_description: audienceDescription,
          });
        } else {
          setBrandContext(null);
        }

        if (personaAvailable && context && context.brand_assets) {
          setBrandAvatarUrl(context.brand_assets.avatar_url ?? null);
          setBrandVoicePreviewUrl(context.brand_assets.voice_preview_url ?? null);
        } else {
          setBrandAvatarUrl(null);
          setBrandVoicePreviewUrl(null);
        }
      } catch (err) {
        console.error('Failed to load story context:', err);
        setBrandContext(null);
        setBrandAvatarUrl(null);
        setBrandVoicePreviewUrl(null);
      } finally {
        setIsLoadingContext(false);
      }
    };

    loadContext();
  }, [open]);

  useEffect(() => {
    if (effectiveMode === 'marketing') {
      setUsePersonaContext(personaEnabled);
    } else {
      setUsePersonaContext(false);
    }
  }, [effectiveMode, personaEnabled]);

  const handleGenerateSetup = async () => {
    if (!storyIdea.trim()) {
      setSetupError('Please enter a story idea');
      return;
    }

    setIsGeneratingSetup(true);
    setSetupError(null);

    try {
      const modeForRequest: 'marketing' | 'pure' = originMode ?? state.storyMode ?? 'pure';
      const templateForRequest: string | null = effectiveTemplate;

      const shouldSendBrandContext =
        modeForRequest === 'marketing' && usePersonaContext && !!brandContext;

      const response = await storyWriterApi.generateStorySetup({
        story_idea: storyIdea,
        story_mode: modeForRequest,
        story_template: templateForRequest,
        brand_context: shouldSendBrandContext ? brandContext || undefined : undefined,
      });

      if (response.success && response.options && response.options.length >= 1) {
        const option = response.options[0];

        // Extract custom values from the option and add them to custom values lists
        const newCustomWritingStyles = new Set<string>();
        const newCustomStoryTones = new Set<string>();
        const newCustomNarrativePOVs = new Set<string>();
        const newCustomAudienceAgeGroups = new Set<string>();
        const newCustomContentRatings = new Set<string>();
        const newCustomEndingPreferences = new Set<string>();

        if (option.writing_style && !WRITING_STYLES.includes(option.writing_style)) {
          newCustomWritingStyles.add(option.writing_style);
        }
        if (option.story_tone && !STORY_TONES.includes(option.story_tone)) {
          newCustomStoryTones.add(option.story_tone);
        }
        if (option.narrative_pov && !NARRATIVE_POVS.includes(option.narrative_pov)) {
          newCustomNarrativePOVs.add(option.narrative_pov);
        }
        if (option.audience_age_group && !AUDIENCE_AGE_GROUPS.includes(option.audience_age_group)) {
          newCustomAudienceAgeGroups.add(option.audience_age_group);
        }
        if (option.content_rating && !CONTENT_RATINGS.includes(option.content_rating)) {
          newCustomContentRatings.add(option.content_rating);
        }
        if (option.ending_preference && !ENDING_PREFERENCES.includes(option.ending_preference)) {
          newCustomEndingPreferences.add(option.ending_preference);
        }

        // Update custom values state (merge with existing)
        customValuesSetters.setCustomWritingStyles((prev) =>
          [...prev, ...Array.from(newCustomWritingStyles)].filter((v, i, arr) => arr.indexOf(v) === i)
        );
        customValuesSetters.setCustomStoryTones((prev) =>
          [...prev, ...Array.from(newCustomStoryTones)].filter((v, i, arr) => arr.indexOf(v) === i)
        );
        customValuesSetters.setCustomNarrativePOVs((prev) =>
          [...prev, ...Array.from(newCustomNarrativePOVs)].filter((v, i, arr) => arr.indexOf(v) === i)
        );
        customValuesSetters.setCustomAudienceAgeGroups((prev) =>
          [...prev, ...Array.from(newCustomAudienceAgeGroups)].filter((v, i, arr) => arr.indexOf(v) === i)
        );
        customValuesSetters.setCustomContentRatings((prev) =>
          [...prev, ...Array.from(newCustomContentRatings)].filter((v, i, arr) => arr.indexOf(v) === i)
        );
        customValuesSetters.setCustomEndingPreferences((prev) =>
          [...prev, ...Array.from(newCustomEndingPreferences)].filter((v, i, arr) => arr.indexOf(v) === i)
        );

        // Apply the generated option directly to the story setup state
        state.setPersona(option.persona);
        state.setStorySetting(option.story_setting);
        state.setCharacters(option.character_input);
        state.setPlotElements(option.plot_elements);

        const writingStyleValue = option.writing_style || WRITING_STYLES[0];
        const storyToneValue = option.story_tone || STORY_TONES[0];
        const narrativePovValue = option.narrative_pov || NARRATIVE_POVS[0];
        const audienceAgeValue =
          option.audience_age_group ||
          AUDIENCE_AGE_GROUPS[0];
        const contentRatingValue = option.content_rating || CONTENT_RATINGS[0];
        const endingPreferenceValue =
          option.ending_preference || ENDING_PREFERENCES[0];

        state.setWritingStyle(writingStyleValue);
        state.setStoryTone(storyToneValue);
        state.setNarrativePOV(narrativePovValue);

        const normalizedAgeGroup =
          audienceAgeValue === 'Adults'
            ? 'Adults (18+)'
            : audienceAgeValue === 'Children'
              ? 'Children (5-12)'
              : audienceAgeValue === 'Young Adults'
                ? 'Young Adults (13-17)'
                : audienceAgeValue;
        state.setAudienceAgeGroup(normalizedAgeGroup);
        state.setContentRating(contentRatingValue);
        state.setEndingPreference(endingPreferenceValue);

        if (option.story_length) {
          state.setStoryLength(option.story_length);
        }
        if (option.premise) {
          state.setPremise(option.premise);
        }
        if (option.image_provider !== undefined) {
          state.setImageProvider(option.image_provider || null);
        }
        if (option.image_width !== undefined) {
          state.setImageWidth(option.image_width);
        }
        if (option.image_height !== undefined) {
          state.setImageHeight(option.image_height);
        }
        if (option.image_model !== undefined) {
          state.setImageModel(option.image_model || null);
        }
        if (option.video_fps !== undefined) {
          state.setVideoFps(option.video_fps);
        }
        if (option.video_transition_duration !== undefined) {
          state.setVideoTransitionDuration(option.video_transition_duration);
        }
        if (option.audio_provider !== undefined) {
          state.setAudioProvider(option.audio_provider);
        }
        if (option.audio_lang !== undefined) {
          state.setAudioLang(option.audio_lang);
        }
        if (option.audio_slow !== undefined) {
          state.setAudioSlow(option.audio_slow);
        }
        if (option.audio_rate !== undefined) {
          state.setAudioRate(option.audio_rate);
        }

        // Close modal and notify caller; parent should navigate to Story Setup phase
        onClose();
        if (onApplied) {
          onApplied();
        }
      } else {
        throw new Error('Failed to generate story setup options');
      }
    } catch (err: any) {
      console.error('Story setup generation failed:', err);

      const status = err?.response?.status;
      if (status === 401) {
        try {
          window.location.assign('/');
        } catch {}
        setIsGeneratingSetup(false);
        return;
      }

      // Check if this is a subscription error (429/402) and trigger global subscription modal
      if (status === 429 || status === 402) {
        console.log('StorySetup: Detected subscription error, triggering global handler', {
          status,
          data: err?.response?.data,
        });
        const handled = await triggerSubscriptionError(err);
        if (handled) {
          console.log('StorySetup: Global subscription error handler triggered successfully');
          // Don't set local error - let the global modal handle it
          setIsGeneratingSetup(false);
          return;
        } else {
          console.warn('StorySetup: Global subscription error handler did not handle the error');
        }
      }

      // For non-subscription errors, show local error message
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to generate story setup options';
      setSetupError(errorMessage);
    } finally {
      setIsGeneratingSetup(false);
    }
  };

  const focusStoryIdeaInput = () => {
    if (storyIdeaInputRef.current) {
      storyIdeaInputRef.current.focus();
      try {
        storyIdeaInputRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' });
      } catch {
        // ignore
      }
    }
  };

  const handleClose = () => {
    setStoryIdea('');
    setSetupError(null);
    setIdeaSuggestions([]);
    setFictionVariant(null);
    setNarrativeEnergy('balanced');
    setPlaceholderIndex(0);
    setCurrentPlaceholder('');
    setBrandContext(null);
    setBrandAvatarUrl(null);
    setBrandVoicePreviewUrl(null);
    charIndexRef.current = 0;
    // Cleanup intervals
    if (typingIntervalRef.current) {
      clearInterval(typingIntervalRef.current);
      typingIntervalRef.current = null;
    }
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    onClose();
  };

  const wordCount = storyIdea.trim() ? storyIdea.trim().split(/\s+/).length : 0;
  const showEnhanceButton =
    wordCount >= 10 && !isGeneratingSetup && !isEnhancingIdea;

  const handleEnhanceStoryIdea = async () => {
    if (!storyIdea.trim() || isGeneratingSetup || isEnhancingIdea) {
      return;
    }

    setIsEnhancingIdea(true);
    setSetupError(null);
     setIdeaSuggestions([]);

    try {
      const modeForRequest: 'marketing' | 'pure' = originMode ?? state.storyMode ?? 'pure';
      const templateForRequest: string | null = effectiveTemplate;

      const shouldSendBrandContext =
        modeForRequest === 'marketing' && usePersonaContext && !!brandContext;

      const isFictionForRequest =
        modeForRequest === 'pure' &&
        (templateForRequest === 'short_fiction' ||
          templateForRequest === 'long_fiction' ||
          templateForRequest === 'anime_fiction' ||
          templateForRequest === 'experimental_fiction');

      const response = await storyWriterApi.enhanceStoryIdea({
        story_idea: storyIdea,
        story_mode: modeForRequest,
        story_template: templateForRequest,
        brand_context: shouldSendBrandContext ? brandContext || undefined : undefined,
        fiction_variant: isFictionForRequest ? fictionVariant || undefined : undefined,
        narrative_energy: isFictionForRequest ? narrativeEnergy || undefined : undefined,
      });

      if (response.success && response.suggestions && response.suggestions.length) {
        setIdeaSuggestions(response.suggestions);
      } else {
        throw new Error('Failed to enhance story idea');
      }
    } catch (err: any) {
      const errorMessage =
        err?.response?.data?.detail || err?.message || 'Failed to enhance story idea';
      setSetupError(errorMessage);
    } finally {
      setIsEnhancingIdea(false);
    }
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 3,
          bgcolor: 'rgba(248,250,252,0.98)',
          color: '#0f172a',
          backgroundImage: 'radial-gradient(circle at top left, rgba(129,140,248,0.18), transparent 55%), radial-gradient(circle at bottom right, rgba(244,114,182,0.16), transparent 55%)',
          boxShadow: '0 32px 80px rgba(15,23,42,0.45)',
          border: '1px solid rgba(148,163,184,0.35)',
        },
      }}
      sx={{
        '& .MuiBackdrop-root': {
          backgroundColor: 'rgba(15,23,42,0.75)',
        },
      }}
    >
      <DialogTitle>
        Generate Story Setup With Alwrity AI
      </DialogTitle>
      <DialogContent>
        {personaEnabled && (
          <Box sx={{ mb: 1, display: 'flex', justifyContent: 'flex-end' }}>
            <FormControlLabel
              control={
                <Switch
                  size="small"
                  checked={usePersonaContext && personaEnabled && effectiveMode === 'marketing'}
                  onChange={(_, checked) => setUsePersonaContext(checked)}
                  disabled={!personaEnabled || effectiveMode !== 'marketing'}
                />
              }
              label={
                <Typography variant="body2" sx={{ color: '#4b5563' }}>
                  Use onboarding brand persona
                  {effectiveMode === 'pure' ? ' (only available for Non-fiction)' : ''}
                </Typography>
              }
            />
          </Box>
        )}
        {usePersonaContext && (brandContext || brandAvatarUrl || brandVoicePreviewUrl) && (
          <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              {brandAvatarUrl && (
                <Box
                  component="img"
                  src={brandAvatarUrl}
                  alt={brandContext?.brand_name || 'Brand avatar'}
                  sx={{
                    width: 40,
                    height: 40,
                    borderRadius: '50%',
                    border: '2px solid rgba(255,255,255,0.6)',
                    boxShadow: '0 4px 10px rgba(0,0,0,0.25)',
                    objectFit: 'cover',
                  }}
                />
              )}
              <Box>
                <Typography variant="subtitle2" sx={{ color: '#4E342E' }}>
                  {brandContext?.brand_name || 'Your brand'}
                </Typography>
                <Typography variant="body2" sx={{ color: '#6D4C41' }}>
                  {brandContext?.writing_tone || 'Brand tone inferred from your site'}
                </Typography>
                {brandContext?.audience_description && (
                  <Typography variant="body2" sx={{ color: '#6D4C41' }}>
                    Audience: {brandContext.audience_description}
                  </Typography>
                )}
              </Box>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {brandVoicePreviewUrl && (
                <audio
                  src={brandVoicePreviewUrl}
                  controls
                  style={{ height: 32 }}
                />
              )}
              {isLoadingContext && (
                <CircularProgress size={18} />
              )}
            </Box>
          </Box>
        )}
        <Typography variant="body2" sx={{ mb: 2, color: '#4b5563' }}>
          Enter your story idea or basic information. The more details you provide, the better story setups will be generated.
        </Typography>
        {(() => {
          const effectiveMode = originMode ?? state.storyMode;
          const effectiveTemplate = originTemplate ?? state.storyTemplate;
          const modeLabel =
            effectiveMode === 'marketing' ? 'Non-fiction' : effectiveMode === 'pure' ? 'Fiction' : null;
          const templateLabel =
            effectiveTemplate === 'product_story'
              ? 'Product Story'
              : effectiveTemplate === 'brand_manifesto'
                ? 'Brand Manifesto'
                : effectiveTemplate === 'founder_story'
                  ? 'Founder Story'
                  : effectiveTemplate === 'customer_story'
                    ? 'Customer Story'
                    : effectiveTemplate === 'short_fiction'
                      ? 'Short Fiction'
                      : effectiveTemplate === 'long_fiction'
                        ? 'Long Fiction'
                        : effectiveTemplate === 'anime_fiction'
                          ? 'Anime Fiction'
                          : effectiveTemplate === 'experimental_fiction'
                            ? 'Experimental'
                            : null;

          if (!modeLabel && !templateLabel) {
            return null;
          }

          return (
            <Typography variant="body2" sx={{ mb: 2, color: '#374151' }}>
              {modeLabel || 'Story'}
              {templateLabel ? ` · ${templateLabel}` : ''}
            </Typography>
          );
        })()}

        {setupError && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setSetupError(null)}>
            {setupError}
          </Alert>
        )}

        {isFictionTemplate && (
          <Box sx={{ mb: 2, display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 2 }}>
            <Box sx={{ flex: 2 }}>
              <Typography variant="subtitle2" sx={{ mb: 1, color: '#111827' }}>
                Fiction Focus
              </Typography>
              <RadioGroup
                row
                value={fictionVariant || ''}
                onChange={(e) => setFictionVariant(e.target.value)}
              >
                {(FICTION_VARIANT_OPTIONS[effectiveTemplate || ''] || []).map((opt) => (
                  <FormControlLabel
                    key={opt.value}
                    value={opt.value}
                    control={<Radio size="small" />}
                    label={
                      <Typography variant="body2" sx={{ color: '#374151' }}>
                        {opt.label}
                      </Typography>
                    }
                  />
                ))}
              </RadioGroup>
            </Box>
            <Box sx={{ flex: 1 }}>
              <Typography variant="subtitle2" sx={{ mb: 1, color: '#111827' }}>
                Narrative Energy
              </Typography>
              <RadioGroup
                row
                value={narrativeEnergy}
                onChange={(e) => setNarrativeEnergy(e.target.value)}
              >
                <FormControlLabel
                  value="grounded"
                  control={<Radio size="small" />}
                  label={
                    <Typography variant="body2" sx={{ color: '#374151' }}>
                      Grounded
                    </Typography>
                  }
                />
                <FormControlLabel
                  value="balanced"
                  control={<Radio size="small" />}
                  label={
                    <Typography variant="body2" sx={{ color: '#374151' }}>
                      Balanced
                    </Typography>
                  }
                />
                <FormControlLabel
                  value="cinematic"
                  control={<Radio size="small" />}
                  label={
                    <Typography variant="body2" sx={{ color: '#374151' }}>
                      Cinematic
                    </Typography>
                  }
                />
              </RadioGroup>
            </Box>
          </Box>
        )}

        <Box
          sx={{
            position: 'relative',
            mb: 3,
            borderRadius: 3,
            p: 1,
            background: 'radial-gradient(circle at 0% 0%, rgba(59,130,246,0.08), transparent 55%), radial-gradient(circle at 100% 100%, rgba(236,72,153,0.08), transparent 55%)',
            '&::before': {
              content: '""',
              position: 'absolute',
              inset: 0,
              borderRadius: 20,
              padding: '1px',
              background: 'linear-gradient(120deg, rgba(59,130,246,0.2), rgba(236,72,153,0.35), rgba(16,185,129,0.22), rgba(129,140,248,0.28))',
              backgroundSize: '300% 300%',
              WebkitMask: 'linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0)',
              WebkitMaskComposite: 'xor',
              maskComposite: 'exclude',
              animation: 'aiBorderOrbit 6s linear infinite',
              pointerEvents: 'none',
            },
            '@keyframes aiBorderOrbit': {
              '0%': { backgroundPosition: '0% 50%' },
              '50%': { backgroundPosition: '100% 50%' },
              '100%': { backgroundPosition: '0% 50%' },
            },
          }}
        >
          <Box
            sx={{
              position: 'relative',
              borderRadius: 2,
              bgcolor: '#ffffff',
              boxShadow: '0 18px 45px rgba(15,23,42,0.18)',
            }}
          >
            <TextField
              fullWidth
              multiline
              rows={6}
              label="Story Idea"
              autoFocus
              inputRef={storyIdeaInputRef}
              placeholder={
                currentPlaceholder ||
                'Enter your story idea, characters, setting, plot elements, or any other relevant information...'
              }
              value={storyIdea}
              onChange={(e) => setStoryIdea(e.target.value)}
              sx={{
                ...textFieldStyles,
                '& .MuiInputBase-input': {
                  color: '#0f172a',
                },
                '& .MuiOutlinedInput-root': {
                  bgcolor: '#ffffff',
                  '& fieldset': {
                    borderColor: 'rgba(148,163,184,0.7)',
                  },
                  '&:hover fieldset': {
                    borderColor: 'rgba(79,70,229,0.9)',
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: 'rgba(129,140,248,1)',
                    boxShadow: '0 0 0 1px rgba(129,140,248,0.5)',
                  },
                },
              }}
              helperText="Provide as much detail as possible. Include characters, setting, plot, themes, or any story elements you want to explore."
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <Tooltip
                      title={
                        <Box>
                          <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                            Story Idea Input
                          </Typography>
                          <Typography variant="body2" sx={{ mb: 1 }}>
                            Enter your story idea or concept. The more details you provide, the better the AI can generate tailored story setup options. Include:
                          </Typography>
                          <Typography variant="body2" component="div">
                            • Main characters and their roles
                            <br />
                            • Setting and time period
                            <br />
                            • Key plot points or conflicts
                            <br />
                            • Themes or messages
                            <br />
                            • Genre or style preferences
                            <br />
                            • Any specific story elements you want
                          </Typography>
                          <Typography variant="body2" sx={{ mt: 1, fontStyle: 'italic', color: '#6b7280' }}>
                            Watch the placeholder examples cycle through for inspiration.
                          </Typography>
                        </Box>
                      }
                      arrow
                      placement="top"
                    >
                      <IconButton size="small" edge="end">
                        <InfoOutlined fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </InputAdornment>
                ),
              }}
            />
          </Box>
          {isEnhancingIdea && (
            <Box sx={{ mt: 1.5, display: 'flex', alignItems: 'center', gap: 1 }}>
              <CircularProgress size={16} />
              <Typography variant="body2" sx={{ color: '#4b5563' }}>
                Alwrity AI is reading your idea and drafting 3 enhanced options with gaps and
                recommendations.
              </Typography>
            </Box>
          )}
          {showEnhanceButton && (
            <Box
              sx={{
                position: 'absolute',
                right: 28,
                bottom: 24,
                pointerEvents: 'none',
              }}
            >
              <Tooltip
                title="Use AI to expand and refine your story idea with richer details, characters, and stakes. This only improves the idea; setup fields are generated when you continue to story setup."
                arrow
              >
                <span>
                  <Button
                    size="small"
                    variant="contained"
                    onClick={handleEnhanceStoryIdea}
                    disabled={isGeneratingSetup || isEnhancingIdea}
                    sx={{
                      pointerEvents: 'auto',
                      borderRadius: 999,
                      px: 2,
                      py: 0.5,
                      textTransform: 'none',
                      fontSize: 12,
                      background: 'linear-gradient(90deg,#6366f1,#ec4899)',
                      boxShadow: '0 10px 20px rgba(15,23,42,0.35)',
                      '&:hover': {
                        background: 'linear-gradient(90deg,#4f46e5,#db2777)',
                        boxShadow: '0 12px 24px rgba(15,23,42,0.45)',
                      },
                    }}
                  >
                    Enhance Story Idea
                  </Button>
                </span>
              </Tooltip>
            </Box>
          )}
        </Box>

        {ideaSuggestions.length > 0 && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle1" sx={{ mb: 1.5, fontWeight: 600, color: '#111827' }}>
              AI-enhanced idea options
            </Typography>
            <Typography variant="body2" sx={{ mb: 1.5, color: '#4b5563' }}>
              Choose one of these refined ideas, or use them as inspiration to further edit your own.
            </Typography>
            <RadioGroup
              value={selectedSuggestionIndex !== null ? selectedSuggestionIndex.toString() : ''}
              onChange={(e) => {
                const idx = Number(e.target.value);
                setSelectedSuggestionIndex(idx);
                if (ideaSuggestions[idx]) {
                  setStoryIdea(ideaSuggestions[idx].idea);
                  focusStoryIdeaInput();
                }
              }}
            >
              {ideaSuggestions.map((sugg, index) => (
                <Card
                  key={index}
                  sx={{
                    mb: 2,
                    ...cardStyles,
                    borderColor:
                      selectedSuggestionIndex === index ? 'primary.main' : 'rgba(148,163,184,0.7)',
                    cursor: 'pointer',
                    '&:hover': {
                      borderColor: 'primary.main',
                    },
                  }}
                  onClick={() => {
                    setSelectedSuggestionIndex(index);
                    setStoryIdea(sugg.idea);
                    focusStoryIdeaInput();
                  }}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.5 }}>
                      <Radio
                        value={index}
                        checked={selectedSuggestionIndex === index}
                        sx={{ mt: 0.5 }}
                      />
                      <Box sx={{ flex: 1 }}>
                        <Typography
                          variant="subtitle2"
                          sx={{ fontWeight: 600, mb: 1, color: '#111827' }}
                        >
                          Option {index + 1}
                        </Typography>
                        <Typography variant="body2" sx={{ mb: 1, color: '#374151' }}>
                          {sugg.idea}
                        </Typography>
                        <Typography
                          variant="body2"
                          sx={{ mt: 1, mb: 0.5, fontWeight: 600, color: '#111827' }}
                        >
                          What&apos;s Missing from Plot
                        </Typography>
                        <Typography variant="body2" sx={{ mb: 1, color: '#4b5563' }}>
                          {sugg.whats_missing}
                        </Typography>
                        <Typography
                          variant="body2"
                          sx={{ mt: 0.5, mb: 0.5, fontWeight: 600, color: '#111827' }}
                        >
                          Why choose this Plot
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#4b5563' }}>
                          {sugg.why_choose}
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              ))}
            </RadioGroup>
          </Box>
        )}

        {isGeneratingSetup && (
          <Box sx={{ display: 'flex', alignItems: 'center', py: 3, gap: 2 }}>
            <CircularProgress size={24} />
            <Box>
              <Typography sx={{ color: '#111827', fontWeight: 500 }}>
                Generating your Story Setup…
              </Typography>
              <Typography variant="body2" sx={{ color: '#4b5563' }}>
                Alwrity AI is creating persona, setting, characters and plot knobs. You&apos;ll be
                taken to the Story Setup phase with everything pre-filled in a moment.
              </Typography>
            </Box>
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button
          onClick={handleGenerateSetup}
          disabled={!storyIdea.trim() || isGeneratingSetup}
          variant="contained"
          sx={{
            textTransform: 'none',
            fontWeight: 600,
            px: 3,
            borderRadius: 999,
            background: 'linear-gradient(90deg,#6366f1,#ec4899)',
            color: '#ffffff',
            boxShadow: '0 12px 30px rgba(15,23,42,0.4)',
            '&:hover': {
              background: 'linear-gradient(90deg,#4f46e5,#db2777)',
              boxShadow: '0 14px 36px rgba(15,23,42,0.5)',
            },
            '&.Mui-disabled': {
              background: 'rgba(148,163,184,0.5)',
              color: '#f9fafb',
              boxShadow: 'none',
            },
          }}
        >
          {isGeneratingSetup ? 'Generating Story Setup…' : 'Continue to Story Setup'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

