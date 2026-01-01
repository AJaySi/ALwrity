/**
 * Research Configuration API
 * Fetches provider availability and persona-aware defaults
 */

import { ResearchMode, ResearchProvider } from '../services/blogWriterApi';
import { apiClient } from './client';

export interface ProviderAvailability {
  google_available: boolean;
  exa_available: boolean;
  tavily_available: boolean;
  gemini_key_status: 'configured' | 'missing';
  exa_key_status: 'configured' | 'missing';
  tavily_key_status: 'configured' | 'missing';
}

export interface PersonaDefaults {
  industry?: string;
  target_audience?: string;
  suggested_domains: string[];
  suggested_exa_category?: string;
  has_research_persona?: boolean;  // Phase 2: Indicates if research persona exists
  
  // Phase 2: Additional fields for pre-filling advanced options
  default_research_mode?: string;  // basic, comprehensive, targeted
  default_provider?: string;  // exa, tavily, google
  suggested_keywords?: string[];  // For keyword suggestions
  research_angles?: string[];  // Alternative research focuses

  // Phase 2+: Enhanced provider-specific defaults from research persona
  suggested_exa_search_type?: string;  // auto, neural, keyword, fast, deep
  suggested_tavily_topic?: string;  // general, news, finance
  suggested_tavily_search_depth?: string;  // basic, advanced, fast, ultra-fast
  suggested_tavily_include_answer?: string;  // false, basic, advanced
  suggested_tavily_time_range?: string;  // day, week, month, year
  suggested_tavily_raw_content_format?: string;  // false, markdown, text
  provider_recommendations?: Record<string, string>;  // Use case -> provider mapping
}

export interface ResearchPreset {
  name: string;
  keywords: string;
  industry: string;
  target_audience: string;
  research_mode: ResearchMode;
  config: any; // ResearchConfig
  description?: string;
  icon?: string;
}

export interface ResearchPersona {
  default_industry: string;
  default_target_audience: string;
  default_research_mode: ResearchMode;
  default_provider: ResearchProvider;
  suggested_keywords: string[];
  keyword_expansion_patterns: Record<string, string[]>;
  suggested_exa_domains: string[];
  suggested_exa_category?: string;
  suggested_exa_search_type?: string;
  suggested_tavily_topic?: string;
  suggested_tavily_search_depth?: string;
  suggested_tavily_include_answer?: string;
  suggested_tavily_time_range?: string;
  suggested_tavily_raw_content_format?: string;
  provider_recommendations?: Record<string, string>;
  research_angles: string[];
  query_enhancement_rules: Record<string, string>;
  recommended_presets: ResearchPreset[];
  research_preferences: Record<string, any>;
  generated_at?: string;
  confidence_score?: number;
  version?: string;
}

export interface ResearchConfigResponse {
  provider_availability: ProviderAvailability;
  persona_defaults: PersonaDefaults;
  research_persona?: ResearchPersona;
  onboarding_completed?: boolean;
  persona_scheduled?: boolean;
}

/**
 * Get provider availability status
 */
export const getProviderAvailability = async (): Promise<ProviderAvailability> => {
  try {
    const response = await apiClient.get('/api/research/providers/status');
    const data = response.data || {};
    return {
      google_available: !!data.google?.available,
      exa_available: !!data.exa?.available,
      tavily_available: !!data.tavily?.available,
      gemini_key_status: data.google?.available ? 'configured' : 'missing',
      exa_key_status: data.exa?.available ? 'configured' : 'missing',
      tavily_key_status: data.tavily?.available ? 'configured' : 'missing',
    };
  } catch (error: any) {
    console.error('[researchConfig] Error getting provider availability:', error);
    throw new Error(`Failed to get provider availability: ${error?.response?.statusText || error.message}`);
  }
};

/**
 * Get persona-aware research defaults
 */
export const getPersonaDefaults = async (): Promise<PersonaDefaults> => {
  try {
    const response = await apiClient.get('/api/research/persona-defaults');
    return response.data;
  } catch (error: any) {
    console.error('[researchConfig] Error getting persona defaults:', error);
    throw new Error(`Failed to get persona defaults: ${error?.response?.statusText || error.message}`);
  }
};

