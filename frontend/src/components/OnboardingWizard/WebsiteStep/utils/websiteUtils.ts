/**
 * Website Step Utility Functions
 * Extracted utility functions for website analysis and URL handling
 */

import { apiClient } from '../../../../api/client';

/**
 * Fixes URL format by adding protocol if missing and ensuring proper format
 * @param url - The URL string to fix
 * @returns Fixed URL string or null if invalid
 */
export const fixUrlFormat = (url: string): string | null => {
  if (!url) return null;
  
  // Remove leading/trailing whitespace
  let fixedUrl = url.trim();
  
  // Check if URL already has a protocol but is missing slashes
  if (fixedUrl.startsWith('https:/') && !fixedUrl.startsWith('https://')) {
    fixedUrl = fixedUrl.replace('https:/', 'https://');
  } else if (fixedUrl.startsWith('http:/') && !fixedUrl.startsWith('http://')) {
    fixedUrl = fixedUrl.replace('http:/', 'http://');
  }
  
  // Add protocol if missing
  if (!fixedUrl.startsWith('http://') && !fixedUrl.startsWith('https://')) {
    fixedUrl = 'https://' + fixedUrl;
  }
  
  // Fix missing slash after protocol
  if (fixedUrl.includes('://') && !fixedUrl.split('://')[1].startsWith('/')) {
    fixedUrl = fixedUrl.replace('://', ':///');
  }
  
  // Ensure only two slashes after protocol
  if (fixedUrl.includes(':///')) {
    fixedUrl = fixedUrl.replace(':///', '://');
  }
  
  // Basic URL validation
  try {
    new URL(fixedUrl);
    return fixedUrl;
  } catch {
    return null;
  }
};

/**
 * Extracts domain name from URL for personalization
 * @param url - The URL to extract domain from
 * @returns Formatted domain name or fallback text
 */
export const extractDomainName = (url: string): string => {
  try {
    const domain = new URL(url).hostname.replace('www.', '');
    return domain.charAt(0).toUpperCase() + domain.slice(1);
  } catch {
    return 'Your Website';
  }
};

/**
 * Checks for existing analysis for a given URL
 * @param url - The URL to check for existing analysis
 * @returns Promise<boolean> - Whether existing analysis was found
 */
