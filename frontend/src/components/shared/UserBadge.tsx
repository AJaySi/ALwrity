import React, { useState, useEffect } from 'react';
import { Avatar, Box, Menu, MenuItem, Typography, Tooltip, Chip, Divider } from '@mui/material';
import { useUser, useClerk } from '@clerk/clerk-react';
import { useSubscription } from '../../contexts/SubscriptionContext';
import SystemStatusIndicator from '../ContentPlanningDashboard/components/SystemStatusIndicator';
import UsageDashboard from './UsageDashboard';
import { apiClient } from '../../api/client';

interface UserBadgeProps {
  colorMode?: 'light' | 'dark';
}

const UserBadge: React.FC<UserBadgeProps> = ({ colorMode = 'light' }) => {
  const { user, isSignedIn } = useUser();
  const { signOut } = useClerk();
  const { subscription } = useSubscription();
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const [systemStatus, setSystemStatus] = useState<'healthy' | 'warning' | 'critical' | 'unknown'>('unknown');
  const open = Boolean(anchorEl);

  const initials = React.useMemo(() => {
    const first = user?.firstName?.[0] || '';
    const last = user?.lastName?.[0] || '';
    return (first + last || user?.username?.[0] || user?.primaryEmailAddress?.emailAddress?.[0] || '?').toUpperCase();
  }, [user]);

  // Fetch system status for status bulb
  useEffect(() => {
    const fetchSystemStatus = async () => {
      try {
        const response = await apiClient.get('/api/content-planning/monitoring/lightweight-stats');
        const result = response.data;
        if (result.status === 'success' && result.data) {
          setSystemStatus(result.data.status || 'unknown');
        }
      } catch (err) {
        // Silently fail for system status to avoid console noise
        setSystemStatus('unknown');
      }
    };

    fetchSystemStatus();
    // Refresh every 120 seconds (2 minutes) to reduce load and avoid timeouts
    const interval = setInterval(fetchSystemStatus, 120000);
    return () => clearInterval(interval);
  }, []);

  if (!isSignedIn) return null;

  // Get status bulb color
  const getStatusBulbColor = () => {
    switch (systemStatus) {
      case 'healthy':
        return '#4caf50'; // Green
      case 'warning':
        return '#ff9800'; // Orange
      case 'critical':
        return '#f44336'; // Red
      default:
        return '#757575'; // Gray for unknown
    }
  };

  // Get plan display info
  const getPlanColor = () => {
    switch (subscription?.plan) {
      case 'free': return '#4caf50';
      case 'basic': return '#2196f3';
      case 'pro': return '#9c27b0';
      case 'enterprise': return '#ff9800';
      default: return '#757575';
    }
  };

  const getPlanLabel = () => {
    if (!subscription?.active) return 'No Plan';
    return subscription.plan.charAt(0).toUpperCase() + subscription.plan.slice(1);
  };

  const handleOpen = (e: React.MouseEvent<HTMLElement>) => setAnchorEl(e.currentTarget);
  const handleClose = () => setAnchorEl(null);

  const handleSignOut = async () => {
    try {
      await signOut();
    } finally {
      window.location.assign('/');
    }
  };

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      {/* Subscription Plan Chip */}
      <Chip
        label={getPlanLabel()}
        size="small"
        sx={{
          bgcolor: `${getPlanColor()}20`,
          border: `1px solid ${getPlanColor()}`,
          color: getPlanColor(),
          fontWeight: 700,
          fontSize: '0.75rem',
          height: 24,
        }}
      />
      
      <Tooltip title={`${user?.fullName || user?.username || user?.primaryEmailAddress?.emailAddress || 'User'} - System: ${systemStatus.toUpperCase()}`}> 
        <Box sx={{ position: 'relative', display: 'inline-flex' }}>
          <Avatar
            onClick={handleOpen}
            sx={{
              width: 36,
              height: 36,
              cursor: 'pointer',
              bgcolor: colorMode === 'dark' ? 'rgba(255,255,255,0.2)' : 'primary.main',
              color: colorMode === 'dark' ? 'white' : 'white',
              fontWeight: 700,
            }}
            src={user?.imageUrl || undefined}
          >
            {initials}
          </Avatar>
          {/* Status Bulb */}
          <Box
            sx={{
              position: 'absolute',
              bottom: 0,
              right: 0,
              width: 12,
              height: 12,
              borderRadius: '50%',
              bgcolor: getStatusBulbColor(),
              border: `2px solid ${colorMode === 'dark' ? '#1a1a1a' : 'white'}`,
              boxShadow: `0 0 8px ${getStatusBulbColor()}80`,
              animation: systemStatus === 'healthy' ? 'pulse 2s ease-in-out infinite' : 'none',
              '@keyframes pulse': {
                '0%, 100%': {
                  opacity: 1,
                  transform: 'scale(1)',
                },
                '50%': {
                  opacity: 0.8,
                  transform: 'scale(1.1)',
                },
              },
            }}
          />
        </Box>
      </Tooltip>
      
      <Menu 
        anchorEl={anchorEl} 
        open={open} 
        onClose={handleClose} 
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }} 
        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
        PaperProps={{
          sx: {
            minWidth: 320,
            maxWidth: 400,
            maxHeight: '80vh',
            overflow: 'auto'
          }
        }}
      >
        <Box sx={{ px: 2, py: 1, borderBottom: '1px solid rgba(0,0,0,0.1)' }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 700 }}>
            {user?.fullName || user?.username || 'User'}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {user?.primaryEmailAddress?.emailAddress}
          </Typography>
        </Box>
        
        {/* Subscription Info in Menu */}
        <Box sx={{ px: 2, py: 1.5, bgcolor: 'rgba(0,0,0,0.02)' }}>
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
            Current Plan
          </Typography>
          <Chip
            label={getPlanLabel()}
            size="small"
            sx={{
              bgcolor: `${getPlanColor()}20`,
              border: `1px solid ${getPlanColor()}`,
              color: getPlanColor(),
              fontWeight: 700,
              fontSize: '0.75rem',
            }}
          />
        </Box>
        
        <Divider sx={{ my: 1 }} />
        
        {/* System Status Indicator */}
        <Box 
          sx={{ 
            px: 2, 
            py: 1.5, 
            bgcolor: 'rgba(0,0,0,0.02)',
            maxWidth: '100%',
            overflow: 'hidden'
          }}
          onClick={(e) => e.stopPropagation()}
        >
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1, fontWeight: 600 }}>
            System Health
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'center', '& > *': { transform: 'scale(0.85)' } }}>
            <SystemStatusIndicator />
          </Box>
        </Box>
        
        <Divider sx={{ my: 1 }} />
        
        {/* Usage Dashboard */}
        <Box 
          sx={{ 
            px: 2, 
            py: 1.5, 
            bgcolor: 'rgba(0,0,0,0.02)',
            maxWidth: '100%',
            overflow: 'auto'
          }}
          onClick={(e) => e.stopPropagation()}
        >
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1, fontWeight: 600 }}>
            Usage Statistics
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'center', flexWrap: 'wrap', gap: 0.5 }}>
            <UsageDashboard compact={true} />
          </Box>
        </Box>
        
        <Divider sx={{ my: 1 }} />
        
        <MenuItem onClick={() => { handleClose(); window.location.href = '/pricing'; }}>
          Manage Subscription
        </MenuItem>
        <MenuItem onClick={handleSignOut}>Sign out</MenuItem>
      </Menu>
    </Box>
  );
};

export default UserBadge;


