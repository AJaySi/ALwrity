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
import StoryWriter from './components/StoryWriter/StoryWriter';
import YouTubeCreator from './components/YouTubeCreator/YouTubeCreator';
import { CreateStudio, EditStudio, UpscaleStudio, ControlStudio, SocialOptimizer, AssetLibrary, ImageStudioDashboard } from './components/ImageStudio';
import { ProductMarketingDashboard } from './components/ProductMarketing';
import PodcastDashboard from './components/PodcastMaker/PodcastDashboard';
import PricingPage from './components/Pricing/PricingPage';
import WixTestPage from './components/WixTestPage/WixTestPage';
import WixCallbackPage from './components/WixCallbackPage/WixCallbackPage';
import WordPressCallbackPage from './components/WordPressCallbackPage/WordPressCallbackPage';
import BingCallbackPage from './components/BingCallbackPage/BingCallbackPage';
import BingAnalyticsStorage from './components/BingAnalyticsStorage/BingAnalyticsStorage';
import ResearchTest from './pages/ResearchTest';
import SchedulerDashboard from './pages/SchedulerDashboard';
import BillingPage from './pages/BillingPage';
import ProtectedRoute from './components/shared/ProtectedRoute';
import GSCAuthCallback from './components/SEODashboard/components/GSCAuthCallback';
import Landing from './components/Landing/Landing';
import ErrorBoundary from './components/shared/ErrorBoundary';
import ErrorBoundaryTest from './components/shared/ErrorBoundaryTest';
import CopilotKitDegradedBanner from './components/shared/CopilotKitDegradedBanner';
import { OnboardingProvider } from './contexts/OnboardingContext';
import { SubscriptionProvider, useSubscription } from './contexts/SubscriptionContext';
import { CopilotKitHealthProvider } from './contexts/CopilotKitHealthContext';
import { useOAuthTokenAlerts } from './hooks/useOAuthTokenAlerts';

import { setAuthTokenGetter, setClerkSignOut } from './api/client';
import { setMediaAuthTokenGetter } from './utils/fetchMediaBlobUrl';
import { setBillingAuthTokenGetter } from './services/billingService';
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
  
  // Poll for OAuth token alerts and show toast notifications
  // Only enabled when user is authenticated (has subscription)
  useOAuthTokenAlerts({
    enabled: subscription?.active === true,
    interval: 60000, // Poll every 1 minute
  });

  // Check subscription on mount (non-blocking - don't wait for it to route)
  useEffect(() => {
    // Delay subscription check slightly to allow auth token getter to be installed first
    const timeoutId = setTimeout(() => {
      checkSubscription().catch((err) => {
        console.error('Error checking subscription (non-blocking):', err);
        
        // Check if it's a connection error - handle it locally
        if (err instanceof Error && (err.name === 'NetworkError' || err.name === 'ConnectionError')) {
          setConnectionError({
            hasError: true,
            error: err,
          });
        }
        // Don't block routing on subscription check errors - allow graceful degradation
      });
    }, 100); // Small delay to ensure TokenInstaller has run
    
    return () => clearTimeout(timeoutId);
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

  // Loading state - only wait for onboarding init, not subscription check
  // Subscription check is non-blocking and happens in background
  const waitingForOnboardingInit = loading || !data;
  if (loading || waitingForOnboardingInit) {
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

  // Decision tree for SIGNED-IN users:
  // Priority: Subscription → Onboarding → Dashboard (as per user flow: Landing → Subscription → Onboarding → Dashboard)
  
  // 1. If subscription is still loading, show loading state
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

  // 2. No subscription data yet - handle gracefully
  // If onboarding is complete, allow access to dashboard (user already went through flow)
  // If onboarding not complete, check if subscription check is still loading or failed
  if (!subscription) {
    if (isOnboardingComplete) {
      console.log('InitialRouteHandler: Onboarding complete but no subscription data → Dashboard (allow access)');
      return <Navigate to="/dashboard" replace />;
    }
    
    // Onboarding not complete and no subscription data
    // If subscription check is still loading, show loading state
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
    
    // Subscription check completed but returned null/undefined
    // This likely means no subscription - redirect to pricing
    console.log('InitialRouteHandler: No subscription data after check → Pricing page');
    return <Navigate to="/pricing" replace />;
  }

  // 3. Check subscription status first
  const isNewUser = !subscription || subscription.plan === 'none';
  
  // No active subscription → Show modal (SubscriptionContext handles this)
  // Don't redirect immediately - let the modal show first
  // User can click "Renew Subscription" button in modal to go to pricing
  // Or click "Maybe Later" to dismiss (but they still can't use features)
  if (isNewUser || !subscription.active) {
    console.log('InitialRouteHandler: No active subscription - modal will be shown by SubscriptionContext');
    // Note: SubscriptionContext will show the modal automatically when subscription is inactive
    // We still redirect to pricing for new users, but allow existing users with expired subscriptions
    // to see the modal first. The modal has a "Renew Subscription" button that navigates to pricing.
    // For new users (no subscription at all), redirect to pricing immediately
    if (isNewUser) {
      console.log('InitialRouteHandler: New user (no subscription) → Pricing page');
      return <Navigate to="/pricing" replace />;
    }
    // For existing users with inactive subscription, show modal but don't redirect immediately
    // The modal will be shown by SubscriptionContext, and user can click "Renew Subscription"
    // Allow access to dashboard (modal will be shown and block functionality)
    console.log('InitialRouteHandler: Inactive subscription - allowing access to show modal');
    // Continue to onboarding/dashboard flow - modal will be shown by SubscriptionContext
  }

  // 4. Has active subscription, check onboarding status
  if (!isOnboardingComplete) {
    console.log('InitialRouteHandler: Subscription active but onboarding incomplete → Onboarding');
    return <Navigate to="/onboarding" replace />;
  }

  // 5. Has subscription AND completed onboarding → Dashboard
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
  const { getToken, userId, isSignedIn, signOut } = useAuth();
  
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
    const tokenGetter = async () => {
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
    };
    
    // Set token getter for main API client
    setAuthTokenGetter(tokenGetter);
    
    // Set token getter for billing API client (same function)
    setBillingAuthTokenGetter(tokenGetter);
    
    // Set token getter for media blob URL fetcher (for authenticated image/video requests)
    setMediaAuthTokenGetter(tokenGetter);
  }, [getToken]);
  
  // Install Clerk signOut function for handling expired tokens
  useEffect(() => {
    if (signOut) {
      setClerkSignOut(async () => {
        await signOut();
      });
    }
  }, [signOut]);
  
  return null;
};

