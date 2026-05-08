import React, { useState, useEffect, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Box, CircularProgress, Typography } from '@mui/material';
import { ClerkProvider, useAuth } from '@clerk/clerk-react';
import ProtectedRoute from './components/shared/ProtectedRoute';
import ErrorBoundary from './components/shared/ErrorBoundary';
import { OnboardingProvider } from './contexts/OnboardingContext';
import { SubscriptionProvider } from './contexts/SubscriptionContext';
import InitialRouteHandler from './components/App/InitialRouteHandler';
import TokenInstaller from './components/App/TokenInstaller';
import { ConditionalCopilotKit, AuthenticatedCopilotWrapper } from './components/App/CopilotWrappers';
import Landing from './components/Landing/Landing';
import LazyLoadingFallback from './components/shared/LazyLoadingFallback';

// ─── Lazy loaded route components ───────────────────────────────────────────
// Default exports
const Wizard = React.lazy(() => import('./components/OnboardingWizard/Wizard'));
const MainDashboard = React.lazy(() => import('./components/MainDashboard/MainDashboard'));
const SEODashboard = React.lazy(() => import('./components/SEODashboard/SEODashboard'));
const ContentPlanningDashboard = React.lazy(() => import('./components/ContentPlanningDashboard/ContentPlanningDashboard'));
const FacebookWriter = React.lazy(() => import('./components/FacebookWriter/FacebookWriter'));
const LinkedInWriter = React.lazy(() => import('./components/LinkedInWriter/LinkedInWriter'));
const BlogWriter = React.lazy(() => import('./components/BlogWriter/BlogWriter'));
const StoryWriter = React.lazy(() => import('./components/StoryWriter/StoryWriter'));
const YouTubeCreator = React.lazy(() => import('./components/YouTubeCreator/YouTubeCreator'));
const PodcastDashboard = React.lazy(() => import('./components/PodcastMaker/PodcastDashboard'));
const PricingPage = React.lazy(() => import('./components/Pricing/PricingPage'));
const WixTestPage = React.lazy(() => import('./components/WixTestPage/WixTestPage'));
const WixCallbackPage = React.lazy(() => import('./components/WixCallbackPage/WixCallbackPage'));
const WordPressCallbackPage = React.lazy(() => import('./components/WordPressCallbackPage/WordPressCallbackPage'));
const BingCallbackPage = React.lazy(() => import('./components/BingCallbackPage/BingCallbackPage'));
const BingAnalyticsStorage = React.lazy(() => import('./components/BingAnalyticsStorage/BingAnalyticsStorage'));
const ResearchDashboard = React.lazy(() => import('./pages/ResearchDashboard'));
const IntentResearchTest = React.lazy(() => import('./pages/IntentResearchTest'));
const SchedulerDashboard = React.lazy(() => import('./pages/SchedulerDashboard'));
const BillingPage = React.lazy(() => import('./pages/BillingPage'));
const ApprovalsPage = React.lazy(() => import('./pages/ApprovalsPage'));
const TeamActivityPage = React.lazy(() => import('./pages/TeamActivityPage'));
const StripeDisputesDashboard = React.lazy(() => import('./pages/StripeDisputesDashboard'));
const GSCAuthCallback = React.lazy(() => import('./components/SEODashboard/components/GSCAuthCallback'));
const ErrorBoundaryTest = React.lazy(() => import('./components/shared/ErrorBoundaryTest'));

// Named exports — need .then() wrapper to resolve default
const StoryProjectList = React.lazy(() => import('./components/StoryWriter/StoryProjectList').then(m => ({ default: m.StoryProjectList })));

// ImageStudio barrel (10 named exports)
const CreateStudio = React.lazy(() => import('./components/ImageStudio').then(m => ({ default: m.CreateStudio })));
const EditStudio = React.lazy(() => import('./components/ImageStudio').then(m => ({ default: m.EditStudio })));
const UpscaleStudio = React.lazy(() => import('./components/ImageStudio').then(m => ({ default: m.UpscaleStudio })));
const ControlStudio = React.lazy(() => import('./components/ImageStudio').then(m => ({ default: m.ControlStudio })));
const SocialOptimizer = React.lazy(() => import('./components/ImageStudio').then(m => ({ default: m.SocialOptimizer })));
const AssetLibrary = React.lazy(() => import('./components/ImageStudio').then(m => ({ default: m.AssetLibrary })));
const ImageStudioDashboard = React.lazy(() => import('./components/ImageStudio').then(m => ({ default: m.ImageStudioDashboard })));
const FaceSwapStudio = React.lazy(() => import('./components/ImageStudio').then(m => ({ default: m.FaceSwapStudio })));
const CompressionStudio = React.lazy(() => import('./components/ImageStudio').then(m => ({ default: m.CompressionStudio })));
const ImageProcessingStudio = React.lazy(() => import('./components/ImageStudio').then(m => ({ default: m.ImageProcessingStudio })));

// VideoStudio barrel (13 named exports)
const VideoStudioDashboard = React.lazy(() => import('./components/VideoStudio').then(m => ({ default: m.VideoStudioDashboard })));
const CreateVideo = React.lazy(() => import('./components/VideoStudio').then(m => ({ default: m.CreateVideo })));
const AvatarVideo = React.lazy(() => import('./components/VideoStudio').then(m => ({ default: m.AvatarVideo })));
const EnhanceVideo = React.lazy(() => import('./components/VideoStudio').then(m => ({ default: m.EnhanceVideo })));
const ExtendVideo = React.lazy(() => import('./components/VideoStudio').then(m => ({ default: m.ExtendVideo })));
const EditVideo = React.lazy(() => import('./components/VideoStudio').then(m => ({ default: m.EditVideo })));
const TransformVideo = React.lazy(() => import('./components/VideoStudio').then(m => ({ default: m.TransformVideo })));
const SocialVideo = React.lazy(() => import('./components/VideoStudio').then(m => ({ default: m.SocialVideo })));
const FaceSwap = React.lazy(() => import('./components/VideoStudio').then(m => ({ default: m.FaceSwap })));
const VideoTranslate = React.lazy(() => import('./components/VideoStudio').then(m => ({ default: m.VideoTranslate })));
const VideoBackgroundRemover = React.lazy(() => import('./components/VideoStudio').then(m => ({ default: m.VideoBackgroundRemover })));
const AddAudioToVideo = React.lazy(() => import('./components/VideoStudio').then(m => ({ default: m.AddAudioToVideo })));
const LibraryVideo = React.lazy(() => import('./components/VideoStudio').then(m => ({ default: m.LibraryVideo })));

// ProductMarketing barrel (5 named exports)
const ProductMarketingDashboard = React.lazy(() => import('./components/ProductMarketing').then(m => ({ default: m.ProductMarketingDashboard })));
const ProductPhotoshootStudio = React.lazy(() => import('./components/ProductMarketing').then(m => ({ default: m.ProductPhotoshootStudio })));
const ProductAnimationStudio = React.lazy(() => import('./components/ProductMarketing').then(m => ({ default: m.ProductAnimationStudio })));
const ProductVideoStudio = React.lazy(() => import('./components/ProductMarketing').then(m => ({ default: m.ProductVideoStudio })));
const ProductAvatarStudio = React.lazy(() => import('./components/ProductMarketing').then(m => ({ default: m.ProductAvatarStudio })));

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
            <Suspense fallback={<LazyLoadingFallback />}>
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
            </Suspense>
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
