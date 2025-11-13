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
} from '@mui/material';
import { InfoOutlined } from '@mui/icons-material';
import { storyWriterApi, StorySetupOption } from '../../../../services/storyWriterApi';
import { triggerSubscriptionError } from '../../../../api/client';
import { useStoryWriterState } from '../../../../hooks/useStoryWriterState';
import { STORY_IDEA_PLACEHOLDERS } from './constants';
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
}

export const AIStorySetupModal: React.FC<AIStorySetupModalProps> = ({
  open,
  onClose,
  state,
  customValuesSetters,
}) => {
  const [storyIdea, setStoryIdea] = useState('');
  const [isGeneratingSetup, setIsGeneratingSetup] = useState(false);
  const [setupOptions, setSetupOptions] = useState<StorySetupOption[]>([]);
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [setupError, setSetupError] = useState<string | null>(null);
  const [placeholderIndex, setPlaceholderIndex] = useState(0);
  const [currentPlaceholder, setCurrentPlaceholder] = useState('');
  const typingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const charIndexRef = useRef(0);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

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

    // Stop all effects if modal is closed or user has entered text
    if (!open || storyIdea.trim() !== '') {
      cleanup();
      setCurrentPlaceholder('');
      charIndexRef.current = 0;
      return cleanup;
    }

    // Start typing animation for current placeholder
    const placeholder = STORY_IDEA_PLACEHOLDERS[placeholderIndex];
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
            setPlaceholderIndex((prev) => (prev + 1) % STORY_IDEA_PLACEHOLDERS.length);
          }
        }, 4000);
      }
    }, 30);

    return cleanup;
  }, [open, placeholderIndex, storyIdea]);

  const handleGenerateSetup = async () => {
    if (!storyIdea.trim()) {
      setSetupError('Please enter a story idea');
      return;
    }

    setIsGeneratingSetup(true);
    setSetupError(null);

    try {
      const response = await storyWriterApi.generateStorySetup({
        story_idea: storyIdea,
      });

      if (response.success && response.options && response.options.length === 3) {
        setSetupOptions(response.options);

        // Extract custom values from all options and add them to custom values lists
        const newCustomWritingStyles = new Set<string>();
        const newCustomStoryTones = new Set<string>();
        const newCustomNarrativePOVs = new Set<string>();
        const newCustomAudienceAgeGroups = new Set<string>();
        const newCustomContentRatings = new Set<string>();
        const newCustomEndingPreferences = new Set<string>();

        response.options.forEach((option) => {
          // Check if values are custom (not in predefined lists)
          if (!WRITING_STYLES.includes(option.writing_style)) {
            newCustomWritingStyles.add(option.writing_style);
          }
          if (!STORY_TONES.includes(option.story_tone)) {
            newCustomStoryTones.add(option.story_tone);
          }
          if (!NARRATIVE_POVS.includes(option.narrative_pov)) {
            newCustomNarrativePOVs.add(option.narrative_pov);
          }
          if (!AUDIENCE_AGE_GROUPS.includes(option.audience_age_group)) {
            newCustomAudienceAgeGroups.add(option.audience_age_group);
          }
          if (!CONTENT_RATINGS.includes(option.content_rating)) {
            newCustomContentRatings.add(option.content_rating);
          }
          if (!ENDING_PREFERENCES.includes(option.ending_preference)) {
            newCustomEndingPreferences.add(option.ending_preference);
          }
        });

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
      } else {
        throw new Error('Failed to generate story setup options');
      }
    } catch (err: any) {
      console.error('Story setup generation failed:', err);

      // Check if this is a subscription error (429/402) and trigger global subscription modal
      const status = err?.response?.status;
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

  const handleSelectOption = (index: number) => {
    setSelectedOption(index);
  };

  const handleApplyOption = () => {
    if (selectedOption === null || !setupOptions[selectedOption]) {
      setSetupError('Please select an option');
      return;
    }

    const option = setupOptions[selectedOption];

    // Extract and add custom values to dropdowns if they don't exist
    if (!WRITING_STYLES.includes(option.writing_style)) {
      customValuesSetters.setCustomWritingStyles((prev) =>
        prev.includes(option.writing_style) ? prev : [...prev, option.writing_style]
      );
    }
    if (!STORY_TONES.includes(option.story_tone)) {
      customValuesSetters.setCustomStoryTones((prev) =>
        prev.includes(option.story_tone) ? prev : [...prev, option.story_tone]
      );
    }
    if (!NARRATIVE_POVS.includes(option.narrative_pov)) {
      customValuesSetters.setCustomNarrativePOVs((prev) =>
        prev.includes(option.narrative_pov) ? prev : [...prev, option.narrative_pov]
      );
    }
    if (!AUDIENCE_AGE_GROUPS.includes(option.audience_age_group)) {
      customValuesSetters.setCustomAudienceAgeGroups((prev) =>
        prev.includes(option.audience_age_group) ? prev : [...prev, option.audience_age_group]
      );
    }
    if (!CONTENT_RATINGS.includes(option.content_rating)) {
      customValuesSetters.setCustomContentRatings((prev) =>
        prev.includes(option.content_rating) ? prev : [...prev, option.content_rating]
      );
    }
    if (!ENDING_PREFERENCES.includes(option.ending_preference)) {
      customValuesSetters.setCustomEndingPreferences((prev) =>
        prev.includes(option.ending_preference) ? prev : [...prev, option.ending_preference]
      );
    }

    // Apply the selected option to the form
    state.setPersona(option.persona);
    state.setStorySetting(option.story_setting);
    state.setCharacters(option.character_input);
    state.setPlotElements(option.plot_elements);
    state.setWritingStyle(option.writing_style);
    state.setStoryTone(option.story_tone);
    state.setNarrativePOV(option.narrative_pov);
    // Normalize audience_age_group value (migrate old format if needed, but preserve custom values)
    const normalizedAgeGroup =
      option.audience_age_group === 'Adults'
        ? 'Adults (18+)'
        : option.audience_age_group === 'Children'
          ? 'Children (5-12)'
          : option.audience_age_group === 'Young Adults'
            ? 'Young Adults (13-17)'
            : option.audience_age_group;
    state.setAudienceAgeGroup(normalizedAgeGroup);
    state.setContentRating(option.content_rating);
    state.setEndingPreference(option.ending_preference);

    // Apply story length if provided
    if (option.story_length) {
      state.setStoryLength(option.story_length);
    }

    // Apply premise if provided
    if (option.premise) {
      state.setPremise(option.premise);
    }

    // Apply image/video/audio settings if provided
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

    // Close modal
    onClose();
  };

  const handleClose = () => {
    setStoryIdea('');
    setSetupOptions([]);
    setSelectedOption(null);
    setSetupError(null);
    setPlaceholderIndex(0);
    setCurrentPlaceholder('');
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

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>Generate Story Setup With Alwrity AI</DialogTitle>
      <DialogContent>
        <Typography variant="body2" sx={{ mb: 2, color: '#5D4037' }}>
          Enter your story idea or basic information. The more details you provide, the better story setups will be generated.
        </Typography>

        {setupError && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setSetupError(null)}>
            {setupError}
          </Alert>
        )}

        <TextField
          fullWidth
          multiline
          rows={6}
          label="Story Idea"
          placeholder={currentPlaceholder || "Enter your story idea, characters, setting, plot elements, or any other relevant information..."}
          value={storyIdea}
          onChange={(e) => setStoryIdea(e.target.value)}
          sx={{ ...textFieldStyles, mb: 3 }}
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
                      <Typography variant="body2" sx={{ mt: 1, fontStyle: 'italic', color: '#5D4037' }}>
                        Watch the placeholder examples cycle through for inspiration!
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

        {isGeneratingSetup && (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 3 }}>
            <CircularProgress size={24} sx={{ mr: 2 }} />
            <Typography sx={{ color: '#2C2416' }}>Generating story setup options...</Typography>
          </Box>
        )}

        {setupOptions.length > 0 && (
          <Box>
            <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600, color: '#1A1611' }}>
              Select one of the following options:
            </Typography>
            <RadioGroup
              value={selectedOption !== null ? selectedOption.toString() : ''}
              onChange={(e) => handleSelectOption(Number(e.target.value))}
            >
              {setupOptions.map((option, index) => (
                <Card
                  key={index}
                  sx={{
                    mb: 2,
                    ...cardStyles,
                    border: selectedOption === index ? 2 : 1,
                    borderColor: selectedOption === index ? 'primary.main' : 'divider',
                    cursor: 'pointer',
                    '&:hover': {
                      borderColor: 'primary.main',
                    },
                  }}
                  onClick={() => handleSelectOption(index)}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                      <Radio value={index} checked={selectedOption === index} />
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: '#1A1611' }}>
                          Option {index + 1}
                        </Typography>
                        <Typography variant="body2" sx={{ mb: 1, color: '#5D4037' }}>
                          <strong>Persona:</strong> {option.persona}
                        </Typography>
                        <Typography variant="body2" sx={{ mb: 1, color: '#5D4037' }}>
                          <strong>Setting:</strong> {option.story_setting}
                        </Typography>
                        <Typography variant="body2" sx={{ mb: 1, color: '#5D4037' }}>
                          <strong>Characters:</strong> {option.character_input}
                        </Typography>
                        <Typography variant="body2" sx={{ mb: 1, color: '#5D4037' }}>
                          <strong>Plot Elements:</strong> {option.plot_elements}
                        </Typography>
                        <Typography variant="body2" sx={{ mb: 1, color: '#5D4037' }}>
                          <strong>Style:</strong> {option.writing_style} | <strong>Tone:</strong> {option.story_tone} | <strong>POV:</strong> {option.narrative_pov}
                        </Typography>
                        <Typography variant="body2" sx={{ mb: 1, color: '#5D4037' }}>
                          <strong>Audience:</strong> {option.audience_age_group} | <strong>Rating:</strong> {option.content_rating} | <strong>Ending:</strong> {option.ending_preference}
                        </Typography>
                        <Typography variant="body2" sx={{ mt: 1, fontStyle: 'italic', color: '#5D4037' }}>
                          <strong>Reasoning:</strong> {option.reasoning}
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              ))}
            </RadioGroup>
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        {setupOptions.length === 0 ? (
          <Button
            onClick={handleGenerateSetup}
            disabled={!storyIdea.trim() || isGeneratingSetup}
            variant="contained"
          >
            {isGeneratingSetup ? 'Generating...' : 'Generate Options'}
          </Button>
        ) : (
          <Button onClick={handleApplyOption} disabled={selectedOption === null} variant="contained">
            Apply Selected Option
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

