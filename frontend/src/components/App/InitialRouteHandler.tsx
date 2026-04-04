import React, { useState, useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { Box, CircularProgress, Typography } from '@mui/material';
import { useOnboarding } from '../../contexts/OnboardingContext';
import { useSubscription } from '../../contexts/SubscriptionContext';
import { useOAuthTokenAlerts } from '../../hooks/useOAuthTokenAlerts';
import { shouldSkipOnboarding } from '../../utils/demoMode';
import ConnectionErrorPage from '../shared/ConnectionErrorPage';

const InitialRouteHandler: React.FC = () => {
  const { loading, error, isOnboardingComplete, initializeOnboarding, data } = useOnboarding();
  const { subscription, loading: subscriptionLoading, checkSubscription } = useSubscription();
  const location = useLocation();
  const [connectionError, setConnectionError] = useState<{
    hasError: boolean;
    error: Error | null;
  }>({
    hasError: false,
    error: null,
  });
  
  useOAuthTokenAlerts({
    enabled: subscription?.active === true,
    interval: 60000,
  });

  useEffect(() => {
    const timeoutId = setTimeout(async () => {
      const maxRetries = 3;
      for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
          await checkSubscription();
          break;
        } catch (err) {
          console.error(`App: Subscription check attempt ${attempt + 1} failed:`, err);
          
          const isConnectionError = err instanceof Error && (err.name === 'NetworkError' || err.name === 'ConnectionError');
          
          if (isConnectionError && attempt < maxRetries - 1) {
             const delay = 1000 * Math.pow(2, attempt);
             await new Promise(resolve => setTimeout(resolve, delay));
             continue;
           }
           
           if (attempt === maxRetries - 1 || !isConnectionError) {
              if (isConnectionError) {
                setConnectionError({
                  hasError: true,
                  error: err as Error,
                });
              }
           }
        }
      }
    }, 100);
    
    return () => clearTimeout(timeoutId);
  }, []);

  const urlParams = new URLSearchParams(location.search);
  const isCheckoutSuccess = urlParams.get('subscription') === 'success';
  
  useEffect(() => {
    if (subscription && !subscriptionLoading) {
      const isNewUser = !subscription || subscription.plan === 'none';
      
      console.log('InitialRouteHandler: Subscription data received:', {
        plan: subscription.plan,
        active: subscription.active,
        isNewUser,
        subscriptionLoading
      });
      
      if (subscription.active && !isNewUser) {
        console.log('InitialRouteHandler: Subscription confirmed, initializing onboarding...');
        
        if (!isCheckoutSuccess) {
          initializeOnboarding();
        }
      }
    }
  }, [subscription, subscriptionLoading, initializeOnboarding, isCheckoutSuccess]);

  if (isCheckoutSuccess && subscription?.active && shouldSkipOnboarding()) {
    console.log('InitialRouteHandler: Early redirect - Stripe checkout success in demo mode → Podcast Maker');
    return <Navigate to="/podcast-maker" replace />;
  }

  if (connectionError.hasError) {
    const handleRetry = () => {
      setConnectionError({
        hasError: false,
        error: null,
      });
      checkSubscription().catch((err) => {
        if (err instanceof Error && (err.name === 'NetworkError' || err.name === 'ConnectionError')) {
          setConnectionError({
            hasError: true,
            error: err,
          });
        }
      });
    };

    const handleGoHome = () => {
      window.location.href = '/';
    };

    return (
      <ConnectionErrorPage
        onRetry={handleRetry}
        onGoHome={handleGoHome}
        message={connectionError.error?.message || "Backend service is not available. Please check if the server is running."}
        title="Connection Error"
      />
    );
  }

  const isDemoMode = shouldSkipOnboarding();
  console.log('InitialRouteHandler DEBUG:', {
    isDemoMode,
    isOnboardingComplete,
    subscription: subscription ? { plan: subscription.plan, active: subscription.active } : null,
    loading,
    data: !!data
  });
  const isActiveSubscriber = Boolean(subscription && subscription.active && subscription.plan !== 'none');
  const waitingForOnboardingInit = !isDemoMode && isActiveSubscriber && (loading || !data);
  if (waitingForOnboardingInit) {
    return (
      <Box
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        minHeight="100vh"
        gap={2}
      >
        <CircularProgress size={60} />
        <Typography variant="h6" color="textSecondary">
          Preparing your workspace...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        minHeight="100vh"
        gap={2}
        p={3}
      >
        <Typography variant="h5" color="error" gutterBottom>
          Error
        </Typography>
        <Typography variant="body1" color="textSecondary" textAlign="center">
          {error}
        </Typography>
      </Box>
    );
  }

  if (subscriptionLoading) {
    return (
      <Box
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        minHeight="100vh"
        gap={2}
      >
        <CircularProgress size={60} />
        <Typography variant="h6" color="textSecondary">
          Checking subscription...
        </Typography>
      </Box>
    );
  }

  if (!subscription) {
    if (isOnboardingComplete) {
      console.log('InitialRouteHandler: Onboarding complete but no subscription data → Dashboard (allow access)');
      return <Navigate to="/dashboard" replace />;
    }
    
    if (subscriptionLoading) {
      return (
        <Box
          display="flex"
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
          minHeight="100vh"
          gap={2}
        >
          <CircularProgress size={60} />
          <Typography variant="h6" color="textSecondary">
            Checking subscription...
          </Typography>
        </Box>
      );
    }
    
    if (!subscription) {
      if (isOnboardingComplete) {
        console.log('InitialRouteHandler: Onboarding complete but no subscription data → Dashboard (allow access)');
        return <Navigate to="/dashboard" replace />;
      }
      
      if (subscriptionLoading) {
        return (
          <Box
            display="flex"
            flexDirection="column"
            alignItems="center"
            justifyContent="center"
            minHeight="100vh"
            gap={2}
          >
            <CircularProgress size={60} />
            <Typography variant="h6" color="textSecondary">
              Checking subscription...
            </Typography>
          </Box>
        );
      }
      
      if (shouldSkipOnboarding()) {
        console.log('InitialRouteHandler: Demo mode - no subscription but allowing access to podcast-maker');
        return <Navigate to="/podcast-maker" replace />;
      }
      
      console.log('InitialRouteHandler: No subscription data after check → Pricing page');
      return <Navigate to="/pricing" replace />;
    }
  }

  const isNewUser = !subscription || subscription.plan === 'none';
  
  if (isNewUser || !subscription.active) {
    console.log('InitialRouteHandler: No active subscription - modal will be shown by SubscriptionContext');
    if (isNewUser) {
      console.log('InitialRouteHandler: New user (no subscription) → Pricing page');
      return <Navigate to="/pricing" replace />;
    }
    console.log('InitialRouteHandler: Inactive subscription - allowing access to show modal');
  }

  if (!isOnboardingComplete) {
    if (shouldSkipOnboarding()) {
      console.log('InitialRouteHandler: Demo mode - skipping onboarding → Podcast Maker');
      return <Navigate to="/podcast-maker" replace />;
    }
    console.log('InitialRouteHandler: Subscription active but onboarding incomplete → Onboarding');
    return <Navigate to="/onboarding" replace />;
  }

  console.log('InitialRouteHandler: All set (subscription + onboarding) → Dashboard');
  return <Navigate to="/dashboard" replace />;
};

export default InitialRouteHandler;
