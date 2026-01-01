/**
 * useIntentResearch Hook
 * 
 * React hook for managing intent-driven research flow:
 * 1. Analyze user input to understand intent
 * 2. Show quick options for user confirmation
 * 3. Execute research with confirmed intent
 * 4. Display results organized by deliverable type
 */

import { useState, useCallback } from 'react';
import { intentResearchApi } from '../../../api/intentResearchApi';
import {
  ResearchIntent,
  ResearchQuery,
  QuickOption,
  IntentDrivenResearchResponse,
  IntentWizardState,
  AnalyzeIntentResponse,
} from '../types/intent.types';

const initialState: IntentWizardState = {
  userInput: '',
  keywords: [],
  intent: null,
  suggestedQueries: [],
  selectedQueries: [],
  quickOptions: [],
  analysisSummary: '',
  suggestedKeywords: [],
  suggestedAngles: [],
  isAnalyzing: false,
  isResearching: false,
  hasConfirmedIntent: false,
  result: null,
  error: null,
};

export interface UseIntentResearchOptions {
  usePersona?: boolean;
  useCompetitorData?: boolean;
  maxSources?: number;
  includeDomains?: string[];
  excludeDomains?: string[];
  autoExecute?: boolean; // Auto-execute research after intent analysis (if high confidence)
  autoExecuteThreshold?: number; // Confidence threshold for auto-execute (default: 0.85)
}

