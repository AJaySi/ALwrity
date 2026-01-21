/**
 * Prospect Analysis Panel - Ported from Legacy Backlinker
 *
 * AI-powered domain analysis with DA scores, confidence ratings,
 * contact information, and opportunity assessment.
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Box,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Button,
  Chip,
  Avatar,
  Grid,
  Badge,
  IconButton,
  LinearProgress,
  Tooltip,
  useTheme,
  alpha,
} from '@mui/material';
import {
  Public as GlobeIcon,
  SmartToy as BrainIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ClockIcon,
  Warning as AlertCircleIcon,
  Visibility as EyeIcon,
  People as UsersIcon,
  Analytics as BarChartIcon,
  Email as EmailIcon,
  Business as BusinessIcon,
  TrendingUp as TrendingUpIcon,
  ExpandMore as ExpandMoreIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { BacklinkingStyles } from './styles/backlinkingStyles';

// Prospecting Transparency Details Component
const ProspectingTransparencyDetails: React.FC<{ prospect: ProspectData }> = ({ prospect }) => {
  if (!prospect.prospectingContext) return null;

  const { campaign, discovery, performance } = prospect.prospectingContext;

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      {/* Campaign Context */}
      <Box>
        <Typography variant="caption" sx={{
          color: '#F1F5F9',
          fontSize: '0.75rem',
          fontWeight: 600,
          mb: 1,
          display: 'flex',
          alignItems: 'center',
          gap: 0.5
        }}>
          🎯 Campaign Context
        </Typography>
        <Box sx={{ pl: 1, borderLeft: '2px solid rgba(96, 165, 250, 0.3)', ml: 1 }}>
          <Typography variant="caption" sx={{ color: '#94A3B8', fontSize: '0.7rem', display: 'block' }}>
            Keywords: {campaign.keywords.join(', ')}
          </Typography>
          <Typography variant="caption" sx={{ color: '#94A3B8', fontSize: '0.7rem', display: 'block' }}>
            Industry: {campaign.industry}
          </Typography>
          <Typography variant="caption" sx={{ color: '#94A3B8', fontSize: '0.7rem', display: 'block' }}>
            Mode: {campaign.aiEnhanced ? '🤖 AI Enhanced' : '⚡ Programmatic'}
          </Typography>
        </Box>
      </Box>

      {/* Discovery Journey */}
      <Box>
        <Typography variant="caption" sx={{
          color: '#F1F5F9',
          fontSize: '0.75rem',
          fontWeight: 600,
          mb: 1,
          display: 'flex',
          alignItems: 'center',
          gap: 0.5
        }}>
          🚀 Discovery Journey
        </Typography>

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, pl: 1 }}>
          {/* Phase 1 */}
          <Box sx={{
            p: 1,
            bgcolor: 'rgba(16, 185, 129, 0.1)',
            border: '1px solid rgba(16, 185, 129, 0.2)',
            borderRadius: 1
          }}>
            <Typography variant="caption" sx={{ color: '#10B981', fontSize: '0.7rem', fontWeight: 600 }}>
              Phase 1: Query Generation
            </Typography>
            <Typography variant="caption" sx={{ color: '#94A3B8', fontSize: '0.65rem', display: 'block' }}>
              Generated {discovery.phase1.totalQueries} queries across {Object.keys(discovery.phase1.queryCategories).length} categories
            </Typography>
            <Typography variant="caption" sx={{ color: '#94A3B8', fontSize: '0.65rem', display: 'block' }}>
              Categories: {Object.entries(discovery.phase1.queryCategories).map(([cat, count]) => `${cat}(${count})`).join(', ')}
            </Typography>
          </Box>

          {/* Phase 2 */}
          <Box sx={{
            p: 1,
            bgcolor: 'rgba(96, 165, 250, 0.1)',
            border: '1px solid rgba(96, 165, 250, 0.2)',
            borderRadius: 1
          }}>
            <Typography variant="caption" sx={{ color: '#60A5FA', fontSize: '0.7rem', fontWeight: 600 }}>
              Phase 2: API Search
            </Typography>
            <Typography variant="caption" sx={{ color: '#94A3B8', fontSize: '0.65rem', display: 'block' }}>
              {discovery.phase2.apiCalls.exa + discovery.phase2.apiCalls.tavily} API calls ({discovery.phase2.apiCalls.exa} Exa, {discovery.phase2.apiCalls.tavily} Tavily)
            </Typography>
            <Typography variant="caption" sx={{ color: '#94A3B8', fontSize: '0.65rem', display: 'block' }}>
              Found {discovery.phase2.totalResults} raw results in {discovery.phase2.executionTime}s
            </Typography>
          </Box>

          {/* Phase 3 */}
          <Box sx={{
            p: 1,
            bgcolor: 'rgba(251, 191, 36, 0.1)',
            border: '1px solid rgba(251, 191, 36, 0.2)',
            borderRadius: 1
          }}>
            <Typography variant="caption" sx={{ color: '#D97706', fontSize: '0.7rem', fontWeight: 600 }}>
              Phase 3: Processing & Deduplication
            </Typography>
            <Typography variant="caption" sx={{ color: '#94A3B8', fontSize: '0.65rem', display: 'block' }}>
              Processed {discovery.phase3.processedResults} unique results
            </Typography>
            <Typography variant="caption" sx={{ color: '#94A3B8', fontSize: '0.65rem', display: 'block' }}>
              Deduplication: {(discovery.phase3.deduplicationRatio * 100).toFixed(1)}% of raw results retained
            </Typography>
          </Box>

          {/* Phase 4 */}
          <Box sx={{
            p: 1,
            bgcolor: 'rgba(168, 85, 247, 0.1)',
            border: '1px solid rgba(168, 85, 247, 0.2)',
            borderRadius: 1
          }}>
            <Typography variant="caption" sx={{ color: '#A855F7', fontSize: '0.7rem', fontWeight: 600 }}>
              Phase 4: Quality Analysis
            </Typography>
            <Typography variant="caption" sx={{ color: '#94A3B8', fontSize: '0.65rem', display: 'block' }}>
              Conversion rate: {(discovery.phase4.conversionRate * 100).toFixed(1)}% (quality threshold: {discovery.phase4.qualityThreshold})
            </Typography>
            <Typography variant="caption" sx={{ color: '#94A3B8', fontSize: '0.65rem', display: 'block' }}>
              This prospect met our quality standards and was selected
            </Typography>
          </Box>
        </Box>
      </Box>

      {/* Performance Context */}
      <Box>
        <Typography variant="caption" sx={{
          color: '#F1F5F9',
          fontSize: '0.75rem',
          fontWeight: 600,
          mb: 1,
          display: 'flex',
          alignItems: 'center',
          gap: 0.5
        }}>
          📊 Performance Context
        </Typography>
        <Box sx={{ pl: 1, borderLeft: '2px solid rgba(168, 85, 247, 0.3)', ml: 1 }}>
          <Typography variant="caption" sx={{ color: '#94A3B8', fontSize: '0.7rem', display: 'block' }}>
            Overall conversion rate: {(performance.overallConversionRate * 100).toFixed(1)}%
          </Typography>
          <Typography variant="caption" sx={{ color: '#94A3B8', fontSize: '0.7rem', display: 'block' }}>
            Category performance: {Object.entries(performance.categoryPerformance)
              .map(([cat, score]) => `${cat}(${(score * 100).toFixed(0)}%)`)
              .join(', ')}
          </Typography>
          <Typography variant="caption" sx={{ color: '#94A3B8', fontSize: '0.7rem', display: 'block' }}>
            Efficiency: {performance.timeEfficiency}% time utilization, ${(performance.costEfficiency * 100).toFixed(2)} per opportunity
          </Typography>
        </Box>
      </Box>

      {/* Content Gap Analysis */}
      {prospect.contentGapAnalysis && (
        <Box>
          <Typography variant="caption" sx={{
            color: '#F1F5F9',
            fontSize: '0.75rem',
            fontWeight: 600,
            mb: 1,
            display: 'flex',
            alignItems: 'center',
            gap: 0.5
          }}>
            🎯 Content Opportunity
          </Typography>
          <Box sx={{ pl: 1, borderLeft: '2px solid rgba(16, 185, 129, 0.3)', ml: 1 }}>
            <Typography variant="caption" sx={{ color: '#94A3B8', fontSize: '0.7rem', display: 'block' }}>
              Target topics: {prospect.contentGapAnalysis.targetTopics.join(', ')}
            </Typography>
            <Typography variant="caption" sx={{ color: '#94A3B8', fontSize: '0.7rem', display: 'block' }}>
              Opportunity score: {(prospect.contentGapAnalysis.opportunityScore * 100).toFixed(1)}%
            </Typography>
            <Typography variant="caption" sx={{ color: '#94A3B8', fontSize: '0.65rem', display: 'block', fontStyle: 'italic' }}>
              "{prospect.contentGapAnalysis.rationale}"
            </Typography>
          </Box>
        </Box>
      )}

      {/* AI Analysis Log */}
      {prospect.aiAnalysisLog && prospect.discoveryMethod === 'ai_enhanced' && (
        <Box>
          <Typography variant="caption" sx={{
            color: '#F1F5F9',
            fontSize: '0.75rem',
            fontWeight: 600,
            mb: 1,
            display: 'flex',
            alignItems: 'center',
            gap: 0.5
          }}>
            🤖 AI Analysis Details
          </Typography>
          <Box sx={{ pl: 1, borderLeft: '2px solid rgba(168, 85, 247, 0.3)', ml: 1 }}>
            <Typography variant="caption" sx={{ color: '#94A3B8', fontSize: '0.7rem', display: 'block' }}>
              Model: {prospect.aiAnalysisLog.aiModelUsed} | Analyzed: {new Date(prospect.aiAnalysisLog.analysisTimestamp).toLocaleString()}
            </Typography>
            <Typography variant="caption" sx={{ color: '#94A3B8', fontSize: '0.7rem', display: 'block' }}>
              Context provided: {prospect.aiAnalysisLog.contextProvided.join(', ')}
            </Typography>
            <Typography variant="caption" sx={{ color: '#94A3B8', fontSize: '0.7rem', display: 'block' }}>
              Decision factors: {prospect.aiAnalysisLog.decisionFactors.join(', ')}
            </Typography>
            <Box sx={{ mt: 0.5 }}>
              <Typography variant="caption" sx={{ color: '#94A3B8', fontSize: '0.7rem', display: 'block', mb: 0.5 }}>
                Confidence breakdown:
              </Typography>
              {Object.entries(prospect.aiAnalysisLog.confidenceBreakdown).map(([factor, score]) => (
                <Typography key={factor} variant="caption" sx={{ color: '#94A3B8', fontSize: '0.65rem', display: 'block', ml: 1 }}>
                  {factor.replace('_', ' ')}: {(score * 100).toFixed(0)}%
                </Typography>
              ))}
            </Box>
          </Box>
        </Box>
      )}
    </Box>
  );
};

