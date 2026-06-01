import React, { useEffect, useRef, useState } from 'react';
import { Box, CircularProgress, Typography, Alert } from '@mui/material';
import { createClient, OAuthStrategy } from '@wix/sdk';
import { apiClient } from '../../api/client';
import { WIX_CLIENT_ID } from '../../config/wixConfig';
import { storeEncrypted } from '../../utils/wixTokenStorage';

const FALLBACK_ORIGIN = 'http://localhost:3000';

const WixCallbackPage: React.FC = () => {
  const [error, setError] = useState<string | null>(null);
  const ranRef = useRef(false);

  useEffect(() => {
    if (ranRef.current) return;
    ranRef.current = true;

    const run = async () => {
      try {
        const wixClient = createClient({ auth: OAuthStrategy({ clientId: WIX_CLIENT_ID }) });
        const { code, state, error: wixError, errorDescription } = wixClient.auth.parseFromUrl();
        if (wixError) {
          setError(`${wixError}: ${errorDescription || ''}`);
          return;
        }
        if (!code) {
          setError('Missing authorization code in URL');
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

        console.log('[WixCallbackPage] oauthData keys:', Object.keys(oauthData || {}));

        let accessToken: string | null = null;
        let refreshToken: string | null = null;
        let expiresIn: number | null = null;
        let siteInfo: any = null;

        // === PRIMARY PATH: Client-side exchange (Wix SDK has internal code_verifier) ===
        try {
          console.log('[WixCallbackPage] Attempting client-side token exchange...');
          const tokens = await wixClient.auth.getMemberTokens(code, state, oauthData);
          wixClient.auth.setTokens(tokens);
          accessToken = (tokens as any)?.accessToken?.value || (tokens as any)?.access_token || null;
          refreshToken = (tokens as any)?.refreshToken?.value || (tokens as any)?.refresh_token || null;
          expiresIn = (tokens as any)?.accessToken?.expiresAt
            ? Math.floor(((tokens as any).accessToken.expiresAt - Date.now()) / 1000)
            : (tokens as any)?.expires_in || null;
          console.log('[WixCallbackPage] Client-side exchange OK. accessToken present:', !!accessToken);
        } catch (clientError: any) {
          console.error('[WixCallbackPage] Client-side exchange failed:', clientError);
          setError(`Client-side token exchange failed: ${clientError?.message || clientError}`);
          return;
        }

        // === SECONDARY PATH: Send token to backend for storage ===
        if (accessToken) {
          try {
            console.log('[WixCallbackPage] Sending token to backend for storage...');
            const response = await apiClient.post('/api/wix/auth/callback', {
              access_token: accessToken,
              refresh_token: refreshToken,
              expires_in: expiresIn,
              token_type: 'Bearer',
            });
            if (response.data.success) {
              siteInfo = response.data.site_info || null;
              console.log('[WixCallbackPage] Backend stored token successfully');
            } else {
              console.warn('[WixCallbackPage] Backend store returned:', response.data.message);
            }
          } catch (backendError: any) {
            console.warn('[WixCallbackPage] Backend store failed (non-fatal):', backendError);
          }
        }

        // Store in current origin's storage
        try {
          if (accessToken) await storeEncrypted('wix_access_token', accessToken);
        } catch {}
        localStorage.setItem('wix_connected', 'true');
        sessionStorage.setItem('wix_connected', 'true');

        // Cleanup oauth data
        sessionStorage.removeItem('wix_oauth_data');
        if (state) sessionStorage.removeItem(`wix_oauth_data_${state}`);
        localStorage.removeItem('wix_oauth_data');

        // Persist across cross-origin redirect via window.name
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

        // Build redirect URL
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
