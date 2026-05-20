import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@clerk/clerk-react';
import { gscAPI, GSCSite } from '../api/gsc';
import { cachedAnalyticsAPI } from '../api/cachedAnalytics';

interface UseGSCBrainstormConnectionReturn {
  gscConnected: boolean;
  gscSites: GSCSite[] | null;
  isConnecting: boolean;
  connectError: string | null;
  checkConnection: () => Promise<boolean>;
  connectGSC: () => Promise<void>;
}

export const useGSCBrainstormConnection = (): UseGSCBrainstormConnectionReturn => {
  const { getToken } = useAuth();
  const [gscConnected, setGscConnected] = useState(false);
  const [gscSites, setGscSites] = useState<GSCSite[] | null>(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectError, setConnectError] = useState<string | null>(null);

  useEffect(() => {
    try {
      gscAPI.setAuthTokenGetter(async () => {
        try {
          return await getToken();
        } catch {
          return null;
        }
      });
    } catch {}
  }, [getToken]);

  const checkConnection = useCallback(async (): Promise<boolean> => {
    try {
      const status = await gscAPI.getStatus();
      if (status.connected) {
        setGscConnected(true);
        if (status.sites && status.sites.length) {
          setGscSites(status.sites);
        }
        setConnectError(null);
        return true;
      } else {
        setGscConnected(false);
        setGscSites(null);
        return false;
      }
    } catch {
      setGscConnected(false);
      setGscSites(null);
      return false;
    }
  }, []);

  useEffect(() => {
    checkConnection();
  }, [checkConnection]);

  const connectGSC = useCallback(async (): Promise<void> => {
    setIsConnecting(true);
    setConnectError(null);

    try {
      try {
        await gscAPI.clearIncomplete();
      } catch (e) {
        console.log('Clear incomplete failed:', e);
      }

      try {
        await gscAPI.disconnect();
      } catch (e) {
        console.log('Disconnect failed:', e);
      }

      setGscConnected(false);
      setGscSites(null);

      const { auth_url } = await gscAPI.getAuthUrl();

      const popup = window.open(
        auth_url,
        'gsc-auth',
        'width=600,height=700,scrollbars=yes,resizable=yes',
      );

      if (!popup) {
        setConnectError('Popup blocked. Please allow popups for this site.');
        setIsConnecting(false);
        return;
      }

      await new Promise<void>((resolve) => {
        let messageHandled = false;

        const messageHandler = (event: MessageEvent) => {
          if (messageHandled) return;
          if (!event?.data || typeof event.data !== 'object') return;
          const { type } = event.data as { type?: string };

          if (type === 'GSC_AUTH_SUCCESS' || type === 'GSC_AUTH_ERROR') {
            messageHandled = true;
            try { popup.close(); } catch {}
            window.removeEventListener('message', messageHandler);

            if (type === 'GSC_AUTH_SUCCESS') {
              checkConnection().then(() => {
                cachedAnalyticsAPI.forceRefreshAnalyticsData(['gsc']).catch(console.error);
                resolve();
              });
            } else {
              setConnectError('Google Search Console connection was cancelled or failed.');
              resolve();
            }
          }
        };

        window.addEventListener('message', messageHandler);

        const safetyTimeout = setTimeout(() => {
          if (!messageHandled) {
            try { if (!popup.closed) popup.close(); } catch {}
            window.removeEventListener('message', messageHandler);
            checkConnection().then(() => resolve());
          }
        }, 3 * 60 * 1000);

        const pollInterval = setInterval(() => {
          try {
            if (popup.closed) {
              clearInterval(pollInterval);
              clearTimeout(safetyTimeout);
              window.removeEventListener('message', messageHandler);
              if (!messageHandled) {
                checkConnection().then(() => resolve());
              }
            }
          } catch {
            clearInterval(pollInterval);
          }
        }, 1000);
      });
    } catch (error) {
      console.error('GSC OAuth error:', error);
      setConnectError(
        error instanceof Error ? error.message : 'Failed to connect Google Search Console.',
      );
    } finally {
      setIsConnecting(false);
    }
  }, [checkConnection]);

  return {
    gscConnected,
    gscSites,
    isConnecting,
    connectError,
    checkConnection,
    connectGSC,
  };
};