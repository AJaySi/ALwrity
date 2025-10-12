import React, { useState, useEffect } from 'react';
import BusinessDescriptionStep from './BusinessDescriptionStep';
import {
  Box,
  Button,
  TextField,
  Typography,
  Alert,
  CircularProgress,
  Card,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  DialogContentText
} from '@mui/material';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import {
  Analytics as AnalyticsIcon,
  History as HistoryIcon,
  Business as BusinessIcon
} from '@mui/icons-material';

// Extracted components
import { AnalysisResultsDisplay, AnalysisProgressDisplay } from './WebsiteStep/components';

// Extracted utilities
import {
  fixUrlFormat,
  checkExistingAnalysis,
  loadExistingAnalysis,
  performAnalysis,
  fetchLastAnalysis
} from './WebsiteStep/utils';

interface WebsiteStepProps {
  onContinue: (stepData?: any) => void;
  updateHeaderContent: (content: { title: string; description: string }) => void;
  onValidationChange?: (isValid: boolean) => void;
}

interface StyleAnalysis {
  writing_style?: {
    tone: string;
    voice: string;
    complexity: string;
    engagement_level: string;
    brand_personality?: string;
    formality_level?: string;
    emotional_appeal?: string;
  };
  content_characteristics?: {
    sentence_structure: string;
    vocabulary_level: string;
    paragraph_organization: string;
    content_flow: string;
    readability_score?: string;
    content_density?: string;
    visual_elements_usage?: string;
  };
  target_audience?: {
    demographics: string[];
    expertise_level: string;
    industry_focus: string;
    geographic_focus: string;
    psychographic_profile?: string;
    pain_points?: string[];
    motivations?: string[];
  };
  content_type?: {
    primary_type: string;
    secondary_types: string[];
    purpose: string;
    call_to_action: string;
    conversion_focus?: string;
    educational_value?: string;
  };
  brand_analysis?: {
    brand_voice: string;
    brand_values: string[];
    brand_positioning: string;
    competitive_differentiation: string;
    trust_signals: string[];
    authority_indicators: string[];
  };
  content_strategy_insights?: {
    strengths: string[];
    weaknesses: string[];
    opportunities: string[];
    threats: string[];
    recommended_improvements: string[];
    content_gaps: string[];
  };
  recommended_settings?: {
    writing_tone: string;
    target_audience: string;
    content_type: string;
    creativity_level: string;
    geographic_location: string;
    industry_context?: string;
    brand_alignment?: string;
  };
  guidelines?: {
    tone_recommendations: string[];
    structure_guidelines: string[];
    vocabulary_suggestions: string[];
    engagement_tips: string[];
    audience_considerations: string[];
    brand_alignment?: string[];
    seo_optimization?: string[];
    conversion_optimization?: string[];
  };
  best_practices?: string[];
  avoid_elements?: string[];
  content_strategy?: string;
  ai_generation_tips?: string[];
  competitive_advantages?: string[];
  content_calendar_suggestions?: string[];
  style_patterns?: {
    sentence_length: string;
    vocabulary_patterns: string[];
    rhetorical_devices: string[];
    paragraph_structure: string;
    transition_phrases: string[];
  };
  style_consistency?: string;
  unique_elements?: string[];
}

interface AnalysisProgress {
  step: number;
  message: string;
  completed: boolean;
}

