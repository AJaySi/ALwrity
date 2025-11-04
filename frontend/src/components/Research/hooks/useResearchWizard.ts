import { useState, useCallback, useEffect } from 'react';
import { WizardState, WizardStepProps } from '../types/research.types';
import { ResearchMode, ResearchConfig, BlogResearchResponse } from '../../../services/blogWriterApi';

const WIZARD_STATE_KEY = 'alwrity_research_wizard_state';
const MAX_STEPS = 3; // Input (combined) -> Progress -> Results

const defaultState: WizardState = {
  currentStep: 1,
  keywords: [],
  industry: 'General',
  targetAudience: 'General',
  researchMode: 'basic' as ResearchMode,
  config: {
    mode: 'basic',
    provider: 'google',
    max_sources: 10,
    include_statistics: true,
    include_expert_quotes: true,
    include_competitors: true,
    include_trends: true,
  },
  results: null,
};

export const useResearchWizard = (initialKeywords?: string[], initialIndustry?: string) => {
  const [state, setState] = useState<WizardState>(() => {
    // Try to load from localStorage first
    const saved = localStorage.getItem(WIZARD_STATE_KEY);
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        return parsed;
      } catch (e) {
        console.warn('Failed to parse saved wizard state', e);
      }
    }
    
    // Use defaults or initial values
    return {
      ...defaultState,
      keywords: initialKeywords || [],
      industry: initialIndustry || defaultState.industry,
    };
  });

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
    };
    setState(resetState);
    localStorage.removeItem(WIZARD_STATE_KEY);
  }, [initialKeywords, initialIndustry]);

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

