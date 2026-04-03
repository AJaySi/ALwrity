import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Box, CircularProgress, Typography } from '@mui/material';
import { ClerkProvider, useAuth } from '@clerk/clerk-react';
import Wizard from './components/OnboardingWizard/Wizard';
import MainDashboard from './components/MainDashboard/MainDashboard';
import SEODashboard from './components/SEODashboard/SEODashboard';
import ContentPlanningDashboard from './components/ContentPlanningDashboard/ContentPlanningDashboard';
import FacebookWriter from './components/FacebookWriter/FacebookWriter';
import LinkedInWriter from './components/LinkedInWriter/LinkedInWriter';
import BlogWriter from './components/BlogWriter/BlogWriter';
import StoryWriter from './components/StoryWriter/StoryWriter';
import { StoryProjectList } from './components/StoryWriter/StoryProjectList';
import YouTubeCreator from './components/YouTubeCreator/YouTubeCreator';
import { CreateStudio, EditStudio, UpscaleStudio, ControlStudio, SocialOptimizer, AssetLibrary, ImageStudioDashboard, FaceSwapStudio, CompressionStudio, ImageProcessingStudio } from './components/ImageStudio';
import {
  VideoStudioDashboard,
  CreateVideo,
  AvatarVideo,
  EnhanceVideo,
  ExtendVideo,
  EditVideo,
  TransformVideo,
  SocialVideo,
  FaceSwap,
  VideoTranslate,
  VideoBackgroundRemover,
  AddAudioToVideo,
  LibraryVideo,
} from './components/VideoStudio';
import {
  ProductMarketingDashboard,
  ProductPhotoshootStudio,
  ProductAnimationStudio,
  ProductVideoStudio,
  ProductAvatarStudio,
} from './components/ProductMarketing';
import PodcastDashboard from './components/PodcastMaker/PodcastDashboard';
import PricingPage from './components/Pricing/PricingPage';
import WixTestPage from './components/WixTestPage/WixTestPage';
import WixCallbackPage from './components/WixCallbackPage/WixCallbackPage';
import WordPressCallbackPage from './components/WordPressCallbackPage/WordPressCallbackPage';
import BingCallbackPage from './components/BingCallbackPage/BingCallbackPage';
import BingAnalyticsStorage from './components/BingAnalyticsStorage/BingAnalyticsStorage';
import ResearchDashboard from './pages/ResearchDashboard';
import IntentResearchTest from './pages/IntentResearchTest';
import SchedulerDashboard from './pages/SchedulerDashboard';
import BillingPage from './pages/BillingPage';
import ApprovalsPage from './pages/ApprovalsPage';
import TeamActivityPage from './pages/TeamActivityPage';
import StripeDisputesDashboard from './pages/StripeDisputesDashboard';
import ProtectedRoute from './components/shared/ProtectedRoute';
import GSCAuthCallback from './components/SEODashboard/components/GSCAuthCallback';
import Landing from './components/Landing/Landing';
import ErrorBoundary from './components/shared/ErrorBoundary';
import ErrorBoundaryTest from './components/shared/ErrorBoundaryTest';
import { OnboardingProvider } from './contexts/OnboardingContext';
import { SubscriptionProvider } from './contexts/SubscriptionContext';
import InitialRouteHandler from './components/App/InitialRouteHandler';
import TokenInstaller from './components/App/TokenInstaller';
import { ConditionalCopilotKit, AuthenticatedCopilotWrapper } from './components/App/CopilotWrappers';

// interface OnboardingStatus {
//   onboarding_required: boolean;
//   onboarding_complete: boolean;
//   current_step?: number;
//   total_steps?: number;
//   completion_percentage?: number;
// }

