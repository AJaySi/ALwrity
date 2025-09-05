import React, { useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Typography,
  Alert,
  Skeleton,
  useTheme,
  Chip,
  Button
} from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth, useUser, SignInButton, SignOutButton } from '@clerk/clerk-react';

// Shared components
import { DashboardContainer, GlassCard } from '../shared/styled';
import SEOAnalyzerPanel from './components/SEOAnalyzerPanel';
import { SEOCopilotKitProvider, SEOCopilotSuggestions } from './index';
// Removed SEOCopilotTest
import useSEOCopilotStore from '../../stores/seoCopilotStore';

// GSC Components
import GSCLoginButton from './components/GSCLoginButton';

// Zustand store
import { useSEODashboardStore } from '../../stores/seoDashboardStore';

// API
import { userDataAPI } from '../../api/userData';

// SEO Dashboard component
const SEODashboard: React.FC = () => {
  const theme = useTheme();
  
  // Clerk authentication hooks
  const { isSignedIn, isLoaded } = useAuth();
  const { user } = useUser();
  
  // Zustand store hooks
  const {
    loading,
    error,
    data,
    analysisData,
    analysisLoading,
    analysisError,
    setData,
    setLoading,
    setError,
    runSEOAnalysis,
    checkAndRunInitialAnalysis,
    refreshSEOAnalysis,
    getAnalysisFreshness,
  } = useSEODashboardStore();

  // Sync dashboard analysis to Copilot store so readables have URL/context
  const setCopilotAnalysisData = useSEOCopilotStore(state => state.setAnalysisData);
  useEffect(() => {
    if (analysisData) {
      setCopilotAnalysisData(analysisData as any);
      if (process.env.NODE_ENV === 'development') {
        console.log('[CopilotSync] Pushed analysis to Copilot store', analysisData?.url);
      }
    }
  }, [analysisData, setCopilotAnalysisData]);

  useEffect(() => {
    // Simulate fetching dashboard data
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Get user's website URL from user data
        const userData = await userDataAPI.getUserData();
        const websiteUrl = userData?.website_url || 'https://alwrity.com';
        
        // Mock data for demonstration
        const mockData = {
          health_score: {
            score: 84,
            change: 5,
            trend: 'up',
            label: 'EXCELLENT',
            color: '#4CAF50'
          },
          key_insight: 'Your website has excellent technical SEO foundation with room for improvement',
          priority_alert: 'Mobile page speed could be optimized further',
          metrics: {
            traffic: { value: 12500, change: 15, trend: 'up', description: 'Organic traffic', color: '#4CAF50' },
            rankings: { value: 8.5, change: 2.3, trend: 'up', description: 'Average ranking', color: '#2196F3' },
            mobile: { value: 92, change: -3, trend: 'down', description: 'Mobile speed', color: '#FF9800' },
            keywords: { value: 150, change: 12, trend: 'up', description: 'Keywords tracked', color: '#9C27B0' }
          },
          platforms: {
            google: { status: 'connected', connected: true, last_sync: '2024-01-15T10:30:00Z', data_points: 1250 },
            bing: { status: 'connected', connected: true, last_sync: '2024-01-15T09:45:00Z', data_points: 850 },
            yandex: { status: 'disconnected', connected: false }
          },
          ai_insights: [
            {
              insight: 'Your website has excellent technical SEO foundation',
              priority: 'low',
              category: 'technical',
              action_required: false
            },
            {
              insight: 'Consider adding more internal links to improve page authority',
              priority: 'medium',
              category: 'content',
              action_required: false
            },
            {
              insight: 'Mobile page speed could be optimized further',
              priority: 'high',
              category: 'performance',
              action_required: true,
              tool_path: '/seo-dashboard'
            }
          ],
          last_updated: new Date().toISOString(),
          website_url: websiteUrl || undefined // Convert null to undefined for TypeScript
        };
        
        setData(mockData);
        setLoading(false);
      } catch (err) {
        setError('Failed to load dashboard data');
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    // Run initial SEO analysis if no data exists
    if (!loading && !error && data) {
      // Call via store to avoid changing function identity in deps
      useSEODashboardStore.getState().checkAndRunInitialAnalysis();
    }
  }, [loading, error, data]);

  if (loading) {
    return <Skeleton variant="rectangular" height={200} />;
  }

  if (error || !data) {
    return <Alert severity="error">Failed to load dashboard data</Alert>;
  }

  // Show sign-in prompt if not authenticated
  if (!isLoaded) {
    return <Skeleton variant="rectangular" height={200} />;
  }

  if (!isSignedIn) {
    return (
      <DashboardContainer>
        <Container maxWidth="md">
          <Box sx={{ 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center', 
            justifyContent: 'center', 
            minHeight: '60vh',
            textAlign: 'center',
            gap: 3
          }}>
            <Typography variant="h4" sx={{ color: 'white', fontWeight: 700 }}>
              🔍 SEO Dashboard
            </Typography>
            <Typography variant="h6" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
              Sign in to access your SEO analytics and Google Search Console data
            </Typography>
            <SignInButton mode="modal">
              <Button 
                variant="contained" 
                size="large"
                sx={{ 
                  bgcolor: '#4285f4',
                  '&:hover': { bgcolor: '#3367d6' },
                  px: 4,
                  py: 1.5,
                  fontSize: '1.1rem',
                  fontWeight: 600
                }}
              >
                Sign In to Continue
              </Button>
            </SignInButton>
          </Box>
        </Container>
      </DashboardContainer>
    );
  }

  return (
    <SEOCopilotKitProvider enableDebugMode={false}>
      <DashboardContainer>
        <Container maxWidth="xl">
          <AnimatePresence>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              {/* Header */}
              <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ color: 'white', fontWeight: 700 }}>
                    🔍 SEO Dashboard
                  </Typography>
                  <Typography variant="subtitle1" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                    AI-powered insights and actionable recommendations
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  {/* User Info */}
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Chip
                      label={`Signed in as ${user?.primaryEmailAddress?.emailAddress || 'User'}`}
                      size="small"
                      sx={{
                        bgcolor: 'rgba(76, 175, 80, 0.25)',
                        border: '1px solid rgba(76, 175, 80, 0.45)',
                        color: 'white',
                        fontWeight: 600
                      }}
                    />
                    <SignOutButton>
                      <Button 
                        variant="outlined" 
                        size="small"
                        sx={{ 
                          borderColor: 'rgba(255, 255, 255, 0.3)',
                          color: 'white',
                          '&:hover': { 
                            borderColor: 'rgba(255, 255, 255, 0.5)',
                            bgcolor: 'rgba(255, 255, 255, 0.1)'
                          }
                        }}
                      >
                        Sign Out
                      </Button>
                    </SignOutButton>
                  </Box>
                  
                  {/* Freshness Indicator */}
                  {(() => {
                    const freshness = getAnalysisFreshness();
                    const chipColor = freshness.isStale ? 'rgba(255, 193, 7, 0.25)' : 'rgba(76, 175, 80, 0.25)';
                    const chipBorder = freshness.isStale ? 'rgba(255, 193, 7, 0.45)' : 'rgba(76, 175, 80, 0.45)';
                    return (
                      <Chip
                        label={`Freshness: ${freshness.label}`}
                        size="small"
                        sx={{
                          bgcolor: chipColor,
                          border: `1px solid ${chipBorder}`,
                          color: 'white',
                          fontWeight: 600
                        }}
                      />
                    );
                  })()}
                  <Button
                    onClick={refreshSEOAnalysis}
                    disabled={analysisLoading}
                    variant="outlined"
                    size="small"
                    sx={{
                      color: 'white',
                      borderColor: 'rgba(255, 255, 255, 0.6)',
                      '&:hover': { borderColor: 'rgba(255, 255, 255, 0.9)' }
                    }}
                  >
                    {analysisLoading ? 'Refreshing…' : 'Refresh'}
                  </Button>
                </Box>
              </Box>

              {/* GSC Connection Section */}
              <Box sx={{ mb: 3 }}>
                <GSCLoginButton />
              </Box>

              {/* CopilotKit Test Panel removed */}

              {/* Executive Summary */}
              <Box sx={{ mb: 4 }}>
                <Typography variant="h6" sx={{ color: 'white', fontWeight: 600, mb: 2 }}>
                  📊 Performance Overview
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6} sm={3}>
                    <GlassCard sx={{ p: 2 }}>
                      <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                        Organic Traffic
                      </Typography>
                      <Typography variant="h5" sx={{ color: '#4CAF50' }}>
                        {data.metrics.traffic.value}
                      </Typography>
                    </GlassCard>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <GlassCard sx={{ p: 2 }}>
                      <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                        Average Ranking
                      </Typography>
                      <Typography variant="h5" sx={{ color: '#2196F3' }}>
                        {data.metrics.rankings.value}
                      </Typography>
                    </GlassCard>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <GlassCard sx={{ p: 2 }}>
                      <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                        Mobile Speed
                      </Typography>
                      <Typography variant="h5" sx={{ color: '#FF9800' }}>
                        {data.metrics.mobile.value}
                      </Typography>
                    </GlassCard>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <GlassCard sx={{ p: 2 }}>
                      <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                        Keywords Tracked
                      </Typography>
                      <Typography variant="h5" sx={{ color: '#9C27B0' }}>
                        {data.metrics.keywords.value}
                      </Typography>
                    </GlassCard>
                  </Grid>
                </Grid>
              </Box>

              {/* SEO Analyzer Panel */}
              <SEOAnalyzerPanel
                analysisData={analysisData}
                onRunAnalysis={runSEOAnalysis}
                loading={analysisLoading}
                error={analysisError}
              />

              {/* Copilot Suggestions Panel */}
              <Box sx={{ mt: 4 }}>
                <SEOCopilotSuggestions />
              </Box>
            </motion.div>
          </AnimatePresence>
        </Container>
      </DashboardContainer>
    </SEOCopilotKitProvider>
  );
};

export default SEODashboard;