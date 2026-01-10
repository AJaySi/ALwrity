/**
 * Intent-Driven Research API Client
 * 
 * Client for the new intent-driven research endpoints:
 * - /api/research/intent/analyze - Analyze user intent
 * - /api/research/intent/research - Execute intent-driven research
 */

import { apiClient, aiApiClient } from './client';
import {
  AnalyzeIntentRequest,
  AnalyzeIntentResponse,
  IntentDrivenResearchRequest,
  IntentDrivenResearchResponse,
  ResearchIntent,
} from '../components/Research/types/intent.types';
import { WizardState } from '../components/Research/types/research.types';
import { BlogResearchResponse } from '../services/blogWriterApi';

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
        also_answering: [],
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

/**
 * Save research project to Asset Library.
 * 
 * Saves the complete research project state so users can resume later.
 */
export const saveResearchProject = async (
  state: WizardState,
  options?: {
    intentAnalysis?: AnalyzeIntentResponse | null;
    confirmedIntent?: ResearchIntent | null;
    intentResult?: IntentDrivenResearchResponse | null;
    legacyResult?: BlogResearchResponse | null;
    title?: string;
    description?: string;
    projectId?: string; // Project ID for updates (optional)
  }
): Promise<{ success: boolean; asset_id?: number; project_id?: string; message: string }> => {
  try {
    // Generate project title from keywords if not provided
    const projectTitle = options?.title || 
      (state.keywords.length > 0 
        ? `Research: ${state.keywords.slice(0, 3).join(', ')}`
        : 'Research Project');

    // Generate description if not provided
    const projectDescription = options?.description ||
      `Research project on ${state.keywords.join(', ')}. ` +
      `Industry: ${state.industry}, Target Audience: ${state.targetAudience}`;

    const request = {
      project_id: options?.projectId || undefined, // Include project_id for updates
      title: projectTitle,
      keywords: state.keywords,
      industry: state.industry,
      target_audience: state.targetAudience,
      research_mode: state.researchMode,
      config: state.config,
      intent_analysis: options?.intentAnalysis ? {
        success: options.intentAnalysis.success,
        intent: options.intentAnalysis.intent,
        analysis_summary: options.intentAnalysis.analysis_summary,
        suggested_queries: options.intentAnalysis.suggested_queries,
        suggested_keywords: options.intentAnalysis.suggested_keywords,
        suggested_angles: options.intentAnalysis.suggested_angles,
        quick_options: options.intentAnalysis.quick_options,
        trends_config: options.intentAnalysis.trends_config,
      } : null,
      confirmed_intent: options?.confirmedIntent || null,
      intent_result: options?.intentResult ? {
        success: options.intentResult.success,
        primary_answer: options.intentResult.primary_answer,
        secondary_answers: options.intentResult.secondary_answers,
        statistics: options.intentResult.statistics,
        expert_quotes: options.intentResult.expert_quotes,
        case_studies: options.intentResult.case_studies,
        trends: options.intentResult.trends,
        comparisons: options.intentResult.comparisons,
        best_practices: options.intentResult.best_practices,
        step_by_step: options.intentResult.step_by_step,
        pros_cons: options.intentResult.pros_cons,
        definitions: options.intentResult.definitions,
        examples: options.intentResult.examples,
        predictions: options.intentResult.predictions,
        executive_summary: options.intentResult.executive_summary,
        key_takeaways: options.intentResult.key_takeaways,
        suggested_outline: options.intentResult.suggested_outline,
        sources: options.intentResult.sources,
        confidence: options.intentResult.confidence,
        gaps_identified: options.intentResult.gaps_identified,
        follow_up_queries: options.intentResult.follow_up_queries,
        intent: options.intentResult.intent,
        google_trends_data: options.intentResult.google_trends_data,
      } : null,
      legacy_result: options?.legacyResult || null,
      current_step: state.currentStep,
      description: projectDescription,
    };

    const { data } = await apiClient.post<{ success: boolean; asset_id?: number; project_id?: string; message: string }>(
      '/api/research/projects/save',
      request
    );
    
    // After saving project, also save to ContentAsset library (following podcast maker pattern)
    if (data.success && data.project_id) {
      try {
        await saveResearchProjectToAssetLibrary({
          projectId: data.project_id,
          title: projectTitle,
          description: projectDescription,
          keywords: state.keywords,
          industry: state.industry,
          targetAudience: state.targetAudience,
          researchMode: state.researchMode,
          config: state.config,
          status: (options?.intentResult || options?.legacyResult) ? 'completed' : (options?.intentAnalysis ? 'draft' : 'draft'),
          currentStep: state.currentStep,
        });
        console.log(`[intentResearchApi] ✅ Research project saved to asset library: project_id=${data.project_id}, status=${(options?.intentResult || options?.legacyResult) ? 'completed' : 'draft'}`);
      } catch (error) {
        console.warn('[intentResearchApi] Failed to save research project to asset library:', error);
        // Don't fail the whole operation if asset creation fails
      }
    }
    
    return data;
  } catch (error: any) {
    console.error('[intentResearchApi] saveResearchProject failed:', error);
    return {
      success: false,
      message: error.message || 'Failed to save research project',
    };
  }
};

/**
 * Save research project to Asset Library (ContentAsset).
 * Following podcast maker pattern: podcastApi.saveAudioToAssetLibrary()
 */
