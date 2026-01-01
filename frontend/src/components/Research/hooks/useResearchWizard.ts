import { useState, useCallback, useEffect } from 'react';
import { WizardState, WizardStepProps } from '../types/research.types';
import { ResearchMode, ResearchConfig, BlogResearchResponse } from '../../../services/blogWriterApi';

const WIZARD_STATE_KEY = 'alwrity_research_wizard_state';
const MAX_STEPS = 3; // Input (combined) -> Progress -> Results

// Default state: "General" is a placeholder that gets replaced by persona defaults on mount
// Phase 2: Backend never returns "General" - persona defaults are always hyper-personalized
// ResearchInput.tsx loads persona defaults and updates these values immediately
const defaultState: WizardState = {
  currentStep: 1,
  keywords: [],
  industry: 'General',  // Placeholder - replaced by persona defaults on mount
  targetAudience: 'General',  // Placeholder - replaced by persona defaults on mount
  researchMode: 'comprehensive' as ResearchMode,
  config: {
    mode: 'comprehensive',
    provider: 'exa',  // Phase 2: Default to Exa (primary provider)
    max_sources: 10,
    include_statistics: true,
    include_expert_quotes: true,
    include_competitors: true,
    include_trends: true,
  },
  results: null,
};

export const useResearchWizard = (
  initialKeywords?: string[], 
  initialIndustry?: string,
  initialTargetAudience?: string,
  initialResearchMode?: ResearchMode,
  initialConfig?: ResearchConfig
) => {
  const [state, setState] = useState<WizardState>(() => {
    // If initial values are provided (preset clicked), clear localStorage and use them
    if (initialKeywords || initialIndustry || initialTargetAudience || initialResearchMode || initialConfig) {
      localStorage.removeItem(WIZARD_STATE_KEY);
      return {
        ...defaultState,
        keywords: initialKeywords || [],
        industry: initialIndustry || defaultState.industry,
        targetAudience: initialTargetAudience || defaultState.targetAudience,
        researchMode: initialResearchMode || defaultState.researchMode,
        config: initialConfig || defaultState.config,
      };
    }
    
    // Try to load from localStorage only if no initial values
    const saved = localStorage.getItem(WIZARD_STATE_KEY);
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        return parsed;
      } catch (e) {
        console.warn('Failed to parse saved wizard state', e);
      }
    }
    
    // Use defaults
    return defaultState;
  });

  // Update state when initial values change (preset clicked)
  useEffect(() => {
    if (initialKeywords || initialIndustry || initialTargetAudience || initialResearchMode || initialConfig) {
      localStorage.removeItem(WIZARD_STATE_KEY);
      setState({
        ...defaultState,
        keywords: initialKeywords || [],
        industry: initialIndustry || defaultState.industry,
        targetAudience: initialTargetAudience || defaultState.targetAudience,
        researchMode: initialResearchMode || defaultState.researchMode,
        config: initialConfig || defaultState.config,
        results: null, // Clear any previous results
      });
    }
  }, [initialKeywords, initialIndustry, initialTargetAudience, initialResearchMode, initialConfig]);

  // Persist state to localStorage
  useEffect(() => {
    if (state.currentStep > 1) {
      localStorage.setItem(WIZARD_STATE_KEY, JSON.stringify(state));
    }
  }, [state]);

  const updateState = useCallback((updates: Partial<WizardState>) => {
    setState(prev => ({ ...prev, ...updates }));
  }, []);

  const nextStep = useCallback(() => {
    setState(prev => {
      if (prev.currentStep >= MAX_STEPS) return prev;
      return { ...prev, currentStep: prev.currentStep + 1 };
    });
  }, []);

  const prevStep = useCallback(() => {
    setState(prev => {
      if (prev.currentStep <= 1) return prev;
      return { ...prev, currentStep: prev.currentStep - 1 };
    });
  }, []);

  const reset = useCallback(() => {
    const resetState = {
      ...defaultState,
      keywords: initialKeywords || [],
      industry: initialIndustry || defaultState.industry,
      targetAudience: initialTargetAudience || defaultState.targetAudience,
      researchMode: initialResearchMode || defaultState.researchMode,
      config: initialConfig || defaultState.config,
    };
    setState(resetState);
    localStorage.removeItem(WIZARD_STATE_KEY);
  }, [initialKeywords, initialIndustry, initialTargetAudience, initialResearchMode, initialConfig]);

  const clearResults = useCallback(() => {
    setState(prev => ({ ...prev, results: null }));
  }, []);

  const canGoNext = useCallback((): boolean => {
    switch (state.currentStep) {
      case 1:
        return state.keywords.length > 0 && state.keywords.every(k => k.trim().length > 0);
      case 2:
        return !!state.results; // Can proceed if we have results
      case 3:
        return false; // Results is the last step
      default:
        return false;
    }
  }, [state]);

  return {
    state,
    updateState,
    nextStep,
    prevStep,
    reset,
    clearResults,
    canGoNext,
    isFirstStep: state.currentStep === 1,
    isLastStep: state.currentStep === MAX_STEPS,
    maxSteps: MAX_STEPS,
  };
};

export type UseResearchWizardReturn = ReturnType<typeof useResearchWizard>;

