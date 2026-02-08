/**
 * AnalysisResultsDisplay Component
 * Displays the comprehensive website analysis results
 */

import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Divider,
  Checkbox,
  FormControlLabel,
  Alert,
  Paper,
  List,
  ListItem,
  ListItemText,
  Link,
  Collapse,
  Switch,
  Button
} from '@mui/material';
import {
  AutoAwesome as AutoAwesomeIcon,
  Verified as VerifiedIcon,
  Analytics as AnalyticsIcon,
  TrendingUp as TrendingUpIcon,
  Business as BusinessIcon,
  Info as InfoIcon,
  Link as LinkIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  ExpandLess as ExpandLessIcon,
  ExpandMore as ExpandMoreIcon,
  Lightbulb as LightbulbIcon
} from '@mui/icons-material';

// Import rendering utilities
import {
  renderProUpgradeAlert,
  renderBestPracticesSection,
  renderAvoidElementsSection,
  renderBrandAnalysisSection
} from '../utils/renderUtils';

// Import extracted components
import { 
  EnhancedGuidelinesSection, 
  KeyInsightsGrid,
  ContentStrategyInsightsSection,
  StrategicInsightsSection,
  SEOAuditSection,
  SitemapAnalysisSection,
  CombinedAnalysisSection,
  CombinedStrategySection,
  TargetAudienceAnalysisSection,
  ContentCharacteristicsSection
} from './index';
import SectionHeader from './SectionHeader';
import { useOnboardingStyles } from '../../common/useOnboardingStyles';

import { apiClient } from '../../../../api/client';

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
    brand_story?: string;
    unique_selling_propositions?: string[];
  };
  strategic_insights?: {
    content_strategy: string;
    competitive_advantages: string[];
    content_calendar_suggestions: string[];
    ai_generation_tips: string[];
  };
  content_strategy_insights?: any;
  style_guidelines?: any;
  style_patterns?: any;
  seo_audit?: any;
  sitemap_analysis?: any;
  best_practices?: string[];
  avoid_elements?: string[];
}

interface AnalysisResultsDisplayProps {
  analysis: StyleAnalysis;
  domainName: string;
  useAnalysisForGenAI: boolean;
  onUseAnalysisChange: (use: boolean) => void;
  crawlResult?: any;
  onAnalysisUpdate?: (updatedAnalysis: StyleAnalysis) => void;
  onSave?: () => void;
}

