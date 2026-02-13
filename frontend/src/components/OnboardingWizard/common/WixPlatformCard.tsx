/**
 * Wix Platform Card Component
 * Handles Wix connection using a compact, premium design
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  Typography,
  Button,
  Chip,
  CircularProgress,
  Tooltip,
  IconButton
} from '@mui/material';
import {
  Web as WixIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Link as LinkIcon,
  OpenInNew as OpenInNewIcon
} from '@mui/icons-material';
import { useWixConnection } from '../../../hooks/useWixConnection';
import { usePlatformConnections } from './usePlatformConnections';

interface WixPlatformCardProps {
  onConnect?: (platform: string) => void;
  onDisconnect?: (platform: string) => void;
  connectedPlatforms: string[];
  setConnectedPlatforms: (platforms: string[]) => void;
}

const WixPlatformCard: React.FC<WixPlatformCardProps> = ({
  onConnect,
  onDisconnect,
  connectedPlatforms,
  setConnectedPlatforms
}) => {
  const { connected, sites, totalSites, isLoading, checkStatus } = useWixConnection();
  const { handleConnect } = usePlatformConnections();
  const [isConnecting, setIsConnecting] = useState(false);

  // Update connected platforms when Wix connection changes
  useEffect(() => {
    if (connected && totalSites > 0) {
      if (!connectedPlatforms.includes('wix')) {
        setConnectedPlatforms([...connectedPlatforms, 'wix']);
      }
    } else {
      if (connectedPlatforms.includes('wix')) {
        setConnectedPlatforms(connectedPlatforms.filter(p => p !== 'wix'));
      }
    }
  }, [connected, totalSites, connectedPlatforms, setConnectedPlatforms]);

  const handleWixConnect = async () => {
    try {
      setIsConnecting(true);
      await handleConnect('wix');
    } catch (error) {
      console.error('Error connecting to Wix:', error);
    } finally {
      setIsConnecting(false);
    }
  };

  const isConnected = connected && totalSites > 0;
  const site = sites[0];

  return (
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
              color: '#000000', // Wix brand black
              bgcolor: '#ffffff',
              p: 0.5,
              borderRadius: 1,
              border: '1px solid #e2e8f0',
              display: 'flex'
            }}
          >
            <WixIcon fontSize="small" />
          </Box>
          <Box>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#1e293b', lineHeight: 1.2 }}>
              Wix
            </Typography>
            <Typography variant="caption" sx={{ color: '#64748b', display: 'block' }}>
              Website & Blog
            </Typography>
          </Box>
        </Box>
        {isLoading || isConnecting ? (
          <CircularProgress size={16} sx={{ color: '#64748b' }} />
        ) : isConnected ? (
          <Tooltip title="Connected">
            <CheckCircleIcon sx={{ color: '#22c55e', fontSize: 20 }} />
          </Tooltip>
        ) : (
          <Chip label="Connect" size="small" onClick={handleWixConnect} clickable sx={{ height: 24, fontSize: '0.75rem', fontWeight: 600, bgcolor: '#000000', color: 'white', '&:hover': { bgcolor: '#333333' } }} />
        )}
      </Box>

      {isConnected && site ? (
        <Box mt={1} p={1} bgcolor="rgba(255,255,255,0.6)" borderRadius={1} border="1px solid rgba(0,0,0,0.05)">
          <Box display="flex" alignItems="center" gap={1} mb={0.5}>
            <LinkIcon sx={{ fontSize: 14, color: '#64748b' }} />
            <Typography variant="caption" sx={{ fontWeight: 600, color: '#334155', maxWidth: '100%', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {site.blog_url.replace(/^https?:\/\//, '')}
            </Typography>
            <IconButton size="small" href={site.blog_url} target="_blank" sx={{ p: 0.5, ml: 'auto' }}>
              <OpenInNewIcon sx={{ fontSize: 12, color: '#94a3b8' }} />
            </IconButton>
          </Box>
        </Box>
      ) : (
        <Typography variant="caption" sx={{ color: '#64748b', mt: 1, lineHeight: 1.4 }}>
          Connect to auto-publish content and track analytics directly from your dashboard.
        </Typography>
      )}
    </Card>
  );
};

export default WixPlatformCard;
