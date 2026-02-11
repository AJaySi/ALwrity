/**
 * Bing Webmaster OAuth API Client
 * 
 * Handles Bing Webmaster Tools OAuth2 authentication flow.
 * Now uses unified OAuth client for consistent patterns.
 */

import { apiClient } from './client';
import { unifiedOAuthClient } from './unifiedOAuthClient';

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
  trusted_origins: string[];
}

export interface BingCallbackResponse {
  success: boolean;
  message: string;
  connection_id?: number;
  connected?: boolean;
  site_count?: number;
}

/**
 * Bing OAuth API Class
 * 
 * Provides Bing Webmaster Tools OAuth2 authentication flow.
 * Uses unified OAuth client for consistent patterns across all platforms.
 */
export class BingOAuthAPI {
  private unifiedClient = unifiedOAuthClient;

  /**
   * Get Bing Webmaster OAuth authorization URL
   * 
   * @deprecated Use unifiedOAuthClient.getAuthUrl('bing') instead
   */
  async getAuthUrl(): Promise<BingOAuthResponse> {
    console.warn('BingOAuthAPI.getAuthUrl() is deprecated. Use unifiedOAuthClient.getAuthUrl("bing") instead');
    
    try {
      const response = await this.unifiedClient.getAuthUrl('bing');
      
      return {
        auth_url: response.auth_url,
        state: response.state,
        trusted_origins: response.trusted_origins
      };
    } catch (error) {
      console.error('BingOAuthAPI: Error getting Bing OAuth URL:', error);
      throw error;
    }
  }

  /**
   * Get Bing Webmaster connection status
   * 
   * @deprecated Use unifiedOAuthClient.getConnectionStatus('bing') instead
   */
  async getStatus(): Promise<BingOAuthStatus> {
    console.warn('BingOAuthAPI.getStatus() is deprecated. Use unifiedOAuthClient.getConnectionStatus("bing") instead');
    
    try {
      const response = await this.unifiedClient.getConnectionStatus('bing');
      
      // Transform unified response to Bing-specific format
      const details = response.details as any;
      const sites = details?.sites || [];
      
      return {
        connected: response.connected,
        sites: sites.map((site: any) => ({
          id: site.id,
          connection_id: site.connection_id,
          connected: site.connected,
          scope: site.scope,
          created_at: site.created_at,
          site_count: sites.length,
          sites: sites.map((site: any) => ({
            id: site.id,
            name: site.name,
            url: site.url,
            status: site.status
          }))
        })),
        total_sites: sites.length
      };
    } catch (error) {
      console.error('Error getting Bing OAuth status:', error);
      throw error;
    }
  }

  /**
   * Disconnect a Bing Webmaster site
   * 
   * @deprecated Use unifiedOAuthClient.disconnect('bing') instead
   */
  async disconnectSite(tokenId: number): Promise<{ success: boolean; message: string }> {
    console.warn('BingOAuthAPI.disconnectSite() is deprecated. Use unifiedOAuthClient.disconnect("bing") instead');
    
    try {
      const response = await this.unifiedClient.disconnect('bing');
      
      return {
        success: response.success,
        message: response.message
      };
    } catch (error) {
      console.error('Error disconnecting Bing site:', error);
      throw error;
    }
  }

  /**
   * Health check for Bing OAuth service
   * 
   * @deprecated Use unified OAuth client health checks instead
   */
  async healthCheck(): Promise<{ status: string; service: string; timestamp: string; version: string }> {
    console.warn('BingOAuthAPI.healthCheck() is deprecated. Use unified OAuth client methods instead');
    
    try {
      const statusResponse = await this.unifiedClient.getConnectionStatus('bing');
      
      return {
        status: statusResponse.connected ? 'healthy' : 'unhealthy',
        service: 'bing-webmaster-oauth',
        timestamp: new Date().toISOString(),
        version: '2.0.0-unified'
      };
    } catch (error) {
      console.error('Error checking Bing OAuth health:', error);
      throw error;
    }
  }
}

// Export the instance for backward compatibility
export const bingOAuthAPI = new BingOAuthAPI();
