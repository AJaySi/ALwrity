import { apiClient } from './client';

export interface ContentOpportunity {
  type: 'Content Optimization' | 'Content Enhancement';
  keyword: string;
  opportunity: string;
  potential_impact: 'High' | 'Medium';
  current_position: number;
  impressions: number;
  priority: 'High' | 'Medium';
}

export interface KeywordGap {
  keyword: string;
  position: number;
  impressions: number;
}

export interface AIRecommendations {
  immediate_opportunities: string[];
  content_strategy: string[];
  long_term_strategy: string[];
}

export interface BrainstormSummary {
  site_url: string;
  date_range: { start: string; end: string };
  total_keywords_analyzed: number;
  total_impressions: number;
  total_clicks: number;
  avg_ctr: number;
  avg_position: number;
  keyword_distribution: {
    positions_1_3: number;
    positions_4_10: number;
    positions_11_20: number;
    positions_21_plus: number;
  };
  top_keywords: Array<{ keyword: string; impressions: number; position: number }>;
  top_pages: Array<{ page: string; clicks: number; impressions: number }>;
}

export interface BrainstormResult {
  error?: string;
  content_opportunities: ContentOpportunity[];
  keyword_gaps: KeywordGap[];
  ai_recommendations: AIRecommendations | Record<string, never>;
  summary: BrainstormSummary | Record<string, never>;
}

class GSCBrainstormAPI {
  private baseUrl = '/gsc';
  private getAuthToken: (() => Promise<string | null>) | null = null;

  setAuthTokenGetter(getToken: () => Promise<string | null>) {
    this.getAuthToken = getToken;
  }

  private async getAuthenticatedClient() {
    const token = this.getAuthToken ? await this.getAuthToken() : null;
    if (!token) {
      throw new Error('No authentication token available');
    }
    return apiClient.create({
      headers: { Authorization: `Bearer ${token}` },
    });
  }

  async brainstorm(keywords: string, siteUrl?: string): Promise<BrainstormResult> {
    const client = await this.getAuthenticatedClient();
    const response = await client.post(`${this.baseUrl}/brainstorm`, {
      keywords,
      site_url: siteUrl || undefined,
    });
    return response.data;
  }
}

export const gscBrainstormAPI = new GSCBrainstormAPI();