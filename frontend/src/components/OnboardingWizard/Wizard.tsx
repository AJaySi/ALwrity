import React, { useEffect, useState, useCallback, useMemo, useRef } from 'react';
import { 
  Box, 
  Paper,
  Fade,
  Slide,
  useTheme,
  useMediaQuery
} from '@mui/material';
import { getCurrentStep, setCurrentStep } from '../../api/onboarding';
import { apiClient } from '../../api/client';
import ApiKeyStep from './ApiKeyStep';
import WebsiteStep from './WebsiteStep';
import CompetitorAnalysisStep from './CompetitorAnalysisStep';
import PersonaStep from './PersonaStep';
import IntegrationsStep from './IntegrationsStep';
import FinalStep from './FinalStep';
import { WizardHeader } from './common/WizardHeader';
import { WizardNavigation } from './common/WizardNavigation';
import { WizardLoadingState } from './common/WizardLoadingState';

const steps = [
  { label: 'API Keys', description: 'Connect your AI services', icon: '🔑' },
  { label: 'Website', description: 'Set up your website', icon: '🌐' },
  { label: 'Research', description: 'Discover competitors', icon: '🔍' },
  { label: 'Personalization', description: 'Customize your experience', icon: '⚙️' },
  { label: 'Integrations', description: 'Connect additional services', icon: '🔗' },
  { label: 'Finish', description: 'Complete setup', icon: '✅' }
];

interface WizardProps {
  onComplete?: () => void;
}

interface StepHeaderContent {
  title: string;
  description: string;
}

