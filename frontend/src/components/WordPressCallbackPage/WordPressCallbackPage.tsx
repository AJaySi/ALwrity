import React, { useEffect, useState } from 'react';
import { Box, CircularProgress, Typography, Alert } from '@mui/material';
import { apiClient } from '../../api/client';

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
          // Use apiClient to ensure base URL is correct (handles proxy/cors)
          // Request JSON response to verify success
          const response = await apiClient.get('/wp/callback', {
            params: { code, state, format: 'json' },
            headers: {
              'Accept': 'application/json'
            }
          });

          if (response.data && response.data.success) {
            const { blog_url, blog_id, sites } = response.data;
            
            // Notify opener and close
            try {
              const payload = { 
                type: 'WPCOM_OAUTH_SUCCESS', 
                success: true,
                blogUrl: blog_url,
                blogId: blog_id,
                sites: sites 
              } as any;
              
              (window.opener || window.parent)?.postMessage(payload, '*');
              if (window.opener) {
                window.close();
                return;
              }
            } catch {}

            // Fallback: redirect back to onboarding
            window.location.replace('/onboarding?step=5&wp_connected=true');
          } else {
            throw new Error(response.data?.error || 'Connection failed');
          }
        } catch (backendError: any) {
          console.error('WordPress OAuth Callback Error:', backendError);
          const msg = backendError.response?.data?.error || backendError.message || 'OAuth callback failed';
          throw new Error(msg);
        }
      } catch (e: any) {
        setError(e?.message || 'OAuth callback failed');
        try {
          (window.opener || window.parent)?.postMessage({ 
            type: 'WPCOM_OAUTH_ERROR', 
            success: false, 
            error: e?.message || 'OAuth callback failed' 
          }, '*');
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


