import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Button, 
  Typography, 
  Alert, 
  Container,
  Fade,
  Zoom,
  CircularProgress
} from '@mui/material';
import { 
  Rocket,
  Star,
  CheckCircle
} from '@mui/icons-material';
import OnboardingButton from '../common/OnboardingButton';
import { getApiKeys, completeOnboarding, getOnboardingSummary, getWebsiteAnalysisData, getResearchPreferencesData, setCurrentStep } from '../../../api/onboarding';
import { SetupSummary, CapabilitiesOverview } from './components';
import { FinalStepProps, OnboardingData, Capability } from './types';

const FinalStep: React.FC<FinalStepProps> = ({ onContinue, updateHeaderContent }) => {
  const [loading, setLoading] = useState(false);
  const [dataLoading, setDataLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [onboardingData, setOnboardingData] = useState<OnboardingData>({
    apiKeys: {}
  });
  const [expandedSection, setExpandedSection] = useState<string | null>('summary');

  useEffect(() => {
    updateHeaderContent({
      title: 'Review & Launch Alwrity 🚀',
      description: 'Review your configuration and confirm all settings before launching your AI-powered content creation workspace.'
    });
    loadOnboardingData();
  }, [updateHeaderContent]);

  const loadOnboardingData = async () => {
    setDataLoading(true);
    try {
      // Load comprehensive onboarding summary
      const summary = await getOnboardingSummary();
      
      // Load individual data sources for detailed information
      const websiteAnalysis = await getWebsiteAnalysisData();
      const researchPreferences = await getResearchPreferencesData();
      // Frontend fallbacks to Step 2 cached data (ensures non-breaking UI)
      const cachedUrl = typeof window !== 'undefined' ? localStorage.getItem('website_url') : null;
      const cachedAnalysisRaw = typeof window !== 'undefined' ? localStorage.getItem('website_analysis_data') : null;
      const cachedAnalysis = cachedAnalysisRaw ? safeParseJSON(cachedAnalysisRaw) : undefined;

      setOnboardingData({
        apiKeys: summary.api_keys || {},
        websiteUrl: websiteAnalysis?.website_url || summary.website_url || cachedUrl || undefined,
        researchPreferences: researchPreferences || summary.research_preferences,
        personalizationSettings: summary.personalization_settings,
        integrations: summary.integrations || {},
        styleAnalysis: websiteAnalysis?.style_analysis || summary.style_analysis || cachedAnalysis || undefined
      });
    } catch (error) {
      console.error('Error loading onboarding data:', error);
      // Fallback to just API keys if other endpoints fail
      try {
        const apiKeys = await getApiKeys();
        setOnboardingData({
          apiKeys,
          websiteUrl: undefined,
          researchPreferences: undefined,
          personalizationSettings: undefined,
          integrations: undefined,
          styleAnalysis: undefined
        });
      } catch (fallbackError) {
        console.error('Error loading API keys as fallback:', fallbackError);
      }
    } finally {
      setDataLoading(false);
    }
  };

  // Safe JSON parser for cached data
  const safeParseJSON = (raw: string | null): any | undefined => {
    if (!raw) return undefined;
    try { return JSON.parse(raw); } catch { return undefined; }
  };

  const handleLaunch = async () => {
    setLoading(true);
    setError(null);
    try {
      console.log('FinalStep: Starting onboarding completion...');
      
      // First, complete step 6 (Final Step) to mark it as completed
      console.log('FinalStep: Completing step 6...');
      await setCurrentStep(6);
      console.log('FinalStep: Step 6 completed successfully');
      
      // Then complete the entire onboarding process
      console.log('FinalStep: Completing onboarding...');
      await completeOnboarding();
      console.log('FinalStep: Onboarding completed successfully');
      
      // Navigate directly to dashboard without calling onContinue
      // This bypasses the wizard flow and goes straight to the dashboard
      console.log('FinalStep: Navigating to dashboard...');
      window.location.href = '/dashboard';
    } catch (e: any) {
      console.error('FinalStep: Error completing onboarding:', e);
      
      // Provide more specific error messages
      let errorMessage = 'Failed to complete onboarding. Please try again.';
      
      if (e.response?.data?.detail) {
        errorMessage = e.response.data.detail;
      } else if (e.message) {
        errorMessage = e.message;
      }
      
      setError(errorMessage);
    }
    setLoading(false);
  };

  const capabilities: Capability[] = [
    {
      id: 'ai-content',
      title: 'AI Content Generation',
      description: 'Generate high-quality, personalized content using advanced AI models',
      icon: <CheckCircle />,
      unlocked: Object.keys(onboardingData.apiKeys).length > 0,
      required: ['API Keys']
    },
    {
      id: 'style-analysis',
      title: 'Style Analysis',
      description: 'Analyze and match your brand\'s writing style and tone',
      icon: <CheckCircle />,
      unlocked: !!onboardingData.websiteUrl,
      required: ['Website URL']
    },
    {
      id: 'research-tools',
      title: 'AI Research Tools',
      description: 'Automated research and fact-checking capabilities',
      icon: <CheckCircle />,
      unlocked: !!onboardingData.researchPreferences,
      required: ['Research Configuration']
    },
    {
      id: 'personalization',
      title: 'Content Personalization',
      description: 'Tailored content based on your brand voice and preferences',
      icon: <CheckCircle />,
      unlocked: !!onboardingData.personalizationSettings,
      required: ['Personalization Settings']
    },
    {
      id: 'integrations',
      title: 'Third-party Integrations',
      description: 'Connect with external tools and platforms',
      icon: <CheckCircle />,
      unlocked: !!onboardingData.integrations,
      required: ['Integration Setup']
    }
  ];

  const getMissingRequirements = () => {
    const missing = [];
    if (Object.keys(onboardingData.apiKeys).length === 0) {
      missing.push('At least one AI provider API key');
    }
    if (!onboardingData.websiteUrl) {
      missing.push('Website URL for style analysis');
    }
    return missing;
  };

  const missingRequirements = getMissingRequirements();

  return (
    <Fade in={true} timeout={500}>
      <Container maxWidth="lg" sx={{ py: 2 }}>
        {/* Loading State */}
        {dataLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 8 }}>
            <Box sx={{ textAlign: 'center' }}>
              <CircularProgress size={60} sx={{ mb: 2 }} />
              <Typography variant="h6" sx={{ mb: 1 }}>
                Loading your configuration...
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Retrieving your onboarding data and settings
              </Typography>
            </Box>
          </Box>
        )}

        {/* Content - Only show when data is loaded */}
        {!dataLoading && (
          <React.Fragment>
            {/* Setup Summary */}
            <SetupSummary 
              onboardingData={onboardingData}
              capabilities={capabilities}
              expandedSection={expandedSection}
              setExpandedSection={setExpandedSection}
            />

            {/* Capabilities Overview */}
            <CapabilitiesOverview capabilities={capabilities} />

            {/* Missing Requirements Warning */}
            {missingRequirements.length > 0 && (
              <Zoom in={true} timeout={1400}>
                <Alert 
                  severity="warning" 
                  sx={{ mb: 4, borderRadius: 2 }}
                  action={
                    <Button color="inherit" size="small">
                      Configure Now
                    </Button>
                  }
                >
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                    Missing Requirements
                  </Typography>
                  <Typography variant="body2">
                    The following items are recommended for optimal experience: {missingRequirements.join(', ')}
                  </Typography>
                </Alert>
              </Zoom>
            )}

            {/* Alerts */}
            <Box sx={{ mt: 3 }}>
              {error && (
                <Fade in={true}>
                  <Alert 
                    severity="error" 
                    sx={{ mb: 2, borderRadius: 2 }}
                    action={
                      <Button 
                        color="inherit" 
                        size="small"
                        onClick={() => setError(null)}
                      >
                        Dismiss
                      </Button>
                    }
                  >
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                      Setup Incomplete
                    </Typography>
                    <Typography variant="body2">
                      {error}
                    </Typography>
                  </Alert>
                </Fade>
              )}
            </Box>

            {/* Action Button */}
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
              <OnboardingButton
                variant="primary"
                onClick={handleLaunch}
                loading={loading}
                size="large"
                icon={<Rocket />}
                disabled={Object.keys(onboardingData.apiKeys).length === 0}
              >
                Launch Alwrity & Complete Setup
              </OnboardingButton>
            </Box>

            {/* Help Text */}
            <Box sx={{ mt: 3, textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                This will complete your onboarding and launch Alwrity with your configured settings.
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
                <Star sx={{ fontSize: 16 }} />
                Ready to create amazing content with AI-powered assistance
              </Typography>
            </Box>
          </React.Fragment>
        )}
      </Container>
    </Fade>
  );
};

export default FinalStep;
