/**
 * Bing Webmaster OAuth React Hook
 * Manages Bing Webmaster Tools OAuth2 authentication state and operations
 */

import { useState, useCallback } from 'react';
import { bingOAuthAPI, BingOAuthStatus, BingOAuthResponse } from '../api/bingOAuth';

interface UseBingOAuthReturn {
  // Connection state
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
  totalSites: number;
  
  // Loading states
  isLoading: boolean;
  isConnecting: boolean;
  
  // Actions
  connect: () => Promise<void>;
  disconnect: (tokenId: number) => Promise<void>;
  refreshStatus: () => Promise<void>;
  
  // Error handling
  error: string | null;
  clearError: () => void;
}

export const useBingOAuth = (): UseBingOAuthReturn => {
  const [connected, setConnected] = useState<boolean>(false);
  const [sites, setSites] = useState<Array<any>>([]);
  const [totalSites, setTotalSites] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isConnecting, setIsConnecting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [lastStatusCheck, setLastStatusCheck] = useState<number>(0);

  /**
   * Check Bing Webmaster connection status
   */
  const checkStatus = useCallback(async () => {
    // Throttle status checks to prevent excessive API calls
    const now = Date.now();
    const THROTTLE_MS = 10000; // 10 seconds - status doesn't change frequently
    
    if (now - lastStatusCheck < THROTTLE_MS) {
      console.log('Bing OAuth: Status check throttled (10s)');
      return;
    }
    
    try {
      setIsLoading(true);
      setLastStatusCheck(now);
      console.log('Bing OAuth: Checking status...');
      const status: BingOAuthStatus = await bingOAuthAPI.getStatus();
      
      console.log('Bing OAuth: Status response:', status);
      setConnected(status.connected);
      setSites(status.sites || []);
      setTotalSites(status.total_sites);
      
      console.log('Bing OAuth status checked:', {
        connected: status.connected,
        sitesCount: status.sites?.length || 0,
        totalSites: status.total_sites
      });
    } catch (error) {
      console.error('Error checking Bing OAuth status:', error);
      setConnected(false);
      setSites([]);
      setTotalSites(0);
      setError('Failed to check Bing Webmaster connection status');
    } finally {
      setIsLoading(false);
    }
  }, [lastStatusCheck]);

  /**
   * Connect to Bing Webmaster Tools
   */
  const connect = useCallback(async () => {
    try {
      setIsConnecting(true);
      setError(null);
      console.log('Bing OAuth: Initiating connection...');
      
      // 1. Get the auth URL from backend
      const authData: BingOAuthResponse = await bingOAuthAPI.getAuthUrl();
      
      // 2. Redirect the user
      window.location.href = authData.auth_url;
      
    } catch (error) {
      console.error('Error connecting to Bing Webmaster:', error);
      setError(error instanceof Error ? error.message : 'Failed to connect to Bing Webmaster');
    } finally {
      setIsConnecting(false);
    }
  }, []);

  /**
   * Disconnect a Bing Webmaster site
   */
  const disconnect = useCallback(async (tokenId: number) => {
    try {
      console.log('Bing OAuth: Disconnecting site with token ID:', tokenId);
      await bingOAuthAPI.disconnectSite(tokenId);
      console.log('Bing OAuth: Site disconnected successfully');
      
      // Refresh status after disconnection
      await checkStatus();
    } catch (error) {
      console.error('Error disconnecting Bing site:', error);
      setError(error instanceof Error ? error.message : 'Failed to disconnect Bing Webmaster site');
    }
  }, [checkStatus]);

  /**
   * Refresh connection status
   */
  const refreshStatus = useCallback(async () => {
    await checkStatus();
  }, [checkStatus]);

  /**
   * Clear error state
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Note: Status check is now handled by the parent component to avoid duplicate API calls

  return {
    connected,
    sites,
    totalSites,
    isLoading,
    isConnecting,
    connect,
    disconnect,
    refreshStatus,
    error,
    clearError
  };
};
