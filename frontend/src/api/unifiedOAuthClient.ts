/**
 * Unified OAuth Client Implementation
 * 
 * Provides a single, consistent interface for all OAuth operations
 * across all platforms using the unified OAuth router.
 */

import { z } from 'zod';

// Import existing API client for base functionality
import { apiClient } from './client';

// Import types and error classes
import type {
  OAuthTokenInfo,
  OAuthConnectionStatus,
  OAuthAuthUrlResponse,
  OAuthCallbackResponse,
  OAuthProvidersResponse,
  OAuthRefreshResponse,
  OAuthDisconnectResponse,
  OAuthProviderConfig,
} from './unifiedOAuth';

import {
  OAuthError,
  OAuthValidationError,
  OAuthNetworkError,
  OAuthAuthenticationError,
  OAuthProvidersResponseSchema,
  OAuthAuthUrlResponseSchema,
  OAuthCallbackResponseSchema,
  OAuthConnectionStatusSchema,
  OAuthRefreshResponseSchema,
  OAuthDisconnectResponseSchema,
} from './unifiedOAuth';

/**
 * Unified OAuth Client Class
 * 
 * Provides a single interface for all OAuth operations across all platforms.
 * Replaces platform-specific OAuth clients with unified patterns.
 */
export class UnifiedOAuthClient {
  private apiClient = apiClient;

  constructor() {
    this.apiClient = apiClient;
  }

  /**
   * Get list of available OAuth providers
   * 
   * Returns all registered OAuth providers with their connection status.
   */
  async getAvailableProviders(): Promise<OAuthProvidersResponse> {
    try {
      const response = await this.apiClient.get('/oauth/providers');
      
      // Validate response schema
      const validatedResponse = OAuthProvidersResponseSchema.parse(response.data);
      
      return {
        success: true,
        providers: validatedResponse.providers
      };
    } catch (error) {
      throw new OAuthNetworkError('Failed to retrieve OAuth providers', undefined, error);
    }
  }

  /**
   * Get OAuth authorization URL for a specific provider
   * 
   * @param providerKey - The provider identifier (gsc, bing, wordpress, wix)
   * @returns Promise<OAuthAuthUrlResponse> - Authorization URL response
   */
  async getAuthUrl(providerKey: string): Promise<OAuthAuthUrlResponse> {
    try {
      // Validate provider key
      if (!['gsc', 'bing', 'wordpress', 'wix'].includes(providerKey)) {
        throw new OAuthValidationError(`Invalid provider: ${providerKey}. Supported providers: gsc, bing, wordpress, wix`);
      }

      const response = await this.apiClient.get(`/oauth/${providerKey}/auth`);
      
      // Validate response schema
      const validatedResponse = OAuthAuthUrlResponseSchema.parse(response.data);
      
      return {
        success: true,
        provider_key: validatedResponse.provider_key,
        display_name: validatedResponse.display_name,
        auth_url: validatedResponse.auth_url,
        state: validatedResponse.state,
        trusted_origins: validatedResponse.trusted_origins
      };
    } catch (error) {
      if (error.response?.status === 400) {
        throw new OAuthValidationError(`Invalid provider: ${providerKey}`, providerKey, error.response?.data);
      }
      if (error.response?.status === 404) {
        throw new OAuthValidationError(`Provider not found: ${providerKey}`, providerKey, error.response?.data);
      }
      throw new OAuthNetworkError(`Failed to get auth URL for ${providerKey}`, providerKey, error);
    }
  }

  /**
   * Handle OAuth callback for a specific provider
   * 
   * @param providerKey - The provider identifier
   * @param code - Authorization code from OAuth callback
   * @param state - State parameter from OAuth callback
   * @returns Promise<OAuthCallbackResponse> - Callback handling response
   */
  async handleCallback(
    providerKey: string,
    code: string,
    state: string
  ): Promise<OAuthCallbackResponse> {
    try {
      // Validate provider key
      if (!['gsc', 'bing', 'wordpress', 'wix'].includes(providerKey)) {
        throw new OAuthValidationError(`Invalid provider: ${providerKey}. Supported providers: gsc, bing, wordpress, wix`);
      }

      const response = await this.apiClient.post(`/oauth/${providerKey}/callback`, {
        code,
        state
      });
      
      // Validate response schema
      const validatedResponse = OAuthCallbackResponseSchema.parse(response.data);
      
      return {
        success: validatedResponse.success,
        provider_key: validatedResponse.provider_key,
        display_name: validatedResponse.display_name,
        connected: validatedResponse.connected,
        message: validatedResponse.message,
        error: validatedResponse.error,
        connection_id: validatedResponse.connection_id,
        site_count: validatedResponse.site_count
      };
    } catch (error) {
      if (error.response?.status === 400) {
        throw new OAuthValidationError(`Invalid callback data for ${providerKey}`, providerKey, error.response?.data);
      }
      if (error.response?.status === 404) {
        throw new OAuthValidationError(`Provider not found: ${providerKey}`, providerKey, error.response?.data);
      }
      throw new OAuthNetworkError(`Failed to handle callback for ${providerKey}`, providerKey, error);
    }
  }