// Request deduplication: cache in-flight requests to prevent duplicate API calls
let pendingConfigRequest: Promise<ResearchConfigResponse> | null = null;

/**
 * Get complete research configuration
 * 
 * Uses request deduplication: if multiple components call this simultaneously,
 * they will share the same promise to prevent duplicate API calls.
 * 
 * Fetches complete configuration including provider availability, persona defaults,
 * and research persona from the unified /api/research/config endpoint.
 */
export const getResearchConfig = async (): Promise<ResearchConfigResponse> => {
  // If a request is already in flight, return the same promise
  if (pendingConfigRequest) {
    console.log('[researchConfig] Reusing pending request to avoid duplicate API call');
    return pendingConfigRequest;
  }

  // Create new request and cache it
  pendingConfigRequest = (async () => {
    try {
      // Use the unified /api/research/config endpoint which returns everything
      const response = await apiClient.get('/api/research/config');
      const config: ResearchConfigResponse = response.data;

      console.log('[researchConfig] Config loaded:', {
        providers: {
          exa: config.provider_availability?.exa_available,
          tavily: config.provider_availability?.tavily_available,
          google: config.provider_availability?.google_available,
        },
        personaDefaults: {
          industry: config.persona_defaults?.industry,
          target_audience: config.persona_defaults?.target_audience,
          hasDomains: config.persona_defaults?.suggested_domains?.length > 0,
          hasResearchPersona: config.persona_defaults?.has_research_persona,
        },
        researchPersona: {
          exists: !!config.research_persona,
          hasPresets: !!config.research_persona?.recommended_presets?.length,
        },
        onboarding: {
          completed: config.onboarding_completed,
          personaScheduled: config.persona_scheduled,
        },
      });

      return config;
    } catch (error: any) {
      const statusCode = error?.response?.status;
      const errorMessage = error?.response?.data?.detail || error?.message || 'Unknown error';
      
      console.error('[researchConfig] Error getting research config:', {
        status: statusCode,
        message: errorMessage,
        fullError: error
      });
      
      // Fallback: Try separate endpoints if unified endpoint fails
      try {
        console.log('[researchConfig] Falling back to separate endpoints');
        const [providersResp, personaDefaultsResp] = await Promise.allSettled([
          getProviderAvailability(),
          getPersonaDefaults(),
        ]);

        const providerAvailability: ProviderAvailability = providersResp.status === 'fulfilled'
          ? providersResp.value
          : {
              google_available: true,
              exa_available: false,
              tavily_available: false,
              gemini_key_status: 'missing',
              exa_key_status: 'missing',
              tavily_key_status: 'missing',
            };

        const personaDefaults: PersonaDefaults = personaDefaultsResp.status === 'fulfilled'
          ? personaDefaultsResp.value
          : {
              industry: 'Technology',
              target_audience: 'Professionals',
              suggested_domains: [],
              has_research_persona: false,
            };

        return {
          provider_availability: providerAvailability,
          persona_defaults: personaDefaults,
          research_persona: undefined,
          onboarding_completed: false,
          persona_scheduled: false,
        };
      } catch (fallbackError: any) {
        // Provide more specific error messages based on status code
        if (statusCode === 500) {
          throw new Error(`Backend server error: ${errorMessage}. Please check backend logs or try again later.`);
        } else if (statusCode === 401) {
          throw new Error('Authentication required. Please sign in again.');
        } else if (statusCode === 403) {
          throw new Error('Access denied. Please check your permissions.');
        } else if (statusCode === 429) {
          throw new Error('Rate limit exceeded. Please try again later.');
        } else if (!statusCode && error?.message) {
          // Network error or other connection issue
          throw new Error(`Failed to connect to server: ${error.message}`);
        } else {
          throw new Error(`Failed to get research config: ${errorMessage}`);
        }
      }
    } finally {
      // Clear the cached request after completion (success or error)
      pendingConfigRequest = null;
    }
  })();

  return pendingConfigRequest;
};