export const checkExistingAnalysis = async (url: string): Promise<{
  exists: boolean;
  analysis?: any;
  error?: string;
}> => {
  try {
    console.log('WebsiteStep: Checking existing analysis for URL:', url);
    const response = await apiClient.get(`/api/onboarding/style-detection/check-existing/${encodeURIComponent(url)}`);
    const result = response.data;
    
    if (result.exists) {
      console.log('WebsiteStep: Existing analysis found:', result);
      return {
        exists: true,
        analysis: result
      };
    } else {
      console.log('WebsiteStep: No existing analysis found');
      return {
        exists: false
      };
    }
  } catch (error) {
    console.error('WebsiteStep: Error checking existing analysis:', error);
    return {
      exists: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
};

/**
 * Loads existing analysis by ID
 * @param analysisId - The ID of the analysis to load
 * @param website - The website URL for domain extraction
 * @returns Promise<boolean> - Whether loading was successful
 */
export const loadExistingAnalysis = async (analysisId: number, website: string): Promise<{
  success: boolean;
  analysis?: any;
  domainName?: string;
  error?: string;
}> => {
  try {
    const response = await apiClient.get(`/api/onboarding/style-detection/analysis/${analysisId}`);
    const result = response.data;
    
    if (result.success && result.analysis) {
      // Extract domain name for personalization
      const extractedDomain = extractDomainName(website);
      
      // Database structure: flat fields at top level
      // Need to combine them into the format expected by UI
      const comprehensiveAnalysis = {
        // Top-level style analysis fields from database
        writing_style: result.analysis.writing_style,
        content_characteristics: result.analysis.content_characteristics,
        target_audience: result.analysis.target_audience,
        content_type: result.analysis.content_type,
        brand_analysis: result.analysis.brand_analysis,
        content_strategy_insights: result.analysis.content_strategy_insights,
        recommended_settings: result.analysis.recommended_settings,
        
        // Extract guidelines from style_guidelines object
        guidelines: result.analysis.style_guidelines?.guidelines,
        best_practices: result.analysis.style_guidelines?.best_practices,
        avoid_elements: result.analysis.style_guidelines?.avoid_elements,
        content_strategy: result.analysis.style_guidelines?.content_strategy,
        ai_generation_tips: result.analysis.style_guidelines?.ai_generation_tips,
        competitive_advantages: result.analysis.style_guidelines?.competitive_advantages,
        content_calendar_suggestions: result.analysis.style_guidelines?.content_calendar_suggestions,
        
        // Style patterns
        style_patterns: result.analysis.style_patterns,
        style_consistency: result.analysis.style_patterns?.style_consistency,
        unique_elements: result.analysis.style_patterns?.unique_elements
      };
      
      return {
        success: true,
        analysis: comprehensiveAnalysis,
        domainName: extractedDomain
      };
    }
    return {
      success: false,
      error: 'Analysis not found'
    };
  } catch (error) {
    console.error('Error loading existing analysis:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
};

/**
 * Performs new website analysis
 * @param fixedUrl - The fixed URL to analyze
 * @param updateProgress - Callback function to update progress
 * @returns Promise<object> - Analysis result
 */
export const performAnalysis = async (
  fixedUrl: string, 
  updateProgress: (step: number, message: string) => void
): Promise<{
  success: boolean;
  analysis?: any;
  domainName?: string;
  warning?: string;
  error?: string;
}> => {
  try {
    // Simulate progress updates
    updateProgress(1, 'Website URL validated');
    
    const requestData = {
      url: fixedUrl,
      include_patterns: true,
      include_guidelines: true
    };

    updateProgress(2, 'Starting content crawl...');
    
    const response = await apiClient.post('/api/onboarding/style-detection/complete', requestData);

    updateProgress(3, 'Content extracted successfully');
    updateProgress(4, 'Style analysis in progress...');
    updateProgress(5, 'Content characteristics analyzed');
    updateProgress(6, 'Target audience identified');
    updateProgress(7, 'Recommendations generated');

    const result = response.data;

    if (result.success) {
      // Extract domain name for personalization
      const extractedDomain = extractDomainName(fixedUrl);
      
      // Combine all analysis data into a comprehensive object
      const comprehensiveAnalysis = {
        ...result.style_analysis,
        guidelines: result.style_guidelines?.guidelines,
        best_practices: result.style_guidelines?.best_practices,
        avoid_elements: result.style_guidelines?.avoid_elements,
        content_strategy: result.style_guidelines?.content_strategy,
        ai_generation_tips: result.style_guidelines?.ai_generation_tips,
        competitive_advantages: result.style_guidelines?.competitive_advantages,
        content_calendar_suggestions: result.style_guidelines?.content_calendar_suggestions,
        style_patterns: result.style_patterns,
        style_consistency: result.style_patterns?.style_consistency,
        unique_elements: result.style_patterns?.unique_elements
      };
      
      return {
        success: true,
        analysis: comprehensiveAnalysis,
        domainName: extractedDomain,
        warning: result.warning
      };
    } else {
      // Handle specific error cases
      let errorMessage = result.error || 'Analysis failed';
      
      if (errorMessage.includes('API key') || errorMessage.includes('configure')) {
        errorMessage = 'API keys not configured. Please complete step 1 of onboarding to configure your AI provider API keys.';
      } else if (errorMessage.includes('library not available')) {
        errorMessage = 'AI provider library not available. Please ensure your AI provider is properly configured in step 1.';
      } else if (errorMessage.includes('crawl') || errorMessage.includes('website')) {
        errorMessage = 'Unable to access the website. Please check the URL and ensure the website is publicly accessible.';
      }
      
      return {
        success: false,
        error: errorMessage
      };
    }
  } catch (error) {
    console.error('Analysis error:', error);
    return {
      success: false,
      error: 'Failed to analyze website. Please check your internet connection and try again.'
    };
  }
};

/**
 * Fetches the last analysis from session for pre-filling
 * @returns Promise<object> - Last analysis data
 */
export const fetchLastAnalysis = async (): Promise<{
  success: boolean;
  website?: string;
  analysis?: any;
  error?: string;
}> => {
  try {
    // Fixed: Added /onboarding prefix to match backend router
    const res = await apiClient.get('/api/onboarding/style-detection/session-analyses');
    const data = res.data;
    if (data.success && Array.isArray(data.analyses) && data.analyses.length > 0) {
      // Pick the most recent analysis (assuming sorted by date desc, else sort here)
      const last = data.analyses[0];
      if (last && last.website_url) {
        return {
          success: true,
          website: last.website_url,
          analysis: last.style_analysis
        };
      }
    }
    return {
      success: false,
      error: 'No previous analysis found'
    };
  } catch (err) {
    console.error('WebsiteStep: Error pre-filling from last analysis', err);
    return {
      success: false,
      error: err instanceof Error ? err.message : 'Unknown error'
    };
  }
};
