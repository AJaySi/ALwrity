/**
 * AnalysisResultsDisplay Component
 * Displays the comprehensive website analysis results
 */

import React from 'react';
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
  Paper
} from '@mui/material';
import {
  AutoAwesome as AutoAwesomeIcon,
  Verified as VerifiedIcon,
  Analytics as AnalyticsIcon,
  TrendingUp as TrendingUpIcon,
  Business as BusinessIcon,
  Lightbulb as LightbulbIcon
} from '@mui/icons-material';

// Import rendering utilities
import {
  renderKeyInsight,
  renderProUpgradeAlert,
  renderBrandAnalysisSection,
  renderContentStrategyInsightsSection,
  renderAIGenerationTipsSection,
  renderBestPracticesSection,
  renderAvoidElementsSection,
  renderStylePatternsSection
} from '../utils/renderUtils';

// Import extracted components
import { 
  EnhancedGuidelinesSection, 
  KeyInsightsGrid,
  ContentCharacteristicsSection,
  TargetAudienceAnalysisSection
} from './index';
import { useOnboardingStyles } from '../../common/useOnboardingStyles';

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
  patterns?: {
    sentence_length: string;
    vocabulary_patterns: string[];
    rhetorical_devices: string[];
    paragraph_structure: string;
    transition_phrases: string[];
  };
  style_consistency?: string;
  unique_elements?: string[];
}

interface AnalysisResultsDisplayProps {
  analysis: StyleAnalysis;
  domainName: string;
  useAnalysisForGenAI: boolean;
  onUseAnalysisChange: (use: boolean) => void;
}

