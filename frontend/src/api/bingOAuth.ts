/**
 * Bing Webmaster OAuth API Client
 * Handles Bing Webmaster Tools OAuth2 authentication flow
 */

import { apiClient } from './client';

export interface BingOAuthSite {
  id: number;
  connection_id: number;
  connected: boolean;
  scope: string;
  created_at: string;
  site_count: number;
  sites: Array<{
    id: string;
    name: string;
    url: string;
    status: string;
  }>;
}

export interface BingOAuthStatus {
  connected: boolean;
  sites: BingOAuthSite[];
  total_sites: number;
}

export interface BingOAuthResponse {
  auth_url: string;
  state: string;
}

export interface BingCallbackResponse {
  success: boolean;
  message: string;
  connection_id?: number;
  connected?: boolean;
  site_count?: number;
}

class BingOAuthAPI {
  /**
   * Get Bing Webmaster OAuth authorization URL
   */
  async getAuthUrl(): Promise<BingOAuthResponse> {
    try {
      console.log('BingOAuthAPI: Requesting /bing/auth/url');
      const response = await apiClient.get('/bing/auth/url');
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
      const response = await apiClient.get('/bing/status');
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
      const response = await apiClient.delete(`/bing/disconnect/${tokenId}`);
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
