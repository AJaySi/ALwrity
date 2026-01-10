import { useState, useCallback, useEffect } from 'react';
import { researchCache } from '../../../services/researchCache';
import { WizardState } from '../types/research.types';
import { researchEngineApi, ResearchEngineRequest } from '../../../services/researchEngineApi';
import { useResearchPolling } from '../../../hooks/usePolling';
import { intentResearchApi } from '../../../api/intentResearchApi';
import {
  ResearchIntent, 
  IntentDrivenResearchResponse,
  AnalyzeIntentResponse,
  ResearchQuery,
} from '../types/intent.types';
import { autoSaveDraft, restoreDraft } from '../../../utils/researchDraftManager';

export const useResearchExecution = () => {
  const [isExecuting, setIsExecuting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  
  // Intent-driven research state
  const [isAnalyzingIntent, setIsAnalyzingIntent] = useState(false);
  const [intentAnalysis, setIntentAnalysis] = useState<AnalyzeIntentResponse | null>(null);
  const [confirmedIntent, setConfirmedIntent] = useState<ResearchIntent | null>(null);
  const [intentResult, setIntentResult] = useState<IntentDrivenResearchResponse | null>(null);
  const [useIntentMode, setUseIntentMode] = useState(true); // Enable by default
  
  // Restore intent analysis and confirmed intent from draft on mount
  useEffect(() => {
    const draft = restoreDraft();
    if (draft) {
      if (draft.intent_analysis) {
        setIntentAnalysis(draft.intent_analysis);
        console.log('[useResearchExecution] 🔄 Restored intent analysis from draft');
      }
      if (draft.confirmed_intent) {
        setConfirmedIntent(draft.confirmed_intent);
        console.log('[useResearchExecution] 🔄 Restored confirmed intent from draft');
      }
      if (draft.intent_result) {
        setIntentResult(draft.intent_result);
        console.log('[useResearchExecution] 🔄 Restored intent result from draft');
      }
    }
  }, []);

  const polling = useResearchPolling({
    onComplete: (result) => {
      if (result && result.keywords) {
        researchCache.cacheResult(
          result.keywords,
          'General',
          'General',
          result
        );
      }
      setIsExecuting(false);
      setResult(result);
    },
    onError: (error) => {
      console.error('Research polling error:', error);
      setError(error);
      setIsExecuting(false);
    }
  });

  const executeResearch = useCallback(async (state: WizardState): Promise<string | null> => {
    setIsExecuting(true);
    setError(null);

    try {
      // Check cache first
      const cachedResult = researchCache.getCachedResult(
        state.keywords,
        state.industry,
        state.targetAudience
      );
      
      if (cachedResult) {
        setIsExecuting(false);
        setResult(cachedResult);
        return 'cached';
      }

      // Build Research Engine request (tool-agnostic)
      const payload: ResearchEngineRequest = {
        query: state.keywords.join(' ') || 'research',
        keywords: state.keywords,
        goal: 'factual',
        depth: state.researchMode === 'basic' ? 'standard' : state.researchMode === 'comprehensive' ? 'comprehensive' : 'standard',
        provider: state.config.provider || 'auto',
        content_type: 'blog',
        industry: state.industry,
        target_audience: state.targetAudience,
        max_sources: state.config.max_sources,
        recency: state.config.tavily_time_range,
        include_domains: state.config.exa_include_domains || state.config.tavily_include_domains,
        exclude_domains: state.config.exa_exclude_domains || state.config.tavily_exclude_domains,
        advanced_mode: true, // expose raw params if provided
        // Exa params
        exa_category: state.config.exa_category,
        exa_search_type: state.config.exa_search_type,
        // Tavily params
        tavily_topic: state.config.tavily_topic,
        tavily_search_depth: state.config.tavily_search_depth,
        tavily_include_answer: state.config.tavily_include_answer,
        tavily_include_raw_content: state.config.tavily_include_raw_content,
        tavily_time_range: state.config.tavily_time_range,
        tavily_country: state.config.tavily_country,
        config: state.config, // keep compatibility
      };

      // For fast smoke tests: use synchronous path when basic mode
      if (state.researchMode === 'basic') {
        const syncResult = await researchEngineApi.execute(payload);
        // Cache and surface immediately
        researchCache.cacheResult(
          state.keywords,
          state.industry,
          state.targetAudience,
          syncResult
        );
        setResult(syncResult);
        setIsExecuting(false);
        return 'sync';
      }

      // Start async research to reuse existing progress step
      const { task_id } = await researchEngineApi.start(payload);
      polling.startPolling(task_id);
      return task_id;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      setIsExecuting(false);
      return null;
    }
  }, [polling]);

  const stopExecution = useCallback(() => {
    polling.stopPolling();
    setIsExecuting(false);
    setError(null);
  }, [polling]);

  /**
   * Analyze user input to understand research intent.
   * Call this before executeResearch to show intent confirmation.
   */
  const analyzeIntent = useCallback(async (state: WizardState): Promise<AnalyzeIntentResponse | null> => {
    setIsAnalyzingIntent(true);
    setError(null);
    setIntentAnalysis(null);
    setConfirmedIntent(null);

    try {
      const userInput = state.keywords.join(' ');
      if (!userInput.trim()) {
        setError('Please enter keywords or a research topic');
        setIsAnalyzingIntent(false);
        return null;
      }

      const response = await intentResearchApi.analyzeIntent({
        user_input: userInput,
        keywords: state.keywords,
        use_persona: true,
        use_competitor_data: true,
        user_provided_purpose: state.userPurpose,
        user_provided_content_output: state.userContentOutput,
        user_provided_depth: state.userDepth,
      });

      if (!response.success) {
        const errorMsg = response.error_message || 'Failed to analyze intent';
        setError(errorMsg);
        setIsAnalyzingIntent(false);
        return response; // Return response even if failed so UI can show error
      }

      setIntentAnalysis(response);
      
      // Auto-confirm if confidence is high and no clarification needed
      if (response.intent.confidence >= 0.85 && !response.intent.needs_clarification) {
        setConfirmedIntent(response.intent);
      }

      // Save draft with intent analysis
      autoSaveDraft(state, {
        intentAnalysis: response,
        confirmedIntent: response.intent.confidence >= 0.85 && !response.intent.needs_clarification ? response.intent : undefined,
      }).catch(error => {
        console.warn('[useResearchExecution] Failed to save draft after intent analysis:', error);
      });

      setIsAnalyzingIntent(false);
      return response;
    } catch (err: any) {
      console.error('[useResearchExecution] analyzeIntent error:', err);
      let errorMessage = 'Failed to analyze intent';
      
      if (err.response) {
        // HTTP error response
        if (err.response.status === 404) {
          errorMessage = 'Smart Research endpoint not found. The feature may not be available yet. Please use the regular research flow.';
        } else if (err.response.status === 401) {
          errorMessage = 'Authentication required. Please log in again.';
        } else if (err.response.status >= 500) {
          errorMessage = 'Server error. Please try again later.';
        } else {
          errorMessage = err.response.data?.detail || err.response.data?.error_message || `Server error: ${err.response.status}`;
        }
      } else if (err.request) {
        // Network error
        errorMessage = 'Network error. Please check your connection and try again.';
      } else {
        errorMessage = err.message || 'Unknown error occurred';
      }
      
      setError(errorMessage);
      setIsAnalyzingIntent(false);
      
      // Return a failed response so UI can show the error
      return {
        success: false,
        intent: {
          primary_question: state.keywords.join(' '),
          secondary_questions: [],
          purpose: 'learn',
          content_output: 'general',
          expected_deliverables: ['key_statistics'],
          depth: 'detailed',
          focus_areas: [],
          also_answering: [],
          perspective: null,
          time_sensitivity: null,
          input_type: 'keywords',
          original_input: state.keywords.join(' '),
          confidence: 0,
          needs_clarification: true,
          clarifying_questions: [],
        },
        analysis_summary: '',
        suggested_queries: [],
        suggested_keywords: [],
        suggested_angles: [],
        quick_options: [],
        error_message: errorMessage,
      };
    }
  }, []);

  /**
   * Confirm the analyzed intent (possibly with user modifications).
   */
  const confirmIntent = useCallback((intent: ResearchIntent, state?: WizardState) => {
    setConfirmedIntent(intent);
    
    // Save draft with confirmed intent
    if (state) {
      autoSaveDraft(state, {
        intentAnalysis: intentAnalysis || undefined,
        confirmedIntent: intent,
      }).catch(error => {
        console.warn('[useResearchExecution] Failed to save draft after intent confirmation:', error);
      });
    }
  }, [intentAnalysis]);

  /**
   * Update a specific field in the analyzed intent.
   */
  const updateIntentField = useCallback(<K extends keyof ResearchIntent>(
    field: K,
    value: ResearchIntent[K]
  ) => {
    if (intentAnalysis?.intent) {
      const updatedIntent = { ...intentAnalysis.intent, [field]: value };
      setIntentAnalysis({
        ...intentAnalysis,
        intent: updatedIntent,
      });
    }
  }, [intentAnalysis]);

  /**
   * Execute research using intent-driven approach.
   */
  const executeIntentResearch = useCallback(async (
    state: WizardState,
    selectedQueries?: ResearchQuery[]
  ): Promise<IntentDrivenResearchResponse | null> => {
    // First analyze intent if not already done
    let intent = confirmedIntent;
    if (!intent) {
      const analysis = await analyzeIntent(state);
      if (!analysis?.success) {
        return null;
      }
      intent = analysis.intent;
    }

    setIsExecuting(true);
    setError(null);

    try {
      // Use provided queries or fall back to intent analysis queries
      const queriesToUse = selectedQueries || intentAnalysis?.suggested_queries?.slice(0, 5) || [];
      
      const response = await intentResearchApi.executeIntentResearch({
        user_input: state.keywords.join(' '),
        confirmed_intent: intent,
        selected_queries: queriesToUse.map(q => ({
          query: q.query,
          purpose: q.purpose,
          provider: q.provider,
          priority: q.priority,
          expected_results: q.expected_results,
        })),
        max_sources: state.config.max_sources || 10,
        include_domains: state.config.exa_include_domains || state.config.tavily_include_domains || [],
        exclude_domains: state.config.exa_exclude_domains || state.config.tavily_exclude_domains || [],
        trends_config: intentAnalysis?.trends_config, // Include Google Trends configuration
        skip_inference: true,
      });

      if (!response.success) {
        setError(response.error_message || 'Research failed');
        setIsExecuting(false);
        return null;
      }

      setIntentResult(response);
      
      // Save draft with research results
      autoSaveDraft(state, {
        intentAnalysis: intentAnalysis || undefined,
        confirmedIntent: intent,
        intentResult: response,
      }).catch(error => {
        console.warn('[useResearchExecution] Failed to save draft after research completion:', error);
      });
      
      // Also set the legacy result for backward compatibility with StepResults
      // Transform intent result to match the expected format
      const legacyResult = {
        success: true,
        sources: response.sources.map(s => ({
          title: s.title,
          url: s.url,
          excerpt: s.excerpt ?? undefined, // Convert null to undefined
          credibility_score: s.credibility_score,
        })),
        keyword_analysis: {
          primary_keywords: state.keywords,
          secondary: response.suggested_outline,
        },
        competitor_analysis: {},
        suggested_angles: response.key_takeaways,
        search_queries: [],
        // Add intent-specific data for enhanced display
        intent_result: response,
      };
      
      setResult(legacyResult);
      setIsExecuting(false);
      
      // Cache the result
      researchCache.cacheResult(
        state.keywords,
        state.industry,
        state.targetAudience,
        legacyResult
      );
      
      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Research failed';
      setError(errorMessage);
      setIsExecuting(false);
      return null;
    }
  }, [confirmedIntent, intentAnalysis, analyzeIntent]);

  /**
   * Clear intent analysis state.
   */
  const clearIntent = useCallback(() => {
    setIntentAnalysis(null);
    setConfirmedIntent(null);
    setIntentResult(null);
  }, []);

  return {
    // Legacy API
    executeResearch,
    stopExecution,
    isExecuting,
    error,
    progressMessages: polling.progressMessages,
    currentStatus: polling.currentStatus,
    result: result ?? polling.result,
    
    // Intent-driven API
    useIntentMode,
    setUseIntentMode,
    isAnalyzingIntent,
    intentAnalysis,
    confirmedIntent,
    intentResult,
    analyzeIntent,
    confirmIntent,
    updateIntentField,
    executeIntentResearch,
    clearIntent,
  };
};

