/**
 * WordPress OAuth Platform Card Component
 * Simplified WordPress connection using OAuth2 flow with compact premium design.
 */

import React, { useState } from 'react';
import {
  Box,
  Card,
  Typography,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  IconButton,
  Tooltip,
  Button
} from '@mui/material';
import {
  Web as WordPressIcon,
  Delete as DeleteIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Link as LinkIcon,
  OpenInNew as OpenInNewIcon
} from '@mui/icons-material';
import { useWordPressOAuth } from '../../../hooks/useWordPressOAuth';

interface WordPressOAuthPlatformCardProps {
  onConnect?: (platform: string) => void;
  onDisconnect?: (platform: string) => void;
  connectedPlatforms: string[];
  setConnectedPlatforms: (platforms: string[]) => void;
}

const WordPressOAuthPlatformCard: React.FC<WordPressOAuthPlatformCardProps> = ({
  onConnect,
  onDisconnect,
  connectedPlatforms,
  setConnectedPlatforms
}) => {
  const {
    connected,
    sites,
    totalSites,
    isLoading,
    startOAuthFlow,
    disconnectSite
  } = useWordPressOAuth();

  const [showSitesDialog, setShowSitesDialog] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);

  const isConnected = connected && totalSites > 0;
  const site = sites[0];

  const handleConnect = async () => {
    try {
      setIsConnecting(true);
      await startOAuthFlow();
    } catch (error: any) {
      console.error('Error connecting to WordPress:', error);
      if (error.response?.status === 500 && error.response?.data?.detail?.includes('not configured')) {
        alert('WordPress OAuth is not properly configured.');
      } else {
        alert('Failed to connect to WordPress.');
      }
    } finally {
      setIsConnecting(false);
    }
  };

  const handleDisconnectSite = async (tokenId: number) => {
    try {
      const success = await disconnectSite(tokenId);
      if (success) {
        const remainingSites = sites.filter(site => site.id !== tokenId);
        if (remainingSites.length === 0) {
          setConnectedPlatforms(connectedPlatforms.filter(p => p !== 'wordpress'));
          onDisconnect?.('wordpress');
        }
        setShowSitesDialog(false);
      }
    } catch (error) {
      console.error('Error disconnecting WordPress site:', error);
    }
  };

  return (
    <>
      <Card 
        variant="outlined"
        sx={{
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          p: 2,
          borderColor: isConnected ? '#4ade80' : '#e2e8f0',
          backgroundColor: isConnected ? '#f0fdf4' : '#ffffff',
          transition: 'all 0.2s ease',
          '&:hover': {
            borderColor: isConnected ? '#22c55e' : '#cbd5e1',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.05)'
          }
        }}
      >
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
          <Box display="flex" alignItems="center" gap={1.5}>
            <Box 
              sx={{ 
                color: '#21759b', // WordPress blue
                bgcolor: '#ffffff',
                p: 0.5,
                borderRadius: 1,
                border: '1px solid #e2e8f0',
                display: 'flex'
              }}
            >
              <WordPressIcon fontSize="small" />
            </Box>
            <Box>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#1e293b', lineHeight: 1.2 }}>
                WordPress
              </Typography>
              <Typography variant="caption" sx={{ color: '#64748b', display: 'block' }}>
                WP.com / Jetpack
              </Typography>
            </Box>
          </Box>
          {isLoading || isConnecting ? (
            <CircularProgress size={16} sx={{ color: '#64748b' }} />
          ) : isConnected ? (
            <Tooltip title="Connected">
              <CheckCircleIcon sx={{ color: '#22c55e', fontSize: 20 }} onClick={() => setShowSitesDialog(true)} style={{ cursor: 'pointer' }} />
            </Tooltip>
          ) : (
            <Chip label="Connect" size="small" onClick={handleConnect} clickable sx={{ height: 24, fontSize: '0.75rem', fontWeight: 600, bgcolor: '#21759b', color: 'white', '&:hover': { bgcolor: '#1a5c7a' } }} />
          )}
        </Box>

        {isConnected && site ? (
          <Box mt={1} p={1} bgcolor="rgba(255,255,255,0.6)" borderRadius={1} border="1px solid rgba(0,0,0,0.05)">
            <Box display="flex" alignItems="center" gap={1} mb={0.5}>
              <LinkIcon sx={{ fontSize: 14, color: '#64748b' }} />
              <Typography variant="caption" sx={{ fontWeight: 600, color: '#334155', maxWidth: '100%', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {(site.blog_url || '').replace(/^https?:\/\//, '') || 'WordPress Site'}
              </Typography>
              <IconButton size="small" href={site.blog_url} target="_blank" sx={{ p: 0.5, ml: 'auto' }}>
                <OpenInNewIcon sx={{ fontSize: 12, color: '#94a3b8' }} />
              </IconButton>
            </Box>
            <Typography variant="caption" sx={{ color: '#64748b', display: 'block', fontSize: '0.7rem' }}>
              {totalSites > 1 ? `+${totalSites - 1} other sites` : 'OAuth Connected'}
            </Typography>
          </Box>
        ) : (
          <Typography variant="caption" sx={{ color: '#64748b', mt: 1, lineHeight: 1.4 }}>
            Connect your WordPress sites securely via official OAuth integration.
          </Typography>
        )}
      </Card>

      {/* Sites Dialog */}
      <Dialog open={showSitesDialog} onClose={() => setShowSitesDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Connected WordPress Sites</DialogTitle>
        <DialogContent>
          {sites.map((site) => (
            <Box key={site.id} display="flex" alignItems="center" justifyContent="space-between" p={2} borderBottom="1px solid #e2e8f0">
              <Box>
                <Typography variant="subtitle2">{site.blog_url}</Typography>
                <Typography variant="caption" color="textSecondary">ID: {site.blog_id}</Typography>
              </Box>
              <IconButton onClick={() => handleDisconnectSite(site.id)} color="error" size="small">
                <DeleteIcon />
              </IconButton>
            </Box>
          ))}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowSitesDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default WordPressOAuthPlatformCard;