/**
 * Get or refresh research persona
 * @param forceRefresh - If true, regenerate persona even if cache is valid     
 */
export const refreshResearchPersona = async (forceRefresh: boolean = false): Promise<ResearchPersona> => {                                                      
  try {
    const url = `/api/research/research-persona${forceRefresh ? '?force_refresh=true' : ''}`;                                                                   
    const response = await apiClient.get(url);
    return response.data;
  } catch (error: any) {
    console.error('[researchConfig] Error refreshing research persona:', error?.response?.status || error?.message);                                            
    // Preserve the original error so subscription errors can be detected       
    // The apiClient interceptor should handle 429 errors, but we preserve the error structure                                                                  
    throw error;
  }
};

/**
 * Competitor Analysis Response Interface
 */
export interface CompetitorAnalysisResponse {
  success: boolean;
  competitors?: Array<{
    name?: string;
    url?: string;
    domain?: string;
    description?: string;
    similarity_score?: number;
    [key: string]: any;
  }>;
  social_media_accounts?: Record<string, string>;
  social_media_citations?: Array<{
    platform?: string;
    account?: string;
    url?: string;
    [key: string]: any;
  }>;
  research_summary?: {
    total_competitors?: number;
    industry_insights?: string;
    [key: string]: any;
  };
  analysis_timestamp?: string;
  error?: string;
}

/**
 * Get competitor analysis data from onboarding
 */
export const getCompetitorAnalysis = async (): Promise<CompetitorAnalysisResponse> => {
  console.log('[getCompetitorAnalysis] ===== START: Fetching competitor analysis =====');
  try {
    console.log('[getCompetitorAnalysis] Making GET request to /api/research/competitor-analysis');
    const response = await apiClient.get('/api/research/competitor-analysis');
    console.log('[getCompetitorAnalysis] ✅ Response received:', {
      success: response.data?.success,
      competitorsCount: response.data?.competitors?.length || 0,
      error: response.data?.error,
      fullResponse: response.data
    });
    return response.data;
  } catch (error: any) {
    const statusCode = error?.response?.status;
    const errorMessage = error?.response?.data?.detail || error?.response?.data?.error || error?.message || 'Unknown error';
    
    console.error('[getCompetitorAnalysis] ❌ ERROR:', {
      status: statusCode,
      message: errorMessage,
      fullError: error,
      responseData: error?.response?.data
    });
    
    // Return error response instead of throwing
    const errorResponse = {
      success: false,
      error: errorMessage
    };
    console.log('[getCompetitorAnalysis] Returning error response:', errorResponse);
    return errorResponse;
  } finally {
    console.log('[getCompetitorAnalysis] ===== END: Fetching competitor analysis =====');
  }
};

/**
 * Refresh competitor analysis by re-running competitor discovery
 */
export const refreshCompetitorAnalysis = async (): Promise<CompetitorAnalysisResponse> => {
  console.log('[refreshCompetitorAnalysis] ===== START: Refreshing competitor analysis =====');
  try {
    console.log('[refreshCompetitorAnalysis] Making POST request to /api/research/competitor-analysis/refresh');
    const response = await apiClient.post('/api/research/competitor-analysis/refresh');
    console.log('[refreshCompetitorAnalysis] ✅ Response received:', {
      success: response.data?.success,
      competitorsCount: response.data?.competitors?.length || 0,
      error: response.data?.error,
      fullResponse: response.data
    });
    return response.data;
  } catch (error: any) {
    const statusCode = error?.response?.status;
    const errorMessage = error?.response?.data?.detail || error?.response?.data?.error || error?.message || 'Unknown error';
    
    console.error('[refreshCompetitorAnalysis] ❌ ERROR:', {
      status: statusCode,
      message: errorMessage,
      fullError: error,
      responseData: error?.response?.data
    });
    
    // Return error response instead of throwing
    const errorResponse = {
      success: false,
      error: errorMessage
    };
    console.log('[refreshCompetitorAnalysis] Returning error response:', errorResponse);
    return errorResponse;
  } finally {
    console.log('[refreshCompetitorAnalysis] ===== END: Refreshing competitor analysis =====');
  }
};
