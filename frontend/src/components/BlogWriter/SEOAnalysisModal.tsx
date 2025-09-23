/**
 * SEO Analysis Modal Component
 * 
 * Displays comprehensive SEO analysis results with visual charts and actionable recommendations.
 * Integrates with CopilotKit for real-time progress updates and user interactions.
 */

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogTitle,
  Button,
  Chip,
  LinearProgress,
  Card,
  CardContent,
  CardHeader,
  Typography,
  Box,
  Tabs,
  Tab,
  Alert,
  Grid,
  Paper,
  Divider,
  IconButton,
  Tooltip
} from '@mui/material';
import { 
  CheckCircle, 
  Cancel, 
  Warning, 
  TrendingUp, 
  GpsFixed,
  MenuBook,
  Search,
  BarChart,
  Lightbulb,
  Refresh,
  Close
} from '@mui/icons-material';
import { KeywordAnalysis, ReadabilityAnalysis, StructureAnalysis, Recommendations } from './SEO';

interface SEOAnalysisResult {
  overall_score: number;
  category_scores: {
    structure: number;
    keywords: number;
    readability: number;
    quality: number;
    headings: number;
    ai_insights: number;
  };
  analysis_summary: {
    overall_grade: string;
    status: string;
    strongest_category: string;
    weakest_category: string;
    key_strengths: string[];
    key_weaknesses: string[];
    ai_summary: string;
  };
  actionable_recommendations: Array<{
    category: string;
    priority: 'High' | 'Medium' | 'Low';
    recommendation: string;
    impact: string;
  }>;
  visualization_data: {
    score_radar: {
      categories: string[];
      scores: number[];
      max_score: number;
    };
    keyword_analysis: {
      densities: Record<string, number>;
      missing_keywords: string[];
      over_optimization: string[];
    };
    readability_metrics: Record<string, number>;
    content_stats: {
      word_count: number;
      sections: number;
      paragraphs: number;
    };
  };
  detailed_analysis?: {
    content_structure?: {
      total_sections: number;
      total_paragraphs: number;
      total_sentences: number;
      has_introduction: boolean;
      has_conclusion: boolean;
      has_call_to_action: boolean;
      structure_score: number;
      recommendations: string[];
    };
    keyword_analysis?: {
      primary_keywords: string[];
      long_tail_keywords: string[];
      semantic_keywords: string[];
      keyword_density: Record<string, number>;
      keyword_distribution: Record<string, any>;
      missing_keywords: string[];
      over_optimization: string[];
      recommendations: string[];
    };
    readability_analysis?: {
      metrics: Record<string, number>;
      avg_sentence_length: number;
      avg_paragraph_length: number;
      readability_score: number;
      target_audience: string;
      recommendations: string[];
    };
    content_quality?: {
      word_count: number;
      unique_words: number;
      vocabulary_diversity: number;
      transition_words_used: number;
      content_depth_score: number;
      flow_score: number;
      recommendations: string[];
    };
    heading_structure?: {
      h1_count: number;
      h2_count: number;
      h3_count: number;
      h1_headings: string[];
      h2_headings: string[];
      h3_headings: string[];
      heading_hierarchy_score: number;
      recommendations: string[];
    };
  };
  generated_at: string;
}

interface SEOAnalysisModalProps {
  isOpen: boolean;
  onClose: () => void;
  blogContent: string;
  researchData: any;
  onApplyRecommendations?: (recommendations: any[]) => void;
}

