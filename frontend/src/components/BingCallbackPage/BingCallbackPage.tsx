import React, { useEffect, useState } from 'react';
import { Box, CircularProgress, Typography, Alert } from '@mui/material';
import { getOAuthPostMessageTargetOrigin } from '../../utils/oauthOrigins';

const BingCallbackPage: React.FC = () => {
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const run = async () => {
      try {
        const params = new URLSearchParams(window.location.search);
        const code = params.get('code');
        const state = params.get('state');
        const error = params.get('error');
        
        if (error) {
          throw new Error(`OAuth error: ${error}`);
        }
        
        if (!code || !state) {
          throw new Error('Missing OAuth parameters');
        }

        try {
          // Call backend to complete token exchange
          await fetch(`/bing/callback?code=${encodeURIComponent(code)}&state=${encodeURIComponent(state)}`, {
            method: 'GET',
            credentials: 'include'
          });
        } catch (e) {
          // Continue; backend HTML callback may already be handled in popup
        }

        // Notify opener and close if this is a popup window
        try {
          const targetOrigin = getOAuthPostMessageTargetOrigin('bing');
          (window.opener || window.parent)?.postMessage({ type: 'BING_OAUTH_SUCCESS', success: true }, targetOrigin);
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
          const targetOrigin = getOAuthPostMessageTargetOrigin('bing');
          (window.opener || window.parent)?.postMessage({ type: 'BING_OAUTH_ERROR', success: false, error: e?.message || 'OAuth callback failed' }, targetOrigin);
          if (window.opener) window.close();
        } catch {}
      }
    };
    run();
  }, []);

  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      minHeight="100vh"
      padding={3}
    >
      {error ? (
        <Alert severity="error" sx={{ mb: 2 }}>
          <Typography variant="h6">Connection Failed</Typography>
          <Typography>{error}</Typography>
        </Alert>
      ) : (
        <>
          <CircularProgress sx={{ mb: 2 }} />
          <Typography variant="h6">Connecting to Bing Webmaster Tools...</Typography>
          <Typography variant="body2" color="text.secondary">
            Please wait while we complete the authentication process.
          </Typography>
        </>
      )}
    </Box>
  );
};

export default BingCallbackPage;
