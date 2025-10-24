import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Box, CircularProgress, Typography } from '@mui/material';
import { CopilotKit } from "@copilotkit/react-core";
import { ClerkProvider, useAuth } from '@clerk/clerk-react';
import "@copilotkit/react-ui/styles.css";
import Wizard from './components/OnboardingWizard/Wizard';
import MainDashboard from './components/MainDashboard/MainDashboard';
import SEODashboard from './components/SEODashboard/SEODashboard';
import ContentPlanningDashboard from './components/ContentPlanningDashboard/ContentPlanningDashboard';
import FacebookWriter from './components/FacebookWriter/FacebookWriter';
import LinkedInWriter from './components/LinkedInWriter/LinkedInWriter';
import BlogWriter from './components/BlogWriter/BlogWriter';
import PricingPage from './components/Pricing/PricingPage';
import WixTestPage from './components/WixTestPage/WixTestPage';
import WixCallbackPage from './components/WixCallbackPage/WixCallbackPage';
import WordPressCallbackPage from './components/WordPressCallbackPage/WordPressCallbackPage';
import BingCallbackPage from './components/BingCallbackPage/BingCallbackPage';
import BingAnalyticsStorage from './components/BingAnalyticsStorage/BingAnalyticsStorage';
import ProtectedRoute from './components/shared/ProtectedRoute';
import GSCAuthCallback from './components/SEODashboard/components/GSCAuthCallback';
import Landing from './components/Landing/Landing';
import ErrorBoundary from './components/shared/ErrorBoundary';
import ErrorBoundaryTest from './components/shared/ErrorBoundaryTest';
import { OnboardingProvider } from './contexts/OnboardingContext';
import { SubscriptionProvider, useSubscription } from './contexts/SubscriptionContext';

import { setAuthTokenGetter } from './api/client';
import { useOnboarding } from './contexts/OnboardingContext';
import { useState, useEffect } from 'react';
import ConnectionErrorPage from './components/shared/ConnectionErrorPage';

// interface OnboardingStatus {
//   onboarding_required: boolean;
//   onboarding_complete: boolean;
//   current_step?: number;
//   total_steps?: number;
//   completion_percentage?: number;
// }

// Conditional CopilotKit wrapper that only shows sidebar on content-planning route
const ConditionalCopilotKit: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Do not render CopilotSidebar here. Let specific pages/components control it.
  return <>{children}</>;
};

