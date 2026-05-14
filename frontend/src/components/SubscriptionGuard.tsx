import React, { ReactNode } from 'react';
import {
  Box,
  Typography,
  Button,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Card,
  CardContent,
  CardActions,
  Chip,
  LinearProgress
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useSubscriptionGuard, SubscriptionGuardOptions } from '../hooks/useSubscriptionGuard';
import { saveNavigationState } from '../utils/navigationState';
import LockIcon from '@mui/icons-material/Lock';
import UpgradeIcon from '@mui/icons-material/Upgrade';

interface SubscriptionGuardProps extends SubscriptionGuardOptions {
  children: ReactNode;
  feature?: string;
  fallbackMessage?: string;
  showUpgradeButton?: boolean;
  showUsageProgress?: boolean;
}

export const SubscriptionGuard: React.FC<SubscriptionGuardProps> = ({
  children,
  feature,
  fallbackMessage,
  showUpgradeButton = true,
  showUsageProgress = false,
  ...guardOptions
}) => {
  const navigate = useNavigate();
  const {
    subscription,
    loading,
    isGuarded,
    checkFeatureAccess,
    getRemainingUsage,
    checkSubscription
  } = useSubscriptionGuard(guardOptions);

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <LinearProgress />
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Checking subscription...
        </Typography>
      </Box>
    );
  }

  if (isGuarded) {
    if (fallbackMessage) {
      return (
        <Alert severity="warning" sx={{ mb: 2 }}>
          {fallbackMessage}
        </Alert>
      );
    }

    return (
      <Card sx={{ maxWidth: 400, mx: 'auto', mt: 2 }}>
        <CardContent>
          <Box sx={{ textAlign: 'center', mb: 2 }}>
            <LockIcon sx={{ fontSize: 48, color: 'warning.main', mb: 1 }} />
            <Typography variant="h6" gutterBottom>
              Feature Locked
            </Typography>
            <Typography variant="body2" color="text.secondary">
              This feature requires an active subscription.
            </Typography>
          </Box>

          {subscription && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" gutterBottom>
                Current Plan: <Chip label={subscription.plan} size="small" />
              </Typography>
              {subscription.reason && (
                <Typography variant="body2" color="error">
                  {subscription.reason}
                </Typography>
              )}
            </Box>
          )}
        </CardContent>

        {showUpgradeButton && (
          <CardActions sx={{ justifyContent: 'center', pb: 2 }}>
            <Button
              variant="contained"
              startIcon={<UpgradeIcon />}
              onClick={() => {
                saveNavigationState(window.location.pathname);
                navigate('/pricing');
              }}
            >
              Upgrade Plan
            </Button>
          </CardActions>
        )}
      </Card>
    );
  }

  if (feature && !checkFeatureAccess(feature)) {
    const remaining = getRemainingUsage(feature);

    return (
      <Alert severity="warning" sx={{ mb: 2 }}>
        <Typography variant="body2">
          {fallbackMessage || `You've reached your limit for ${feature}. Upgrade to continue using this feature.`}
        </Typography>
        {showUpgradeButton && (
          <Button
            size="small"
            variant="outlined"
            sx={{ mt: 1 }}
            onClick={() => {
              saveNavigationState(window.location.pathname);
              navigate('/pricing');
            }}
          >
            Upgrade
          </Button>
        )}
      </Alert>
    );
  }

  return <>{children}</>;
};

// Convenience component for protecting entire sections
export const ProtectedSection: React.FC<{
  children: ReactNode;
  feature?: string;
  title?: string;
}> = ({ children, feature, title }) => {
  return (
    <SubscriptionGuard feature={feature}>
      <Box>
        {title && (
          <Typography variant="h6" gutterBottom>
            {title}
          </Typography>
        )}
        {children}
      </Box>
    </SubscriptionGuard>
  );
};

// Hook for checking if user can perform an action
export const useCanPerformAction = (action: string) => {
  const { subscription, isFeatureAvailable } = useSubscriptionGuard();

  return {
    canPerform: subscription?.active && isFeatureAvailable(action),
    subscription,
  };
};
