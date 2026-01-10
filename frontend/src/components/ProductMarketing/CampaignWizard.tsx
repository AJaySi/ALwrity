import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Stack,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  CircularProgress,
  Divider,
  Grid,
  Tooltip,
  IconButton,
} from '@mui/material';
import {
  ArrowBack,
  ArrowForward,
  CheckCircle,
  Campaign,
  AutoAwesome,
  TrendingUp,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { ImageStudioLayout } from '../ImageStudio/ImageStudioLayout';
import { GlassyCard } from '../ImageStudio/ui/GlassyCard';
import { SectionHeader } from '../ImageStudio/ui/SectionHeader';
import { CampaignFlowIndicator } from './CampaignFlowIndicator';
import { PreflightValidationAlert } from './PreflightValidationAlert';
import { CampaignPreview } from './CampaignPreview';
import { useCampaignCreator } from '../../hooks/useCampaignCreator';
import { getSimpleTerm, getTooltipText, getTermExamples, getTermDescription } from '../../utils/terminology';
import { Info as InfoIcon } from '@mui/icons-material';

const MotionBox = motion(Box);

interface CampaignWizardProps {
  onComplete: (blueprint: any) => void;
  onCancel: () => void;
}

const steps = [
  'Campaign Goal & Success Metric',
  'Select Platforms',
  'Product Information',
  'Review & Create',
];

const channelOptions = [
  { value: 'instagram', label: 'Instagram', icon: '📷' },
  { value: 'linkedin', label: 'LinkedIn', icon: '💼' },
  { value: 'facebook', label: 'Facebook', icon: '👥' },
  { value: 'tiktok', label: 'TikTok', icon: '🎵' },
  { value: 'twitter', label: 'Twitter/X', icon: '🐦' },
  { value: 'pinterest', label: 'Pinterest', icon: '📌' },
  { value: 'youtube', label: 'YouTube', icon: '▶️' },
];

const goalOptions = [
  { value: 'product_launch', label: 'Product Launch', description: 'Launch a new product or feature' },
  { value: 'awareness', label: 'Brand Awareness', description: 'Increase brand visibility' },
  { value: 'conversion', label: 'Drive Conversions', description: 'Generate leads and sales' },
  { value: 'retention', label: 'Customer Retention', description: 'Engage existing customers' },
];

export const CampaignWizard: React.FC<CampaignWizardProps> = ({ onComplete, onCancel }) => {
  const {
    createCampaignBlueprint,
    generateAssetProposals,
    isCreatingBlueprint,
    isGeneratingProposals,
    error,
    getBrandDNA,
    brandDNA,
    validateCampaignPreflight,
    preflightResult,
    isValidatingPreflight,
    getPersonalizedDefaults,
    getRecommendations,
  } = useCampaignCreator();
  const [activeStep, setActiveStep] = useState(0);
  const [campaignName, setCampaignName] = useState('');
  const [goal, setGoal] = useState('');
  const [kpi, setKpi] = useState('');
  const [selectedChannels, setSelectedChannels] = useState<string[]>([]);
  const [productDescription, setProductDescription] = useState('');
  const [productName, setProductName] = useState('');
  const [marketingGoal, setMarketingGoal] = useState('');

  useEffect(() => {
    // Load brand DNA on mount
    if (!brandDNA) {
      getBrandDNA();
    }
    
    // Load personalized defaults for campaign creator
    getPersonalizedDefaults('campaign_creator')
      .then((defaults) => {
        if (defaults) {
          // Pre-select recommended channels
          if (defaults.channels && defaults.channels.length > 0) {
            setSelectedChannels(defaults.channels);
          }
          // Pre-select goal if available
          if (defaults.goal) {
            setGoal(defaults.goal);
          }
        }
      })
      .catch((err) => {
        console.warn('Failed to load personalized defaults:', err);
        // Continue without defaults
      });
  }, [brandDNA, getBrandDNA, getPersonalizedDefaults]);

  // Run pre-flight validation when on review step (step 3) and we have all required data
  useEffect(() => {
    if (activeStep === 3 && campaignName && goal && selectedChannels.length > 0) {
      validateCampaignPreflight({
        campaign_name: campaignName,
        goal: goal,
        kpi: kpi || undefined,
        channels: selectedChannels,
        product_context: {
          product_name: productName,
          product_description: productDescription,
          marketing_goal: marketingGoal,
        },
      }).catch(console.error);
    }
  }, [activeStep, campaignName, goal, selectedChannels, kpi, productName, productDescription, marketingGoal, validateCampaignPreflight]);

  const handleNext = () => {
    if (activeStep < steps.length - 1) {
      setActiveStep((prev) => prev + 1);
    }
  };

  const handleBack = () => {
    if (activeStep > 0) {
      setActiveStep((prev) => prev - 1);
    }
  };

  const handleChannelToggle = (channel: string) => {
    setSelectedChannels((prev) =>
      prev.includes(channel) ? prev.filter((c) => c !== channel) : [...prev, channel]
    );
  };

  const handleCreate = async () => {
    try {
      // Step 1: Create blueprint
      const blueprint = await createCampaignBlueprint({
        campaign_name: campaignName,
        goal: goal,
        kpi: kpi || undefined,
        channels: selectedChannels,
        product_context: {
          product_name: productName,
          product_description: productDescription,
          marketing_goal: marketingGoal,
        },
      });

      // Step 2: Generate proposals automatically
      try {
        await generateAssetProposals(blueprint.campaign_id, {
          product_name: productName,
          product_description: productDescription,
          marketing_goal: marketingGoal,
        });
      } catch (proposalErr) {
        // Log but don't fail - proposals can be generated later
        console.warn('Failed to generate proposals:', proposalErr);
      }

      // Step 3: Complete wizard
      onComplete(blueprint);
    } catch (err) {
      // Error handled in hook
    }
  };

  const canProceed = () => {
    switch (activeStep) {
      case 0:
        return campaignName.trim() !== '' && goal !== '';
      case 1:
        return selectedChannels.length > 0;
      case 2:
        return productDescription.trim() !== '' || productName.trim() !== '';
      case 3:
        return true;
      default:
        return false;
    }
  };

  return (
    <ImageStudioLayout
      headerProps={{
        title: 'Campaign Wizard',
        subtitle: 'Create a personalized marketing campaign with AI-generated assets',
      }}
    >
      <GlassyCard
        sx={{
          maxWidth: 900,
          mx: 'auto',
          p: { xs: 3, md: 4 },
        }}
      >
        <CampaignFlowIndicator currentStep="blueprint" />

        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => {}}>
            {error}
          </Alert>
        )}

        <Stepper activeStep={activeStep} orientation="vertical">
          {/* Step 1: Campaign Goal & Success Metric */}
          <Step>
            <StepLabel>
              <Typography variant="h6" fontWeight={700}>
                Campaign Goal & Success Metric
              </Typography>
            </StepLabel>
            <StepContent>
              <Stack spacing={3}>
                <TextField
                  label="Campaign Name"
                  value={campaignName}
                  onChange={(e) => setCampaignName(e.target.value)}
                  fullWidth
                  placeholder="e.g., Q1 Product Launch"
                  required
                />

                <FormControl fullWidth>
                  <InputLabel>Campaign Goal</InputLabel>
                  <Select value={goal} onChange={(e) => setGoal(e.target.value)} label="Campaign Goal">
                    {goalOptions.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        <Box>
                          <Typography variant="body1">{option.label}</Typography>
                          <Typography variant="caption" color="text.secondary">
                            {option.description}
                          </Typography>
                        </Box>
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                <TextField
                  label={getSimpleTerm('KPI')}
                  value={kpi}
                  onChange={(e) => setKpi(e.target.value)}
                  fullWidth
                  placeholder="e.g., 10,000 impressions, 500 sign-ups"
                  helperText={getTermDescription('KPI')}
                  InputProps={{
                    endAdornment: (
                      <Tooltip title={getTooltipText('KPI')}>
                        <IconButton size="small" edge="end">
                          <InfoIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    ),
                  }}
                />
                {getTermExamples('KPI') && (
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="caption" color="text.secondary" sx={{ mb: 0.5, display: 'block' }}>
                      Examples:
                    </Typography>
                    <Stack direction="row" spacing={1} flexWrap="wrap">
                      {getTermExamples('KPI')?.map((example, idx) => (
                        <Chip
                          key={idx}
                          label={example}
                          size="small"
                          onClick={() => setKpi(example)}
                          sx={{ cursor: 'pointer' }}
                        />
                      ))}
                    </Stack>
                  </Box>
                )}

                {brandDNA && (
                  <Alert severity="info">
                    <Typography variant="body2" fontWeight={700} gutterBottom>
                      Personalized for: {brandDNA.persona?.persona_name || 'Your Brand'}
                    </Typography>
                    <Typography variant="caption">
                      Tone: {brandDNA.writing_style?.tone} • Audience: {brandDNA.target_audience?.industry_focus}
                    </Typography>
                  </Alert>
                )}

                <Box display="flex" justifyContent="flex-end" gap={2}>
                  <Button onClick={onCancel}>Cancel</Button>
                  <Button variant="contained" onClick={handleNext} disabled={!canProceed()}>
                    Next
                  </Button>
                </Box>
              </Stack>
            </StepContent>
          </Step>

          {/* Step 2: Select Platforms */}
          <Step>
            <StepLabel>
              <Typography variant="h6" fontWeight={700}>
                Select Platforms
              </Typography>
            </StepLabel>
            <StepContent>
              <Stack spacing={3}>
                <Typography variant="body2" color="text.secondary">
                  Select the platforms where you want to publish your campaign. AI will generate platform-optimized content for each.
                </Typography>

                <Grid container spacing={2}>
                  {channelOptions.map((channel) => (
                    <Grid item xs={6} sm={4} key={channel.value}>
                      <Paper
                        onClick={() => handleChannelToggle(channel.value)}
                        sx={{
                          p: 2,
                          cursor: 'pointer',
                          border: selectedChannels.includes(channel.value)
                            ? '2px solid #7c3aed'
                            : '1px solid rgba(255,255,255,0.1)',
                          background: selectedChannels.includes(channel.value)
                            ? 'rgba(124, 58, 237, 0.1)'
                            : 'rgba(255,255,255,0.02)',
                          transition: 'all 0.2s',
                          '&:hover': {
                            background: 'rgba(124, 58, 237, 0.05)',
                          },
                        }}
                      >
                        <Stack spacing={1} alignItems="center">
                          <Typography variant="h4">{channel.icon}</Typography>
                          <Typography variant="body2" fontWeight={600}>
                            {channel.label}
                          </Typography>
                          {selectedChannels.includes(channel.value) && (
                            <CheckCircle sx={{ color: '#7c3aed', fontSize: 20 }} />
                          )}
                        </Stack>
                      </Paper>
                    </Grid>
                  ))}
                </Grid>

                {selectedChannels.length > 0 && (
                  <Alert severity="success">
                    {selectedChannels.length} platform(s) selected. AI will generate optimized content for each platform.
                  </Alert>
                )}

                <Box display="flex" justifyContent="space-between">
                  <Button onClick={handleBack}>Back</Button>
                  <Button variant="contained" onClick={handleNext} disabled={!canProceed()}>
                    Next
                  </Button>
                </Box>
              </Stack>
            </StepContent>
          </Step>

          {/* Step 3: Product Information */}
          <Step>
            <StepLabel>
              <Typography variant="h6" fontWeight={700}>
                Product Information
              </Typography>
            </StepLabel>
            <StepContent>
              <Stack spacing={3}>
                <Typography variant="body2" color="text.secondary">
                  Provide information about your product. This helps AI generate more accurate and relevant marketing content.
                </Typography>

                {/* Campaign Preview */}
                {campaignName && goal && selectedChannels.length > 0 && (
                  <CampaignPreview
                    campaignName={campaignName}
                    goal={goal}
                    kpi={kpi}
                    channels={selectedChannels}
                    productName={productName}
                    productDescription={productDescription}
                    goalOptions={goalOptions}
                    channelOptions={channelOptions}
                  />
                )}

                <TextField
                  label="Product Name"
                  value={productName}
                  onChange={(e) => setProductName(e.target.value)}
                  fullWidth
                  placeholder="e.g., AI Writing Assistant"
                />

                <TextField
                  label="Product Description"
                  value={productDescription}
                  onChange={(e) => setProductDescription(e.target.value)}
                  fullWidth
                  multiline
                  rows={4}
                  placeholder="Describe your product, its key features, and benefits..."
                  required
                />

                <TextField
                  label="Marketing Goal for This Campaign"
                  value={marketingGoal}
                  onChange={(e) => setMarketingGoal(e.target.value)}
                  fullWidth
                  placeholder="e.g., Drive sign-ups, increase awareness, showcase features"
                  helperText="What specific outcome do you want from this campaign?"
                />

                <Box display="flex" justifyContent="space-between">
                  <Button onClick={handleBack}>Back</Button>
                  <Button variant="contained" onClick={handleNext} disabled={!canProceed()}>
                    Next
                  </Button>
                </Box>
              </Stack>
            </StepContent>
          </Step>

          {/* Step 4: Review & Create */}
          <Step>
            <StepLabel>
              <Typography variant="h6" fontWeight={700}>
                Review & Create
              </Typography>
            </StepLabel>
            <StepContent>
              <Stack spacing={3}>
                <GlassyCard sx={{ p: 3 }}>
                  <Stack spacing={2}>
                    <Box>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Campaign Name
                      </Typography>
                      <Typography variant="h6">{campaignName}</Typography>
                    </Box>

                    <Divider sx={{ borderColor: 'rgba(255,255,255,0.08)' }} />

                    <Box>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Goal
                      </Typography>
                      <Typography variant="body1">
                        {goalOptions.find((g) => g.value === goal)?.label || goal}
                      </Typography>
                    </Box>

                    {kpi && (
                      <>
                        <Divider sx={{ borderColor: 'rgba(255,255,255,0.08)' }} />
                        <Box>
                          <Typography variant="body2" color="text.secondary" gutterBottom>
                            {getSimpleTerm('KPI')}
                          </Typography>
                          <Typography variant="body1">{kpi}</Typography>
                        </Box>
                      </>
                    )}

                    <Divider sx={{ borderColor: 'rgba(255,255,255,0.08)' }} />

                    <Box>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Channels ({selectedChannels.length})
                      </Typography>
                      <Box display="flex" gap={1} flexWrap="wrap">
                        {selectedChannels.map((channel) => {
                          const channelInfo = channelOptions.find((c) => c.value === channel);
                          return (
                            <Chip
                              key={channel}
                              label={`${channelInfo?.icon} ${channelInfo?.label}`}
                              size="small"
                            />
                          );
                        })}
                      </Box>
                    </Box>

                    {productDescription && (
                      <>
                        <Divider sx={{ borderColor: 'rgba(255,255,255,0.08)' }} />
                        <Box>
                          <Typography variant="body2" color="text.secondary" gutterBottom>
                            Product Description
                          </Typography>
                          <Typography variant="body2">{productDescription}</Typography>
                        </Box>
                      </>
                    )}
                  </Stack>
                </GlassyCard>

                {/* Pre-flight Validation Alert */}
                <PreflightValidationAlert
                  validationResult={preflightResult}
                  isLoading={isValidatingPreflight}
                />

                <Alert severity="info" icon={<AutoAwesome />}>
                  <Typography variant="body2" fontWeight={700} gutterBottom>
                    Next Steps
                  </Typography>
                  <Typography variant="body2">
                    After creating your campaign, AI will automatically generate personalized content ideas. You'll then review and approve them before content is generated.
                  </Typography>
                </Alert>

                <Box display="flex" justifyContent="space-between">
                  <Button onClick={handleBack}>Back</Button>
                  <Button
                    variant="contained"
                    onClick={handleCreate}
                    disabled={
                      Boolean(
                        isCreatingBlueprint ||
                        isGeneratingProposals ||
                        isValidatingPreflight ||
                        (preflightResult ? !preflightResult.can_proceed : false)
                      )
                    }
                    startIcon={
                      isCreatingBlueprint || isGeneratingProposals ? (
                        <CircularProgress size={16} />
                      ) : (
                        <AutoAwesome />
                      )
                    }
                  >
                    {isCreatingBlueprint
                      ? 'Creating Campaign...'
                      : isGeneratingProposals
                      ? 'Generating Proposals...'
                      : 'Create Campaign & Generate Proposals'}
                  </Button>
                </Box>
              </Stack>
            </StepContent>
          </Step>
        </Stepper>
      </GlassyCard>
    </ImageStudioLayout>
  );
};

