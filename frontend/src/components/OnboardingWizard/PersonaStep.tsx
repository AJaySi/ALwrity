import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Box
} from '@mui/material';
import {
  Psychology as PsychologyIcon,
  AutoAwesome as AutoAwesomeIcon,
  Assessment as AssessmentIcon
} from '@mui/icons-material';
import { usePersonaPolling } from '../../hooks/usePersonaPolling';
import { apiClient } from '../../api/client';
import { 
  type GenerationStep
} from './PersonaStep/PersonaGenerationProgress';
import { usePersonaInitialization } from './PersonaStep/personaInitialization';
import { usePersonaGeneration } from './PersonaStep/personaGeneration';
import { PersonaPreviewSection } from './PersonaStep/PersonaPreviewSection';
import { PersonaLoadingState } from './PersonaStep/PersonaLoadingState';
import { ComingSoonSection } from './PersonaStep/ComingSoonSection';

interface PersonaStepProps {
  onContinue: (personaData: PersonaData) => void;
  updateHeaderContent: (content: StepHeaderContent) => void;
  onValidationChange?: (isValid: boolean) => void;
  onboardingData?: {
    websiteAnalysis?: any;
    competitorResearch?: any;
    sitemapAnalysis?: any;
    businessData?: any;
  };
  stepData?: {
    corePersona?: any;
    platformPersonas?: Record<string, any>;
    qualityMetrics?: any;
    selectedPlatforms?: string[];
  };
}

interface StepHeaderContent {
  title: string;
  description: string;
}

interface PersonaData {
  corePersona: any;
  platformPersonas: Record<string, any>;
  qualityMetrics: any;
  selectedPlatforms: string[];
}

// GenerationStep and ProgressMessage types imported from PersonaGenerationProgress

interface QualityMetrics {
  overall_score: number;
  style_consistency: number;
  brand_alignment: number;
  platform_optimization: number;
  engagement_potential: number;
  recommendations: string[];
}