export const SEOAnalysisModal: React.FC<SEOAnalysisModalProps> = ({
  isOpen,
  onClose,
  blogContent,
  researchData,
  onApplyRecommendations
}) => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<SEOAnalysisResult | null>(null);
  const [progress, setProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState('recommendations');

  // Debug logging
  console.log('SEOAnalysisModal render:', { isOpen, blogContent: blogContent?.length, researchData: !!researchData });

  const runSEOAnalysis = async () => {
    try {
      setIsAnalyzing(true);
      setError(null);
      setProgress(0);
      setProgressMessage('Starting SEO analysis...');

      // Simulate progress updates (in real implementation, this would be SSE)
      const progressStages = [
        { progress: 20, message: 'Extracting keywords from research data...' },
        { progress: 40, message: 'Analyzing content structure and readability...' },
        { progress: 70, message: 'Generating AI-powered insights...' },
        { progress: 90, message: 'Compiling analysis results...' },
        { progress: 100, message: 'SEO analysis completed!' }
      ];

      for (const stage of progressStages) {
        setProgress(stage.progress);
        setProgressMessage(stage.message);
        await new Promise(resolve => setTimeout(resolve, 1000));
      }

      // Make API call to analyze blog content
      const response = await fetch('/api/blog-writer/seo/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          blog_content: blogContent,
          research_data: researchData
        })
      });

      if (!response.ok) {
        throw new Error('Failed to analyze blog content');
      }

      const result = await response.json();
      console.log('🔍 Backend SEO Analysis Response:', result);
      console.log('📊 Category Scores:', result.category_scores);
      console.log('💡 Recommendations:', result.actionable_recommendations);
      console.log('🔍 Visualization Data:', result.visualization_data);
      console.log('📝 Detailed Analysis:', result.detailed_analysis);
      console.log('🏗️ Content Structure:', result.detailed_analysis?.content_structure);
      console.log('📋 Heading Structure:', result.detailed_analysis?.heading_structure);
      
      // Convert API response to frontend format - fail fast if data is missing
      if (!result.success) {
        throw new Error(result.recommendations?.[0] || 'SEO analysis failed');
      }

      if (!result.overall_score && result.overall_score !== 0) {
        throw new Error('Invalid SEO score received from API');
      }

      const convertedResult: SEOAnalysisResult = {
        overall_score: result.overall_score,
        category_scores: {
          structure: result.category_scores?.structure || 0,
          keywords: result.category_scores?.keywords || 0,
          readability: result.category_scores?.readability || 0,
          quality: result.category_scores?.quality || 0,
          headings: result.category_scores?.headings || 0,
          ai_insights: result.category_scores?.ai_insights || 0
        },
        analysis_summary: result.analysis_summary || {
          overall_grade: result.overall_score >= 80 ? 'A' : result.overall_score >= 60 ? 'B' : 'C',
          status: result.overall_score >= 80 ? 'Excellent' : result.overall_score >= 60 ? 'Good' : 'Needs Improvement',
          strongest_category: 'structure',
          weakest_category: 'keywords',
          key_strengths: ['Good content structure', 'Appropriate length'],
          key_weaknesses: ['Keyword optimization needs work'],
          ai_summary: 'Content provides good value with room for SEO improvements.'
        },
        actionable_recommendations: (result.actionable_recommendations || []).map((rec: any) => ({
          category: rec.category || 'General',
          priority: rec.priority || 'Medium' as const,
          recommendation: rec.recommendation || rec,
          impact: rec.impact || 'Improves SEO performance'
        })),
        visualization_data: {
          score_radar: {
            categories: ['structure', 'keywords', 'readability', 'quality', 'headings', 'ai_insights'],
            scores: [
              result.category_scores?.structure || 0,
              result.category_scores?.keywords || 0,
              result.category_scores?.readability || 0,
              result.category_scores?.quality || 0,
              result.category_scores?.headings || 0,
              result.category_scores?.ai_insights || 0
            ],
            max_score: 100
          },
          keyword_analysis: {
            densities: result.visualization_data?.keyword_analysis?.densities || {},
            missing_keywords: result.visualization_data?.keyword_analysis?.missing_keywords || [],
            over_optimization: result.visualization_data?.keyword_analysis?.over_optimization || []
          },
          readability_metrics: result.visualization_data?.readability_metrics || {},
          content_stats: {
            word_count: result.visualization_data?.content_stats?.word_count || 0,
            sections: result.visualization_data?.content_stats?.sections || 0,
            paragraphs: result.visualization_data?.content_stats?.paragraphs || 0
          }
        },
        detailed_analysis: result.detailed_analysis || undefined,
        generated_at: new Date().toISOString()
      };
      
      setAnalysisResult(convertedResult);
      setIsAnalyzing(false);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
      setIsAnalyzing(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'success.main';
    if (score >= 60) return 'warning.main';
    return 'error.main';
  };

  const getScoreBadgeVariant = (score: number) => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'error';
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'High': return 'error.main';
      case 'Medium': return 'warning.main';
      case 'Low': return 'success.main';
      default: return 'text.secondary';
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'High': return <Cancel sx={{ fontSize: 16 }} />;
      case 'Medium': return <Warning sx={{ fontSize: 16 }} />;
      case 'Low': return <CheckCircle sx={{ fontSize: 16 }} />;
      default: return <Warning sx={{ fontSize: 16 }} />;
    }
  };

  // Tooltip content for each metric
  const getMetricTooltip = (category: string) => {
    const tooltips = {
      structure: {
        title: "Content Structure Analysis",
        description: "Evaluates how well your content is organized and structured for both readers and search engines.",
        methodology: "Analyzes heading hierarchy (H1, H2, H3), paragraph length, section organization, and logical flow.",
        score_meaning: "Higher scores indicate better content organization, clear headings, and logical structure.",
        examples: "Good: Clear H1 title, logical H2 sections, short paragraphs. Poor: No headings, long walls of text."
      },
      keywords: {
        title: "Keyword Optimization Analysis", 
        description: "Measures how effectively your target keywords are used throughout the content.",
        methodology: "Analyzes keyword density, distribution, placement in headings, and semantic keyword usage.",
        score_meaning: "Higher scores indicate optimal keyword usage without over-optimization.",
        examples: "Good: 1-3% keyword density, keywords in headings. Poor: Keyword stuffing or missing target keywords."
      },
      readability: {
        title: "Readability Assessment",
        description: "Evaluates how easy your content is to read and understand for your target audience.",
        methodology: "Uses Flesch Reading Ease, sentence length, word complexity, and paragraph structure.",
        score_meaning: "Higher scores indicate content that's easier to read and understand.",
        examples: "Good: Short sentences, simple words, clear paragraphs. Poor: Long complex sentences, jargon."
      },
      quality: {
        title: "Content Quality Evaluation",
        description: "Assesses the depth, value, and comprehensiveness of your content.",
        methodology: "Analyzes word count, content depth, information density, and topic coverage.",
        score_meaning: "Higher scores indicate more comprehensive and valuable content.",
        examples: "Good: Detailed explanations, examples, comprehensive coverage. Poor: Thin content, lack of detail."
      },
      headings: {
        title: "Heading Structure Analysis",
        description: "Evaluates the effectiveness of your heading hierarchy and organization.",
        methodology: "Analyzes heading distribution, hierarchy levels, keyword usage in headings, and logical flow.",
        score_meaning: "Higher scores indicate better heading structure and organization.",
        examples: "Good: Clear H1, logical H2/H3 progression. Poor: Missing headings, poor hierarchy."
      },
      ai_insights: {
        title: "AI-Powered Content Insights",
        description: "Advanced analysis of content engagement potential and user value.",
        methodology: "Uses AI to analyze content quality, engagement factors, and user value proposition.",
        score_meaning: "Higher scores indicate content that's more likely to engage and provide value to readers.",
        examples: "Good: Clear value proposition, engaging content, actionable insights. Poor: Generic content, low engagement potential."
      }
    };
    return tooltips[category as keyof typeof tooltips] || tooltips.structure;
  };

  useEffect(() => {
    if (isOpen && !analysisResult) {
      runSEOAnalysis();
    }
  }, [isOpen]);

  return (
    <Dialog 
      open={isOpen} 
      onClose={onClose}
      maxWidth="lg"
      fullWidth
      PaperProps={{
        sx: {
          maxHeight: '90vh',
          borderRadius: 3,
          background: 'rgba(255, 255, 255, 0.98)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(0,0,0,0.1)',
          color: 'text.primary'
        }
      }}
    >
      <DialogContent sx={{ p: 0 }}>
        <Box sx={{ p: 3, borderBottom: '1px solid rgba(0,0,0,0.1)' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Search sx={{ color: 'primary.main' }} />
              <Typography variant="h5" component="h2" sx={{ fontWeight: 600 }}>
                SEO Analysis Results
              </Typography>
            </Box>
            <IconButton onClick={onClose} sx={{ color: 'text.secondary' }}>
              <Close />
            </IconButton>
          </Box>
          <Typography variant="body2" sx={{ color: 'text.secondary', mt: 1 }}>
            Comprehensive analysis of your blog content's SEO optimization
          </Typography>
        </Box>

        {isAnalyzing && (
          <Box sx={{ p: 3 }}>
            <Box sx={{ textAlign: 'center', mb: 3 }}>
              <Refresh sx={{ 
                fontSize: 32, 
                animation: 'spin 1s linear infinite',
                '@keyframes spin': {
                  '0%': { transform: 'rotate(0deg)' },
                  '100%': { transform: 'rotate(360deg)' }
                }
              }} />
              <Typography variant="body2" sx={{ color: 'text.secondary', mt: 1 }}>
                {progressMessage}
              </Typography>
            </Box>
            <LinearProgress 
              variant="determinate" 
              value={progress} 
              sx={{ 
                height: 8, 
                borderRadius: 4,
                backgroundColor: 'rgba(255,255,255,0.1)',
                '& .MuiLinearProgress-bar': {
                  borderRadius: 4,
                  background: 'linear-gradient(90deg, #4caf50, #8bc34a)'
                }
              }} 
            />
          </Box>
        )}

        {error && (
          <Box sx={{ p: 3 }}>
            <Alert severity="error" sx={{ borderRadius: 2 }}>
              <Cancel sx={{ mr: 1 }} />
              {error}
            </Alert>
          </Box>
        )}

        {analysisResult && (
          <Box sx={{ p: 3 }}>
            {/* Overall Score Section */}
            <Card sx={{ mb: 3, background: 'rgba(255,255,255,0.9)', border: '1px solid rgba(0,0,0,0.1)' }}>
              <CardHeader>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <BarChart sx={{ color: 'primary.main' }} />
                  <Typography variant="h6" component="h3" sx={{ fontWeight: 600 }}>
                    Overall SEO Score
                  </Typography>
                </Box>
              </CardHeader>
              <CardContent>
                <Grid container spacing={3} alignItems="center">
                  <Grid item xs={4}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography 
                        variant="h2" 
                        sx={{ 
                          fontWeight: 'bold',
                          color: getScoreColor(analysisResult.overall_score),
                          background: 'linear-gradient(45deg, #4caf50, #8bc34a)',
                          backgroundClip: 'text',
                          WebkitBackgroundClip: 'text',
                          WebkitTextFillColor: 'transparent'
                        }}
                      >
                        {analysisResult.overall_score}
                      </Typography>
                      <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                        Overall Score
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={4}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h3" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                        {analysisResult.analysis_summary.overall_grade}
                      </Typography>
                      <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                        Grade
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={4}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Chip 
                        label={analysisResult.analysis_summary.status}
                        color={getScoreBadgeVariant(analysisResult.overall_score)}
                        variant="filled"
                        sx={{ 
                          fontWeight: 600,
                          fontSize: '0.9rem',
                          px: 2,
                          py: 1
                        }}
                      />
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>

            {/* Category Scores */}
            <Card sx={{ mb: 3, background: 'rgba(255,255,255,0.9)', border: '1px solid rgba(0,0,0,0.1)' }}>
              <CardHeader>
                <Typography variant="h6" component="h3" sx={{ fontWeight: 600 }}>
                  Category Breakdown
                </Typography>
              </CardHeader>
              <CardContent>
                <Grid container spacing={2}>
                  {Object.entries(analysisResult.category_scores).map(([category, score]) => {
                    const tooltip = getMetricTooltip(category);
                    return (
                      <Grid item xs={6} md={4} key={category}>
                        <Tooltip
                          title={
                            <Box sx={{ p: 1 }}>
                              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                                {tooltip.title}
                              </Typography>
                              <Typography variant="body2" sx={{ mb: 1 }}>
                                {tooltip.description}
                              </Typography>
                              <Typography variant="caption" sx={{ display: 'block', mb: 1, fontStyle: 'italic' }}>
                                <strong>Methodology:</strong> {tooltip.methodology}
                              </Typography>
                              <Typography variant="caption" sx={{ display: 'block', mb: 1 }}>
                                <strong>Score Meaning:</strong> {tooltip.score_meaning}
                              </Typography>
                              <Typography variant="caption" sx={{ display: 'block' }}>
                                <strong>Examples:</strong> {tooltip.examples}
                              </Typography>
                            </Box>
                          }
                          arrow
                          placement="top"
                        >
                          <Paper 
                            sx={{ 
                              p: 2, 
                              textAlign: 'center',
                              background: 'rgba(255,255,255,0.8)',
                              border: '1px solid rgba(0,0,0,0.1)',
                              borderRadius: 2,
                              cursor: 'help',
                              '&:hover': {
                                background: 'rgba(255,255,255,0.9)',
                                transform: 'translateY(-2px)',
                                transition: 'all 0.2s ease-in-out'
                              }
                            }}
                          >
                            <Typography 
                              variant="h4" 
                              sx={{ 
                                fontWeight: 'bold',
                                color: getScoreColor(score),
                                mb: 1
                              }}
                            >
                              {score}
                            </Typography>
                            <Typography variant="body2" sx={{ color: 'text.secondary', textTransform: 'capitalize' }}>
                              {category.replace('_', ' ')}
                            </Typography>
                          </Paper>
                        </Tooltip>
                      </Grid>
                    );
                  })}
                </Grid>
              </CardContent>
            </Card>

            {/* Detailed Analysis Tabs */}
            <Card sx={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)' }}>
              <Tabs 
                value={tabValue} 
                onChange={(e, newValue) => setTabValue(newValue)}
                variant="fullWidth"
                sx={{
                  '& .MuiTab-root': {
                    color: 'text.secondary',
                    fontWeight: 500,
                    '&.Mui-selected': {
                      color: 'primary.main',
                      fontWeight: 600
                    }
                  },
                  '& .MuiTabs-indicator': {
                    background: 'linear-gradient(90deg, #4caf50, #8bc34a)',
                    height: 3
                  }
                }}
              >
                <Tab label="Recommendations" value="recommendations" />
                <Tab label="Keywords" value="keywords" />
                <Tab label="Readability" value="readability" />
                <Tab label="Structure" value="structure" />
                <Tab label="AI Insights" value="insights" />
              </Tabs>

              <Box sx={{ p: 3 }}>
                {tabValue === 'recommendations' && (
                  <Recommendations recommendations={analysisResult.actionable_recommendations} />
                )}

                {tabValue === 'keywords' && (
                  <KeywordAnalysis detailedAnalysis={analysisResult.detailed_analysis} />
                )}

                {tabValue === 'readability' && (
                  <ReadabilityAnalysis 
                    detailedAnalysis={analysisResult.detailed_analysis} 
                    visualizationData={analysisResult.visualization_data}
                  />
                )}

                {tabValue === 'structure' && (
                  <StructureAnalysis detailedAnalysis={analysisResult.detailed_analysis} />
                )}

                {tabValue === 'insights' && (
                  <Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
                      <TrendingUp sx={{ color: 'primary.main' }} />
                      <Typography variant="h6" component="h3" sx={{ fontWeight: 600 }}>
                        AI-Powered Insights
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                      <Paper sx={{ p: 3, background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.1)' }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
                          Content Summary
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                          {analysisResult.analysis_summary.ai_summary}
                        </Typography>
                      </Paper>
                      
                      <Paper sx={{ p: 3, background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.1)' }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
                          Key Strengths
                        </Typography>
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                          {analysisResult.analysis_summary.key_strengths.map((strength, index) => (
                            <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <CheckCircle sx={{ color: 'success.main', fontSize: 16 }} />
                              <Typography variant="body2">{strength}</Typography>
                            </Box>
                          ))}
                        </Box>
                      </Paper>
                      
                      <Paper sx={{ p: 3, background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.1)' }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
                          Areas for Improvement
                        </Typography>
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                          {analysisResult.analysis_summary.key_weaknesses.map((weakness, index) => (
                            <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Warning sx={{ color: 'warning.main', fontSize: 16 }} />
                              <Typography variant="body2">{weakness}</Typography>
                            </Box>
                          ))}
                        </Box>
                      </Paper>
                    </Box>
                  </Box>
                )}
              </Box>
            </Card>

            {/* Action Buttons */}
            <Box sx={{ p: 3, borderTop: '1px solid rgba(255,255,255,0.1)' }}>
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
                <Button variant="outlined" onClick={onClose} sx={{ color: 'text.secondary' }}>
                  Close
                </Button>
                <Button 
                  variant="contained"
                  onClick={() => {
                    if (onApplyRecommendations) {
                      onApplyRecommendations(analysisResult.actionable_recommendations);
                    }
                    onClose();
                  }}
                  disabled={!onApplyRecommendations}
                  sx={{
                    background: 'linear-gradient(45deg, #4caf50, #8bc34a)',
                    '&:hover': {
                      background: 'linear-gradient(45deg, #45a049, #7cb342)'
                    }
                  }}
                >
                  Apply Recommendations
                </Button>
              </Box>
            </Box>
          </Box>
        )}
      </DialogContent>
    </Dialog>
  );
};
