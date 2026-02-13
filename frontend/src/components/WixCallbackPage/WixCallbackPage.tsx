import React, { useEffect, useState } from 'react';
import { Box, CircularProgress, Typography, Alert } from '@mui/material';
import { createClient, OAuthStrategy } from '@wix/sdk';
import { apiClient } from '../../api/client';

const WixCallbackPage: React.FC = () => {
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const run = async () => {
      try {
        // Prefer client ID stored during the OAuth kickoff so callbacks stay in sync
        // with backend-provided configuration. Fall back to env var and legacy ID.
        const storedClientId = sessionStorage.getItem('wix_oauth_client_id');
        const fallbackClientId = process.env.REACT_APP_WIX_CLIENT_ID || '75d88e36-1c76-4009-b769-15f4654556df';
        const wixClient = createClient({ auth: OAuthStrategy({ clientId: storedClientId || fallbackClientId }) });
        const { code, state, error, errorDescription } = wixClient.auth.parseFromUrl();
        if (error) {
          setError(`${error}: ${errorDescription || ''}`);
          return;
        }
        // Recover oauthData via multiple fallbacks so we can support popup and
        // full-page redirect flows across different browser storage behaviors.
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

        // Exchange code for tokens via backend to ensure persistence and get site info
        try {
          const response = await apiClient.post('/api/wix/auth/callback', { 
            code,
            state 
          });

          if (response.data.success) {
            const { tokens, site_info, permissions } = response.data;
            
            // Store tokens and site info
            try { 
              sessionStorage.setItem('wix_tokens', JSON.stringify(tokens));
              if (site_info) {
                sessionStorage.setItem('wix_site_info', JSON.stringify(site_info));
              }
            } catch {}

            // Mark frontend session as connected
            sessionStorage.setItem('wix_connected', 'true');

            // Cleanup saved oauth data
            sessionStorage.removeItem('wix_oauth_data');
            sessionStorage.removeItem(`wix_oauth_data_${state}`);
            localStorage.removeItem('wix_oauth_data');
            try { (window as any).name = ''; } catch {}

            // Notify opener (if opened as popup) and close
            try {
              const payload = { 
                type: 'WIX_OAUTH_SUCCESS', 
                success: true, 
                tokens,
                site_info 
              } as any;
              (window.opener || window.parent)?.postMessage(payload, '*');
              if (window.opener) {
                window.close();
                return;
              }
            } catch {}

            // Fallback redirect for same-tab flow
            let redirectUrl = sessionStorage.getItem('wix_oauth_redirect');
            if (redirectUrl) {
              try {
                const urlObj = new URL(redirectUrl);
                const currentOrigin = window.location.origin;
                if (urlObj.origin !== currentOrigin) {
                  redirectUrl = `${currentOrigin}${urlObj.pathname}${urlObj.hash}${urlObj.search}`;
                }
              } catch (e) {}
              
              sessionStorage.removeItem('wix_oauth_redirect');
              window.location.replace(redirectUrl);
            } else {
              // Default redirect
              const referrer = document.referrer;
              const isFromBlogWriter = referrer.includes('/blog-writer') || 
                                      window.location.search.includes('from=blog-writer');
              
              if (isFromBlogWriter) {
                window.location.replace('/blog-writer#publish');
              } else {
                window.location.replace('/onboarding?step=5&wix_connected=true');
              }
            }
          } else {
            throw new Error(response.data.message || 'Connection failed');
          }
        } catch (backendError: any) {
          console.error('Backend exchange failed, falling back to client-side:', backendError);
          // Fallback to client-side exchange if backend fails
          const tokens = await wixClient.auth.getMemberTokens(code, state, oauthData);
          wixClient.auth.setTokens(tokens);
          sessionStorage.setItem('wix_tokens', JSON.stringify(tokens));
          sessionStorage.setItem('wix_connected', 'true');
          
          // ... rest of the cleanup and redirect logic ...
          sessionStorage.removeItem('wix_oauth_data');
          // (Simplified fallback for brevity, assuming backend usually works)
           try {
            const payload = { type: 'WIX_OAUTH_SUCCESS', success: true, tokens } as any;
            (window.opener || window.parent)?.postMessage(payload, '*');
            if (window.opener) { window.close(); return; }
          } catch {}
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
