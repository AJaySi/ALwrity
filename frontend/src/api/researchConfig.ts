/**
 * Research Configuration API
 * Fetches provider availability and persona-aware defaults
 */

import { ResearchMode, ResearchProvider } from '../services/blogWriterApi';
import { apiClient } from './client';

export interface ProviderAvailability {
  google_available: boolean;
  exa_available: boolean;
  gemini_key_status: 'configured' | 'missing';
  exa_key_status: 'configured' | 'missing';
}

export interface PersonaDefaults {
  industry?: string;
  target_audience?: string;
  suggested_domains: string[];
  suggested_exa_category?: string;
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
    const response = await apiClient.get('/api/research/provider-availability');
    return response.data;
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
      const response = await apiClient.get('/api/research/config');
      return response.data;
    } catch (error: any) {
      const statusCode = error?.response?.status;
      const errorMessage = error?.response?.data?.detail || error?.message || 'Unknown error';
      
      console.error('[researchConfig] Error getting research config:', {
        status: statusCode,
        message: errorMessage,
        fullError: error
      });
      
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

