/** Google Search Console API client for ALwrity frontend. */

import { apiClient } from './client';

export interface GSCSite {
  siteUrl: string;
  permissionLevel: string;
}

export interface GSCAnalyticsRequest {
  site_url: string;
  start_date?: string;
  end_date?: string;
}

export interface GSCAnalyticsResponse {
  rows: Array<{
    keys: string[];
    clicks: number;
    impressions: number;
    ctr: number;
    position: number;
  }>;
  rowCount: number;
  startDate: string;
  endDate: string;
  siteUrl: string;
}

export interface GSCSitemap {
  path: string;
  lastSubmitted: string;
  contents: Array<{
    type: string;
    submitted: string;
    indexed: string;
  }>;
}

export interface GSCStatusResponse {
  connected: boolean;
  sites?: GSCSite[];
  last_sync?: string;
}

export interface GSCDataQualityResponse {
  site_url: string;
  permission_level?: string;
  has_sufficient_permission: boolean;
  data_days_available: number;
  data_window_start?: string;
  data_window_end?: string;
  indexing_health: {
    submitted_urls: number;
    indexed_urls: number;
    indexing_ratio?: number;
    sitemaps_count: number;
  };
}

export interface GSCCachedOpportunitiesResponse {
  site_url: string;
  opportunities: Array<{
    query: string;
    clicks: number;
    impressions: number;
    ctr: number;
    position: number;
    recommended_action: string;
  }>;
  generated_from_cache: boolean;
}

class GSCAPI {
  private baseUrl = '/gsc';
  private getAuthToken: (() => Promise<string | null>) | null = null;

  /**
   * Set the auth token getter function
   */
  setAuthTokenGetter(getToken: () => Promise<string | null>) {
    this.getAuthToken = getToken;
  }

  /**
   * Get authenticated API client with auth token
   */
  private async getAuthenticatedClient() {
    const token = this.getAuthToken ? await this.getAuthToken() : null;
    
    if (!token) {
      throw new Error('No authentication token available');
    }

    return apiClient.create({
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
  }

  /**
   * Get Google Search Console OAuth authorization URL
   */
  async getAuthUrl(): Promise<{ auth_url: string; trusted_origins?: string[] }> {
    try {
      const client = await this.getAuthenticatedClient();
      const response = await client.get(`${this.baseUrl}/auth/url`);
      return response.data;
    } catch (error) {
      console.error('GSC API: Error getting OAuth URL:', error);
      throw error;
    }
  }

  /**
   * Handle OAuth callback (typically called from popup)
   */
  async handleCallback(code: string, state: string): Promise<{ success: boolean; message: string }> {
    try {
      const client = await this.getAuthenticatedClient();
      const response = await client.get(`${this.baseUrl}/callback`, {
        params: { code, state }
      });
      return response.data;
    } catch (error) {
      console.error('GSC API: Error handling OAuth callback:', error);
      throw error;
    }
  }

  /**
   * Get user's Google Search Console sites
   */
  async getSites(): Promise<{ sites: GSCSite[] }> {
    try {
      const client = await this.getAuthenticatedClient();
      const response = await client.get(`${this.baseUrl}/sites`);
      return response.data;
    } catch (error) {
      console.error('GSC API: Error getting sites:', error);
      throw error;
    }
  }

  /**
   * Get search analytics data
   */
  async getAnalytics(request: GSCAnalyticsRequest): Promise<GSCAnalyticsResponse> {
    try {
      const client = await this.getAuthenticatedClient();
      const response = await client.post(`${this.baseUrl}/analytics`, request);
      return response.data;
    } catch (error) {
      console.error('GSC API: Error getting analytics:', error);
      throw error;
    }
  }

  /**
   * Get sitemaps for a specific site
   */
  async getSitemaps(siteUrl: string): Promise<{ sitemaps: GSCSitemap[] }> {
    try {
      const client = await this.getAuthenticatedClient();
      const response = await client.get(`${this.baseUrl}/sitemaps/${encodeURIComponent(siteUrl)}`);
      return response.data;
    } catch (error) {
      console.error('GSC API: Error getting sitemaps:', error);
      throw error;
    }
  }

  /**
   * Get GSC connection status
   */
  async getStatus(): Promise<GSCStatusResponse> {
    try {
      const client = await this.getAuthenticatedClient();
      const response = await client.get(`${this.baseUrl}/status`);
      return response.data;
    } catch (error) {
      console.error('GSC API: Error getting status:', error);
      throw error;
    }
  }

  /**
   * Clear incomplete GSC credentials
   */
  async clearIncomplete(): Promise<{ success: boolean; message: string }> {
    try {
      const client = await this.getAuthenticatedClient();
      const response = await client.post(`${this.baseUrl}/clear-incomplete`);
      return response.data;
    } catch (error) {
      console.error('GSC API: Error clearing incomplete credentials:', error);
      throw error;
    }
  }

  /**
   * Disconnect GSC account
   */
  async disconnect(): Promise<{ success: boolean; message: string }> {
    try {
      const client = await this.getAuthenticatedClient();
      const response = await client.delete(`${this.baseUrl}/disconnect`);
      return response.data;
    } catch (error) {
      console.error('GSC API: Error disconnecting account:', error);
      throw error;
    }
  }

  async getDataQuality(siteUrl: string): Promise<GSCDataQualityResponse> {
    const client = await this.getAuthenticatedClient();
    const response = await client.get(`${this.baseUrl}/data-quality`, {
      params: { site_url: siteUrl }
    });
    return response.data;
  }

  async getOpportunities(siteUrl: string): Promise<GSCCachedOpportunitiesResponse> {
    const client = await this.getAuthenticatedClient();
    const response = await client.get(`${this.baseUrl}/opportunities`, {
      params: { site_url: siteUrl }
    });
    return response.data;
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: string; service: string; timestamp: string }> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/health`);
      return response.data;
    } catch (error) {
      console.error('GSC API: Health check failed:', error);
      throw error;
    }
  }
}

export const gscAPI = new GSCAPI();