interface ExistingAnalysis {
  exists: boolean;
  analysis_date?: string;
  analysis_id?: number;
  summary?: {
    writing_style?: any;
    target_audience?: any;
    content_type?: any;
  };
  error?: string;
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

const WebsiteStep: React.FC<WebsiteStepProps> = ({ onContinue, updateHeaderContent, onValidationChange }) => {
  // Scoped high-contrast theme for Step 2 only
  const scopedTheme = React.useMemo(() => createTheme({
    palette: {
      mode: 'light',
      background: { default: '#ffffff', paper: '#ffffff' },
      text: { primary: '#111827', secondary: '#374151' }
    },
    components: {
      MuiPaper: {
        styleOverrides: {
          root: {
            backgroundColor: '#ffffff !important',
            backgroundImage: 'none !important'
          }
        }
      },
      MuiCard: {
        styleOverrides: {
          root: {
            backgroundColor: '#ffffff !important',
            backgroundImage: 'none !important'
          }
        }
      },
      MuiTypography: {
        styleOverrides: {
          root: {
            color: '#111827 !important',
            WebkitTextFillColor: '#111827'
          }
        }
      },
      MuiTooltip: {
        styleOverrides: {
          tooltip: {
            color: '#111827',
            backgroundColor: '#F9FAFB',
            border: '1px solid #E5E7EB'
          }
        }
      }
    }
  }), []);
  const [website, setWebsite] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<StyleAnalysis | null>(null);
  const [existingAnalysis, setExistingAnalysis] = useState<ExistingAnalysis | null>(null);
  const [showConfirmationDialog, setShowConfirmationDialog] = useState(false);
  const [useAnalysisForGenAI, setUseAnalysisForGenAI] = useState(true);
  const [domainName, setDomainName] = useState<string>('');
  const [hasCheckedExisting, setHasCheckedExisting] = useState(false);
  const [showBusinessForm, setShowBusinessForm] = useState(false);
  const [progress, setProgress] = useState<AnalysisProgress[]>([
    { step: 1, message: 'Validating website URL', completed: false },
    { step: 2, message: 'Crawling website content', completed: false },
    { step: 3, message: 'Extracting content structure', completed: false },
    { step: 4, message: 'Analyzing writing style', completed: false },
    { step: 5, message: 'Identifying content characteristics', completed: false },
    { step: 6, message: 'Determining target audience', completed: false },
    { step: 7, message: 'Generating recommendations', completed: false }
  ]);

  useEffect(() => {
    // Update header content when component mounts
    updateHeaderContent({
      title: 'Analyze Your Website',
      description: 'Let Alwrity analyze your website to understand your brand voice, writing style, and content characteristics. This helps us generate content that matches your existing tone and resonates with your audience.'
    });
  }, [updateHeaderContent]);

  // Notify parent when validation state changes
  useEffect(() => {
    const isValid = !!(website.trim() && analysis);
    console.log('WebsiteStep: Validation check:', { website: website.trim(), analysis: !!analysis, isValid });
    if (onValidationChange) {
      console.log('WebsiteStep: Calling onValidationChange with:', isValid);
      onValidationChange(isValid);
    }
  }, [website, analysis, onValidationChange]);

  useEffect(() => {
    // Prefill from last session analysis on mount
    const loadLastAnalysis = async () => {
      try {
        const result = await fetchLastAnalysis();
        if (result.success) {
          if (result.website) {
            setWebsite(result.website);
          }
          if (result.analysis) {
            setAnalysis(result.analysis);
          }
        }
      } catch (error) {
        // Silently fail - non-critical pre-fill
        console.warn('Could not pre-fill from last analysis (non-critical)');
      }
    };
    loadLastAnalysis();
  }, []);

  // Reset existing analysis check when URL changes significantly
  useEffect(() => {
    if (website.trim()) {
      setHasCheckedExisting(false);
      setExistingAnalysis(null);
      setShowConfirmationDialog(false);
    }
  }, [website]);

  // Check for existing analysis when URL changes
  useEffect(() => {
    if (website.trim() && !hasCheckedExisting) {
      const checkExisting = async () => {
        const fixedUrl = fixUrlFormat(website);
        if (fixedUrl) {
          console.log('WebsiteStep: Checking for existing analysis for URL:', fixedUrl);
          try {
            const result = await checkExistingAnalysis(fixedUrl);
            if (result.exists) {
              console.log('WebsiteStep: Found existing analysis, showing confirmation dialog');
              setExistingAnalysis(result.analysis);
              setShowConfirmationDialog(true);
            }
            setHasCheckedExisting(true);
          } catch (err) {
            // Gracefully handle errors (e.g., 401 during token refresh)
            console.warn('WebsiteStep: Failed to check existing analysis, proceeding with new analysis option', err);
            setHasCheckedExisting(true);
            // Don't show error to user - just allow them to proceed with new analysis
          }
        }
      };
      
      // Debounce the check to avoid too many API calls
      const timeoutId = setTimeout(checkExisting, 1000);
      return () => clearTimeout(timeoutId);
    }
  }, [website, hasCheckedExisting]);

  const handleLoadExisting = async (analysisId: number) => {
    const result = await loadExistingAnalysis(analysisId, website);
    if (result.success) {
      setDomainName(result.domainName || '');
      setAnalysis(result.analysis);
      setSuccess('Loaded previous analysis successfully!');
    }
    return result;
  };

  const handleAnalyze = async () => {
    setError(null);
    setSuccess(null);
    setLoading(true);
    setAnalysis(null);
    
    // Reset progress
    setProgress(prev => prev.map(p => ({ ...p, completed: false })));

    try {
      // Validate and fix URL format
      const fixedUrl = fixUrlFormat(website);
      if (!fixedUrl) {
        setError('Please enter a valid website URL (starting with http:// or https://)');
        setLoading(false);
        return;
      }

      // Check for existing analysis
      const result = await checkExistingAnalysis(fixedUrl);
      if (result.exists && result.analysis) {
        setExistingAnalysis(result.analysis);
        setShowConfirmationDialog(true);
        setLoading(false);
        return;
      }

      // Proceed with new analysis
      const analysisResult = await performAnalysis(fixedUrl, updateProgress);
      if (analysisResult.success) {
        setDomainName(analysisResult.domainName || '');
        setAnalysis(analysisResult.analysis);
        
        // Store in localStorage for Step 3 (Competitor Analysis)
        localStorage.setItem('website_url', fixedUrl);
        localStorage.setItem('website_analysis_data', JSON.stringify(analysisResult.analysis));
        
        if (analysisResult.warning) {
          setSuccess(`Website style analysis completed successfully! Note: ${analysisResult.warning}`);
        } else {
          setSuccess('Website style analysis completed successfully!');
        }
      } else {
        setError(analysisResult.error || 'Analysis failed');
      }
    } catch (err) {
      console.error('Analysis error:', err);
      setError('Failed to analyze website. Please check your internet connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  const updateProgress = (step: number, message: string) => {
    setProgress(prev => prev.map(p => 
      p.step === step ? { ...p, message, completed: true } : p
    ));
  };

  const handleLoadExistingConfirm = async () => {
    if (!existingAnalysis?.analysis_id) {
      setShowConfirmationDialog(false);
      return;
    }

    setLoading(true);
    const result = await handleLoadExisting(existingAnalysis.analysis_id);
    setLoading(false);
    setShowConfirmationDialog(false);

    if (!result?.success || !result.analysis) {
      setError('Failed to load existing analysis. Please try a new analysis.');
      return;
    }

    const fixedUrl = fixUrlFormat(website);
    if (!fixedUrl) {
      setError('Website URL is missing or invalid. Please re-enter the URL.');
      return;
    }

    // Set the loaded analysis data for display
    setDomainName(result.domainName || domainName);
    setAnalysis(result.analysis);
    setSuccess('Previous analysis loaded successfully!');

    // Store in localStorage for Step 3 (Competitor Analysis)
    localStorage.setItem('website_url', fixedUrl);
    localStorage.setItem('website_analysis_data', JSON.stringify(result.analysis));

    // DO NOT call onContinue() here - let user review the analysis first
    // User will click "Continue" button when ready to proceed
  };

  const handleNewAnalysis = async () => {
    setShowConfirmationDialog(false);
    setExistingAnalysis(null);
    if (website) {
      const fixedUrl = fixUrlFormat(website);
      if (fixedUrl) {
        setLoading(true);
        const analysisResult = await performAnalysis(fixedUrl, updateProgress);
        if (analysisResult.success) {
          setDomainName(analysisResult.domainName || '');
          setAnalysis(analysisResult.analysis);
          
          if (analysisResult.warning) {
            setSuccess(`Website style analysis completed successfully! Note: ${analysisResult.warning}`);
          } else {
            setSuccess('Website style analysis completed successfully!');
          }
        } else {
          setError(analysisResult.error || 'Analysis failed');
        }
        setLoading(false);
      }
    }
  };

  const handleContinue = () => {
    setError(null);
    const fixedUrl = fixUrlFormat(website);
    if (!fixedUrl) {
      setError('Please enter a valid website URL (starting with http:// or https://)');
      return;
    }
    
    // Prepare step data for the next step
    const stepData = {
      website: fixedUrl,
      domainName: domainName,
      analysis: analysis,
      useAnalysisForGenAI: useAnalysisForGenAI
    };
    
    // Store in localStorage for Step 3 (Competitor Analysis)
    localStorage.setItem('website_url', fixedUrl);
    localStorage.setItem('website_analysis_data', JSON.stringify(analysis));
    
    onContinue(stepData);
  };

  // Conditional rendering for business description form
  if (showBusinessForm) {
    return (
      <BusinessDescriptionStep
        onBack={() => {
          console.log('⬅️ Going back to website form...');
          setShowBusinessForm(false);
        }}
        onContinue={(businessData: any) => {
          console.log('➡️ Business info completed, proceeding to next step...');
          
          // Prepare step data combining website and business data
          const stepData = {
            website: fixUrlFormat(website),
            domainName: domainName,
            analysis: analysis,
            useAnalysisForGenAI: useAnalysisForGenAI,
            businessData: businessData
          };
          
          // Store in localStorage for Step 3 (Competitor Analysis)
          const fixedUrl = fixUrlFormat(website);
          if (fixedUrl) {
            localStorage.setItem('website_url', fixedUrl);
            localStorage.setItem('website_analysis_data', JSON.stringify(analysis));
          }
          
          onContinue(stepData);
        }}
      />
    );
  }

  return (
    <ThemeProvider theme={scopedTheme}>
    <Box sx={{ 
      maxWidth: '100%',
      width: '100%',
      mx: 0,
      p: 3,
      '@keyframes fadeIn': {
        '0%': { opacity: 0, transform: 'translateY(20px)' },
        '100%': { opacity: 1, transform: 'translateY(0)' }
      }
    }}>
      {/* Enhanced Explanatory Text */}
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary" sx={{ 
          mb: 3, 
          lineHeight: 1.6, 
          maxWidth: 800, 
          mx: 'auto',
          fontWeight: 500,
          opacity: 0.8
        }}>
          Provide your website URL to enable comprehensive content analysis and style detection. 
          We'll analyze your content to understand your writing style, target audience, and provide personalized recommendations for better content creation.
        </Typography>
      </Box>

      {/* API Key Configuration Notice removed per request */}

      <Card sx={{ mb: 3, p: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={8}>
            <TextField
              label="Website URL"
              value={website}
              onChange={e => setWebsite(e.target.value)}
              fullWidth
              placeholder="https://yourwebsite.com"
              disabled={loading}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <Button
              variant="contained"
              color="primary"
              onClick={handleAnalyze}
              disabled={!website || loading}
              fullWidth
              startIcon={loading ? <CircularProgress size={20} /> : <AnalyticsIcon />}
            >
              {loading ? 'Analyzing...' : 'Analyze Content Style'}
            </Button>
          </Grid>
        </Grid>
      </Card>

      {/* No Website Button */}
      <Box sx={{ mt: 2, textAlign: 'center', mb: 3 }}>
        <Button
          variant="outlined"
          color="secondary"
          onClick={() => {
            console.log('🔄 Switching to business description form...');
            setShowBusinessForm(true);
          }}
          startIcon={<BusinessIcon />}
          disabled={loading}
        >
          Don't have a website?
        </Button>
      </Box>

      <AnalysisProgressDisplay loading={loading} progress={progress} />

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 3 }}>
          {success}
        </Alert>
      )}

