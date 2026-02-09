/**
 * WordPress OAuth2 API client for ALwrity frontend.
 * Handles WordPress.com OAuth2 authentication flow.
 */

import { apiClient } from './client';

export interface WordPressOAuthResponse {
  provider_id: string;
  url: string;
  state?: string;
  details?: {
    redirect_uri?: string;
    trusted_origins?: string[];
  };
}

export interface WordPressOAuthStatus {
  connected: boolean;
  sites: WordPressOAuthSite[];
  total_sites: number;
}

export interface WordPressOAuthSite {
  id: number;
  blog_id: string;
  blog_url: string;
  scope: string;
  created_at: string;
}

class WordPressOAuthAPI {
  private baseUrl = '/wp';
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
   * Get WordPress OAuth2 authorization URL
   */
  async getAuthUrl(): Promise<WordPressOAuthResponse> {
    try {
      const client = await this.getAuthenticatedClient();
      const response = await client.get(`/api/oauth/wordpress/auth-url`);
      return response.data;
    } catch (error) {
      console.error('WordPress OAuth API: Error getting auth URL:', error);
      throw error;
    }
  }

  /**
   * Get WordPress OAuth connection status
   */
  async getStatus(): Promise<WordPressOAuthStatus> {
    try {
      const client = await this.getAuthenticatedClient();
      const response = await client.get(`${this.baseUrl}/status`);
      return response.data;
    } catch (error) {
      console.error('WordPress OAuth API: Error getting status:', error);
      throw error;
    }
  }

  /**
   * Disconnect a WordPress site
   */
  async disconnectSite(tokenId: number): Promise<{ success: boolean; message: string }> {
    try {
      const client = await this.getAuthenticatedClient();
      const response = await client.delete(`${this.baseUrl}/disconnect/${tokenId}`);
      return response.data;
    } catch (error) {
      console.error('WordPress OAuth API: Error disconnecting site:', error);
      throw error;
    }
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: string; service: string; timestamp: string; version: string }> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/health`);
      return response.data;
    } catch (error) {
      console.error('WordPress OAuth API: Health check failed:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const wordpressOAuthAPI = new WordPressOAuthAPI();
export default wordpressOAuthAPI;
