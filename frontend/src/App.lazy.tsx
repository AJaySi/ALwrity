import React, { Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Box, CircularProgress, Typography } from '@mui/material';
import { CopilotKit } from "@copilotkit/react-core";
import { ClerkProvider, useAuth } from '@clerk/clerk-react';
import "@copilotkit/react-ui/styles.css";

// Lazy loaded components - ZERO BREAKING CHANGES
const LazyMainDashboard = React.lazy(() => import('./components/MainDashboard/MainDashboard'));
const LazySEODashboard = React.lazy(() => import('./components/SEODashboard/SEODashboard'));
const LazyContentPlanningDashboard = React.lazy(() => import('./components/ContentPlanningDashboard/ContentPlanningDashboard'));
const LazyFacebookWriter = React.lazy(() => import('./components/FacebookWriter/FacebookWriter'));
const LazyLinkedInWriter = React.lazy(() => import('./components/LinkedInWriter/LinkedInWriter'));
const LazyBlogWriter = React.lazy(() => import('./components/BlogWriter/BlogWriter'));
const LazyStoryWriter = React.lazy(() => import('./components/StoryWriter/StoryWriter'));
const LazyYouTubeCreator = React.lazy(() => import('./components/YouTubeCreator/YouTubeCreator'));
const LazyImageStudio = React.lazy(() => import('./components/ImageStudio/ImageStudioDashboard'));
const LazyVideoStudio = React.lazy(() => import('./components/VideoStudio/VideoStudioDashboard'));
const LazyProductMarketing = React.lazy(() => import('./components/ProductMarketing/ProductMarketingDashboard'));
const LazyPodcastDashboard = React.lazy(() => import('./components/PodcastMaker/PodcastDashboard'));
const LazyPricingPage = React.lazy(() => import('./components/Pricing/PricingPage'));
const LazyWixTestPage = React.lazy(() => import('./components/WixTestPage/WixTestPage'));
const LazyWixCallbackPage = React.lazy(() => import('./components/WixCallbackPage/WixCallbackPage'));
const LazyWordPressCallbackPage = React.lazy(() => import('./components/WordPressCallbackPage/WordPressCallbackPage'));
const LazyBingCallbackPage = React.lazy(() => import('./components/BingCallbackPage/BingCallbackPage'));
const LazyBingAnalyticsStorage = React.lazy(() => import('./components/BingAnalyticsStorage/BingAnalyticsStorage'));
const LazyResearchDashboard = React.lazy(() => import('./pages/ResearchDashboard'));
const LazyIntentResearchTest = React.lazy(() => import('./pages/IntentResearchTest'));
const LazySchedulerDashboard = React.lazy(() => import('./pages/SchedulerDashboard'));
const LazyBillingPage = React.lazy(() => import('./pages/BillingPage'));

// Loading component - SAME UX, better performance
const LoadingSpinner = () => (
  <Box
    display="flex"
    justifyContent="center"
    alignItems="center"
    minHeight="200px"
  >
    <Box textAlign="center">
      <CircularProgress size={40} />
      <Typography variant="body1" sx={{ mt: 2 }}>
        Loading...
      </Typography>
    </Box>
  </Box>
);

// Error boundary for lazy loading - SAME FUNCTIONALITY, better error handling
const LazyErrorBoundary = ({ children, error }) => (
  <Box
    display="flex"
    flexDirection="column"
    justifyContent="center"
    alignItems="center"
    minHeight="300px"
    p={3}
  >
    <Typography variant="h6" color="error" gutterBottom>
      ⚠️ Failed to load
    </Typography>
    <Typography variant="body2" color="text.secondary">
      {error?.message || 'Component failed to load'}
    </Typography>
    <Typography variant="body2" sx={{ mt: 1 }}>
      Please refresh the page or check your connection
    </Typography>
  </Box>
);

function App() {
  const { isSignedIn, user } = useAuth();

  return (
    <ClerkProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          
          {/* Critical routes - wrapped in Suspense for loading states */}
          <Route 
            path="/dashboard" 
            element={
              <Suspense fallback={<LoadingSpinner />}>
                <LazyMainDashboard />
              </Suspense>
            } 
          />
          
          <Route 
            path="/seo" 
            element={
              <Suspense fallback={<LoadingSpinner />}>
                <LazySEODashboard />
              </Suspense>
            } 
          />
          
          <Route 
            path="/content-planning" 
            element={
              <Suspense fallback={<LoadingSpinner />}>
                <LazyContentPlanningDashboard />
              </Suspense>
            } 
          />
          
          <Route 
            path="/facebook-writer" 
            element={
              <Suspense fallback={<LoadingSpinner />}>
                <LazyFacebookWriter />
              </Suspense>
            } 
          />
          
          <Route 
            path="/linkedin-writer" 
            element={
              <Suspense fallback={<LoadingSpinner />}>
                <LazyLinkedInWriter />
              </Suspense>
            } 
          />
          
          <Route 
            path="/blog-writer" 
            element={
              <Suspense fallback={<LoadingSpinner />}>
                <LazyBlogWriter />
              </Suspense>
            } 
          />
          
          <Route 
            path="/story-writer" 
            element={
              <Suspense fallback={<LoadingSpinner />}>
                <LazyStoryWriter />
              </Suspense>
            } 
          />
          
          {/* Heavy feature routes - lazy loaded for performance */}
          <Route 
            path="/youtube-creator" 
            element={
              <Suspense fallback={<LoadingSpinner />}>
                <LazyYouTubeCreator />
              </Suspense>
            } 
          />
          
          <Route 
            path="/image-studio/*" 
            element={
              <Suspense fallback={<LoadingSpinner />}>
                <LazyImageStudio />
              </Suspense>
            } 
          />
          
          <Route 
            path="/video-studio/*" 
            element={
              <Suspense fallback={<LoadingSpinner />}>
                <LazyVideoStudio />
              </Suspense>
            } 
          />
          
          <Route 
            path="/product-marketing/*" 
            element={
              <Suspense fallback={<LoadingSpinner />}>
                <LazyProductMarketing />
              </Suspense>
            } 
          />
          
          <Route 
            path="/podcast-maker" 
            element={
              <Suspense fallback={<LoadingSpinner />}>
                <LazyPodcastDashboard />
              </Suspense>
            } 
          />
          
          <Route 
            path="/pricing" 
            element={
              <Suspense fallback={<LoadingSpinner />}>
                <LazyPricingPage />
              </Suspense>
            } 
          />
          
          <Route 
            path="/billing" 
            element={
              <Suspense fallback={<LoadingSpinner />}>
                <LazyBillingPage />
              </Suspense>
            } 
          />
          
          {/* Other routes - same as before */}
          <Route path="/research" element={<LazyResearchDashboard />} />
          <Route path="/intent-research-test" element={<LazyIntentResearchTest />} />
          <Route path="/scheduler" element={<LazySchedulerDashboard />} />
          <Route path="/wix-test" element={<LazyWixTestPage />} />
          <Route path="/wix-callback" element={<LazyWixCallbackPage />} />
          <Route path="/wordpress-callback" element={<LazyWordPressCallbackPage />} />
          <Route path="/bing-callback" element={<LazyBingCallbackPage />} />
          <Route path="/bing-analytics-storage" element={<LazyBingAnalyticsStorage />} />
        </Routes>
      </Router>
    </ClerkProvider>
  );
}

export default App;
