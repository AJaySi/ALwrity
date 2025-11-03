import React, { useEffect, useState } from 'react';
import { Box, CircularProgress, Typography, Alert } from '@mui/material';
import { createClient, OAuthStrategy } from '@wix/sdk';
import { apiClient } from '../../api/client';

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
        // Recover oauthData via multiple fallbacks
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
          try { oauthData = JSON.parse(atob(window.name.replace('WIX_OAUTH::',''))); } catch {}
        }
        if (!oauthData) {
          setError('Missing OAuth state. Please start the connection again.');
          return;
        }
        // Use the originally generated state to avoid SDK "Invalid _state" errors
        const tokens = await wixClient.auth.getMemberTokens(code, state, oauthData);
        wixClient.auth.setTokens(tokens);
        // Persist tokens for subsequent API calls on this tab
        try { sessionStorage.setItem('wix_tokens', JSON.stringify(tokens)); } catch {}
        // optional: ping backend to mark connected
        try { await apiClient.get('/api/wix/test/connection/status'); } catch {}
        // Cleanup saved oauth data
        sessionStorage.removeItem('wix_oauth_data');
        sessionStorage.removeItem(`wix_oauth_data_${state}`);
        localStorage.removeItem('wix_oauth_data');
        try { (window as any).name = ''; } catch {}
        // Mark frontend session as connected for onboarding UI
        sessionStorage.setItem('wix_connected', 'true');
        // Notify opener (if opened as popup) and close; otherwise fallback to redirect
        try {
          const payload = { type: 'WIX_OAUTH_SUCCESS', success: true, tokens } as any;
          (window.opener || window.parent)?.postMessage(payload, '*');
          if (window.opener) {
            window.close();
            return;
          }
        } catch {}
        // Fallback redirect for same-tab flow - check if we have a stored redirect URL
        const redirectUrl = sessionStorage.getItem('wix_oauth_redirect');
        console.log('[Wix Callback] Checking redirect URL:', redirectUrl);
        if (redirectUrl) {
          console.log('[Wix Callback] Redirecting to stored URL:', redirectUrl);
          sessionStorage.removeItem('wix_oauth_redirect');
          window.location.replace(redirectUrl);
        } else {
          // Default to onboarding if no redirect URL stored
          console.warn('[Wix Callback] No redirect URL found, defaulting to onboarding');
          window.location.replace('/onboarding?step=5&wix_connected=true');
        }
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


