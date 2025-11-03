import { useState, useEffect } from 'react';
import { createClient, OAuthStrategy } from '@wix/sdk';

export const usePlatformConnections = () => {
  const [connectedPlatforms, setConnectedPlatforms] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');

  // Handle Wix OAuth popup messages
  useEffect(() => {
    const handler = (event: MessageEvent) => {
      const trusted = [window.location.origin, 'https://littery-sonny-unscrutinisingly.ngrok-free.dev'];
      if (!trusted.includes(event.origin)) return;
      if (!event.data || typeof event.data !== 'object') return;

      if (event.data.type === 'WIX_OAUTH_SUCCESS') {
        console.log('Wix OAuth success message received');
        setConnectedPlatforms(prev => {
          const updated = [...prev.filter(id => id !== 'wix'), 'wix'];
          console.log('Updated connected platforms via message:', updated);
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
  }, [setConnectedPlatforms, setToastMessage]);

  // Fallback: detect wix_connected query param after full-page redirect
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('wix_connected') === 'true') {
      console.log('Wix connected via URL param, updating state');
      setConnectedPlatforms(prev => {
        const updated = [...prev.filter(id => id !== 'wix'), 'wix'];
        console.log('Updated connected platforms:', updated);
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
      // Store current page URL BEFORE redirecting (critical for proper redirect back)
      // This ensures we can redirect back to the correct page (e.g., Blog Writer) after OAuth
      const currentUrl = window.location.href;
      try {
        // Only store if not already set (allows WixConnectModal to override if needed)
        if (!sessionStorage.getItem('wix_oauth_redirect')) {
          sessionStorage.setItem('wix_oauth_redirect', currentUrl);
          console.log('[Wix OAuth] Stored redirect URL:', currentUrl);
        } else {
          console.log('[Wix OAuth] Redirect URL already set, keeping existing:', sessionStorage.getItem('wix_oauth_redirect'));
        }
      } catch (e) {
        console.warn('[Wix OAuth] Failed to store redirect URL:', e);
      }

      // Use the working Wix OAuth flow from WixTestPage
      const wixClient = createClient({
        auth: OAuthStrategy({ clientId: '75d88e36-1c76-4009-b769-15f4654556df' })
      });

      const NGROK_ORIGIN = 'https://littery-sonny-unscrutinisingly.ngrok-free.dev';
      const redirectOrigin = window.location.origin.includes('localhost') ? NGROK_ORIGIN : window.location.origin;
      const redirectUri = `${redirectOrigin}/wix/callback`;
      const oauthData = await wixClient.auth.generateOAuthData(redirectUri);
      
      // Persist OAuth data robustly so callback can always recover it
      // 1) SessionStorage for same-origin same-tab flows
      try { sessionStorage.setItem('wix_oauth_data', JSON.stringify(oauthData)); } catch {}
      // 2) Key by state so callback can look up by state value
      try { sessionStorage.setItem(`wix_oauth_data_${oauthData.state}`, JSON.stringify(oauthData)); } catch {}
      // 3) window.name persists across top-level redirects even when origin changes
      try { (window as any).name = `WIX_OAUTH::${btoa(JSON.stringify(oauthData))}`; } catch {}
      const { authUrl } = await wixClient.auth.getAuthUrl(oauthData);
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
      console.log(`🔧 USE_PLATFORM_CONNECTIONS: Connecting to ${platformId}...`);
      console.log(`🔧 USE_PLATFORM_CONNECTIONS: Stack trace:`, new Error().stack);
      
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
