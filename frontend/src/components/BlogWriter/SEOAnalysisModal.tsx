/**
 * SEO Analysis Modal Component
 * 
 * Displays comprehensive SEO analysis results with visual charts and actionable recommendations.
 * Integrates with CopilotKit for real-time progress updates and user interactions.
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Dialog,
  DialogContent,
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
  IconButton,
  Tooltip,
  Avatar,
  CircularProgress
} from '@mui/material';
import { apiClient, triggerSubscriptionError } from '../../api/client';
import { 
  CheckCircle, 
  Cancel, 
  Warning, 
  TrendingUp, 
  Search,
  Refresh,
  Close
} from '@mui/icons-material';
import { KeywordAnalysis, ReadabilityAnalysis, StructureAnalysis, Recommendations } from './SEO';
import OverallScoreCard from './SEO/OverallScoreCard';

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
  blogTitle?: string;
  researchData: any;
  onApplyRecommendations?: (recommendations: SEOAnalysisResult['actionable_recommendations']) => Promise<void>;
  onAnalysisComplete?: (analysis: SEOAnalysisResult) => void;
}

// Simple content hashing helper (SHA-256)
async function hashContent(text: string): Promise<string> {
  try {
    const enc = new TextEncoder().encode(text);
    const digest = await crypto.subtle.digest('SHA-256', enc);
    const bytes = Array.from(new Uint8Array(digest));
    return bytes.map(b => b.toString(16).padStart(2, '0')).join('');
  } catch {
    // Fallback hash
    let h = 0;
    for (let i = 0; i < text.length; i++) h = (h * 31 + text.charCodeAt(i)) | 0;
    return String(h);
  }
}

function getSeoCacheKey(contentHash: string, title?: string) {
  return `seo_cache:${contentHash}:${title || ''}`;
}

export const SEOAnalysisModal: React.FC<SEOAnalysisModalProps> = ({
  isOpen,
  onClose,
  blogContent,
  blogTitle,
  researchData,
  onApplyRecommendations,
  onAnalysisComplete
}) => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<SEOAnalysisResult | null>(null);
  const [progress, setProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState('recommendations');
  const [contentHash, setContentHash] = useState<string>('');
  const [isApplying, setIsApplying] = useState(false);
  const [applyError, setApplyError] = useState<string | null>(null);

  // Debug logging only in development and when modal state changes meaningfully
  useEffect(() => {
    if (process.env.NODE_ENV === 'development' && isOpen) {
      console.log('SEOAnalysisModal render:', { isOpen, blogContent: blogContent?.length, researchData: !!researchData });
    }
  }, [isOpen, blogContent?.length, researchData]);

  const runSEOAnalysis = useCallback(async (forceRefresh = false) => {
    // Prevent multiple simultaneous calls
    if (isAnalyzing && !forceRefresh) {
      console.log('⏸️ SEO analysis already in progress, skipping duplicate call');
      return;
    }

    try {
      setIsAnalyzing(true);
      setError(null);
      setProgress(0);
      setProgressMessage('Checking cache for previous SEO analysis...');

      // Cache check - always check cache first unless force refresh is requested
      // Compute hash if not already available
      let hash = contentHash;
      if (!hash) {
        hash = await hashContent(`${blogTitle || ''}\n${blogContent}`);
        // Update state for future use
        setContentHash(hash);
      }
      const cacheKey = getSeoCacheKey(hash, blogTitle);
      console.log('🔍 Checking SEO cache', { 
        cacheKey, 
        hasHash: !!hash, 
        forceRefresh,
        hashLength: hash?.length,
        titleLength: blogTitle?.length,
        contentLength: blogContent?.length
      });
      
      if (!forceRefresh) {
        const cached = typeof window !== 'undefined' ? window.localStorage.getItem(cacheKey) : null;
        if (cached) {
          try {
            const parsed = JSON.parse(cached) as SEOAnalysisResult;
            // Validate cached data has required fields
            if (parsed && typeof parsed.overall_score === 'number' && parsed.category_scores) {
              console.log('✅ Using cached SEO analysis', { cacheKey, overall_score: parsed.overall_score });
              setAnalysisResult(parsed);
              setIsAnalyzing(false);
              setProgress(100);
              setProgressMessage('SEO analysis loaded from cache');
              // Notify parent that analysis is complete (from cache)
              if (onAnalysisComplete) {
                onAnalysisComplete(parsed);
              }
              return;
            } else {
              console.warn('⚠️ Cached SEO analysis data is invalid, will fetch fresh analysis');
            }
          } catch (parseError) {
            console.warn('⚠️ Failed to parse cached SEO analysis, will fetch fresh analysis', parseError);
            // Remove invalid cache entry
            if (typeof window !== 'undefined') {
              window.localStorage.removeItem(cacheKey);
            }
          }
        } else {
          console.log('ℹ️ No cached SEO analysis found, will fetch from API', { cacheKey });
        }
      } else {
        console.log('🔄 Force refresh requested, skipping cache check');
      }

      setProgressMessage('Starting SEO analysis...');

      // Simulated progress
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

      // Backend call
      const response = await apiClient.post('/api/blog-writer/seo/analyze', {
        blog_content: blogContent,
        blog_title: blogTitle,
        research_data: researchData
      });

      const result = response.data;
      console.log('🔍 Backend SEO Analysis Response:', result);
      if (!result.success) throw new Error(result.recommendations?.[0] || 'SEO analysis failed');
      if (!result.overall_score && result.overall_score !== 0) throw new Error('Invalid SEO score received from API');

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

      // Save to cache - use the same cacheKey that was used for checking
      try {
        // Use the same hash and cacheKey from the cache check section
        // This ensures consistency between cache check and save
        if (typeof window !== 'undefined' && cacheKey) {
          window.localStorage.setItem(cacheKey, JSON.stringify(convertedResult));
          console.log('💾 SEO analysis cached', { cacheKey, overall_score: convertedResult.overall_score });
        }
      } catch (cacheError) {
        console.warn('⚠️ Failed to cache SEO analysis', cacheError);
      }

      setIsAnalyzing(false);

      // Notify parent that analysis is complete (fresh analysis)
      if (onAnalysisComplete) {
        onAnalysisComplete(convertedResult);
      }

    } catch (err: any) {
      console.error('SEO analysis failed:', err);
      
      // Check if this is a subscription error (429/402) and trigger global subscription modal
      const status = err?.response?.status;
      if (status === 429 || status === 402) {
        console.log('SEOAnalysisModal: Detected subscription error, triggering global handler', {
          status,
          data: err?.response?.data
        });
        const handled = await triggerSubscriptionError(err);
        if (handled) {
          console.log('SEOAnalysisModal: Global subscription error handler triggered successfully');
          // Don't set local error - let the global modal handle it
          setIsAnalyzing(false);
          return;
        } else {
          console.warn('SEOAnalysisModal: Global subscription error handler did not handle the error');
        }
      }
      
      // For non-subscription errors, show local error message
      setError(err instanceof Error ? err.message : 'Analysis failed');
      setIsAnalyzing(false);
    }
  }, [blogContent, blogTitle, researchData, contentHash, onAnalysisComplete]);

  // Precompute hash when modal opens and trigger cache check
  // Use a ref to prevent multiple simultaneous calls
  const hasRunAnalysisRef = React.useRef(false);
  useEffect(() => {
    if (isOpen && !hasRunAnalysisRef.current) {
      hasRunAnalysisRef.current = true;
      (async () => {
        const h = await hashContent(`${blogTitle || ''}\n${blogContent}`);
        setContentHash(h);
        // After hash is computed, check cache if we don't have analysis result yet
        if (!analysisResult) {
          // Small delay to ensure hash is set in state
          setTimeout(() => {
            runSEOAnalysis();
          }, 100);
        }
      })();
    } else if (!isOpen) {
      // Reset hash and flag when modal closes
      setContentHash('');
      hasRunAnalysisRef.current = false;
    }
  }, [isOpen, blogContent, blogTitle, analysisResult, runSEOAnalysis]);

  // Fallback: if modal opens and hash is already computed, check cache immediately
  useEffect(() => {
    if (isOpen && !analysisResult && contentHash && !hasRunAnalysisRef.current) {
      hasRunAnalysisRef.current = true;
      runSEOAnalysis();
    }
  }, [isOpen, analysisResult, contentHash, runSEOAnalysis]);

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'success.main';
    if (score >= 60) return 'warning.main';
    return 'error.main';
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
          backgroundColor: '#f8fafc',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(148,163,184,0.25)',
          color: '#0f172a'
        }
      }}
    >
      <DialogContent sx={{ p: 0, color: '#0f172a' }}>
        <Box sx={{ p: 3, borderBottom: '1px solid rgba(0,0,0,0.1)' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Search sx={{ color: 'primary.main' }} />
              <Typography variant="h5" component="h2" sx={{ fontWeight: 600 }}>
                SEO Analysis Results
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Button
                variant="outlined"
                size="small"
                startIcon={<Refresh />}
                onClick={() => {
                  setAnalysisResult(null);
                  runSEOAnalysis(true);
                }}
              >
                Refresh
              </Button>
              <IconButton onClick={onClose} sx={{ color: 'text.secondary' }}>
                <Close />
              </IconButton>
            </Box>
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
            <OverallScoreCard
              overallScore={analysisResult.overall_score}
              overallGrade={analysisResult.analysis_summary.overall_grade}
              statusLabel={analysisResult.analysis_summary.status}
              categoryScores={analysisResult.category_scores}
              getMetricTooltip={getMetricTooltip}
              getScoreColor={getScoreColor}
            />

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
                  analysisResult ? (
                    <StructureAnalysis detailedAnalysis={analysisResult.detailed_analysis} />
                  ) : (
                    <Box sx={{ p: 3, textAlign: 'center' }}>
                      <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                        Loading structure analysis...
                      </Typography>
                    </Box>
                  )
                )}

                {tabValue === 'insights' && (
                  <Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
                      <TrendingUp sx={{ color: 'primary.main' }} />
                      <Typography variant="h6" component="h3" sx={{ fontWeight: 700, color: '#0f172a' }}>
                        AI-Powered Insights
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                      <Paper sx={{ p: 3, backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: 3, boxShadow: '0 12px 28px rgba(15,23,42,0.08)', color: '#0f172a' }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 1.5 }}>
                          Content Summary
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#475569', lineHeight: 1.6 }}>
                          {analysisResult.analysis_summary.ai_summary}
                        </Typography>
                      </Paper>
                      <Paper sx={{ p: 3, backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: 3, boxShadow: '0 12px 28px rgba(15,23,42,0.08)', color: '#0f172a' }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 1.5 }}>
                          Key Strengths
                        </Typography>
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                          {analysisResult.analysis_summary.key_strengths.map((strength, index) => (
                            <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <CheckCircle sx={{ color: 'success.main', fontSize: 16 }} />
                              <Typography variant="body2" sx={{ color: '#1f2937' }}>{strength}</Typography>
                            </Box>
                          ))}
                        </Box>
                      </Paper>
                      <Paper sx={{ p: 3, backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: 3, boxShadow: '0 12px 28px rgba(15,23,42,0.08)', color: '#0f172a' }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 1.5 }}>
                          Areas for Improvement
                        </Typography>
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                          {analysisResult.analysis_summary.key_weaknesses.map((weakness, index) => (
                            <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Warning sx={{ color: 'warning.main', fontSize: 16 }} />
                              <Typography variant="body2" sx={{ color: '#1f2937' }}>{weakness}</Typography>
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
              {applyError && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  <Cancel sx={{ mr: 1 }} />
                  {applyError}
                </Alert>
              )}
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
                <Button variant="outlined" onClick={onClose} sx={{ color: 'text.secondary' }} disabled={isApplying}>
                  Close
                </Button>
                <Button 
                  variant="contained"
                  onClick={async () => {
                    if (!onApplyRecommendations) return;
                    setApplyError(null);
                    setIsApplying(true);
                    try {
                      await onApplyRecommendations(analysisResult.actionable_recommendations);
                      // Increased delay to ensure sections are fully updated and phase stays in SEO
                      setTimeout(() => {
                        onClose();
                      }, 200);
                    } catch (applyErr: any) {
                      setApplyError(applyErr?.message || 'Failed to apply recommendations.');
                    } finally {
                      setIsApplying(false);
                    }
                  }}
                  disabled={!onApplyRecommendations || isApplying}
                  sx={{
                    background: 'linear-gradient(45deg, #4caf50, #8bc34a)',
                    '&:hover': {
                      background: 'linear-gradient(45deg, #45a049, #7cb342)'
                    }
                  }}
                >
                  {isApplying ? (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <CircularProgress size={16} color="inherit" />
                      Applying...
                    </Box>
                  ) : (
                    'Apply Recommendations'
                  )}
                </Button>
              </Box>
            </Box>
          </Box>
        )}
      </DialogContent>
    </Dialog>
  );
};
