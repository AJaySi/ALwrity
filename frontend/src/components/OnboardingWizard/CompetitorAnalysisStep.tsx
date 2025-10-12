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
  DialogContent
} from '@mui/material';
import {
  Assessment as AssessmentIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { aiApiClient } from '../../api/client';  // Use aiApiClient for long-running operations
import { useOnboardingStyles } from './common/useOnboardingStyles';
import { SocialMediaPresenceSection, CompetitorsGrid, SitemapAnalysisResults } from './WebsiteStep/components';
import type { Competitor } from './WebsiteStep/components';
import { ComingSoonSection } from './CompetitorAnalysisStep/ComingSoonSection';


interface ResearchSummary {
  total_competitors: number;
  market_insights: string;
  key_findings: string[];
}

interface CompetitorAnalysisStepProps {
  onContinue: (researchData?: any) => void;
  onBack: () => void;
  // sessionId removed - backend uses authenticated user from Clerk token
  userUrl: string;
  industryContext?: string;
  // Expose data collection function for global Continue button
  onDataReady?: (getData: () => any) => void;
}

const CompetitorAnalysisStep: React.FC<CompetitorAnalysisStepProps> = ({
  onContinue,
  onBack,
  userUrl,
  industryContext,
  onDataReady
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

  // Check for cached competitor analysis data
  const loadCachedAnalysis = useCallback(() => {
    try {
      const cachedData = localStorage.getItem('competitor_analysis_data');
      const cachedUrl = localStorage.getItem('competitor_analysis_url');
      const cacheTimestamp = localStorage.getItem('competitor_analysis_timestamp');
      
      // Get current URL for comparison
      const finalUserUrl = userUrl || localStorage.getItem('website_url') || '';
      
      if (cachedData && cachedUrl === finalUserUrl && cacheTimestamp) {
        const cacheAge = Date.now() - parseInt(cacheTimestamp);
        const cacheValidDuration = 24 * 60 * 60 * 1000; // 24 hours
        
        // Check if cache is still valid (less than 24 hours old)
        if (cacheAge < cacheValidDuration) {
          const parsedData = JSON.parse(cachedData);
          
          console.log('CompetitorAnalysisStep: Loading cached competitor analysis:', {
            url: cachedUrl,
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

  // Sitemap Analysis Function
  const startSitemapAnalysis = useCallback(async () => {
    if (isAnalyzingSitemap) return;
    
    setIsAnalyzingSitemap(true);
    
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
      // Try to load from cache first
      const cacheLoaded = loadCachedAnalysis();
      
      // If no cache found, run fresh analysis
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
    return {
      competitors,
      researchSummary,
      sitemapAnalysis,
      userUrl,
      industryContext,
      analysisTimestamp: new Date().toISOString()
    };
  }, [competitors, researchSummary, sitemapAnalysis, userUrl, industryContext]);


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

  return (
    <Box sx={classes.container}>
      <Box sx={classes.header}>
        <Typography 
          variant="h4" 
          sx={{ 
            fontWeight: 600, 
            mb: 2,
            color: '#1a202c !important' // Force dark text for readability
          }}
        >
          Research Your Competition
        </Typography>
        <Typography 
          variant="h6" 
          sx={{ 
            color: '#4a5568 !important', // Force dark secondary text
            fontWeight: 400 
          }}
        >
          Discover your competitors and analyze their strategies to gain competitive advantage
        </Typography>
      </Box>

      {usingCachedData && !error && (
        <Alert 
          severity="info" 
          sx={{ 
            mb: 3,
            background: 'linear-gradient(135deg, #e0f2fe 0%, #b3e5fc 100%)',
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
            sx={{ ml: 2 }}
            size="small"
          >
            Run Fresh Analysis
          </Button>
        </Alert>
      )}

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
              <Typography variant="h6" gutterBottom fontWeight={600} color="primary">
                <AssessmentIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Research Summary
              </Typography>
              
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
                  <Typography 
                    variant="body1" 
                    sx={{ color: '#2d3748 !important' }} // Force dark text for readability
                  >
                    {researchSummary.market_insights}
                  </Typography>
                </Grid>
              </Grid>
            </Paper>
          )}

          {/* Social Media Accounts Section */}
          <SocialMediaPresenceSection socialMediaAccounts={socialMediaAccounts} />

          {/* Competitors Grid Section */}
          <CompetitorsGrid 
            competitors={competitors}
            onShowHighlights={handleShowHighlights}
          />

          {/* Sitemap Analysis Section */}
          {(sitemapAnalysis || isAnalyzingSitemap) && (
            <>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography 
                  variant="h5" 
                  fontWeight={600}
                  sx={{ color: '#1a202c !important' }}
                >
                  Website Structure Analysis
                </Typography>
                {!isAnalyzingSitemap && (
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={startSitemapAnalysis}
                    sx={{ 
                      borderColor: '#667eea',
                      color: '#667eea',
                      '&:hover': {
                        borderColor: '#5a6fd8',
                        backgroundColor: 'rgba(102, 126, 234, 0.04)'
                      }
                    }}
                  >
                    Re-analyze Structure
                  </Button>
                )}
              </Box>
              <SitemapAnalysisResults
                analysisData={sitemapAnalysis?.analysis_data || {}}
                userUrl={userUrl || localStorage.getItem('website_url') || ''}
                sitemapUrl={sitemapAnalysis?.sitemap_url || `${(userUrl || localStorage.getItem('website_url') || '').replace(/\/$/, '')}/sitemap.xml`}
                isLoading={isAnalyzingSitemap}
                discoveryMethod={sitemapAnalysis?.discovery_method}
              />
            </>
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
      <ComingSoonSection />
    </Box>
  );
};

export default CompetitorAnalysisStep;