const Wizard: React.FC<WizardProps> = ({ onComplete }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(true);
  const [progress, setProgressState] = useState(0);
  const [direction, setDirection] = useState<'left' | 'right'>('right');
  const [showHelp, setShowHelp] = useState(false);
  const [showProgressMessage, setShowProgressMessage] = useState(false);
  const [progressMessage, setProgressMessage] = useState('');
  // sessionId removed - backend uses Clerk user ID from auth token
  const [stepData, setStepData] = useState<any>(null);
  const [competitorDataCollector, setCompetitorDataCollector] = useState<(() => any) | null>(null);
  const [isCurrentStepValid, setIsCurrentStepValid] = useState<boolean>(false);
  const [stepValidationStates, setStepValidationStates] = useState<Record<number, boolean>>({});
  const [stepHeaderContent, setStepHeaderContent] = useState<StepHeaderContent>({
    title: steps[0].label,
    description: steps[0].description
  });

  // Step validation function
  const isStepDataValid = useCallback((step: number, data: any): boolean => {
    console.log(`Wizard: Validating step ${step} with data:`, data);
    
    switch (step) {
      case 0: // API Keys
        const hasApiKeys = data && data.api_keys && Object.keys(data.api_keys).length > 0;
        console.log(`Wizard: Step 0 (API Keys) validation:`, !!hasApiKeys);
        return !!hasApiKeys;
      
      case 1: // Website Analysis
        const hasWebsite = data && (data.website || data.website_url);
        console.log(`Wizard: Step 1 (Website) validation:`, !!hasWebsite);
        return !!hasWebsite;
      
      case 2: // Competitor Analysis
        const hasCompetitorData = data && (data.competitors || data.researchSummary || data.sitemapAnalysis);
        console.log(`Wizard: Step 2 (Competitor Analysis) validation:`, {
          hasCompetitorData: !!hasCompetitorData,
          hasCompetitors: !!(data && data.competitors),
          hasResearchSummary: !!(data && data.researchSummary),
          hasSitemapAnalysis: !!(data && data.sitemapAnalysis),
          dataKeys: data ? Object.keys(data) : 'no data'
        });
        return !!hasCompetitorData;
      
      case 3: // Persona Generation
        const hasValidPersonaData = data && 
                                  data.corePersona && 
                                  data.platformPersonas && 
                                  Object.keys(data.platformPersonas).length > 0 &&
                                  data.qualityMetrics;
        console.log(`Wizard: Step 3 (Persona Generation) validation:`, {
          hasValidPersonaData: !!hasValidPersonaData,
          hasCorePersona: !!(data && data.corePersona),
          hasPlatformPersonas: !!(data && data.platformPersonas),
          platformPersonasCount: data && data.platformPersonas ? Object.keys(data.platformPersonas).length : 0,
          hasQualityMetrics: !!(data && data.qualityMetrics),
          dataKeys: data ? Object.keys(data) : 'no data'
        });
        return !!hasValidPersonaData;
      
      case 4: // Integrations
        console.log(`Wizard: Step 4 (Integrations) validation: always true (optional)`);
        return true; // Integrations step is optional
      
      case 5: // Final Step
        console.log(`Wizard: Step 5 (Final) validation: always true`);
        return true; // Final step is always valid
      
      default:
        console.log(`Wizard: Unknown step ${step} validation: false`);
        return false;
    }
  }, []);
  
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // Use refs to avoid dependency cycles
  const stepDataRef = useRef(stepData);
  const competitorDataCollectorRef = useRef(competitorDataCollector);
  
  // Keep refs in sync with state
  useEffect(() => {
    stepDataRef.current = stepData;
    console.log('Wizard: stepData changed:', stepData);
  }, [stepData]);
  
  useEffect(() => {
    competitorDataCollectorRef.current = competitorDataCollector;
    console.log('Wizard: competitorDataCollector changed:', competitorDataCollector);
  }, [competitorDataCollector]);

  // Validate current step data
  useEffect(() => {
    console.log(`Wizard: Validation effect triggered - activeStep: ${activeStep}, stepData:`, stepData);
    console.log(`Wizard: stepData type:`, typeof stepData, 'keys:', stepData ? Object.keys(stepData) : 'no data');
    console.log(`Wizard: stepValidationStates:`, stepValidationStates);
    
    // For step 0 (API Keys), step 1 (Website), and step 3 (Persona), use the step validation state if available
    if ((activeStep === 0 || activeStep === 1 || activeStep === 3) && stepValidationStates[activeStep] !== undefined) {
      console.log(`Wizard: Using step validation state for step ${activeStep}:`, stepValidationStates[activeStep]);
      setIsCurrentStepValid(stepValidationStates[activeStep]);
      return;
    }
    
    // For other steps, use the existing validation logic
    // For CompetitorAnalysisStep, also check the competitorDataCollector data
    let dataToValidate = stepData;
    if (activeStep === 2 && competitorDataCollector) {
      console.log(`Wizard: Using competitorDataCollector data for validation:`, competitorDataCollector);
      dataToValidate = competitorDataCollector;
    }
    
    const isValid = isStepDataValid(activeStep, dataToValidate);
    console.log(`Wizard: Validation result for step ${activeStep}:`, isValid);
    console.log(`Wizard: Setting isCurrentStepValid to:`, isValid);
    setIsCurrentStepValid(isValid);
  }, [activeStep, stepData, isStepDataValid, competitorDataCollector, stepValidationStates]);
  
  // Debug: log all state changes
  useEffect(() => {
    console.log('Wizard: Render triggered - activeStep:', activeStep, 'direction:', direction);
  }, [activeStep, direction]);
  
  // Debug: log Continue button state
  useEffect(() => {
    console.log(`Wizard: isCurrentStepValid changed to: ${isCurrentStepValid} (Continue button ${isCurrentStepValid ? 'ENABLED' : 'DISABLED'})`);
  }, [isCurrentStepValid]);

  // Handle validation changes from individual steps
  const handleStepValidationChange = useCallback((step: number, isValid: boolean) => {
    console.log(`Wizard: handleStepValidationChange called - step: ${step}, isValid: ${isValid}`);
    setStepValidationStates(prev => {
      // Only update if the value actually changed
      if (prev[step] === isValid) {
        console.log(`Wizard: Validation state unchanged for step ${step}, skipping update`);
        return prev; // Return same reference to prevent re-render
      }
      const newState = { ...prev, [step]: isValid };
      console.log(`Wizard: Updated stepValidationStates:`, newState);
      return newState;
    });
  }, []);
  
  // Memoized callback specifically for ApiKeyStep to prevent infinite loops
  const handleApiKeyValidationChange = useCallback((isValid: boolean) => {
    handleStepValidationChange(0, isValid);
  }, [handleStepValidationChange]);

  // Memoize the onDataReady callback to prevent infinite loops
  const handleCompetitorDataReady = useCallback((dataCollector: (() => any) | undefined) => {
    console.log('Wizard: onDataReady called with:', dataCollector);
    console.log('Wizard: dataCollector type:', typeof dataCollector);
    if (typeof dataCollector === 'function') {
      setCompetitorDataCollector(dataCollector);
    } else {
      console.error('Wizard: dataCollector is not a function:', dataCollector);
    }
  }, []);

  useEffect(() => {
    console.log('Wizard: Component mounted');
    const init = async () => {
      try {
        setLoading(true);
        console.log('Wizard: Starting initialization...');
        
        // Check if we already have init data from App (cached in sessionStorage)
        const cachedInit = sessionStorage.getItem('onboarding_init');
        
        if (cachedInit) {
          console.log('Wizard: Using cached init data from batch endpoint');
          const data = JSON.parse(cachedInit);

          // Extract data from batch response
          const { onboarding, session } = data;

          // Load step data, especially research data from step 3 and persona data from step 4
          if (onboarding.steps && Array.isArray(onboarding.steps)) {
            // Load research preferences from step 3
            const step3Data = onboarding.steps.find((step: any) => step.step_number === 3);
            if (step3Data && step3Data.data) {
              console.log('Wizard: Loading research data from step 3:', Object.keys(step3Data.data));
              setStepData((prevData: any) => ({ ...prevData, ...step3Data.data }));
            }

            // Load persona data from step 4
            const step4Data = onboarding.steps.find((step: any) => step.step_number === 4);
            if (step4Data && step4Data.data) {
              console.log('Wizard: Loading persona data from step 4:', Object.keys(step4Data.data));
              setStepData((prevData: any) => ({ ...prevData, ...step4Data.data }));
            }
          }

          // Set state from cached data - NO API CALLS NEEDED!
          setActiveStep(onboarding.current_step - 1);
          setProgressState(onboarding.completion_percentage);
          // Note: Session managed by Clerk auth, no need to track separately

          console.log('Wizard: Initialized from cache:', {
            step: onboarding.current_step,
            progress: onboarding.completion_percentage,
            userId: session.session_id,  // Clerk user ID from backend
            hasPersonaData: !!stepData
          });

          setLoading(false);
          return; // ← Skip redundant API calls!
        }
        
        // Fallback: If no cached data (shouldn't happen), make batch call
        console.log('Wizard: No cached data, making batch init call');
        const response = await apiClient.get('/api/onboarding/init');
        const { onboarding, session } = response.data;

        // Load step data, especially research data from step 3 and persona data from step 4
        if (onboarding.steps && Array.isArray(onboarding.steps)) {
          // Load research preferences from step 3
          const step3Data = onboarding.steps.find((step: any) => step.step_number === 3);
          if (step3Data && step3Data.data) {
            console.log('Wizard: Loading research data from step 3 API call:', Object.keys(step3Data.data));
            setStepData((prevData: any) => ({ ...prevData, ...step3Data.data }));
          }

          // Load persona data from step 4
          const step4Data = onboarding.steps.find((step: any) => step.step_number === 4);
          if (step4Data && step4Data.data) {
            console.log('Wizard: Loading persona data from step 4 API call:', Object.keys(step4Data.data));
            setStepData((prevData: any) => ({ ...prevData, ...step4Data.data }));
          }
        }

        // Cache for future use
        sessionStorage.setItem('onboarding_init', JSON.stringify(response.data));

        // Set state from API response
        setActiveStep(onboarding.current_step - 1);
        setProgressState(onboarding.completion_percentage);
        // Note: Session managed by Clerk auth, no need to track separately

        console.log('Wizard: Initialized from API:', {
          step: onboarding.current_step,
          progress: onboarding.completion_percentage,
          userId: session.session_id,  // Clerk user ID from backend
          hasPersonaData: !!stepData
        });
      } catch (error) {
        console.error('Error initializing onboarding:', error);
      } finally {
        setLoading(false);
      }
    };
    init();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Run only once on mount - stepData is used for logging only

  const handleNext = useCallback(async (rawStepData?: any) => {
    console.log('Wizard: handleNext called');
    console.log('Wizard: Current step:', activeStep);
    console.log('Wizard: Step data:', stepDataRef.current);
    console.log('Wizard: competitorDataCollector:', competitorDataCollectorRef.current);
    console.log('Wizard: competitorDataCollector type:', typeof competitorDataCollectorRef.current);
    
    if (rawStepData && typeof rawStepData === 'object') {
      if (typeof rawStepData.preventDefault === 'function') {
        rawStepData.preventDefault();
      }
      if (typeof rawStepData.stopPropagation === 'function') {
        rawStepData.stopPropagation();
      }
    }

    let currentStepData = rawStepData && typeof rawStepData === 'object' && 'nativeEvent' in rawStepData
      ? undefined
      : rawStepData;

    // Special handling for CompetitorAnalysisStep (step 2)
    if (activeStep === 2) {
      console.log('Wizard: Handling CompetitorAnalysisStep data...');
      
      // If we have data from onContinue, use it
      if (currentStepData) {
        console.log('Wizard: Using data from CompetitorAnalysisStep onContinue:', currentStepData);
      } else {
        // Fallback: try to get data from collector
        const collector = competitorDataCollectorRef.current;
        if (collector && typeof collector === 'function') {
          console.log('Wizard: Collecting data from CompetitorAnalysisStep collector...');
          currentStepData = collector();
        } else if (collector && typeof collector === 'object') {
          console.warn('Wizard: competitorDataCollector is an object; using it directly as step data');
          currentStepData = collector;
        } else {
          console.warn('Wizard: competitorDataCollector not available; using empty data');
          // Fallback: create minimal data structure to prevent errors
          const currentData = stepDataRef.current;
          currentStepData = {
            competitors: [],
            researchSummary: null,
            sitemapAnalysis: null,
            userUrl: currentData?.website || '',
            industryContext: currentData?.industryContext,
            analysisTimestamp: new Date().toISOString()
          };
        }
      }
    }

    // Merge research data with existing step data for CompetitorAnalysisStep
    if (activeStep === 2 && currentStepData) {
      console.log('Wizard: Merging CompetitorAnalysisStep data with existing step data...');
      
      // Merge research data with existing step data
      const currentData = stepDataRef.current || {};
      const researchData = currentStepData || {};

      // Ensure we have research data
      if (researchData.competitors || researchData.researchSummary || researchData.sitemapAnalysis) {
        currentStepData = {
          ...currentData, // Preserve existing data (website, etc.)
          ...researchData, // Add/update research data
          // Ensure all required research fields are present
          competitors: researchData.competitors || currentData.competitors,
          researchSummary: researchData.researchSummary || currentData.researchSummary,
          sitemapAnalysis: researchData.sitemapAnalysis || currentData.sitemapAnalysis,
          // Mark this as the research step
          stepType: 'research',
          completedAt: new Date().toISOString()
        };

        console.log('Wizard: Merged research data:', currentStepData);
      } else {
        console.warn('Wizard: No research data provided, using existing step data');
        currentStepData = currentData;
      }
    }

    // Special handling for PersonaStep (step 3)
    if (activeStep === 3) {
      console.log('Wizard: Handling PersonaStep data...');

      // If we have data from onContinue, use it
      if (currentStepData && currentStepData.corePersona && currentStepData.qualityMetrics) {
        console.log('Wizard: Using persona data from PersonaStep onContinue:', currentStepData);
        // Data is already in currentStepData, no need to modify it
      } else {
        // Check if we have valid persona data in stepData
        const currentData = stepDataRef.current || {};
        const hasValidPersonaData = currentData.corePersona && 
                                   currentData.platformPersonas && 
                                   Object.keys(currentData.platformPersonas).length > 0 &&
                                   currentData.qualityMetrics;
        
        console.log('Wizard: Persona data validation:', {
          hasCorePersona: !!currentData.corePersona,
          hasPlatformPersonas: !!currentData.platformPersonas,
          platformPersonasCount: currentData.platformPersonas ? Object.keys(currentData.platformPersonas).length : 0,
          hasQualityMetrics: !!currentData.qualityMetrics,
          hasValidPersonaData
        });
        
        if (hasValidPersonaData) {
          console.log('Wizard: Using existing valid persona data from stepData');
          currentStepData = currentData;
        } else {
          console.warn('Wizard: No valid persona data available for PersonaStep - cannot complete step');
          // Don't try to complete the step if we don't have valid persona data
          console.log('Wizard: Aborting step completion - missing valid persona data');
          setLoading(false);
          setShowProgressMessage(false);
          setProgressMessage('');
          return;
        }
      }
    }

    // Store step data in state
    if (currentStepData) {
      setStepData(currentStepData);
    }

    console.log('Wizard: handleNext called with stepData:', currentStepData);
    console.log('Wizard: Current activeStep:', activeStep);
    console.log('Wizard: Steps length:', steps.length);
    
    setDirection('right');
    const nextStep = activeStep + 1;
    
    console.log('Wizard: Next step will be:', nextStep);
    
    // Show progress message
    const newProgress = ((nextStep + 1) / steps.length) * 100;
    setProgressMessage(`Your data is saved, moving to the next step. Progress is ${Math.round(newProgress)}%`);
    setShowProgressMessage(true);
    
    // Hide message after 3 seconds
    setTimeout(() => {
      setShowProgressMessage(false);
    }, 3000);
    
    // Complete the current step (activeStep + 1 because steps are 1-indexed)
    const currentStepNumber = activeStep + 1;

    const stepWasCompleted = currentStepData && typeof currentStepData === 'object' && (
      currentStepData.website || 
      currentStepData.businessData || 
      currentStepData.competitors ||
      currentStepData.researchSummary ||
      currentStepData.sitemapAnalysis ||
      currentStepData.corePersona || 
      currentStepData.platformPersonas ||
      currentStepData.qualityMetrics
    );

    console.log('Wizard: Step completion check:', {
      currentStepNumber,
      hasData: !!currentStepData,
      dataKeys: currentStepData ? Object.keys(currentStepData) : [],
      stepWasCompleted,
      website: !!currentStepData?.website,
      businessData: !!currentStepData?.businessData,
      competitors: !!currentStepData?.competitors,
      researchSummary: !!currentStepData?.researchSummary,
      sitemapAnalysis: !!currentStepData?.sitemapAnalysis,
      corePersona: !!currentStepData?.corePersona,
      platformPersonas: !!currentStepData?.platformPersonas,
      qualityMetrics: !!currentStepData?.qualityMetrics
    });

    if (!stepWasCompleted) {
      console.warn('Wizard: No serialized step data supplied; skipping backend completion for step', currentStepNumber);
    } else {
      console.log('Wizard: Completing current step:', currentStepNumber, 'with data:', currentStepData);

      try {
        await setCurrentStep(currentStepNumber, currentStepData);
      } catch (error) {
        console.error('Wizard: Failed to complete step with backend. Aborting progression.', error);
        setShowProgressMessage(false);
        setProgressMessage('');
        setLoading(false);
        return;
      }

      console.log('Wizard: Checking backend step after completion...');
      const stepResponse = await getCurrentStep();
      console.log('Wizard: Backend says current step should be:', stepResponse.step);
    }
    
    setActiveStep(nextStep);
    console.log('Wizard: Setting activeStep to:', nextStep);
    
    // Update progress
    setProgressState(newProgress);
    
    // If this is the final step, call onComplete
    if (nextStep === steps.length - 1) {
      console.log('Wizard: This is the final step, calling onComplete');
      onComplete?.();
    } else {
      console.log('Wizard: Not the final step, continuing to next step');
    }
  }, [activeStep, onComplete]);

  const handleBack = useCallback(async () => {
    setDirection('left');
    const prevStep = activeStep - 1;
    setActiveStep(prevStep);
    // Do not complete a step when navigating back; just update UI state
    // Backend step progression should only occur on forward completion with valid data
    
    // Update progress
    const newProgress = ((prevStep + 1) / steps.length) * 100;
    setProgressState(newProgress);
  }, [activeStep]);

  const handleStepClick = (stepIndex: number) => {
    if (stepIndex <= activeStep) {
      setDirection(stepIndex > activeStep ? 'right' : 'left');
      setActiveStep(stepIndex);
      // Do not complete a step on arbitrary step navigation; only adjust UI
    }
  };

  const updateHeaderContent = useCallback((content: StepHeaderContent) => {
    setStepHeaderContent(prev => {
      if (prev.title === content.title && prev.description === content.description) {
        return prev;
      }
      return content;
    });
  }, []);

  const handleComplete = useCallback(async () => {
    console.log('Wizard: handleComplete called - completing onboarding');
    try {
      // Call onComplete to notify parent component
      onComplete?.();
    } catch (error) {
      console.error('Error completing onboarding:', error);
    }
  }, [onComplete]);

  // Memoize data objects passed as props to avoid recreating them each render
  const personaOnboardingData = useMemo(() => ({
    websiteAnalysis: stepData?.analysis,
    competitorResearch: stepData?.competitors,
    sitemapAnalysis: stepData?.sitemapAnalysis,
    businessData: stepData?.businessData
  }), [stepData?.analysis, stepData?.competitors, stepData?.sitemapAnalysis, stepData?.businessData]);

  const personaStepData = useMemo(() => ({
    corePersona: stepData?.corePersona,
    platformPersonas: stepData?.platformPersonas,
    qualityMetrics: stepData?.qualityMetrics,
    selectedPlatforms: stepData?.selectedPlatforms
  }), [stepData?.corePersona, stepData?.platformPersonas, stepData?.qualityMetrics, stepData?.selectedPlatforms]);

  const renderStepContent = (step: number) => {
    const stepComponents = [
      <ApiKeyStep key="api-keys" onContinue={handleNext} updateHeaderContent={updateHeaderContent} onValidationChange={handleApiKeyValidationChange} />,
      <WebsiteStep key="website" onContinue={handleNext} updateHeaderContent={updateHeaderContent} onValidationChange={(isValid) => handleStepValidationChange(1, isValid)} />,
      <CompetitorAnalysisStep 
        key="research" 
        onContinue={handleNext} 
        onBack={handleBack}
        userUrl={stepData?.website || localStorage.getItem('website_url') || ''}
        industryContext={stepData?.industryContext}
        onDataReady={handleCompetitorDataReady}
      />,
      <PersonaStep 
        key="personalization" 
        onContinue={handleNext} 
        updateHeaderContent={updateHeaderContent}
        onValidationChange={(isValid) => handleStepValidationChange(3, isValid)}
        onboardingData={personaOnboardingData}
        stepData={personaStepData}
      />,
      <IntegrationsStep key="integrations" onContinue={handleNext} updateHeaderContent={updateHeaderContent} />,
      <FinalStep key="final" onContinue={handleComplete} updateHeaderContent={updateHeaderContent} />
    ];

    return (
      <Slide direction={direction} in={true} mountOnEnter unmountOnExit key={`step-${step}`}>
        <Box sx={{ minHeight: '500px', display: 'flex', flexDirection: 'column' }}>
          {stepComponents[step]}
        </Box>
      </Slide>
    );
  };

  // Show loading state if loading
  if (loading) {
    return <WizardLoadingState loading={loading} />;
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        p: { xs: 2, md: 4 },
        position: 'relative',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%), radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%)',
          pointerEvents: 'none',
        }
      }}
    >
      <Paper
        elevation={24}
        sx={{
          maxWidth: '100%',
          width: '100%',
          borderRadius: 4,
          overflow: 'visible',
          background: 'rgba(255, 255, 255, 0.98)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.3)',
          position: 'relative',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
        }}
      >
        {/* Header with Stepper */}
        <WizardHeader
          activeStep={activeStep}
          progress={progress}
          stepHeaderContent={stepHeaderContent}
          showProgressMessage={showProgressMessage}
          progressMessage={progressMessage}
          showHelp={showHelp}
          isMobile={isMobile}
          steps={steps}
          onStepClick={handleStepClick}
          onHelpToggle={() => setShowHelp(!showHelp)}
        />

        {/* Content */}
        <Box sx={{ p: { xs: 1, md: 2 }, pt: 1, width: '100%', overflow: 'visible' }}>
          <Fade in={true} timeout={400}>
            <Box sx={{ width: '100%', overflow: 'visible' }}>
              {renderStepContent(activeStep)}
            </Box>
          </Fade>
        </Box>

        {/* Navigation */}
        <WizardNavigation
          activeStep={activeStep}
          totalSteps={steps.length}
          onBack={handleBack}
          onNext={handleNext}
          isLastStep={activeStep === steps.length - 1}
          isCurrentStepValid={isCurrentStepValid}
        />
      </Paper>
    </Box>
  );
};

export default Wizard; 