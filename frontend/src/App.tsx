import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Box, CircularProgress, Typography } from '@mui/material';
import { CopilotKit } from "@copilotkit/react-core";
import { ClerkProvider, useAuth, useUser } from '@clerk/clerk-react';
import "@copilotkit/react-ui/styles.css";
import Wizard from './components/OnboardingWizard/Wizard';
import MainDashboard from './components/MainDashboard/MainDashboard';
import SEODashboard from './components/SEODashboard/SEODashboard';
import ContentPlanningDashboard from './components/ContentPlanningDashboard/ContentPlanningDashboard';
import FacebookWriter from './components/FacebookWriter/FacebookWriter';
import LinkedInWriter from './components/LinkedInWriter/LinkedInWriter';
import BlogWriter from './components/BlogWriter/BlogWriter';
import ProtectedRoute from './components/shared/ProtectedRoute';
import GSCAuthCallback from './components/SEODashboard/components/GSCAuthCallback';

import { apiClient } from './api/client';

interface OnboardingStatus {
  onboarding_required: boolean;
  onboarding_complete: boolean;
  current_step?: number;
  total_steps?: number;
  completion_percentage?: number;
}

// Conditional CopilotKit wrapper that only shows sidebar on content-planning route
const ConditionalCopilotKit: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const location = useLocation();
  const isContentPlanningRoute = location.pathname === '/content-planning';

  // Do not render CopilotSidebar here. Let specific pages/components control it.
  return <>{children}</>;
};

// Component to handle initial routing based on onboarding status
const InitialRouteHandler: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [onboardingComplete, setOnboardingComplete] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const checkOnboardingStatus = async () => {
      try {
        console.log('Checking onboarding status...');
        const response = await apiClient.get('/api/onboarding/status');
        const status = response.data;
        
        console.log('Onboarding status:', status);
        
        if (status.is_completed) {
          console.log('Onboarding is complete, redirecting to dashboard');
          setOnboardingComplete(true);
        } else {
          console.log('Onboarding not complete, staying on onboarding');
          setOnboardingComplete(false);
        }
      } catch (err) {
        console.error('Error checking onboarding status:', err);
        setError('Failed to check onboarding status');
      } finally {
        setLoading(false);
      }
    };

    checkOnboardingStatus();
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
          Checking onboarding status...
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

  // Redirect based on onboarding status
  if (onboardingComplete) {
    return <Navigate to="/dashboard" replace />;
  } else {
    return <Navigate to="/onboarding" replace />;
  }
};

const App: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const checkBackendHealth = async () => {
      try {
        await apiClient.get('/health');
        setLoading(false);
      } catch (err) {
        setError('Backend service is not available. Please check if the server is running.');
        setLoading(false);
      }
    };

    checkBackendHealth();
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
          Connection Error
        </Typography>
        <Typography variant="body1" color="textSecondary" textAlign="center">
          {error}
        </Typography>
        <Typography variant="body2" color="textSecondary" textAlign="center">
          Please ensure the backend server is running and try refreshing the page.
        </Typography>
      </Box>
    );
  }

  // Get environment variables with fallbacks
  const clerkPublishableKey = process.env.REACT_APP_CLERK_PUBLISHABLE_KEY || '';
  const copilotApiKey = process.env.REACT_APP_COPILOTKIT_API_KEY || '';

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

  return (
    <ClerkProvider publishableKey={clerkPublishableKey}>
      <CopilotKit 
        publicApiKey={copilotApiKey}
        showDevConsole={false}
        onError={(e) => console.error("CopilotKit Error:", e)}
        
      >
        <Router>
          <ConditionalCopilotKit>
            <Routes>
              <Route path="/" element={<InitialRouteHandler />} />
              <Route path="/onboarding" element={<Wizard />} />
              <Route path="/dashboard" element={<ProtectedRoute><MainDashboard /></ProtectedRoute>} />
              <Route path="/seo" element={<ProtectedRoute><SEODashboard /></ProtectedRoute>} />
              <Route path="/seo-dashboard" element={<ProtectedRoute><SEODashboard /></ProtectedRoute>} />
              <Route path="/content-planning" element={<ProtectedRoute><ContentPlanningDashboard /></ProtectedRoute>} />
              <Route path="/facebook-writer" element={<ProtectedRoute><FacebookWriter /></ProtectedRoute>} />
              <Route path="/linkedin-writer" element={<ProtectedRoute><LinkedInWriter /></ProtectedRoute>} />
              <Route path="/blog-writer" element={<ProtectedRoute><BlogWriter /></ProtectedRoute>} />
              <Route path="/gsc/callback" element={<GSCAuthCallback />} />
            </Routes>
          </ConditionalCopilotKit>
        </Router>
      </CopilotKit>
    </ClerkProvider>
  );
};

export default App; 