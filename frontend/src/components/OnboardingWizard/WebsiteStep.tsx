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
  CardContent,
  Grid,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  LinearProgress,
  Stepper,
  Step,
  StepLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  DialogContentText,
  Chip,
  Divider,
  Checkbox,
  FormControlLabel,
  Paper,
  Fade,
  Slide,
  Zoom,
  Tooltip,
  IconButton
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckIcon,
  Info as InfoIcon,
  Language as LanguageIcon,
  Web as WebIcon,
  Analytics as AnalyticsIcon,
  Psychology as PsychologyIcon,
  TrendingUp as TrendingUpIcon,
  History as HistoryIcon,
  Star as StarIcon,
  Warning as WarningIcon,
  Lightbulb as LightbulbIcon,
  Palette as PaletteIcon,
  Speed as SpeedIcon,
  Group as GroupIcon,
  Business as BusinessIcon,
  LocationOn as LocationIcon,
  AutoAwesome as AutoAwesomeIcon,
  Verified as VerifiedIcon,
  Close as CloseIcon
} from '@mui/icons-material';

interface WebsiteStepProps {
  onContinue: () => void;
  updateHeaderContent: (content: { title: string; description: string }) => void;
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
  // New comprehensive analysis fields
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

const WebsiteStep: React.FC<WebsiteStepProps> = ({ onContinue, updateHeaderContent }) => {
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

  useEffect(() => {
    // Prefill from last session analysis on mount
    const fetchLastAnalysis = async () => {
      try {
        const res = await fetch('/api/style-detection/session-analyses');
        const data = await res.json();
        if (data.success && Array.isArray(data.analyses) && data.analyses.length > 0) {
          // Pick the most recent analysis (assuming sorted by date desc, else sort here)
          const last = data.analyses[0];
          if (last && last.website_url) {
            setWebsite(last.website_url);
          }
          if (last && last.style_analysis) {
            setAnalysis(last.style_analysis);
          }
        }
      } catch (err) {
        console.error('WebsiteStep: Error pre-filling from last analysis', err);
      }
    };
    fetchLastAnalysis();
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
          const hasExisting = await checkExistingAnalysis(fixedUrl);
          if (hasExisting) {
            console.log('WebsiteStep: Found existing analysis, showing confirmation dialog');
            setShowConfirmationDialog(true);
          }
          setHasCheckedExisting(true);
        }
      };
      
      // Debounce the check to avoid too many API calls
      const timeoutId = setTimeout(checkExisting, 1000);
      return () => clearTimeout(timeoutId);
    }
  }, [website, hasCheckedExisting]);

  const checkExistingAnalysis = async (url: string) => {
    try {
      console.log('WebsiteStep: Checking existing analysis for URL:', url);
      const response = await fetch(`/api/onboarding/style-detection/check-existing/${encodeURIComponent(url)}`);
      const result = await response.json();
      
      if (result.exists) {
        console.log('WebsiteStep: Existing analysis found:', result);
        setExistingAnalysis(result);
        return true;
      } else {
        console.log('WebsiteStep: No existing analysis found');
        setExistingAnalysis(null);
        return false;
      }
    } catch (error) {
      console.error('WebsiteStep: Error checking existing analysis:', error);
      setExistingAnalysis(null);
      return false;
    }
  };

  const loadExistingAnalysis = async (analysisId: number) => {
    try {
      const response = await fetch(`/api/onboarding/style-detection/analysis/${analysisId}`);
      const result = await response.json();
      
      if (result.success && result.analysis) {
        // Extract domain name for personalization
        const extractedDomain = extractDomainName(website);
        setDomainName(extractedDomain);
        
        // Combine all analysis data into a comprehensive object
        const comprehensiveAnalysis = {
          ...result.analysis.style_analysis,
          guidelines: result.analysis.style_guidelines,
          best_practices: result.analysis.style_guidelines?.best_practices,
          avoid_elements: result.analysis.style_guidelines?.avoid_elements,
          content_strategy: result.analysis.style_guidelines?.content_strategy,
          style_patterns: result.analysis.style_patterns,
          style_consistency: result.analysis.style_patterns?.style_consistency,
          unique_elements: result.analysis.style_patterns?.unique_elements
        };
        
        setAnalysis(comprehensiveAnalysis);
        setSuccess('Loaded previous analysis successfully!');
        return true;
      }
      return false;
    } catch (error) {
      console.error('Error loading existing analysis:', error);
      return false;
    }
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
      const hasExisting = await checkExistingAnalysis(fixedUrl);
      if (hasExisting && existingAnalysis) {
        setShowConfirmationDialog(true);
        setLoading(false);
        return;
      }

      // Proceed with new analysis
      await performAnalysis(fixedUrl);
    } catch (err) {
      console.error('Analysis error:', err);
      setError('Failed to analyze website. Please check your internet connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  const performAnalysis = async (fixedUrl: string) => {
      // Simulate progress updates
      const updateProgress = (step: number, message: string) => {
        setProgress(prev => prev.map(p => 
          p.step === step ? { ...p, message, completed: true } : p
        ));
      };

      updateProgress(1, 'Website URL validated');
      
      const requestData = {
        url: fixedUrl,
        include_patterns: true,
        include_guidelines: true
      };

      updateProgress(2, 'Starting content crawl...');
      
      const response = await fetch('/api/onboarding/style-detection/complete', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      updateProgress(3, 'Content extracted successfully');
      updateProgress(4, 'Style analysis in progress...');
      updateProgress(5, 'Content characteristics analyzed');
      updateProgress(6, 'Target audience identified');
      updateProgress(7, 'Recommendations generated');

      const result = await response.json();

      if (result.success) {
      // Extract domain name for personalization
      const extractedDomain = extractDomainName(fixedUrl);
      setDomainName(extractedDomain);
      
      // Combine all analysis data into a comprehensive object
      const comprehensiveAnalysis = {
        ...result.style_analysis,
        guidelines: result.style_guidelines,
        best_practices: result.style_guidelines?.best_practices,
        avoid_elements: result.style_guidelines?.avoid_elements,
        content_strategy: result.style_guidelines?.content_strategy,
        style_patterns: result.style_patterns,
        style_consistency: result.style_patterns?.style_consistency,
        unique_elements: result.style_patterns?.unique_elements
      };
      
      setAnalysis(comprehensiveAnalysis);
        
        // Check if there's a warning about fallback data
        if (result.warning) {
          setSuccess(`Website style analysis completed successfully! Note: ${result.warning}`);
        } else {
          setSuccess('Website style analysis completed successfully!');
        }
      } else {
        // Handle specific error cases
        let errorMessage = result.error || 'Analysis failed';
        
        if (errorMessage.includes('API key') || errorMessage.includes('configure')) {
          errorMessage = 'API keys not configured. Please complete step 1 of onboarding to configure your AI provider API keys.';
        } else if (errorMessage.includes('library not available')) {
          errorMessage = 'AI provider library not available. Please ensure your AI provider is properly configured in step 1.';
        } else if (errorMessage.includes('crawl') || errorMessage.includes('website')) {
          errorMessage = 'Unable to access the website. Please check the URL and ensure the website is publicly accessible.';
        }
        
        setError(errorMessage);
      }
  };

  const handleLoadExisting = async () => {
    if (existingAnalysis?.analysis_id) {
      setLoading(true);
      const success = await loadExistingAnalysis(existingAnalysis.analysis_id);
      if (!success) {
        setError('Failed to load existing analysis. Please try a new analysis.');
      }
      setLoading(false);
    }
    setShowConfirmationDialog(false);
  };

  const handleNewAnalysis = async () => {
    setShowConfirmationDialog(false);
    setExistingAnalysis(null);
    if (website) {
      const fixedUrl = fixUrlFormat(website);
      if (fixedUrl) {
        setLoading(true);
        await performAnalysis(fixedUrl);
        setLoading(false);
      }
    }
  };

  const fixUrlFormat = (url: string): string | null => {
    if (!url) return null;
    
    // Remove leading/trailing whitespace
    let fixedUrl = url.trim();
    
    // Check if URL already has a protocol but is missing slashes
    if (fixedUrl.startsWith('https:/') && !fixedUrl.startsWith('https://')) {
      fixedUrl = fixedUrl.replace('https:/', 'https://');
    } else if (fixedUrl.startsWith('http:/') && !fixedUrl.startsWith('http://')) {
      fixedUrl = fixedUrl.replace('http:/', 'http://');
    }
    
    // Add protocol if missing
    if (!fixedUrl.startsWith('http://') && !fixedUrl.startsWith('https://')) {
      fixedUrl = 'https://' + fixedUrl;
    }
    
    // Fix missing slash after protocol
    if (fixedUrl.includes('://') && !fixedUrl.split('://')[1].startsWith('/')) {
      fixedUrl = fixedUrl.replace('://', ':///');
    }
    
    // Ensure only two slashes after protocol
    if (fixedUrl.includes(':///')) {
      fixedUrl = fixedUrl.replace(':///', '://');
    }
    
    // Basic URL validation
    try {
      new URL(fixedUrl);
      return fixedUrl;
    } catch {
      return null;
    }
  };

  const handleContinue = () => {
    setError(null);
    const fixedUrl = fixUrlFormat(website);
    if (!fixedUrl) {
      setError('Please enter a valid website URL (starting with http:// or https://)');
      return;
    }
    onContinue();
  };

  const renderAnalysisSection = (title: string, data: any, icon: React.ReactNode, description?: string) => (
    <Accordion key={title} sx={{ mb: 2 }}>
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Box display="flex" alignItems="center" gap={1}>
          {icon}
          <Typography variant="h6">{title}</Typography>
        </Box>
      </AccordionSummary>
      <AccordionDetails>
        {description && (
          <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
            {description}
          </Typography>
        )}
        <Grid container spacing={2}>
          {Object.entries(data).map(([key, value]) => (
            <Grid item xs={12} md={6} key={key}>
              <Typography variant="subtitle2" color="primary" gutterBottom>
                {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:
              </Typography>
              <Typography variant="body2">
                {Array.isArray(value) ? value.join(', ') : String(value)}
              </Typography>
            </Grid>
          ))}
        </Grid>
      </AccordionDetails>
    </Accordion>
  );

  const renderGuidelinesSection = (guidelines: any) => (
    <Accordion sx={{ mb: 2 }}>
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Box display="flex" alignItems="center" gap={1}>
          <PsychologyIcon color="primary" />
          <Typography variant="h6">Content Guidelines</Typography>
        </Box>
      </AccordionSummary>
      <AccordionDetails>
        <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
          Personalized recommendations for improving your content creation based on your writing style analysis.
        </Typography>
        
        {guidelines.tone_recommendations && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle1" color="primary" gutterBottom>
              Tone Recommendations
            </Typography>
            <Box component="ul" sx={{ pl: 2 }}>
              {guidelines.tone_recommendations.map((rec: string, index: number) => (
                <Typography component="li" variant="body2" key={index} sx={{ mb: 1 }}>
                  {rec}
                </Typography>
              ))}
            </Box>
          </Box>
        )}

        {guidelines.structure_guidelines && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle1" color="primary" gutterBottom>
              Structure Guidelines
            </Typography>
            <Box component="ul" sx={{ pl: 2 }}>
              {guidelines.structure_guidelines.map((guideline: string, index: number) => (
                <Typography component="li" variant="body2" key={index} sx={{ mb: 1 }}>
                  {guideline}
                </Typography>
              ))}
            </Box>
          </Box>
        )}

        {guidelines.vocabulary_suggestions && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle1" color="primary" gutterBottom>
              Vocabulary Suggestions
            </Typography>
            <Box component="ul" sx={{ pl: 2 }}>
              {guidelines.vocabulary_suggestions.map((suggestion: string, index: number) => (
                <Typography component="li" variant="body2" key={index} sx={{ mb: 1 }}>
                  {suggestion}
                </Typography>
              ))}
            </Box>
          </Box>
        )}

        {guidelines.engagement_tips && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle1" color="primary" gutterBottom>
              Engagement Tips
            </Typography>
            <Box component="ul" sx={{ pl: 2 }}>
              {guidelines.engagement_tips.map((tip: string, index: number) => (
                <Typography component="li" variant="body2" key={index} sx={{ mb: 1 }}>
                  {tip}
                </Typography>
              ))}
            </Box>
          </Box>
        )}

        {guidelines.audience_considerations && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle1" color="primary" gutterBottom>
              Audience Considerations
            </Typography>
            <Box component="ul" sx={{ pl: 2 }}>
              {guidelines.audience_considerations.map((consideration: string, index: number) => (
                <Typography component="li" variant="body2" key={index} sx={{ mb: 1 }}>
                  {consideration}
                </Typography>
              ))}
            </Box>
          </Box>
        )}
      </AccordionDetails>
    </Accordion>
  );

  const renderBestPracticesSection = (bestPractices: string[]) => (
    <Accordion sx={{ mb: 2 }}>
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Box display="flex" alignItems="center" gap={1}>
          <CheckIcon color="success" />
          <Typography variant="h6">Best Practices</Typography>
        </Box>
      </AccordionSummary>
      <AccordionDetails>
        <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
          Recommended practices to enhance your content quality and effectiveness.
        </Typography>
        <Box component="ul" sx={{ pl: 2 }}>
          {bestPractices.map((practice: string, index: number) => (
            <Typography component="li" variant="body2" key={index} sx={{ mb: 1 }}>
              {practice}
            </Typography>
          ))}
        </Box>
      </AccordionDetails>
    </Accordion>
  );

  const renderAvoidElementsSection = (avoidElements: string[]) => (
    <Accordion sx={{ mb: 2 }}>
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Box display="flex" alignItems="center" gap={1}>
          <InfoIcon color="warning" />
          <Typography variant="h6">Elements to Avoid</Typography>
        </Box>
      </AccordionSummary>
      <AccordionDetails>
        <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
          Elements that may detract from your content's effectiveness based on your writing style.
        </Typography>
        <Box component="ul" sx={{ pl: 2 }}>
          {avoidElements.map((element: string, index: number) => (
            <Typography component="li" variant="body2" key={index} sx={{ mb: 1 }}>
              {element}
            </Typography>
          ))}
        </Box>
      </AccordionDetails>
    </Accordion>
  );

  const renderContentStrategySection = (contentStrategy: string) => (
    <Accordion sx={{ mb: 2 }}>
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Box display="flex" alignItems="center" gap={1}>
          <TrendingUpIcon color="info" />
          <Typography variant="h6">Content Strategy</Typography>
        </Box>
      </AccordionSummary>
      <AccordionDetails>
        <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
          Overall content strategy recommendation based on your writing style analysis.
        </Typography>
        <Typography variant="body1" sx={{ lineHeight: 1.6 }}>
          {contentStrategy}
        </Typography>
      </AccordionDetails>
    </Accordion>
  );

  const renderStylePatternsSection = (patterns: any) => (
    <Accordion sx={{ mb: 2 }}>
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Box display="flex" alignItems="center" gap={1}>
          <AnalyticsIcon color="secondary" />
          <Typography variant="h6">Style Patterns</Typography>
        </Box>
      </AccordionSummary>
      <AccordionDetails>
        <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
          Recurring patterns and characteristics identified in your writing style.
        </Typography>
        
        <Grid container spacing={2}>
          {Object.entries(patterns).map(([key, value]) => (
            <Grid item xs={12} md={6} key={key}>
              <Typography variant="subtitle2" color="primary" gutterBottom>
                {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:
                  </Typography>
                  <Typography variant="body2">
                    {Array.isArray(value) ? value.join(', ') : String(value)}
                  </Typography>
            </Grid>
          ))}
        </Grid>
      </AccordionDetails>
    </Accordion>
  );

  const getProgressPercentage = () => {
    const completedSteps = progress.filter(p => p.completed).length;
    return (completedSteps / progress.length) * 100;
  };

  const extractDomainName = (url: string): string => {
    try {
      const domain = new URL(url).hostname.replace('www.', '');
      return domain.charAt(0).toUpperCase() + domain.slice(1);
    } catch {
      return 'Your Website';
    }
  };

  const renderKeyInsight = (title: string, value: string | string[], icon: React.ReactNode, color: string = 'primary') => (
    <Fade in timeout={800}>
      <Paper elevation={2} sx={{ p: 2, mb: 2, borderLeft: `4px solid ${color}.main` }}>
        <Box display="flex" alignItems="center" gap={2}>
          <Box sx={{ color: `${color}.main` }}>
            {icon}
          </Box>
          <Box flex={1}>
            <Typography variant="subtitle2" color="textSecondary" gutterBottom>
              {title}
            </Typography>
            <Typography variant="body1" fontWeight={500}>
              {Array.isArray(value) ? value.join(', ') : value}
            </Typography>
          </Box>
        </Box>
      </Paper>
    </Fade>
  );

  const renderGuidelinesCard = (title: string, items: string[], icon: React.ReactNode, color: string = 'primary') => (
    <Zoom in timeout={600}>
      <Card sx={{ mb: 2, border: `1px solid ${color}.light` }}>
        <CardContent>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <Box sx={{ color: `${color}.main` }}>
              {icon}
            </Box>
            <Typography variant="h6" fontWeight={600}>
              {title}
            </Typography>
          </Box>
          <Box component="ul" sx={{ pl: 2, m: 0 }}>
            {items.map((item, index) => (
              <Typography component="li" variant="body2" key={index} sx={{ mb: 1, lineHeight: 1.6 }}>
                {item}
              </Typography>
            ))}
          </Box>
        </CardContent>
      </Card>
    </Zoom>
  );

  const renderProUpgradeAlert = () => (
    <Slide direction="up" in timeout={1000}>
      <Alert 
        severity="info" 
        sx={{ 
          mb: 3, 
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          '& .MuiAlert-icon': { color: 'white' }
        }}
        action={
          <Button color="inherit" size="small" variant="outlined" sx={{ color: 'white', borderColor: 'white' }}>
            Learn More
          </Button>
        }
      >
        <Typography variant="subtitle2" gutterBottom>
          <StarIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Limited Analysis Scope
        </Typography>
        <Typography variant="body2">
          This analysis is based on your homepage only. <strong>ALwrity Pro</strong> can index your entire website and social media content for comprehensive personalized content generation.
        </Typography>
      </Alert>
    </Slide>
  );

  const renderBrandAnalysisSection = (brandAnalysis: any) => (
    <Zoom in timeout={700}>
      <Card sx={{ mb: 2, border: '2px solid info.light', background: 'info.50' }}>
        <CardContent>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <BusinessIcon color="info" />
            <Typography variant="h6" fontWeight={600} color="info.main">
              Brand Analysis
            </Typography>
          </Box>
          
          <Grid container spacing={2}>
            {brandAnalysis.brand_voice && (
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="primary" gutterBottom>
                  Brand Voice:
                </Typography>
                <Typography variant="body2" sx={{ mb: 2 }}>
                  {brandAnalysis.brand_voice}
                </Typography>
              </Grid>
            )}
            
            {brandAnalysis.brand_positioning && (
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="primary" gutterBottom>
                  Brand Positioning:
                </Typography>
                <Typography variant="body2" sx={{ mb: 2 }}>
                  {brandAnalysis.brand_positioning}
                </Typography>
              </Grid>
            )}
            
            {brandAnalysis.brand_values && brandAnalysis.brand_values.length > 0 && (
              <Grid item xs={12}>
                <Typography variant="subtitle2" color="primary" gutterBottom>
                  Brand Values:
                </Typography>
                <Box component="ul" sx={{ pl: 2, m: 0 }}>
                  {brandAnalysis.brand_values.map((value: string, index: number) => (
                    <Typography component="li" variant="body2" key={index} sx={{ mb: 1 }}>
                      {value}
                    </Typography>
                  ))}
                </Box>
              </Grid>
            )}
          </Grid>
        </CardContent>
      </Card>
    </Zoom>
  );

  const renderContentStrategyInsightsSection = (insights: any) => (
    <Zoom in timeout={800}>
      <Card sx={{ mb: 2, border: '2px solid secondary.light', background: 'secondary.50' }}>
        <CardContent>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <AnalyticsIcon color="secondary" />
            <Typography variant="h6" fontWeight={600} color="secondary.main">
              Content Strategy Insights
            </Typography>
          </Box>
          
          <Grid container spacing={3}>
            {insights.strengths && insights.strengths.length > 0 && (
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="success.main" gutterBottom>
                  ✅ Strengths:
                </Typography>
                <Box component="ul" sx={{ pl: 2, m: 0 }}>
                  {insights.strengths.map((strength: string, index: number) => (
                    <Typography component="li" variant="body2" key={index} sx={{ mb: 1 }}>
                      {strength}
                    </Typography>
                  ))}
                </Box>
              </Grid>
            )}
            
            {insights.opportunities && insights.opportunities.length > 0 && (
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="info.main" gutterBottom>
                  🎯 Opportunities:
                </Typography>
                <Box component="ul" sx={{ pl: 2, m: 0 }}>
                  {insights.opportunities.map((opportunity: string, index: number) => (
                    <Typography component="li" variant="body2" key={index} sx={{ mb: 1 }}>
                      {opportunity}
                    </Typography>
                  ))}
                </Box>
              </Grid>
            )}
            
            {insights.recommended_improvements && insights.recommended_improvements.length > 0 && (
              <Grid item xs={12}>
                <Typography variant="subtitle2" color="primary" gutterBottom>
                  🔧 Recommended Improvements:
                </Typography>
                <Box component="ul" sx={{ pl: 2, m: 0 }}>
                  {insights.recommended_improvements.map((improvement: string, index: number) => (
                    <Typography component="li" variant="body2" key={index} sx={{ mb: 1 }}>
                      {improvement}
                    </Typography>
                  ))}
                </Box>
              </Grid>
            )}
          </Grid>
        </CardContent>
      </Card>
    </Zoom>
  );

  const renderAIGenerationTipsSection = (tips: string[]) => (
    <Zoom in timeout={900}>
      <Card sx={{ mb: 2, border: '2px solid primary.light', background: 'primary.50' }}>
        <CardContent>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <AutoAwesomeIcon color="primary" />
            <Typography variant="h6" fontWeight={600} color="primary.main">
              AI Content Generation Tips
            </Typography>
          </Box>
          <Box component="ul" sx={{ pl: 2, m: 0 }}>
            {tips.map((tip: string, index: number) => (
              <Typography component="li" variant="body2" key={index} sx={{ mb: 1, lineHeight: 1.6 }}>
                {tip}
              </Typography>
            ))}
          </Box>
        </CardContent>
      </Card>
    </Zoom>
  );

  // Conditional rendering for business description form
  if (showBusinessForm) {
    return (
      <BusinessDescriptionStep
        onBack={() => {
          console.log('⬅️ Going back to website form...');
          setShowBusinessForm(false);
        }}
        onContinue={() => {
          console.log('➡️ Business info completed, proceeding to next step...');
          onContinue();
        }}
      />
    );
  }

  return (
    <Box sx={{ maxWidth: 900, mx: 'auto', p: 3 }}>
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

      {/* API Key Configuration Notice */}
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body2">
          <strong>Note:</strong> To perform accurate style analysis, you need to configure AI provider API keys in step 1. 
          If you haven't completed step 1 yet, please go back and configure your API keys for the best experience.
        </Typography>
      </Alert>

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

      {loading && (
        <Card sx={{ mb: 3, p: 3 }}>
          <Typography variant="h6" gutterBottom>
            <AnalyticsIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Analysis Progress
          </Typography>
          
          <LinearProgress 
            variant="determinate" 
            value={getProgressPercentage()} 
            sx={{ mb: 2 }}
          />
          
          <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
            {Math.round(getProgressPercentage())}% Complete
          </Typography>

          <Stepper orientation="vertical" activeStep={progress.filter(p => p.completed).length}>
            {progress.map((step) => (
              <Step key={step.step} completed={step.completed}>
                <StepLabel>
                  <Typography variant="body2">
                    {step.message}
                  </Typography>
                </StepLabel>
              </Step>
            ))}
          </Stepper>
        </Card>
      )}

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
        <Fade in timeout={800}>
          <Box>
            {/* Pro Upgrade Alert */}
            {renderProUpgradeAlert()}
            
            {/* Main Analysis Results */}
            <Card sx={{ mb: 3, background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)' }}>
              <CardContent sx={{ p: 4 }}>
                <Box display="flex" alignItems="center" gap={2} mb={3}>
                  <VerifiedIcon sx={{ color: 'success.main', fontSize: 32 }} />
                  <Box>
                    <Typography variant="h4" fontWeight={700} gutterBottom>
                      {domainName} Style Analysis
                    </Typography>
                    <Typography variant="body1" color="textSecondary">
                      Comprehensive content analysis and personalized recommendations
                    </Typography>
                  </Box>
                </Box>

                {/* Key Insights Grid */}
                <Grid container spacing={3} mb={4}>
                  {analysis.writing_style?.tone && (
                    <Grid item xs={12} md={6}>
                      {renderKeyInsight(
                        'Writing Tone',
                        analysis.writing_style.tone,
                        <PaletteIcon />,
                        'primary'
                      )}
                    </Grid>
                  )}
                  
                  {analysis.writing_style?.complexity && (
                    <Grid item xs={12} md={6}>
                      {renderKeyInsight(
                        'Content Complexity',
                        analysis.writing_style.complexity,
                        <SpeedIcon />,
                        'secondary'
                      )}
                    </Grid>
                  )}
                  
                  {analysis.target_audience?.expertise_level && (
                    <Grid item xs={12} md={6}>
                      {renderKeyInsight(
                        'Target Audience',
                        analysis.target_audience.expertise_level,
                        <GroupIcon />,
                        'info'
                      )}
                    </Grid>
                  )}
                  
                  {analysis.content_type?.primary_type && (
                    <Grid item xs={12} md={6}>
                      {renderKeyInsight(
                        'Content Type',
                        analysis.content_type.primary_type,
                        <BusinessIcon />,
                        'warning'
                      )}
                    </Grid>
                  )}
                </Grid>

                <Divider sx={{ my: 3 }} />

                {/* Content Strategy */}
                {analysis.content_strategy && (
                  <Box mb={4}>
                    <Typography variant="h5" fontWeight={600} gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <AutoAwesomeIcon color="primary" />
                      Content Strategy
                    </Typography>
                    <Paper elevation={3} sx={{ p: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
                      <Typography variant="body1" sx={{ lineHeight: 1.8, fontSize: '1.1rem' }}>
                        {analysis.content_strategy}
                      </Typography>
                    </Paper>
                  </Box>
                )}

                {/* Brand Analysis */}
                {analysis.brand_analysis && renderBrandAnalysisSection(analysis.brand_analysis)}

                {/* Content Strategy Insights */}
                {analysis.content_strategy_insights && renderContentStrategyInsightsSection(analysis.content_strategy_insights)}

                {/* AI Generation Tips */}
                {analysis.ai_generation_tips && renderAIGenerationTipsSection(analysis.ai_generation_tips)}

                {/* Enhanced Guidelines Section */}
                {analysis.guidelines && (
                  <Box mb={4}>
                    <Typography variant="h5" fontWeight={600} gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <LightbulbIcon color="primary" />
                      Enhanced Content Guidelines for {domainName}
                    </Typography>
                    
                    <Grid container spacing={3}>
                      {analysis.guidelines.tone_recommendations && (
                        <Grid item xs={12} md={6}>
                          {renderGuidelinesCard(
                            'Tone Recommendations',
                            analysis.guidelines.tone_recommendations,
                            <PsychologyIcon />,
                            'primary'
                          )}
                        </Grid>
                      )}
                      
                      {analysis.guidelines.structure_guidelines && (
                        <Grid item xs={12} md={6}>
                          {renderGuidelinesCard(
                            'Structure Guidelines',
                            analysis.guidelines.structure_guidelines,
                            <AnalyticsIcon />,
                            'secondary'
                          )}
                        </Grid>
                      )}
                      
                      {analysis.guidelines.engagement_tips && (
                        <Grid item xs={12} md={6}>
                          {renderGuidelinesCard(
                            'Engagement Tips',
                            analysis.guidelines.engagement_tips,
                            <TrendingUpIcon />,
                            'success'
                          )}
                        </Grid>
                      )}
                      
                      {analysis.guidelines.vocabulary_suggestions && (
                        <Grid item xs={12} md={6}>
                          {renderGuidelinesCard(
                            'Vocabulary Suggestions',
                            analysis.guidelines.vocabulary_suggestions,
                            <LanguageIcon />,
                            'info'
                          )}
                        </Grid>
                      )}
                      
                      {analysis.guidelines.brand_alignment && (
                        <Grid item xs={12} md={6}>
                          {renderGuidelinesCard(
                            'Brand Alignment',
                            analysis.guidelines.brand_alignment,
                            <BusinessIcon />,
                            'warning'
                          )}
                        </Grid>
                      )}
                      
                      {analysis.guidelines.seo_optimization && (
                        <Grid item xs={12} md={6}>
                          {renderGuidelinesCard(
                            'SEO Optimization',
                            analysis.guidelines.seo_optimization,
                            <WebIcon />,
                            'primary'
                          )}
                        </Grid>
                      )}
                      
                      {analysis.guidelines.conversion_optimization && (
                        <Grid item xs={12} md={6}>
                          {renderGuidelinesCard(
                            'Conversion Optimization',
                            analysis.guidelines.conversion_optimization,
                            <TrendingUpIcon />,
                            'success'
                          )}
                        </Grid>
                      )}
                    </Grid>
                  </Box>
                )}

                {/* Best Practices & Avoid Elements */}
                <Grid container spacing={3} mb={4}>
                  {analysis.best_practices && (
                    <Grid item xs={12} md={6}>
                      <Zoom in timeout={800}>
                        <Card sx={{ border: '2px solid success.light', background: 'success.50' }}>
                          <CardContent>
                            <Box display="flex" alignItems="center" gap={1} mb={2}>
                              <CheckIcon color="success" />
                              <Typography variant="h6" fontWeight={600} color="success.main">
                                Best Practices
                              </Typography>
                            </Box>
                            <Box component="ul" sx={{ pl: 2, m: 0 }}>
                              {analysis.best_practices.map((practice, index) => (
                                <Typography component="li" variant="body2" key={index} sx={{ mb: 1, lineHeight: 1.6 }}>
                                  {practice}
                                </Typography>
                              ))}
                            </Box>
                          </CardContent>
                        </Card>
                      </Zoom>
                    </Grid>
                  )}
                  
                  {analysis.avoid_elements && (
                    <Grid item xs={12} md={6}>
                      <Zoom in timeout={1000}>
                        <Card sx={{ border: '2px solid warning.light', background: 'warning.50' }}>
                          <CardContent>
                            <Box display="flex" alignItems="center" gap={1} mb={2}>
                              <WarningIcon color="warning" />
                              <Typography variant="h6" fontWeight={600} color="warning.main">
                                Elements to Avoid
                              </Typography>
                            </Box>
                            <Box component="ul" sx={{ pl: 2, m: 0 }}>
                              {analysis.avoid_elements.map((element, index) => (
                                <Typography component="li" variant="body2" key={index} sx={{ mb: 1, lineHeight: 1.6 }}>
                                  {element}
                                </Typography>
                              ))}
                            </Box>
                          </CardContent>
                        </Card>
                      </Zoom>
                    </Grid>
                  )}
                </Grid>

                {/* GenAI Integration Checkbox */}
                <Box sx={{ 
                  p: 3, 
                  bgcolor: 'primary.50', 
                  borderRadius: 2, 
                  border: '2px solid primary.light',
                  mb: 3
                }}>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={useAnalysisForGenAI}
                        onChange={(e) => setUseAnalysisForGenAI(e.target.checked)}
                        color="primary"
                        size="large"
                      />
                    }
                    label={
                      <Box>
                        <Typography variant="h6" fontWeight={600} gutterBottom>
                          Use Analysis for AI Content Generation
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          Apply this style analysis to personalize AI-generated content, ensuring it matches {domainName}'s voice and tone.
                        </Typography>
                      </Box>
                    }
                  />
                </Box>

                {/* Success Message */}
                <Alert severity="success" sx={{ mb: 0 }}>
                  <Typography variant="body1" fontWeight={500}>
                    ✅ Analysis complete! Your content style has been analyzed and personalized recommendations are ready.
                  </Typography>
                </Alert>
          </CardContent>
        </Card>
          </Box>
        </Fade>
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
          <Button onClick={handleLoadExisting} variant="outlined" startIcon={<HistoryIcon />}>
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