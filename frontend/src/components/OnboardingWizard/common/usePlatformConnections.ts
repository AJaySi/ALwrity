import { useState, useEffect } from 'react';
import { apiClient } from '../../../api/client';

export const usePlatformConnections = () => {
  const [connectedPlatforms, setConnectedPlatforms] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  // Trusted origins come from the backend (validated redirect origin) + current origin.
  // This prevents accepting messages from unexpected popups or mismatched environments.
  const [trustedOrigins, setTrustedOrigins] = useState<string[]>([window.location.origin]);

  // Handle Wix OAuth popup messages
  useEffect(() => {
    const handler = (event: MessageEvent) => {
      // Only accept postMessage events from trusted origins to avoid spoofing.
      if (!trustedOrigins.includes(event.origin)) return;
      if (!event.data || typeof event.data !== 'object') return;

      if (event.data.type === 'WIX_OAUTH_SUCCESS') {
        setConnectedPlatforms(prev => {
          const updated = [...prev.filter(id => id !== 'wix'), 'wix'];
          return updated;
        });
        setToastMessage('Wix account connected successfully!');
        setShowToast(true);
      }
      if (event.data.type === 'WIX_OAUTH_ERROR') {
        setToastMessage('Wix connection failed. Please try again.');
        setShowToast(true);
      }
    };
    window.addEventListener('message', handler);
    return () => window.removeEventListener('message', handler);
  }, [setConnectedPlatforms, setToastMessage, trustedOrigins]);

  // Fallback: detect wix_connected query param after full-page redirect
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('wix_connected') === 'true') {
      setConnectedPlatforms(prev => {
        const updated = [...prev.filter(id => id !== 'wix'), 'wix'];
        return updated;
      });
      setToastMessage('Wix account connected successfully!');
      setShowToast(true);
      // Clean URL
      const clean = window.location.pathname + window.location.hash;
      window.history.replaceState({}, document.title, clean || '/');
    }
  }, [setConnectedPlatforms, setToastMessage]);

  const handleWixConnect = async () => {
    try {
      // We persist the current location before redirecting so we can reliably
      // return users to where they started (onboarding/blog writer).
      // Store current page URL BEFORE redirecting (critical for proper redirect back)
      // This ensures we can redirect back to the correct page (e.g., Blog Writer) after OAuth
      // Only store if not already set (allows WixConnectModal to override if needed)
      // WixConnectModal will always override when connecting from Blog Writer
      const currentUrl = window.location.href;
      try {
        if (!sessionStorage.getItem('wix_oauth_redirect')) {
          sessionStorage.setItem('wix_oauth_redirect', currentUrl);
        }
      } catch (e) {
        // Ignore storage errors
      }

      // Fetch canonical OAuth configuration from the backend (validated origin + PKCE).
      const response = await apiClient.get('/api/oauth/wix/auth-url');
      const { auth_url: authUrl, oauth_data: oauthData, trusted_origins: apiOrigins, client_id: clientId } = response.data;

      // Fetch canonical OAuth configuration from the backend (validated origin + PKCE).
      const response = await apiClient.get('/api/oauth/wix/auth-url');
      const { auth_url: authUrl, oauth_data: oauthData, trusted_origins: apiOrigins, client_id: clientId } = response.data;

      if (!authUrl || !oauthData) {
        throw new Error('Missing Wix OAuth configuration from backend.');
      }

      // Merge backend-supplied origins to match environment-driven redirect validation.
      if (Array.isArray(apiOrigins) && apiOrigins.length > 0) {
        setTrustedOrigins(prev => Array.from(new Set([...prev, ...apiOrigins])));
      }
      
      // Persist OAuth data robustly so callback can always recover it.
      // The Wix SDK requires this PKCE + state payload to validate the callback.
      // 1) SessionStorage for same-origin same-tab flows
      try { sessionStorage.setItem('wix_oauth_data', JSON.stringify(oauthData)); } catch {}
      // 2) Key by state so callback can look up by state value
      try { sessionStorage.setItem(`wix_oauth_data_${oauthData.state}`, JSON.stringify(oauthData)); } catch {}
      // 2.1) Persist client ID for callback usage
      try {
        if (clientId) {
          sessionStorage.setItem('wix_oauth_client_id', clientId);
        }
      } catch {}
      // 3) window.name persists across top-level redirects even when origin changes
      try { (window as any).name = `WIX_OAUTH::${btoa(JSON.stringify(oauthData))}`; } catch {}
      window.location.href = authUrl;
    } catch (error) {
      console.error('Wix connection error:', error);
      throw error;
    }
  };

  const handleConnect = async (platformId: string) => {
    setIsLoading(true);
    try {
      if (platformId === 'wix') {
        await handleWixConnect();
        return;
      }
      
      // For other platforms, you can add their connection logic here
      
    } catch (error) {
      console.error('Connection error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return {
    connectedPlatforms,
    setConnectedPlatforms,
    isLoading,
    showToast,
    setShowToast,
    toastMessage,
    setToastMessage,
    handleConnect
  };
};
