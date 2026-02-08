import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Button,
  Grid,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Chip,
  Tooltip,
  IconButton,
  Collapse
} from '@mui/material';
import {
  Assessment as AssessmentIcon,
  Refresh as RefreshIcon,
  ExpandMore as ExpandMoreIcon,
  Info as InfoIcon,
  Lightbulb as LightbulbIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  Search as SearchIcon,
  AutoAwesome as AutoFixHighIcon,
  ExpandLess as ExpandLessIcon
} from '@mui/icons-material';
import { aiApiClient, longRunningApiClient } from '../../api/client';  // Use aiApiClient for long-running operations
import { useOnboardingStyles } from './common/useOnboardingStyles';
import { SocialMediaPresenceSection, CompetitorsGrid } from './WebsiteStep/components';
import type { Competitor } from './WebsiteStep/components';
import { ComingSoonSection } from './CompetitorAnalysisStep/ComingSoonSection';

// Light theme constants matching requirements
const lightTheme = {
  surface: '#FFFFFF',
  text: '#0B1220',
  textSecondary: '#4B5563',
  border: '#E5E7EB',
  inputBg: '#FFFFFF',
  inputText: '#0B1220',
  placeholder: '#6B7280',
  primary: '#6C5CE7',
  primaryContrast: '#FFFFFF',
  shadowSm: '0 1px 2px rgba(16,24,40,0.06)',
  shadowMd: '0 4px 10px rgba(16,24,40,0.08)',
  radiusLg: '20px'
};

interface ResearchSummary {
  total_competitors: number;
  market_insights: string;
  key_findings: string[];
}

interface CompetitorAnalysisStepProps {
  onContinue: (researchData?: any) => void;
  onBack: () => void;
  userUrl: string;
  industryContext?: string;
  // Expose data collection function for global Continue button
  onDataReady?: (getData: () => any) => void;
  initialData?: any;
}

