import React, { useEffect, useState } from 'react';
import { Box, CircularProgress, Typography, Alert } from '@mui/material';

const YouTubeCallbackPage: React.FC = () => {
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const run = async () => {
      try {
        const params = new URLSearchParams(window.location.search);
        const code = params.get('code');
        const state = params.get('state');
        const errorParam = params.get('error');

        if (errorParam) {
          throw new Error(`OAuth error: ${errorParam}`);
        }

        if (!code || !state) {
          throw new Error('Missing OAuth parameters');
        }

        // Call backend to complete token exchange (fallback if backend HTML postMessage didn't work)
        try {
          await fetch(`/api/youtube/oauth/callback?code=${encodeURIComponent(code)}&state=${encodeURIComponent(state)}&format=json`, {
            method: 'GET',
            credentials: 'include',
          });
        } catch {
          // Backend HTML callback is the primary path — this is a fallback
        }

        // Notify opener and close if popup
        try {
          (window.opener || window.parent)?.postMessage({ type: 'YOUTUBE_OAUTH_SUCCESS', success: true }, '*');
          if (window.opener) {
            window.close();
            return;
          }
        } catch {}

        // Fallback: redirect
        window.location.replace('/youtube-creator');
      } catch (e: any) {
        setError(e?.message || 'OAuth callback failed');
        try {
          (window.opener || window.parent)?.postMessage({ type: 'YOUTUBE_OAUTH_ERROR', success: false, error: e?.message || 'OAuth callback failed' }, '*');
          if (window.opener) window.close();
        } catch {}
      }
    };
    run();
  }, []);

  return (
    <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" minHeight="100vh" padding={3}>
      {error ? (
        <Alert severity="error" sx={{ mb: 2 }}>
          <Typography variant="h6">Connection Failed</Typography>
          <Typography>{error}</Typography>
        </Alert>
      ) : (
        <>
          <CircularProgress sx={{ mb: 2 }} />
          <Typography variant="h6">Connecting to YouTube...</Typography>
          <Typography variant="body2" color="text.secondary">
            Please wait while we complete the authentication process.
          </Typography>
        </>
      )}
    </Box>
  );
};

export default YouTubeCallbackPage;
