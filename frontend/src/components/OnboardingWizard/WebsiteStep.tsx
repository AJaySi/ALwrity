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
  DialogContentText,
  Collapse
} from '@mui/material';
import {
  Analytics as AnalyticsIcon,
  History as HistoryIcon,
  Business as BusinessIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Search as SearchIcon,
  Psychology as PsychologyIcon,
  AutoAwesome as AutoFixHighIcon
} from '@mui/icons-material';

// Extracted components
import { AnalysisResultsDisplay, AnalysisProgressDisplay } from './WebsiteStep/components';

// Import API client for saving
import { apiClient } from '../../api/client';

// Extracted utilities
import {
  fixUrlFormat,
  checkExistingAnalysis,
  loadExistingAnalysis,
  performAnalysis,
  fetchLastAnalysis
} from './WebsiteStep/utils';
import { onboardingCache, WebsiteIntakeCache } from '../../services/onboardingCache';

interface WebsiteStepProps {
  onContinue: (stepData?: any) => void;
  updateHeaderContent: (content: { title: string; description: string }) => void;
  onValidationChange?: (isValid: boolean) => void;
}

interface StyleAnalysis {
  id?: number;
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
  patterns?: {
    sentence_length: string;
    vocabulary_patterns: string[];
    rhetorical_devices: string[];
    paragraph_structure: string;
    transition_phrases: string[];
  };
  style_consistency?: string;
  unique_elements?: string[];
  seo_audit?: any;
  sitemap_analysis?: any;
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

const WebsiteStep: React.FC<WebsiteStepProps> = ({ onContinue, updateHeaderContent, onValidationChange }) => {
  const [website, setWebsite] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<StyleAnalysis | null>(null);
  const [crawlResult, setCrawlResult] = useState<any>(null);
  const [existingAnalysis, setExistingAnalysis] = useState<ExistingAnalysis | null>(null);
  const [showConfirmationDialog, setShowConfirmationDialog] = useState(false);
  const [useAnalysisForGenAI, setUseAnalysisForGenAI] = useState(true);
  const [domainName, setDomainName] = useState<string>('');
  const [hasCheckedExisting, setHasCheckedExisting] = useState(false);
  const [showBusinessForm, setShowBusinessForm] = useState(false);
  const [isProgressModalOpen, setIsProgressModalOpen] = useState(false);
  const [progress, setProgress] = useState<AnalysisProgress[]>([
    { step: 1, message: 'Validating URL...', completed: false },
    { step: 2, message: 'Crawling website & Analyzing SEO...', completed: false },
    { step: 3, message: 'Processing content structure...', completed: false },
    { step: 4, message: 'Analyzing brand voice & tone...', completed: false },
    { step: 5, message: 'Generating strategic insights...', completed: false },
    { step: 6, message: 'Finalizing recommendations...', completed: false }
  ]);
  const [showInfo, setShowInfo] = useState(false);

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
            if (result.exists && result.analysis) {
              console.log('WebsiteStep: Found existing analysis, showing confirmation dialog');
              setExistingAnalysis(result.analysis);
              setShowConfirmationDialog(true);
            }
          } catch (err) {
            console.warn('WebsiteStep: Failed to check existing analysis', err);
          } finally {
            setHasCheckedExisting(true);
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
      setCrawlResult(result.crawlResult);
      setSuccess('Loaded previous analysis successfully!');
    }
    return result;
  };

  const handleAnalyze = async () => {
    setError(null);
    setSuccess(null);
    setLoading(true);
    setAnalysis(null);
    setCrawlResult(null);
    
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
      setIsProgressModalOpen(true);
      const analysisResult = await performAnalysis(fixedUrl, updateProgress);
      if (analysisResult.success) {
        setDomainName(analysisResult.domainName || '');
        setAnalysis(analysisResult.analysis);
        setCrawlResult(analysisResult.crawlResult);
        
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
      setTimeout(() => setIsProgressModalOpen(false), 1000);
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

  const saveAnalysis = async (currentAnalysis: StyleAnalysis) => {
    if (!currentAnalysis?.id) {
      console.warn('Cannot save analysis: Missing analysis ID');
      return false;
    }

    try {
      console.log('Saving analysis updates...', currentAnalysis);
      await apiClient.put(`/api/onboarding/style-detection/analysis/${currentAnalysis.id}`, currentAnalysis);
      console.log('Analysis updates saved successfully');
      return true;
    } catch (err) {
      console.error('Failed to save analysis updates:', err);
      return false;
    }
  };

  const handleAnalysisUpdate = (updatedAnalysis: StyleAnalysis) => {
    setAnalysis(updatedAnalysis);
  };

  const handleContinue = async () => {
    setError(null);
    const fixedUrl = fixUrlFormat(website);
    if (!fixedUrl) {
      setError('Please enter a valid website URL (starting with http:// or https://)');
      return;
    }
    
    // Save current analysis state to backend before continuing
    if (analysis && analysis.id) {
      setLoading(true);
      await saveAnalysis(analysis);
      setLoading(false);
    }
    
    // Prepare step data for the next step
    const stepData = {
      website: fixedUrl,
      domainName: domainName,
      analysis: analysis,
      useAnalysisForGenAI: useAnalysisForGenAI
    };

    const cachedIntake = onboardingCache.getStepData(2) as WebsiteIntakeCache | undefined;
    onboardingCache.saveStepData(2, {
      ...cachedIntake,
      website: fixedUrl,
      analysis: analysis,
      hasWebsite: true
    });
  
    // Store in localStorage for Step 3 (Competitor Analysis)
    localStorage.setItem('website_url', fixedUrl);
    localStorage.setItem('website_analysis_data', JSON.stringify(analysis));
  
    onContinue(stepData);
  };

  // Conditional rendering for business description form - now handled inline via toggle
  /*
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

          const cachedIntake = onboardingCache.getStepData(2) as WebsiteIntakeCache | undefined;
          onboardingCache.saveStepData(2, {
            ...cachedIntake,
            website: fixUrlFormat(website),
            analysis: analysis,
            businessInfo: businessData,
            hasWebsite: false
          });
          
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
  */

  return (
    <Box sx={{ 
      maxWidth: '100%',
      width: '100%',
      mx: 0,
      p: 2,
      '@keyframes fadeIn': {
        '0%': { opacity: 0, transform: 'translateY(10px)' },
        '100%': { opacity: 1, transform: 'translateY(0)' }
      }
    }}>
      {/* Educational Header */}
      <Box sx={{ mb: 4, textAlign: 'center', animation: 'fadeIn 0.6s ease-out' }}>
        <Typography variant="h4" sx={{ 
          fontWeight: 700, 
          mb: 2,
          background: 'linear-gradient(45deg, #2563EB 30%, #7C3AED 90%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
        }}>
          Let AI Learn Your Brand Voice
        </Typography>
        
        <Typography variant="body1" color="text.secondary" sx={{ 
          mb: 2, 
          maxWidth: 600, 
          mx: 'auto',
          fontSize: '1.1rem'
        }}>
          Enter your website URL to automatically extract your unique writing style, tone, and audience preferences.
        </Typography>

        <Button 
          size="small" 
          onClick={() => setShowInfo(!showInfo)}
          endIcon={showInfo ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          sx={{ textTransform: 'none', borderRadius: 2 }}
        >
          {showInfo ? 'Hide details' : 'How does this work?'}
        </Button>

        <Collapse in={showInfo}>
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
                  <Typography variant="subtitle2" fontWeight="bold" gutterBottom>1. Scan & Crawl</Typography>
                  <Typography variant="caption" color="text.secondary">We securely analyze your public pages to gather content samples.</Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
                  <Box sx={{ p: 1.5, bgcolor: '#F3E8FF', borderRadius: '50%', mb: 1.5, color: '#7C3AED' }}>
                    <PsychologyIcon />
                  </Box>
                  <Typography variant="subtitle2" fontWeight="bold" gutterBottom>2. AI Analysis</Typography>
                  <Typography variant="caption" color="text.secondary">Our AI identifies your tone, vocabulary, and sentence structure.</Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
                  <Box sx={{ p: 1.5, bgcolor: '#DCFCE7', borderRadius: '50%', mb: 1.5, color: '#16A34A' }}>
                    <AutoFixHighIcon />
                  </Box>
                  <Typography variant="subtitle2" fontWeight="bold" gutterBottom>3. Personalization</Typography>
                  <Typography variant="caption" color="text.secondary">Future content is generated to match your brand's unique voice perfectly.</Typography>
                </Box>
              </Grid>
            </Grid>
          </Box>
        </Collapse>
      </Box>

      {/* Input Section */}
      <Card sx={{ 
        mb: 3, 
        p: 4, 
        bgcolor: lightTheme.surface,
        color: lightTheme.text,
        borderRadius: lightTheme.radiusLg,
        boxShadow: lightTheme.shadowSm,
        border: `1px solid ${lightTheme.border}`,
        position: 'relative',
        overflow: 'visible'
      }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={8}>
            <TextField
              label="Website URL"
              value={website}
              onChange={e => setWebsite(e.target.value)}
              fullWidth
              placeholder="https://yourwebsite.com"
              disabled={loading}
              helperText="We'll only read public pages. No login required."
              InputProps={{
                sx: { 
                  borderRadius: 2,
                  bgcolor: lightTheme.inputBg,
                  color: lightTheme.inputText,
                }
              }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  bgcolor: lightTheme.inputBg,
                  color: lightTheme.inputText,
                  '& fieldset': { borderColor: lightTheme.border },
                  '&:hover fieldset': { borderColor: lightTheme.primary },
                  '&.Mui-focused fieldset': { borderColor: lightTheme.primary }
                },
                '& .MuiInputLabel-root': { color: lightTheme.textSecondary },
                '& .MuiInputLabel-root.Mui-focused': { color: lightTheme.primary },
                '& .MuiFormHelperText-root': { color: lightTheme.textSecondary }
              }}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <Button
              variant="contained"
              onClick={handleAnalyze}
              disabled={!website || loading}
              fullWidth
              size="large"
              startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <AnalyticsIcon />}
              sx={{ 
                borderRadius: '16px',
                py: 1.5,
                bgcolor: lightTheme.primary,
                color: lightTheme.primaryContrast,
                boxShadow: lightTheme.shadowMd,
                transition: 'all 0.3s ease',
                '&:hover': {
                  bgcolor: lightTheme.primary,
                  filter: 'brightness(1.06)',
                  transform: 'translateY(-1px)',
                  boxShadow: '0 8px 25px 0 rgba(37, 99, 235, 0.4)',
                },
                '&:active': {
                  transform: 'translateY(1px)'
                }
              }}
            >
              {loading ? 'Analyzing...' : 'Website Analysis'}
            </Button>
          </Grid>
        </Grid>
      </Card>

      {/* No Website Option */}
      <Box sx={{ mt: 2, textAlign: 'center', mb: 3 }}>
        {!showBusinessForm ? (
          <>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              Don't have a live website yet?
            </Typography>
            <Button
              onClick={() => {
                console.log('🔄 Expanding business description form...');
                setShowBusinessForm(true);
              }}
              startIcon={<BusinessIcon />}
              sx={{ 
                textTransform: 'none', 
                color: 'text.secondary',
                '&:hover': { color: 'primary.main', bgcolor: 'transparent' }
              }}
            >
              Describe your business manually instead
            </Button>
          </>
        ) : (
          <Box sx={{ 
            mt: 2, 
            textAlign: 'left', 
            animation: 'fadeIn 0.5s ease-out'
          }}>
             <BusinessDescriptionStep
                onBack={() => {
                  console.log('⬅️ Collapsing business form...');
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
          </Box>
        )}
      </Box>

      {error && (
        <Alert 
          severity="error" 
          sx={{ mb: 3 }}
          action={
            <Button color="inherit" size="small" onClick={() => setShowBusinessForm(true)}>
              ENTER MANUALLY
            </Button>
          }
        >
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
            crawlResult={crawlResult}
            domainName={domainName}
            useAnalysisForGenAI={useAnalysisForGenAI}
            onUseAnalysisChange={setUseAnalysisForGenAI}
            onAnalysisUpdate={handleAnalysisUpdate}
            onSave={() => saveAnalysis(analysis)}
          />
        </Box>
      )}

      {/* Analysis Progress Modal */}
      <Dialog
        open={isProgressModalOpen}
        maxWidth="sm"
        fullWidth
        disableEscapeKeyDown
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <CircularProgress size={24} />
          Analyzing Your Website...
        </DialogTitle>
        <DialogContent>
          <AnalysisProgressDisplay loading={true} progress={progress} />
        </DialogContent>
      </Dialog>

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
  );
};

export default WebsiteStep;