const App: React.FC = () => {
  // React Hooks MUST be at the top before any conditionals
  const [loading, setLoading] = useState(true);
  
  // Get CopilotKit key from localStorage or .env
  const [copilotApiKey, setCopilotApiKey] = useState(() => {
    const savedKey = localStorage.getItem('copilotkit_api_key');
    const envKey = process.env.REACT_APP_COPILOTKIT_API_KEY || '';
    const key = (savedKey || envKey).trim();
    
    // Validate key format if present
    if (key && !key.startsWith('ck_pub_')) {
      console.warn('CopilotKit API key format invalid - must start with ck_pub_');
    }
    
    return key;
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
                <Route path="/story-writer" element={<ProtectedRoute><StoryWriter /></ProtectedRoute>} />
                <Route path="/youtube-creator" element={<ProtectedRoute><YouTubeCreator /></ProtectedRoute>} />
                <Route path="/podcast-maker" element={<ProtectedRoute><PodcastDashboard /></ProtectedRoute>} />
                <Route path="/image-studio" element={<ProtectedRoute><ImageStudioDashboard /></ProtectedRoute>} />
                <Route path="/image-generator" element={<ProtectedRoute><CreateStudio /></ProtectedRoute>} />
                <Route path="/image-editor" element={<ProtectedRoute><EditStudio /></ProtectedRoute>} />
                <Route path="/image-upscale" element={<ProtectedRoute><UpscaleStudio /></ProtectedRoute>} />
                <Route path="/image-control" element={<ProtectedRoute><ControlStudio /></ProtectedRoute>} />
                <Route path="/image-studio/social-optimizer" element={<ProtectedRoute><SocialOptimizer /></ProtectedRoute>} />
                <Route path="/asset-library" element={<ProtectedRoute><AssetLibrary /></ProtectedRoute>} />
                <Route path="/campaign-creator" element={<ProtectedRoute><ProductMarketingDashboard /></ProtectedRoute>} />
                <Route path="/product-marketing" element={<Navigate to="/campaign-creator" replace />} />
                <Route path="/scheduler-dashboard" element={<ProtectedRoute><SchedulerDashboard /></ProtectedRoute>} />
                <Route path="/billing" element={<ProtectedRoute><BillingPage /></ProtectedRoute>} />
                <Route path="/pricing" element={<PricingPage />} />
                <Route path="/research-test" element={<ResearchTest />} />
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
      // Enhanced error handler that updates health context
      const handleCopilotKitError = (e: any) => {
        console.error("CopilotKit Error:", e);
        
        // Try to get health context if available
        // We'll use a custom event to notify health context since we can't access it directly here
        const errorMessage = e?.error?.message || e?.message || 'CopilotKit error occurred';
        const errorType = errorMessage.toLowerCase();
        
        // Differentiate between fatal and transient errors
        const isFatalError = 
          errorType.includes('cors') ||
          errorType.includes('ssl') ||
          errorType.includes('certificate') ||
          errorType.includes('403') ||
          errorType.includes('forbidden') ||
          errorType.includes('ERR_CERT_COMMON_NAME_INVALID');
        
        // Dispatch event for health context to listen to
        window.dispatchEvent(new CustomEvent('copilotkit-error', {
          detail: {
            error: e,
            errorMessage,
            isFatal: isFatalError,
          }
        }));
      };

      return (
        <ErrorBoundary 
          context="CopilotKit" 
          showDetails={process.env.NODE_ENV === 'development'}
          fallback={
            <Box sx={{ p: 3, textAlign: 'center' }}>
              <Typography variant="h6" color="warning" gutterBottom>
                Chat Unavailable
              </Typography>
              <Typography variant="body2" color="textSecondary">
                CopilotKit encountered an error. The app continues to work with manual controls.
              </Typography>
            </Box>
          }
        >
          <CopilotKit 
            publicApiKey={copilotApiKey}
            showDevConsole={false}
            onError={handleCopilotKitError}
          >
            {appContent}
          </CopilotKit>
        </ErrorBoundary>
      );
    }

    // Return app without CopilotKit if no key available
    return appContent;
  };

  // Determine initial health status based on whether CopilotKit key is available
  const hasCopilotKitKey = copilotApiKey && copilotApiKey.trim();
  
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
            <CopilotKitHealthProvider initialHealthStatus={!!hasCopilotKitKey}>
              <CopilotKitDegradedBanner />
              {renderApp()}
            </CopilotKitHealthProvider>
          </OnboardingProvider>
        </SubscriptionProvider>
      </ClerkProvider>
    </ErrorBoundary>
  );
};

export default App; 