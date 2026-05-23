/**
 * Service for calling the hallucination detector API endpoints.
 */

import { longRunningApiClient } from '../api/client';

export interface SourceDocument {
  title: string;
  url: string;
  text: string;
  published_date?: string;
  author?: string;
  score: number;
}

export interface Claim {
  text: string;
  confidence: number;
  assessment: 'supported' | 'refuted' | 'insufficient_information';
  supporting_sources: SourceDocument[];
  refuting_sources: SourceDocument[];
  reasoning?: string;
}

export interface HallucinationDetectionRequest {
  text: string;
  include_sources?: boolean;
  max_claims?: number;
}

export interface HallucinationDetectionResponse {
  success: boolean;
  claims: Claim[];
  overall_confidence: number;
  total_claims: number;
  supported_claims: number;
  refuted_claims: number;
  insufficient_claims: number;
  timestamp: string;
  processing_time_ms?: number;
  error?: string;
}

export interface ClaimExtractionRequest {
  text: string;
  max_claims?: number;
}

export interface ClaimExtractionResponse {
  success: boolean;
  claims: string[];
  total_claims: number;
  timestamp: string;
  error?: string;
}

export interface ClaimVerificationRequest {
  claim: string;
  include_sources?: boolean;
}

export interface ClaimVerificationResponse {
  success: boolean;
  claim: Claim;
  timestamp: string;
  processing_time_ms?: number;
  error?: string;
}

export interface HealthCheckResponse {
  status: string;
  version: string;
  exa_api_available: boolean;
  openai_api_available: boolean;
  timestamp: string;
}

class HallucinationDetectorService {
  private baseUrl: string;

  constructor() {
    const getApiBaseUrl = () => {
      const url = process.env.REACT_APP_API_URL;
      if (process.env.NODE_ENV === 'production' && !url) {
        throw new Error('REACT_APP_API_URL environment variable is required for production');
      }
      return url || 'http://localhost:8000';
    };
    this.baseUrl = getApiBaseUrl();
  }

  // Kept for backward compatibility — auth is now handled by longRunningApiClient interceptors
  setAuthTokenGetter(_getter: (() => Promise<string | null>) | null) {
    // no-op
  }

  /**
   * Detect hallucinations in the provided text.
   */
  async detectHallucinations(request: HallucinationDetectionRequest): Promise<HallucinationDetectionResponse> {
    console.log('🔍 [HallucinationDetectorService] detectHallucinations called with request:', request);
    try {
      const url = `/api/hallucination-detector/detect`;
      console.log('🔍 [HallucinationDetectorService] Making request to:', url);
      
      const response = await longRunningApiClient.post(url, request);

      console.log('🔍 [HallucinationDetectorService] Response status:', response.status, 'OK:', response.status === 200);
      console.log('🔍 [HallucinationDetectorService] Response data:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('🔍 [HallucinationDetectorService] Error detecting hallucinations:', error);
      const errorMessage = error?.response?.data?.error || error?.response?.data?.message || error?.message || 'Unknown error occurred';
      return {
        success: false,
        claims: [],
        overall_confidence: 0,
        total_claims: 0,
        supported_claims: 0,
        refuted_claims: 0,
        insufficient_claims: 0,
        timestamp: new Date().toISOString(),
        error: errorMessage
      };
    }
  }

  /**
   * Extract claims from the provided text.
   */
  async extractClaims(request: ClaimExtractionRequest): Promise<ClaimExtractionResponse> {
    try {
      const response = await longRunningApiClient.post('/api/hallucination-detector/extract-claims', request);
      return response.data;
    } catch (error: any) {
      console.error('Error extracting claims:', error);
      return {
        success: false,
        claims: [],
        total_claims: 0,
        timestamp: new Date().toISOString(),
        error: error?.response?.data?.error || error?.message || 'Unknown error occurred'
      };
    }
  }

  /**
   * Verify a single claim.
   */
  async verifyClaim(request: ClaimVerificationRequest): Promise<ClaimVerificationResponse> {
    try {
      const response = await longRunningApiClient.post('/api/hallucination-detector/verify-claim', request);
      return response.data;
    } catch (error: any) {
      console.error('Error verifying claim:', error);
      return {
        success: false,
        claim: {
          text: request.claim,
          confidence: 0,
          assessment: 'insufficient_information',
          supporting_sources: [],
          refuting_sources: [],
          reasoning: 'Error during verification'
        },
        timestamp: new Date().toISOString(),
        error: error?.response?.data?.error || error?.message || 'Unknown error occurred'
      };
    }
  }

  /**
   * Check the health of the hallucination detector service.
   */
  async healthCheck(): Promise<HealthCheckResponse> {
    try {
      const response = await longRunningApiClient.get('/api/hallucination-detector/health');
      return response.data;
    } catch (error: any) {
      console.error('Error checking health:', error);
      return {
        status: 'unhealthy',
        version: '1.0.0',
        exa_api_available: false,
        openai_api_available: false,
        timestamp: new Date().toISOString()
      };
    }
  }

  /**
   * Get demo information about the API.
   */
  async getDemoInfo(): Promise<any> {
    try {
      const response = await longRunningApiClient.get('/api/hallucination-detector/demo');
      return response.data;
    } catch (error) {
      console.error('Error getting demo info:', error);
      return null;
    }
  }
}

// Export a singleton instance
export const hallucinationDetectorService = new HallucinationDetectorService();
export default hallucinationDetectorService;
