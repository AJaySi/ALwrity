import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Box, CircularProgress, Typography } from '@mui/material';
import Wizard from './components/OnboardingWizard/Wizard';
import MainDashboard from './components/MainDashboard/MainDashboard';
import SEODashboard from './components/SEODashboard/SEODashboard';
import ContentPlanningDashboard from './components/ContentPlanningDashboard/ContentPlanningDashboard';
import FacebookWriter from './components/FacebookWriter/FacebookWriter';
import LinkedInWriter from './components/LinkedInWriter/LinkedInWriter';
import BlogWriter from './components/BlogWriter/BlogWriter';
import StoryWriter from './components/StoryWriter/StoryWriter';
import PricingPage from './components/Pricing/PricingPage';
import BingCallbackPage from './components/BingCallbackPage/BingCallbackPage';
import BingAnalyticsStorage from './components/BingAnalyticsStorage/BingAnalyticsStorage';
import ResearchTest from './pages/ResearchTest';
import SchedulerDashboard from './pages/SchedulerDashboard';
import BillingPage from './pages/BillingPage';
import GSCAuthCallback from './components/SEODashboard/components/GSCAuthCallback';
import Landing from './components/Landing/Landing';
import ErrorBoundary from './components/shared/ErrorBoundary';
import ErrorBoundaryTest from './components/shared/ErrorBoundaryTest';
import { OnboardingProvider } from './contexts/OnboardingContext';
import { SubscriptionProvider } from './contexts/SubscriptionContext';

import { useOnboarding } from './contexts/OnboardingContext';
import { useState, useEffect } from 'react';


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
  const [loading, setLoading] = useState(true);

  // Initialize app
  useEffect(() => {
    // Set static user ID for personal use
    localStorage.setItem('user_id', 'personal_user');
    setLoading(false);
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

  return (
    <ErrorBoundary
      context="Application Root"
      showDetails={process.env.NODE_ENV === 'development'}
      onError={(error, errorInfo) => {
        console.error('Global error caught:', { error, errorInfo });
      }}
    >
      <SubscriptionProvider>
        <OnboardingProvider>
          <Router>
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
              <Route path="/gsc/callback" element={<GSCAuthCallback />} />
              <Route path="/bing/callback" element={<BingCallbackPage />} />
              <Route path="/bing-analytics-storage" element={<BingAnalyticsStorage />} />
            </Routes>
          </Router>
        </OnboardingProvider>
      </SubscriptionProvider>
    </ErrorBoundary>
  );
};

export default App; 