import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  CircularProgress,
  Alert
} from '@mui/material';
import { usePlatformConnections } from '../../../components/OnboardingWizard/common/usePlatformConnections';

interface WixConnectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConnectionSuccess?: () => void;
}

export const WixConnectModal: React.FC<WixConnectModalProps> = ({
  isOpen,
  onClose,
  onConnectionSuccess
}) => {
  const { handleConnect, isLoading } = usePlatformConnections();
  const [error, setError] = useState<string | null>(null);
  const [isConnecting, setIsConnecting] = useState(false);

  // Handle OAuth success via postMessage (same pattern as onboarding)
  useEffect(() => {
    if (!isOpen) return;

    const handler = (event: MessageEvent) => {
      const trusted = [window.location.origin, 'https://littery-sonny-unscrutinisingly.ngrok-free.dev'];
      if (!trusted.includes(event.origin)) return;
      if (!event.data || typeof event.data !== 'object') return;

      if (event.data.type === 'WIX_OAUTH_SUCCESS') {
        console.log('Wix OAuth success in modal');
        setIsConnecting(false);
        setError(null);
        // Close modal and notify parent
        if (onConnectionSuccess) {
          onConnectionSuccess();
        }
        onClose();
      }

      if (event.data.type === 'WIX_OAUTH_ERROR') {
        console.error('Wix OAuth error in modal:', event.data.error);
        setIsConnecting(false);
        setError(event.data.error || 'Wix connection failed. Please try again.');
      }
    };

    window.addEventListener('message', handler);
    return () => window.removeEventListener('message', handler);
  }, [isOpen, onClose, onConnectionSuccess]);

  // Also check for URL param (fallback for same-tab redirect)
  useEffect(() => {
    if (!isOpen) return;

    const params = new URLSearchParams(window.location.search);
    if (params.get('wix_connected') === 'true') {
      console.log('Wix connected via URL param in modal');
      setIsConnecting(false);
      setError(null);
      if (onConnectionSuccess) {
        onConnectionSuccess();
      }
      onClose();
      // Clean URL
      const clean = window.location.pathname + window.location.hash;
      window.history.replaceState({}, document.title, clean || '/');
    }
  }, [isOpen, onClose, onConnectionSuccess]);

  const handleConnectClick = async () => {
    try {
      setIsConnecting(true);
      setError(null);
      await handleConnect('wix');
      // OAuth will redirect, so we don't need to do anything else here
      // The postMessage handler or URL param handler will close the modal
    } catch (err: any) {
      console.error('Error connecting to Wix:', err);
      setIsConnecting(false);
      setError(err?.message || 'Failed to start Wix connection. Please try again.');
    }
  };

  return (
    <Dialog
      open={isOpen}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 2,
          boxShadow: '0 4px 20px rgba(0,0,0,0.15)'
        }
      }}
    >
      <DialogTitle sx={{ pb: 1 }}>
        <Typography variant="h6" sx={{ fontWeight: 600, color: '#1e293b' }}>
          Connect Your Wix Account
        </Typography>
      </DialogTitle>
      
      <DialogContent>
        <Box sx={{ py: 1 }}>
          <Typography variant="body2" color="text.secondary" paragraph>
            Connect your Wix account to publish blog posts directly to your website.
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {isConnecting && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, py: 2 }}>
              <CircularProgress size={20} />
              <Typography variant="body2" color="text.secondary">
                Opening Wix authorization page...
              </Typography>
            </Box>
          )}

          <Box sx={{ mt: 2, p: 2, bgcolor: '#f8fafc', borderRadius: 1 }}>
            <Typography variant="caption" color="text.secondary">
              <strong>What happens next:</strong>
            </Typography>
            <Typography variant="caption" component="div" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
              <ol style={{ margin: '8px 0 0 20px', padding: 0 }}>
                <li>You'll be redirected to Wix to authorize ALwrity</li>
                <li>Grant permissions for blog creation and publishing</li>
                <li>You'll be redirected back to ALwrity</li>
                <li>Your blog post will be published automatically</li>
              </ol>
            </Typography>
          </Box>
        </Box>
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button onClick={onClose} disabled={isConnecting}>
          Cancel
        </Button>
        <Button
          variant="contained"
          onClick={handleConnectClick}
          disabled={isConnecting || isLoading}
          startIcon={isConnecting ? <CircularProgress size={16} /> : undefined}
        >
          {isConnecting ? 'Connecting...' : 'Connect to Wix'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default WixConnectModal;