      {analysis && (
        <Box sx={{ animation: 'fadeIn 0.8s ease-in' }}>
          <AnalysisResultsDisplay
            analysis={analysis}
            domainName={domainName}
            useAnalysisForGenAI={useAnalysisForGenAI}
            onUseAnalysisChange={setUseAnalysisForGenAI}
          />
        </Box>
      )}

      {/* Confirmation Dialog for Existing Analysis */}
      <Dialog
        open={showConfirmationDialog}
        onClose={() => setShowConfirmationDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={1}>
            <HistoryIcon color="primary" />
            Previous Analysis Found
          </Box>
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            We found a previous analysis for this website from{' '}
            {existingAnalysis?.analysis_date ? 
              new Date(existingAnalysis.analysis_date).toLocaleDateString() : 
              'a previous session'
            }.
          </DialogContentText>
          <DialogContentText sx={{ mt: 2 }}>
            Would you like to load the previous analysis or perform a new one?
          </DialogContentText>
          {existingAnalysis?.summary && (
            <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
              <Typography variant="subtitle2" gutterBottom>
                Previous Analysis Summary:
              </Typography>
              {existingAnalysis.summary.writing_style?.tone && (
                <Typography variant="body2" color="textSecondary">
                  Tone: {existingAnalysis.summary.writing_style.tone}
                </Typography>
              )}
              {existingAnalysis.summary.target_audience?.expertise_level && (
                <Typography variant="body2" color="textSecondary">
                  Target Audience: {existingAnalysis.summary.target_audience.expertise_level}
                </Typography>
              )}
              {existingAnalysis.summary.content_type?.primary_type && (
                <Typography variant="body2" color="textSecondary">
                  Content Type: {existingAnalysis.summary.content_type.primary_type}
                </Typography>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowConfirmationDialog(false)}>
            Cancel
          </Button>
          <Button onClick={handleLoadExistingConfirm} variant="outlined" startIcon={<HistoryIcon />}>
            Load Previous
          </Button>
          <Button onClick={handleNewAnalysis} variant="contained" startIcon={<AnalyticsIcon />}>
            New Analysis
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
    </ThemeProvider>
  );
};

export default WebsiteStep;
