import { useCallback } from 'react';

interface PersonaInitializationProps {
  stepData?: {
    corePersona?: any;
    platformPersonas?: Record<string, any>;
    qualityMetrics?: any;
    selectedPlatforms?: string[];
  };
  updateHeaderContent: (content: { title: string; description: string }) => void;
  setCorePersona: (persona: any) => void;
  setPlatformPersonas: (personas: Record<string, any>) => void;
  setQualityMetrics: (metrics: any) => void;
  setSelectedPlatforms: (platforms: string[]) => void;
  setShowPreview: (show: boolean) => void;
  setGenerationStep: (step: string) => void;
  setProgress: (progress: number) => void;
  setHasCheckedCache: (checked: boolean) => void;
  setSuccess: (message: string | null) => void;
  loadCachedPersonaData: () => boolean;
  loadServerCachedPersonaData: () => Promise<boolean>;
  generatePersonas: () => Promise<void>;
}

export const usePersonaInitialization = ({
  stepData,
  updateHeaderContent,
  setCorePersona,
  setPlatformPersonas,
  setQualityMetrics,
  setSelectedPlatforms,
  setShowPreview,
  setGenerationStep,
  setProgress,
  setHasCheckedCache,
  setSuccess,
  loadCachedPersonaData,
  loadServerCachedPersonaData,
  generatePersonas
}: PersonaInitializationProps) => {
  
  const initialize = useCallback(async () => {
    console.log('PersonaStep: Initialization started');
    
    // Update header immediately
    updateHeaderContent({
      title: 'AI Writing Persona Generation',
      description: 'ALwrity is analyzing your content and creating a sophisticated AI writing persona that captures your unique style, brand voice, and content preferences across all platforms.'
    });

    // Check if we already have persona data from stepData (when navigating back)
    if (stepData?.corePersona) {
      console.log('PersonaStep: Loading persona data from stepData (navigation back)');
      setCorePersona(stepData.corePersona);
      setPlatformPersonas(stepData.platformPersonas || {});
      setQualityMetrics(stepData.qualityMetrics || null);
      if (stepData.selectedPlatforms) {
        setSelectedPlatforms(stepData.selectedPlatforms);
      }
      setShowPreview(true);
      setGenerationStep('preview');
      setProgress(100);
      setHasCheckedCache(true);
      return;
    }

    // For fresh loads (not navigation back), always try server cache first
    // For navigation back, we already have stepData so skip server check
    if (!stepData?.corePersona) {
      try {
        console.log('PersonaStep: Checking server cache (fresh load)');
        const foundCache = await loadServerCachedPersonaData();
        if (foundCache) {
          console.log('PersonaStep: Server cache found, using it');
          setHasCheckedCache(true);
          return;
        }
      } catch (error: any) {
        console.warn('PersonaStep: Error loading server cache:', error);
      }
    } else {
      console.log('PersonaStep: Skipping server cache check (navigation with stepData)');
    }

    // Try local cache
    console.log('PersonaStep: Checking local cache');
    const foundCache = loadCachedPersonaData();
    if (foundCache) {
      console.log('PersonaStep: Local cache found, using it');
      setHasCheckedCache(true);
      return;
    }

    // No cache found, start generation
    console.log('PersonaStep: No cache found, starting generation');
    await generatePersonas();
    setHasCheckedCache(true);
  }, [
    stepData,
    updateHeaderContent,
    setCorePersona,
    setPlatformPersonas,
    setQualityMetrics,
    setSelectedPlatforms,
    setShowPreview,
    setGenerationStep,
    setProgress,
    setHasCheckedCache,
    loadCachedPersonaData,
    loadServerCachedPersonaData,
    generatePersonas
  ]);

  return {
    initialize
  };
};
