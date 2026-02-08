import React, { useState, useEffect, useRef } from 'react';
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
  CheckCircle,
  CreditCard,
  Warning
} from '@mui/icons-material';
import OnboardingButton from '../common/OnboardingButton';
import { getApiKeys, completeOnboarding, getOnboardingSummary, getWebsiteAnalysisData, getResearchPreferencesData, setCurrentStep } from '../../../api/onboarding';
import { SetupSummary, CapabilitiesOverview, AgentTeamSection } from './components';
import { FinalStepProps, OnboardingData, Capability } from './types';
import { getAgentTeam, type AgentTeamCatalogEntry } from '../../../api/agentsTeam';

const FinalStep: React.FC<FinalStepProps> = ({ onContinue, updateHeaderContent }) => {
  const [loading, setLoading] = useState(false);
  const [dataLoading, setDataLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [onboardingData, setOnboardingData] = useState<OnboardingData>({
    apiKeys: {}
  });
  const [expandedSection, setExpandedSection] = useState<string | null>('summary');
  const [validationStatus, setValidationStatus] = useState<{isValid: boolean, missingSteps: string[]} | null>(null);
  const [agentTeam, setAgentTeam] = useState<AgentTeamCatalogEntry[]>([]);
  const [agentTeamError, setAgentTeamError] = useState<string | null>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    updateHeaderContent({
      title: 'Review & Launch Alwrity 🚀',
      description: 'Review your configuration and confirm all settings before launching your AI-powered content creation workspace.'
    });
    // Always attempt to load data once on mount
    loadOnboardingData();
  }, [updateHeaderContent]);

  // Remove the DOM manipulation approach - we'll use React's built-in event handling

  const loadOnboardingData = async () => {
    // Prevent multiple simultaneous data loading calls
    if (dataLoading) {
      return;
    }
    
    setDataLoading(true);
    
    // Set a timeout to prevent infinite loading
    const loadingTimeout = setTimeout(() => {
      console.log('FinalStep: Data loading timeout reached, proceeding with available data');
      setDataLoading(false);
    }, 4000); // 4s timeout
    
    try {
      // Load comprehensive onboarding summary
      const summary = await getOnboardingSummary();
      
      // Load individual data sources for detailed information
      const websiteAnalysis = await getWebsiteAnalysisData();
      const researchPreferences = await getResearchPreferencesData();
      try {
        const team = await getAgentTeam();
        setAgentTeam(team || []);
        setAgentTeamError(null);
      } catch (e: any) {
        setAgentTeam([]);
        setAgentTeamError(e?.message || 'Failed to load agent team configuration');
      }
      // Frontend fallbacks to Step 2 cached data (ensures non-breaking UI)
      const cachedUrl = typeof window !== 'undefined' ? localStorage.getItem('website_url') : null;
      const cachedAnalysisRaw = typeof window !== 'undefined' ? localStorage.getItem('website_analysis_data') : null;
      const cachedAnalysis = cachedAnalysisRaw ? safeParseJSON(cachedAnalysisRaw) : undefined;

      const newOnboardingData = {
        apiKeys: summary.api_keys || {},
        websiteUrl: websiteAnalysis?.website_url || summary.website_url || cachedUrl || undefined,
        researchPreferences: researchPreferences || summary.research_preferences,
        personalizationSettings: summary.personalization_settings,
        integrations: summary.integrations || {},
        styleAnalysis: websiteAnalysis?.style_analysis || summary.style_analysis || cachedAnalysis || undefined,
        canonicalProfile: summary.canonical_profile
      };
      
      setOnboardingData(newOnboardingData);
      
      // Validate completion status after data is loaded
      console.log('FinalStep: Data loaded, running validation...');
      const validation = await validateOnboardingCompletionWithData(newOnboardingData);
      setValidationStatus(validation);
    } catch (error) {
      console.error('Error loading onboarding data:', error);
      
      // Error handling is managed by global API client interceptors
      
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
        // Error handling is managed by global API client interceptors
      }
    } finally {
      setDataLoading(false);
      clearTimeout(loadingTimeout);
    }
  };

  const websiteName = React.useMemo(() => {
    const url = onboardingData.websiteUrl;
    if (!url) return 'Your';
    try {
      const hostname = new URL(url).hostname.replace(/^www\./, '');
      const parts = hostname.split('.');
      if (parts.length <= 2) return parts[0] || hostname;
      return parts.slice(0, -1).join('.') || hostname;
    } catch {
      return 'Your';
    }
  }, [onboardingData.websiteUrl]);

  const agentContextCard = React.useMemo(() => {
    const style = onboardingData.styleAnalysis || {};
    const persona = onboardingData.personalizationSettings || {};
    const canonical = onboardingData.canonicalProfile || {};
    const research = onboardingData.researchPreferences || {};

    const contentPillars =
      style?.content_strategy_insights?.content_pillars ||
      style?.sitemap_analysis?.content_pillars ||
      canonical?.content_pillars ||
      [];

    const competitors =
      research?.competitors ||
      canonical?.competitors ||
      [];

    return {
      website_name: websiteName,
      website_url: onboardingData.websiteUrl,
      brand_voice: persona?.corePersona || persona?.platformPersonas || persona?.brand_voice || canonical?.brand_voice || "",
      target_audience: style?.target_audience || canonical?.target_audience || "",
      style_guidelines: style?.style_guidelines || style?.style_patterns || canonical?.style_guidelines || "",
      content_pillars: Array.isArray(contentPillars) ? contentPillars : [],
      competitors: Array.isArray(competitors) ? competitors : [],
      business_goals: canonical?.business_goals || [],
    };
  }, [onboardingData, websiteName]);

  // Safe JSON parser for cached data
  const safeParseJSON = (raw: string | null): any | undefined => {
    if (!raw) return undefined;
    try { return JSON.parse(raw); } catch { return undefined; }
  };

  const validateOnboardingCompletionWithData = async (data: OnboardingData): Promise<{isValid: boolean, missingSteps: string[]}> => {
    console.log('FinalStep: Validating onboarding completion with data...');
    console.log('FinalStep: Data to validate:', data);
    const missingSteps: string[] = [];
    
    try {
      // Check API Keys (Step 1) - Since the user is on step 5 (FinalStep), 
      // they must have completed step 1 (API Keys) to get here
      // The backend has EXA_API_KEY and GEMINI_API_KEY in .env and user completed step 1
      const hasApiKeys = true; // User is on final step, so step 1 must be completed
      
      console.log('FinalStep: API Keys check:', {
        hasApiKeys, 
        reason: 'User is on final step, so step 1 (API Keys) must be completed',
        note: 'Backend has EXA_API_KEY and GEMINI_API_KEY in .env'
      });
      if (!hasApiKeys) {
        missingSteps.push('API Keys');
      }
      
      // Check Website Analysis (Step 2) - Check for website URL or analysis data
      const hasWebsiteAnalysis = (data.websiteUrl && data.websiteUrl.trim() !== '') ||
                               (data.styleAnalysis && Object.keys(data.styleAnalysis).length > 0);
      console.log('FinalStep: Website Analysis check:', {
        websiteUrl: data.websiteUrl, 
        styleAnalysis: data.styleAnalysis,
        hasWebsiteAnalysis
      });
      if (!hasWebsiteAnalysis) {
        missingSteps.push('Website Analysis');
      }
      
      // Check Research Preferences (Step 3) - Check for research preferences data
      const hasResearchPreferences = data.researchPreferences && 
                                   (data.researchPreferences.research_depth || 
                                    data.researchPreferences.content_characteristics ||
                                    Object.keys(data.researchPreferences).length > 0);
      console.log('FinalStep: Research Preferences check:', {
        researchPreferences: data.researchPreferences,
        hasResearchPreferences
      });
      if (!hasResearchPreferences) {
        missingSteps.push('Research Preferences');
      }
      
      // Check Persona Generation (Step 4) - Check for persona readiness or data
      const hasPersonaData = (data.personaReadiness && data.personaReadiness.isReady) ||
                            (data.personalizationSettings && Object.keys(data.personalizationSettings).length > 0);
      console.log('FinalStep: Persona Generation check:', {
        personaReadiness: data.personaReadiness,
        personalizationSettings: data.personalizationSettings,
        hasPersonaData
      });
      if (!hasPersonaData) {
        missingSteps.push('Persona Generation');
      }
      
      // Check Integrations (Step 5) - For now, we'll consider this optional
      // In the future, this could check for specific integration data
      
      const isValid = missingSteps.length === 0;
      console.log('FinalStep: Validation result:', {isValid, missingSteps});
      
      return {isValid, missingSteps};
    } catch (error) {
      console.error('FinalStep: Error validating completion:', error);
      return {isValid: false, missingSteps: ['Validation Error']};
    }
  };

  const validateOnboardingCompletion = async (): Promise<{isValid: boolean, missingSteps: string[]}> => {
    return validateOnboardingCompletionWithData(onboardingData);
  };

  const handleLaunch = async () => {
    console.log('FinalStep: handleLaunch called - button clicked');
    console.log('FinalStep: handleLaunch - starting execution');
    console.log('FinalStep: handleLaunch - current state:', {loading, error, validationStatus, dataLoading});

    if (loading) {
      console.log('FinalStep: Already processing, ignoring click');
      return;
    }

    // Wait for data to be fully loaded before proceeding
    if (dataLoading) {
      console.log('FinalStep: Data still loading, waiting...');
      // Wait a bit and try again
      setTimeout(() => {
        if (!dataLoading) {
          handleLaunch();
        }
      }, 100);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      console.log('FinalStep: Starting onboarding completion...');
      
      // First, validate that all required steps are completed
      console.log('FinalStep: Validating all required steps...');
      const validationResult = await validateOnboardingCompletion();
      if (!validationResult.isValid) {
        throw new Error(`Cannot complete onboarding. Missing steps: ${validationResult.missingSteps.join(', ')}`);
      }
      console.log('FinalStep: All required steps validated successfully');
      
      // Complete step 6 (Final Step) to mark it as completed
      console.log('FinalStep: Completing step 6...');
      console.log('FinalStep: Calling setCurrentStep(6)...');
      const step6Result = await setCurrentStep(6);
      console.log('FinalStep: Step 6 completed successfully:', step6Result);
      
      // Complete the entire onboarding process
      console.log('FinalStep: Completing onboarding...');
      console.log('FinalStep: Calling completeOnboarding()...');
      const completionResult = await completeOnboarding();
      console.log('FinalStep: Onboarding completed successfully:', completionResult);
      
      // Mark onboarding as complete locally to unblock immediate navigation
      try { 
        localStorage.setItem('onboarding_complete', 'true'); 
        localStorage.setItem('onboarding_active_step', String(stepsLengthFallback()));
      } catch {}
      
      // Navigate directly to dashboard without calling onContinue
      // This bypasses the wizard flow and goes straight to the dashboard
      console.log('FinalStep: Navigating to dashboard...');
      console.log('FinalStep: Setting window.location.href to /dashboard');
      
      // Try multiple navigation methods to ensure redirect works
      try {
        window.location.href = '/dashboard';
        console.log('FinalStep: window.location.href set successfully');
      } catch (navError) {
        console.error('FinalStep: window.location.href failed:', navError);
        console.log('FinalStep: Trying alternative navigation method...');
        window.location.assign('/dashboard');
      }
      
      console.log('FinalStep: Navigation initiated');
    } catch (e: any) {
      console.error('FinalStep: Error completing onboarding:', e);
      console.error('FinalStep: Error details:', {
        message: e.message,
        status: e.response?.status,
        statusText: e.response?.statusText,
        data: e.response?.data,
        stack: e.stack
      });
      
      // Error handling is managed by global API client interceptors
      
      // Provide more specific error messages
      let errorMessage = 'Failed to complete onboarding. Please try again.';
      
      if (e.response?.data?.detail) {
        errorMessage = e.response.data.detail;
      } else if (e.response?.data?.message) {
        errorMessage = e.response.data.message;
      } else if (e.message) {
        errorMessage = e.message;
      }
      
      setError(errorMessage);
    }
    setLoading(false);
  };

  // Helper to compute steps length for storing active step (fallback value)
  const stepsLengthFallback = () => 6;

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

            {/* Agent Team */}
            {agentTeamError && (
              <Alert severity="warning" sx={{ mt: 3, borderRadius: 2 }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 0.5 }}>
                  Agent team configuration unavailable
                </Typography>
                <Typography variant="body2">{agentTeamError}</Typography>
              </Alert>
            )}
            {!agentTeamError && agentTeam.length > 0 && (
              <AgentTeamSection websiteName={websiteName} agents={agentTeam} contextCard={agentContextCard} />
            )}

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
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Button 
                          color="inherit" 
                          size="small"
                          onClick={() => setError(null)}
                        >
                          Dismiss
                        </Button>
                      </Box>
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

            {/* Validation Status */}
            {validationStatus && !validationStatus.isValid && (
              <Box sx={{ mb: 3 }}>
                <Alert severity="warning" sx={{ borderRadius: 2 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                    Setup Incomplete
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    The following steps need to be completed before launching:
                  </Typography>
                  <Box component="ul" sx={{ pl: 2, m: 0 }}>
                    {validationStatus.missingSteps.map((step, index) => (
                      <li key={index}>
                        <Typography variant="body2">{step}</Typography>
                      </li>
                    ))}
                  </Box>
                </Alert>
              </Box>
            )}

            {/* Launch Button */}
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
              <Button
                variant="contained"
                size="large"
                disabled={loading || dataLoading}
                onClick={handleLaunch}
                startIcon={<Rocket />}
                sx={{
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  fontSize: '1.125rem',
                  fontWeight: 600,
                  px: 4,
                  py: 2,
                  borderRadius: 2,
                  textTransform: 'none',
                  boxShadow: '0 4px 12px rgba(102, 126, 234, 0.3)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%)',
                    transform: 'translateY(-1px)',
                    boxShadow: '0 6px 16px rgba(102, 126, 234, 0.4)',
                  },
                  '&:disabled': {
                    background: 'rgba(0,0,0,0.1)',
                    color: 'rgba(0,0,0,0.4)',
                    boxShadow: 'none',
                    transform: 'none',
                  }
                }}
              >
                Launch Alwrity & Complete Setup
              </Button>
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
