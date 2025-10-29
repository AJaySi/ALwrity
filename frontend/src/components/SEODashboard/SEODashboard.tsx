import React, { useEffect, useRef, useState } from 'react';
import {
  Box,
  Container,
  Grid,
  Typography,
  Alert,
  Skeleton,
  Chip,
  Button,
  IconButton,
  Tooltip,
  Menu,
  MenuItem,
  Divider,
  Avatar
} from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth, useUser, SignInButton, SignOutButton } from '@clerk/clerk-react';
import { apiClient } from '../../api/client';
import {
  Search as SearchIcon,
  Refresh as RefreshIcon,
  Person as PersonIcon,
  ExitToApp as ExitIcon,
  ArrowBack as ArrowBackIcon,
  MoreVert as MoreVertIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
  Info as InfoIcon
} from '@mui/icons-material';

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

// Shared components
import PlatformAnalytics from '../shared/PlatformAnalytics';
import { cachedAnalyticsAPI } from '../../api/cachedAnalytics';

// OAuth hooks
import { useBingOAuth } from '../../hooks/useBingOAuth';
import { useGSCConnection } from '../OnboardingWizard/common/useGSCConnection';

// SEO Dashboard component
const SEODashboard: React.FC = () => {
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

  // OAuth hooks
  const { connect: connectBing } = useBingOAuth();
  const { handleGSCConnect } = useGSCConnection();

  // Platform status state
  const [platformStatus, setPlatformStatus] = useState({
    gsc: { connected: false, sites: [], last_sync: null, status: 'disconnected' },
    bing: { 
      connected: false, 
      sites: [], 
      last_sync: null, 
      status: 'disconnected',
      has_expired_tokens: false,
      last_token_date: undefined,
      total_tokens: 0
    }
  });

  // Menu state
  const [userMenuAnchor, setUserMenuAnchor] = useState<null | HTMLElement>(null);
  const [statusMenuAnchor, setStatusMenuAnchor] = useState<null | HTMLElement>(null);
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);
  
  // Competitor analysis data from onboarding step 3
  const [competitorAnalysisData, setCompetitorAnalysisData] = useState<any>(null);

  // PlatformAnalytics refresh handle
  const platformRefreshRef = useRef<(() => Promise<void>) | null>(null);

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

  // Load competitor analysis data on component mount
  useEffect(() => {
    loadCompetitorAnalysisData();
  }, []);

  // Reconnect handlers using existing OAuth hooks
  const handleGSCReconnect = async () => {
    try {
      console.log('Initiating GSC reconnect...');
      await handleGSCConnect();
    } catch (error) {
      console.error('Error reconnecting GSC:', error);
    }
  };

  const handleBingReconnect = async () => {
    try {
      console.log('Initiating Bing reconnect...');
      // Purge expired tokens before reconnecting to avoid refresh loops
      try {
        await apiClient.post('/bing/purge-expired');
        console.log('Purged expired Bing tokens before reconnect');
      } catch (purgeError) {
        console.warn('Failed to purge expired tokens (non-critical):', purgeError);
      }
      await connectBing();
      // After successful reconnect, refresh platform status and run analysis
      try {
        // Invalidate backend analytics cache for Bing
        try {
          await apiClient.post('/api/analytics/cache/clear', null, { params: { platform: 'bing' } });
          console.log('Cleared backend analytics cache for Bing');
        } catch (cacheErr) {
          console.warn('Failed to clear backend analytics cache (non-critical):', cacheErr);
        }

        // Invalidate frontend cached analytics
        try {
          cachedAnalyticsAPI.invalidatePlatformStatus();
          // Optional: clear all analytics cache if available
          // @ts-ignore - method may not exist in older builds
          cachedAnalyticsAPI.clearCache?.();
          console.log('Cleared frontend analytics cache');
        } catch (feCacheErr) {
          console.warn('Failed to clear frontend analytics cache (non-critical):', feCacheErr);
        }

        await fetchPlatformStatus();
      } catch (e) {
        console.warn('Post-reconnect platform status refresh failed:', e);
      }
      try {
        await useSEODashboardStore.getState().refreshSEOAnalysis();
      } catch (e) {
        console.warn('Post-reconnect analysis refresh failed:', e);
      }

      // Force PlatformAnalytics to refresh (bypass cache)
      try {
        await platformRefreshRef.current?.();
      } catch (e) {
        console.warn('Platform analytics forced refresh failed (non-critical):', e);
      }
    } catch (error) {
      console.error('Error reconnecting Bing:', error);
    }
  };

  // One-run guard to avoid duplicate fetches under StrictMode
  const dataFetchedRef = useRef(false);

  // Consolidated data fetching effect
  useEffect(() => {
    if (dataFetchedRef.current || !isSignedIn) return;
    dataFetchedRef.current = true;

    const fetchAllData = async () => {
      let websiteUrl = 'https://alwrity.com'; // Default fallback
      
      try {
        setLoading(true);
        
        // Fetch platform status and user data in parallel
        const [platformResponse, userData] = await Promise.all([
          apiClient.get('/api/seo-dashboard/platforms'),
          userDataAPI.getUserData()
        ]);
        
        console.log('Platform status response:', platformResponse.status, platformResponse.statusText);
        console.log('Platform status data:', platformResponse.data);
        setPlatformStatus(platformResponse.data);
        
        websiteUrl = userData?.website_url || 'https://alwrity.com';
        
        // Fetch real data from backend using authenticated API client
        console.log('Fetching SEO dashboard overview...');
        const response = await apiClient.get('/api/seo-dashboard/overview', {
          params: { site_url: websiteUrl }
        });
        
        console.log('SEO overview response:', response.status, response.statusText);
        console.log('Real SEO data received:', response.data);
        setData(response.data);
      } catch (error) {
        console.error('Error fetching SEO dashboard data:', error);
        // Fallback to mock data on error
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
      } finally {
        setLoading(false);
      }
    };

    fetchAllData();
  }, [isSignedIn, setLoading, setData]);

  useEffect(() => {
    // Run initial SEO analysis if no data exists
    if (!loading && !error && data) {
      // Check if we have cached analysis data first
      const store = useSEODashboardStore.getState();
      store.checkAndRunInitialAnalysis();
      
      // If no cached analysis data and we have a website URL, run initial analysis
      if (!store.analysisData && data.website_url) {
        console.log('No cached analysis data found, running initial SEO analysis...');
        store.runSEOAnalysis();
      }
    }
  }, [loading, error, data]);

  // Menu handlers
  const handleUserMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setUserMenuAnchor(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setUserMenuAnchor(null);
  };

  const handleStatusMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setStatusMenuAnchor(event.currentTarget);
  };

  const handleStatusMenuClose = () => {
    setStatusMenuAnchor(null);
  };

  const handleBackToDashboard = () => {
    window.location.href = '/seo-dashboard';
  };

  const handleRefreshData = async () => {
    try {
      setLoading(true);
      await refreshSEOAnalysis();
      await fetchPlatformStatus();
      setLastRefresh(new Date());
    } catch (error) {
      console.error('Error refreshing data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Background jobs visibility (user-triggered)
  const [showBackgroundJobs, setShowBackgroundJobs] = useState(false);

  // Platform status fetching function
  const fetchPlatformStatus = async () => {
    try {
      console.log('Fetching platform status...');
      const response = await apiClient.get('/api/seo-dashboard/platforms');
      console.log('Platform status response:', response.status, response.statusText);
      console.log('Platform status data:', response.data);
      setPlatformStatus(response.data);
    } catch (error) {
      console.error('Error fetching platform status:', error);
    }
  };

  // Load competitor analysis data from onboarding step 3
  const loadCompetitorAnalysisData = () => {
    try {
      const cachedData = localStorage.getItem('competitor_analysis_data');
      const cachedUrl = localStorage.getItem('competitor_analysis_url');
      const cachedTimestamp = localStorage.getItem('competitor_analysis_timestamp');
      
      if (cachedData && cachedUrl && cachedTimestamp) {
        const analysisData = JSON.parse(cachedData);
        const timestamp = parseInt(cachedTimestamp);
        const isRecent = (Date.now() - timestamp) < (7 * 24 * 60 * 60 * 1000); // 7 days
        
        if (isRecent) {
          console.log('Loading competitor analysis data from onboarding step 3:', analysisData);
          setCompetitorAnalysisData(analysisData);
        } else {
          console.log('Competitor analysis data is too old, not loading');
        }
      } else {
        console.log('No competitor analysis data found in localStorage');
      }
    } catch (error) {
      console.error('Error loading competitor analysis data:', error);
    }
  };


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
              {/* Professional Compact Header */}
              <Box sx={{ 
                mb: 4, 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'space-between',
                py: 2,
                px: 3,
                bgcolor: 'rgba(255, 255, 255, 0.05)',
                borderRadius: 2,
                border: '1px solid rgba(255, 255, 255, 0.1)'
              }}>
                {/* Left Section - Navigation & Title */}
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <IconButton
                    onClick={handleBackToDashboard}
                    sx={{ 
                      color: 'white',
                      '&:hover': { bgcolor: 'rgba(255, 255, 255, 0.1)' }
                    }}
                  >
                    <ArrowBackIcon />
                  </IconButton>
                  
                  <Box>
                    <Typography variant="h5" sx={{ color: 'white', fontWeight: 700, lineHeight: 1.2 }}>
                      SEO Dashboard
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                      AI-powered insights and recommendations
                    </Typography>
                  </Box>
                </Box>

                {/* Center Section - Status Overview */}
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Tooltip title="Platform Connection Status">
                    <IconButton
                      onClick={handleStatusMenuOpen}
                      sx={{ 
                        color: 'white',
                        '&:hover': { bgcolor: 'rgba(255, 255, 255, 0.1)' }
                      }}
                    >
                      <CheckCircleIcon sx={{ 
                        color: platformStatus.gsc.connected && platformStatus.bing.connected 
                          ? '#4CAF50' 
                          : platformStatus.gsc.connected || platformStatus.bing.connected 
                            ? '#FF9800' 
                            : '#f44336' 
                      }} />
                    </IconButton>
                  </Tooltip>
                  
                  <Tooltip title="Data Freshness">
                    <Chip
                      icon={<ScheduleIcon />}
                      label={(() => {
                        const freshness = getAnalysisFreshness();
                        return freshness.label;
                      })()}
                      size="small"
                      sx={{
                        bgcolor: 'rgba(255, 255, 255, 0.1)',
                        color: 'white',
                        border: '1px solid rgba(255, 255, 255, 0.2)',
                        fontSize: '0.75rem'
                      }}
                    />
                  </Tooltip>
                </Box>

                {/* Right Section - User Menu */}
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Avatar sx={{ width: 32, height: 32, bgcolor: 'rgba(33, 150, 243, 0.8)' }}>
                    <PersonIcon fontSize="small" />
                  </Avatar>
                  
                  <IconButton
                    onClick={handleUserMenuOpen}
                    sx={{ 
                      color: 'white',
                      '&:hover': { bgcolor: 'rgba(255, 255, 255, 0.1)' }
                    }}
                  >
                    <MoreVertIcon />
                  </IconButton>
                </Box>

          {/* Status Menu */}
          <Menu
            anchorEl={statusMenuAnchor}
            open={Boolean(statusMenuAnchor)}
            onClose={handleStatusMenuClose}
            PaperProps={{
              sx: {
                bgcolor: 'rgba(30, 30, 30, 0.95)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                color: 'white',
                minWidth: 280
              }
            }}
          >
            <MenuItem disabled>
              <Typography variant="subtitle2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                Platform Status
              </Typography>
            </MenuItem>
            
            {/* GSC Status */}
            <MenuItem>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CheckCircleIcon sx={{ 
                    color: platformStatus.gsc.connected ? '#4CAF50' : '#f44336',
                    fontSize: 16
                  }} />
                  <Typography variant="body2">
                    Google Search Console: {platformStatus.gsc.connected ? 'Connected' : 'Disconnected'}
                  </Typography>
                </Box>
                {!platformStatus.gsc.connected && (
                  <Button
                    size="small"
                    variant="outlined"
                    onClick={handleGSCReconnect}
                    sx={{
                      ml: 2,
                      borderColor: 'rgba(255, 255, 255, 0.3)',
                      color: 'white',
                      fontSize: '0.75rem',
                      '&:hover': {
                        borderColor: 'rgba(255, 255, 255, 0.5)',
                        bgcolor: 'rgba(255, 255, 255, 0.1)'
                      }
                    }}
                  >
                    Reconnect
                  </Button>
                )}
              </Box>
            </MenuItem>
            
            {/* Bing Status */}
            <MenuItem>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CheckCircleIcon sx={{ 
                    color: platformStatus.bing.connected ? '#4CAF50' : 
                           platformStatus.bing.status === 'expired' ? '#FF9800' : '#f44336',
                    fontSize: 16
                  }} />
                  <Box>
                    <Typography variant="body2">
                      Bing Webmaster: {platformStatus.bing.connected ? 'Connected' : 
                                     platformStatus.bing.status === 'expired' ? 'Expired' : 'Disconnected'}
                    </Typography>
                    {platformStatus.bing.status === 'expired' && platformStatus.bing.last_token_date && (
                      <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.5)', fontSize: '0.7rem' }}>
                        Last connected: {new Date(platformStatus.bing.last_token_date).toLocaleDateString()}
                      </Typography>
                    )}
                  </Box>
                </Box>
                {!platformStatus.bing.connected && (
                  <Button
                    size="small"
                    variant="outlined"
                    onClick={handleBingReconnect}
                    sx={{
                      ml: 2,
                      borderColor: platformStatus.bing.status === 'expired' ? '#FF9800' : 'rgba(255, 255, 255, 0.3)',
                      color: platformStatus.bing.status === 'expired' ? '#FF9800' : 'white',
                      fontSize: '0.75rem',
                      '&:hover': {
                        borderColor: platformStatus.bing.status === 'expired' ? '#FFB74D' : 'rgba(255, 255, 255, 0.5)',
                        bgcolor: platformStatus.bing.status === 'expired' ? 'rgba(255, 152, 0, 0.1)' : 'rgba(255, 255, 255, 0.1)'
                      }
                    }}
                  >
                    {platformStatus.bing.status === 'expired' ? 'Reconnect' : 'Connect'}
                  </Button>
                )}
              </Box>
            </MenuItem>
          </Menu>

                {/* User Menu */}
                <Menu
                  anchorEl={userMenuAnchor}
                  open={Boolean(userMenuAnchor)}
                  onClose={handleUserMenuClose}
                  PaperProps={{
                    sx: {
                      bgcolor: 'rgba(30, 30, 30, 0.95)',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      color: 'white'
                    }
                  }}
                >
                  <MenuItem disabled>
                    <Typography variant="subtitle2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                      {user?.primaryEmailAddress?.emailAddress || 'User'}
                    </Typography>
                  </MenuItem>
                  <Divider sx={{ bgcolor: 'rgba(255, 255, 255, 0.1)' }} />
                  <MenuItem onClick={handleRefreshData}>
                    <RefreshIcon sx={{ mr: 1, fontSize: 16 }} />
                    <Typography variant="body2">Refresh Data</Typography>
                  </MenuItem>
                  <Divider sx={{ bgcolor: 'rgba(255, 255, 255, 0.1)' }} />
                  <SignOutButton>
                    <MenuItem>
                      <ExitIcon sx={{ mr: 1, fontSize: 16 }} />
                      <Typography variant="body2">Sign Out</Typography>
                    </MenuItem>
                  </SignOutButton>
                </Menu>
              </Box>


              {/* CopilotKit Test Panel removed */}

              {/* Search Performance Overview */}
              <Box sx={{ mb: 4 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
                  <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
                    📊 Search Performance Overview
                  </Typography>
                  <Tooltip title="Real-time analytics data from connected search platforms">
                    <InfoIcon sx={{ color: 'rgba(255, 255, 255, 0.5)', fontSize: 18 }} />
                  </Tooltip>
                  <Box sx={{ flexGrow: 1 }} />
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => setShowBackgroundJobs((v) => !v)}
                    sx={{ textTransform: 'none' }}
                  >
                    {showBackgroundJobs ? 'Hide Background Jobs' : 'Run Background Jobs'}
                  </Button>
                </Box>
                
                <PlatformAnalytics
                  platforms={['gsc', 'bing']}
                  showSummary={true}
                  refreshInterval={0}
                  onDataLoaded={(analyticsData) => {
                    console.log('Real analytics data loaded:', analyticsData);
                  }}
                  onRefreshReady={(fn) => { platformRefreshRef.current = fn; }}
                  onReconnect={(platform) => {
                    if (platform === 'gsc') {
                      handleGSCReconnect();
                    } else if (platform === 'bing') {
                      handleBingReconnect();
                    }
                  }}
                  showBackgroundJobs={showBackgroundJobs}
                />
                
                {/* Enhanced Metrics with Tooltips */}
                <Box sx={{ mt: 3 }}>
                  <Grid container spacing={2}>
                    <Grid item xs={6} sm={3}>
                      <Tooltip title="Number of search engine platforms (GSC, Bing) currently connected to your dashboard">
                        <GlassCard sx={{ p: 2, cursor: 'help' }}>
                          <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
                            Connected Platforms
                          </Typography>
                          <Typography variant="h4" sx={{ color: '#4CAF50', fontWeight: 700 }}>
                            {(platformStatus.gsc.connected ? 1 : 0) + (platformStatus.bing.connected ? 1 : 0)}
                          </Typography>
                          <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                            of 2 platforms
                          </Typography>
                        </GlassCard>
                      </Tooltip>
                    </Grid>
                    
                    <Grid item xs={6} sm={3}>
                      <Tooltip title="Total number of clicks from search results to your website within the selected time period">
                        <GlassCard sx={{ p: 2, cursor: 'help' }}>
                          <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
                            Total Clicks
                          </Typography>
                          <Typography variant="h4" sx={{ color: '#2196F3', fontWeight: 700 }}>
                            {data.metrics?.traffic?.value || data.summary?.clicks || 0}
                          </Typography>
                          <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                            from search results
                          </Typography>
                        </GlassCard>
                      </Tooltip>
                    </Grid>
                    
                    <Grid item xs={6} sm={3}>
                      <Tooltip title="Total number of times your website appeared in search results within the selected time period">
                        <GlassCard sx={{ p: 2, cursor: 'help' }}>
                          <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
                            Total Impressions
                          </Typography>
                          <Typography variant="h4" sx={{ color: '#FF9800', fontWeight: 700 }}>
                            {data.metrics?.impressions?.value || data.summary?.impressions || 0}
                          </Typography>
                          <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                            search appearances
                          </Typography>
                        </GlassCard>
                      </Tooltip>
                    </Grid>
                    
                    <Grid item xs={6} sm={3}>
                      <Tooltip title="Percentage of impressions that resulted in a click to your website (Clicks ÷ Impressions × 100)">
                        <GlassCard sx={{ p: 2, cursor: 'help' }}>
                          <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
                            Overall CTR
                          </Typography>
                          <Typography variant="h4" sx={{ color: '#9C27B0', fontWeight: 700 }}>
                            {data.metrics?.ctr?.value || data.summary?.ctr || 0}%
                          </Typography>
                          <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                            click-through rate
                          </Typography>
                        </GlassCard>
                      </Tooltip>
                    </Grid>
                  </Grid>
                </Box>
              </Box>

              {/* Competitive Analysis from Onboarding Step 3 */}
              {competitorAnalysisData && (
                <Box sx={{ mb: 4 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
                    <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
                      🎯 Competitive Analysis
                    </Typography>
                    <Tooltip title="Real competitor analysis data from onboarding step 3">
                      <InfoIcon sx={{ color: 'rgba(255, 255, 255, 0.5)', fontSize: 18 }} />
                    </Tooltip>
                  </Box>
                  
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={4}>
                      <Tooltip title="Number of competitors discovered during onboarding analysis">
                        <GlassCard sx={{ p: 2, cursor: 'help' }}>
                          <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
                            Competitors Found
                          </Typography>
                          <Typography variant="h4" sx={{ color: '#4CAF50', fontWeight: 700 }}>
                            {competitorAnalysisData.competitors?.length || 0}
                          </Typography>
                          <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                            in your market
                          </Typography>
                        </GlassCard>
                      </Tooltip>
                    </Grid>
                    
                    <Grid item xs={12} md={4}>
                      <Tooltip title="Social media accounts discovered for competitors">
                        <GlassCard sx={{ p: 2, cursor: 'help' }}>
                          <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
                            Social Media Accounts
                          </Typography>
                          <Typography variant="h4" sx={{ color: '#2196F3', fontWeight: 700 }}>
                            {Object.keys(competitorAnalysisData.social_media_accounts || {}).length}
                          </Typography>
                          <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                            competitor accounts
                          </Typography>
                        </GlassCard>
                      </Tooltip>
                    </Grid>
                    
                    <Grid item xs={12} md={4}>
                      <Tooltip title="Social media citations and mentions found">
                        <GlassCard sx={{ p: 2, cursor: 'help' }}>
                          <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
                            Social Citations
                          </Typography>
                          <Typography variant="h4" sx={{ color: '#FF9800', fontWeight: 700 }}>
                            {competitorAnalysisData.social_media_citations?.length || 0}
                          </Typography>
                          <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                            mentions found
                          </Typography>
                        </GlassCard>
                      </Tooltip>
                    </Grid>
                  </Grid>

                  {/* Competitor List */}
                  {competitorAnalysisData.competitors && competitorAnalysisData.competitors.length > 0 && (
                    <Box sx={{ mt: 3 }}>
                      <Typography variant="h6" sx={{ color: 'white', fontWeight: 600, mb: 2 }}>
                        Top Competitors
                      </Typography>
                      <Grid container spacing={2}>
                        {competitorAnalysisData.competitors.slice(0, 6).map((competitor: any, index: number) => (
                          <Grid item xs={12} sm={6} md={4} key={index}>
                            <GlassCard sx={{ p: 2 }}>
                              <Typography variant="subtitle2" sx={{ color: 'white', fontWeight: 600, mb: 1 }}>
                                {competitor.name || competitor.domain || `Competitor ${index + 1}`}
                              </Typography>
                              <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
                                {competitor.domain || competitor.url || 'No domain available'}
                              </Typography>
                              {competitor.description && (
                                <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                                  {competitor.description.length > 100 
                                    ? `${competitor.description.substring(0, 100)}...` 
                                    : competitor.description}
                                </Typography>
                              )}
                            </GlassCard>
                          </Grid>
                        ))}
                      </Grid>
                    </Box>
                  )}

                  {/* Research Summary */}
                  {competitorAnalysisData.research_summary && (
                    <Box sx={{ mt: 3 }}>
                      <Typography variant="h6" sx={{ color: 'white', fontWeight: 600, mb: 2 }}>
                        Research Summary
                      </Typography>
                      <GlassCard sx={{ p: 3 }}>
                        <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.9)', lineHeight: 1.6 }}>
                          {competitorAnalysisData.research_summary}
                        </Typography>
                      </GlassCard>
                    </Box>
                  )}
                </Box>
              )}

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