/**
 * Save research project to Asset Library (ContentAsset).
 * Following podcast maker pattern: podcastApi.saveAudioToAssetLibrary()
 * 
 * Checks for existing asset with same project_id and updates it, otherwise creates new one.
 */
export const saveResearchProjectToAssetLibrary = async (params: {
  projectId: string;
  title: string;
  description?: string;
  keywords: string[];
  industry?: string;
  targetAudience?: string;
  researchMode?: string;
  config?: any;
  status?: string;
  currentStep?: number;
}): Promise<{ assetId: number }> => {
  try {
    const fileUrl = `/api/research/projects/${params.projectId}/export`;
    const assetMetadata = {
      project_type: 'research_project',
      project_id: params.projectId,
      status: params.status || 'draft',
      keywords: params.keywords,
      industry: params.industry,
      target_audience: params.targetAudience,
      research_mode: params.researchMode,
      current_step: params.currentStep || 1,
    };

    // Check if asset already exists for this project_id
    try {
      const searchResponse = await aiApiClient.get('/api/content-assets/', {
        params: {
          asset_type: 'text',
          source_module: 'research_tools',
          search: params.projectId,
          limit: 100,
        },
      });

      // Find existing asset with matching project_id in metadata
      const existingAsset = searchResponse.data.assets?.find(
        (asset: any) => 
          asset.asset_metadata?.project_type === 'research_project' &&
          asset.asset_metadata?.project_id === params.projectId
      );

      if (existingAsset) {
        // Update existing asset
        const updateResponse = await aiApiClient.put(`/api/content-assets/${existingAsset.id}`, {
          title: params.title,
          description: params.description || `Research project on ${params.keywords.slice(0, 3).join(', ')}`,
          tags: ['research', 'research_project', params.projectId, ...params.keywords.slice(0, 5)],
          asset_metadata: assetMetadata,
        });
        console.log(`[intentResearchApi] Updated existing ContentAsset for project ${params.projectId}: asset_id=${existingAsset.id}`);
        return { assetId: updateResponse.data.id };
      }
    } catch (searchError) {
      console.warn('[intentResearchApi] Failed to search for existing asset, creating new one:', searchError);
      // Continue to create new asset if search fails
    }

    // Create new asset if none exists
    const response = await aiApiClient.post('/api/content-assets/', {
      asset_type: 'text',
      source_module: 'research_tools',
      filename: `research_${params.projectId}.json`,
      file_url: fileUrl,
      title: params.title,
      description: params.description || `Research project on ${params.keywords.slice(0, 3).join(', ')}`,
      tags: ['research', 'research_project', params.projectId, ...params.keywords.slice(0, 5)],
      asset_metadata: assetMetadata,
      cost: 0,
      mime_type: 'application/json',
    });
    console.log(`[intentResearchApi] ✅ Created new ContentAsset for project ${params.projectId}: asset_id=${response.data.id}, status=${params.status || 'draft'}, source_module=research_tools, asset_type=text`);
    return { assetId: response.data.id };
  } catch (error: any) {
    console.error('[intentResearchApi] saveResearchProjectToAssetLibrary failed:', error);
    throw error;
  }
};

/**
 * List research projects.
 */
export const listResearchProjects = async (params?: {
  status?: string;
  is_favorite?: boolean;
  limit?: number;
  offset?: number;
}): Promise<{ projects: any[]; total: number; limit: number; offset: number }> => {
  try {
    const { data } = await apiClient.get<{ projects: any[]; total: number; limit: number; offset: number }>(
      '/api/research/projects',
      { params }
    );
    return data;
  } catch (error: any) {
    console.error('[intentResearchApi] listResearchProjects failed:', error);
    return {
      projects: [],
      total: 0,
      limit: params?.limit || 50,
      offset: params?.offset || 0,
    };
  }
};

/**
 * Get a single research project by ID.
 */
export const getResearchProject = async (projectId: string): Promise<any> => {
  try {
    const { data } = await apiClient.get(`/api/research/projects/${projectId}`);
    return data;
  } catch (error: any) {
    console.error('[intentResearchApi] getResearchProject failed:', error);
    throw error;
  }
};

/**
 * Delete a research project.
 */
export const deleteResearchProject = async (projectId: string): Promise<void> => {
  try {
    await apiClient.delete(`/api/research/projects/${projectId}`);
  } catch (error: any) {
    console.error('[intentResearchApi] deleteResearchProject failed:', error);
    throw error;
  }
};

/**
 * Toggle favorite status of a research project.
 */
export const toggleResearchProjectFavorite = async (projectId: string): Promise<any> => {
  try {
    // First get the project to check current favorite status
    const project = await getResearchProject(projectId);
    const newFavoriteStatus = !project.is_favorite;
    
    // Update the project with new favorite status
    const { data } = await apiClient.put(`/api/research/projects/${projectId}`, {
      is_favorite: newFavoriteStatus,
    });
    return data;
  } catch (error: any) {
    console.error('[intentResearchApi] toggleResearchProjectFavorite failed:', error);
    throw error;
  }
};

export const intentResearchApi = {
  analyzeIntent,
  executeIntentResearch,
  quickIntentResearch,
  saveResearchProject,
  saveResearchProjectToAssetLibrary,
  listResearchProjects,
  getResearchProject,
  deleteResearchProject,
  toggleResearchProjectFavorite,
};

export default intentResearchApi;