  /**
   * Get connection status for a specific provider
   * 
   * @param providerKey - The provider identifier
   * @returns Promise<OAuthConnectionStatus> - Connection status response
   */
  async getConnectionStatus(providerKey: string): Promise<OAuthConnectionStatus> {
    try {
      // Validate provider key
      if (!['gsc', 'bing', 'wordpress', 'wix'].includes(providerKey)) {
        throw new OAuthValidationError(`Invalid provider: ${providerKey}. Supported providers: gsc, bing, wordpress, wix`);
      }

      const response = await this.apiClient.get(`/oauth/${providerKey}/status`);
      
      // Validate response schema
      const validatedResponse = OAuthConnectionStatusSchema.parse(response.data);
      
      return {
        success: true,
        provider: validatedResponse.provider_key,
        display_name: validatedResponse.display_name,
        connected: validatedResponse.connected,
        details: validatedResponse.details,
        error: validatedResponse.error
      };
    } catch (error) {
      if (error.response?.status === 400) {
        throw new OAuthValidationError(`Invalid provider: ${providerKey}`, providerKey, error.response?.data);
      }
      if (error.response?.status === 404) {
        throw new OAuthValidationError(`Provider not found: ${providerKey}`, providerKey, error.response?.data);
      }
      throw new OAuthNetworkError(`Failed to get connection status for ${providerKey}`, providerKey, error);
    }
  }

  /**
   * Refresh OAuth token for a specific provider
   * 
   * @param providerKey - The provider identifier
   * @returns Promise<OAuthRefreshResponse> - Token refresh response
   */
  async refreshToken(providerKey: string): Promise<OAuthRefreshResponse> {
    try {
      // Validate provider key
      if (!['gsc', 'bing', 'wordpress', 'wix'].includes(providerKey)) {
        throw new OAuthValidationError(`Invalid provider: ${providerKey}. Supported providers: gsc, bing, wordpress, wix`);
      }

      const response = await this.apiClient.post(`/oauth/${providerKey}/refresh`);
      
      // Validate response schema
      const validatedResponse = OAuthRefreshResponseSchema.parse(response.data);
      
      return {
        success: validatedResponse.success,
        provider_key: validatedResponse.provider_key,
        display_name: validatedResponse.display_name,
        message: validatedResponse.message,
        error: validatedResponse.error
      };
    } catch (error) {
      if (error.response?.status === 400) {
        throw new OAuthValidationError(`Provider does not support refresh: ${providerKey}`, providerKey, error.response?.data);
      }
      if (error.response?.status === 404) {
        throw new OAuthValidationError(`Provider not found: ${providerKey}`, providerKey, error.response?.data);
      }
      throw new OAuthNetworkError(`Failed to refresh token for ${providerKey}`, providerKey, error);
    }
  }

  /**
   * Disconnect OAuth connection for a specific provider
   * 
   * @param providerKey - The provider identifier
   * @returns Promise<OAuthDisconnectResponse> - Disconnection response
   */
  async disconnect(providerKey: string): Promise<OAuthDisconnectResponse> {
    try {
      // Validate provider key
      if (!['gsc', 'bing', 'wordpress', 'wix'].includes(providerKey)) {
        throw new OAuthValidationError(`Invalid provider: ${providerKey}. Supported providers: gsc, bing, wordpress, wix`);
      }

      const response = await this.apiClient.post(`/oauth/${providerKey}/disconnect`);
      
      // Validate response schema
      const validatedResponse = OAuthDisconnectResponseSchema.parse(response.data);
      
      return {
        success: validatedResponse.success,
        provider_key: validatedResponse.provider_key,
        display_name: validatedResponse.display_name,
        message: validatedResponse.message
      };
    } catch (error) {
      if (error.response?.status === 400) {
        throw new OAuthValidationError(`Provider does not support disconnection: ${providerKey}`, providerKey, error.response?.data);
      }
      if (error.response?.status === 404) {
        throw new OAuthValidationError(`Provider not found: ${providerKey}`, providerKey, error.response?.data);
      }
      throw new OAuthNetworkError(`Failed to disconnect from ${providerKey}`, providerKey, error);
    }
  }

  /**
   * Get comprehensive OAuth status for all providers
   * 
   * @returns Promise<OAuthProvidersResponse> - Status for all providers
   */
  async getAllProvidersStatus(): Promise<OAuthProvidersResponse> {
    try {
      const response = await this.apiClient.get('/oauth/providers');
      
      // Validate response schema
      const validatedResponse = OAuthProvidersResponseSchema.parse(response.data);
      
      return {
        success: true,
        providers: validatedResponse.providers
      };
    } catch (error) {
      throw new OAuthNetworkError('Failed to retrieve OAuth providers status', undefined, error);
    }
  }

  /**
   * Get token information for a specific provider
   * 
   * @param providerKey - The provider identifier
   * @returns Promise<OAuthTokenInfo> - Token information
   */
  async getTokenInfo(providerKey: string): Promise<OAuthTokenInfo> {
    try {
      // Get connection status which includes token info
      const statusResponse = await this.getConnectionStatus(providerKey);
      
      if (statusResponse.success && statusResponse.details) {
        // Extract token info from connection details
        const details = statusResponse.details as any;
        
        return {
          provider: statusResponse.provider_key,
          display_name: statusResponse.display_name,
          connected: statusResponse.connected,
          connected_at: details.connected_at,
          expires_at: details.expires_at,
          is_active: details.is_active,
          scope: details.scope,
          account_info: details.account_info
        };
      }
      
      // Return basic token info if no detailed info available
      return {
        provider: statusResponse.provider_key,
        display_name: statusResponse.display_name,
        connected: statusResponse.connected,
        is_active: false
      };
    } catch (error) {
      throw new OAuthNetworkError(`Failed to get token info for ${providerKey}`, providerKey, error);
    }
  }
}

// Export singleton instance
export const unifiedOAuthClient = new UnifiedOAuthClient();

// Export types and schemas for use in other components
export {
  OAuthProviderConfig,
  OAuthTokenInfo,
  OAuthConnectionStatus,
  OAuthAuthUrlResponse,
  OAuthCallbackResponse,
  OAuthProvidersResponse,
  OAuthRefreshResponse,
  OAuthDisconnectResponse,
  OAuthError,
  OAuthValidationError,
  OAuthNetworkError,
  OAuthAuthenticationError
};