const PersonaStep: React.FC<PersonaStepProps> = ({
  onContinue,
  updateHeaderContent,
  onValidationChange,
  onboardingData = {},
  stepData
}) => {
  // Generation state
  const [generationStep, setGenerationStep] = useState<string>('analyzing');
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Persona data
  const [corePersona, setCorePersona] = useState<any>(null);
  const [platformPersonas, setPlatformPersonas] = useState<Record<string, any>>({});
  const [qualityMetrics, setQualityMetrics] = useState<QualityMetrics | null>(null);
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>(['linkedin', 'blog']);

  // UI state
  const [showPreview, setShowPreview] = useState(false);
  const [expandedAccordion, setExpandedAccordion] = useState<string | false>('core');

  // Available platforms are now defined in PersonaPreviewSection

  // Generation steps
  const generationSteps: GenerationStep[] = [
    {
      id: 'analyzing',
      name: 'Analyzing Your Data',
      description: 'Processing website analysis, competitor research, and content insights',
      icon: <AssessmentIcon />,
      completed: generationStep !== 'analyzing',
      progress: generationStep === 'analyzing' ? 100 : 100
    },
    {
      id: 'generating',
      name: 'Generating Brand Voice',
      description: 'Creating your unique brand writing style and identity',
      icon: <PsychologyIcon />,
      completed: ['adapting', 'assessing', 'preview'].includes(generationStep),
      progress: ['adapting', 'assessing', 'preview'].includes(generationStep) ? 100 : 0
    },
    {
      id: 'adapting',
      name: 'Adapting to Platforms',
      description: 'Tailoring your brand voice for different content platforms',
      icon: <AutoAwesomeIcon />,
      completed: ['assessing', 'preview'].includes(generationStep),
      progress: ['assessing', 'preview'].includes(generationStep) ? 100 : 0
    },
    {
      id: 'assessing',
      name: 'Quality Assessment',
      description: 'Evaluating persona accuracy and optimization potential',
      icon: <AssessmentIcon />,
      completed: generationStep === 'preview',
      progress: generationStep === 'preview' ? 100 : 0
    }
  ];

  // Load cached persona data
  const loadCachedPersonaData = useCallback(() => {
    try {
      const cachedData = localStorage.getItem('persona_generation_data');
      if (cachedData) {
        const parsedData = JSON.parse(cachedData);
        
        // Check if cache is still valid (24 hours)
        const cacheTime = new Date(parsedData.timestamp);
        const now = new Date();
        const hoursDiff = (now.getTime() - cacheTime.getTime()) / (1000 * 60 * 60);
        
        if (hoursDiff < 24) {
          console.log('Loading cached persona data...');
          setCorePersona(parsedData.core_persona);
          setPlatformPersonas(parsedData.platform_personas);
          setQualityMetrics(parsedData.quality_metrics);
          setShowPreview(true);
          setGenerationStep('preview');
          setProgress(100);
          
          // Show cache notification
          setSuccess('Loaded your saved Brand Voice. Click "Regenerate" for a fresh analysis.');
          return true;
        } else {
          // Remove expired cache
          localStorage.removeItem('persona_generation_data');
        }
      }
    } catch (err) {
      console.warn('Failed to load cached Brand Voice:', err);
    }
    return false;
  }, []);

  // Load cached persona data from server (24h TTL on backend)
  const loadServerCachedPersonaData = useCallback(async () => {
    try {
      const resp = await apiClient.get('/api/onboarding/step4/persona-latest');
      if (resp.data && resp.data.success && resp.data.persona) {
        const p = resp.data.persona;
        setCorePersona(p.core_persona);
        setPlatformPersonas(p.platform_personas || {});
        setQualityMetrics(p.quality_metrics || null);
        if (Array.isArray(p.selected_platforms)) {
          setSelectedPlatforms(p.selected_platforms);
        }
        setShowPreview(true);
        setGenerationStep('preview');
        setProgress(100);

        // Mirror to local cache for faster subsequent loads
        try {
          localStorage.setItem('persona_generation_data', JSON.stringify({
            ...p,
            timestamp: p.timestamp || new Date().toISOString(),
          }));
        } catch {}

        setSuccess('Loaded your saved Brand Voice from server. Click "Regenerate" for a fresh analysis.');
        return true;
      }
    } catch (e: any) {
      // 404 means no cache; 401 means auth issue (will be handled by delay/retry)
      if (e?.response?.status === 404) {
        console.log('No cached persona found on server');
      } else if (e?.response?.status === 401) {
        console.log('Authentication not ready, will retry');
        throw e; // Re-throw to trigger retry in parent function
      } else {
        console.warn('Error loading server cached persona:', e);
      }
    }
    return false;
  }, []);

  // Save persona data to cache
  const savePersonaDataToCache = useCallback((personaData: any) => {
    try {
      const cacheData = {
        ...personaData,
        timestamp: new Date().toISOString(),
        selected_platforms: selectedPlatforms
      };
      localStorage.setItem('persona_generation_data', JSON.stringify(cacheData));
      console.log('Persona data cached successfully');
    } catch (err) {
      console.warn('Failed to cache persona data:', err);
    }
  }, [selectedPlatforms]);

  // Use the polling hook for persona generation first
  const {
    progressMessages,
    error: pollingError,
    startPolling
  } = usePersonaPolling({
    onProgress: (message, progress) => {
      console.log('Persona generation progress:', message, progress);
      setProgress(progress);
      setGenerationStep(getStepFromMessage(message));
    },
    onComplete: (personaResult) => {
      console.log('Persona generation completed:', personaResult);
      if (personaResult && personaResult.success) {
        setCorePersona(personaResult.core_persona);
        setPlatformPersonas(personaResult.platform_personas);
        setQualityMetrics(personaResult.quality_metrics);
        setShowPreview(true);
        setGenerationStep('preview');
        setProgress(100);
        
        // Save to cache
        savePersonaDataToCache(personaResult);
      }
      setIsGenerating(false);
    },
    onError: (error) => {
      console.error('Persona generation failed:', error);
      setError(error);
      setIsGenerating(false);
    }
  });

  // Use extracted hooks for initialization and generation logic
  const {
    generatePersonas,
    getStepFromMessage
  } = usePersonaGeneration({
    onboardingData,
    selectedPlatforms,
    setCorePersona,
    setPlatformPersonas,
    setQualityMetrics,
    setShowPreview,
    setGenerationStep,
    setProgress,
    setIsGenerating,
    setError,
    savePersonaDataToCache,
    startPolling
  });

  const {
    initialize
  } = usePersonaInitialization({
    onboardingData,
    stepData,
    updateHeaderContent,
    setCorePersona,
    setPlatformPersonas,
    setQualityMetrics,
    setSelectedPlatforms,
    setShowPreview,
    setGenerationStep,
    setProgress,
    setSuccess,
    loadCachedPersonaData,
    loadServerCachedPersonaData,
    generatePersonas
  });

  // Prevent double initialization in React Strict Mode
  const initRef = useRef(false);

  useEffect(() => {
    // Skip if already initialized
    if (initRef.current) {
      console.log('PersonaStep: Skipping duplicate initialization (initRef guard)');
      return;
    }
    initRef.current = true;

    initialize();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Run only once on mount

  // Cache loading and saving functions are now handled by usePersonaInitialization hook

  const handleRegenerate = () => {
    setShowPreview(false);
    setCorePersona(null);
    setPlatformPersonas({});
    setQualityMetrics(null);
    generatePersonas();
  };

  // Handle continue with persona data
  const handleContinue = useCallback(() => {
    if (corePersona && platformPersonas && qualityMetrics) {
      const personaData = {
        corePersona,
        platformPersonas,
        qualityMetrics,
        selectedPlatforms,
        stepType: 'personalization',
        completedAt: new Date().toISOString()
      };
      console.log('PersonaStep: Calling onContinue with persona data:', personaData);
      onContinue(personaData);
    } else {
      console.warn('PersonaStep: Missing persona data, cannot continue');
    }
  }, [corePersona, platformPersonas, qualityMetrics, selectedPlatforms, onContinue]);

  // Validation effect - notify wizard when persona data is ready
  useEffect(() => {
    // Only validate as complete if:
    // 1. Not currently generating
    // 2. Generation completed successfully (has success data)
    // 3. Has all required persona data
    const hasValidData = !!(corePersona && platformPersonas && Object.keys(platformPersonas).length > 0 && qualityMetrics);
    const isComplete = !isGenerating && hasValidData && generationStep === 'preview';
    const isValid = isComplete;
    
    console.log('PersonaStep: Validation check:', {
      corePersona: !!corePersona,
      platformPersonas: !!platformPersonas,
      platformPersonasCount: platformPersonas ? Object.keys(platformPersonas).length : 0,
      qualityMetrics: !!qualityMetrics,
      isGenerating,
      generationStep,
      hasValidData,
      isComplete,
      isValid
    });
    
    if (onValidationChange) {
      console.log('PersonaStep: Calling onValidationChange with:', isValid);
      onValidationChange(isValid);
    }
  }, [corePersona, platformPersonas, qualityMetrics, isGenerating, generationStep, onValidationChange]);

  // Auto-call onContinue when persona data is ready and generation is complete
  useEffect(() => {
    console.log('PersonaStep: Checking persona data readiness:', {
      corePersona: !!corePersona,
      platformPersonas: !!platformPersonas,
      qualityMetrics: !!qualityMetrics,
      success,
      isGenerating,
      generationStep
    });
    
    // Only auto-continue if:
    // 1. Generation is complete (not generating and at preview step)
    // 2. Has valid persona data and success flag
    const hasValidData = corePersona && platformPersonas && qualityMetrics && success;
    const isGenerationComplete = !isGenerating && generationStep === 'preview';
    
    if (hasValidData && isGenerationComplete) {
      console.log('PersonaStep: Persona data is ready and generation complete, auto-calling onContinue');
      handleContinue();
    } else {
      console.log('PersonaStep: Not ready to continue yet - hasValidData:', hasValidData, 'isGenerationComplete:', isGenerationComplete);
    }
  }, [corePersona, platformPersonas, qualityMetrics, success, isGenerating, generationStep, handleContinue]);

  // (auto-generation handled in initial effect via server/local cache fallback)

  return (
    <Box sx={{
      width: '100%',
      maxWidth: '100%',
      mx: 'auto',
      p: { xs: 1, sm: 2, md: 3 },
      background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
      minHeight: '100vh',
      overflow: 'hidden'
    }}>
      {/* Loading State and Error Handling */}
      <PersonaLoadingState
        showPreview={showPreview}
        isGenerating={isGenerating}
        corePersona={corePersona}
        progress={progress}
        generationStep={generationStep}
        generationSteps={generationSteps}
        progressMessages={progressMessages}
        error={error}
        pollingError={pollingError}
        success={success}
        handleRegenerate={handleRegenerate}
        generatePersonas={generatePersonas}
        setShowPreview={setShowPreview}
        setSuccess={setSuccess}
      />

      {/* Persona Preview Section */}
      <PersonaPreviewSection
        showPreview={showPreview}
        corePersona={corePersona}
        platformPersonas={platformPersonas}
        qualityMetrics={qualityMetrics}
        selectedPlatforms={selectedPlatforms}
        expandedAccordion={expandedAccordion}
        setExpandedAccordion={setExpandedAccordion}
        setCorePersona={setCorePersona}
        setPlatformPersonas={setPlatformPersonas}
        handleRegenerate={handleRegenerate}
      />

      {/* Coming Soon Section */}
      <ComingSoonSection />
    </Box>
  );
};

export default PersonaStep;
