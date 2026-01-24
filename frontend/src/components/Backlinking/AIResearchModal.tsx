/**
 * AI Research Modal - Ported from Legacy Backlinker
 *
 * This component provides an engaging AI research experience with animated progress
 * during backlinking opportunity discovery. It transforms waiting time into an
 * interactive experience showcasing AI capabilities.
 */

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  LinearProgress,
  Grid,
  Card,
  CardContent,
  Chip,
  Avatar,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Psychology as BrainIcon,
  CheckCircle as CheckCircleIcon,
  TrendingUp as TrendingUpIcon,
  Email as EmailIcon,
  Web as WebIcon,
  Search as SearchIcon,
  Analytics as AnalyticsIcon,
  Psychology as PsychologyIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

interface AIResearchModalProps {
  open: boolean;
  onClose: () => void;
  campaignId?: string;
  keywords?: string[];
  targetIndustry?: string;
  aiEnhanced?: boolean;
  enableTrendAnalysis?: boolean;
  onComplete?: (results: AIResearchResults) => void;
}

interface AIResearchResults {
  prospectsFound: number;
  emailsReady: number;
  opportunities: any[];
  success: boolean;
  campaignId?: string;
}

const researchSteps = [
  {
    title: "Phase 1: Intelligent Query Generation",
    description: (aiEnhanced: boolean) =>
      aiEnhanced
        ? "AI analyzes your keywords and generates semantic search queries with contextual understanding"
        : "Programmatic generation of proven guest post search patterns across multiple categories",
    icon: <PsychologyIcon />,
    duration: 2000,
    phase: 1,
    details: (aiEnhanced: boolean) => ({
      programmatic: "Generated 45+ queries across semantic, industry, and operator categories",
      ai_enhanced: "AI enhanced queries with semantic understanding and industry expertise"
    })
  },
  {
    title: "Phase 1.5: Trend Analysis",
    description: (aiEnhanced: boolean, enableTrendAnalysis: boolean) =>
      enableTrendAnalysis
        ? "Google Trends analysis for seasonal patterns, emerging topics, and geographic insights"
        : "Trend analysis skipped - using standard discovery methods",
    icon: <TrendingUpIcon />,
    duration: 1500,
    phase: 1.5,
    details: (aiEnhanced: boolean, enableTrendAnalysis: boolean) => ({
      trend_insights: enableTrendAnalysis ? "Analyzing seasonal patterns and emerging topics" : "Not enabled",
      geographic_data: enableTrendAnalysis ? "Regional interest distribution analysis" : "Skipped",
      query_enhancement: enableTrendAnalysis ? "Trend-based query optimization applied" : "Standard queries used"
    })
  },
  {
    title: "Phase 2: Adaptive API Search",
    description: (aiEnhanced: boolean) =>
      "Dual API execution (Exa + Tavily) with intelligent query distribution and real-time optimization",
    icon: <SearchIcon />,
    duration: 3500,
    phase: 2,
    details: (aiEnhanced: boolean) => ({
      probing: "Smart initial probing: 2 queries per category at low result limits",
      expansion: "Performance-based expansion of successful categories",
      api_balance: "Exa for semantic search, Tavily for real-time results"
    })
  },
  {
    title: "Phase 3: Quality Processing & Deduplication",
    description: (aiEnhanced: boolean) =>
      "Advanced deduplication and quality filtering with intelligent spam detection",
    icon: <AnalyticsIcon />,
    duration: 2200,
    phase: 3,
    details: (aiEnhanced: boolean) => ({
      deduplication: "URL deduplication and quality filtering",
      spam_detection: "Advanced spam risk assessment",
      quality_scoring: "Multi-factor opportunity evaluation"
    })
  },
  {
    title: "Phase 4: Content Analysis & Contact Extraction",
    description: (aiEnhanced: boolean) =>
      aiEnhanced
        ? "AI-powered content analysis with strategic context and contact intelligence"
        : "Programmatic content analysis with pattern-based contact extraction",
    icon: <WebIcon />,
    duration: 2800,
    phase: 4,
    details: (aiEnhanced: boolean) => ({
      content_analysis: aiEnhanced
        ? "AI analyzes webpage content with full prospecting context"
        : "Programmatic pattern matching for guest post signals",
      contact_extraction: "Multi-strategy email and contact discovery",
      quality_assessment: "Authority and relevance evaluation"
    })
  },
  {
    title: "Phase 5: Strategic Opportunity Selection",
    description: (aiEnhanced: boolean) =>
      "Final opportunity selection based on comprehensive analysis and campaign objectives",
    icon: <BrainIcon />,
    duration: 2000,
    phase: 5,
    details: (aiEnhanced: boolean) => ({
      quality_filtering: "Multi-factor scoring with campaign alignment",
      transparency_prep: "Complete discovery audit trail preparation",
      performance_tracking: "Conversion rate and efficiency metrics"
    })
  },
  {
    title: "Phase 6: Results Compilation & Validation",
    description: "Setting up tracking and analytics",
    icon: <AnalyticsIcon />,
    duration: 1500,
  },
];

