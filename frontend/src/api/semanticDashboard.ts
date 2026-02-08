import { apiClient } from './client';

// Semantic health metric interface matching backend SemanticHealthMetric
export interface SemanticHealthMetric {
  metric_name: string;
  value: number;
  threshold: number;
  status: 'healthy' | 'warning' | 'critical';
  timestamp: string;
  description: string;
  recommendations: string[];
}

// Competitor semantic snapshot interface
export interface CompetitorSemanticSnapshot {
  competitor_id: string;
  competitor_name: string;
  semantic_overlap: number;
  unique_topics: string[];
  content_volume: number;
  authority_score: number;
  last_updated: string;
  trending_topics: string[];
}

// Content semantic insight interface
export interface ContentSemanticInsight {
  insight_id: string;
  insight_type: 'gap' | 'opportunity' | 'trend' | 'threat';
  title: string;
  description: string;
  confidence_score: number;
  impact_score: number;
  related_topics: string[];
  suggested_actions: string[];
  created_at: string;
  expires_at: string;
}

// Semantic dashboard data interface
export interface SemanticDashboardData {
  health_metrics: SemanticHealthMetric[];
  competitor_snapshots: CompetitorSemanticSnapshot[];
  content_insights: ContentSemanticInsight[];
  monitoring_status: 'active' | 'inactive';
  last_updated: string;
}

// Semantic Dashboard API functions
export const semanticDashboardAPI = {
  // Get semantic health metrics
  async getSemanticHealth(): Promise<SemanticHealthMetric> {
    try {
      const response = await apiClient.get('/api/seo-dashboard/semantic-health');
      return response.data;
    } catch (error) {
      console.error('Error fetching semantic health:', error);
      throw error;
    }
  },

  // Get complete semantic dashboard data
  async getSemanticDashboardData(): Promise<SemanticDashboardData> {
    try {
      const response = await apiClient.get('/api/semantic-dashboard/data');
      return response.data;
    } catch (error) {
      console.error('Error fetching semantic dashboard data:', error);
      throw error;
    }
  },

  // Get competitor semantic snapshots
  async getCompetitorSnapshots(): Promise<CompetitorSemanticSnapshot[]> {
    try {
      const response = await apiClient.get('/api/semantic-dashboard/competitors');
      return response.data;
    } catch (error) {
      console.error('Error fetching competitor snapshots:', error);
      throw error;
    }
  },

  // Get content insights
  async getContentInsights(): Promise<ContentSemanticInsight[]> {
    try {
      const response = await apiClient.get('/api/semantic-dashboard/insights');
      return response.data;
    } catch (error) {
      console.error('Error fetching content insights:', error);
      throw error;
    }
  },

  // Refresh semantic analysis
  async refreshSemanticAnalysis(): Promise<void> {
    try {
      await apiClient.post('/api/semantic-dashboard/refresh');
    } catch (error) {
      console.error('Error refreshing semantic analysis:', error);
      throw error;
    }
  }
};