export const useIntentResearch = (options: UseIntentResearchOptions = {}) => {
  const [state, setState] = useState<IntentWizardState>(initialState);

  const {
    usePersona = true,
    useCompetitorData = true,
    maxSources = 10,
    includeDomains = [],
    excludeDomains = [],
    autoExecute = false,
    autoExecuteThreshold = 0.85,
  } = options;

  /**
   * Analyze user input to understand research intent.
   */
  const analyzeIntent = useCallback(async (userInput: string) => {
    setState(prev => ({
      ...prev,
      userInput,
      keywords: userInput.split(' ').filter(k => k.length > 2),
      isAnalyzing: true,
      error: null,
    }));

    try {
      const response: AnalyzeIntentResponse = await intentResearchApi.analyzeIntent({
        user_input: userInput,
        keywords: userInput.split(' ').filter(k => k.length > 2),
        use_persona: usePersona,
        use_competitor_data: useCompetitorData,
      });

      if (!response.success) {
        setState(prev => ({
          ...prev,
          isAnalyzing: false,
          error: response.error_message || 'Failed to analyze intent',
        }));
        return null;
      }

      const newState: Partial<IntentWizardState> = {
        intent: response.intent,
        suggestedQueries: response.suggested_queries,
        selectedQueries: response.suggested_queries.slice(0, 5), // Select top 5 by default
        quickOptions: response.quick_options,
        analysisSummary: response.analysis_summary,
        suggestedKeywords: response.suggested_keywords,
        suggestedAngles: response.suggested_angles,
        isAnalyzing: false,
      };

      setState(prev => ({ ...prev, ...newState }));

      // Auto-execute if confidence is high enough
      if (
        autoExecute &&
        response.intent.confidence >= autoExecuteThreshold &&
        !response.intent.needs_clarification
      ) {
        // Trigger research automatically
        await executeResearchInternal(response.intent, response.suggested_queries.slice(0, 5));
      }

      return response;
    } catch (error: any) {
      setState(prev => ({
        ...prev,
        isAnalyzing: false,
        error: error.message || 'Failed to analyze intent',
      }));
      return null;
    }
  }, [usePersona, useCompetitorData, autoExecute, autoExecuteThreshold]);

  /**
   * Update a quick option value.
   */
  const updateQuickOption = useCallback((optionId: string, newValue: any) => {
    setState(prev => {
      if (!prev.intent) return prev;

      // Update intent based on option
      const updatedIntent = { ...prev.intent };

      switch (optionId) {
        case 'purpose':
          updatedIntent.purpose = newValue;
          break;
        case 'content_output':
          updatedIntent.content_output = newValue;
          break;
        case 'deliverables':
          updatedIntent.expected_deliverables = newValue;
          break;
        case 'depth':
          updatedIntent.depth = newValue;
          break;
      }

      return {
        ...prev,
        intent: updatedIntent,
        quickOptions: prev.quickOptions.map(opt =>
          opt.id === optionId ? { ...opt, value: newValue } : opt
        ),
      };
    });
  }, []);

  /**
   * Toggle a query selection.
   */
  const toggleQuerySelection = useCallback((query: ResearchQuery) => {
    setState(prev => {
      const isSelected = prev.selectedQueries.some(q => q.query === query.query);
      
      return {
        ...prev,
        selectedQueries: isSelected
          ? prev.selectedQueries.filter(q => q.query !== query.query)
          : [...prev.selectedQueries, query],
      };
    });
  }, []);

  /**
   * Confirm intent and execute research.
   */
  const confirmAndExecute = useCallback(async () => {
    if (!state.intent) {
      setState(prev => ({ ...prev, error: 'No intent to confirm' }));
      return null;
    }

    return executeResearchInternal(state.intent, state.selectedQueries);
  }, [state.intent, state.selectedQueries]);

  /**
   * Internal research execution.
   */
  const executeResearchInternal = async (
    intent: ResearchIntent,
    queries: ResearchQuery[]
  ): Promise<IntentDrivenResearchResponse | null> => {
    setState(prev => ({
      ...prev,
      isResearching: true,
      hasConfirmedIntent: true,
      error: null,
    }));

    try {
      const response = await intentResearchApi.executeIntentResearch({
        user_input: state.userInput || intent.original_input,
        confirmed_intent: intent,
        selected_queries: queries,
        max_sources: maxSources,
        include_domains: includeDomains,
        exclude_domains: excludeDomains,
        skip_inference: true,
      });

      if (!response.success) {
        setState(prev => ({
          ...prev,
          isResearching: false,
          error: response.error_message || 'Research failed',
        }));
        return null;
      }

      setState(prev => ({
        ...prev,
        isResearching: false,
        result: response,
      }));

      return response;
    } catch (error: any) {
      setState(prev => ({
        ...prev,
        isResearching: false,
        error: error.message || 'Research failed',
      }));
      return null;
    }
  };

  /**
   * Quick research - analyze and execute in one step.
   * Skips user confirmation.
   */
  const quickResearch = useCallback(async (userInput: string) => {
    setState(prev => ({
      ...prev,
      userInput,
      isAnalyzing: true,
      isResearching: true,
      error: null,
    }));

    try {
      const response = await intentResearchApi.quickIntentResearch(userInput, {
        usePersona,
        useCompetitorData,
        maxSources,
        includeDomains,
        excludeDomains,
      });

      setState(prev => ({
        ...prev,
        isAnalyzing: false,
        isResearching: false,
        result: response,
        intent: response.intent,
        hasConfirmedIntent: true,
        error: response.success ? null : response.error_message,
      }));

      return response;
    } catch (error: any) {
      setState(prev => ({
        ...prev,
        isAnalyzing: false,
        isResearching: false,
        error: error.message || 'Research failed',
      }));
      return null;
    }
  }, [usePersona, useCompetitorData, maxSources, includeDomains, excludeDomains]);

  /**
   * Reset to initial state.
   */
  const reset = useCallback(() => {
    setState(initialState);
  }, []);

  /**
   * Clear just the results.
   */
  const clearResults = useCallback(() => {
    setState(prev => ({
      ...prev,
      result: null,
      hasConfirmedIntent: false,
    }));
  }, []);

  return {
    // State
    state,
    
    // Derived state
    isLoading: state.isAnalyzing || state.isResearching,
    hasIntent: state.intent !== null,
    hasResults: state.result !== null,
    needsConfirmation: state.intent?.needs_clarification || false,
    confidence: state.intent?.confidence || 0,
    
    // Actions
    analyzeIntent,
    updateQuickOption,
    toggleQuerySelection,
    confirmAndExecute,
    quickResearch,
    reset,
    clearResults,
  };
};

export default useIntentResearch;
