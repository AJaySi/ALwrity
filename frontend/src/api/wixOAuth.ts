/**
 * Wix OAuth API Client
 * 
 * Handles Wix OAuth2 authentication flow.
 * Now uses unified OAuth client for consistent patterns.
 */

import { apiClient } from './client';
import { unifiedOAuthClient } from './unifiedOAuthClient';
import type {
  OAuthAuthUrlResponse,
  OAuthCallbackResponse,
  OAuthConnectionStatus,
  OAuthDisconnectResponse
} from './unifiedOAuth';

export interface WixOAuthSite {
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
    permissions: string[];
  }>;
}

export interface WixOAuthStatus {
  connected: boolean;
  sites: WixOAuthSite[];
  total_sites: number;
  permissions?: {
    can_create_posts: boolean;
    can_edit_posts: boolean;
    can_delete_posts: boolean;
    can_manage_categories: boolean;
    can_manage_tags: boolean;
  };
  error?: string;
}

export interface WixAuthUrlResponse {
  auth_url: string;
  state: string;
  oauth_data?: {
    codeVerifier: string;
    codeChallenge: string;
    redirectUri: string;
  };
}

export interface WixConnectionStatus {
  connected: boolean;
  site_id?: string;
  member_id?: string;
  site_info?: {
    siteId: string;
    siteName: string;
    siteUrl: string;
  };
  permissions?: {
    can_create_posts: boolean;
    can_edit_posts: boolean;
    can_delete_posts: boolean;
    can_manage_categories: boolean;
    can_manage_tags: boolean;
  };
  error?: string;
}

/**
 * Wix OAuth API Class
 * 
 * Provides Wix-specific OAuth operations while using the unified OAuth client
 * for consistent patterns and error handling.
 */
class WixOAuthAPI {
  private client = unifiedOAuthClient;

  /**
   * Get Wix OAuth authorization URL
   * 
   * @deprecated Use unifiedOAuthClient.getAuthUrl('wix') instead
   * This method is preserved for backward compatibility but will be removed in future versions.
   */
  async getAuthUrl(): Promise<WixAuthUrlResponse> {
    console.warn('Wix Router: getAuthUrl() is deprecated. Use unifiedOAuthClient.getAuthUrl("wix") instead');
    
    try {
      // Use unified OAuth client for consistent patterns
      const authResponse: OAuthAuthUrlResponse = await this.client.getAuthUrl('wix');
      
      // Transform unified response to Wix-specific format
      const wixResponse: WixAuthUrlResponse = {
        auth_url: authResponse.auth_url,
        state: authResponse.state
      };

      // Add Wix-specific OAuth data if available
      if ((authResponse as any).oauth_data) {
        wixResponse.oauth_data = {
          codeVerifier: (authResponse as any).oauth_data.codeVerifier,
          codeChallenge: (authResponse as any).oauth_data.codeChallenge,
          redirectUri: (authResponse as any).oauth_data.redirectUri
        };
      }

      return wixResponse;
    } catch (error: Error) {
      // Fall back to legacy service if unified client fails
      console.warn('Unified client failed, falling back to legacy Wix service:', error);
      return await this.legacyGetAuthUrl();
    }
  }

  /**
   * Handle Wix OAuth callback
   * 
   * @deprecated Use unifiedOAuthClient.handleCallback('wix', code, state) instead
   * This method is preserved for backward compatibility but will be removed in future versions.
   */
  async handleCallback(code: string, state: string): Promise<{
    success: boolean;
    tokens?: any;
    site_info?: any;
    permissions?: any;
    message: string;
    error?: string;
  }> {
    console.warn('Wix Router: handleCallback() is deprecated. Use unifiedOAuthClient.handleCallback("wix", code, state) instead');
    
    try {
      // Use unified OAuth client for consistent patterns
      const callbackResponse: OAuthCallbackResponse = await this.client.handleCallback('wix', code, state);
      
      if (callbackResponse.success) {
        return {
          success: true,
          tokens: {
            access_token: (callbackResponse as any).access_token,
            refresh_token: (callbackResponse as any).refresh_token,
            expires_in: (callbackResponse as any).expires_in,
            token_type: (callbackResponse as any).token_type || 'Bearer'
          },
          site_info: (callbackResponse as any).details?.site_info,
          permissions: (callbackResponse as any).details?.permissions,
          message: "Successfully connected to Wix"
        };
      } else {
        return {
          success: false,
          message: callbackResponse.message || "Wix OAuth callback failed",
          error: callbackResponse.error
        };
      }
    } catch (error: Error) {
      // Fall back to legacy service if unified client fails
      console.warn('Unified client failed, falling back to legacy Wix service:', error);
      return await this.legacyHandleCallback(code, state);
    }
  }

