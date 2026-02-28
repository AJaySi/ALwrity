import React, { useState, useEffect } from 'react';
import { Paper, Typography, Box, Button, Alert, Grid, CircularProgress } from '@mui/material';
import { storyWriterApi, StoryScene } from '../../../../services/storyWriterApi';
import { triggerSubscriptionError } from '../../../../api/client';
import { StoryParametersSection } from './StoryParametersSection';
import { StoryConfigurationSection } from './StoryConfigurationSection';

// TODO: Reintroduce FeatureCheckboxesSection and GenerationSettingsSection in a later
// publishing/campaign configuration phase (after Outline/Writing), so they feel like
// output configuration rather than part of the initial story setup step.
import { textFieldStyles, paperStyles } from './styles';
import { AUDIENCE_AGE_GROUPS } from './constants';
import { StorySetupProps, CustomValuesState, CustomValuesSetters } from './types';

const StorySetup: React.FC<StorySetupProps> = ({ state, onNext }) => {
  const [isRegeneratingPremise, setIsRegeneratingPremise] = useState(false);
  const [isGeneratingOutline, setIsGeneratingOutline] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Track custom values from AI-generated options
  const [customWritingStyles, setCustomWritingStyles] = useState<string[]>([]);
  const [customStoryTones, setCustomStoryTones] = useState<string[]>([]);
  const [customNarrativePOVs, setCustomNarrativePOVs] = useState<string[]>([]);
  const [customAudienceAgeGroups, setCustomAudienceAgeGroups] = useState<string[]>([]);
  const [customContentRatings, setCustomContentRatings] = useState<string[]>([]);
  const [customEndingPreferences, setCustomEndingPreferences] = useState<string[]>([]);

  const customValues: CustomValuesState = {
    customWritingStyles,
    customStoryTones,
    customNarrativePOVs,
    customAudienceAgeGroups,
    customContentRatings,
    customEndingPreferences,
  };

  const handleGenerateOutlineAndProceed = async () => {
    if (!state.premise) {
      setError('Please generate a premise before generating the outline');
      return;
    }

    setIsGeneratingOutline(true);
    setError(null);

    try {
      const request = state.getRequest();
      const response = await storyWriterApi.generateOutline(state.premise, request);

      if (response.anime_bible) {
        state.setAnimeBible(response.anime_bible);
      }

      if (response.success && response.outline) {
        if (response.is_structured && Array.isArray(response.outline)) {
          const scenes = response.outline as StoryScene[];
          state.setOutlineScenes(scenes);
          state.setIsOutlineStructured(true);
          const formattedOutline = scenes
            .map((scene, idx) => `Scene ${scene.scene_number || idx + 1}: ${scene.title}\n${scene.description}`)
            .join('\n\n');
          state.setOutline(formattedOutline);
        } else {
          state.setOutline(typeof response.outline === 'string' ? response.outline : String(response.outline));
          state.setOutlineScenes(null);
          state.setIsOutlineStructured(false);
        }
        state.setError(null);
        onNext();
      } else {
        throw new Error(typeof response.outline === 'string' ? response.outline : 'Failed to generate outline');
      }
    } catch (err: any) {
      const status = err?.response?.status;
      if (status === 429 || status === 402) {
        const handled = await triggerSubscriptionError(err);
        if (handled) {
          setIsGeneratingOutline(false);
          return;
        }
      }

      const errorMessage = err.response?.data?.detail || err.message || 'Failed to generate outline';
      setError(errorMessage);
      state.setError(errorMessage);
    } finally {
      setIsGeneratingOutline(false);
    }
  };

  const customValuesSetters: CustomValuesSetters = {
    setCustomWritingStyles,
    setCustomStoryTones,
    setCustomNarrativePOVs,
    setCustomAudienceAgeGroups,
    setCustomContentRatings,
    setCustomEndingPreferences,
  };

  // Get normalized audienceAgeGroup value (fallback to default if invalid, but preserve custom values)
  const allAudienceAgeGroups = [...AUDIENCE_AGE_GROUPS, ...customAudienceAgeGroups];
  const normalizedAudienceAgeGroup = allAudienceAgeGroups.includes(state.audienceAgeGroup)
    ? state.audienceAgeGroup
    : state.audienceAgeGroup === 'Adults'
      ? 'Adults (18+)'
      : state.audienceAgeGroup === 'Children'
        ? 'Children (5-12)'
        : state.audienceAgeGroup === 'Young Adults'
          ? 'Young Adults (13-17)'
          : state.audienceAgeGroup || 'Adults (18+)'; // Preserve custom values instead of defaulting

  // Fix invalid audienceAgeGroup values on mount and when state changes (but preserve custom values)
  useEffect(() => {
    // Only normalize if it's an old format value, not a custom value
    if (
      state.audienceAgeGroup &&
      state.audienceAgeGroup !== normalizedAudienceAgeGroup &&
      !allAudienceAgeGroups.includes(state.audienceAgeGroup) &&
      (state.audienceAgeGroup === 'Adults' ||
        state.audienceAgeGroup === 'Children' ||
        state.audienceAgeGroup === 'Young Adults')
    ) {
      state.setAudienceAgeGroup(normalizedAudienceAgeGroup);
    }
  }, [state.audienceAgeGroup, normalizedAudienceAgeGroup, state.setAudienceAgeGroup, allAudienceAgeGroups]);

  const handleRegeneratePremise = async () => {
    // Validate required fields
    if (!state.persona || !state.storySetting || !state.characters || !state.plotElements) {
      setError('Please fill in all required fields (Persona, Setting, Characters, Plot Elements)');
      return;
    }

    setIsRegeneratingPremise(true);
    setError(null);

    try {
      const request = state.getRequest();
      const response = await storyWriterApi.generatePremise(request);

      if (response.success && response.premise) {
        state.setPremise(response.premise);
        state.setError(null);
      } else {
        throw new Error(response.premise || 'Failed to generate premise');
      }
    } catch (err: any) {
      // Check if this is a subscription error (429/402) and trigger global subscription modal
      const status = err?.response?.status;
      if (status === 429 || status === 402) {
        console.log('StorySetup: Detected subscription error in regenerate premise, triggering global handler', {
          status,
          data: err?.response?.data,
        });
        const handled = await triggerSubscriptionError(err);
        if (handled) {
          console.log('StorySetup: Global subscription error handler triggered successfully');
          setIsRegeneratingPremise(false);
          return;
        } else {
          console.warn('StorySetup: Global subscription error handler did not handle the error');
        }
      }

      // For non-subscription errors, show local error message
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to generate premise';
      setError(errorMessage);
      state.setError(errorMessage);
    } finally {
      setIsRegeneratingPremise(false);
    }
  };

  return (
    <>
      <Paper sx={paperStyles}>
        <Box
          sx={{
            display: 'flex',
            flexDirection: { xs: 'column', md: 'row' },
            justifyContent: 'space-between',
            alignItems: { xs: 'flex-start', md: 'center' },
            gap: 3,
            mb: 4,
          }}
        >
          <Box>
            <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, color: '#1A1611' }}>
              Story Studio Setup
            </Typography>
            <Typography variant="body2" sx={{ color: '#5D4037', mb: 1.5 }}>
              Configure your core story parameters and premise. These choices will guide outline and writing in the next phases.
            </Typography>
            {(() => {
              const modeLabel =
                state.storyMode === 'marketing'
                  ? 'Non-fiction'
                  : state.storyMode === 'pure'
                    ? 'Fiction'
                    : null;

              let templateLabel: string | null = null;
              if (state.storyMode === 'marketing') {
                templateLabel =
                  state.storyTemplate === 'product_story'
                    ? 'Product Story'
                    : state.storyTemplate === 'brand_manifesto'
                      ? 'Brand Manifesto'
                      : state.storyTemplate === 'founder_story'
                        ? 'Founder Story'
                        : state.storyTemplate === 'customer_story'
                          ? 'Customer Story'
                          : null;
              }

              if (!modeLabel && !templateLabel) return null;

              return (
                <Typography variant="body2" sx={{ color: '#374151', mt: 0.5 }}>
                  You&apos;re setting up a {modeLabel || 'Story'}
                  {templateLabel ? ` · ${templateLabel}` : ''}. You can fine-tune details later in the Outline and Writing phases.
                </Typography>
              );
            })()}
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center' }} />
        </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

        <Grid container spacing={4}>
          <Grid item xs={12}>
            <Grid container spacing={3}>
              <StoryParametersSection
                state={state}
                customValues={customValues}
                textFieldStyles={textFieldStyles}
                isRegeneratingPremise={isRegeneratingPremise}
                onRegeneratePremise={handleRegeneratePremise}
              />

              <StoryConfigurationSection
                state={state}
                customValues={customValues}
                textFieldStyles={textFieldStyles}
                normalizedAudienceAgeGroup={normalizedAudienceAgeGroup}
              />
            </Grid>
          </Grid>
        </Grid>

      {/* Generate Button */}
      <Box sx={{ mt: 4, display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
        <Button
          variant="contained"
          size="large"
            onClick={handleGenerateOutlineAndProceed}
            disabled={
              !state.persona ||
              !state.storySetting ||
              !state.characters ||
              !state.plotElements ||
              !state.premise ||
              isGeneratingOutline
            }
          sx={{ minWidth: 200 }}
        >
            {isGeneratingOutline ? (
              <>
                <CircularProgress size={20} sx={{ mr: 1 }} />
                Generating Outline...
              </>
            ) : (
              'Generate Outline'
            )}
        </Button>
      </Box>
      </Paper>
    </>
  );
};

export default StorySetup;