const CompetitorAnalysisStep: React.FC<CompetitorAnalysisStepProps> = ({
  onContinue,
  onBack,
  userUrl,
  industryContext,
  onDataReady,
  initialData
}) => {
  const classes = useOnboardingStyles();
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [analysisStep, setAnalysisStep] = useState('');
  const [competitors, setCompetitors] = useState<Competitor[]>([]);
  const [socialMediaAccounts, setSocialMediaAccounts] = useState<any>({});
  const [, setSocialMediaCitations] = useState<any[]>([]);
  const [researchSummary, setResearchSummary] = useState<ResearchSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showProgressModal, setShowProgressModal] = useState(false);
  const [showHighlightsModal, setShowHighlightsModal] = useState(false);
  const [selectedCompetitorHighlights, setSelectedCompetitorHighlights] = useState<string[]>([]);
  const [selectedCompetitorTitle, setSelectedCompetitorTitle] = useState<string>('');
  const [usingCachedData, setUsingCachedData] = useState(false);
  const [sitemapAnalysis, setSitemapAnalysis] = useState<any>(null);
  const [isAnalyzingSitemap, setIsAnalyzingSitemap] = useState(false);
  const [isDiscoveringSocial, setIsDiscoveringSocial] = useState(false);
  const [showHeaderInfo, setShowHeaderInfo] = useState(false);
  const [showWhyImportant, setShowWhyImportant] = useState(false);
  const [missingData, setMissingData] = useState(false);

  // Ref to track if initialization has already started to prevent duplicate calls
  const initializationStarted = React.useRef(false);

  // Check for missing data
  useEffect(() => {
    // Wait a bit to ensure Wizard has finished initializing its stepData
    const timer = setTimeout(() => {
      const propUserUrl = userUrl || '';
      const localStorageUrl = localStorage.getItem('website_url') || '';
      const sessionStorageUrl = sessionStorage.getItem('website_url') || '';
      const onboardingContextUrl = (window as any).onboardingContext?.websiteUrl || '';
      
      // Also check initialData if available
      const initialDataUrl = initialData?.website || initialData?.website_url || '';
      
      const finalUserUrl = propUserUrl || localStorageUrl || sessionStorageUrl || onboardingContextUrl || initialDataUrl || '';
      
      if (!finalUserUrl) {
        console.warn('CompetitorAnalysisStep: No website URL found (prop, local, session, context, or initialData).');
        setMissingData(true);
      } else {
        console.log('CompetitorAnalysisStep: Valid website URL found:', finalUserUrl);
        setMissingData(false);
        // Ensure website_url is in localStorage for other parts of the step to use
        if (!localStorage.getItem('website_url')) {
          localStorage.setItem('website_url', finalUserUrl);
        }
      }
    }, 1000); // Increased timeout to 1s to allow for slower data loading
    
    return () => clearTimeout(timer);
  }, [userUrl, initialData]);


  // Check for cached competitor analysis data
  const loadCachedAnalysis = useCallback(() => {
    try {
      const cachedData = localStorage.getItem('competitor_analysis_data');
      const cachedUrl = localStorage.getItem('competitor_analysis_url') || '';
      const cacheTimestamp = localStorage.getItem('competitor_analysis_timestamp');
      
      // Get current URL for comparison
      const finalUserUrl = userUrl || localStorage.getItem('website_url') || '';
      
      // Helper to normalize URL for comparison (ignore trailing slashes and protocol differences)
      const normalizeUrl = (url: string) => {
        if (!url) return '';
        return url.trim().toLowerCase().replace(/\/$/, '').replace(/^https?:\/\//, '').replace(/^www\./, '');
      };

      if (cachedData && normalizeUrl(cachedUrl) === normalizeUrl(finalUserUrl) && cacheTimestamp) {
        const cacheAge = Date.now() - parseInt(cacheTimestamp);
        const cacheValidDuration = 24 * 60 * 60 * 1000; // 24 hours
        
        // Check if cache is still valid (less than 24 hours old)
        if (cacheAge < cacheValidDuration) {
          const parsedData = JSON.parse(cachedData);
          
          console.log('CompetitorAnalysisStep: Loading cached competitor analysis:', {
            url: cachedUrl,
            currentUrl: finalUserUrl,
            match: 'normalized',
            cacheAge: Math.round(cacheAge / (60 * 1000)),
            competitors: parsedData.competitors?.length || 0
          });
          
          setCompetitors(parsedData.competitors || []);
          setSocialMediaAccounts(parsedData.social_media_accounts || {});
          setSocialMediaCitations(parsedData.social_media_citations || []);
          setResearchSummary(parsedData.research_summary || null);
          setSitemapAnalysis(parsedData.sitemap_analysis || null);
          setUsingCachedData(true);
          
          return true; // Successfully loaded from cache
        } else {
          console.log('CompetitorAnalysisStep: Cache expired, will run fresh analysis');
        }
      } else {
        console.log('CompetitorAnalysisStep: Cache miss or URL mismatch', {
            cachedUrl,
            finalUserUrl,
            hasData: !!cachedData,
            hasTimestamp: !!cacheTimestamp
        });
      }
      
      return false; // No valid cache found
    } catch (err) {
      console.error('Error loading cached analysis:', err);
      return false;
    }
  }, [userUrl]);

  // Update cache with sitemap analysis
  const updateCacheWithSitemapAnalysis = useCallback((sitemapResult: any) => {
    try {
      const cachedData = localStorage.getItem('competitor_analysis_data');
      if (cachedData) {
        const parsedData = JSON.parse(cachedData);
        parsedData.sitemap_analysis = sitemapResult;
        
        localStorage.setItem('competitor_analysis_data', JSON.stringify(parsedData));
        console.log('CompetitorAnalysisStep: Updated cache with sitemap analysis');
      }
    } catch (err) {
      console.warn('Failed to update cache with sitemap analysis:', err);
    }
  }, []);

  const startCompetitorDiscovery = useCallback(async (force = false) => {
    // Check cache first unless forced
    if (!force && loadCachedAnalysis()) {
      console.log('CompetitorAnalysisStep: Using cached competitor analysis');
      return;
    }

    setIsAnalyzing(true);
    setShowProgressModal(true);
    setError(null);
    setAnalysisProgress(0);
    setAnalysisStep('Initializing competitor discovery...');
    setUsingCachedData(false);

    try {
      setAnalysisStep('Validating session...');
      setAnalysisProgress(20);
      await new Promise(resolve => setTimeout(resolve, 500));

      setAnalysisStep('Discovering competitors using AI...');
      setAnalysisProgress(40);
      await new Promise(resolve => setTimeout(resolve, 1000));

      setAnalysisStep('Analyzing competitor content and strategy...');
      setAnalysisProgress(60);
      await new Promise(resolve => setTimeout(resolve, 1500));

      setAnalysisStep('Generating competitive insights...');
      setAnalysisProgress(80);
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Get website URL from multiple sources with better fallbacks
      const propUserUrl = userUrl || '';
      const localStorageUrl = localStorage.getItem('website_url') || '';
      const sessionStorageUrl = sessionStorage.getItem('website_url') || '';
      
      // Try to get from onboarding context or global state
      const onboardingContextUrl = (window as any).onboardingContext?.websiteUrl || '';
      
      const finalUserUrl = propUserUrl || localStorageUrl || sessionStorageUrl || onboardingContextUrl || '';
      
      // Get website analysis data from multiple sources
      const localStorageAnalysis = localStorage.getItem('website_analysis_data');
      const sessionStorageAnalysis = sessionStorage.getItem('website_analysis_data');
      
      let websiteAnalysisData = null;
      if (localStorageAnalysis) {
        try {
          websiteAnalysisData = JSON.parse(localStorageAnalysis);
        } catch (e) {
          console.warn('Failed to parse localStorage website_analysis_data:', e);
        }
      }
      if (!websiteAnalysisData && sessionStorageAnalysis) {
        try {
          websiteAnalysisData = JSON.parse(sessionStorageAnalysis);
        } catch (e) {
          console.warn('Failed to parse sessionStorage website_analysis_data:', e);
        }
      }
      
      console.log('CompetitorAnalysisStep: URL sources debug:', {
        propUserUrl,
        localStorageUrl,
        sessionStorageUrl,
        onboardingContextUrl,
        finalUserUrl,
        hasLocalStorageAnalysis: !!localStorageAnalysis,
        hasSessionStorageAnalysis: !!sessionStorageAnalysis,
        websiteAnalysisData: websiteAnalysisData ? 'present' : 'null'
      });

      console.log('CompetitorAnalysisStep: Making request with data:', {
        user_url: finalUserUrl,
        industry_context: industryContext,
        num_results: 25,
        website_analysis_data: websiteAnalysisData
      });

      // Validate that we have a URL before making the request
      if (!finalUserUrl || finalUserUrl.trim() === '') {
        throw new Error('No website URL available for competitor analysis. Please complete Step 2 (Website Analysis) first.');
      }

      const response = await aiApiClient.post('/api/onboarding/step3/discover-competitors', {
        // session_id removed - backend gets user from auth token
        user_url: finalUserUrl,
        industry_context: industryContext,
        num_results: 25,
        website_analysis_data: websiteAnalysisData
      });

      const result = response.data;

      if (result.success) {
        setAnalysisStep('Finalizing analysis...');
        setAnalysisProgress(100);
        await new Promise(resolve => setTimeout(resolve, 500));

        const analysisData = {
          competitors: result.competitors || [],
          social_media_accounts: result.social_media_accounts || {},
          social_media_citations: result.social_media_citations || [],
          research_summary: result.research_summary || null,
          sitemap_analysis: null // Will be updated when sitemap analysis completes
        };

        setCompetitors(analysisData.competitors);
        setSocialMediaAccounts(analysisData.social_media_accounts);
        setSocialMediaCitations(analysisData.social_media_citations);
        setResearchSummary(analysisData.research_summary);
        
        // Cache the analysis results
        try {
          localStorage.setItem('competitor_analysis_data', JSON.stringify(analysisData));
          localStorage.setItem('competitor_analysis_url', finalUserUrl);
          localStorage.setItem('competitor_analysis_timestamp', Date.now().toString());
          console.log('CompetitorAnalysisStep: Cached competitor analysis for future use');
        } catch (cacheErr) {
          console.warn('Failed to cache competitor analysis:', cacheErr);
        }
        
        setShowProgressModal(false);
        setIsAnalyzing(false);
      } else {
        throw new Error(result.error || 'Competitor discovery failed');
      }
    } catch (err) {
      console.error('Competitor discovery error:', err);
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
      setIsAnalyzing(false);
      setShowProgressModal(false);
    }
  }, [userUrl, industryContext, loadCachedAnalysis]);  // sessionId removed from dependencies

  // Social Media Discovery Function
  const discoverSocialMedia = useCallback(async () => {
    if (isDiscoveringSocial) return;
    
    setIsDiscoveringSocial(true);
    try {
      const finalUserUrl = userUrl || localStorage.getItem('website_url') || '';
      console.log('Starting targeted social media discovery for:', finalUserUrl);
      
      const response = await aiApiClient.post('/api/onboarding/step3/discover-social-media', {
        user_url: finalUserUrl
      });
      
      const result = response.data;
      
      if (result.success) {
        console.log('Social media discovery completed:', result.social_media_accounts);
        const newAccounts = result.social_media_accounts || {};
        
        // Check if we found any valid accounts
        // We cast to any because values might be empty strings
        const hasNewAccounts = Object.values(newAccounts).some((val: any) => val && val.length > 0);
        const hasExistingAccounts = Object.values(socialMediaAccounts).some((val: any) => val && val.length > 0);

        // Only update if we found something, or if we had nothing to begin with.
        // This prevents "vanishing" profiles if a re-discovery returns a false negative/empty result.
        if (hasNewAccounts || !hasExistingAccounts) {
            setSocialMediaAccounts(newAccounts);
            
            // Update cache
            try {
                const cachedData = localStorage.getItem('competitor_analysis_data');
                if (cachedData) {
                    const parsedData = JSON.parse(cachedData);
                    parsedData.social_media_accounts = newAccounts;
                    localStorage.setItem('competitor_analysis_data', JSON.stringify(parsedData));
                }
            } catch (e) {
                console.warn('Failed to update cache for social accounts', e);
            }
        } else {
            console.warn('Re-discovery returned no accounts. Keeping existing ones to prevent vanishing.');
        }
      } else {
        console.error('Social media discovery failed:', result.error);
        setError(result.error || 'Social media discovery failed');
      }
    } catch (err) {
      console.error('Social media discovery error:', err);
      setError(err instanceof Error ? err.message : 'Social media discovery failed');
    } finally {
      setIsDiscoveringSocial(false);
    }
  }, [userUrl, isDiscoveringSocial]);

  // Sitemap Analysis Function
  const startSitemapAnalysis = useCallback(async (force = false) => {
    if (isAnalyzingSitemap) return;
    
    setIsAnalyzingSitemap(true);
    if (force) {
        setSitemapAnalysis(null); // Clear existing data to show loading state
    }
    
    try {
      const finalUserUrl = userUrl || localStorage.getItem('website_url') || '';
      const competitorDomains = competitors.map(c => c.domain).filter(Boolean);
      
      console.log('Starting sitemap analysis for:', finalUserUrl);
      
      const response = await aiApiClient.post('/api/onboarding/step3/analyze-sitemap', {
        user_url: finalUserUrl,
        competitors: competitorDomains,
        industry_context: industryContext,
        analyze_content_trends: true,
        analyze_publishing_patterns: true
      });
      
      const result = response.data;
      
      if (result.success) {
        console.log('Sitemap analysis completed successfully');
        setSitemapAnalysis(result);
        
        // Update cache with sitemap analysis
        updateCacheWithSitemapAnalysis(result);
      } else {
        console.error('Sitemap analysis failed:', result.error);
        setError(result.error || 'Sitemap analysis failed');
      }
    } catch (err) {
      console.error('Sitemap analysis error:', err);
      setError(err instanceof Error ? err.message : 'Sitemap analysis failed');
    } finally {
      setIsAnalyzingSitemap(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userUrl, competitors, industryContext, isAnalyzingSitemap]);

  // Initialize: Check cache first, then run analysis if needed
  useEffect(() => {
    const initialize = async () => {
      // Prevent double-initialization (React Strict Mode or rapid remounts)
      if (initializationStarted.current) {
        console.log('CompetitorAnalysisStep: Initialization already started, skipping duplicate run');
        return;
      }
      initializationStarted.current = true;

      // 1. Check for backend data (SSOT)
      if (initialData && (initialData.competitors?.length > 0 || initialData.social_media_accounts)) {
        console.log('CompetitorAnalysisStep: Initializing from backend data');
        if (initialData.competitors) setCompetitors(initialData.competitors);
        if (initialData.social_media_accounts) setSocialMediaAccounts(initialData.social_media_accounts);
        if (initialData.social_media_citations) setSocialMediaCitations(initialData.social_media_citations);
        if (initialData.researchSummary) setResearchSummary(initialData.researchSummary);
        if (initialData.sitemapAnalysis) setSitemapAnalysis(initialData.sitemapAnalysis);
        setUsingCachedData(true);
        
        // Prime local cache for consistency
        try {
          const analysisData = {
            competitors: initialData.competitors || [],
            social_media_accounts: initialData.social_media_accounts || {},
            social_media_citations: initialData.social_media_citations || [],
            research_summary: initialData.researchSummary || null,
            sitemap_analysis: initialData.sitemapAnalysis || null
          };
          const finalUserUrl = userUrl || localStorage.getItem('website_url') || '';
          localStorage.setItem('competitor_analysis_data', JSON.stringify(analysisData));
          localStorage.setItem('competitor_analysis_url', finalUserUrl);
          localStorage.setItem('competitor_analysis_timestamp', Date.now().toString());
          console.log('CompetitorAnalysisStep: Primed cache from backend data');
        } catch (e) {
          console.warn('Failed to prime cache from backend data', e);
        }
        return;
      }

      // 2. Try to load from cache
      const cacheLoaded = loadCachedAnalysis();
      
      // 3. If no cache found, run fresh analysis
      if (!cacheLoaded) {
        await startCompetitorDiscovery(false);
      }
    };
    
    initialize();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Run only once on mount

  // Auto-trigger sitemap analysis when competitors are loaded (only if not cached)
  useEffect(() => {
    if (competitors.length > 0 && !sitemapAnalysis && !isAnalyzingSitemap) {
      // Check if sitemap analysis is already cached
      const cachedData = localStorage.getItem('competitor_analysis_data');
      if (cachedData) {
        try {
          const parsedData = JSON.parse(cachedData);
          if (parsedData.sitemap_analysis) {
            console.log('CompetitorAnalysisStep: Sitemap analysis already cached, skipping auto-trigger');
            setSitemapAnalysis(parsedData.sitemap_analysis);
            return;
          }
        } catch (err) {
          console.warn('Error checking cached sitemap analysis:', err);
        }
      }
      
      console.log('Competitors loaded, starting sitemap analysis...');
      startSitemapAnalysis();
    }
  }, [competitors, sitemapAnalysis, isAnalyzingSitemap, startSitemapAnalysis]);

  // Data collection function for global Continue button
  const getResearchData = useCallback(() => {
    // Auto-schedule sitemap benchmark if proceeding to next step
    // We fire-and-forget this call to ensure it runs in background
    const validCompetitors = competitors
        .filter(c => c.url && (c.url.startsWith('http') || c.url.startsWith('https')))
        .map(c => c.url);

    longRunningApiClient.post('/api/seo/competitive-sitemap-benchmarking/run', { 
      max_competitors: 5,
      competitors: validCompetitors.slice(0, 5)
    })
      .then(() => console.log('CompetitorAnalysisStep: Auto-scheduled sitemap benchmark'))
      .catch(err => console.warn('CompetitorAnalysisStep: Failed to auto-schedule benchmark (may be running)', err));

    return {
      competitors,
      social_media_accounts: socialMediaAccounts,
      researchSummary,
      sitemapAnalysis,
      userUrl,
      industryContext,
      analysisTimestamp: new Date().toISOString()
    };
  }, [competitors, socialMediaAccounts, researchSummary, sitemapAnalysis, userUrl, industryContext]);


  // Expose data collection function to parent (only when onDataReady changes)
  useEffect(() => {
    if (onDataReady) {
      console.log('CompetitorAnalysisStep: Exposing data collection function to parent');
      // Always provide a data collection function, even if data is empty
      const safeGetData = () => {
        console.log('CompetitorAnalysisStep: getResearchData called');
        return getResearchData();
      };
      onDataReady(safeGetData);
    }
  }, [onDataReady, getResearchData]); // Include getResearchData in dependencies

  const handleShowHighlights = (competitor: Competitor) => {
    setSelectedCompetitorHighlights(competitor.highlights || []);
    setSelectedCompetitorTitle(competitor.title);
    setShowHighlightsModal(true);
  };

  // Handlers for interactive features
  const handleUpdateSocialAccounts = (newAccounts: { [key: string]: string }) => {
    setSocialMediaAccounts(newAccounts);
    // Update cache
    try {
        const cachedData = localStorage.getItem('competitor_analysis_data');
        if (cachedData) {
            const parsedData = JSON.parse(cachedData);
            parsedData.social_media_accounts = newAccounts;
            localStorage.setItem('competitor_analysis_data', JSON.stringify(parsedData));
        }
    } catch (e) {
        console.warn('Failed to update cache for social accounts', e);
    }
  };

  const handleRemoveCompetitor = (index: number) => {
    const newCompetitors = [...competitors];
    newCompetitors.splice(index, 1);
    setCompetitors(newCompetitors);
     // Update cache
     try {
        const cachedData = localStorage.getItem('competitor_analysis_data');
        if (cachedData) {
            const parsedData = JSON.parse(cachedData);
            parsedData.competitors = newCompetitors;
            localStorage.setItem('competitor_analysis_data', JSON.stringify(parsedData));
        }
    } catch (e) {
        console.warn('Failed to update cache for competitors', e);
    }
  };

  const handleAddCompetitor = (competitor: Competitor) => {
    const newCompetitors = [...competitors, competitor];
    setCompetitors(newCompetitors);
    // Update cache
    try {
        const cachedData = localStorage.getItem('competitor_analysis_data');
        if (cachedData) {
            const parsedData = JSON.parse(cachedData);
            parsedData.competitors = newCompetitors;
            localStorage.setItem('competitor_analysis_data', JSON.stringify(parsedData));
        }
    } catch (e) {
        console.warn('Failed to update cache for competitors', e);
    }
  };

  if (missingData) {
    return (
      <Box sx={{ p: 4, textAlign: 'center', mt: 8 }}>
        <Typography variant="h5" color="error" gutterBottom>
          Missing Website URL
        </Typography>
        <Typography variant="body1" sx={{ mb: 3 }}>
          We couldn't find the website URL to analyze. This might happen if the page was refreshed and session data was lost.
        </Typography>
        <Button variant="contained" onClick={onBack}>
          Return to Website Step
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={classes.container}>
      {/* Educational Header */}
      <Box sx={{ mb: 4, textAlign: 'center', animation: 'fadeIn 0.6s ease-out' }}>
        <Typography variant="h4" sx={{ 
          fontWeight: 700, 
          mb: 2,
          background: 'linear-gradient(45deg, #2563EB 30%, #7C3AED 90%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
        }}>
          Competitive Intelligence
        </Typography>
        
        <Typography variant="body1" color="text.secondary" sx={{ 
          mb: 2, 
          maxWidth: 600, 
          mx: 'auto',
          fontSize: '1.1rem'
        }}>
          Uncover the strategies that are working for your competitors to build your own advantage.
        </Typography>

        <Button 
          size="small" 
          onClick={() => setShowHeaderInfo(!showHeaderInfo)}
          endIcon={showHeaderInfo ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          sx={{ textTransform: 'none', borderRadius: 2 }}
        >
          {showHeaderInfo ? 'Hide details' : 'About this Step'}
        </Button>

        <Collapse in={showHeaderInfo}>
          <Box sx={{ 
            mt: 2, 
            p: 3, 
            bgcolor: lightTheme.surface,
            color: lightTheme.text,
            borderRadius: 3,
            border: `1px solid ${lightTheme.border}`,
            boxShadow: lightTheme.shadowSm,
            maxWidth: 800,
            mx: 'auto',
            textAlign: 'left'
          }}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
                  <Box sx={{ p: 1.5, bgcolor: '#DBEAFE', borderRadius: '50%', mb: 1.5, color: '#2563EB' }}>
                    <SearchIcon />
                  </Box>
                  <Typography variant="subtitle2" fontWeight="bold" gutterBottom>What</Typography>
                  <Typography variant="caption" color="text.secondary">We analyze top competitors in your niche.</Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
                  <Box sx={{ p: 1.5, bgcolor: '#F3E8FF', borderRadius: '50%', mb: 1.5, color: '#7C3AED' }}>
                    <TrendingUpIcon />
                  </Box>
                  <Typography variant="subtitle2" fontWeight="bold" gutterBottom>Why</Typography>
                  <Typography variant="caption" color="text.secondary">To identify content gaps and market positioning.</Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
                  <Box sx={{ p: 1.5, bgcolor: '#DCFCE7', borderRadius: '50%', mb: 1.5, color: '#16A34A' }}>
                    <AutoFixHighIcon />
                  </Box>
                  <Typography variant="subtitle2" fontWeight="bold" gutterBottom>How</Typography>
                  <Typography variant="caption" color="text.secondary">Using AI to scan their public content and social footprint.</Typography>
                </Box>
              </Grid>
            </Grid>
          </Box>
        </Collapse>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
          <Button 
            startIcon={<RefreshIcon />} 
            onClick={() => startCompetitorDiscovery(true)}
            sx={{ ml: 2 }}
          >
            Retry
          </Button>
        </Alert>
      )}

      {!isAnalyzing && !error && (competitors.length > 0 || researchSummary) && (
        <Box>
          {researchSummary && (
            <Paper sx={{ 
              p: 3, 
              mb: 4, 
              background: 'linear-gradient(135deg, #e0f2fe 0%, #b3e5fc 100%)', // Warm sky-blue gradient
              border: '1px solid #81d4fa',
              borderRadius: 2,
              boxShadow: '0 4px 12px rgba(3, 169, 244, 0.15)'
            }}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Tooltip title="This section provides a high-level overview of the competitive landscape, including the total number of competitors found and key market insights derived from AI analysis.">
                    <Typography variant="h6" fontWeight={600} color="primary" sx={{ display: 'flex', alignItems: 'center', cursor: 'help' }}>
                        <AssessmentIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                        Research Summary
                    </Typography>
                </Tooltip>
              </Box>

              {usingCachedData && (
                <Alert 
                  severity="info" 
                  sx={{ 
                    mb: 3,
                    bgcolor: 'rgba(255, 255, 255, 0.6)',
                    backdropFilter: 'blur(10px)',
                    border: '1px solid #81d4fa',
                    color: '#01579b',
                    '& .MuiAlert-icon': {
                      color: '#0277bd'
                    }
                  }}
                >
                  Loaded previously analyzed competitor data. 
                  <Button 
                    startIcon={<RefreshIcon />} 
                    onClick={() => startCompetitorDiscovery(true)}
                    sx={{ 
                        ml: 2,
                        background: 'linear-gradient(45deg, #2563EB 30%, #7C3AED 90%)',
                        color: 'white',
                        fontWeight: 600,
                        boxShadow: '0 3px 5px 2px rgba(37, 99, 235, .3)',
                        '&:hover': {
                            background: 'linear-gradient(45deg, #1d4ed8 30%, #6d28d9 90%)',
                        }
                    }}
                    size="small"
                  >
                    Run Fresh Analysis
                  </Button>
                </Alert>
              )}
              
              <Grid container spacing={3} mt={1}>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="h4" color="primary" fontWeight={700}>
                    {researchSummary.total_competitors}
                  </Typography>
                  <Typography 
                    variant="body2" 
                    sx={{ color: '#4a5568 !important' }} // Force dark text for readability
                  >
                    Competitors Found
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={9}>
                  <Typography variant="subtitle1" fontWeight={700} color="text.primary" gutterBottom>
                    Market Insights
                  </Typography>
                  <Typography 
                    variant="body1" 
                    sx={{ color: '#2d3748 !important' }} // Force dark text for readability
                  >
                    {researchSummary.market_insights || "Analysis complete. Review the competitors below to see detailed insights."}
                  </Typography>
                </Grid>
              </Grid>
            </Paper>
          )}

          {/* Social Media Accounts Section */}
          <SocialMediaPresenceSection 
            socialMediaAccounts={socialMediaAccounts} 
            onUpdateAccounts={handleUpdateSocialAccounts}
            onRefresh={discoverSocialMedia}
            isRefreshing={isDiscoveringSocial}
          />

          {/* Competitors Grid Section */}
          <CompetitorsGrid 
            competitors={competitors}
            onShowHighlights={handleShowHighlights}
            onRemoveCompetitor={handleRemoveCompetitor}
            onAddCompetitor={handleAddCompetitor}
          />

          {/* Strategic Opportunities Section (Replaces Sitemap Analysis) */}
          {(sitemapAnalysis || isAnalyzingSitemap) && (
            <Box mt={6} mb={4}>
               <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Tooltip title="Actionable Insights: Based on competitor analysis, these are specific recommendations to improve your SEO. Use 'Content Gaps' to find topics to write about, and 'Growth Areas' to identify low-competition keywords.">
                  <Typography 
                    variant="h5" 
                    fontWeight={600}
                    sx={{ color: '#1a202c !important', display: 'flex', alignItems: 'center', cursor: 'help' }}
                  >
                    Strategic Content Opportunities
                    <InfoIcon sx={{ ml: 1, fontSize: 20, color: 'text.disabled' }} />
                  </Typography>
                </Tooltip>
                <Button
                    variant="outlined"
                    size="small"
                    startIcon={isAnalyzingSitemap ? <CircularProgress size={16} color="inherit" /> : null}
                    onClick={() => startSitemapAnalysis(true)}
                    disabled={isAnalyzingSitemap}
                    sx={{ 
                      borderColor: '#667eea',
                      color: '#667eea',
                      '&:hover': {
                        borderColor: '#5a6fd8',
                        backgroundColor: 'rgba(102, 126, 234, 0.04)'
                      }
                    }}
                  >
                    {isAnalyzingSitemap ? 'Refreshing...' : 'Refresh Strategy'}
                  </Button>
              </Box>

              {isAnalyzingSitemap ? (
                 <Paper sx={{ p: 4, textAlign: 'center', bgcolor: '#f8fafc', borderStyle: 'dashed', borderColor: '#cbd5e0' }}>
                    <CircularProgress size={24} sx={{ mb: 2 }} />
                    <Typography color="text.secondary">Analyzing competitive landscape for opportunities...</Typography>
                 </Paper>
              ) : (
                <Box>
                    {/* Market Positioning & Benchmarks */}
                    {sitemapAnalysis?.analysis_data?.onboarding_insights && (
                        <Grid container spacing={3} mb={3}>
                            <Grid item xs={12}>
                                <Paper sx={{ p: 2, bgcolor: '#f0f9ff', border: '1px solid #bae6fd', display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                                    <Box sx={{ p: 1, bgcolor: 'white', borderRadius: '50%', color: '#0284c7' }}>
                                        <AssessmentIcon />
                                    </Box>
                                    <Box>
                                        <Typography variant="subtitle1" fontWeight={600} color="#0c4a6e" gutterBottom>
                                            Market Positioning
                                        </Typography>
                                        <Typography variant="body2" color="#0c4a6e">
                                            {sitemapAnalysis.analysis_data.onboarding_insights.competitive_positioning}
                                        </Typography>
                                    </Box>
                                </Paper>
                            </Grid>
                        </Grid>
                    )}

                    <Grid container spacing={3}>
                        {/* Content Gaps */}
                    <Grid item xs={12} md={4}>
                        <Card sx={{ height: '100%', bgcolor: '#fff5f5', border: '1px solid #fed7d7' }}>
                            <CardContent>
                                <Typography variant="h6" color="error.main" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                    <WarningIcon fontSize="small" /> Content Gaps
                                </Typography>
                                <Divider sx={{ mb: 2, borderColor: '#feb2b2' }} />
                                <Typography variant="body2" sx={{ mb: 2, color: '#2d3748' }}>
                                    Topics your competitors are covering that you are missing:
                                </Typography>
                                {sitemapAnalysis?.analysis_data?.onboarding_insights?.content_gaps?.length > 0 ? (
                                    <Box display="flex" flexWrap="wrap" gap={1}>
                                        {sitemapAnalysis.analysis_data.onboarding_insights.content_gaps.map((gap: string, i: number) => (
                                            <Chip key={i} label={gap} size="small" color="error" variant="outlined" sx={{ bgcolor: 'white' }} />
                                        ))}
                                    </Box>
                                ) : (
                                    <Typography variant="caption" fontStyle="italic">No specific gaps detected yet.</Typography>
                                )}
                            </CardContent>
                        </Card>
                    </Grid>

                    {/* Growth Opportunities */}
                    <Grid item xs={12} md={4}>
                        <Card sx={{ height: '100%', bgcolor: '#f0fff4', border: '1px solid #c6f6d5' }}>
                            <CardContent>
                                <Typography variant="h6" color="success.main" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                    <TrendingUpIcon fontSize="small" /> Growth Areas
                                </Typography>
                                <Divider sx={{ mb: 2, borderColor: '#9ae6b4' }} />
                                <Typography variant="body2" sx={{ mb: 2, color: '#2d3748' }}>
                                    High-potential areas for organic traffic growth:
                                </Typography>
                                <List dense disablePadding>
                                    {sitemapAnalysis?.analysis_data?.onboarding_insights?.growth_opportunities?.length > 0 ? (
                                        sitemapAnalysis.analysis_data.onboarding_insights.growth_opportunities.slice(0, 4).map((opp: string, i: number) => (
                                            <ListItem key={i} disableGutters sx={{ py: 0.5 }}>
                                                <ListItemIcon sx={{ minWidth: 28 }}>
                                                    <TrendingUpIcon fontSize="small" color="success" sx={{ fontSize: 16 }} />
                                                </ListItemIcon>
                                                <ListItemText primary={opp} primaryTypographyProps={{ variant: 'body2', color: '#2d3748' }} />
                                            </ListItem>
                                        ))
                                    ) : (
                                        <Typography variant="caption" fontStyle="italic">Analysis in progress.</Typography>
                                    )}
                                </List>
                            </CardContent>
                        </Card>
                    </Grid>

                     {/* Strategic Recommendations */}
                     <Grid item xs={12} md={4}>
                        <Card sx={{ height: '100%', bgcolor: '#ebf8ff', border: '1px solid #bee3f8' }}>
                            <CardContent>
                                <Typography variant="h6" color="primary.main" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                    <LightbulbIcon fontSize="small" /> Strategy
                                </Typography>
                                <Divider sx={{ mb: 2, borderColor: '#90cdf4' }} />
                                <Typography variant="body2" sx={{ mb: 2, color: '#2d3748' }}>
                                    Recommended next steps for your content strategy:
                                </Typography>
                                <List dense disablePadding>
                                    {sitemapAnalysis?.analysis_data?.onboarding_insights?.strategic_recommendations?.length > 0 ? (
                                        sitemapAnalysis.analysis_data.onboarding_insights.strategic_recommendations.slice(0, 4).map((rec: string, i: number) => (
                                            <ListItem key={i} disableGutters sx={{ py: 0.5 }}>
                                                <ListItemIcon sx={{ minWidth: 28 }}>
                                                    <InfoIcon fontSize="small" color="primary" sx={{ fontSize: 16 }} />
                                                </ListItemIcon>
                                                <ListItemText primary={rec} primaryTypographyProps={{ variant: 'body2', color: '#2d3748' }} />
                                            </ListItem>
                                        ))
                                    ) : (
                                        <Typography variant="caption" fontStyle="italic">Generating recommendations...</Typography>
                                    )}
                                </List>
                            </CardContent>
                        </Card>
                    </Grid>
                </Grid>

                {/* Industry Benchmarks */}
                {sitemapAnalysis?.analysis_data?.onboarding_insights?.industry_benchmarks?.length > 0 && (
                    <Box mt={3}>
                        <Typography variant="subtitle2" color="text.secondary" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <TrendingUpIcon fontSize="small" /> Industry Benchmarks
                        </Typography>
                        <Grid container spacing={2}>
                            {sitemapAnalysis.analysis_data.onboarding_insights.industry_benchmarks.map((benchmark: string, i: number) => (
                                <Grid item xs={12} sm={6} key={i}>
                                    <Paper variant="outlined" sx={{ p: 1.5, bgcolor: '#f8fafc', display: 'flex', alignItems: 'center', gap: 1.5 }}>
                                        <Box sx={{ width: 6, height: 6, borderRadius: '50%', bgcolor: '#94a3b8' }} />
                                        <Typography variant="body2" color="#334155">
                                            {benchmark}
                                        </Typography>
                                    </Paper>
                                </Grid>
                            ))}
                        </Grid>
                    </Box>
                )}
                </Box>
              )}
            </Box>
          )}

        </Box>
      )}

      <Dialog
        open={showProgressModal}
        onClose={() => {}}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 3,
            p: 3
          }
        }}
      >
        <DialogTitle sx={{ textAlign: 'center', pb: 2 }}>
          <Box display="flex" alignItems="center" justifyContent="center" gap={2}>
            <CircularProgress size={32} color="primary" />
            <Typography variant="h6" fontWeight={600}>
              Analyzing Your Competition
            </Typography>
          </Box>
        </DialogTitle>
        
        <DialogContent sx={{ textAlign: 'center', pt: 2 }}>
          <Typography variant="body1" color="text.secondary" mb={3}>
            We're discovering your competitors and analyzing their strategies using AI...
          </Typography>
          
          <Box mb={3}>
            <LinearProgress 
              variant="determinate" 
              value={analysisProgress} 
              sx={{ 
                height: 8, 
                borderRadius: 4,
                mb: 2
              }} 
            />
            <Typography variant="body2" color="text.secondary">
              {analysisProgress}% Complete
            </Typography>
          </Box>
          
          <Typography variant="body2" color="primary" fontWeight={500}>
            {analysisStep}
          </Typography>
        </DialogContent>
      </Dialog>

      {/* Highlights Modal */}
      <Dialog 
        open={showHighlightsModal} 
        onClose={() => setShowHighlightsModal(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Typography variant="h6" fontWeight={600}>
            Key Highlights - {selectedCompetitorTitle}
          </Typography>
        </DialogTitle>
        <DialogContent>
          {selectedCompetitorHighlights.length > 0 ? (
            <Box>
              {selectedCompetitorHighlights.map((highlight, index) => (
                <Box 
                  key={index} 
                  sx={{ 
                    p: 2, 
                    mb: 2, 
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 1,
                    backgroundColor: 'background.paper'
                  }}
                >
                  <Typography variant="body2" color="text.secondary">
                    {highlight}
                  </Typography>
                </Box>
              ))}
            </Box>
          ) : (
            <Typography variant="body2" color="text.secondary">
              No highlights available for this competitor.
            </Typography>
          )}
        </DialogContent>
      </Dialog>

      {/* Coming Soon Section */}
      <ComingSoonSection missingData={missingData} />
    </Box>
  );
};

export default CompetitorAnalysisStep;