const AnalysisResultsDisplay: React.FC<AnalysisResultsDisplayProps> = ({
  analysis,
  domainName,
  useAnalysisForGenAI,
  onUseAnalysisChange,
  crawlResult,
  onAnalysisUpdate,
  onSave
}) => {
  const styles = useOnboardingStyles();
  const [isCrawlExpanded, setIsCrawlExpanded] = useState(false);
  const [isEditable, setIsEditable] = useState(false);

  // Helper to handle section updates
  const handleSectionUpdate = (section: string, fieldPath: string, value: any) => {
    if (!onAnalysisUpdate) return;
    
    const newAnalysis = { ...analysis };
    
    // Check if we are updating a nested field or the section itself
    // If section and fieldPath are same, it's a direct update of a top-level property
    if (section === fieldPath) {
        (newAnalysis as any)[section] = value;
    } else {
        // Nested update
        // Handle style_patterns specifically as it might be undefined initially
        if (section === 'style_patterns' || section === 'patterns') {
            const sectionData: any = { ...((newAnalysis as any)[section] || {}) };
            sectionData[fieldPath] = value;
            (newAnalysis as any)[section] = sectionData;
        } 
        // Handle guidelines specifically
        else if (section === 'guidelines') {
            const sectionData: any = { ...((newAnalysis as any)[section] || {}) };
            sectionData[fieldPath] = value;
            (newAnalysis as any)[section] = sectionData;
        }
        else if (
          typeof (newAnalysis as any)[section] === 'object' &&
          (newAnalysis as any)[section] !== null &&
          !Array.isArray((newAnalysis as any)[section])
        ) {
            // Generic object update
            const sectionData: any = { ...((newAnalysis as any)[section] || {}) };
            sectionData[fieldPath] = value;
            (newAnalysis as any)[section] = sectionData;
        }
    }
      
    onAnalysisUpdate(newAnalysis);
  };

  const handleRunSEOAudit = async (url: string) => {
    try {
      const response = await apiClient.post('/api/seo/on-page-analysis', {
        url: url,
        analyze_images: true,
        analyze_content_quality: true
      });
      return response.data;
    } catch (error) {
      console.error('Failed to run SEO audit:', error);
      throw error;
    }
  };

  if (!analysis) {
    return null;
  }

  return (
    <Box sx={{
      ...styles.analysisContainer,
      // Global readability hard overrides for Step 2 display area
      '& .MuiTypography-root': {
        color: '#111827 !important',
        WebkitTextFillColor: '#111827',
      },
      '& .MuiPaper-root': {
        backgroundColor: '#ffffff !important',
        backgroundImage: 'none !important',
      },
      '& .MuiCard-root': {
        backgroundColor: '#ffffff !important',
        backgroundImage: 'none !important',
      }
    }}>
      {/* Pro Upgrade Alert removed per request */}
      
      {/* Main Analysis Results */}
      <Card sx={styles.analysisHeaderCard}>
        <CardContent sx={styles.analysisCardContent}>
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                <VerifiedIcon sx={{ ...styles.analysisHeaderIcon, fontSize: 32 }} />
                <Box>
                  <Typography 
                    variant="h4" 
                    sx={{
                      ...styles.analysisHeaderTitle,
                      color: '#1a202c !important',
                      fontWeight: '700 !important',
                      mb: 0.5
                    }} 
                  >
                    {domainName} Style Analysis
                  </Typography>
                  <Typography 
                    variant="body1" 
                    sx={{ color: '#4a5568 !important' }}
                  >
                    AI-powered analysis of your brand voice and content strategy
                  </Typography>
                </Box>
              </Box>
              <Box sx={{ display: 'flex', gap: 1 }}>
                {onSave && (
                  <Button
                    startIcon={<SaveIcon />}
                    variant="contained"
                    onClick={onSave}
                    sx={{
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      color: 'white',
                      '&:hover': {
                         background: 'linear-gradient(135deg, #5a6fd6 0%, #663d91 100%)',
                      }
                    }}
                  >
                    Save Analysis
                  </Button>
                )}
                {onAnalysisUpdate && (
                  <FormControlLabel
                    control={
                      <Switch
                        checked={isEditable}
                        onChange={(e) => setIsEditable(e.target.checked)}
                        color="primary"
                      />
                    }
                    label="Edit Mode"
                    sx={{ 
                      '& .MuiTypography-root': { color: '#4a5568 !important' } 
                    }}
                  />
                )}
              </Box>
            </Box>

            <Alert 
              severity="info" 
              icon={<AutoAwesomeIcon />}
              sx={{ 
                mb: 3, 
                borderRadius: 2,
                '& .MuiAlert-message': { color: '#1e293b' },
                '& .MuiAlert-icon': { color: '#3b82f6' }
              }}
            >
              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 0.5 }}>
                AI Analysis Complete
              </Typography>
              <Typography variant="body2">
                We've analyzed your content to understand your brand voice, audience, and strategy. 
                Use these insights to generate on-brand content automatically.
              </Typography>
            </Alert>

            <FormControlLabel
              control={
                <Checkbox
                  checked={useAnalysisForGenAI}
                  onChange={(e) => onUseAnalysisChange(e.target.checked)}
                  color="primary"
                  sx={{ '&.Mui-checked': { color: '#764ba2' } }}
                />
              }
              label={
                <Box>
                  <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#1f2937 !important' }}>
                    Use this analysis for AI generation
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#4b5563 !important' }}>
                    Apply these style guidelines to all future content generated by ALwrity
                  </Typography>
                </Box>
              }
              sx={{ 
                mt: 1,
                p: 2,
                borderRadius: 2,
                bgcolor: '#f8fafc',
                border: '1px solid #e2e8f0',
                width: '100%',
                ml: 0
              }}
            />
          </Box>

          <Divider sx={{ my: 3 }} />

          {/* Key Insights Grid */}
          <KeyInsightsGrid 
            writing_style={analysis.writing_style}
            target_audience={analysis.target_audience}
            content_type={analysis.content_type}
          />

          {/* Strategic Insights Section */}
          <Box sx={{ mt: 4 }}>
            <SectionHeader 
              title="Strategic Insights" 
              icon={<LightbulbIcon />} 
            />
            <StrategicInsightsSection 
              contentStrategy={analysis.strategic_insights?.content_strategy}
              competitiveAdvantages={analysis.strategic_insights?.competitive_advantages}
              contentCalendarSuggestions={analysis.strategic_insights?.content_calendar_suggestions}
              aiGenerationTips={analysis.strategic_insights?.ai_generation_tips}
              isEditable={isEditable}
              onUpdate={(field, value) => handleSectionUpdate('strategic_insights', field, value)}
            />
          </Box>

          {/* Content Strategy Insights */}
          <Box sx={{ mt: 4 }}>
             <SectionHeader 
              title="Content Strategy" 
              icon={<TrendingUpIcon />} 
            />
             <ContentStrategyInsightsSection 
               insights={analysis.content_strategy_insights}
               isEditable={isEditable}
               onUpdate={(field, value) => handleSectionUpdate('content_strategy_insights', field, value)}
             />
          </Box>
          
          {/* Brand Analysis Section */}
          <Box sx={{ mt: 4 }}>
            <SectionHeader 
              title="Brand Identity" 
              icon={<BusinessIcon />} 
            />
            {renderBrandAnalysisSection(analysis)}
          </Box>

          {/* Style Guidelines Section */}
          <Box sx={{ mt: 4 }}>
            <SectionHeader 
              title="Style Guidelines" 
              icon={<AutoAwesomeIcon />} 
            />
            <EnhancedGuidelinesSection 
              guidelines={analysis.style_guidelines}
              domainName={domainName}
            />
          </Box>

          {/* SEO Audit Section */}
          <Box sx={{ mt: 4 }}>
             <SectionHeader 
              title="SEO Audit" 
              icon={<AnalyticsIcon />} 
            />
             <SEOAuditSection
               seoAudit={analysis.seo_audit}
               domainName={domainName}
               onRunAudit={() => handleRunSEOAudit(domainName)}
             />
          </Box>

          {/* Sitemap Analysis Section */}
          <Box sx={{ mt: 4 }}>
             <SectionHeader 
              title="Sitemap Analysis" 
              icon={<LinkIcon />} 
            />
             <SitemapAnalysisSection
               sitemapAnalysis={analysis.sitemap_analysis}
               domainName={domainName}
             />
          </Box>

          {/* Combined Analysis Section (Legacy Support) */}
          <Box sx={{ mt: 4 }}>
            <CombinedAnalysisSection 
              contentCharacteristics={analysis.content_characteristics}
              targetAudience={analysis.target_audience}
              contentType={analysis.content_type}
              brandAnalysis={analysis.brand_analysis}
              contentStrategyInsights={analysis.content_strategy_insights}
              isEditable={isEditable}
              onUpdate={handleSectionUpdate}
            />
          </Box>

          {/* Combined Strategy Section (Legacy Support) */}
          <Box sx={{ mt: 4 }}>
             <CombinedStrategySection 
               contentStrategy={analysis.strategic_insights?.content_strategy}
               competitiveAdvantages={analysis.strategic_insights?.competitive_advantages}
               contentCalendarSuggestions={analysis.strategic_insights?.content_calendar_suggestions}
               aiGenerationTips={analysis.strategic_insights?.ai_generation_tips}
               stylePatterns={analysis.style_patterns}
               domainName={domainName}
               isEditable={isEditable}
               onUpdate={handleSectionUpdate}
             />
          </Box>
          
          <Grid container spacing={3} sx={{ mt: 2 }}>
            {/* Target Audience */}
            <Grid item xs={12} md={6}>
              <TargetAudienceAnalysisSection targetAudience={analysis.target_audience} />
            </Grid>
            
            {/* Content Characteristics */}
            <Grid item xs={12} md={6}>
              <ContentCharacteristicsSection contentCharacteristics={analysis.content_characteristics} />
            </Grid>
          </Grid>

          <Grid container spacing={3} sx={{ mt: 2 }}>
            <Grid item xs={12} md={6}>
              {analysis.best_practices && renderBestPracticesSection(analysis.best_practices)}
            </Grid>
            <Grid item xs={12} md={6}>
              {analysis.avoid_elements && renderAvoidElementsSection(analysis.avoid_elements)}
            </Grid>
          </Grid>
          
          {/* Raw Crawl Data (Collapsible) */}
          {crawlResult && (
            <Box sx={{ mt: 4 }}>
              <Button
                onClick={() => setIsCrawlExpanded(!isCrawlExpanded)}
                endIcon={isCrawlExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                sx={{ mb: 2 }}
              >
                {isCrawlExpanded ? 'Hide Raw Crawl Data' : 'Show Raw Crawl Data'}
              </Button>
              <Collapse in={isCrawlExpanded}>
                <Paper sx={{ p: 2, bgcolor: '#f8fafc', maxHeight: '400px', overflow: 'auto' }}>
                  <Typography variant="h6" gutterBottom>Raw Crawl Result</Typography>
                  <pre style={{ fontSize: '0.75rem', whiteSpace: 'pre-wrap' }}>
                    {JSON.stringify(crawlResult, null, 2)}
                  </pre>
                </Paper>
              </Collapse>
            </Box>
          )}

        </CardContent>
      </Card>
    </Box>
  );
};

export default AnalysisResultsDisplay;
