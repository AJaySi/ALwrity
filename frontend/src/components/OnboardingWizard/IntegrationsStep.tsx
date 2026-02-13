import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Fade,
  Snackbar,
  Typography,
  Paper
} from '@mui/material';
import {
  // Social Media Icons
  Facebook as FacebookIcon,
  Twitter as TwitterIcon,
  Instagram as InstagramIcon,
  LinkedIn as LinkedInIcon,
  YouTube as YouTubeIcon,
  VideoLibrary as TikTokIcon,
  Pinterest as PinterestIcon,
  // Platform Icons
  Web as WordPressIcon,
  Web as WixIcon,
  Google as GoogleIcon,
  Analytics as AnalyticsIcon
} from '@mui/icons-material';

// Import refactored components
import EmailSection from './common/EmailSection';
import PlatformSection from './common/PlatformSection';
import BenefitsSummary from './common/BenefitsSummary';
import ComingSoonSection from './common/ComingSoonSection';
import { useWordPressOAuth } from '../../hooks/useWordPressOAuth';
import { useBingOAuth } from '../../hooks/useBingOAuth';
import { useGSCConnection } from './common/useGSCConnection';
import { usePlatformConnections } from './common/usePlatformConnections';
import PlatformAnalytics from '../shared/PlatformAnalytics';
import GSCTaskReportsPanel from '../shared/GSCTaskReportsPanel';
import { cachedAnalyticsAPI } from '../../api/cachedAnalytics';
import { gscAPI, type GSCDataQualityResponse, type GSCCachedOpportunitiesResponse } from '../../api/gsc';

interface IntegrationsStepProps {
  onContinue: () => void;
  updateHeaderContent: (content: { title: string; description: string }) => void;
}

interface IntegrationPlatform {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  category: 'website' | 'social' | 'analytics';
  status: 'available' | 'connected' | 'coming_soon' | 'disabled';
  features: string[];
  benefits: string[];
  oauthUrl?: string;
  isEnabled: boolean;
}

