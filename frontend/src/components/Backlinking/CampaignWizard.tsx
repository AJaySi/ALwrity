import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
  Chip,
  IconButton,
  Stack,
  Alert,
  Stepper,
  Step,
  StepLabel,
  Fade,
  CircularProgress,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Campaign as CampaignIcon,
} from '@mui/icons-material';
import { BacklinkingStyles } from './styles/backlinkingStyles';
import {
  GradientButton,
  BacklinkingTextField,
  KeywordChip,
} from './styles/components';

interface CampaignWizardProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: any) => void;
}

const wizardSteps = ['Campaign Details', 'Target Keywords', 'Guest Post Proposal'];

export const CampaignWizard: React.FC<CampaignWizardProps> = ({
  open,
  onClose,
  onSubmit,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const [activeStep, setActiveStep] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    keywords: [] as string[],
    currentKeyword: '',
    user_proposal: {
      user_name: '',
      user_email: '',
      topic: '',
      description: '',
    },
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  const handleNext = () => {
    if (validateStep(activeStep)) {
      setActiveStep(activeStep + 1);
    }
  };

  const handleBack = () => {
    setActiveStep(activeStep - 1);
  };

  const handleSubmit = async () => {
    if (validateStep(activeStep)) {
      setIsSubmitting(true);
      try {
        await onSubmit(formData);
        handleClose();
      } catch (error) {
        setIsSubmitting(false);
        // Error handling is done in the parent component
      }
    }
  };

  const handleClose = () => {
    setActiveStep(0);
    setFormData({
      name: '',
      keywords: [],
      currentKeyword: '',
      user_proposal: {
        user_name: '',
        user_email: '',
        topic: '',
        description: '',
      },
    });
    setErrors({});
    setTouched({});
    setIsSubmitting(false);
    onClose();
  };

  const handleFieldTouch = (field: string) => {
    setTouched(prev => ({ ...prev, [field]: true }));
  };

  const validateStep = (currentStep: number): boolean => {
    const newErrors: Record<string, string> = {};

    switch (currentStep) {
      case 0: // Campaign Details
        if (!formData.name.trim()) {
          newErrors.name = 'Campaign name is required';
        } else if (formData.name.trim().length < 3) {
          newErrors.name = 'Campaign name must be at least 3 characters';
        } else if (formData.name.trim().length > 100) {
          newErrors.name = 'Campaign name cannot exceed 100 characters';
        }
        break;
      case 1: // Target Keywords
        if (formData.keywords.length === 0) {
          newErrors.keywords = 'At least one keyword is required';
        } else if (formData.keywords.length > 10) {
          newErrors.keywords = 'Cannot have more than 10 keywords';
        }
        break;
      case 2: // Guest Post Proposal
        if (!formData.user_proposal.user_name.trim()) {
          newErrors.user_name = 'Your name is required';
        }
        if (!formData.user_proposal.user_email.trim()) {
          newErrors.user_email = 'Your email is required';
        } else if (!/\S+@\S+\.\S+/.test(formData.user_proposal.user_email)) {
          newErrors.user_email = 'Please enter a valid email address';
        }
        if (!formData.user_proposal.topic.trim()) {
          newErrors.topic = 'Guest post topic is required';
        } else if (formData.user_proposal.topic.trim().length > 200) {
          newErrors.topic = 'Topic cannot exceed 200 characters';
        }
        if (formData.user_proposal.description && formData.user_proposal.description.length > 1000) {
          newErrors.description = 'Description cannot exceed 1000 characters';
        }
        break;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const addKeyword = () => {
    const keyword = formData.currentKeyword.trim();
    if (keyword && !formData.keywords.includes(keyword)) {
      setFormData(prev => ({
        ...prev,
        keywords: [...prev.keywords, keyword],
        currentKeyword: '',
      }));
    }
  };

  const removeKeyword = (keywordToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      keywords: prev.keywords.filter(k => k !== keywordToRemove),
    }));
  };

  const updateFormData = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const updateUserProposal = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      user_proposal: {
        ...prev.user_proposal,
        [field]: value,
      },
    }));
  };

  const renderStep1 = () => (
    <Fade in={true} timeout={300}>
      <Box sx={{ minHeight: 300 }}>
        <Typography variant="h6" sx={{ mb: 2 }} id="step-1-heading">
          Campaign Details
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Give your backlinking campaign a descriptive name and define its purpose.
        </Typography>

        <BacklinkingTextField
          fullWidth
          label="Campaign Name"
          value={formData.name}
          onChange={(e) => {
            updateFormData('name', e.target.value);
            handleFieldTouch('name');
          }}
          onBlur={() => handleFieldTouch('name')}
          error={touched.name && !!errors.name}
          helperText={touched.name ? errors.name : 'Choose a descriptive name for your campaign'}
          placeholder="e.g., Technology Guest Posts Q1 2024"
          sx={{ mb: 2 }}
          aria-describedby="step-1-heading campaign-name-helper"
          inputProps={{
            'aria-label': 'Campaign name',
            maxLength: 100,
          }}
        />

        <Alert severity="info" sx={{ mt: 2 }}>
          <Typography variant="body2">
            Your campaign will automatically search for guest post opportunities,
            generate personalized emails, and track responses. Choose a name that
            reflects your content focus.
          </Typography>
        </Alert>
      </Box>
    </Fade>
  );

  const renderStep2 = () => (
    <Box sx={{ minHeight: 300 }}>
      <Typography variant="h6" sx={{ mb: 2 }}>
        Target Keywords
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Enter keywords related to your niche. The system will find websites that accept guest posts in these areas.
      </Typography>

      <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
        <BacklinkingTextField
          fullWidth
          label="Add Keyword"
          value={formData.currentKeyword}
          onChange={(e) => updateFormData('currentKeyword', e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && addKeyword()}
          placeholder="e.g., AI tools, content marketing"
        />
        <Button
          variant="contained"
          onClick={addKeyword}
          disabled={!formData.currentKeyword.trim()}
          sx={{ minWidth: 100 }}
        >
          <AddIcon />
        </Button>
      </Box>

      {errors.keywords && (
        <Typography variant="body2" color="error" sx={{ mb: 2 }}>
          {errors.keywords}
        </Typography>
      )}

      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle2" sx={{ mb: 1 }}>
          Selected Keywords:
        </Typography>
        <Stack direction="row" spacing={1} flexWrap="wrap">
          {formData.keywords.map((keyword) => (
            <KeywordChip
              key={keyword}
              label={keyword}
              onDelete={() => removeKeyword(keyword)}
            />
          ))}
        </Stack>
      </Box>

      <Alert severity="info" sx={{ mt: 2 }}>
        <Typography variant="body2">
          <strong>Tip:</strong> Use specific, long-tail keywords for better results.
          Example: "AI content writing tools" instead of just "AI".
        </Typography>
      </Alert>
    </Box>
  );

  const renderStep3 = () => (
    <Box sx={{ minHeight: 300 }}>
      <Typography variant="h6" sx={{ mb: 2 }}>
        Your Guest Post Proposal
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Provide details about the guest post you'd like to contribute. This information will be used to generate personalized outreach emails.
      </Typography>

      <BacklinkingTextField
        fullWidth
        label="Your Name"
        value={formData.user_proposal.user_name}
        onChange={(e) => updateUserProposal('user_name', e.target.value)}
        error={!!errors.user_name}
        helperText={errors.user_name}
        sx={BacklinkingStyles.formField}
      />

      <BacklinkingTextField
        fullWidth
        label="Your Email"
        type="email"
        value={formData.user_proposal.user_email}
        onChange={(e) => updateUserProposal('user_email', e.target.value)}
        error={!!errors.user_email}
        helperText={errors.user_email}
        sx={BacklinkingStyles.formField}
      />

      <BacklinkingTextField
        fullWidth
        label="Guest Post Topic"
        value={formData.user_proposal.topic}
        onChange={(e) => updateUserProposal('topic', e.target.value)}
        error={!!errors.topic}
        helperText={errors.topic}
        placeholder="e.g., The Future of AI in Content Creation"
        sx={BacklinkingStyles.formField}
      />

      <BacklinkingTextField
        fullWidth
        multiline
        rows={3}
        label="Brief Description (Optional)"
        value={formData.user_proposal.description}
        onChange={(e) => updateUserProposal('description', e.target.value)}
        placeholder="Briefly describe what your guest post will cover..."
        sx={BacklinkingStyles.formField}
      />

      <Alert severity="info" sx={{ mt: 2 }}>
        <Typography variant="body2">
          The AI will use this information to craft personalized emails that highlight
          your expertise and show genuine interest in each target website.
        </Typography>
      </Alert>
    </Box>
  );

  const getStepContent = () => {
    switch (activeStep) {
      case 0:
        return renderStep1();
      case 1:
        return renderStep2();
      case 2:
        return renderStep3();
      default:
        return null;
    }
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      fullScreen={isMobile}
      aria-labelledby="campaign-wizard-title"
      aria-describedby="campaign-wizard-description"
      sx={BacklinkingStyles.wizardDialog}
    >
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <CampaignIcon />
        Create Backlinking Campaign
      </DialogTitle>

      <DialogContent sx={{ pb: 1 }}>
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ mb: 3 }}
          id="campaign-wizard-description"
        >
          Set up an automated campaign to discover guest post opportunities and send personalized outreach emails.
        </Typography>

        <Stepper activeStep={activeStep} sx={BacklinkingStyles.wizardStepper}>
          {wizardSteps.map((label, index) => (
            <Step key={label}>
              <StepLabel
                optional={
                  index === 2 ? (
                    <Typography variant="caption">Final step</Typography>
                  ) : undefined
                }
              >
                {label}
              </StepLabel>
            </Step>
          ))}
        </Stepper>

        <Box sx={{ minHeight: 300 }}>
          {getStepContent()}
        </Box>
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 2, flexWrap: 'wrap', gap: 1 }}>
        <Button
          onClick={handleClose}
          color="inherit"
          disabled={isSubmitting}
          aria-label="Cancel campaign creation"
        >
          Cancel
        </Button>

        {activeStep > 0 && (
          <Button
            onClick={handleBack}
            variant="outlined"
            disabled={isSubmitting}
            aria-label={`Go back to ${wizardSteps[activeStep - 1]}`}
          >
            Back
          </Button>
        )}

        <Box sx={{ flex: '1 1 auto' }} />

        {activeStep < wizardSteps.length - 1 ? (
          <Button
            onClick={handleNext}
            variant="contained"
            disabled={!validateStep(activeStep)}
            aria-label={`Continue to ${wizardSteps[activeStep + 1]}`}
          >
            Next
          </Button>
        ) : (
          <GradientButton
            onClick={handleSubmit}
            disabled={!validateStep(activeStep) || isSubmitting}
            startIcon={isSubmitting ? <CircularProgress size={16} /> : null}
            aria-label="Create campaign and start discovery"
          >
            {isSubmitting ? 'Creating...' : 'Create Campaign'}
          </GradientButton>
        )}
      </DialogActions>
    </Dialog>
  );
};