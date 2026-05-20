import React, { useEffect, useState } from 'react';
import { Box, CircularProgress, Typography, Alert } from '@mui/material';
import { createClient, OAuthStrategy } from '@wix/sdk';
import { apiClient } from '../../api/client';

const FALLBACK_ORIGIN = 'http://localhost:3000';

const WixCallbackPage: React.FC = () => {
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const run = async () => {
      try {
        const wixClient = createClient({ auth: OAuthStrategy({ clientId: '75d88e36-1c76-4009-b769-15f4654556df' }) });
        const { code, state, error, errorDescription } = wixClient.auth.parseFromUrl();
        if (error) {
          setError(`${error}: ${errorDescription || ''}`);
          return;
        }

        let oauthData: any | null = null;
        const saved = sessionStorage.getItem('wix_oauth_data') || localStorage.getItem('wix_oauth_data');
        if (saved) {
          try { oauthData = JSON.parse(saved); } catch {}
        }
        if (!oauthData && state) {
          const byState = sessionStorage.getItem(`wix_oauth_data_${state}`);
          if (byState) {
            try { oauthData = JSON.parse(byState); } catch {}
          }
        }
        if (!oauthData && typeof window.name === 'string' && window.name.startsWith('WIX_OAUTH::')) {
          try { oauthData = JSON.parse(atob(window.name.replace('WIX_OAUTH::', ''))); } catch {}
        }
        if (!oauthData) {
          setError('Missing OAuth state. Please start the connection again.');
          return;
        }

        let accessToken: string | null = null;
        let siteInfo: any = null;

        try {
          const response = await apiClient.post('/api/wix/auth/callback', { code, state });
          if (response.data.success) {
            const { tokens, site_info } = response.data;
            accessToken = tokens?.access_token || tokens?.accessToken?.value || null;
            siteInfo = site_info || null;
          } else {
            throw new Error(response.data.message || 'Connection failed');
          }
        } catch (backendError: any) {
          console.error('Backend exchange failed, falling back to client-side:', backendError);
          const tokens = await wixClient.auth.getMemberTokens(code, state, oauthData);
          wixClient.auth.setTokens(tokens);
          accessToken = (tokens as any)?.accessToken?.value || (tokens as any)?.access_token || null;
        }

        // Store in current origin's storage (may be ngrok — not accessible from localhost,
        // but useful if the callback runs on the same origin as the app)
        try {
          if (accessToken) localStorage.setItem('wix_access_token', accessToken);
        } catch {}
        localStorage.setItem('wix_connected', 'true');
        sessionStorage.setItem('wix_connected', 'true');

        // Cleanup oauth data
        sessionStorage.removeItem('wix_oauth_data');
        if (state) sessionStorage.removeItem(`wix_oauth_data_${state}`);
        localStorage.removeItem('wix_oauth_data');

        // CRITICAL: Put access_token + site_info into window.name so it survives
        // the cross-origin redirect (ngrok → localhost). window.name persists
        // across same-tab navigations even when the origin changes.
        try {
          const payload = { access_token: accessToken, site_info: siteInfo };
          (window as any).name = `WIX_RESULT::${btoa(JSON.stringify(payload))}`;
        } catch {}

        // Notify opener if popup
        try {
          const targetOrigin = window.location.ancestorOrigins?.[0] || '*';
          (window.opener || window.parent)?.postMessage(
            { type: 'WIX_OAUTH_SUCCESS', success: true, access_token: accessToken, site_info: siteInfo },
            targetOrigin
          );
          if (window.opener) { window.close(); return; }
        } catch {}

        localStorage.setItem('blogwriter_current_phase', 'publish');
        localStorage.setItem('blogwriter_user_selected_phase', 'true');

        // Build redirect URL. oauthData.redirect_to was set by WixConnectModal
        // to the user's actual origin (e.g. http://localhost:3000/blog-writer#publish).
        // sessionStorage is per-origin so wix_oauth_redirect may be null on ngrok.
        let redirectUrl = oauthData?.redirect_to || sessionStorage.getItem('wix_oauth_redirect');
        if (redirectUrl) {
          sessionStorage.removeItem('wix_oauth_redirect');
          try {
            const urlObj = new URL(redirectUrl);
            urlObj.searchParams.set('wix_connected', 'true');
            redirectUrl = urlObj.toString();
          } catch {
            redirectUrl = `${redirectUrl}?wix_connected=true`;
          }
        } else {
          // Fallback: construct localhost URL
          redirectUrl = `${FALLBACK_ORIGIN}/blog-writer?wix_connected=true#publish`;
        }

        window.location.replace(redirectUrl);
      } catch (e: any) {
        setError(e?.message || 'OAuth callback failed');
        try {
          (window.opener || window.parent)?.postMessage({ type: 'WIX_OAUTH_ERROR', success: false, error: e?.message || 'OAuth callback failed' }, '*');
          if (window.opener) window.close();
        } catch {}
      }
    };
    run();
  }, []);

  return (
    <Box sx={{ p: 4, maxWidth: 680, mx: 'auto' }}>
      {!error ? (
        <Box display="flex" alignItems="center" gap={2}>
          <CircularProgress size={22} />
          <Typography>Completing Wix sign‑in…</Typography>
        </Box>
      ) : (
        <Alert severity="error">{error}</Alert>
      )}
    </Box>
  );
};

export default WixCallbackPage;
