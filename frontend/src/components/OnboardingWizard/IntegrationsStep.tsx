import React, { useState, useEffect, useCallback } from 'react';
import { useUser } from '@clerk/clerk-react';
import {
  Box,
  Fade,
  Snackbar,
  Typography,
  Paper,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  FormLabel,
  Card,
  CardContent,
  Alert,
  Chip
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
  Analytics as AnalyticsIcon,
  // UI Icons
  Lightbulb as LightbulbIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon
} from '@mui/icons-material';

// Import refactored components
import EmailSection from './common/EmailSection';
import PlatformSection from './common/PlatformSection';
import BenefitsSummary from './common/BenefitsSummary';
import ComingSoonSection from './common/ComingSoonSection';
import { useWordPressOAuth } from '../../hooks/useWordPressOAuth';
import { useWixConnection } from '../../hooks/useWixConnection';
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
  onValidationChange?: (isValid: boolean) => void;
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

const IntegrationsStep: React.FC<IntegrationsStepProps> = ({ onContinue, updateHeaderContent, onValidationChange }) => {
  const { user } = useUser();
  const [email, setEmail] = useState<string>('');

  // Use custom hooks
  const { gscSites, connectedPlatforms, setConnectedPlatforms, handleGSCConnect, refreshGSCStatus } = useGSCConnection();
  const [primaryGscSite, setPrimaryGscSite] = useState<string>(() => localStorage.getItem('onboarding_primary_gsc_site') || '');
  const [gscDataQuality, setGscDataQuality] = useState<GSCDataQualityResponse | null>(null);
  const [gscOpportunities, setGscOpportunities] = useState<GSCCachedOpportunitiesResponse | null>(null);

  // Invalidate analytics cache when platform connections change
  const invalidateAnalyticsCache = useCallback(() => {
    cachedAnalyticsAPI.invalidateAll();
  }, []);

  // Force refresh analytics data (bypass cache)
  const forceRefreshAnalytics = useCallback(async () => {
    try {
      // Clear all cache first
      cachedAnalyticsAPI.clearCache();
      
      // Force refresh platform status
      await cachedAnalyticsAPI.forceRefreshPlatformStatus();
      
      // Force refresh analytics data
      await cachedAnalyticsAPI.forceRefreshAnalyticsData(['bing', 'gsc']);
      
    } catch (error) {
      console.error('IntegrationsStep: Error force refreshing analytics:', error);
    }
  }, []);
  const { isLoading, showToast, setShowToast, toastMessage, handleConnect } = usePlatformConnections();

  // WordPress OAuth hook
  const { connected: wordpressConnected, sites: wordpressSites } = useWordPressOAuth();
  
  // Bing OAuth hook
  const { connected: bingConnected, sites: bingSites, connect: connectBing } = useBingOAuth();

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
    
    if (wordpressConnected && wordpressSites.length > 0) {
      if (!connectedPlatforms.includes('wordpress')) {
        setConnectedPlatforms([...connectedPlatforms, 'wordpress']);
        invalidateAnalyticsCache();
      }
    } else if (!wordpressConnected && connectedPlatforms.includes('wordpress')) {
      // WordPress is disconnected, remove from connected platforms
      setConnectedPlatforms(connectedPlatforms.filter(platform => platform !== 'wordpress'));
      invalidateAnalyticsCache();
    }
  }, [wordpressConnected, wordpressSites, connectedPlatforms, setConnectedPlatforms, invalidateAnalyticsCache]);

  // Handle Bing connection status changes
  useEffect(() => {
    
    if (bingConnected && bingSites.length > 0) {
      if (!connectedPlatforms.includes('bing')) {
        setConnectedPlatforms([...connectedPlatforms, 'bing']);
        invalidateAnalyticsCache();
      }
    } else if (!bingConnected && connectedPlatforms.includes('bing')) {
      setConnectedPlatforms(connectedPlatforms.filter(platform => platform !== 'bing'));
      invalidateAnalyticsCache();
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
    if (user) {
      const primaryEmail = user.primaryEmailAddress?.emailAddress;
      const firstEmail = user.emailAddresses?.[0]?.emailAddress;
      const resolvedEmail = primaryEmail || firstEmail || '';
      
      if (resolvedEmail) {
        setEmail(resolvedEmail);
      }
    }
  }, [user]);

  const handlePlatformConnect = async (platformId: string) => {
    if (platformId === 'gsc') {
      await handleGSCConnect();
    } else if (platformId === 'bing') {
      // Use the Bing OAuth hook for connection
      try {
        await connectBing();
      } catch (error) {
        console.error('Bing connection failed:', error);
      }
    } else {
      await handleConnect(platformId);
    }
  };

  // Filter platforms by category
  const websitePlatforms = integrations.filter(p => p.category === 'website');
  const analyticsPlatforms = integrations.filter(p => p.category === 'analytics');
  const socialPlatforms = integrations.filter(p => p.category === 'social');


  // Primary Site Selection State
  const [primarySite, setPrimarySite] = useState<string>('');
  
  // Get sites from hooks for the memo
  const { sites: wixSites, connected: wixConnected } = useWixConnection();
  
  const availableSites = React.useMemo(() => {
    const sites: { url: string; source: string; name: string }[] = [];
    
    if (wixConnected && wixSites.length > 0) {
      sites.push(...wixSites.map(s => ({ 
        url: s.blog_url, 
        source: 'Wix',
        name: 'Wix Site'
      })));
    }
    
    if (wordpressConnected && wordpressSites.length > 0) {
      sites.push(...wordpressSites.map(s => ({ 
        url: s.blog_url, 
        source: 'WordPress',
        name: 'WordPress Site'
      })));
    }
    
    return sites;
  }, [wixConnected, wixSites, wordpressConnected, wordpressSites]);

  // Default to first site
  useEffect(() => {
    if (availableSites.length > 0 && !primarySite) {
      setPrimarySite(availableSites[0].url);
    }
  }, [availableSites, primarySite]);

  // Save primary site when selected
  useEffect(() => {
    if (primarySite) {
      localStorage.setItem('primary_website', primarySite);
    }
  }, [primarySite]);

  // Validation Effect
  useEffect(() => {
    if (onValidationChange) {
      // Valid if:
      // 1. No sites available (user can proceed without site)
      // 2. Sites available AND primarySite selected
      const isValid = availableSites.length === 0 || !!primarySite;
      onValidationChange(isValid);
    }
  }, [availableSites.length, primarySite, onValidationChange]);

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

      {/* Primary Site Selection */}
      <Fade in timeout={900}>
        <Box sx={{ mt: 3 }}>
          <Paper 
            elevation={2} 
            sx={{ 
              p: 3, 
              borderRadius: 2,
              background: 'linear-gradient(135deg, #f8fafc 0%, #ffffff 100%)',
              border: '1px solid',
              borderColor: primarySite ? '#86efac' : '#e2e8f0'
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2, justifyContent: 'space-between' }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Box 
                  sx={{ 
                    width: 40, 
                    height: 40, 
                    borderRadius: '50%', 
                    bgcolor: primarySite ? '#dcfce7' : '#f1f5f9',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mr: 2
                  }}
                >
                  <LightbulbIcon sx={{ color: primarySite ? '#22c55e' : '#94a3b8' }} />
                </Box>
                <Box>
                  <Typography variant="h6" sx={{ fontWeight: 600, color: '#1e293b' }}>
                    Primary Website Selection
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#64748b' }}>
                    Select your primary website for content publishing
                  </Typography>
                </Box>
              </Box>
              
              {/* Green/Red Indicator */}
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Box
                  sx={{
                    width: 12,
                    height: 12,
                    borderRadius: '50%',
                    bgcolor: primarySite ? '#22c55e' : '#ef4444',
                    boxShadow: primarySite ? '0 0 0 4px #dcfce7' : '0 0 0 4px #fee2e2'
                  }}
                />
                <Typography variant="caption" sx={{ fontWeight: 600, color: primarySite ? '#15803d' : '#b91c1c' }}>
                  {primarySite ? 'Primary Set' : 'Selection Required'}
                </Typography>
              </Box>
            </Box>

            {availableSites.length > 0 ? (
              <FormControl component="fieldset" sx={{ width: '100%', mt: 1 }}>
                <RadioGroup
                  value={primarySite}
                  onChange={(e) => setPrimarySite(e.target.value)}
                >
                  {availableSites.map((site, index) => (
                    <Card 
                      key={index} 
                      variant="outlined" 
                      sx={{ 
                        mb: 1.5, 
                        borderColor: primarySite === site.url ? '#22c55e' : '#e2e8f0',
                        bgcolor: primarySite === site.url ? '#f0fdf4' : '#ffffff',
                        transition: 'all 0.2s',
                        '&:hover': { borderColor: '#22c55e' }
                      }}
                    >
                      <CardContent sx={{ p: '12px !important', '&:last-child': { pb: '12px !important' } }}>
                        <FormControlLabel
                          value={site.url}
                          control={<Radio size="small" sx={{ color: primarySite === site.url ? '#22c55e' : undefined, '&.Mui-checked': { color: '#22c55e' } }} />}
                          label={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                              <Typography variant="body2" sx={{ fontWeight: 600, color: '#334155' }}>
                                {site.url ? site.url.replace(/^https?:\/\//, '') : 'No URL'}
                              </Typography>
                              <Chip 
                                label={site.source} 
                                size="small" 
                                sx={{ 
                                  height: 20, 
                                  fontSize: '0.65rem', 
                                  fontWeight: 600,
                                  bgcolor: site.source === 'Wix' ? '#000000' : '#21759b',
                                  color: '#ffffff'
                                }} 
                              />
                            </Box>
                          }
                          sx={{ width: '100%', m: 0 }}
                        />
                      </CardContent>
                    </Card>
                  ))}
                </RadioGroup>
              </FormControl>
            ) : (
              <Alert severity="warning" sx={{ mt: 1, borderRadius: 2 }}>
                No connected websites found. Please connect Wix or WordPress to continue.
              </Alert>
            )}
          </Paper>
        </Box>
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
                platforms={connectedPlatforms.filter(p => ['gsc', 'bing'].includes(p))}
                showSummary={true}
                refreshInterval={connectedPlatforms.some(p => ['gsc', 'bing'].includes(p)) ? 300000 : 0} // 5 minutes, only if connected
                onDataLoaded={(data) => {
                  // Data loaded silently
                }}
                onRefreshReady={(refreshFn) => {
                  // Store refresh function if needed
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