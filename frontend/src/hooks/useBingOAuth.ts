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
      
      // Get authorization URL
      console.log('Bing OAuth: Calling bingOAuthAPI.getAuthUrl()...');
      const authData: BingOAuthResponse = await bingOAuthAPI.getAuthUrl();
      console.log('Bing OAuth: Got auth URL:', authData.auth_url);
      
      // Open OAuth popup window
      const popup = window.open(
        authData.auth_url,
        'bing-oauth',
        'width=600,height=700,scrollbars=yes,resizable=yes'
      );
      
      if (!popup) {
        throw new Error('Failed to open Bing OAuth popup. Please allow popups for this site.');
      }

      // Track if we've already handled success/error to avoid duplicate processing
      let messageHandled = false;

      // Listen for popup completion and messages
      const messageHandler = (event: MessageEvent) => {
        console.log('Bing OAuth: Message received from any source:', {
          origin: event.origin,
          data: event.data,
          dataType: event.data?.type,
          source: event.source === popup ? 'our-popup' : 'other',
          expectedOrigin: 'https://littery-sonny-unscrutinisingly.ngrok-free.dev',
          timestamp: new Date().toISOString()
        });
        
        // Log the full message data for debugging
        console.log('Bing OAuth: Full message data:', JSON.stringify(event.data, null, 2));
        
        // Check if message is from our expected origin (more reliable than checking source)
        console.log('Bing OAuth: Checking origin match...', {
          receivedOrigin: event.origin,
          expectedOrigin: 'https://littery-sonny-unscrutinisingly.ngrok-free.dev',
          originMatch: event.origin === 'https://littery-sonny-unscrutinisingly.ngrok-free.dev'
        });
        
        if (event.origin === 'https://littery-sonny-unscrutinisingly.ngrok-free.dev') {
          console.log('Bing OAuth: Message from expected origin, processing...');
          console.log('Bing OAuth: Message data:', event.data);
          console.log('Bing OAuth: Message data type:', event.data?.type);
          
          if (event.data?.type === 'BING_OAUTH_SUCCESS') {
            console.log('Bing OAuth: Success message received:', event.data);
            messageHandled = true;
            popup.close();
            window.removeEventListener('message', messageHandler);
            
            // Refresh status after successful connection
            setTimeout(() => {
              checkStatus();
            }, 1000);
          } else if (event.data?.type === 'BING_OAUTH_ERROR') {
            console.error('Bing OAuth: Error message received:', event.data);
            messageHandled = true;
            popup.close();
            window.removeEventListener('message', messageHandler);
            setError(event.data.error || 'Bing OAuth connection failed');
          } else {
            console.log('Bing OAuth: Unknown message type:', event.data?.type);
            console.log('Bing OAuth: Full message data:', event.data);
          }
        } else {
          console.log('Bing OAuth: Message from unexpected origin, ignoring:', event.origin);
        }
      };

      window.addEventListener('message', messageHandler);
      
      // Test if popup is working
      console.log('Bing OAuth: Popup opened, waiting for messages...');
      
      const checkClosed = setInterval(() => {
        if (popup.closed) {
          clearInterval(checkClosed);
          window.removeEventListener('message', messageHandler);
          console.log('Bing OAuth: Popup closed, refreshing status...');
          
          if (!messageHandled) {
            console.log('Bing OAuth: Popup closed without receiving success/error message');
          } else {
            console.log('Bing OAuth: Popup closed after successful message handling');
          }
          
          // Refresh status after OAuth completion
          setTimeout(() => {
            checkStatus();
          }, 1000);
        }
      }, 1000);
      
    } catch (error) {
      console.error('Error connecting to Bing Webmaster:', error);
      setError(error instanceof Error ? error.message : 'Failed to connect to Bing Webmaster');
    } finally {
      setIsConnecting(false);
    }
  }, [checkStatus]);

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
