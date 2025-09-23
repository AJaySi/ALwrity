/**
 * Service for calling the hallucination detector API endpoints.
 */

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
    // Use environment variable or default to localhost
    this.baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  }

  /**
   * Detect hallucinations in the provided text.
   */
  async detectHallucinations(request: HallucinationDetectionRequest): Promise<HallucinationDetectionResponse> {
    console.log('🔍 [HallucinationDetectorService] detectHallucinations called with request:', request);
    try {
      const url = `${this.baseUrl}/api/hallucination-detector/detect`;
      console.log('🔍 [HallucinationDetectorService] Making request to:', url);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      console.log('🔍 [HallucinationDetectorService] Response status:', response.status, 'OK:', response.ok);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('🔍 [HallucinationDetectorService] HTTP error response:', errorText);
        throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
      }

      const data = await response.json();
      console.log('🔍 [HallucinationDetectorService] Response data:', data);
      return data;
    } catch (error) {
      console.error('🔍 [HallucinationDetectorService] Error detecting hallucinations:', error);
      return {
        success: false,
        claims: [],
        overall_confidence: 0,
        total_claims: 0,
        supported_claims: 0,
        refuted_claims: 0,
        insufficient_claims: 0,
        timestamp: new Date().toISOString(),
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  /**
   * Extract claims from the provided text.
   */
  async extractClaims(request: ClaimExtractionRequest): Promise<ClaimExtractionResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/hallucination-detector/extract-claims`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error extracting claims:', error);
      return {
        success: false,
        claims: [],
        total_claims: 0,
        timestamp: new Date().toISOString(),
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  /**
   * Verify a single claim.
   */
  async verifyClaim(request: ClaimVerificationRequest): Promise<ClaimVerificationResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/hallucination-detector/verify-claim`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
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
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  /**
   * Check the health of the hallucination detector service.
   */
  async healthCheck(): Promise<HealthCheckResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/hallucination-detector/health`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
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
      const response = await fetch(`${this.baseUrl}/api/hallucination-detector/demo`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error getting demo info:', error);
      return null;
    }
  }
}

// Export a singleton instance
export const hallucinationDetectorService = new HallucinationDetectorService();
export default hallucinationDetectorService;
