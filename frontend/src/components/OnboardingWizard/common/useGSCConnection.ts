import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@clerk/clerk-react';
import { gscAPI, type GSCSite } from '../../../api/gsc';
import { unifiedOAuthClient } from '../../../api/unifiedOAuthClient';

const DEPRECATED_GSC_ROUTES_REMOVAL_DATE = '2026-06-30';

export const useGSCConnection = () => {
  const { getToken } = useAuth();
  const [gscSites, setGscSites] = useState<GSCSite[] | null>(null);
  const [connectedPlatforms, setConnectedPlatforms] = useState<string[]>([]);

  useEffect(() => {
    // Ensure GSC API uses authenticated client for GSC analytics/sitemaps endpoints.
    try {
      gscAPI.setAuthTokenGetter(async () => {
        try {
          return await getToken();
        } catch {
          return null;
        }
      });
    } catch {
      // no-op
    }
  }, [getToken]);

  const refreshGSCStatus = useCallback(async () => {
    const status = await unifiedOAuthClient.getConnectionStatus('gsc');
    if (!status.connected) {
      setConnectedPlatforms(prev => prev.filter(p => p !== 'gsc'));
      setGscSites(null);
      return;
    }

    setConnectedPlatforms(prev => Array.from(new Set([...prev, 'gsc'])));

    try {
      const sitesResponse = await gscAPI.getSites();
      setGscSites(sitesResponse.sites ?? []);
    } catch {
      setGscSites([]);
    }
  }, []);

  useEffect(() => {
    (async () => {
      try {
        await refreshGSCStatus();
      } catch {
        setConnectedPlatforms(prev => prev.filter(p => p !== 'gsc'));
        setGscSites(null);
      }
    })();
  }, [refreshGSCStatus]);

  const handleGSCConnect = async () => {
    try {
      // Keep /gsc/* callback endpoint for backward compatibility only.
      console.warn(`GSC legacy callback endpoint is deprecated and scheduled for removal after ${DEPRECATED_GSC_ROUTES_REMOVAL_DATE}`);

      const authResponse = await unifiedOAuthClient.getAuthUrl('gsc');
      const { auth_url, trusted_origins = [] } = authResponse;

      const oauthNonce = crypto.randomUUID();
      const popup = window.open(
        auth_url,
        `gsc-auth-${oauthNonce}`,
        'width=600,height=700,scrollbars=yes,resizable=yes'
      );

      if (!popup) {
        window.location.href = auth_url;
        return;
      }

      let messageHandled = false;
      const messageHandler = (event: MessageEvent) => {
        if (messageHandled || !event?.data || typeof event.data !== 'object') return;

        const allowedOrigins = new Set<string>([
          ...trusted_origins,
          window.location.origin
        ]);

        if (!allowedOrigins.has(event.origin)) return;

        const { type, nonce } = event.data as { type?: string; nonce?: string };
        if (nonce !== oauthNonce) return;

        if (type === 'GSC_AUTH_SUCCESS' || type === 'GSC_AUTH_ERROR') {
          messageHandled = true;
          try { popup.close(); } catch {
            // no-op
          }
          window.removeEventListener('message', messageHandler);

          if (type === 'GSC_AUTH_SUCCESS') {
            void refreshGSCStatus();
          }

          setTimeout(() => {
            window.location.href = '/onboarding?step=5';
          }, 250);
        }
      };

      window.addEventListener('message', messageHandler);

      setTimeout(() => {
        try {
          if (!popup.closed) popup.close();
        } catch {
          // no-op
        }
        window.removeEventListener('message', messageHandler);
      }, 3 * 60 * 1000);
    } catch (error) {
      console.error('GSC OAuth error:', error);
      throw error;
    }
  };

  return {
    gscSites,
    connectedPlatforms,
    setConnectedPlatforms,
    setGscSites,
    handleGSCConnect,
    refreshGSCStatus
  };
};