interface ProspectData {
  id: string;
  domain: string;
  da: number; // Domain Authority
  status: 'analyzed' | 'pending' | 'reviewing' | 'qualified' | 'contacted';
  opportunity: string;
  confidence: number; // AI confidence score 0-100
  contact?: string;
  contactEmail?: string;
  contactName?: string;
  contentQuality?: number;
  backlinkPotential?: number;
  spamRisk?: number;
  lastAnalyzed?: string;
  aiRecommendation?: string;
  // Transparency fields
  discoveryMethod?: 'programmatic' | 'ai_enhanced';
  queryUsed?: string;
  apiSource?: 'exa' | 'tavily';
  searchPhase?: 'probing' | 'expansion';
  semanticMatchScore?: number;
  industryRelevance?: number;
  prospectingContext?: {
    campaign: {
      keywords: string[];
      industry: string;
      aiEnhanced: boolean;
    };
    discovery: {
      phase1: { queryCategories: Record<string, number>; totalQueries: number };
      phase2: { apiCalls: Record<string, number>; totalResults: number; executionTime: number };
      phase3: { processedResults: number; deduplicationRatio: number };
      phase4: { conversionRate: number; qualityThreshold: number };
    };
    performance: {
      overallConversionRate: number;
      categoryPerformance: Record<string, number>;
      timeEfficiency: number;
      costEfficiency: number;
    };
  };
  contentGapAnalysis?: {
    targetTopics: string[];
    competitorCoverage: Record<string, number>;
    opportunityScore: number;
    rationale: string;
  };
  aiAnalysisLog?: {
    aiModelUsed: string;
    analysisTimestamp: string;
    contextProvided: string[];
    decisionFactors: string[];
    confidenceBreakdown: Record<string, number>;
    alternativeConsiderations: string[];
  };
}

