/**
 * Unified OAuth Client for ALwrity
 * 
 * Provides a single, consistent interface for all OAuth operations
 * across all platforms (GSC, Bing, WordPress, Wix).
 * 
 * Replaces platform-specific OAuth clients with unified patterns.
 */

import { z } from 'zod';

// Base OAuth types
export interface OAuthTokenInfo {
  provider: string;
  display_name: string;
  connected: boolean;
  connected_at?: string;
  expires_at?: string;
  is_active: boolean;
  scope?: string;
  account_info?: {
    email?: string;
    name?: string;
    account_id?: string;
  };
}

export interface OAuthConnectionStatus {
  success: boolean;
  provider: string;
  display_name: string;
  connected: boolean;
  details?: any;
  error?: string;
}

export interface OAuthAuthUrlResponse {
  provider_key: string;
  display_name: string;
  auth_url: string;
  state: string;
  trusted_origins: string[];
}

export interface OAuthCallbackResponse {
  success: boolean;
  provider_key: string;
  display_name: string;
  connected?: boolean;
  message: string;
  error?: string;
  connection_id?: number;
  site_count?: number;
}

export interface OAuthProvidersResponse {
  providers: Array<{
    key: string;
    display_name: string;
    connected: boolean;
    details?: any;
    error?: string;
  }>;
}

export interface OAuthRefreshResponse {
  success: boolean;
  provider_key: string;
  display_name: string;
  message: string;
  error?: string;
}

export interface OAuthDisconnectResponse {
  success: boolean;
  provider_key: string;
  display_name: string;
  message: string;
}

// Configuration schema
export const OAuthProviderConfig = z.object({
  provider: z.string(),
  display_name: z.string(),
  requires_redirect: z.boolean().default(false),
  supports_refresh: z.boolean().default(true),
  supports_disconnect: z.boolean().default(true),
  scopes: z.array(z.string()).optional(),
  auth_methods: z.array(z.string()).optional(),
});

export type OAuthProviderType = z.infer<typeof OAuthProviderConfig>;

// API response schemas
export const OAuthTokenInfoSchema = z.object({
  provider: z.string(),
  display_name: z.string(),
  connected: z.boolean(),
  connected_at: z.string().optional(),
  expires_at: z.string().optional(),
  is_active: z.boolean(),
  scope: z.string().optional(),
  account_info: z.object({
    email: z.string().optional(),
    name: z.string().optional(),
    account_id: z.string().optional(),
  }).optional(),
});

export const OAuthConnectionStatusSchema = z.object({
  success: z.boolean(),
  provider: z.string(),
  display_name: z.string(),
  connected: z.boolean(),
  details: z.any().optional(),
  error: z.string().optional(),
});

export const OAuthAuthUrlResponseSchema = z.object({
  provider_key: z.string(),
  display_name: z.string(),
  auth_url: z.string(),
  state: z.string(),
  trusted_origins: z.array(z.string()),
});

export const OAuthCallbackResponseSchema = z.object({
  success: z.boolean(),
  provider_key: z.string(),
  display_name: z.string(),
  connected: z.boolean().optional(),
  message: z.string(),
  error: z.string().optional(),
  connection_id: z.number().optional(),
  site_count: z.number().optional(),
});

export const OAuthProvidersResponseSchema = z.object({
  providers: z.array(z.object({
    key: z.string(),
    display_name: z.string(),
    connected: z.boolean(),
    details: z.any().optional(),
    error: z.string().optional(),
  })),
});

export const OAuthRefreshResponseSchema = z.object({
  success: z.boolean(),
  provider_key: z.string(),
  display_name: z.string(),
  message: z.string(),
  error: z.string().optional(),
});

export const OAuthDisconnectResponseSchema = z.object({
  success: z.boolean(),
  provider_key: z.string(),
  display_name: z.string(),
  message: z.string(),
});

// Error types
export class OAuthError extends Error {
  constructor(
    message: string,
    public provider?: string,
    public statusCode?: number,
    public details?: any
  ) {
    super(message);
    this.name = 'OAuthError';
    this.provider = provider;
    this.statusCode = statusCode;
    this.details = details;
  }
}

export class OAuthValidationError extends OAuthError {
  constructor(message: string, provider?: string, details?: any) {
    super(message, provider, 400, details);
    this.name = 'OAuthValidationError';
  }
}

export class OAuthNetworkError extends OAuthError {
  constructor(message: string, provider?: string, details?: any) {
    super(message, provider, 0, details);
    this.name = 'OAuthNetworkError';
  }
}

export class OAuthAuthenticationError extends OAuthError {
  constructor(message: string, provider?: string, details?: any) {
    super(message, provider, 401, details);
    this.name = 'OAuthAuthenticationError';
  }
}
