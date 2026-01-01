/**
 * Intent-Driven Research API Client
 * 
 * Client for the new intent-driven research endpoints:
 * - /api/research/intent/analyze - Analyze user intent
 * - /api/research/intent/research - Execute intent-driven research
 */

import { apiClient } from './client';
import {
  AnalyzeIntentRequest,
  AnalyzeIntentResponse,
  IntentDrivenResearchRequest,
  IntentDrivenResearchResponse,
} from '../components/Research/types/intent.types';

/**
 * Analyze user input to understand research intent.
 * 
 * Uses AI to infer:
 * - What questions need answering
 * - What deliverables user expects (statistics, quotes, case studies)
 * - What depth and focus is appropriate
 */
export const analyzeIntent = async (
  request: AnalyzeIntentRequest
): Promise<AnalyzeIntentResponse> => {
  try {
    const { data } = await apiClient.post<AnalyzeIntentResponse>(
      '/api/research/intent/analyze',
      request
    );
    return data;
  } catch (error: any) {
    console.error('[intentResearchApi] analyzeIntent failed:', error);
    return {
      success: false,
      intent: {
        primary_question: request.user_input,
        secondary_questions: [],
        purpose: 'learn',
        content_output: 'general',
        expected_deliverables: ['key_statistics'],
        depth: 'detailed',
        focus_areas: [],
        perspective: null,
        time_sensitivity: null,
        input_type: 'keywords',
        original_input: request.user_input,
        confidence: 0.5,
        needs_clarification: true,
        clarifying_questions: [],
      },
      analysis_summary: 'Failed to analyze intent',
      suggested_queries: [],
      suggested_keywords: [],
      suggested_angles: [],
      quick_options: [],
      error_message: error.message || 'Failed to analyze intent',
    };
  }
};

/**
 * Execute research based on user intent.
 * 
 * This is the main endpoint for intent-driven research. It:
 * 1. Uses the confirmed intent (or infers from user_input)
 * 2. Generates targeted queries for each expected deliverable
 * 3. Executes research using Exa/Tavily/Google
 * 4. Analyzes results through the lens of user intent
 * 5. Returns exactly what the user needs
 */
export const executeIntentResearch = async (
  request: IntentDrivenResearchRequest
): Promise<IntentDrivenResearchResponse> => {
  try {
    const { data } = await apiClient.post<IntentDrivenResearchResponse>(
      '/api/research/intent/research',
      request
    );
    return data;
  } catch (error: any) {
    console.error('[intentResearchApi] executeIntentResearch failed:', error);
    return {
      success: false,
      primary_answer: '',
      secondary_answers: {},
      statistics: [],
      expert_quotes: [],
      case_studies: [],
      trends: [],
      comparisons: [],
      best_practices: [],
      step_by_step: [],
      pros_cons: null,
      definitions: {},
      examples: [],
      predictions: [],
      executive_summary: '',
      key_takeaways: [],
      suggested_outline: [],
      sources: [],
      confidence: 0,
      gaps_identified: [],
      follow_up_queries: [],
      intent: null,
      error_message: error.message || 'Research failed',
    };
  }
};

/**
 * Combined function to analyze intent and execute research in one call.
 * 
 * For simple use cases where user doesn't need to confirm intent.
 */
export const quickIntentResearch = async (
  userInput: string,
  options?: {
    usePersona?: boolean;
    useCompetitorData?: boolean;
    maxSources?: number;
    includeDomains?: string[];
    excludeDomains?: string[];
  }
): Promise<IntentDrivenResearchResponse> => {
  try {
    // First analyze intent
    const analyzeResponse = await analyzeIntent({
      user_input: userInput,
      keywords: userInput.split(' ').filter(k => k.length > 2),
      use_persona: options?.usePersona ?? true,
      use_competitor_data: options?.useCompetitorData ?? true,
    });

    if (!analyzeResponse.success) {
      return {
        success: false,
        primary_answer: '',
        secondary_answers: {},
        statistics: [],
        expert_quotes: [],
        case_studies: [],
        trends: [],
        comparisons: [],
        best_practices: [],
        step_by_step: [],
        pros_cons: null,
        definitions: {},
        examples: [],
        predictions: [],
        executive_summary: '',
        key_takeaways: [],
        suggested_outline: [],
        sources: [],
        confidence: 0,
        gaps_identified: [],
        follow_up_queries: [],
        intent: null,
        error_message: analyzeResponse.error_message || 'Failed to analyze intent',
      };
    }

    // Execute research with inferred intent
    return await executeIntentResearch({
      user_input: userInput,
      confirmed_intent: analyzeResponse.intent,
      selected_queries: analyzeResponse.suggested_queries.slice(0, 5), // Top 5 queries
      max_sources: options?.maxSources ?? 10,
      include_domains: options?.includeDomains ?? [],
      exclude_domains: options?.excludeDomains ?? [],
      skip_inference: true, // We already have intent
    });
  } catch (error: any) {
    console.error('[intentResearchApi] quickIntentResearch failed:', error);
    return {
      success: false,
      primary_answer: '',
      secondary_answers: {},
      statistics: [],
      expert_quotes: [],
      case_studies: [],
      trends: [],
      comparisons: [],
      best_practices: [],
      step_by_step: [],
      pros_cons: null,
      definitions: {},
      examples: [],
      predictions: [],
      executive_summary: '',
      key_takeaways: [],
      suggested_outline: [],
      sources: [],
      confidence: 0,
      gaps_identified: [],
      follow_up_queries: [],
      intent: null,
      error_message: error.message || 'Research failed',
    };
  }
};

export const intentResearchApi = {
  analyzeIntent,
  executeIntentResearch,
  quickIntentResearch,
};

export default intentResearchApi;
