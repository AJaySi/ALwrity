/**
 * Backlinking Help Modal - Educational Content from Legacy Landing Page
 *
 * Comprehensive help modal that explains the backlinking app using
 * content from the legacy landing page to educate users.
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
  Avatar,
  Divider,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Close as CloseIcon,
  HelpOutline as HelpIcon,
  TrendingUp as TrendingUpIcon,
  Email as EmailIcon,
  Search as SearchIcon,
  Psychology as BrainIcon,
  Analytics as AnalyticsIcon,
  People as PeopleIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as XCircleIcon,
  ArrowForward as ArrowRightIcon,
  Bolt as ZapIcon,
  Hub as NetworkIcon,
  Language as GlobeIcon,
  TrackChanges as TargetIcon,
  Shield as ShieldIcon,
  BarChart as BarChartIcon,
  SmartToy as SmartToyIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';

interface BacklinkingHelpModalProps {
  open: boolean;
  onClose: () => void;
}

const BacklinkingHelpModal: React.FC<BacklinkingHelpModalProps> = ({ open, onClose }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const features = [
    {
      icon: SearchIcon,
      title: "Intelligent Discovery",
      description: "AI-powered web scraping finds high-quality guest posting opportunities across the web",
      gradient: "linear-gradient(135deg, #60A5FA 0%, #3B82F6 100%)"
    },
    {
      icon: BrainIcon,
      title: "Neural Personalization",
      description: "Advanced AI crafts personalized outreach emails tailored to each target website",
      gradient: "linear-gradient(135deg, #A855F7 0%, #9333EA 100%)"
    },
    {
      icon: EmailIcon,
      title: "Automated Outreach",
      description: "Streamlined email campaigns with follow-up automation and response tracking",
      gradient: "linear-gradient(135deg, #10B981 0%, #059669 100%)"
    },
    {
      icon: BarChartIcon,
      title: "Advanced Analytics",
      description: "Real-time performance metrics, open rates, and backlink success tracking",
      gradient: "linear-gradient(135deg, #F59E0B 0%, #D97706 100%)"
    },
    {
      icon: PeopleIcon,
      title: "Lead Management",
      description: "Comprehensive contact database with status tracking and relationship management",
      gradient: "linear-gradient(135deg, #3B82F6 0%, #2563EB 100%)"
    },
    {
      icon: ZapIcon,
      title: "Batch Processing",
      description: "Handle multiple keywords and campaigns simultaneously for maximum efficiency",
      gradient: "linear-gradient(135deg, #F59E0B 0%, #D97706 100%)"
    },
    {
      icon: GlobeIcon,
      title: "Global Reach",
      description: "Find opportunities across multiple languages and geographic regions",
      gradient: "linear-gradient(135deg, #06B6D4 0%, #0891B2 100%)"
    },
    {
      icon: TargetIcon,
      title: "Smart Targeting",
      description: "AI algorithms identify the most promising prospects based on domain authority and relevance",
      gradient: "linear-gradient(135deg, #EC4899 0%, #DB2777 100%)"
    },
    {
      icon: ShieldIcon,
      title: "Safe & Compliant",
      description: "Built-in safeguards ensure ethical outreach practices and compliance with email regulations",
      gradient: "linear-gradient(135deg, #6B7280 0%, #4B5563 100%)"
    }
  ];

  const manualVsAI = [
    {
      manual: "Manual Google searches, endless tabs",
      ai: "AI web research finds and refines prospects"
    },
    {
      manual: "Copy-paste emails scraped by hand",
      ai: "Auto-scrapes verified contacts and roles"
    },
    {
      manual: "Generic outreach with low replies",
      ai: "Personalized AI emails for each prospect"
    },
    {
      manual: "No domain authority prioritization",
      ai: "DA ranking + semantic relevance scoring"
    },
    {
      manual: "Spreadsheet chaos, hard to track",
      ai: "Integrated sending + response intelligence"
    },
    {
      manual: "Slow follow-ups and missed windows",
      ai: "Human-in-the-loop reviews where it matters"
    }
  ];

  const workflowSteps = [
    {
      icon: SearchIcon,
      title: "AI Prospect Discovery",
      description: "Neural networks scan the web for high-quality backlinking opportunities using your keywords"
    },
    {
      icon: TargetIcon,
      title: "Smart Qualification",
      description: "AI analyzes domain authority, content relevance, and link-building potential"
    },
    {
      icon: BrainIcon,
      title: "Personalized Outreach",
      description: "Advanced AI crafts custom emails tailored to each prospect's industry and content"
    },
    {
      icon: EmailIcon,
      title: "Automated Campaigns",
      description: "Streamlined email sending with follow-up automation and response tracking"
    },
    {
      icon: AnalyticsIcon,
      title: "Performance Analytics",
      description: "Real-time metrics, conversion tracking, and AI-powered optimization insights"
    }
  ];

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="lg"
      fullWidth
      fullScreen={isMobile}
      sx={{
        '& .MuiDialog-paper': {
          background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.95) 100%)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: isMobile ? 0 : 3,
          maxHeight: '90vh',
        },
      }}
    >
      <DialogTitle sx={{
        pb: 1,
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Avatar sx={{
            bgcolor: 'rgba(96, 165, 250, 0.1)',
            border: '1px solid rgba(96, 165, 250, 0.3)',
          }}>
            <HelpIcon sx={{ color: '#60A5FA' }} />
          </Avatar>
          <Box>
            <Typography variant="h5" sx={{ fontWeight: 700, color: '#F1F5F9', mb: 0.5 }}>
              AI Backlinking Guide
            </Typography>
            <Typography variant="body2" sx={{ color: 'rgba(203, 213, 225, 0.8)' }}>
              Everything you need to know about ALwrity's AI-powered backlinking platform
            </Typography>
          </Box>
        </Box>
        <Button
          onClick={onClose}
          sx={{
            minWidth: 'auto',
            p: 1,
            color: 'rgba(203, 213, 225, 0.7)',
            '&:hover': {
              color: '#F1F5F9',
              bgcolor: 'rgba(255, 255, 255, 0.1)',
            },
          }}
        >
          <CloseIcon />
        </Button>
      </DialogTitle>

      <DialogContent sx={{ p: 0, overflow: 'auto' }}>
        <Box sx={{ p: 3 }}>
          {/* Hero Section */}
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <Typography variant="h3" sx={{
                fontWeight: 800,
                mb: 2,
                background: 'linear-gradient(135deg, #60A5FA 0%, #A855F7 50%, #06B6D4 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}>
                AI-Powered Backlinking
              </Typography>
              <Typography variant="h6" sx={{
                color: 'rgba(203, 213, 225, 0.9)',
                mb: 3,
                fontWeight: 400,
                maxWidth: 600,
                mx: 'auto',
                lineHeight: 1.4,
              }}>
                Automate your link building strategy with neural network intelligence.
                Find opportunities, craft personalized outreach, and secure high-quality backlinks.
              </Typography>

              <Box sx={{ display: 'flex', justifyContent: 'center', gap: 3, flexWrap: 'wrap', mb: 3 }}>
                {[
                  { icon: ZapIcon, text: "Automated Discovery", color: '#F59E0B' },
                  { icon: BrainIcon, text: "AI Personalization", color: '#A855F7' },
                  { icon: NetworkIcon, text: "Smart Outreach", color: '#06B6D4' }
                ].map((feature, index) => (
                  <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <feature.icon sx={{ color: feature.color, fontSize: 20 }} />
                    <Typography variant="body2" sx={{ color: 'rgba(203, 213, 225, 0.9)', fontWeight: 500 }}>
                      {feature.text}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </motion.div>
          </Box>

          <Divider sx={{ my: 3, backgroundColor: 'rgba(255, 255, 255, 0.1)' }} />

          {/* How It Works */}
          <Box sx={{ mb: 4 }}>
            <Typography variant="h4" sx={{
              fontWeight: 700,
              color: '#F1F5F9',
              mb: 3,
              textAlign: 'center',
            }}>
              How AI Backlinking Works
            </Typography>

            <Grid container spacing={2}>
              {workflowSteps.map((step, index) => (
                <Grid item xs={12} sm={6} lg={12/workflowSteps.length} key={index}>
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1, duration: 0.5 }}
                  >
                    <Card sx={{
                      height: '100%',
                      background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(51, 65, 85, 0.8) 100%)',
                      backdropFilter: 'blur(10px)',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      borderRadius: 2,
                      position: 'relative',
                      overflow: 'hidden',
                      textAlign: 'center',
                    }}>
                      <CardContent sx={{ p: 2.5, position: 'relative', zIndex: 1 }}>
                        <Box sx={{
                          width: 50,
                          height: 50,
                          borderRadius: '50%',
                          background: 'linear-gradient(135deg, #60A5FA 0%, #A855F7 100%)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          mx: 'auto',
                          mb: 2,
                        }}>
                          <step.icon sx={{ color: '#FFFFFF', fontSize: 24 }} />
                        </Box>
                        <Typography variant="h6" sx={{
                          fontWeight: 600,
                          color: '#F1F5F9',
                          mb: 1,
                        }}>
                          {step.title}
                        </Typography>
                        <Typography variant="body2" sx={{
                          color: 'rgba(203, 213, 225, 0.8)',
                          fontSize: '0.875rem',
                          lineHeight: 1.4,
                        }}>
                          {step.description}
                        </Typography>
                      </CardContent>
                    </Card>
                  </motion.div>
                </Grid>
              ))}
            </Grid>
          </Box>

          <Divider sx={{ my: 3, backgroundColor: 'rgba(255, 255, 255, 0.1)' }} />

          {/* Manual vs AI Comparison */}
          <Box sx={{ mb: 4 }}>
            <Typography variant="h4" sx={{
              fontWeight: 700,
              color: '#F1F5F9',
              mb: 3,
              textAlign: 'center',
            }}>
              Manual Grind vs AI-First Backlinking
            </Typography>

            <Typography variant="body1" sx={{
              color: 'rgba(203, 213, 225, 0.9)',
              textAlign: 'center',
              mb: 3,
              maxWidth: 600,
              mx: 'auto',
            }}>
              ALwrity Backlinker revolutionizes traditional backlinking by automating research, outreach, and analysis with powerful AI.
            </Typography>

            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Card sx={{
                  height: '100%',
                  background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.1) 100%)',
                  border: '1px solid rgba(239, 68, 68, 0.3)',
                  borderRadius: 2,
                }}>
                  <CardContent sx={{ p: 3 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                      <Avatar sx={{
                        bgcolor: 'rgba(239, 68, 68, 0.2)',
                        border: '1px solid rgba(239, 68, 68, 0.4)',
                      }}>
                        <GlobeIcon sx={{ color: '#EF4444' }} />
                      </Avatar>
                      <Typography variant="h6" sx={{ fontWeight: 600, color: '#F1F5F9' }}>
                        Traditional Manual Backlinking
                      </Typography>
                    </Box>
                    <Box sx={{ spaceY: 2 }}>
                      {manualVsAI.map((item, index) => (
                        <Box key={index} sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, mb: 1.5 }}>
                          <XCircleIcon sx={{ color: '#EF4444', fontSize: 16, mt: 0.5, flexShrink: 0 }} />
                          <Typography variant="body2" sx={{ color: 'rgba(203, 213, 225, 0.8)', fontSize: '0.875rem' }}>
                            {item.manual}
                          </Typography>
                        </Box>
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={6}>
                <Card sx={{
                  height: '100%',
                  background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%)',
                  border: '1px solid rgba(16, 185, 129, 0.3)',
                  borderRadius: 2,
                }}>
                  <CardContent sx={{ p: 3 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                      <Avatar sx={{
                        bgcolor: 'rgba(16, 185, 129, 0.2)',
                        border: '1px solid rgba(16, 185, 129, 0.4)',
                      }}>
                        <BrainIcon sx={{ color: '#10B981' }} />
                      </Avatar>
                      <Typography variant="h6" sx={{ fontWeight: 600, color: '#F1F5F9' }}>
                        ALwrity AI-First Backlinker
                      </Typography>
                    </Box>
                    <Box sx={{ spaceY: 2 }}>
                      {manualVsAI.map((item, index) => (
                        <Box key={index} sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, mb: 1.5 }}>
                          <CheckCircleIcon sx={{ color: '#10B981', fontSize: 16, mt: 0.5, flexShrink: 0 }} />
                          <Typography variant="body2" sx={{ color: 'rgba(203, 213, 225, 0.8)', fontSize: '0.875rem' }}>
                            {item.ai}
                          </Typography>
                        </Box>
                      ))}
                    </Box>

                    <Divider sx={{ my: 2, backgroundColor: 'rgba(255, 255, 255, 0.1)' }} />

                    <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 1.5 }}>
                      {[
                        { icon: NetworkIcon, label: "Prospects refined by AI" },
                        { icon: EmailIcon, label: "Personalized outreach at scale" },
                        { icon: BarChartIcon, label: "Replies analyzed for collabs" }
                      ].map((k, i) => (
                        <Box key={i} sx={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: 1,
                          p: 1.5,
                          borderRadius: 1,
                          background: 'rgba(16, 185, 129, 0.1)',
                          border: '1px solid rgba(16, 185, 129, 0.2)',
                        }}>
                          <k.icon sx={{ color: '#10B981', fontSize: 16 }} />
                          <Typography variant="caption" sx={{ color: 'rgba(203, 213, 225, 0.9)', fontSize: '0.75rem' }}>
                            {k.label}
                          </Typography>
                        </Box>
                      ))}
                    </Box>

                    <Typography variant="caption" sx={{
                      color: 'rgba(203, 213, 225, 0.7)',
                      fontSize: '0.7rem',
                      mt: 1.5,
                      display: 'block',
                    }}>
                      Includes human-in-the-loop reviews for final send and approvals.
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>

          <Divider sx={{ my: 3, backgroundColor: 'rgba(255, 255, 255, 0.1)' }} />

          {/* Features Grid */}
          <Box sx={{ mb: 4 }}>
            <Typography variant="h4" sx={{
              fontWeight: 700,
              color: '#F1F5F9',
              mb: 3,
              textAlign: 'center',
            }}>
              Powered by Advanced AI
            </Typography>

            <Typography variant="body1" sx={{
              color: 'rgba(203, 213, 225, 0.9)',
              textAlign: 'center',
              mb: 4,
              maxWidth: 600,
              mx: 'auto',
            }}>
              Every feature is enhanced with machine learning algorithms to maximize your backlinking success
            </Typography>

            <Grid container spacing={3}>
              {features.map((feature, index) => (
                <Grid item xs={12} sm={6} lg={4} key={index}>
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1, duration: 0.5 }}
                  >
                    <Card sx={{
                      height: '100%',
                      background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(51, 65, 85, 0.8) 100%)',
                      backdropFilter: 'blur(10px)',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      borderRadius: 2,
                      position: 'relative',
                      overflow: 'hidden',
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        transition: 'transform 0.3s ease',
                      },
                    }}>
                      <CardContent sx={{ p: 3, position: 'relative', zIndex: 1 }}>
                        <Box sx={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: 2,
                          mb: 2,
                        }}>
                          <Box sx={{
                            p: 1.5,
                            borderRadius: 2,
                            background: feature.gradient,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                          }}>
                            <feature.icon sx={{ color: '#FFFFFF', fontSize: 24 }} />
                          </Box>
                        </Box>
                        <Typography variant="h6" sx={{
                          fontWeight: 600,
                          color: '#F1F5F9',
                          mb: 1.5,
                        }}>
                          {feature.title}
                        </Typography>
                        <Typography variant="body2" sx={{
                          color: 'rgba(203, 213, 225, 0.8)',
                          lineHeight: 1.5,
                        }}>
                          {feature.description}
                        </Typography>
                      </CardContent>
                    </Card>
                  </motion.div>
                </Grid>
              ))}
            </Grid>
          </Box>

          {/* Stats Section */}
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Typography variant="h5" sx={{
              fontWeight: 700,
              color: '#F1F5F9',
              mb: 3,
            }}>
              Proven Results
            </Typography>

            <Grid container spacing={2} sx={{ maxWidth: 400, mx: 'auto' }}>
              {[
                { number: "10,000+", label: "Opportunities Found" },
                { number: "85%", label: "Response Rate" },
                { number: "3x", label: "Faster Outreach" }
              ].map((stat, index) => (
                <Grid item xs={4} key={index}>
                  <Box sx={{
                    p: 2,
                    borderRadius: 2,
                    background: 'rgba(96, 165, 250, 0.1)',
                    border: '1px solid rgba(96, 165, 250, 0.2)',
                  }}>
                    <Typography variant="h4" sx={{
                      fontWeight: 800,
                      color: '#60A5FA',
                      mb: 0.5,
                    }}>
                      {stat.number}
                    </Typography>
                    <Typography variant="caption" sx={{
                      color: 'rgba(203, 213, 225, 0.7)',
                      fontSize: '0.75rem',
                      fontWeight: 500,
                    }}>
                      {stat.label}
                    </Typography>
                  </Box>
                </Grid>
              ))}
            </Grid>
          </Box>
        </Box>
      </DialogContent>

      <DialogActions sx={{
        p: 3,
        pt: 2,
        borderTop: '1px solid rgba(255, 255, 255, 0.1)',
        justifyContent: 'space-between',
      }}>
        <Typography variant="body2" sx={{ color: 'rgba(203, 213, 225, 0.7)' }}>
          Need more help? Check our documentation or contact support.
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            onClick={onClose}
            variant="outlined"
            sx={{
              borderColor: 'rgba(255, 255, 255, 0.2)',
              color: '#F1F5F9',
              '&:hover': {
                borderColor: '#60A5FA',
                bgcolor: 'rgba(96, 165, 250, 0.1)',
              },
            }}
          >
            Close
          </Button>
          <Button
            variant="contained"
            startIcon={<ArrowRightIcon sx={{ color: '#FFFFFF' }} />}
            sx={{
              background: 'linear-gradient(135deg, #60A5FA 0%, #A855F7 100%)',
              '&:hover': {
                background: 'linear-gradient(135deg, #3B82F6 0%, #9333EA 100%)',
              },
            }}
          >
            Get Started
          </Button>
        </Box>
      </DialogActions>
    </Dialog>
  );
};

export default BacklinkingHelpModal;