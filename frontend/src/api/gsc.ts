/** Google Search Console API client for ALwrity frontend. */

import { apiClient } from './client';
import { useAuth } from '@clerk/clerk-react';

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
  async getAuthUrl(): Promise<{ auth_url: string }> {
    console.log('GSC API: Getting OAuth authorization URL');
    try {
      const client = await this.getAuthenticatedClient();
      const response = await client.get(`${this.baseUrl}/auth/url`);
      console.log('GSC API: OAuth URL retrieved successfully');
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
    console.log('GSC API: Handling OAuth callback');
    try {
      const client = await this.getAuthenticatedClient();
      const response = await client.get(`${this.baseUrl}/callback`, {
        params: { code, state }
      });
      console.log('GSC API: OAuth callback handled successfully');
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
    console.log('GSC API: Getting user sites');
    try {
      const client = await this.getAuthenticatedClient();
      const response = await client.get(`${this.baseUrl}/sites`);
      console.log(`GSC API: Retrieved ${response.data.sites.length} sites`);
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
    console.log('GSC API: Getting analytics data for site:', request.site_url);
    try {
      const client = await this.getAuthenticatedClient();
      const response = await client.post(`${this.baseUrl}/analytics`, request);
      console.log('GSC API: Analytics data retrieved successfully');
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
    console.log('GSC API: Getting sitemaps for site:', siteUrl);
    try {
      const client = await this.getAuthenticatedClient();
      const response = await client.get(`${this.baseUrl}/sitemaps/${encodeURIComponent(siteUrl)}`);
      console.log(`GSC API: Retrieved ${response.data.sitemaps.length} sitemaps`);
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
    console.log('GSC API: Getting connection status');
    try {
      const client = await this.getAuthenticatedClient();
      const response = await client.get(`${this.baseUrl}/status`);
      console.log('GSC API: Status retrieved, connected:', response.data.connected);
      return response.data;
    } catch (error) {
      console.error('GSC API: Error getting status:', error);
      throw error;
    }
  }

  /**
   * Disconnect GSC account
   */
  async disconnect(): Promise<{ success: boolean; message: string }> {
    console.log('GSC API: Disconnecting GSC account');
    try {
      const client = await this.getAuthenticatedClient();
      const response = await client.delete(`${this.baseUrl}/disconnect`);
      console.log('GSC API: Account disconnected successfully');
      return response.data;
    } catch (error) {
      console.error('GSC API: Error disconnecting account:', error);
      throw error;
    }
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: string; service: string; timestamp: string }> {
    console.log('GSC API: Performing health check');
    try {
      const response = await apiClient.get(`${this.baseUrl}/health`);
      console.log('GSC API: Health check passed');
      return response.data;
    } catch (error) {
      console.error('GSC API: Health check failed:', error);
      throw error;
    }
  }
}

export const gscAPI = new GSCAPI();
