import { apiClient } from './client';

export interface SEOHealthScore {
  score: number;
  change: number;
  trend: string;
  label: string;
  color: string;
}

export interface SEOMetric {
  value: number;
  change: number;
  trend: string;
  description: string;
  color: string;
}

export interface PlatformStatus {
  status: string;
  connected: boolean;
  last_sync?: string;
  data_points?: number;
  // Additional Bing-specific properties
  has_expired_tokens?: boolean;
  last_token_date?: string;
  total_tokens?: number;
}

export interface AIInsight {
  insight: string;
  priority: string;
  category: string;
  action_required: boolean;
  tool_path?: string;
}

export interface SEODashboardData {
  health_score: SEOHealthScore;
  key_insight: string;
  priority_alert: string;
  metrics: Record<string, SEOMetric>;
  platforms: Record<string, PlatformStatus>;
  ai_insights: AIInsight[];
  last_updated: string;
  website_url?: string;  // User's website URL from onboarding
  // Real data from backend
  summary?: {
    clicks: number;
    impressions: number;
    ctr: number;
    position: number;
  };
  timeseries?: any[];
  advertools_insights?: any;
  competitor_insights?: {
    competitor_keywords: any[];
    content_gaps: any[];
    opportunity_score: number;
  };
  technical_seo_audit?: {
    status: string;
    task_status?: string | null;
    next_execution?: string | null;
    pages_audited: number;
    avg_score: number;
    fix_scheduled_pages: number;
    worst_pages: Array<{
      page_url: string;
      overall_score: number;
      status: string;
      issues_count?: number;
    }>;
    error?: string;
  };
}

// SEO Dashboard API functions
export const seoDashboardAPI = {
  // Get complete dashboard data
  async getDashboardData(): Promise<SEODashboardData> {
    try {
      const response = await apiClient.get('/api/seo-dashboard/data');
      return response.data;
    } catch (error) {
      console.error('Error fetching SEO dashboard data:', error);
      throw error;
    }
  },

  // Get health score only
  async getHealthScore(): Promise<SEOHealthScore> {
    try {
      const response = await apiClient.get('/api/seo-dashboard/health-score');
      return response.data;
    } catch (error) {
      console.error('Error fetching SEO health score:', error);
      throw error;
    }
  },

  // Get metrics only
  async getMetrics(): Promise<Record<string, SEOMetric>> {
    try {
      const response = await apiClient.get('/api/seo-dashboard/metrics');
      return response.data;
    } catch (error) {
      console.error('Error fetching SEO metrics:', error);
      throw error;
    }
  },

  // Get platform status
  async getPlatformStatus(): Promise<Record<string, PlatformStatus>> {
    try {
      const response = await apiClient.get('/api/seo-dashboard/platforms');
      return response.data;
    } catch (error) {
      console.error('Error fetching platform status:', error);
      throw error;
    }
  },

  // Get AI insights
  async getAIInsights(): Promise<AIInsight[]> {
    try {
      const response = await apiClient.get('/api/seo-dashboard/insights');
      return response.data;
    } catch (error) {
      console.error('Error fetching AI insights:', error);
      throw error;
    }
  },

  // Health check
  async healthCheck(): Promise<any> {
    try {
      const response = await apiClient.get('/api/seo-dashboard/health');
      return response.data;
    } catch (error) {
      console.error('Error checking SEO dashboard health:', error);
      throw error;
    }
  }
}; 
