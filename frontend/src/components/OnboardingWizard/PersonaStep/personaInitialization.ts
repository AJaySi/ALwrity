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
      return;
    }

    // Check session flag to avoid redundant server cache checks
    const serverCacheChecked = sessionStorage.getItem('persona_server_cache_checked');
    
    // Try to load from server cache first (skip if already checked this session and was 404)
    let foundCache = false;
    if (!serverCacheChecked || serverCacheChecked !== '404') {
      try {
        console.log('PersonaStep: Checking server cache');
        foundCache = await loadServerCachedPersonaData();
        if (foundCache) {
          console.log('PersonaStep: Server cache found, using it');
          sessionStorage.setItem('persona_server_cache_checked', 'found');
          return;
        } else {
          // Mark that we checked and got 404
          sessionStorage.setItem('persona_server_cache_checked', '404');
        }
      } catch (error: any) {
        console.warn('PersonaStep: Error loading server cache, trying local cache:', error);
        sessionStorage.setItem('persona_server_cache_checked', '404');
      }
    } else {
      console.log('PersonaStep: Skipping server cache check (already checked this session, was 404)');
    }

    // Try local cache
    console.log('PersonaStep: Checking local cache');
    foundCache = loadCachedPersonaData();
    if (foundCache) {
      console.log('PersonaStep: Local cache found, using it');
      return;
    }

    // No cache found, start generation
    console.log('PersonaStep: No cache found, starting generation');
    await generatePersonas();
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
    loadCachedPersonaData,
    loadServerCachedPersonaData,
    generatePersonas
  ]);

  return {
    initialize
  };
};