const AnalysisResultsDisplay: React.FC<AnalysisResultsDisplayProps> = ({
  analysis,
  domainName,
  useAnalysisForGenAI,
  onUseAnalysisChange
}) => {
  const styles = useOnboardingStyles();

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
          <Box sx={styles.analysisHeader}>
            <VerifiedIcon sx={styles.analysisHeaderIcon} />
            <Box>
              <Typography 
                variant="h4" 
                sx={{
                  ...styles.analysisHeaderTitle,
                  color: '#1a202c !important', // Force dark text
                  fontWeight: '700 !important'
                }} 
                gutterBottom
              >
                {domainName} Style Analysis
              </Typography>
              <Typography 
                variant="body1" 
                sx={{
                  ...styles.analysisHeaderSubtitle,
                  color: '#4a5568 !important' // Force dark secondary text
                }}
              >
                Comprehensive content analysis and personalized recommendations
              </Typography>
            </Box>
          </Box>

          {/* Key Insights Grid */}
          <KeyInsightsGrid 
            writing_style={analysis.writing_style}
            target_audience={analysis.target_audience}
            content_type={analysis.content_type}
          />

          {/* Content Characteristics Section */}
          <ContentCharacteristicsSection 
            contentCharacteristics={analysis.content_characteristics as any}
          />

          {/* Target Audience Analysis Section */}
          <TargetAudienceAnalysisSection 
            targetAudience={analysis.target_audience as any}
          />

          {/* Content Type Details Section */}
          {analysis.content_type && (
            <Box sx={{ ...styles.analysisSection, mt: 4 }}>
              <Typography 
                variant="h5" 
                sx={{
                  ...styles.analysisSectionHeader,
                  color: '#1a202c !important', // Force dark text
                  fontWeight: '700 !important'
                }}
              >
                <BusinessIcon sx={{ color: '#667eea !important' }} />
                Content Type Analysis
               </Typography>
               <Grid container spacing={2}>
                 {analysis.content_type.purpose && (
                  <Grid item xs={12} sm={6} md={4} lg={3} xl={2}>
                    {renderKeyInsight(
                      'Content Purpose',
                      analysis.content_type.purpose,
                      <AutoAwesomeIcon />,
                      'primary'
                    )}
                  </Grid>
                )}
                
                {analysis.content_type.call_to_action && (
                  <Grid item xs={12} sm={6} md={4} lg={3} xl={2}>
                    {renderKeyInsight(
                      'Call to Action Style',
                      analysis.content_type.call_to_action,
                      <TrendingUpIcon />,
                      'success'
                    )}
                  </Grid>
                )}
                
                {analysis.content_type.conversion_focus && (
                  <Grid item xs={12} sm={6} md={4} lg={3} xl={2}>
                    {renderKeyInsight(
                      'Conversion Focus',
                      analysis.content_type.conversion_focus,
                      <AnalyticsIcon />,
                      'info'
                    )}
                  </Grid>
                )}
                
                {analysis.content_type.educational_value && (
                  <Grid item xs={12} sm={6} md={4} lg={3} xl={2}>
                    {renderKeyInsight(
                      'Educational Value',
                      analysis.content_type.educational_value,
                      <LightbulbIcon />,
                      'warning'
                    )}
                  </Grid>
                )}
                
                {analysis.content_type.secondary_types && analysis.content_type.secondary_types.length > 0 && (
                  <Grid item xs={12}>
                    <Paper elevation={2} sx={styles.analysisAccentPaperSuccess}>
                      <Box display="flex" alignItems="center" gap={2}>
                        <Box sx={styles.analysisAccentIconSuccess}>
                          <BusinessIcon />
                        </Box>
                        <Box flex={1}>
                          <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                            Secondary Content Types
                          </Typography>
                          <Box component="ul" sx={styles.analysisList}>
                            {analysis.content_type.secondary_types.map((type: string, index: number) => (
                              <Typography component="li" variant="body2" key={index} sx={styles.analysisListItem}>
                                {type}
                              </Typography>
                            ))}
                          </Box>
                        </Box>
                      </Box>
                    </Paper>
                  </Grid>
                )}
              </Grid>
            </Box>
          )}

          <Divider sx={styles.analysisDivider} />

          {/* Content Strategy */}
          {analysis.content_strategy && (
            <Box sx={styles.analysisSection}>
              <Typography 
                variant="h5" 
                sx={{
                  ...styles.analysisSectionHeader,
                  color: '#1a202c !important', // Force dark text
                  fontWeight: '700 !important'
                }} 
                gutterBottom
              >
                <AutoAwesomeIcon color="primary" />
                Content Strategy
              </Typography>
              <Paper elevation={3} sx={styles.analysisGradientPaperPrimary}>
                <Typography variant="body1" sx={styles.analysisParagraph}>
                  {analysis.content_strategy}
                </Typography>
              </Paper>
            </Box>
          )}

          {/* Recommended Settings for AI Generation */}
          {analysis.recommended_settings && (
            <Box sx={styles.analysisSection}>
              <Typography 
                variant="h5" 
                sx={{
                  ...styles.analysisSectionHeader,
                  color: '#1a202c !important', // Force dark text
                  fontWeight: '700 !important'
                }} 
                gutterBottom
              >
                <AutoAwesomeIcon color="primary" />
                Recommended AI Generation Settings
              </Typography>
              <Paper elevation={3} sx={styles.analysisGradientPaperPrimary}>
                <Grid container spacing={2}>
                  {analysis.recommended_settings.writing_tone && (
                    <Grid item xs={12} sm={6} md={4} lg={3} xl={2}>
                      <Typography variant="subtitle2" sx={styles.analysisSubheader}>
                        Writing Tone:
                      </Typography>
                      <Typography variant="body1" sx={styles.analysisValue}>
                        {analysis.recommended_settings.writing_tone}
                      </Typography>
                    </Grid>
                  )}
                  
                  {analysis.recommended_settings.target_audience && (
                    <Grid item xs={12} sm={6} md={4} lg={3} xl={2}>
                      <Typography variant="subtitle2" sx={styles.analysisSubheader}>
                        Target Audience:
                      </Typography>
                      <Typography variant="body1" sx={styles.analysisValue}>
                        {analysis.recommended_settings.target_audience}
                      </Typography>
                    </Grid>
                  )}
                  
                  {analysis.recommended_settings.content_type && (
                    <Grid item xs={12} sm={6} md={4} lg={3} xl={2}>
                      <Typography variant="subtitle2" sx={styles.analysisSubheader}>
                        Content Type:
                      </Typography>
                      <Typography variant="body1" sx={styles.analysisValue}>
                        {analysis.recommended_settings.content_type}
                      </Typography>
                    </Grid>
                  )}
                  
                  {analysis.recommended_settings.creativity_level && (
                    <Grid item xs={12} sm={6} md={4} lg={3} xl={2}>
                      <Typography variant="subtitle2" sx={styles.analysisSubheader}>
                        Creativity Level:
                      </Typography>
                      <Typography variant="body1" sx={styles.analysisValue}>
                        {analysis.recommended_settings.creativity_level}
                      </Typography>
                    </Grid>
                  )}
                  
                  {analysis.recommended_settings.industry_context && (
                    <Grid item xs={12} sm={6} md={4} lg={3} xl={2}>
                      <Typography variant="subtitle2" sx={styles.analysisSubheader}>
                        Industry Context:
                      </Typography>
                      <Typography variant="body1" sx={styles.analysisValue}>
                        {analysis.recommended_settings.industry_context}
                      </Typography>
                    </Grid>
                  )}
                  
                  {analysis.recommended_settings.geographic_location && (
                    <Grid item xs={12} sm={6} md={4} lg={3} xl={2}>
                      <Typography variant="subtitle2" sx={styles.analysisSubheader}>
                        Geographic Focus:
                      </Typography>
                      <Typography variant="body1" sx={styles.analysisValue}>
                        {analysis.recommended_settings.geographic_location}
                      </Typography>
                    </Grid>
                  )}

                  {analysis.recommended_settings.brand_alignment && (
                    <Grid item xs={12} sm={6} md={4} lg={3} xl={2}>
                      <Typography variant="subtitle2" sx={styles.analysisSubheader}>
                        Brand Alignment:
                      </Typography>
                      <Typography variant="body1" sx={styles.analysisValue}>
                        {analysis.recommended_settings.brand_alignment}
                      </Typography>
                    </Grid>
                  )}
                </Grid>
              </Paper>
            </Box>
          )}

          {/* Brand Analysis */}
          {analysis.brand_analysis && renderBrandAnalysisSection(analysis.brand_analysis)}

          {/* Content Strategy Insights */}
          {analysis.content_strategy_insights && renderContentStrategyInsightsSection(analysis.content_strategy_insights)}

          {/* AI Generation Tips */}
          {analysis.ai_generation_tips && renderAIGenerationTipsSection(analysis.ai_generation_tips)}

          {/* Style Patterns Section */}
          {(analysis.style_patterns || analysis.patterns) && (
            <Box sx={styles.analysisSection}>
              {renderStylePatternsSection(analysis.style_patterns || analysis.patterns)}
            </Box>
          )}

          {/* Style Consistency Section */}
          {analysis.style_consistency && (
            <Box sx={styles.analysisSection}>
              <Typography 
                variant="h5" 
                sx={{
                  ...styles.analysisSectionHeader,
                  color: '#1a202c !important', // Force dark text
                  fontWeight: '700 !important'
                }} 
                gutterBottom
              >
                <AnalyticsIcon color="info" />
                Style Consistency
              </Typography>
              <Paper elevation={3} sx={styles.analysisGradientPaperWarning}>
                <Typography variant="body1" sx={styles.analysisParagraph}>
                  {analysis.style_consistency}
                </Typography>
              </Paper>
            </Box>
          )}

          {/* Unique Elements Section */}
          {analysis.unique_elements && analysis.unique_elements.length > 0 && (
            <Box sx={styles.analysisSection}>
              <Typography 
                variant="h5" 
                sx={{
                  ...styles.analysisSectionHeader,
                  color: '#1a202c !important', // Force dark text
                  fontWeight: '700 !important'
                }} 
                gutterBottom
              >
                <AutoAwesomeIcon color="primary" />
                Unique Style Elements
              </Typography>
              <Paper elevation={3} sx={styles.analysisGradientPaperAccent}>
                <Box component="ul" sx={styles.analysisList}>
                  {analysis.unique_elements.map((element: string, index: number) => (
                    <Typography component="li" variant="body1" key={index} sx={styles.analysisListItem}>
                      {element}
                    </Typography>
                  ))}
                </Box>
              </Paper>
            </Box>
          )}

          {/* Enhanced Guidelines Section */}
          {analysis.guidelines && (
            <EnhancedGuidelinesSection 
              guidelines={analysis.guidelines}
              domainName={domainName}
            />
          )}

          {/* Best Practices & Avoid Elements */}
           <Grid container spacing={2} sx={styles.analysisSection}>
            {analysis.best_practices && (
                    <Grid item xs={12} sm={6} md={4} lg={3} xl={2}>
                {renderBestPracticesSection(analysis.best_practices)}
              </Grid>
            )}
            
            {analysis.avoid_elements && (
                    <Grid item xs={12} sm={6} md={4} lg={3} xl={2}>
                {renderAvoidElementsSection(analysis.avoid_elements)}
              </Grid>
            )}
          </Grid>

          {/* Competitive Advantages */}
          {analysis.competitive_advantages && analysis.competitive_advantages.length > 0 && (
            <Box sx={styles.analysisSection}>
              <Typography 
                variant="h5" 
                sx={{
                  ...styles.analysisSectionHeader,
                  color: '#1a202c !important', // Force dark text
                  fontWeight: '700 !important'
                }} 
                gutterBottom
              >
                <TrendingUpIcon color="success" />
                Competitive Advantages
              </Typography>
              <Paper elevation={3} sx={styles.analysisGradientPaperSuccess}>
                <Box component="ul" sx={styles.analysisList}>
                  {analysis.competitive_advantages.map((advantage: string, index: number) => (
                    <Typography component="li" variant="body1" key={index} sx={styles.analysisListItem}>
                      {advantage}
                    </Typography>
                  ))}
                </Box>
              </Paper>
            </Box>
          )}

          {/* Content Calendar Suggestions */}
          {analysis.content_calendar_suggestions && analysis.content_calendar_suggestions.length > 0 && (
            <Box sx={styles.analysisSection}>
              <Typography 
                variant="h5" 
                sx={{
                  ...styles.analysisSectionHeader,
                  color: '#1a202c !important', // Force dark text
                  fontWeight: '700 !important'
                }} 
                gutterBottom
              >
                <AnalyticsIcon color="primary" />
                Content Calendar Suggestions
              </Typography>
              <Paper elevation={3} sx={styles.analysisGradientPaperInfo}>
                <Box component="ul" sx={styles.analysisList}>
                  {analysis.content_calendar_suggestions.map((suggestion: string, index: number) => (
                    <Typography component="li" variant="body1" key={index} sx={styles.analysisListItem}>
                      {suggestion}
                    </Typography>
                  ))}
                </Box>
              </Paper>
            </Box>
          )}

          {/* Content Strategy */}
          {analysis.content_strategy && (
            <Box sx={styles.analysisSection}>
              <Typography 
                variant="h5" 
                sx={{
                  ...styles.analysisSectionHeader,
                  color: '#1a202c !important', // Force dark text
                  fontWeight: '700 !important'
                }} 
                gutterBottom
              >
                <BusinessIcon color="primary" />
                Content Strategy Overview
              </Typography>
              <Paper elevation={3} sx={styles.analysisGradientPaperPrimary}>
                <Typography variant="body1" sx={styles.analysisParagraph}>
                  {analysis.content_strategy}
                </Typography>
              </Paper>
            </Box>
          )}

          {/* AI Generation Tips */}
          {analysis.ai_generation_tips && analysis.ai_generation_tips.length > 0 && (
            <Box sx={styles.analysisSection}>
              <Typography 
                variant="h5" 
                sx={{
                  ...styles.analysisSectionHeader,
                  color: '#1a202c !important', // Force dark text
                  fontWeight: '700 !important'
                }} 
                gutterBottom
              >
                <AutoAwesomeIcon color="secondary" />
                AI Content Generation Tips
              </Typography>
              <Paper elevation={3} sx={styles.analysisGradientPaperAccent}>
                <Box component="ul" sx={styles.analysisList}>
                  {analysis.ai_generation_tips.map((tip: string, index: number) => (
                    <Typography component="li" variant="body1" key={index} sx={styles.analysisListItem}>
                      {tip}
                    </Typography>
                  ))}
                </Box>
              </Paper>
            </Box>
          )}

          {/* GenAI Integration Checkbox */}
          <Box sx={styles.analysisCheckboxContainer}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={useAnalysisForGenAI}
                  onChange={(e) => onUseAnalysisChange(e.target.checked)}
                  color="primary"
                  size="large"
                />
              }
              label={
                <Box>
                  <Typography variant="h6" sx={styles.analysisSubheader} gutterBottom>
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
          <Alert severity="success" sx={styles.analysisSuccessAlert}>
            <Typography variant="body1" sx={styles.analysisAlertText}>
              ✅ Analysis complete! Your content style has been analyzed and personalized recommendations are ready.
            </Typography>
          </Alert>
        </CardContent>
      </Card>
    </Box>
  );
};

export default AnalysisResultsDisplay;
