/**
 * Persona API Client
 * Handles communication with the persona generation backend services.
 */

import { apiClient } from './client';

export interface PersonaGenerationRequest {
  onboarding_data: {
    websiteAnalysis?: any;
    competitorResearch?: any;
    sitemapAnalysis?: any;
    businessData?: any;
    researchPreferences?: any;
    deepCompetitorAnalysis?: any;
  };
  selected_platforms: string[];
  user_preferences?: any;
}

export interface PersonaGenerationResponse {
  success: boolean;
  core_persona?: any;
  platform_personas?: Record<string, any>;
  quality_metrics?: any;
  error?: string;
}

export interface PersonaQualityRequest {
  core_persona: any;
  platform_personas: Record<string, any>;
  user_feedback?: any;
}

export interface PersonaQualityResponse {
  success: boolean;
  quality_metrics?: any;
  recommendations?: string[];
  error?: string;
}

export interface PersonaOptions {
  success: boolean;
  available_platforms: Array<{
    id: string;
    name: string;
    description: string;
  }>;
  persona_types: string[];
  quality_metrics: string[];
}

/**
 * Generate AI writing personas using the sophisticated persona system.
 */
export const generateWritingPersonas = async (
  request: PersonaGenerationRequest
): Promise<PersonaGenerationResponse> => {
  try {
    const response = await apiClient.post('/api/onboarding/step4/generate-personas', request);
    return response.data;
  } catch (error: any) {
    console.error('Error generating personas:', error);
    return {
      success: false,
      error: error.response?.data?.detail || error.message || 'Failed to generate personas'
    };
  }
};

/**
 * Assess the quality of generated personas.
 */
export const assessPersonaQuality = async (
  request: PersonaQualityRequest
): Promise<PersonaQualityResponse> => {
  try {
    const response = await apiClient.post('/api/onboarding/step4/assess-quality', request);
    return response.data;
  } catch (error: any) {
    console.error('Error assessing persona quality:', error);
    return {
      success: false,
      error: error.response?.data?.detail || error.message || 'Failed to assess persona quality'
    };
  }
};

/**
 * Regenerate persona with different parameters.
 */
export const regeneratePersona = async (
  request: PersonaGenerationRequest
): Promise<PersonaGenerationResponse> => {
  try {
    const response = await apiClient.post('/api/onboarding/step4/regenerate-persona', request);
    return response.data;
  } catch (error: any) {
    console.error('Error regenerating persona:', error);
    return {
      success: false,
      error: error.response?.data?.detail || error.message || 'Failed to regenerate persona'
    };
  }
};

/**
 * Get available options for persona generation.
 */
export const getPersonaGenerationOptions = async (): Promise<PersonaOptions> => {
  try {
    const response = await apiClient.get('/api/onboarding/step4/persona-options');
    return response.data;
  } catch (error: any) {
    console.error('Error getting persona options:', error);
    return {
      success: false,
      available_platforms: [],
      persona_types: [],
      quality_metrics: []
    };
  }
};

/**
 * Utility function to prepare onboarding data for persona generation.
 */
export const prepareOnboardingData = (stepData: any) => {
  const websiteAnalysis =
    stepData?.websiteAnalysis ??
    stepData?.analysis ??
    null;

  const competitorResearch =
    stepData?.competitorResearch ??
    {
      competitors: stepData?.competitors || [],
      researchSummary: stepData?.researchSummary || null,
      socialMediaAccounts: stepData?.socialMediaAccounts || {},
    };

  return {
    websiteAnalysis,
    competitorResearch,
    sitemapAnalysis: stepData?.sitemapAnalysis ?? null,
    businessData: stepData?.businessData ?? null,
    researchPreferences: stepData?.researchPreferences ?? null,
    deepCompetitorAnalysis: stepData?.deepCompetitorAnalysis ?? null,
  };
};

/**
 * Utility function to validate persona generation request.
 */
export const validatePersonaRequest = (request: PersonaGenerationRequest): string[] => {
  const errors: string[] = [];
  
  if (!request.onboarding_data) {
    errors.push('Onboarding data is required');
  }
  
  if (!request.selected_platforms || request.selected_platforms.length === 0) {
    errors.push('At least one platform must be selected');
  }
  
  if (request.selected_platforms && request.selected_platforms.length > 5) {
    errors.push('Maximum 5 platforms can be selected');
  }
  
  return errors;
};
