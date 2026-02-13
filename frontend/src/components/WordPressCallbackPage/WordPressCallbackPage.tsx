import React, { useEffect, useState } from 'react';
import { Box, CircularProgress, Typography, Alert } from '@mui/material';
import { getOAuthPostMessageTargetOrigin } from '../../utils/oauthOrigins';

const WordPressCallbackPage: React.FC = () => {
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const run = async () => {
      try {
        const params = new URLSearchParams(window.location.search);
        const code = params.get('code');
        const state = params.get('state');
        if (!code || !state) {
          throw new Error('Missing OAuth parameters');
        }

        try {
          // Call backend to complete token exchange
          await fetch(`/wp/callback?code=${encodeURIComponent(code)}&state=${encodeURIComponent(state)}`, {
            method: 'GET',
            credentials: 'include'
          });
        } catch (e) {
          // Continue; backend HTML callback may already be handled in popup
        }

        // Notify opener and close if this is a popup window
        try {
          const targetOrigin = getOAuthPostMessageTargetOrigin('wordpress');
          (window.opener || window.parent)?.postMessage({ type: 'WPCOM_OAUTH_SUCCESS', success: true }, targetOrigin);
          if (window.opener) {
            window.close();
            return;
          }
        } catch {}

        // Fallback: redirect back to onboarding
        window.location.replace('/onboarding?step=5');
      } catch (e: any) {
        setError(e?.message || 'OAuth callback failed');
        try {
          const targetOrigin = getOAuthPostMessageTargetOrigin('wordpress');
          (window.opener || window.parent)?.postMessage({ type: 'WPCOM_OAUTH_ERROR', success: false, error: e?.message || 'OAuth callback failed' }, targetOrigin);
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
          <Typography>Completing WordPress sign‑in…</Typography>
        </Box>
      ) : (
        <Alert severity="error">{error}</Alert>
      )}
    </Box>
  );
};

export default WordPressCallbackPage;