const IntegrationsStep: React.FC<IntegrationsStepProps> = ({ onContinue, updateHeaderContent }) => {
  const [email, setEmail] = useState<string>('');

  // Use custom hooks
  const { gscSites, connectedPlatforms, setConnectedPlatforms, handleGSCConnect, refreshGSCStatus } = useGSCConnection();
  const [primaryGscSite, setPrimaryGscSite] = useState<string>(() => localStorage.getItem('onboarding_primary_gsc_site') || '');
  const [gscDataQuality, setGscDataQuality] = useState<GSCDataQualityResponse | null>(null);
  const [gscOpportunities, setGscOpportunities] = useState<GSCCachedOpportunitiesResponse | null>(null);

  // Invalidate analytics cache when platform connections change
  const invalidateAnalyticsCache = useCallback(() => {
    console.log('🔄 IntegrationsStep: Invalidating analytics cache due to connection change');
    cachedAnalyticsAPI.invalidateAll();
  }, []);

  const { isLoading, showToast, setShowToast, toastMessage, handleConnect } = usePlatformConnections();

  // WordPress OAuth hook
  const { connected: wordpressConnected, sites: wordpressSites } = useWordPressOAuth();
  
  // Bing OAuth hook
  const { connected: bingConnected, sites: bingSites, connect: connectBing } = useBingOAuth();
  console.log('Bing OAuth hook initialized:', { bingConnected, connectBing: typeof connectBing });

  // Initialize integrations data
  const [integrations] = useState<IntegrationPlatform[]>([
    // Website Platforms
    {
      id: 'wix',
      name: 'Wix',
      description: 'Connect your Wix website for automated content publishing and analytics',
      icon: <WixIcon />,
      category: 'website',
      status: 'available',
      features: ['Auto-publish content', 'Analytics tracking', 'SEO optimization'],
      benefits: ['Direct publishing to your Wix site', 'Content performance insights', 'Automated SEO optimization'],
      oauthUrl: '/api/oauth/wix/connect',
      isEnabled: true
    },
    {
      id: 'wordpress',
      name: 'WordPress',
      description: 'Connect your WordPress.com sites with secure OAuth authentication',
      icon: <WordPressIcon />,
      category: 'website',
      status: 'available',
      features: ['OAuth authentication', 'Auto-publish content', 'Media management', 'SEO optimization'],
      benefits: ['Secure OAuth connection', 'Direct publishing to WordPress', 'Media library integration', 'Advanced SEO features'],
      isEnabled: true
    },
    // Analytics Platforms
    {
      id: 'gsc',
      name: 'Google Search Console',
      description: 'Connect GSC for comprehensive SEO analytics and content optimization',
      icon: <GoogleIcon />,
      category: 'analytics',
      status: 'available',
      features: ['Search performance data', 'Keyword insights', 'Content optimization'],
      benefits: ['Real-time SEO metrics', 'Keyword performance tracking', 'Content gap analysis'],
      oauthUrl: '/gsc/auth/url',
      isEnabled: true
    },
    {
      id: 'bing',
      name: 'Bing Webmaster Tools',
      description: 'Connect Bing Webmaster for comprehensive SEO insights and search performance data',
      icon: <AnalyticsIcon />,
      category: 'analytics',
      status: 'available',
      features: ['Bing search performance', 'SEO insights', 'Index status monitoring'],
      benefits: ['Bing search analytics', 'SEO optimization insights', 'Search engine visibility tracking'],
      oauthUrl: '/bing/auth/url',
      isEnabled: true
    },
    // Social Media Platforms
    {
      id: 'facebook',
      name: 'Facebook',
      description: 'Connect your Facebook page for AI-powered content creation and posting',
      icon: <FacebookIcon />,
      category: 'social',
      status: 'coming_soon',
      features: ['Auto-posting', 'Engagement tracking', 'Content optimization'],
      benefits: ['Automated Facebook posts', 'Engagement analytics', 'Content performance insights'],
      isEnabled: false
    },
    {
      id: 'twitter',
      name: 'Twitter',
      description: 'Connect your Twitter account for automated tweeting and analytics',
      icon: <TwitterIcon />,
      category: 'social',
      status: 'coming_soon',
      features: ['Auto-tweeting', 'Trend analysis', 'Engagement tracking'],
      benefits: ['Automated Twitter posts', 'Trend monitoring', 'Audience insights'],
      isEnabled: false
    },
    {
      id: 'linkedin',
      name: 'LinkedIn',
      description: 'Connect your LinkedIn profile for professional content publishing',
      icon: <LinkedInIcon />,
      category: 'social',
      status: 'coming_soon',
      features: ['Professional posting', 'Network insights', 'Content optimization'],
      benefits: ['LinkedIn article publishing', 'Professional network analytics', 'B2B content insights'],
      isEnabled: false
    },
    {
      id: 'instagram',
      name: 'Instagram',
      description: 'Connect your Instagram account for visual content management',
      icon: <InstagramIcon />,
      category: 'social',
      status: 'coming_soon',
      features: ['Visual content posting', 'Story management', 'Engagement tracking'],
      benefits: ['Instagram post automation', 'Visual content optimization', 'Story insights'],
      isEnabled: false
    },
    {
      id: 'youtube',
      name: 'YouTube',
      description: 'Connect your YouTube channel for video content optimization',
      icon: <YouTubeIcon />,
      category: 'social',
      status: 'coming_soon',
      features: ['Video optimization', 'Thumbnail generation', 'Analytics tracking'],
      benefits: ['Video SEO optimization', 'Thumbnail automation', 'YouTube analytics'],
      isEnabled: false
    },
    {
      id: 'tiktok',
      name: 'TikTok',
      description: 'Connect your TikTok account for short-form content optimization',
      icon: <TikTokIcon />,
      category: 'social',
      status: 'coming_soon',
      features: ['Trend analysis', 'Content optimization', 'Performance tracking'],
      benefits: ['TikTok trend insights', 'Content performance analytics', 'Viral content optimization'],
      isEnabled: false
    },
    {
      id: 'pinterest',
      name: 'Pinterest',
      description: 'Connect your Pinterest account for visual content strategy',
      icon: <PinterestIcon />,
      category: 'social',
      status: 'coming_soon',
      features: ['Pin optimization', 'Board management', 'Visual analytics'],
      benefits: ['Pinterest pin automation', 'Visual content strategy', 'Pin performance insights'],
      isEnabled: false
    }
  ]);

  useEffect(() => {
    updateHeaderContent({
      title: 'Connect Your Platforms',
      description: 'Connect your websites and social media accounts to enable AI-powered content publishing and analytics'
    });
  }, [updateHeaderContent]);


  useEffect(() => {
    if (!gscSites || gscSites.length === 0) return;
    if (primaryGscSite && gscSites.some((s) => s.siteUrl === primaryGscSite)) return;

    const defaultSite = gscSites[0].siteUrl;
    setPrimaryGscSite(defaultSite);
    localStorage.setItem('onboarding_primary_gsc_site', defaultSite);
  }, [gscSites, primaryGscSite]);

  useEffect(() => {
    if (!connectedPlatforms.includes('gsc') || !primaryGscSite) {
      setGscDataQuality(null);
      setGscOpportunities(null);
      return;
    }

    (async () => {
      try {
        const [quality, opportunities] = await Promise.all([
          gscAPI.getDataQuality(primaryGscSite),
          gscAPI.getOpportunities(primaryGscSite)
        ]);
        setGscDataQuality(quality);
        setGscOpportunities(opportunities);
      } catch (error) {
        console.warn('Failed to load GSC onboarding insights', error);
        setGscDataQuality(null);
        setGscOpportunities(null);
      }
    })();
  }, [connectedPlatforms, primaryGscSite]);

  const handlePrimaryGscSiteChange = useCallback((siteUrl: string) => {
    setPrimaryGscSite(siteUrl);
    localStorage.setItem('onboarding_primary_gsc_site', siteUrl);
  }, []);

  // Handle WordPress connection status changes
  useEffect(() => {
    console.log('IntegrationsStep: WordPress status changed:', {
      wordpressConnected,
      wordpressSitesCount: wordpressSites.length,
      connectedPlatforms,
      currentPlatforms: connectedPlatforms
    });
    
    if (wordpressConnected && wordpressSites.length > 0) {
      // WordPress is connected, add to connected platforms
      if (!connectedPlatforms.includes('wordpress')) {
        console.log('IntegrationsStep: Adding WordPress to connected platforms');
        setConnectedPlatforms([...connectedPlatforms, 'wordpress']);
        console.log('WordPress connection detected:', wordpressSites);
        invalidateAnalyticsCache();
      } else {
        console.log('IntegrationsStep: WordPress already in connected platforms');
      }
    } else if (!wordpressConnected && connectedPlatforms.includes('wordpress')) {
      // WordPress is disconnected, remove from connected platforms
      console.log('IntegrationsStep: Removing WordPress from connected platforms');
      setConnectedPlatforms(connectedPlatforms.filter(platform => platform !== 'wordpress'));
      console.log('WordPress disconnection detected');
      invalidateAnalyticsCache();
    } else {
      console.log('IntegrationsStep: No WordPress status change needed');
    }
  }, [wordpressConnected, wordpressSites, connectedPlatforms, setConnectedPlatforms, invalidateAnalyticsCache]);

  // Handle Bing connection status changes
  useEffect(() => {
    console.log('IntegrationsStep: Bing status changed:', {
      bingConnected,
      bingSitesCount: bingSites.length,
      connectedPlatforms,
      currentPlatforms: connectedPlatforms
    });
    
    if (bingConnected && bingSites.length > 0) {
      if (!connectedPlatforms.includes('bing')) {
        console.log('IntegrationsStep: Adding Bing to connected platforms');
        setConnectedPlatforms([...connectedPlatforms, 'bing']);
        console.log('Bing connection detected:', bingSites);
        invalidateAnalyticsCache();
      } else {
        console.log('IntegrationsStep: Bing already in connected platforms');
      }
    } else if (!bingConnected && connectedPlatforms.includes('bing')) {
      console.log('IntegrationsStep: Removing Bing from connected platforms');
      setConnectedPlatforms(connectedPlatforms.filter(platform => platform !== 'bing'));
      console.log('Bing disconnection detected');
      invalidateAnalyticsCache();
    } else {
      console.log('IntegrationsStep: No Bing status change needed');
    }
  }, [bingConnected, bingSites, connectedPlatforms, setConnectedPlatforms, invalidateAnalyticsCache]);

  // Handle OAuth callback parameters (legacy support)
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const wordpressConnected = urlParams.get('wordpress_connected');
    const blogUrl = urlParams.get('blog_url');
    const error = urlParams.get('error');

    if (wordpressConnected === 'true' && blogUrl) {
      // WordPress OAuth successful
      setConnectedPlatforms([...connectedPlatforms, 'wordpress']);
      // Remove query parameters from URL
      window.history.replaceState({}, document.title, window.location.pathname);
      console.log('WordPress OAuth connection successful:', blogUrl);
    } else if (error) {
      // WordPress OAuth failed
      console.error('WordPress OAuth error:', error);
      // Remove query parameters from URL
      window.history.replaceState({}, document.title, window.location.pathname);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Get user email from Clerk
  useEffect(() => {
    const getUserEmail = () => {
      if (typeof window !== 'undefined') {
        const clerkUser = (window as any).__clerk_user;
        if (clerkUser?.emailAddresses?.[0]?.emailAddress) {
          return clerkUser.emailAddresses[0].emailAddress;
        }
        
        const clerkSession = localStorage.getItem('__clerk_session');
        if (clerkSession) {
          try {
            const sessionData = JSON.parse(clerkSession);
            if (sessionData?.user?.emailAddresses?.[0]?.emailAddress) {
              return sessionData.user.emailAddresses[0].emailAddress;
            }
          } catch (e) {
            // Ignore parsing errors
          }
        }
        
        const userData = localStorage.getItem('user_data');
        if (userData) {
          try {
            const data = JSON.parse(userData);
            if (data.email) return data.email;
          } catch (e) {
            // Ignore parsing errors
          }
        }
        
        const currentUserEmail = 'ajay.calsoft@gmail.com';
        if (currentUserEmail && currentUserEmail.includes('@')) {
          return currentUserEmail;
        }
      }
      
      return 'user@example.com';
    };
    
    const userEmail = getUserEmail();
    setEmail(userEmail);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handlePlatformConnect = async (platformId: string) => {
    console.log('🚀 INTEGRATIONS_STEP: handlePlatformConnect called with platformId:', platformId);
    console.log('🚀 INTEGRATIONS_STEP: platformId type:', typeof platformId);
    console.log('🚀 INTEGRATIONS_STEP: platformId length:', platformId.length);
    console.log('🚀 INTEGRATIONS_STEP: platformId === "bing":', platformId === 'bing');
    console.log('🚀 INTEGRATIONS_STEP: platformId === "gsc":', platformId === 'gsc');
    console.log('🚀 INTEGRATIONS_STEP: connectBing function type:', typeof connectBing);
    console.log('🚀 INTEGRATIONS_STEP: connectBing function:', connectBing);
    console.log('🚀 INTEGRATIONS_STEP: Stack trace:', new Error().stack);
    
    if (platformId === 'gsc') {
      console.log('🚀 INTEGRATIONS_STEP: Handling GSC connection');
      await handleGSCConnect();
    } else if (platformId === 'bing') {
      console.log('🚀 INTEGRATIONS_STEP: Handling Bing connection - about to call connectBing');
      // Use the Bing OAuth hook for connection
      try {
        console.log('🚀 INTEGRATIONS_STEP: Calling connectBing()...');
        await connectBing();
        console.log('🚀 INTEGRATIONS_STEP: Bing connection initiated successfully');
      } catch (error) {
        console.error('🚀 INTEGRATIONS_STEP: Bing connection failed:', error);
      }
    } else {
      console.log('🚀 INTEGRATIONS_STEP: Handling other platform connection:', platformId);
      console.log('🚀 INTEGRATIONS_STEP: This should NOT happen for Bing!');
      await handleConnect(platformId);
    }
  };

  // Filter platforms by category
  const websitePlatforms = integrations.filter(p => p.category === 'website');
  const analyticsPlatforms = integrations.filter(p => p.category === 'analytics');
  const socialPlatforms = integrations.filter(p => p.category === 'social');


  return (
    <Box sx={{ width: '100%', maxWidth: '100%', p: { xs: 1, sm: 2, md: 3 } }}>
      {/* Email Address Section */}
      <EmailSection email={email} onEmailChange={setEmail} />

      {/* Website Platforms */}
      <Fade in timeout={800}>
        <div>
          <PlatformSection
            title="Website Platforms"
            description="Connect your website for automated content publishing and SEO optimization"
            platforms={websitePlatforms}
            connectedPlatforms={connectedPlatforms}
            gscSites={null}
                  isLoading={isLoading}
            onConnect={handlePlatformConnect}
            onDisconnect={(platformId) => {
              setConnectedPlatforms(connectedPlatforms.filter(p => p !== platformId));
            }}
            setConnectedPlatforms={setConnectedPlatforms}
            primarySite={primaryGscSite}
            onPrimarySiteChange={handlePrimaryGscSiteChange}
            dataQuality={gscDataQuality}
            opportunities={gscOpportunities}
          />
        </div>
      </Fade>

      {/* Analytics Platforms */}
      <Fade in timeout={1000}>
        <div>
          <PlatformSection
            title="Analytics & SEO"
            description="Connect analytics platforms for data-driven content optimization"
            platforms={analyticsPlatforms}
            connectedPlatforms={connectedPlatforms}
            gscSites={gscSites}
            isLoading={isLoading}
            onConnect={handlePlatformConnect}
            primarySite={primaryGscSite}
            onPrimarySiteChange={handlePrimaryGscSiteChange}
            dataQuality={gscDataQuality}
            opportunities={gscOpportunities}
          />
        </div>
      </Fade>

      {/* Analytics Data Display */}
      {connectedPlatforms.length > 0 && (
        <Fade in timeout={1200}>
          <div>
            <Paper 
              elevation={2} 
              sx={{ 
                mt: 3, 
                p: 3, 
                borderRadius: 2,
                background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)'
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <AnalyticsIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6" sx={{ fontWeight: 600, color: 'text.primary' }}>
                  Platform Analytics
                </Typography>
              </Box>
              <Typography variant="body2" sx={{ color: 'text.secondary', mb: 3 }}>
                Here's what data is available from your connected platforms:
              </Typography>
              
              <PlatformAnalytics 
                platforms={connectedPlatforms}
                showSummary={true}
                refreshInterval={0}
                onDataLoaded={(data: any) => {
                  console.log('Analytics data loaded:', data);
                }}
                onRefreshReady={(refreshFn) => {
                  console.log('🔄 PlatformAnalytics refresh function ready');
                  // Store the refresh function for potential use
                  (window as any).refreshAnalytics = refreshFn;
                }}
              />
            </Paper>
          </div>
        </Fade>
      )}



      {/* Optional Step-5 task testing UI (shared with SEO dashboard) */}
      {connectedPlatforms.includes('gsc') && (
        <Fade in timeout={1250}>
          <div>
            <GSCTaskReportsPanel
              siteUrl={primaryGscSite || undefined}
              title="Step 5 Optional Task Testing (GSC)"
            />
          </div>
        </Fade>
      )}

      {/* Social Media Platforms */}
      <Fade in timeout={1200}>
        <div>
          <PlatformSection
            title="Social Media Platforms"
            description="Connect your social media accounts for automated posting and engagement analytics"
            platforms={socialPlatforms}
            connectedPlatforms={connectedPlatforms}
            gscSites={null}
            isLoading={isLoading}
            onConnect={handlePlatformConnect}
            primarySite={primaryGscSite}
            onPrimarySiteChange={handlePrimaryGscSiteChange}
            dataQuality={gscDataQuality}
            opportunities={gscOpportunities}
          />
        </div>
      </Fade>

      {/* Benefits Summary */}
      <Fade in timeout={1400}>
        <div>
        <BenefitsSummary />
        </div>
      </Fade>

      {/* Coming Soon Section */}
      <ComingSoonSection />

      {/* Success Toast */}
      <Snackbar
        open={showToast}
        autoHideDuration={4000}
        onClose={() => setShowToast(false)}
        message={toastMessage}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        sx={{
          '& .MuiSnackbarContent-root': {
            backgroundColor: '#10b981',
            color: 'white',
            fontWeight: 600
          }
        }}
      />
    </Box>
  );
};

export default IntegrationsStep; 