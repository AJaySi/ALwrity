/**
 * AI Visibility Insights API Client
 * Fetches AI Overview detection analysis from GSC data.
 */

import { apiClient } from './client';

export interface AIOThresholdInput {
  impacted_min_impressions: number;
  impacted_max_position: number;
  impacted_max_ctr: number;
  opportunity_min_impressions: number;
  opportunity_min_position: number;
  opportunity_max_position: number;
  opportunity_min_ctr: number;
}

export interface AIKeywordEntry {
  keyword: string;
  impressions: number;
  clicks: number;
  ctr: number;
  position: number;
  estimated_traffic_loss?: number;
  target_ctr?: number;
  recommendation?: string;
}

export interface AIVisibilitySummary {
  total_keywords_analyzed: number;
  total_impressions: number;
  total_clicks: number;
  average_ctr: number;
  average_position: number;
  aio_impacted_keywords: number;
  aio_opportunity_keywords: number;
  aio_zero_click_impressions: number;
  aio_estimated_traffic_loss: number;
  date_range: { start: string; end: string };
  thresholds_used: {
    impacted: { min_impressions: number; max_position: number; max_ctr: number };
    opportunity: { min_impressions: number; min_position: number; max_position: number; min_ctr: number };
  };
}

export interface AIVisibilityResponse {
  success: boolean;
  error?: string;
  summary: AIVisibilitySummary;
  impacted_keywords: AIKeywordEntry[];
  opportunity_keywords: AIKeywordEntry[];
  recommendations: string[];
}

class AIVisibilityAPI {
  async getOverviewInsights(
    siteUrl: string,
    startDate?: string,
    endDate?: string,
    thresholds?: AIOThresholdInput,
  ): Promise<AIVisibilityResponse> {
    const response = await apiClient.post('/ai-visibility/overview-insights', {
      site_url: siteUrl,
      start_date: startDate,
      end_date: endDate,
      thresholds,
    });
    return response.data;
  }
}

export const aiVisibilityApi = new AIVisibilityAPI();
