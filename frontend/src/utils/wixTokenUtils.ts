/**
 * Wix Token Utilities
 * Functions for validating and refreshing Wix OAuth tokens
 */

import { apiClient } from '../api/client';

interface WixTokens {
  accessToken?: {
    value: string;
    expiresAt?: string;
  };
  refreshToken?: {
    value: string;
  };
  access_token?: string;
  refresh_token?: string;
  expires_in?: number;
}

interface TokenValidationResult {
  valid: boolean;
  accessToken: string | null;
  needsRefresh: boolean;
  needsReconnect: boolean;
}

/**
 * Get Wix tokens from sessionStorage
 */
export function getWixTokens(): WixTokens | null {
  try {
    const tokensRaw = sessionStorage.getItem('wix_tokens');
    if (!tokensRaw) return null;
    return JSON.parse(tokensRaw);
  } catch (error) {
    console.error('Error parsing Wix tokens:', error);
    return null;
  }
}

/**
 * Extract access token from token structure
 */
export function extractAccessToken(tokens: WixTokens | null): string | null {
  if (!tokens) return null;
  return tokens.accessToken?.value || tokens.access_token || null;
}

/**
 * Extract refresh token from token structure
 */
export function extractRefreshToken(tokens: WixTokens | null): string | null {
  if (!tokens) return null;
  return tokens.refreshToken?.value || tokens.refresh_token || null;
}

/**
 * Refresh Wix access token using refresh token
 */
export async function refreshWixToken(refreshToken: string): Promise<WixTokens | null> {
  try {
    const response = await apiClient.post('/api/wix/refresh-token', {
      refresh_token: refreshToken
    });

    if (response.data.success) {
      // Create new token structure matching Wix SDK format
      const newTokens: WixTokens = {
        accessToken: {
          value: response.data.access_token
        },
        refreshToken: {
          value: response.data.refresh_token || refreshToken // Keep old refresh token if new one not provided
        },
        access_token: response.data.access_token,
        refresh_token: response.data.refresh_token || refreshToken
      };

      // Update sessionStorage
      try {
        sessionStorage.setItem('wix_tokens', JSON.stringify(newTokens));
        sessionStorage.setItem('wix_connected', 'true');
      } catch (e) {
        console.error('Error saving refreshed tokens:', e);
      }

      return newTokens;
    }

    return null;
  } catch (error: any) {
    console.error('Error refreshing Wix token:', error);
    return null;
  }
}

/**
 * Check if token is expired based on expiresAt timestamp
 */
function isTokenExpired(tokens: WixTokens): boolean {
  if (tokens.accessToken?.expiresAt) {
    try {
      const expiresAt = new Date(tokens.accessToken.expiresAt);
      return expiresAt < new Date();
    } catch (e) {
      // If we can't parse, assume not expired (will validate during publish)
      return false;
    }
  }
  // If no expiration info, we can't tell - assume valid for now
  // Real validation happens during actual API call
  return false;
}

/**
 * Validate and refresh Wix tokens proactively
 * Returns access token if valid, or null if needs reconnection
 * 
 * Strategy:
 * 1. Check if tokens exist
 * 2. Check if token is expired (if expiration info available)
 * 3. If expired, attempt refresh
 * 4. If refresh fails or no refresh token, needs reconnection
 * 5. Real validation happens during actual publish (we catch 401/403 errors)
 */
export async function validateAndRefreshWixTokens(): Promise<TokenValidationResult> {
  const tokens = getWixTokens();
  
  if (!tokens) {
    return {
      valid: false,
      accessToken: null,
      needsRefresh: false,
      needsReconnect: true
    };
  }

  const accessToken = extractAccessToken(tokens);
  const refreshToken = extractRefreshToken(tokens);

  if (!accessToken) {
    return {
      valid: false,
      accessToken: null,
      needsRefresh: false,
      needsReconnect: true
    };
  }

  // Check if token is expired (if we have expiration info)
  const expired = isTokenExpired(tokens);

  if (!expired) {
    // Token appears valid (not expired or no expiration info)
    // We'll do real validation during publish
    return {
      valid: true,
      accessToken: accessToken,
      needsRefresh: false,
      needsReconnect: false
    };
  }

  // Token is expired, try to refresh
  if (!refreshToken) {
    return {
      valid: false,
      accessToken: null,
      needsRefresh: false,
      needsReconnect: true
    };
  }

  // Attempt to refresh token
  const refreshedTokens = await refreshWixToken(refreshToken);
  
  if (refreshedTokens) {
    const newAccessToken = extractAccessToken(refreshedTokens);
    if (newAccessToken) {
      return {
        valid: true,
        accessToken: newAccessToken,
        needsRefresh: true,
        needsReconnect: false
      };
    }
  }

  // Refresh failed, needs reconnection
  return {
    valid: false,
    accessToken: null,
    needsRefresh: false,
    needsReconnect: true
  };
}