  /**
   * Get Wix OAuth connection status
   * 
   * @deprecated Use unifiedOAuthClient.getConnectionStatus('wix') instead
   * This method is preserved for backward compatibility but will be removed in future versions.
   */
  async getConnectionStatus(): Promise<WixOAuthStatus> {
    console.warn('Wix Router: getConnectionStatus() is deprecated. Use unifiedOAuthClient.getConnectionStatus("wix") instead');
    
    try {
      // Use unified OAuth client for consistent patterns
      const statusResponse: OAuthConnectionStatus = await this.client.getConnectionStatus('wix');
      
      // Transform unified response to Wix-specific format
      const details = statusResponse.details || {};
      const sites = details.sites || [];
      
      return {
        connected: statusResponse.connected,
        sites: sites.map((site: any) => ({
          id: site.site_id || site.id,
          connection_id: site.id,
          connected: true,
          scope: site.scope || 'wix_management',
          created_at: site.created_at || new Date().toISOString(),
          site_count: 1,
          sites: [{
            id: site.site_id || site.id,
            name: site.site_name || site.name || 'Wix Site',
            url: site.site_url || site.url,
            permissions: site.permissions || []
          }]
        })),
        total_sites: sites.length,
        permissions: details.permissions,
        error: statusResponse.error
      };
    } catch (error: Error) {
      // Fall back to legacy service if unified client fails
      console.warn('Unified client failed, falling back to legacy Wix service:', error);
      return await this.legacyGetConnectionStatus();
    }
  }

  /**
   * Disconnect Wix account
   * 
   * @deprecated Use unifiedOAuthClient.disconnect('wix') instead
   * This method is preserved for backward compatibility but will be removed in future versions.
   */
  async disconnect(): Promise<{
    success: boolean;
    message: string;
    error?: string;
  }> {
    console.warn('Wix Router: disconnect() is deprecated. Use unifiedOAuthClient.disconnect("wix") instead');
    
    try {
      // Use unified OAuth client for consistent patterns
      const disconnectResponse: OAuthDisconnectResponse = await this.client.disconnect('wix');
      
      return {
        success: disconnectResponse.success,
        message: disconnectResponse.message || "Wix account disconnected successfully"
      };
    } catch (error: Error) {
      // Fall back to legacy service if unified client fails
      console.warn('Unified client failed, falling back to legacy Wix service:', error);
      return await this.legacyDisconnect();
    }
  }

  /**
   * Health check for Wix OAuth service
   */
  async healthCheck(): Promise<{
    status: 'healthy' | 'degraded' | 'unhealthy';
    timestamp: string;
    details: any;
  }> {
    try {
      const response = await apiClient.get('/api/wix/test/connection/status');
      return {
        status: 'healthy',
        timestamp: new Date().toISOString(),
        details: response.data
      };
    } catch (error: Error) {
      return {
        status: 'unhealthy',
        timestamp: new Date().toISOString(),
        details: { error: error.message }
      };
    }
  }

  // Legacy fallback methods (for backward compatibility during transition)
  private async legacyGetAuthUrl(): Promise<WixAuthUrlResponse> {
    try {
      const response = await apiClient.get('/api/wix/test/auth/url');
      return response.data;
    } catch (error: Error) {
      throw new Error(`Legacy Wix auth URL generation failed: ${error.message}`);
    }
  }

  private async legacyHandleCallback(code: string, state: string): Promise<any> {
    try {
      const response = await apiClient.post('/api/wix/auth/callback', { code, state });
      return response.data;
    } catch (error: Error) {
      throw new Error(`Legacy Wix callback handling failed: ${error.message}`);
    }
  }

  private async legacyGetConnectionStatus(): Promise<WixOAuthStatus> {
    try {
      const response = await apiClient.get('/api/wix/connection/status');
      return response.data;
    } catch (error: Error) {
      throw new Error(`Legacy Wix status check failed: ${error.message}`);
    }
  }

  private async legacyDisconnect(): Promise<any> {
    try {
      const response = await apiClient.post('/api/wix/disconnect');
      return response.data;
    } catch (error: Error) {
      throw new Error(`Legacy Wix disconnect failed: ${error.message}`);
    }
  }
}

// Export singleton instance
export const wixOAuthAPI = new WixOAuthAPI();

// Export types and class for use in other components
export { WixOAuthAPI };
