/**
 * Bing Webmaster OAuth API Client
 * Handles Bing Webmaster Tools OAuth2 authentication flow
 */

import { apiClient } from './client';

export interface BingOAuthStatus {
  connected: boolean;
  sites: Array<{
    id: number;
    access_token: string;
    scope: string;
    created_at: string;
    sites: Array<{
      id: string;
      name: string;
      url: string;
      status: string;
    }>;
  }>;
  total_sites: number;
}

export interface BingOAuthResponse {
  provider_id: string;
  url: string;
  state?: string;
  details?: {
    redirect_uri?: string;
    trusted_origins?: string[];
  };
}

export interface BingCallbackResponse {
  success: boolean;
  message: string;
  access_token?: string;
  expires_in?: number;
}

class BingOAuthAPI {
  private getAuthToken: (() => Promise<string | null>) | null = null;

  /**
   * Set authentication token getter
   */
  setAuthTokenGetter(getter: () => Promise<string | null>) {
    this.getAuthToken = getter;
  }

  /**
   * Get authenticated client with token
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
   * Get Bing Webmaster OAuth authorization URL
   */
  async getAuthUrl(): Promise<BingOAuthResponse> {
    try {
      console.log('BingOAuthAPI: Making GET request to /api/oauth/bing/auth-url');
      const client = await this.getAuthenticatedClient();
      const response = await client.get('/api/oauth/bing/auth-url');
      console.log('BingOAuthAPI: Response received:', response.data);
      return response.data;
    } catch (error) {
      console.error('BingOAuthAPI: Error getting Bing OAuth URL:', error);
      throw error;
    }
  }

  /**
   * Get Bing Webmaster connection status
   */
  async getStatus(): Promise<BingOAuthStatus> {
    try {
      const client = await this.getAuthenticatedClient();
      const response = await client.get('/bing/status');
      return response.data;
    } catch (error) {
      console.error('Error getting Bing OAuth status:', error);
      throw error;
    }
  }

  /**
   * Disconnect a Bing Webmaster site
   */
  async disconnectSite(tokenId: number): Promise<{ success: boolean; message: string }> {
    try {
      const client = await this.getAuthenticatedClient();
      const response = await client.delete(`/bing/disconnect/${tokenId}`);
      return response.data;
    } catch (error) {
      console.error('Error disconnecting Bing site:', error);
      throw error;
    }
  }

  /**
   * Health check for Bing OAuth service
   */
  async healthCheck(): Promise<{ status: string; service: string; timestamp: string; version: string }> {
    try {
      const response = await apiClient.get('/bing/health');
      return response.data;
    } catch (error) {
      console.error('Error checking Bing OAuth health:', error);
      throw error;
    }
  }
}

export const bingOAuthAPI = new BingOAuthAPI();
