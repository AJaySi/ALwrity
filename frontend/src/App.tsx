import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Box, CircularProgress, Typography } from '@mui/material';
import { CopilotKit } from "@copilotkit/react-core";
import "@copilotkit/react-ui/styles.css";
import Wizard from './components/OnboardingWizard/Wizard';
import MainDashboard from './components/MainDashboard/MainDashboard';
import SEODashboard from './components/SEODashboard/SEODashboard';
import ContentPlanningDashboard from './components/ContentPlanningDashboard/ContentPlanningDashboard';
import FacebookWriter from './components/FacebookWriter/FacebookWriter';
import LinkedInWriter from './components/LinkedInWriter/LinkedInWriter';
import BlogWriter from './components/BlogWriter/BlogWriter';
import StoryWriter from './components/StoryWriter/StoryWriter';
import PricingPage from './components/Pricing/PricingPage';
import WixTestPage from './components/WixTestPage/WixTestPage';
import WixCallbackPage from './components/WixCallbackPage/WixCallbackPage';
import WordPressCallbackPage from './components/WordPressCallbackPage/WordPressCallbackPage';
import BingCallbackPage from './components/BingCallbackPage/BingCallbackPage';
import BingAnalyticsStorage from './components/BingAnalyticsStorage/BingAnalyticsStorage';
import ResearchTest from './pages/ResearchTest';
import SchedulerDashboard from './pages/SchedulerDashboard';
import BillingPage from './pages/BillingPage';
import GSCAuthCallback from './components/SEODashboard/components/GSCAuthCallback';
import Landing from './components/Landing/Landing';
import ErrorBoundary from './components/shared/ErrorBoundary';
import ErrorBoundaryTest from './components/shared/ErrorBoundaryTest';
import CopilotKitDegradedBanner from './components/shared/CopilotKitDegradedBanner';
import { OnboardingProvider } from './contexts/OnboardingContext';
import { SubscriptionProvider, useSubscription } from './contexts/SubscriptionContext';
import { CopilotKitHealthProvider } from './contexts/CopilotKitHealthContext';
import { useOAuthTokenAlerts } from './hooks/useOAuthTokenAlerts';

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

// Component to handle initial routing based on onboarding status
// Authentication disabled for personal use - simplified flow
const InitialRouteHandler: React.FC = () => {
  const { loading, error, isOnboardingComplete, initializeOnboarding, data } = useOnboarding();

  // Initialize onboarding on mount
  useEffect(() => {
    initializeOnboarding();
  }, [initializeOnboarding]);

  // Loading state
  if (loading || !data) {
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

  // Check onboarding status - redirect to onboarding if not complete
  if (!isOnboardingComplete) {
    console.log('InitialRouteHandler: Onboarding incomplete → Onboarding');
    return <Navigate to="/onboarding" replace />;
  }

  // Onboarding complete → Dashboard
  console.log('InitialRouteHandler: Onboarding complete → Dashboard');
  return <Navigate to="/dashboard" replace />;
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
    // Set static user ID for personal use
    localStorage.setItem('user_id', 'personal_user');
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

  // Render app with or without CopilotKit based on whether we have a key
  const renderApp = () => {
    const appContent = (
      <Router>
        <ConditionalCopilotKit>
          <Routes>
                <Route path="/" element={<InitialRouteHandler />} />
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
                <Route path="/dashboard" element={<MainDashboard />} />
                <Route path="/seo" element={<SEODashboard />} />
                <Route path="/seo-dashboard" element={<SEODashboard />} />
                <Route path="/content-planning" element={<ContentPlanningDashboard />} />
                <Route path="/facebook-writer" element={<FacebookWriter />} />
                <Route path="/linkedin-writer" element={<LinkedInWriter />} />
                <Route path="/blog-writer" element={<BlogWriter />} />
                <Route path="/story-writer" element={<StoryWriter />} />
                <Route path="/scheduler-dashboard" element={<SchedulerDashboard />} />
                <Route path="/billing" element={<BillingPage />} />
                <Route path="/pricing" element={<PricingPage />} />
                <Route path="/research-test" element={<ResearchTest />} />
                <Route path="/wix-test" element={<WixTestPage />} />
                <Route path="/wix-test-direct" element={<WixTestPage />} />
                <Route path="/wix/callback" element={<WixCallbackPage />} />
                <Route path="/wp/callback" element={<WordPressCallbackPage />} />
                <Route path="/gsc/callback" element={<GSCAuthCallback />} />
                <Route path="/bing/callback" element={<BingCallbackPage />} />
                <Route path="/bing-analytics-storage" element={<BingAnalyticsStorage />} />
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
      <SubscriptionProvider>
        <OnboardingProvider>
          <CopilotKitHealthProvider initialHealthStatus={!!hasCopilotKitKey}>
            <CopilotKitDegradedBanner />
            {renderApp()}
          </CopilotKitHealthProvider>
        </OnboardingProvider>
      </SubscriptionProvider>
    </ErrorBoundary>
  );
};

export default App; 