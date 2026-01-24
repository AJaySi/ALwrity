/**
 * AI Enhancement Modal
 *
 * Comprehensive modal explaining AI enhancements vs programmatic approaches
 * Allows users to choose between cost-effective vs enhanced results
 */

import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Chip,
  Divider,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  useTheme,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Speed as SpeedIcon,
  Psychology as PsychologyIcon,
  AccountBalanceWallet as WalletIcon,
  TrendingUp as TrendingUpIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';
import { BacklinkingStyles } from './styles/backlinkingStyles';

interface AIEnhancementModalProps {
  open: boolean;
  onClose: () => void;
  aiEnhanced: boolean;
  onToggleAI: () => void;
}

export const AIEnhancementModal: React.FC<AIEnhancementModalProps> = ({
  open,
  onClose,
  aiEnhanced,
  onToggleAI,
}) => {
  const theme = useTheme();

  const handleToggleAndClose = () => {
    onToggleAI();
    onClose();
  };

  const programmaticFeatures = [
    {
      icon: <SpeedIcon sx={{ color: '#10B981' }} />,
      title: 'Fast & Reliable',
      description: 'Programmatic pattern matching ensures consistent, fast results',
      benefits: ['Sub-30s discovery', '100% uptime', 'Predictable performance']
    },
    {
      icon: <WalletIcon sx={{ color: '#10B981' }} />,
      title: 'Cost-Effective',
      description: 'No AI calls means lower costs and transparent pricing',
      benefits: ['$0.005-0.01 per search', 'No hidden fees', 'Budget-friendly']
    },
    {
      icon: <CheckCircleIcon sx={{ color: '#10B981' }} />,
      title: 'Core Functionality',
      description: 'All essential backlinking features work reliably',
      benefits: ['Guest post discovery', 'Email extraction', 'Campaign management']
    }
  ];

  const aiEnhancedFeatures = [
    {
      icon: <PsychologyIcon sx={{ color: '#A855F7' }} />,
      title: 'Semantic Intelligence',
      description: 'AI understands keyword relationships and semantic context',
      benefits: ['35% more query diversity', 'Better semantic matching', 'Contextual understanding']
    },
    {
      icon: <TrendingUpIcon sx={{ color: '#A855F7' }} />,
      title: 'Enhanced Quality',
      description: 'AI detects subtle guest posting signals and opportunities',
      benefits: ['30% better opportunity detection', 'Industry expertise', 'Subtle pattern recognition']
    },
    {
      icon: <SpeedIcon sx={{ color: '#A855F7' }} />,
      title: 'Strategic Optimization',
      description: 'AI optimizes search strategies based on performance data',
      benefits: ['Adaptive query expansion', 'Smart result filtering', 'Performance-based decisions']
    }
  ];

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="lg"
      fullWidth
      PaperProps={{
        sx: {
          ...BacklinkingStyles.modal,
          maxHeight: '90vh',
          overflow: 'auto'
        }
      }}
    >
      <DialogTitle sx={{
        ...BacklinkingStyles.modalTitle,
        textAlign: 'center',
        pb: 1
      }}>
        🚀 AI Enhancement Settings
      </DialogTitle>

      <DialogContent sx={{ px: 3, pb: 1 }}>
        <Typography variant="h6" sx={{
          ...BacklinkingStyles.modalSubtitle,
          textAlign: 'center',
          mb: 3,
          color: '#94A3B8'
        }}>
          Choose between cost-effective programmatic discovery or AI-enhanced results
        </Typography>

        {/* Current Status */}
        <Alert
          severity={aiEnhanced ? "info" : "success"}
          sx={{
            mb: 3,
            background: aiEnhanced
              ? 'linear-gradient(135deg, rgba(168, 85, 247, 0.1) 0%, rgba(96, 165, 250, 0.1) 100%)'
              : 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(96, 165, 250, 0.1) 100%)',
            border: `1px solid ${aiEnhanced ? 'rgba(168, 85, 247, 0.3)' : 'rgba(16, 185, 129, 0.3)'}`,
            color: aiEnhanced ? '#A855F7' : '#10B981'
          }}
        >
          <Typography variant="body2" sx={{ fontWeight: 600 }}>
            Currently: {aiEnhanced ? '🤖 AI Enhanced Mode' : '⚡ Programmatic Mode'}
          </Typography>
          <Typography variant="body2">
            {aiEnhanced
              ? 'AI enhancements active - better results with moderate cost increase'
              : 'Cost-effective mode - fast, reliable results at minimal cost'
            }
          </Typography>
        </Alert>

        {/* Feature Comparison */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          {/* Programmatic Mode */}
          <Grid item xs={12} md={6}>
            <Card sx={{
              height: '100%',
              background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(30, 41, 59, 0.8) 100%)',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              backdropFilter: 'blur(10px)',
            }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6" sx={{
                    color: '#10B981',
                    fontWeight: 700,
                    mr: 1
                  }}>
                    ⚡ Programmatic Mode
                  </Typography>
                  <Chip
                    label="Cost-Effective"
                    size="small"
                    sx={{
                      bgcolor: 'rgba(16, 185, 129, 0.2)',
                      color: '#10B981',
                      border: '1px solid rgba(16, 185, 129, 0.3)'
                    }}
                  />
                </Box>

                <Typography variant="body2" sx={{ color: '#94A3B8', mb: 3, lineHeight: 1.6 }}>
                  Fast, reliable prospect discovery using proven algorithmic patterns.
                  No AI calls means predictable costs and consistent performance.
                </Typography>

                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {programmaticFeatures.map((feature, index) => (
                    <Box key={index} sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                      <Box sx={{ mt: 0.5 }}>{feature.icon}</Box>
                      <Box>
                        <Typography variant="body2" sx={{ fontWeight: 600, color: '#F1F5F9', mb: 0.5 }}>
                          {feature.title}
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#94A3B8', fontSize: '0.8rem', mb: 1 }}>
                          {feature.description}
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {feature.benefits.map((benefit, i) => (
                            <Chip
                              key={i}
                              label={benefit}
                              size="small"
                              variant="outlined"
                              sx={{
                                fontSize: '0.7rem',
                                height: '20px',
                                bgcolor: 'rgba(16, 185, 129, 0.1)',
                                borderColor: 'rgba(16, 185, 129, 0.3)',
                                color: '#10B981'
                              }}
                            />
                          ))}
                        </Box>
                      </Box>
                    </Box>
                  ))}
                </Box>

                <Divider sx={{ my: 2, borderColor: 'rgba(16, 185, 129, 0.3)' }} />

                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="body2" sx={{ color: '#10B981', fontWeight: 600, mb: 1 }}>
                    💰 Cost: $0.005-0.01 per search
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#94A3B8', fontSize: '0.8rem' }}>
                    Perfect for budget-conscious users who want reliable results
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* AI Enhanced Mode */}
          <Grid item xs={12} md={6}>
            <Card sx={{
              height: '100%',
              background: 'linear-gradient(135deg, rgba(168, 85, 247, 0.1) 0%, rgba(30, 41, 59, 0.8) 100%)',
              border: '1px solid rgba(168, 85, 247, 0.3)',
              backdropFilter: 'blur(10px)',
            }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6" sx={{
                    color: '#A855F7',
                    fontWeight: 700,
                    mr: 1
                  }}>
                    🤖 AI Enhanced Mode
                  </Typography>
                  <Chip
                    label="Premium Quality"
                    size="small"
                    sx={{
                      bgcolor: 'rgba(168, 85, 247, 0.2)',
                      color: '#A855F7',
                      border: '1px solid rgba(168, 85, 247, 0.3)'
                    }}
                  />
                </Box>

                <Typography variant="body2" sx={{ color: '#94A3B8', mb: 3, lineHeight: 1.6 }}>
                  Strategic AI enhancements for superior prospect quality and discovery.
                  AI provides semantic understanding and pattern recognition where it matters most.
                </Typography>

                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {aiEnhancedFeatures.map((feature, index) => (
                    <Box key={index} sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                      <Box sx={{ mt: 0.5 }}>{feature.icon}</Box>
                      <Box>
                        <Typography variant="body2" sx={{ fontWeight: 600, color: '#F1F5F9', mb: 0.5 }}>
                          {feature.title}
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#94A3B8', fontSize: '0.8rem', mb: 1 }}>
                          {feature.description}
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {feature.benefits.map((benefit, i) => (
                            <Chip
                              key={i}
                              label={benefit}
                              size="small"
                              variant="outlined"
                              sx={{
                                fontSize: '0.7rem',
                                height: '20px',
                                bgcolor: 'rgba(168, 85, 247, 0.1)',
                                borderColor: 'rgba(168, 85, 247, 0.3)',
                                color: '#A855F7'
                              }}
                            />
                          ))}
                        </Box>
                      </Box>
                    </Box>
                  ))}
                </Box>

                <Divider sx={{ my: 2, borderColor: 'rgba(168, 85, 247, 0.3)' }} />

                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="body2" sx={{ color: '#A855F7', fontWeight: 600, mb: 1 }}>
                    💰 Cost: $0.05-0.12 per campaign
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#94A3B8', fontSize: '0.8rem' }}>
                    Enhanced results for users seeking maximum prospect quality
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Detailed AI Usage Breakdown */}
        <Accordion
          sx={{
            background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(51, 65, 85, 0.8) 100%)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            mb: 2,
            '&:before': { display: 'none' }
          }}
        >
          <AccordionSummary
            expandIcon={<ExpandMoreIcon sx={{ color: '#60A5FA' }} />}
            sx={{
              color: '#F1F5F9',
              '&:hover': { bgcolor: 'rgba(96, 165, 250, 0.05)' }
            }}
          >
            <Typography variant="body1" sx={{ fontWeight: 600 }}>
              📊 Detailed AI Usage & Cost Breakdown
            </Typography>
          </AccordionSummary>
          <AccordionDetails sx={{ pt: 0 }}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Typography variant="body2" sx={{ color: '#94A3B8', mb: 2 }}>
                AI is used strategically where it provides the highest value-to-cost ratio:
              </Typography>

              <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 2 }}>
                <Card sx={{ bgcolor: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
                  <CardContent sx={{ p: 2 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#10B981', mb: 1 }}>
                      ✅ Semantic Query Enhancement
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#94A3B8', fontSize: '0.8rem', mb: 1 }}>
                      AI generates conversation patterns, question-based queries, and semantic variations
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#10B981', fontSize: '0.8rem' }}>
                      Cost: $0.02-0.04 | Value: 35% better coverage
                    </Typography>
                  </CardContent>
                </Card>

                <Card sx={{ bgcolor: 'rgba(168, 85, 247, 0.1)', border: '1px solid rgba(168, 85, 247, 0.3)' }}>
                  <CardContent sx={{ p: 2 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#A855F7', mb: 1 }}>
                      ✅ Industry-Specific Intelligence
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#94A3B8', fontSize: '0.8rem', mb: 1 }}>
                      AI understands industry platforms and terminology for targeted discovery
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#A855F7', fontSize: '0.8rem' }}>
                      Cost: $0.02-0.03 | Value: 40% better targeting
                    </Typography>
                  </CardContent>
                </Card>

                <Card sx={{ bgcolor: 'rgba(168, 85, 247, 0.1)', border: '1px solid rgba(168, 85, 247, 0.3)' }}>
                  <CardContent sx={{ p: 2 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#A855F7', mb: 1 }}>
                      ✅ Content Analysis Enhancement
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#94A3B8', fontSize: '0.8rem', mb: 1 }}>
                      AI detects subtle guest posting signals in webpage content
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#A855F7', fontSize: '0.8rem' }}>
                      Cost: $0.03-0.05 | Value: 30% better detection
                    </Typography>
                  </CardContent>
                </Card>

                <Card sx={{ bgcolor: 'rgba(6, 182, 212, 0.1)', border: '1px solid rgba(6, 182, 212, 0.3)' }}>
                  <CardContent sx={{ p: 2 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#06B6D4', mb: 1 }}>
                      🚀 Trend Analysis Integration
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#94A3B8', fontSize: '0.8rem', mb: 1 }}>
                      Google Trends data enhances prospect discovery with seasonal patterns and emerging topics
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#06B6D4', fontSize: '0.8rem' }}>
                      Cost: $0.02-0.04 | Value: 25-40% better prospect quality
                    </Typography>
                  </CardContent>
                </Card>

                <Card sx={{ bgcolor: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)' }}>
                  <CardContent sx={{ p: 2 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#EF4444', mb: 1 }}>
                      ❌ Complex Optimization (Removed)
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#94A3B8', fontSize: '0.8rem', mb: 1 }}>
                      Expensive AI-driven cost optimization replaced with smart programmatic logic
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#EF4444', fontSize: '0.8rem' }}>
                      Saved: $0.50+ per campaign | Replaced with efficient algorithms
                    </Typography>
                  </CardContent>
                </Card>
              </Box>

              <Alert severity="info" sx={{ mt: 2 }}>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  🎯 Strategic AI Balance
                </Typography>
                <Typography variant="body2">
                  AI is used where it provides 3-5x value improvement over programmatic approaches.
                  Fallback to programmatic methods ensures reliability and cost control.
                </Typography>
              </Alert>
            </Box>
          </AccordionDetails>
        </Accordion>

        {/* Performance Context */}
        <Accordion
          sx={{
            background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(51, 65, 85, 0.8) 100%)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            '&:before': { display: 'none' }
          }}
        >
          <AccordionSummary
            expandIcon={<ExpandMoreIcon sx={{ color: '#60A5FA' }} />}
            sx={{
              color: '#F1F5F9',
              '&:hover': { bgcolor: 'rgba(96, 165, 250, 0.05)' }
            }}
          >
            <Typography variant="body1" sx={{ fontWeight: 600 }}>
              🔄 How Context Flows Between Phases
            </Typography>
          </AccordionSummary>
          <AccordionDetails sx={{ pt: 0 }}>
            <Typography variant="body2" sx={{ color: '#94A3B8', mb: 2 }}>
              The system builds context progressively, with AI enhancements receiving programmatic data:
            </Typography>

            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, p: 2, bgcolor: 'rgba(16, 185, 129, 0.1)', borderRadius: 1 }}>
                <Typography variant="body2" sx={{ color: '#10B981', fontWeight: 600, minWidth: '120px' }}>
                  Phase 1: Probing
                </Typography>
                <Typography variant="body2" sx={{ color: '#94A3B8' }}>
                  Programmatic queries collect baseline data → Performance metrics inform expansion strategy
                </Typography>
              </Box>

              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, p: 2, bgcolor: 'rgba(168, 85, 247, 0.1)', borderRadius: 1 }}>
                <Typography variant="body2" sx={{ color: '#A855F7', fontWeight: 600, minWidth: '120px' }}>
                  AI Enhancement
                </Typography>
                <Typography variant="body2" sx={{ color: '#94A3B8' }}>
                  Receives programmatic performance data → Generates smarter queries → Improves semantic coverage
                </Typography>
              </Box>

              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, p: 2, bgcolor: 'rgba(16, 185, 129, 0.1)', borderRadius: 1 }}>
                <Typography variant="body2" sx={{ color: '#10B981', fontWeight: 600, minWidth: '120px' }}>
                  Phase 2: Expansion
                </Typography>
                <Typography variant="body2" sx={{ color: '#94A3B8' }}>
                  Uses AI-enhanced query results → Programmatic analysis determines success → Smart resource allocation
                </Typography>
              </Box>

              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, p: 2, bgcolor: 'rgba(168, 85, 247, 0.1)', borderRadius: 1 }}>
                <Typography variant="body2" sx={{ color: '#A855F7', fontWeight: 600, minWidth: '120px' }}>
                  AI Analysis
                </Typography>
                <Typography variant="body2" sx={{ color: '#94A3B8' }}>
                  Receives programmatic content analysis → Enhances with semantic understanding → Better opportunity detection
                </Typography>
              </Box>
            </Box>

            <Alert severity="success" sx={{ mt: 2 }}>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                🔄 Perfect Context Flow
              </Typography>
              <Typography variant="body2">
                Programmatic approaches provide reliable data → AI enhancements build upon this foundation → Results improve quality without sacrificing reliability
              </Typography>
            </Alert>
          </AccordionDetails>
        </Accordion>
      </DialogContent>

      <DialogActions sx={{
        px: 3,
        pb: 3,
        pt: 1,
        justifyContent: 'space-between',
        gap: 2
      }}>
        <Button
          onClick={onClose}
          sx={{
            color: '#94A3B8',
            '&:hover': { color: '#F1F5F9' }
          }}
        >
          Cancel
        </Button>

        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            onClick={handleToggleAndClose}
            variant="outlined"
            sx={{
              borderColor: aiEnhanced ? '#10B981' : '#A855F7',
              color: aiEnhanced ? '#10B981' : '#A855F7',
              '&:hover': {
                borderColor: aiEnhanced ? '#059669' : '#9333EA',
                bgcolor: aiEnhanced ? 'rgba(16, 185, 129, 0.1)' : 'rgba(168, 85, 247, 0.1)'
              }
            }}
          >
            Switch to {aiEnhanced ? 'Programmatic Mode' : 'AI Enhanced Mode'}
          </Button>

          <Button
            onClick={onClose}
            variant="contained"
            sx={{
              background: 'linear-gradient(135deg, #60A5FA 0%, #A855F7 100%)',
              '&:hover': {
                background: 'linear-gradient(135deg, #3B82F6 0%, #9333EA 100%)'
              }
            }}
          >
            Done
          </Button>
        </Box>
      </DialogActions>
    </Dialog>
  );
};