const sampleProspects: ProspectData[] = [
  {
    id: '1',
    domain: 'techcrunch.com',
    da: 94,
    status: 'analyzed',
    opportunity: 'Guest Post',
    confidence: 92,
    contact: 'editor@techcrunch.com',
    contactEmail: 'editor@techcrunch.com',
    contactName: 'TechCrunch Editor',
    contentQuality: 95,
    backlinkPotential: 88,
    spamRisk: 5,
    lastAnalyzed: '2024-01-15',
    aiRecommendation: 'High-value target with strong editorial standards',
    discoveryMethod: 'ai_enhanced',
    queryUsed: '"guest post" AI technology intitle:"write for us"',
    apiSource: 'exa',
    searchPhase: 'probing',
    semanticMatchScore: 0.92,
    industryRelevance: 0.95,
    prospectingContext: {
      campaign: {
        keywords: ['AI', 'technology', 'machine learning'],
        industry: 'technology',
        aiEnhanced: true
      },
      discovery: {
        phase1: { queryCategories: { semantic: 15, industry: 12, operators: 10, authority: 5, fresh: 3 }, totalQueries: 45 },
        phase2: { apiCalls: { exa: 25, tavily: 20 }, totalResults: 234, executionTime: 12.5 },
        phase3: { processedResults: 156, deduplicationRatio: 0.67 },
        phase4: { conversionRate: 0.077, qualityThreshold: 0.8 }
      },
      performance: {
        overallConversionRate: 0.077,
        categoryPerformance: { semantic: 0.85, industry: 0.80, operators: 0.75 },
        timeEfficiency: 85,
        costEfficiency: 0.032
      }
    },
    contentGapAnalysis: {
      targetTopics: ['AI ethics', 'machine learning trends', 'technology innovation'],
      competitorCoverage: { 'venturebeat.com': 0.85, 'techcrunch.com': 0.92, 'wired.com': 0.78 },
      opportunityScore: 0.88,
      rationale: 'Strong content gap in AI ethics discussions, competitor coverage shows opportunity'
    },
    aiAnalysisLog: {
      aiModelUsed: 'gemini-pro',
      analysisTimestamp: '2024-01-15T10:35:00Z',
      contextProvided: ['campaign_keywords', 'industry_focus', 'search_performance', 'competitor_analysis'],
      decisionFactors: ['high_domain_authority', 'content_quality', 'semantic_relevance', 'guest_post_signals'],
      confidenceBreakdown: {
        domain_authority: 0.95,
        content_quality: 0.90,
        semantic_match: 0.92,
        guest_post_signals: 0.88
      },
      alternativeConsiderations: ['competitor_saturation', 'editorial_focus_alignment', 'publication_frequency']
    }
  },
  {
    id: '2',
    domain: 'contentmarketing.org',
    da: 78,
    status: 'pending',
    opportunity: 'Resource Link',
    confidence: 85,
    contact: 'info@contentmarketing.org',
    contactEmail: 'info@contentmarketing.org',
    contentQuality: 82,
    backlinkPotential: 76,
    spamRisk: 8,
    lastAnalyzed: '2024-01-14',
    aiRecommendation: 'Good authority, focus on resource pages',
  },
  {
    id: '3',
    domain: 'aitrends.net',
    da: 65,
    status: 'reviewing',
    opportunity: 'Case Study',
    confidence: 78,
    contact: 'submissions@aitrends.net',
    contactEmail: 'submissions@aitrends.net',
    contentQuality: 75,
    backlinkPotential: 68,
    spamRisk: 12,
    lastAnalyzed: '2024-01-13',
    aiRecommendation: 'Emerging site with AI focus - monitor growth',
  },
  {
    id: '4',
    domain: 'marketingland.com',
    da: 88,
    status: 'analyzed',
    opportunity: 'Expert Quote',
    confidence: 88,
    contact: 'news@marketingland.com',
    contactEmail: 'news@marketingland.com',
    contactName: 'Marketing Land News',
    contentQuality: 87,
    backlinkPotential: 82,
    spamRisk: 6,
    lastAnalyzed: '2024-01-12',
    aiRecommendation: 'Excellent for expert contributions',
  },
  {
    id: '5',
    domain: 'searchengineland.com',
    da: 91,
    status: 'qualified',
    opportunity: 'Sponsored Content',
    confidence: 94,
    contact: 'sponsorships@searchengineland.com',
    contactEmail: 'sponsorships@searchengineland.com',
    contentQuality: 92,
    backlinkPotential: 89,
    spamRisk: 4,
    lastAnalyzed: '2024-01-11',
    aiRecommendation: 'Premium opportunity for sponsored placements',
  },
  {
    id: '6',
    domain: 'moz.com',
    da: 89,
    status: 'contacted',
    opportunity: 'Resource Page',
    confidence: 91,
    contact: 'content@moz.com',
    contactEmail: 'content@moz.com',
    contentQuality: 94,
    backlinkPotential: 85,
    spamRisk: 3,
    lastAnalyzed: '2024-01-10',
    aiRecommendation: 'Industry leader - focus on educational content',
  },
];

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'analyzed':
      return <CheckCircleIcon sx={{ fontSize: 16, color: '#10B981' }} />;
    case 'pending':
      return <ClockIcon sx={{ fontSize: 16, color: '#F59E0B' }} />;
    case 'reviewing':
      return <AlertCircleIcon sx={{ fontSize: 16, color: '#3B82F6' }} />;
    case 'qualified':
      return <TrendingUpIcon sx={{ fontSize: 16, color: '#8B5CF6' }} />;
    case 'contacted':
      return <EmailIcon sx={{ fontSize: 16, color: '#06B6D4' }} />;
    default:
      return <GlobeIcon sx={{ fontSize: 16 }} />;
  }
};

