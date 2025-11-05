// SEO API Service
// Handles all communication with the FastAPI backend SEO endpoints

import { 
  SEOAnalysisData, 
  MetaDescriptionResponse, 
  PageSpeedResponse, 
  SitemapResponse, 
  PersonalizationData,
  DashboardLayout,
  CopilotActionResponse,
  CopilotSuggestion
} from '../types/seoCopilotTypes';

// Consistent API URL pattern - use same env vars as other services
const API_BASE_URL = process.env.REACT_APP_API_URL || process.env.REACT_APP_BACKEND_URL || '';

class SEOApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  // Generic API request method
  private async makeRequest<T>(
    endpoint: string, 
    method: 'GET' | 'POST' | 'PUT' | 'DELETE' = 'GET',
    data?: any
  ): Promise<T> {
    try {
      const url = `${this.baseUrl}${endpoint}`;
      const options: RequestInit = {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      };

      if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
      }

      const response = await fetch(url, options);
      
      if (!response.ok) {
        throw new Error(`API request failed: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`SEO API Error (${endpoint}):`, error);
      throw error;
    }
  }

  // SEO Analysis Methods
  async analyzeSEO(url: string, options?: any): Promise<SEOAnalysisData> {
    return this.makeRequest<SEOAnalysisData>('/api/seo-dashboard/analyze-comprehensive', 'POST', {
      url,
      ...options
    });
  }

  async analyzeSEOFull(url: string, options?: any): Promise<SEOAnalysisData> {
    return this.makeRequest<SEOAnalysisData>('/api/seo-dashboard/analyze-full', 'POST', {
      url,
      ...options
    });
  }

  async getSEOHealthScore(): Promise<{ health_score: number }> {
    return this.makeRequest<{ health_score: number }>('/api/seo-dashboard/health-score');
  }

  async getSEOMetrics(url?: string): Promise<any> {
    const endpoint = url ? `/api/seo-dashboard/metrics-detailed?url=${encodeURIComponent(url)}` : '/api/seo-dashboard/metrics';
    return this.makeRequest(endpoint);
  }

  async getAnalysisSummary(url: string): Promise<any> {
    return this.makeRequest(`/api/seo-dashboard/analysis-summary?url=${encodeURIComponent(url)}`);
  }

  async batchAnalyzeUrls(urls: string[]): Promise<any> {
    return this.makeRequest('/api/seo-dashboard/batch-analyze', 'POST', { urls });
  }

  // Meta Description Generation
  async generateMetaDescriptions(params: {
    keywords: string[];
    tone?: string;
    search_intent?: string;
    language?: string;
    custom_prompt?: string;
  }): Promise<MetaDescriptionResponse> {
    return this.makeRequest<MetaDescriptionResponse>('/api/seo/meta-description', 'POST', params);
  }

  // PageSpeed Analysis
  async analyzePageSpeed(params: {
    url: string;
    strategy?: 'DESKTOP' | 'MOBILE';
    locale?: string;
    categories?: string[];
  }): Promise<PageSpeedResponse> {
    return this.makeRequest<PageSpeedResponse>('/api/seo/pagespeed-analysis', 'POST', params);
  }

  // Sitemap Analysis
  async analyzeSitemap(params: {
    sitemap_url: string;
    analyze_content_trends?: boolean;
    analyze_publishing_patterns?: boolean;
  }): Promise<SitemapResponse> {
    return this.makeRequest<SitemapResponse>('/api/seo/sitemap-analysis', 'POST', params);
  }

  // Image Alt Text Generation
  async generateImageAltText(params: {
    image_url?: string;
    context?: string;
    keywords?: string[];
  }): Promise<any> {
    return this.makeRequest('/api/seo/image-alt-text', 'POST', params);
  }

  // OpenGraph Tag Generation
  async generateOpenGraphTags(params: {
    url: string;
    title_hint?: string;
    description_hint?: string;
    platform?: string;
  }): Promise<any> {
    return this.makeRequest('/api/seo/opengraph-tags', 'POST', params);
  }

  // On-Page SEO Analysis
  async analyzeOnPageSEO(params: {
    url: string;
    target_keywords?: string[];
    analyze_images?: boolean;
    analyze_content_quality?: boolean;
  }): Promise<any> {
    return this.makeRequest('/api/seo/on-page-analysis', 'POST', params);
  }

  // Technical SEO Analysis
  async analyzeTechnicalSEO(params: {
    url: string;
    analyze_core_web_vitals?: boolean;
    analyze_mobile_friendliness?: boolean;
    analyze_security?: boolean;
  }): Promise<any> {
    return this.makeRequest('/api/seo/technical-seo', 'POST', params);
  }

  // Enterprise SEO Analysis
  async analyzeEnterpriseSEO(params: {
    url: string;
    analyze_competitors?: boolean;
    analyze_market_position?: boolean;
    analyze_roi_metrics?: boolean;
  }): Promise<any> {
    return this.makeRequest('/api/seo/workflow/website-audit', 'POST', params);
  }

  // Content Strategy Analysis
  async analyzeContentStrategy(params: {
    url: string;
    analyze_content_gaps?: boolean;
    analyze_topic_clusters?: boolean;
    analyze_content_performance?: boolean;
  }): Promise<any> {
    return this.makeRequest('/api/seo/workflow/content-analysis', 'POST', params);
  }

  // Health Check
  async getSEOHealthCheck(): Promise<any> {
    return this.makeRequest('/api/seo/health');
  }

  async getSEOToolsStatus(): Promise<any> {
    return this.makeRequest('/api/seo/tools/status');
  }

  // Website Audit Workflow
  async performWebsiteAudit(url: string, options?: any): Promise<SEOAnalysisData> {
    return this.makeRequest<SEOAnalysisData>('/api/seo/workflow/website-audit', 'POST', {
      url,
      audit_type: options?.audit_type || 'comprehensive',
      include_recommendations: options?.include_recommendations ?? true
    });
  }

  // Content Analysis Workflow
  async analyzeContentComprehensive(url: string, options?: any): Promise<SEOAnalysisData> {
    return this.makeRequest<SEOAnalysisData>('/api/seo/workflow/content-analysis', 'POST', {
      url,
      content_focus: options?.content_focus,
      seo_optimization: options?.seo_optimization ?? true
    });
  }

  // SEO Health Check
  async checkSEOHealth(url?: string, options?: any): Promise<{ health_score: number; status: string; tools_status?: any }> {
    const endpoint = url ? '/api/seo/health' : '/api/seo/tools/status';
    const params = url ? { url } : {};
    
    return this.makeRequest(endpoint, 'GET', params);
  }

  // Personalization Data
  async getPersonalizationData(): Promise<PersonalizationData> {
    // This would typically fetch from a user profile endpoint
    // For now, return mock data
    return Promise.resolve({
      user_profile: {
        id: '1',
        name: 'SEO User',
        email: 'seo@example.com',
        experience_level: 'intermediate',
        business_type: 'ecommerce',
        target_audience: 'general',
        seo_goals: ['improve_rankings', 'increase_traffic'],
        seo_experience: 'intermediate'
      },
      business_type: 'ecommerce',
      target_audience: 'general',
      seo_goals: ['improve_rankings', 'increase_traffic'],
      seo_experience: 'intermediate'
    });
  }

  // Dashboard Layout Update
  async updateDashboardLayout(layout: DashboardLayout): Promise<{ success: boolean; layout: DashboardLayout }> {
    // This would typically save to backend
    // For now, return success
    return Promise.resolve({
      success: true,
      layout
    });
  }

  // SEO Suggestions
  async getSEOSuggestions(context: string): Promise<CopilotSuggestion[]> {
    // This would typically call an AI service for contextual suggestions
    // For now, return mock suggestions
    return Promise.resolve([
      {
        id: '1',
        title: 'Optimize Page Speed',
        description: 'Your page speed could be improved for better user experience',
        message: 'Consider optimizing your page speed for better user experience and SEO rankings',
        category: 'optimization',
        priority: 'high',
        action: 'analyzePageSpeed',
        icon: '⚡',
        severity: 'medium'
      }
    ]);
  }

  // CopilotKit Specific Methods
  async executeCopilotAction(action: string, params: any): Promise<CopilotActionResponse> {
    try {
      const startTime = Date.now();
      
      let result: any;
      
      switch (action) {
        case 'analyzeSEOComprehensive':
          result = await this.analyzeSEO(params.url, params);
          break;
        case 'generateMetaDescriptions':
          result = await this.generateMetaDescriptions(params);
          break;
        case 'analyzePageSpeed':
          result = await this.analyzePageSpeed(params);
          break;
        case 'analyzeSitemap':
          result = await this.analyzeSitemap(params);
          break;
        case 'generateImageAltText':
          result = await this.generateImageAltText(params);
          break;
        case 'generateOpenGraphTags':
          result = await this.generateOpenGraphTags(params);
          break;
        case 'analyzeOnPageSEO':
          result = await this.analyzeOnPageSEO(params);
          break;
        case 'analyzeTechnicalSEO':
          result = await this.analyzeTechnicalSEO(params);
          break;
        case 'analyzeEnterpriseSEO':
          result = await this.analyzeEnterpriseSEO(params);
          break;
        case 'analyzeContentStrategy':
          result = await this.analyzeContentStrategy(params);
          break;
        case 'performWebsiteAudit':
          result = await this.performWebsiteAudit(params.url, params);
          break;
        case 'analyzeContentComprehensive':
          result = await this.analyzeContentComprehensive(params.url, params);
          break;
        case 'checkSEOHealth':
          result = await this.checkSEOHealth(params.url, params);
          break;
        default:
          throw new Error(`Unknown action: ${action}`);
      }

      const executionTime = Date.now() - startTime;

      return {
        success: true,
        message: `${action} completed successfully`,
        data: result,
        execution_time: executionTime
      };
    } catch (error: any) {
      return {
        success: false,
        message: `Failed to execute ${action}: ${error.message}`,
        error: error.message,
        execution_time: 0
      };
    }
  }

  // Error handling utility
  private handleError(error: any, context: string): never {
    console.error(`SEO API Error (${context}):`, error);
    throw new Error(`SEO API Error: ${error.message || 'Unknown error occurred'}`);
  }
}

// Export singleton instance
export const seoApiService = new SEOApiService();
export default seoApiService;
