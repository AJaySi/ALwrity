import React, { useState, useEffect } from 'react';
import { Paper, Typography, Box, Button, Alert, Grid, CircularProgress } from '@mui/material';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import { useStoryWriterState } from '../../../../hooks/useStoryWriterState';
import { storyWriterApi, StoryScene } from '../../../../services/storyWriterApi';
import { triggerSubscriptionError } from '../../../../api/client';
import { StoryParametersSection } from './StoryParametersSection';
import { StoryConfigurationSection } from './StoryConfigurationSection';
import { FeatureCheckboxesSection } from './FeatureCheckboxesSection';
import { GenerationSettingsSection } from './GenerationSettingsSection';
import { AIStorySetupModal } from './AIStorySetupModal';
import { textFieldStyles, paperStyles } from './styles';
import { AUDIENCE_AGE_GROUPS } from './constants';
import { StorySetupProps, CustomValuesState, CustomValuesSetters } from './types';

const StorySetup: React.FC<StorySetupProps> = ({ state, onNext }) => {
  const [isRegeneratingPremise, setIsRegeneratingPremise] = useState(false);
  const [isGeneratingOutline, setIsGeneratingOutline] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

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
            gap: 3,
            mb: 4,
          }}
        >
          <Box>
            <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, color: '#1A1611' }}>
        Story Setup
      </Typography>
            <Typography variant="body2" sx={{ color: '#5D4037' }}>
              Configure your story parameters and premise. Fill in the required fields and click "Generate Outline" to
              continue.
      </Typography>
          </Box>
          <FeatureCheckboxesSection state={state} layout="inline" />
        </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Box sx={{ mb: 4 }}>
          <Button
            variant="contained"
            size="large"
            startIcon={<AutoAwesomeIcon />}
            onClick={() => setIsModalOpen(true)}
            sx={{
              mb: 1,
              px: 4,
              py: 1.5,
              borderRadius: '999px',
              textTransform: 'none',
              fontWeight: 600,
              background: 'linear-gradient(135deg, #7F5AF0 0%, #2CB67D 100%)',
              boxShadow: '0 12px 24px rgba(127, 90, 240, 0.3)',
              '&:hover': {
                background: 'linear-gradient(135deg, #6c4cd4 0%, #24a26f 100%)',
                boxShadow: '0 14px 30px rgba(127, 90, 240, 0.35)',
              },
            }}
          >
            Generate Story Setup with Alwrity AI
        </Button>
          <Typography variant="caption" sx={{ color: '#5D4037' }}>
            Let Alwrity AI craft a cohesive persona, setting, and premise instantly.
          </Typography>
      </Box>

        <Grid container spacing={4}>
          <Grid item xs={12} md={8}>
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
          <Grid item xs={12} md={4}>
            <Box
              sx={{
                position: { md: 'sticky' },
                top: { md: 16 },
              }}
            >
              <GenerationSettingsSection state={state} customValues={customValues} textFieldStyles={textFieldStyles} />
            </Box>
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

      <AIStorySetupModal
        open={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        state={state}
        customValuesSetters={customValuesSetters}
      />
    </>
  );
};

export default StorySetup;