const getStatusColor = (status: string) => {
  switch (status) {
    case 'analyzed': return '#10B981';
    case 'pending': return '#F59E0B';
    case 'reviewing': return '#3B82F6';
    case 'qualified': return '#8B5CF6';
    case 'contacted': return '#06B6D4';
    default: return '#6B7280';
  }
};

const getDAColor = (da: number) => {
  if (da >= 90) return '#10B981'; // High authority - green
  if (da >= 70) return '#F59E0B'; // Good authority - amber
  if (da >= 50) return '#F97316'; // Medium authority - orange
  return '#EF4444'; // Low authority - red
};

const getConfidenceColor = (confidence: number) => {
  if (confidence >= 90) return '#10B981';
  if (confidence >= 80) return '#84CC16';
  if (confidence >= 70) return '#F59E0B';
  return '#EF4444';
};

interface ProspectCardProps {
  prospect: ProspectData;
  onViewDetails?: (prospect: ProspectData) => void;
  onContact?: (prospect: ProspectData) => void;
}

const ProspectCard: React.FC<ProspectCardProps> = ({ prospect, onViewDetails, onContact }) => {
  const theme = useTheme();

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={{ scale: 1.02, y: -2 }}
    >
      <Card
        sx={{
          background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(51, 65, 85, 0.8) 100%)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: 2,
          cursor: 'pointer',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          position: 'relative',
          overflow: 'hidden',
          '&:hover': {
            boxShadow: '0 8px 25px rgba(96, 165, 250, 0.2)',
            borderColor: 'rgba(96, 165, 250, 0.3)',
          },
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: `radial-gradient(circle at 30% 30%, ${alpha(getConfidenceColor(prospect.confidence), 0.08)} 0%, transparent 70%)`,
            pointerEvents: 'none',
          },
        }}
        onClick={() => onViewDetails?.(prospect)}
      >
        <CardContent sx={{ p: 2, position: 'relative', zIndex: 1 }}>
          {/* Header */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1.5 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              {getStatusIcon(prospect.status)}
              <Box>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#F1F5F9', fontSize: '0.9rem' }}>
                  {prospect.domain}
                </Typography>
                <Typography variant="caption" sx={{ color: 'rgba(203, 213, 225, 0.7)' }}>
                  {prospect.opportunity}
                </Typography>
              </Box>
            </Box>
            <Chip
              label={`DA ${prospect.da}`}
              size="small"
              sx={{
                backgroundColor: alpha(getDAColor(prospect.da), 0.1),
                color: getDAColor(prospect.da),
                border: `1px solid ${alpha(getDAColor(prospect.da), 0.3)}`,
                fontSize: '0.7rem',
                fontWeight: 600,
              }}
            />
          </Box>

          {/* Metrics Grid */}
          <Grid container spacing={2} sx={{ mb: 1.5 }}>
            <Grid item xs={6}>
              <Box sx={{ textAlign: 'center', p: 1, backgroundColor: 'rgba(30, 41, 59, 0.6)', borderRadius: 1 }}>
                <Typography variant="h6" sx={{ fontWeight: 700, color: getConfidenceColor(prospect.confidence), fontSize: '1rem' }}>
                  {prospect.confidence}%
                </Typography>
                <Typography variant="caption" sx={{ color: 'rgba(203, 213, 225, 0.7)', fontSize: '0.7rem' }}>
                  AI Score
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6}>
              <Box sx={{ textAlign: 'center', p: 1, backgroundColor: 'rgba(30, 41, 59, 0.6)', borderRadius: 1 }}>
                <Typography variant="h6" sx={{ fontWeight: 700, color: '#60A5FA', fontSize: '1rem' }}>
                  {prospect.backlinkPotential || 0}%
                </Typography>
                <Typography variant="caption" sx={{ color: 'rgba(203, 213, 225, 0.7)', fontSize: '0.7rem' }}>
                  Potential
                </Typography>
              </Box>
            </Grid>
          </Grid>

          {/* Contact Info */}
          {prospect.contactEmail && (
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <EmailIcon sx={{ fontSize: 14, color: 'rgba(203, 213, 225, 0.7)' }} />
                <Typography variant="caption" sx={{ color: 'rgba(203, 213, 225, 0.8)', fontSize: '0.75rem' }}>
                  {prospect.contactEmail}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', gap: 0.5 }}>
                <Tooltip title="View Details">
                  <IconButton
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation();
                      onViewDetails?.(prospect);
                    }}
                    sx={{
                      color: '#60A5FA',
                      '&:hover': {
                        backgroundColor: 'rgba(96, 165, 250, 0.1)',
                      },
                    }}
                  >
                    <EyeIcon sx={{ fontSize: 14 }} />
                  </IconButton>
                </Tooltip>
                {prospect.contactEmail && (
                  <Tooltip title="Contact Prospect">
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        onContact?.(prospect);
                      }}
                      sx={{
                        color: '#10B981',
                        '&:hover': {
                          backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        },
                      }}
                    >
                      <EmailIcon sx={{ fontSize: 14 }} />
                    </IconButton>
                  </Tooltip>
                )}
              </Box>
            </Box>
          )}

          {/* AI Recommendation */}
          {prospect.aiRecommendation && (
            <Box sx={{
              mt: 1,
              p: 1,
              backgroundColor: 'rgba(96, 165, 250, 0.05)',
              border: '1px solid rgba(96, 165, 250, 0.2)',
              borderRadius: 1,
            }}>
              <Typography variant="caption" sx={{ color: '#60A5FA', fontSize: '0.7rem', lineHeight: 1.3 }}>
                🤖 {prospect.aiRecommendation}
              </Typography>
            </Box>
          )}

          {/* Prospecting Transparency */}
          {prospect.prospectingContext && (
            <Accordion
              sx={{
                mt: 1,
                backgroundColor: 'rgba(30, 41, 59, 0.5)',
                border: '1px solid rgba(96, 165, 250, 0.2)',
                borderRadius: 1,
                '&:before': { display: 'none' },
                '&.Mui-expanded': {
                  backgroundColor: 'rgba(30, 41, 59, 0.7)',
                }
              }}
            >
              <AccordionSummary
                expandIcon={<ExpandMoreIcon sx={{ color: '#60A5FA', fontSize: 16 }} />}
                sx={{
                  minHeight: 32,
                  '& .MuiAccordionSummary-content': { my: 0.5 },
                  '&:hover': {
                    backgroundColor: 'rgba(96, 165, 250, 0.05)',
                  }
                }}
              >
                <Typography variant="caption" sx={{
                  color: '#60A5FA',
                  fontSize: '0.7rem',
                  fontWeight: 600,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 0.5
                }}>
                  🔍 How we found this prospect
                </Typography>
              </AccordionSummary>
              <AccordionDetails sx={{ pt: 0, pb: 1 }}>
                <ProspectingTransparencyDetails prospect={prospect} />
              </AccordionDetails>
            </Accordion>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
};

interface ProspectAnalysisPanelProps {
  campaignId?: string;
  onProspectSelect?: (prospect: ProspectData) => void;
  onViewDetails?: (prospect: ProspectData) => void;
  onContact?: (prospect: ProspectData) => void;
  showHeader?: boolean;
}

export const ProspectAnalysisPanel: React.FC<ProspectAnalysisPanelProps> = ({
  campaignId,
  onProspectSelect,
  onViewDetails,
  onContact,
  showHeader = true,
}) => {
  const theme = useTheme();
  const [prospects, setProspects] = useState<ProspectData[]>(sampleProspects);
  const [selectedProspects, setSelectedProspects] = useState<string[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [expanded, setExpanded] = useState<string | false>('prospects');
  const [filter, setFilter] = useState<'all' | 'qualified' | 'contacted' | 'pending'>('all');
  const [transparencyView, setTransparencyView] = useState<string | null>(null);

  // Filter prospects based on selection
  const filteredProspects = prospects.filter(prospect => {
    if (filter === 'all') return true;
    return prospect.status === filter;
  });

  // Calculate summary stats
  const stats = {
    total: prospects.length,
    analyzed: prospects.filter(p => p.status === 'analyzed').length,
    qualified: prospects.filter(p => p.status === 'qualified').length,
    contacted: prospects.filter(p => p.status === 'contacted').length,
    avgConfidence: Math.round(prospects.reduce((sum, p) => sum + p.confidence, 0) / prospects.length),
    avgDA: Math.round(prospects.reduce((sum, p) => sum + p.da, 0) / prospects.length),
  };

  const handleProspectClick = (prospect: ProspectData) => {
    setSelectedProspects(prev => {
      const isSelected = prev.includes(prospect.id);
      const newSelected = isSelected
        ? prev.filter(id => id !== prospect.id)
        : [...prev, prospect.id];

      onProspectSelect?.(prospect);
      return newSelected;
    });
  };

  const handleAnalyzeNew = async () => {
    setIsAnalyzing(true);

    // Simulate AI analysis
    await new Promise(resolve => setTimeout(resolve, 3000));

    // Add new analyzed prospects
    const newProspects: ProspectData[] = [
      {
        id: Date.now().toString(),
        domain: 'seojournal.com',
        da: 76,
        status: 'analyzed',
        opportunity: 'Expert Interview',
        confidence: 84,
        contact: 'interviews@seojournal.com',
        contactEmail: 'interviews@seojournal.com',
        contentQuality: 79,
        backlinkPotential: 72,
        spamRisk: 7,
        lastAnalyzed: new Date().toISOString().split('T')[0],
        aiRecommendation: 'Strong SEO focus - ideal for technical content',
      },
    ];

    setProspects(prev => [...newProspects, ...prev]);
    setIsAnalyzing(false);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3, duration: 0.5 }}
    >
      <Card sx={{
        ...BacklinkingStyles.campaignCard,
        minHeight: 600,
        position: 'relative',
      }}>
        {showHeader && (
          <CardHeader sx={BacklinkingStyles.campaignCardHeader}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Avatar sx={{
                  bgcolor: 'rgba(168, 85, 247, 0.1)',
                  border: '1px solid rgba(168, 85, 247, 0.3)',
                }}>
                  <BrainIcon sx={{ color: '#A855F7' }} />
                </Avatar>
                <Box>
                  <Typography variant="h6" sx={{ fontWeight: 700, color: '#F1F5F9' }}>
                    AI Prospect Analysis
                  </Typography>
                  <Typography variant="caption" sx={{ color: 'rgba(203, 213, 225, 0.7)' }}>
                    Domain authority scoring and contact discovery
                  </Typography>
                </Box>
              </Box>

              <Box sx={{ display: 'flex', gap: 1 }}>
                <Badge
                  badgeContent={stats.analyzed}
                  color="success"
                  sx={{
                    '& .MuiBadge-badge': {
                      background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
                    },
                  }}
                >
                  <Chip
                    label={`${stats.total} Total`}
                    size="small"
                    sx={{
                      backgroundColor: 'rgba(96, 165, 250, 0.1)',
                      color: '#60A5FA',
                      border: '1px solid rgba(96, 165, 250, 0.3)',
                    }}
                  />
                </Badge>

                <Chip
                  icon={<BarChartIcon />}
                  label={`${stats.avgConfidence}% Avg Score`}
                  size="small"
                  sx={{
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    color: '#10B981',
                    border: '1px solid rgba(16, 185, 129, 0.3)',
                  }}
                />
              </Box>
            </Box>
          </CardHeader>
        )}

        <CardContent sx={{ ...BacklinkingStyles.campaignCardContent, p: 0 }}>
          <Accordion
            expanded={expanded === 'prospects'}
            onChange={() => setExpanded(expanded === 'prospects' ? false : 'prospects')}
            sx={{
              background: 'transparent',
              boxShadow: 'none',
              '&:before': { display: 'none' },
              '& .MuiAccordionSummary-root': {
                background: 'linear-gradient(135deg, rgba(168, 85, 247, 0.05) 0%, rgba(96, 165, 250, 0.05) 100%)',
                borderRadius: 2,
                mx: 2,
                mt: 2,
                minHeight: 64,
              },
              '& .MuiAccordionSummary-content': {
                alignItems: 'center',
              },
              '& .MuiAccordionDetails-root': {
                px: 2,
                pb: 2,
              },
            }}
          >
            <AccordionSummary
              expandIcon={<ExpandMoreIcon sx={{ color: '#A855F7' }} />}
              sx={{
                '&:hover': {
                  background: 'linear-gradient(135deg, rgba(168, 85, 247, 0.1) 0%, rgba(96, 165, 250, 0.1) 100%)',
                },
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                <Avatar sx={{
                  bgcolor: 'rgba(168, 85, 247, 0.1)',
                  border: '1px solid rgba(168, 85, 247, 0.3)',
                }}>
                  <GlobeIcon sx={{ color: '#A855F7' }} />
                </Avatar>
                <Box sx={{ flex: 1 }}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#F1F5F9' }}>
                    AI-Scored Prospects
                  </Typography>
                  <Typography variant="caption" sx={{ color: 'rgba(203, 213, 225, 0.7)' }}>
                    Domain analysis with confidence ratings and contact information
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Chip
                    label="AI Scored"
                    size="small"
                    sx={{
                      background: 'linear-gradient(135deg, #A855F7 0%, #60A5FA 100%)',
                      color: 'white',
                      fontSize: '0.7rem',
                    }}
                  />
                  <Chip
                    label={`${filteredProspects.length} Shown`}
                    size="small"
                    variant="outlined"
                    sx={{
                      borderColor: 'rgba(168, 85, 247, 0.5)',
                      color: '#A855F7',
                    }}
                  />
                </Box>
              </Box>
            </AccordionSummary>

            <AccordionDetails>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                {/* Filter Buttons */}
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  {[
                    { key: 'all', label: 'All Prospects', count: stats.total },
                    { key: 'qualified', label: 'Qualified', count: stats.qualified },
                    { key: 'contacted', label: 'Contacted', count: stats.contacted },
                    { key: 'pending', label: 'Pending', count: prospects.filter(p => p.status === 'pending').length },
                  ].map(({ key, label, count }) => (
                    <Button
                      key={key}
                      size="small"
                      variant={filter === key ? 'contained' : 'outlined'}
                      onClick={() => setFilter(key as any)}
                      sx={{
                        ...(filter === key && {
                          background: 'linear-gradient(135deg, #A855F7 0%, #60A5FA 100%)',
                          boxShadow: '0 4px 15px rgba(168, 85, 247, 0.4)',
                        }),
                        '&:hover': {
                          background: filter === key
                            ? 'linear-gradient(135deg, #9333EA 0%, #3B82F6 100%)'
                            : 'rgba(168, 85, 247, 0.1)',
                        },
                      }}
                    >
                      {label} ({count})
                    </Button>
                  ))}
                </Box>

                {/* Prospects Grid */}
                <Box>
                  <Grid container spacing={2}>
                    <AnimatePresence>
                      {filteredProspects.map((prospect) => (
                        <Grid item xs={12} sm={6} lg={4} key={prospect.id}>
                          <motion.div
                            layout
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.9 }}
                            transition={{ duration: 0.3 }}
                          >
                            <ProspectCard
                              prospect={prospect}
                              onViewDetails={onViewDetails}
                              onContact={onContact}
                            />
                          </motion.div>
                        </Grid>
                      ))}
                    </AnimatePresence>
                  </Grid>
                </Box>

                {/* Analysis Action */}
                <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                  <Button
                    fullWidth
                    variant="contained"
                    startIcon={isAnalyzing ? <RefreshIcon /> : <BrainIcon />}
                    onClick={handleAnalyzeNew}
                    disabled={isAnalyzing}
                    sx={{
                      background: 'linear-gradient(135deg, #A855F7 0%, #60A5FA 50%, #06B6D4 100%)',
                      boxShadow: '0 4px 15px rgba(168, 85, 247, 0.4)',
                      '&:hover': {
                        background: 'linear-gradient(135deg, #9333EA 0%, #3B82F6 50%, #0891B2 100%)',
                        boxShadow: '0 6px 20px rgba(168, 85, 247, 0.6)',
                        transform: 'translateY(-2px)',
                      },
                      '&:disabled': {
                        background: 'rgba(107, 114, 128, 0.5)',
                      },
                    }}
                  >
                    {isAnalyzing ? (
                      <>
                        <motion.div
                          animate={{ rotate: 360 }}
                          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                          style={{ display: 'inline-block', marginRight: 8 }}
                        >
                          <RefreshIcon />
                        </motion.div>
                        AI Analyzing New Prospects...
                      </>
                    ) : (
                      <>
                        🤖 Analyze New Prospects
                      </>
                    )}
                  </Button>

                  {isAnalyzing && (
                    <Box sx={{ flex: 1, ml: 2 }}>
                      <LinearProgress
                        sx={{
                          height: 8,
                          borderRadius: 4,
                          backgroundColor: 'rgba(168, 85, 247, 0.1)',
                          '& .MuiLinearProgress-bar': {
                            borderRadius: 4,
                            background: 'linear-gradient(90deg, #A855F7 0%, #60A5FA 50%, #06B6D4 100%)',
                          },
                        }}
                      />
                    </Box>
                  )}
                </Box>
              </Box>
            </AccordionDetails>
          </Accordion>
        </CardContent>
      </Card>
    </motion.div>
  );
};