const AnimatedIcon = ({ icon, isActive }: { icon: React.ReactNode; isActive: boolean }) => (
  <motion.div
    animate={isActive ? { scale: [1, 1.2, 1], rotate: [0, 5, -5, 0] } : { scale: 1 }}
    transition={{ duration: 0.5, repeat: isActive ? Infinity : 0 }}
  >
    {icon}
  </motion.div>
);

export const AIResearchModal: React.FC<AIResearchModalProps> = ({
  open,
  onClose,
  campaignId,
  keywords = [],
  targetIndustry,
  aiEnhanced = false,
  enableTrendAnalysis = false,
  onComplete,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(0);
  const [isCompleted, setIsCompleted] = useState(false);
  const [prospectsFound, setProspectsFound] = useState(0);
  const [emailsReady, setEmailsReady] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [discoveryMethod, setDiscoveryMethod] = useState<'ai_enhanced' | 'programmatic'>('programmatic');
  const [phaseStats, setPhaseStats] = useState<Record<string, any>>({});

  // Simulate AI research process
  useEffect(() => {
    if (open && !isProcessing && !isCompleted) {
      setIsProcessing(true);
      setCurrentStep(0);
      setProgress(0);
      setProspectsFound(0);
      setEmailsReady(0);
      setDiscoveryMethod(aiEnhanced ? 'ai_enhanced' : 'programmatic');
      setPhaseStats({});

      const runResearch = async () => {
        for (let i = 0; i < researchSteps.length; i++) {
          setCurrentStep(i);
          const step = researchSteps[i];

          // Animate progress for this step
          const stepProgress = 100 / researchSteps.length;
          const startProgress = i * stepProgress;
          const endProgress = (i + 1) * stepProgress;

          // Smooth progress animation
          for (let p = startProgress; p <= endProgress; p += 1) {
            setProgress(p);
            await new Promise(resolve => setTimeout(resolve, step.duration / stepProgress));
          }

          // Update metrics and phase stats based on step
          if (i >= 1) {
            const newProspects = Math.floor((i + 1) * 3.5);
            setProspectsFound(newProspects);
            setPhaseStats(prev => ({
              ...prev,
              queriesGenerated: 45,
              apiCalls: 45,
              resultsProcessed: 234,
              opportunitiesAnalyzed: 156
            }));
          }
          if (i >= 3) {
            const newEmails = Math.floor((i - 2) * 2.8);
            setEmailsReady(newEmails);
          }
        }

        // Complete the research
        setProgress(100);
        setIsCompleted(true);
        setIsProcessing(false);

        // Simulate final results
        const finalResults: AIResearchResults = {
          prospectsFound: 24,
          emailsReady: 18,
          opportunities: [],
          success: true,
          campaignId,
        };

        setProspectsFound(24);
        setEmailsReady(18);

        // Call completion callback after a brief delay
        setTimeout(() => {
          onComplete?.(finalResults);
        }, 2000);
      };

      runResearch();
    }
  }, [open, isProcessing, isCompleted, campaignId, onComplete]);

  // Reset state when modal closes
  useEffect(() => {
    if (!open) {
      setTimeout(() => {
        setIsProcessing(false);
        setIsCompleted(false);
        setCurrentStep(0);
        setProgress(0);
        setProspectsFound(0);
        setEmailsReady(0);
      }, 300);
    }
  }, [open]);

  const currentStepData = researchSteps[currentStep];
  const isStepActive = !isCompleted && currentStep < researchSteps.length;

  return (
    <Dialog
      open={open}
      onClose={() => {}} // Prevent closing during research
      maxWidth="sm"
      fullWidth
      sx={{
        '& .MuiDialog-paper': {
          borderRadius: '20px',
          background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.95) 100%)',
          backdropFilter: 'blur(30px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          boxShadow: '0 25px 50px rgba(96, 165, 250, 0.15)',
          overflow: 'hidden',
          position: 'relative',
        },
      }}
    >
      {/* AI Background Pattern */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: `
            radial-gradient(circle at 20% 20%, rgba(96, 165, 250, 0.08) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(168, 85, 247, 0.08) 0%, transparent 50%),
            radial-gradient(circle at 40% 70%, rgba(6, 182, 212, 0.05) 0%, transparent 50%)
          `,
          opacity: 0.6,
          pointerEvents: 'none',
        }}
      />

      <DialogTitle sx={{ position: 'relative', zIndex: 2, textAlign: 'center', pb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 2, mb: 1 }}>
          <Avatar
            sx={{
              bgcolor: 'rgba(96, 165, 250, 0.1)',
              border: '1px solid rgba(96, 165, 250, 0.3)',
              width: 48,
              height: 48,
            }}
          >
            <AnimatedIcon icon={<BrainIcon />} isActive={isStepActive} />
          </Avatar>
          <Box>
            <Typography variant="h5" sx={{ fontWeight: 700, color: '#F1F5F9' }}>
              AI Research in Progress
            </Typography>
          </Box>
        </Box>
        <Typography variant="body2" sx={{ color: 'rgba(203, 213, 225, 0.8)', maxWidth: 400, mx: 'auto' }}>
          ALwrity is analyzing prospects and generating personalized outreach strategies
        </Typography>
      </DialogTitle>

      <DialogContent sx={{ position: 'relative', zIndex: 2, px: 3, py: 1 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {/* Progress Bar */}
          <Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2" sx={{ fontWeight: 600, color: '#CBD5E1' }}>
                Progress
              </Typography>
              <Typography variant="body2" sx={{ fontWeight: 600, color: '#60A5FA' }}>
                {Math.round(progress)}%
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={progress}
              sx={{
                height: 10,
                borderRadius: 5,
                backgroundColor: 'rgba(96, 165, 250, 0.1)',
                '& .MuiLinearProgress-bar': {
                  borderRadius: 5,
                  background: 'linear-gradient(90deg, #60A5FA 0%, #06B6D4 50%, #A855F7 100%)',
                  boxShadow: '0 0 20px rgba(96, 165, 250, 0.4)',
                },
              }}
            />
          </Box>

          {/* Current Step */}
          <AnimatePresence mode="wait">
            <motion.div
              key={currentStep}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <Card
                sx={{
                  background: 'linear-gradient(135deg, rgba(96, 165, 250, 0.1) 0%, rgba(6, 182, 212, 0.1) 100%)',
                  border: '1px solid rgba(96, 165, 250, 0.2)',
                  borderRadius: 3,
                }}
              >
                <CardContent sx={{ p: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Avatar
                      sx={{
                        bgcolor: 'rgba(96, 165, 250, 0.2)',
                        width: 40,
                        height: 40,
                      }}
                    >
                      <AnimatedIcon icon={currentStepData?.icon} isActive={isStepActive} />
                    </Avatar>
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#F1F5F9' }}>
                        {currentStepData?.title}
                      </Typography>
                      <Typography variant="caption" sx={{ color: 'rgba(203, 213, 225, 0.7)' }}>
                        {typeof currentStepData?.description === 'function'
                          ? currentStepData.description(aiEnhanced, enableTrendAnalysis)
                          : currentStepData?.description}
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          </AnimatePresence>

          {/* Metrics Grid */}
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Card sx={{
                background: 'rgba(30, 41, 59, 0.6)',
                border: '1px solid rgba(96, 165, 250, 0.2)',
                textAlign: 'center',
              }}>
                <CardContent sx={{ p: 2 }}>
                  <Typography variant="h4" sx={{ fontWeight: 700, color: '#60A5FA', mb: 0.5 }}>
                    {prospectsFound}
                  </Typography>
                  <Typography variant="caption" sx={{ color: 'rgba(203, 213, 225, 0.7)' }}>
                    Prospects Found
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6}>
              <Card sx={{
                background: 'rgba(30, 41, 59, 0.6)',
                border: '1px solid rgba(6, 182, 212, 0.2)',
                textAlign: 'center',
              }}>
                <CardContent sx={{ p: 2 }}>
                  <Typography variant="h4" sx={{ fontWeight: 700, color: '#06B6D4', mb: 0.5 }}>
                    {emailsReady}
                  </Typography>
                  <Typography variant="caption" sx={{ color: 'rgba(203, 213, 225, 0.7)' }}>
                    Emails Ready
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Completion Celebration */}
          <AnimatePresence>
            {isCompleted && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ duration: 0.5 }}
              >
                <Card sx={{
                  background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%)',
                  border: '1px solid rgba(16, 185, 129, 0.3)',
                  textAlign: 'center',
                }}>
                  <CardContent sx={{ p: 3 }}>
                    <motion.div
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 0.5, repeat: Infinity, repeatDelay: 1 }}
                    >
                      <CheckCircleIcon sx={{ fontSize: 48, color: '#10B981', mb: 2 }} />
                    </motion.div>
                    <Typography variant="h6" sx={{ fontWeight: 700, color: '#10B981', mb: 1 }}>
                      Research Complete!
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'rgba(203, 213, 225, 0.8)' }}>
                      Found {prospectsFound} high-quality prospects with {emailsReady} email addresses ready for outreach.
                    </Typography>
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </AnimatePresence>
        </Box>
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 3, justifyContent: 'center', position: 'relative', zIndex: 2 }}>
        <Button
          onClick={onClose}
          disabled={!isCompleted}
          variant="outlined"
          sx={{
            borderColor: 'rgba(96, 165, 250, 0.5)',
            color: '#60A5FA',
            '&:hover': {
              borderColor: '#60A5FA',
              backgroundColor: 'rgba(96, 165, 250, 0.1)',
            },
            '&:disabled': {
              borderColor: 'rgba(203, 213, 225, 0.3)',
              color: 'rgba(203, 213, 225, 0.5)',
            },
          }}
        >
          {isCompleted ? 'Continue to Campaign' : 'Research in Progress...'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};