// Component to handle initial routing based on subscription and onboarding status
// Flow: Subscription → Onboarding → Dashboard
const InitialRouteHandler: React.FC = () => {
  const { loading, error, isOnboardingComplete, initializeOnboarding, data } = useOnboarding();
  const { subscription, loading: subscriptionLoading, error: subscriptionError, checkSubscription } = useSubscription();
  // Note: subscriptionError is available for future error handling
  const [connectionError, setConnectionError] = useState<{
    hasError: boolean;
    error: Error | null;
  }>({
    hasError: false,
    error: null,
  });

  // Check subscription on mount
  useEffect(() => {
    checkSubscription().catch((err) => {
      console.error('Error checking subscription:', err);
      
      // Check if it's a connection error - handle it locally
      if (err instanceof Error && (err.name === 'NetworkError' || err.name === 'ConnectionError')) {
        setConnectionError({
          hasError: true,
          error: err,
        });
      }
    });
  }, []); // Remove checkSubscription dependency to prevent loop

  // Initialize onboarding only after subscription is confirmed
  useEffect(() => {
    if (subscription && !subscriptionLoading) {
      // Check if user is new (no subscription record at all)
      const isNewUser = !subscription || subscription.plan === 'none';
      
      console.log('InitialRouteHandler: Subscription data received:', {
        plan: subscription.plan,
        active: subscription.active,
        isNewUser,
        subscriptionLoading
      });
      
      if (subscription.active && !isNewUser) {
        console.log('InitialRouteHandler: Subscription confirmed, initializing onboarding...');
        initializeOnboarding();
      }
    }
  }, [subscription, subscriptionLoading, initializeOnboarding]);

  // Handle connection error - show connection error page
  if (connectionError.hasError) {
    const handleRetry = () => {
      setConnectionError({
        hasError: false,
        error: null,
      });
      // Re-trigger the subscription check using context
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

  // Loading state - ensure we wait for onboarding init after subscription is confirmed
  const waitingForOnboardingInit = !!subscription && subscription.active && !subscriptionLoading && (loading || !data);
  if (subscriptionLoading || loading || waitingForOnboardingInit) {
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
          {subscriptionLoading ? 'Checking subscription...' : 'Preparing your workspace...'}
        </Typography>
      </Box>
    );
  }

  // Error state
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

  if (!subscription) {
    return null; // Should not happen, but just in case
  }

  // Decision tree for SIGNED-IN users:
  // Priority: Subscription → Onboarding → Dashboard
  
  // Check if user is new (no subscription record at all)
  const isNewUser = !subscription || subscription.plan === 'none';
  
  // 1. No active subscription? → Must subscribe first (even if onboarding is complete)
  if (isNewUser || !subscription.active) {
    console.log('InitialRouteHandler: No active subscription → Pricing page');
    return <Navigate to="/pricing" replace />;
  }

  // 2. Has active subscription, check onboarding status
  if (!isOnboardingComplete) {
    console.log('InitialRouteHandler: Subscription active but onboarding incomplete → Onboarding');
    return <Navigate to="/onboarding" replace />;
  }

  // 3. Has subscription AND completed onboarding → Dashboard
  console.log('InitialRouteHandler: All set (subscription + onboarding) → Dashboard');
  return <Navigate to="/dashboard" replace />;
};

// Root route that chooses Landing (signed out) or InitialRouteHandler (signed in)
const RootRoute: React.FC = () => {
  const { isSignedIn } = useAuth();
  if (isSignedIn) {
    return <InitialRouteHandler />;
  }
  return <Landing />;
};

// Installs Clerk auth token getter into axios clients and stores user_id
// Must render under ClerkProvider
const TokenInstaller: React.FC = () => {
  const { getToken, userId, isSignedIn } = useAuth();
  
  // Store user_id in localStorage when user signs in
  useEffect(() => {
    if (isSignedIn && userId) {
      console.log('TokenInstaller: Storing user_id in localStorage:', userId);
      localStorage.setItem('user_id', userId);
      
      // Trigger event to notify SubscriptionContext that user is authenticated
      window.dispatchEvent(new CustomEvent('user-authenticated', { detail: { userId } }));
    } else if (!isSignedIn) {
      // Clear user_id when signed out
      console.log('TokenInstaller: Clearing user_id from localStorage');
      localStorage.removeItem('user_id');
    }
  }, [isSignedIn, userId]);
  
  // Install token getter for API calls
  useEffect(() => {
    setAuthTokenGetter(async () => {
      try {
        const template = process.env.REACT_APP_CLERK_JWT_TEMPLATE;
        // If a template is provided and it's not a placeholder, request a template-specific JWT
        if (template && template !== 'your_jwt_template_name_here') {
          // @ts-ignore Clerk types allow options object
          return await getToken({ template });
        }
        return await getToken();
      } catch {
        return null;
      }
    });
  }, [getToken]);
  
  return null;
};

const App: React.FC = () => {
  // React Hooks MUST be at the top before any conditionals
  const [loading, setLoading] = useState(true);
  
  // Get CopilotKit key from localStorage or .env
  const [copilotApiKey, setCopilotApiKey] = useState(() => {
    const savedKey = localStorage.getItem('copilotkit_api_key');
    return savedKey || process.env.REACT_APP_COPILOTKIT_API_KEY || '';
  });

  // Initialize app - loading state will be managed by InitialRouteHandler
  useEffect(() => {
    // Remove manual health check - connection errors are handled by ErrorBoundary
    setLoading(false);
  }, []);

  // Listen for CopilotKit key updates
  useEffect(() => {
    const handleKeyUpdate = (event: CustomEvent) => {
      const newKey = event.detail?.apiKey;
      if (newKey) {
        console.log('App: CopilotKit key updated, reloading...');
        setCopilotApiKey(newKey);
        setTimeout(() => window.location.reload(), 500);
      }
    };
    
    window.addEventListener('copilotkit-key-updated', handleKeyUpdate as EventListener);
    return () => window.removeEventListener('copilotkit-key-updated', handleKeyUpdate as EventListener);
  }, []);

  // Token installer must be inside ClerkProvider; see TokenInstaller below

  if (loading) {
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
          Connecting to ALwrity...
        </Typography>
      </Box>
    );
  }


  // Get environment variables with fallbacks
  const clerkPublishableKey = process.env.REACT_APP_CLERK_PUBLISHABLE_KEY || '';

  // Show error if required keys are missing
  if (!clerkPublishableKey) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography color="error" variant="h6">
          Missing Clerk Publishable Key
        </Typography>
        <Typography variant="body2" sx={{ mt: 1 }}>
          Please add REACT_APP_CLERK_PUBLISHABLE_KEY to your .env file
        </Typography>
      </Box>
    );
  }

  // Render app with or without CopilotKit based on whether we have a key
  const renderApp = () => {
    const appContent = (
      <Router>
        <ConditionalCopilotKit>
          <TokenInstaller />
          <Routes>
                <Route path="/" element={<RootRoute />} />
                <Route 
                  path="/onboarding" 
                  element={
                    <ErrorBoundary context="Onboarding Wizard" showDetails>
                      <Wizard />
                    </ErrorBoundary>
                  } 
                />
                {/* Error Boundary Testing - Development Only */}
                {process.env.NODE_ENV === 'development' && (
                  <Route path="/error-test" element={<ErrorBoundaryTest />} />
                )}
                <Route path="/dashboard" element={<ProtectedRoute><MainDashboard /></ProtectedRoute>} />
                <Route path="/seo" element={<ProtectedRoute><SEODashboard /></ProtectedRoute>} />
                <Route path="/seo-dashboard" element={<ProtectedRoute><SEODashboard /></ProtectedRoute>} />
                <Route path="/content-planning" element={<ProtectedRoute><ContentPlanningDashboard /></ProtectedRoute>} />
                <Route path="/facebook-writer" element={<ProtectedRoute><FacebookWriter /></ProtectedRoute>} />
                <Route path="/linkedin-writer" element={<ProtectedRoute><LinkedInWriter /></ProtectedRoute>} />
                <Route path="/blog-writer" element={<ProtectedRoute><BlogWriter /></ProtectedRoute>} />
                <Route path="/pricing" element={<PricingPage />} />
                <Route path="/wix-test" element={<WixTestPage />} />
                <Route path="/wix-test-direct" element={<WixTestPage />} />
                <Route path="/wix/callback" element={<WixCallbackPage />} />
                <Route path="/wp/callback" element={<WordPressCallbackPage />} />
                <Route path="/gsc/callback" element={<GSCAuthCallback />} />
                <Route path="/bing/callback" element={<BingCallbackPage />} />
                <Route path="/bing-analytics-storage" element={<ProtectedRoute><BingAnalyticsStorage /></ProtectedRoute>} />
          </Routes>
        </ConditionalCopilotKit>
      </Router>
    );

    // Only wrap with CopilotKit if we have a valid key
    if (copilotApiKey && copilotApiKey.trim()) {
      return (
        <CopilotKit 
          publicApiKey={copilotApiKey}
          showDevConsole={false}
          onError={(e) => console.error("CopilotKit Error:", e)}
        >
          {appContent}
        </CopilotKit>
      );
    }

    // Return app without CopilotKit if no key available
    return appContent;
  };

  return (
    <ErrorBoundary 
      context="Application Root"
      showDetails={process.env.NODE_ENV === 'development'}
      onError={(error, errorInfo) => {
        // Custom error handler - send to analytics/monitoring
        console.error('Global error caught:', { error, errorInfo });
        // TODO: Send to error tracking service (Sentry, LogRocket, etc.)
      }}
    >
      <ClerkProvider publishableKey={clerkPublishableKey}>
        <SubscriptionProvider>
          <OnboardingProvider>
            {renderApp()}
          </OnboardingProvider>
        </SubscriptionProvider>
      </ClerkProvider>
    </ErrorBoundary>
  );
};

export default App; 