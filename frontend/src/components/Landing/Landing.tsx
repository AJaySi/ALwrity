import React, { Suspense, lazy } from 'react';
import usePerformanceMonitor from '../../hooks/usePerformanceMonitor';
import { 
  Box, 
  Button, 
  Container, 
  Typography, 
  Stack, 
  Grid, 
  Card, 
  CardContent,
  Chip,
  Avatar,
  useTheme,
  alpha,
  CircularProgress
} from '@mui/material';
import { keyframes } from '@mui/system';
import { SignInButton } from '@clerk/clerk-react';
import {
  AutoAwesome,
  Speed,
  TrendingUp,
  Security,
  Analytics,
  Psychology,
  AccessTime,
  MonetizationOn,
  TrendingDown,
  Group,
  CalendarToday,
  Create,
  Publish,
  Chat,
  Refresh,
  OpenInNew
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import HeroSection from './HeroSection';

// Lazy load components for better performance
const FeatureShowcase = lazy(() => import('./FeatureShowcase'));
const SolopreneurDilemma = lazy(() => import('./SolopreneurDilemma'));
const EnterpriseCTA = lazy(() => import('./EnterpriseCTA'));
const IntroducingAlwrity = lazy(() => import('./IntroducingAlwrity'));

const Landing: React.FC = () => {
  const theme = useTheme();
  
  // Monitor performance
  usePerformanceMonitor('Landing');

  // Optimized Framer Motion variants for better performance
  const fadeInUp = {
    hidden: { opacity: 0, y: 24 },
    visible: { 
      opacity: 1, 
      y: 0, 
      transition: { 
        duration: 0.4, 
        ease: "easeOut" as const,
        // Use transform3d for hardware acceleration
        transform: "translate3d(0,0,0)"
      } 
    },
  };

  const stagger = {
    hidden: {},
    visible: { 
      transition: { 
        staggerChildren: 0.08, // Reduced stagger time
        delayChildren: 0.1 
      } 
    },
  };

  // Cinematic lifecycle section animations
  const backgroundFade = {
    hidden: { opacity: 0 },
    visible: { 
      opacity: 1,
      transition: { duration: 1, ease: "easeInOut" as const }
    }
  };

  const titleFlyIn = {
    hidden: { opacity: 0, y: -80, scale: 0.8 },
    visible: { 
      opacity: 1, 
      y: 0,
      scale: 1,
      transition: { 
        delay: 1,
        duration: 0.8, 
        ease: [0.22, 1, 0.36, 1] as const // Custom easing
      }
    }
  };

  const chipsFlyIn = {
    hidden: { opacity: 0, y: 60 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { 
        delay: 1.3,
        duration: 0.7,
        ease: "easeOut" as const
      }
    }
  };

  const descriptionFade = {
    hidden: { opacity: 0 },
    visible: { 
      opacity: 1,
      transition: { 
        delay: 1.6,
        duration: 0.6
      }
    }
  };

  // Card zoom animations from different directions
  const cardVariants = [
    // Top-left
    { 
      hidden: { opacity: 0, scale: 0.3, x: -200, y: -200, rotate: -15 },
      visible: { opacity: 1, scale: 1, x: 0, y: 0, rotate: 0 }
    },
    // Top
    { 
      hidden: { opacity: 0, scale: 0.3, y: -250, rotate: 0 },
      visible: { opacity: 1, scale: 1, y: 0, rotate: 0 }
    },
    // Top-right
    { 
      hidden: { opacity: 0, scale: 0.3, x: 200, y: -200, rotate: 15 },
      visible: { opacity: 1, scale: 1, x: 0, y: 0, rotate: 0 }
    },
    // Bottom-left
    { 
      hidden: { opacity: 0, scale: 0.3, x: -200, y: 200, rotate: 15 },
      visible: { opacity: 1, scale: 1, x: 0, y: 0, rotate: 0 }
    },
    // Bottom
    { 
      hidden: { opacity: 0, scale: 0.3, y: 250, rotate: 0 },
      visible: { opacity: 1, scale: 1, y: 0, rotate: 0 }
    },
    // Bottom-right
    { 
      hidden: { opacity: 0, scale: 0.3, x: 200, y: 200, rotate: -15 },
      visible: { opacity: 1, scale: 1, x: 0, y: 0, rotate: 0 }
    }
  ];

  const cardsStagger = {
    hidden: {},
    visible: {
      transition: {
        delayChildren: 2,
        staggerChildren: 0.15
      }
    }
  };

  const features = [
    {
      icon: <CalendarToday />,
      title: 'Content Planning',
      description: 'ALwrity builds a living strategy and calendar from your goals, audience and market signals. Drag-and-drop calendar, briefs, topics and distribution plans generated automatically.',
      badge: 'Strategy'
    },
    {
      icon: <Create />,
      title: 'Content Generation',
      description: 'Generate text, images, audio, video and channel-ready posts for LinkedIn, Facebook, Instagram and blogs. Templates, brand voice and Personas baked in.',
      badge: 'Multi‑Format'
    },
    {
      icon: <Publish />,
      title: 'Content Publishing',
      description: 'Publish and schedule directly to connected social channels and your website. One-click cross‑posting while preserving native formats.',
      badge: 'Automated'
    },
    {
      icon: <Analytics />,
      title: 'Content Analytics',
      description: 'Pulls analytics from connected platforms, analyzes with AI and surfaces actionable insights. Signals flow back to strategy and calendar for adaptive learning.',
      badge: 'AI Insights'
    },
    {
      icon: <Chat />,
      title: 'Content Engagement',
      description: 'Monitor comments, DMs and reactions. Research communities and reply with AI assistance from within ALwrity to grow audience authentically.',
      badge: 'Community'
    },
    {
      icon: <Refresh />,
      title: 'Content Remarketing',
      description: 'Analyzes historic performance, suggests edits, variants and redistribution. Measures KPI attainment and explains what worked—and what did not.',
      badge: 'Optimization'
    }
  ];


  const painPoints = [
    {
      icon: <AccessTime />,
      title: 'Time Constraints',
      description: 'Limited time for content creation and strategy development. Solopreneurs wear many hats and struggle to maintain consistent content output.'
    },
    {
      icon: <TrendingDown />,
      title: 'Lack of Expertise',
      description: 'Not trained as content strategists, SEO experts, or data analysts. Missing the knowledge to create effective marketing campaigns.'
    },
    {
      icon: <MonetizationOn />,
      title: 'Resource Limitations',
      description: 'Cannot afford full marketing teams or expensive enterprise tools. Need cost-effective solutions that deliver professional results.'
    },
    {
      icon: <Analytics />,
      title: 'Poor ROI Tracking',
      description: 'Only 21% of marketers successfully track content ROI. Lack of data-driven insights to optimize marketing spend and strategy.'
    },
    {
      icon: <Group />,
      title: 'Manual Processes',
      description: 'Overwhelmed by repetitive content creation tasks. Need automation to scale efforts without sacrificing quality.'
    },
    {
      icon: <Psychology />,
      title: 'Inconsistent Voice',
      description: 'Struggle to maintain brand voice across platforms. Need personalized AI that understands your unique style and messaging.'
    }
  ];



  // Glassmorphism styles
  const glassPanelSx = {
    background: `linear-gradient(135deg, ${alpha(theme.palette.common.white, 0.06)} 0%, ${alpha(theme.palette.common.white, 0.02)} 100%)`,
    backdropFilter: 'blur(12px)',
    border: '1px solid rgba(255,255,255,0.12)',
    borderRadius: 4,
    boxShadow: '0 10px 30px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.06)'
  } as const;

  const glassCardSx = {
    background: `linear-gradient(135deg, ${alpha(theme.palette.common.white, 0.05)} 0%, ${alpha(theme.palette.common.white, 0.015)} 100%)`,
    backdropFilter: 'blur(14px)',
    border: '1px solid rgba(255,255,255,0.12)',
    borderRadius: 3,
    boxShadow: '0 10px 25px rgba(0,0,0,0.28), inset 0 1px 0 rgba(255,255,255,0.06)',
    p: 0
  } as const;

  // Shimmer animation for lifecycle chip line
  const shimmer = keyframes`
    0% { background-position: 0% 50%; }
    100% { background-position: 100% 50%; }
  `;

  // Glow pulse animation for chips
  const glowPulse = keyframes`
    0%, 100% { 
      box-shadow: 0 0 10px ${alpha(theme.palette.primary.main, 0.3)}, 
                  0 0 20px ${alpha(theme.palette.primary.main, 0.2)},
                  inset 0 0 10px ${alpha(theme.palette.primary.main, 0.1)};
    }
    50% { 
      box-shadow: 0 0 20px ${alpha(theme.palette.primary.main, 0.6)}, 
                  0 0 30px ${alpha(theme.palette.primary.main, 0.4)},
                  inset 0 0 15px ${alpha(theme.palette.primary.main, 0.2)};
    }
  `;

  // Slide in animation for lifecycle image
  const slideIn = keyframes`
    0% { opacity: 0; transform: scale(0.9) translateY(20px); }
    100% { opacity: 1; transform: scale(1) translateY(0); }
  `;

  // Loading component for Suspense
  const LoadingSpinner = () => (
    <Box 
      sx={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        py: 8,
        minHeight: '200px'
      }}
    >
      <CircularProgress size={40} />
    </Box>
  );

  return (
    <Box sx={{ minHeight: '100vh', overflow: 'hidden', position: 'relative' }}>
      {/* Hero Section - Extracted to separate component */}
      <HeroSection />

      {/* Lifecycle Section with Background Image */}
      <Box
        sx={{
          position: 'relative',
          minHeight: '100vh',
          py: 12,
          overflow: 'hidden'
        }}
      >
        {/* Background Image Layer */}
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.1 }}
          variants={backgroundFade}
        >
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundImage: 'url(/content_lifecycle.png)',
              backgroundSize: 'cover',
              backgroundPosition: 'center',
              backgroundRepeat: 'no-repeat',
              zIndex: 0
            }}
          />
          {/* Dark overlay for readability */}
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: `linear-gradient(
                135deg, 
                rgba(0,0,0,0.85) 0%, 
                rgba(0,0,0,0.75) 50%,
                rgba(0,0,0,0.85) 100%
              )`,
              backdropFilter: 'blur(2px)',
              zIndex: 1
            }}
          />
        </motion.div>

        {/* Content Layer */}
        <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 2 }}>
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.1 }}
          >
            <Stack spacing={8} alignItems="center">
              {/* Title */}
              <motion.div variants={titleFlyIn} style={{ width: '100%' }}>
                <Stack spacing={3} alignItems="center" textAlign="center">
                  <Typography 
                    variant="h2" 
                    fontWeight={700}
                    sx={{
                      color: 'white',
                      textShadow: `0 0 30px ${alpha(theme.palette.primary.main, 0.5)}, 0 4px 20px rgba(0,0,0,0.8)`
                    }}
                  >
                    ALwrity Content Lifecycle
                  </Typography>
                  <Typography 
                    variant="h5" 
                    fontWeight={600}
                    sx={{
                      color: alpha('#fff', 0.9),
                      textShadow: '0 2px 10px rgba(0,0,0,0.6)'
                    }}
                  >
                    End‑to‑End, HITL by Design
                  </Typography>
                </Stack>
              </motion.div>

              {/* Phases chips with animated connector */}
              <motion.div variants={chipsFlyIn} style={{ width: '100%' }}>
                <Box sx={{ position: 'relative', width: '100%', maxWidth: 1100, px: { xs: 2, md: 4 }, py: 2 }}>
                  {/* animated line */}
                  <Box
                    sx={{
                      position: 'absolute',
                      top: { xs: 28, md: 32 },
                      left: 0,
                      right: 0,
                      height: 3,
                      borderRadius: 2,
                      background: `linear-gradient(90deg, 
                        ${alpha(theme.palette.primary.main, 0.4)}, 
                        ${alpha(theme.palette.secondary.main, 0.5)}, 
                        ${alpha(theme.palette.primary.main, 0.4)})`,
                      overflow: 'hidden',
                      boxShadow: `0 0 20px ${alpha(theme.palette.primary.main, 0.6)}`
                    }}
                  >
                    <Box
                      sx={{
                        width: '40%',
                        height: '100%',
                        background: `linear-gradient(90deg, 
                          transparent, 
                          ${alpha(theme.palette.primary.main, 1)}, 
                          ${alpha(theme.palette.secondary.main, 1)},
                          transparent)`,
                        backgroundSize: '200% 100%',
                        animation: `${shimmer} 3s ease-in-out infinite`
                      }}
                    />
                  </Box>
                  {/* chips */}
                  <Grid container spacing={{ xs: 1, md: 2 }} justifyContent="space-between" alignItems="center">
                    {['Plan','Generate','Publish','Analyze','Engage','Remarket'].map((label, idx) => (
                      <Grid item key={label} xs={2} sx={{ display: 'flex', justifyContent: idx === 0 ? 'flex-start' : idx === 5 ? 'flex-end' : 'center' }}>
                        <Chip 
                          label={
                            <Stack direction="row" spacing={0.5} alignItems="center">
                              <Typography 
                                variant="caption" 
                                sx={{ 
                                  fontWeight: 800, 
                                  fontSize: { xs: '0.65rem', md: '0.75rem' },
                                  color: 'primary.main'
                                }}
                              >
                                {idx+1}
                              </Typography>
                              <Typography 
                                variant="caption" 
                                sx={{ 
                                  fontWeight: 700, 
                                  fontSize: { xs: '0.7rem', md: '0.8rem' },
                                  color: 'white'
                                }}
                              >
                                {label}
                              </Typography>
                            </Stack>
                          }
                          size="medium"
                          sx={{
                            px: { xs: 1, md: 2 },
                            py: { xs: 1.5, md: 2 },
                            fontWeight: 700,
                            letterSpacing: 0.5,
                            background: `linear-gradient(135deg, 
                              ${alpha(theme.palette.primary.main, 0.3)}, 
                              ${alpha(theme.palette.secondary.main, 0.3)})`,
                            border: `2px solid ${alpha(theme.palette.primary.main, 0.6)}`,
                            backdropFilter: 'blur(12px)',
                            animation: `${glowPulse} 3s ease-in-out infinite`,
                            animationDelay: `${idx * 0.3}s`,
                            transition: 'all 0.3s ease',
                            '&:hover': {
                              transform: 'scale(1.1) translateY(-2px)',
                              background: `linear-gradient(135deg, 
                                ${alpha(theme.palette.primary.main, 0.5)}, 
                                ${alpha(theme.palette.secondary.main, 0.5)})`,
                              boxShadow: `0 8px 30px ${alpha(theme.palette.primary.main, 0.7)}`
                            }
                          }}
                        />
                      </Grid>
                    ))}
                  </Grid>
                </Box>
              </motion.div>

              {/* Description */}
              <motion.div variants={descriptionFade}>
                <Typography 
                  variant="h6" 
                  color={alpha('#fff', 0.9)}
                  maxWidth="900px"
                  textAlign="center"
                  sx={{
                    textShadow: '0 2px 10px rgba(0,0,0,0.6)',
                    lineHeight: 1.8
                  }}
                >
                  ALwrity automates each phase with AI while you review and approve as the human‑in‑the‑loop.
                </Typography>
              </motion.div>

              {/* Cards with zoom animations */}
              <motion.div
                variants={cardsStagger}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true, amount: 0.1 }}
                style={{ width: '100%' }}
              >
                <Grid container spacing={2.5}>
                  {features.map((feature, index) => (
                    <Grid item xs={12} md={6} lg={4} key={index}>
                      <motion.div
                        variants={cardVariants[index]}
                        transition={{
                          duration: 0.6,
                          ease: [0.25, 0.46, 0.45, 0.94]
                        }}
                      >
                        <Card 
                          sx={{ 
                            ...glassCardSx, 
                            height: '100%', 
                            background: `linear-gradient(135deg, ${alpha(theme.palette.common.white, 0.08)} 0%, ${alpha(theme.palette.common.white, 0.03)} 100%)`,
                            backdropFilter: 'blur(20px)',
                            border: `1px solid ${alpha(theme.palette.common.white, 0.15)}`,
                            transition: 'all 0.25s ease', 
                            '&:hover': { 
                              transform: 'translateY(-6px)', 
                              boxShadow: `0 24px 48px ${alpha(theme.palette.primary.main, 0.25)}`, 
                              borderColor: alpha(theme.palette.primary.main, 0.4) 
                            } 
                          }}
                        >
                          <CardContent sx={{ p: 3 }}>
                            <Stack spacing={2}>
                              <Stack direction="row" justifyContent="space-between" alignItems="center">
                                <Avatar
                                  sx={{
                                    width: 44,
                                    height: 44,
                                    borderRadius: 2,
                                    background: `linear-gradient(45deg, ${alpha(theme.palette.primary.main, 0.25)}, ${alpha(theme.palette.secondary.main, 0.25)})`,
                                    color: theme.palette.primary.main
                                  }}
                                >
                                  {feature.icon}
                                </Avatar>
                                <Chip 
                                  label={feature.badge} 
                                  size="small" 
                                  sx={{ 
                                    background: alpha(theme.palette.primary.main, 0.2),
                                    color: theme.palette.primary.main,
                                    fontWeight: 600,
                                    backdropFilter: 'blur(10px)'
                                  }} 
                                />
                              </Stack>
                              <Stack spacing={1.25}>
                                <Typography variant="h6" fontWeight={700} sx={{ fontSize: '1.05rem', color: 'white' }}>
                                  {feature.title}
                                </Typography>
                                <Typography variant="body2" color={alpha('#fff', 0.85)} lineHeight={1.6} sx={{ fontSize: '0.93rem' }}>
                                  {feature.description}
                                </Typography>
                              </Stack>
                              <Box sx={{ pt: 0.5 }}>
                                <Button 
                                  size="small" 
                                  endIcon={<OpenInNew sx={{ fontSize: 16 }} />} 
                                  sx={{
                                    textTransform: 'none',
                                    fontWeight: 600,
                                    px: 0,
                                    minWidth: 0,
                                    color: theme.palette.primary.main,
                                    '&:hover': {
                                      color: theme.palette.primary.light
                                    }
                                  }}
                                  href="#"
                                >
                                  Learn more
                                </Button>
                              </Box>
                            </Stack>
                          </CardContent>
                        </Card>
                      </motion.div>
                    </Grid>
                  ))}
                </Grid>
              </motion.div>
            </Stack>
          </motion.div>
        </Container>
      </Box>

      {/* Feature Showcase with Carousel - Lazy Loaded */}
      <Suspense fallback={<LoadingSpinner />}>
        <FeatureShowcase />
      </Suspense>

      {/* The Solopreneur's Dilemma Section - Lazy Loaded */}
      <Suspense fallback={<LoadingSpinner />}>
        <SolopreneurDilemma />
      </Suspense>

      {/* Introducing ALwrity Section with Background - Lazy Loaded */}
      <Suspense fallback={<LoadingSpinner />}>
        <IntroducingAlwrity />
      </Suspense>

      {/* Final CTA Section - Lazy Loaded */}
      <Suspense fallback={<LoadingSpinner />}>
        <EnterpriseCTA />
      </Suspense>
    </Box>
  );
};

export default Landing;