// Root route that chooses Landing (signed out) or InitialRouteHandler (signed in)
const RootRoute: React.FC = () => {
  const { isSignedIn } = useAuth();
  if (isSignedIn) {
    return <InitialRouteHandler />;
  }
  return <Landing />;
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
  const clerkJSUrl = process.env.REACT_APP_CLERK_JS_URL;

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
    return (
      <Router>
        <AuthenticatedCopilotWrapper apiKey={copilotApiKey}>
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
                  <Route path="/story-projects" element={<ProtectedRoute><StoryProjectList /></ProtectedRoute>} />
                  <Route path="/youtube-creator" element={<ProtectedRoute><YouTubeCreator /></ProtectedRoute>} />
                  <Route path="/podcast-maker" element={<ProtectedRoute><PodcastDashboard /></ProtectedRoute>} />
                  <Route path="/image-studio" element={<ProtectedRoute><ImageStudioDashboard /></ProtectedRoute>} />
                  <Route path="/video-studio" element={<ProtectedRoute><VideoStudioDashboard /></ProtectedRoute>} />
                  <Route path="/video-studio/create" element={<ProtectedRoute><CreateVideo /></ProtectedRoute>} />
                  <Route path="/video-studio/avatar" element={<ProtectedRoute><AvatarVideo /></ProtectedRoute>} />
                  <Route path="/video-studio/enhance" element={<ProtectedRoute><EnhanceVideo /></ProtectedRoute>} />
                  <Route path="/video-studio/extend" element={<ProtectedRoute><ExtendVideo /></ProtectedRoute>} />
                  <Route path="/video-studio/edit" element={<ProtectedRoute><EditVideo /></ProtectedRoute>} />
                  <Route path="/video-studio/transform" element={<ProtectedRoute><TransformVideo /></ProtectedRoute>} />
                  <Route path="/video-studio/social" element={<ProtectedRoute><SocialVideo /></ProtectedRoute>} />
                  <Route path="/video-studio/face-swap" element={<ProtectedRoute><FaceSwap /></ProtectedRoute>} />
                  <Route path="/video-studio/video-translate" element={<ProtectedRoute><VideoTranslate /></ProtectedRoute>} />
                  <Route path="/video-studio/video-background-remover" element={<ProtectedRoute><VideoBackgroundRemover /></ProtectedRoute>} />
                  <Route path="/video-studio/add-audio-to-video" element={<ProtectedRoute><AddAudioToVideo /></ProtectedRoute>} />
                  <Route path="/video-studio/library" element={<ProtectedRoute><LibraryVideo /></ProtectedRoute>} />
                  <Route path="/image-generator" element={<ProtectedRoute><CreateStudio /></ProtectedRoute>} />
                  <Route path="/image-editor" element={<ProtectedRoute><EditStudio /></ProtectedRoute>} />
                  <Route path="/image-upscale" element={<ProtectedRoute><UpscaleStudio /></ProtectedRoute>} />
                  <Route path="/image-control" element={<ProtectedRoute><ControlStudio /></ProtectedRoute>} />
                  <Route path="/image-studio/face-swap" element={<ProtectedRoute><FaceSwapStudio /></ProtectedRoute>} />
                  <Route path="/image-studio/compress" element={<ProtectedRoute><CompressionStudio /></ProtectedRoute>} />
                  <Route path="/image-studio/processing" element={<ProtectedRoute><ImageProcessingStudio /></ProtectedRoute>} />
                  <Route path="/image-studio/social-optimizer" element={<ProtectedRoute><SocialOptimizer /></ProtectedRoute>} />
                  <Route path="/asset-library" element={<ProtectedRoute><AssetLibrary /></ProtectedRoute>} />
                  <Route path="/campaign-creator" element={<ProtectedRoute><ProductMarketingDashboard /></ProtectedRoute>} />
                  <Route path="/campaign-creator/photoshoot" element={<ProtectedRoute><ProductPhotoshootStudio /></ProtectedRoute>} />
                  <Route path="/campaign-creator/animation" element={<ProtectedRoute><ProductAnimationStudio /></ProtectedRoute>} />
                  <Route path="/campaign-creator/video" element={<ProtectedRoute><ProductVideoStudio /></ProtectedRoute>} />
                  <Route path="/campaign-creator/avatar" element={<ProtectedRoute><ProductAvatarStudio /></ProtectedRoute>} />
                  <Route path="/product-marketing" element={<Navigate to="/campaign-creator" replace />} />
                  <Route path="/scheduler-dashboard" element={<ProtectedRoute><SchedulerDashboard /></ProtectedRoute>} />
                  <Route path="/billing" element={<ProtectedRoute><BillingPage /></ProtectedRoute>} />
                  <Route path="/approvals" element={<ProtectedRoute><ApprovalsPage /></ProtectedRoute>} />
                  <Route path="/team-activity" element={<ProtectedRoute><TeamActivityPage /></ProtectedRoute>} />
                  <Route path="/stripe-disputes" element={<ProtectedRoute><StripeDisputesDashboard /></ProtectedRoute>} />
                  <Route path="/pricing" element={<PricingPage />} />
                  <Route path="/research-test" element={<ResearchDashboard />} />
                  <Route path="/research-dashboard" element={<ResearchDashboard />} />
                  <Route path="/alwrity-researcher" element={<ResearchDashboard />} />
                  <Route path="/intent-research" element={<IntentResearchTest />} />
                  <Route path="/wix-test" element={<WixTestPage />} />
                  <Route path="/wix-test-direct" element={<WixTestPage />} />
                  <Route path="/wix/callback" element={<WixCallbackPage />} />
                  <Route path="/wp/callback" element={<WordPressCallbackPage />} />
                  <Route path="/gsc/callback" element={<GSCAuthCallback />} />
                  <Route path="/bing/callback" element={<BingCallbackPage />} />
                  <Route path="/bing-analytics-storage" element={<ProtectedRoute><BingAnalyticsStorage /></ProtectedRoute>} />
            </Routes>
          </ConditionalCopilotKit>
        </AuthenticatedCopilotWrapper>
      </Router>
    );
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
      <ClerkProvider publishableKey={clerkPublishableKey} clerkJSUrl={clerkJSUrl}>
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
