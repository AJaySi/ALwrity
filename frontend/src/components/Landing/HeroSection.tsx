import React from 'react';
import { 
  Box, 
  Button, 
  Container, 
  Typography, 
  Stack, 
  Grid, 
  Chip,
  useTheme,
  alpha
} from '@mui/material';
import { SignInButton, useClerk } from '@clerk/clerk-react';
import {
  RocketLaunch,
  Lightbulb,
  Verified,
  Security,
  Shield,
  CloudDone,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { ScrambleText } from '../ScrambleText';

// Scrambling text component with multiple phrases
const ScramblingText: React.FC<{ phrases: string[]; interval?: number; duration?: number; delay?: number }> = ({ 
  phrases, 
  interval = 4000,
  duration = 800,
  delay = 200
}) => {
  const [currentIndex, setCurrentIndex] = React.useState(0);

  React.useEffect(() => {
    const timer = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % phrases.length);
    }, interval);
    return () => clearInterval(timer);
  }, [phrases.length, interval]);

  return (
    <ScrambleText
      text={phrases[currentIndex]}
      duration={duration}
      delay={delay}
      restartInterval={interval}
      as="span"
      className="scramble-text"
      style={{
        color: '#fff',
        fontWeight: 900,
        textShadow: `
          0 2px 10px rgba(0, 0, 0, 0.9),
          0 4px 20px rgba(0, 0, 0, 0.7),
          0 0 40px rgba(102, 126, 234, 0.4)
        `,
      }}
    />
  );
};

const HeroSection: React.FC = () => {
  const theme = useTheme();

  const { openSignIn } = useClerk();

  const fadeInUp = {
    hidden: { opacity: 0, y: 24 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" as const } },
  };

  const stagger = {
    hidden: {},
    visible: { transition: { staggerChildren: 0.12 } },
  };

  const stats = [
    { value: '70%', label: 'Time Savings' },
    { value: '65%', label: 'Better Engagement' },
    { value: '5x', label: 'Faster Publishing' },
    { value: '21%', label: 'More ROI Tracking' }
  ];

  const trustSignals = [
    { icon: <Security />, label: "Hyper Personalization" },
    { icon: <Shield />, label: "Hallucination Free" },
    { icon: <CloudDone />, label: "SME AI Platform" },
    { icon: <Verified />, label: "Connected Platforms" }
  ];

  const glassPanelSx = {
    background: `linear-gradient(135deg, ${alpha(theme.palette.common.white, 0.08)} 0%, ${alpha(theme.palette.common.white, 0.03)} 100%)`,
    backdropFilter: 'blur(16px) saturate(180%)',
    border: '1px solid rgba(255,255,255,0.15)',
    borderRadius: 4,
    boxShadow: '0 12px 40px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.08)'
  } as const;

  return (
    <Box sx={{ position: 'relative', bgcolor: '#000', color: theme.palette.getContrastText('#000'), overflow: 'hidden' }}>
      {/* Background Image */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundImage: 'url(/alwrity_landing_hero_bg.png)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          zIndex: 0,
        }}
      />

      {/* Dark Overlay for Better Readability */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: `
            linear-gradient(135deg, 
              rgba(0, 0, 0, 0.55) 0%, 
              rgba(0, 0, 0, 0.45) 50%, 
              rgba(0, 0, 0, 0.50) 100%
            )
          `,
          zIndex: 1,
        }}
      />

      {/* Subtle Gradient Enhancement */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: `
            radial-gradient(circle at 50% 50%, ${alpha(theme.palette.primary.main, 0.10)} 0%, transparent 60%),
            radial-gradient(circle at 20% 80%, ${alpha(theme.palette.secondary.main, 0.08)} 0%, transparent 50%)
          `,
          zIndex: 2,
        }}
      />

      {/* Hero Content */}
      <Container maxWidth="lg" sx={{ pt: 10, pb: 6, position: 'relative', zIndex: 3 }}>
        <motion.div variants={stagger} initial="hidden" animate="visible">
          <Stack spacing={6} alignItems="center" textAlign="center">
            {/* Main Headline */}
            <motion.div variants={fadeInUp}>
              <Stack spacing={3} alignItems="center">
                <Stack direction="row" spacing={2} alignItems="center" flexWrap="wrap" justifyContent="center">
                  <Chip
                    icon={<RocketLaunch />}
                    label="AI Marketing Platform"
                    variant="outlined"
                    sx={{
                      background: alpha(theme.palette.primary.main, 0.15),
                      borderColor: theme.palette.primary.main,
                      color: theme.palette.primary.light,
                      fontWeight: 600,
                      fontSize: '0.9rem'
                    }}
                  />
                  <Chip
                    icon={<Verified />}
                    label="AI-First Copilot"
                    variant="outlined"
                    sx={{
                      background: alpha(theme.palette.success.main, 0.15),
                      borderColor: theme.palette.success.main,
                      color: theme.palette.success.light,
                      fontWeight: 600,
                      fontSize: '0.9rem'
                    }}
                  />
                </Stack>
                
                <Typography 
                  variant="h1" 
                  component="h1" 
                  sx={{
                    fontSize: { xs: '2.8rem', md: '4.5rem', lg: '5.5rem' },
                    fontWeight: 900,
                    letterSpacing: '-0.03em',
                    lineHeight: 1.05,
                    mb: 2,
                    color: '#fff',
                    // Enhanced text shadow for better readability
                    textShadow: `
                      0 2px 10px rgba(0, 0, 0, 0.8),
                      0 4px 20px rgba(0, 0, 0, 0.6),
                      0 0 40px rgba(102, 126, 234, 0.3)
                    `,
                  }}
                >
                  Enterprise AI for{' '}
                  <ScramblingText 
                    phrases={['Content Planning', 'MultiModal Generation', 'Cross Platform Publishing', 'All-Analytics One-platform', 'Content Engagement', 'Content Remarketing']}
                  />
                </Typography>

                <Typography 
                  variant="h4" 
                  sx={{
                    fontSize: { xs: '1.2rem', md: '1.5rem' },
                    fontWeight: 500,
                    maxWidth: '950px',
                    lineHeight: 1.5,
                    mb: 3,
                    color: 'rgba(255, 255, 255, 0.92)',
                    // Enhanced text shadow for description
                    textShadow: `
                      0 2px 8px rgba(0, 0, 0, 0.8),
                      0 4px 16px rgba(0, 0, 0, 0.5)
                    `,
                  }}
                >
                  AI-powered marketing copilot that learns your brand voice, analyzes competitors, 
                  and creates hyper-personalized content strategies. Built for solopreneurs and SMEs 
                  who want enterprise-level AI without the enterprise complexity.
                </Typography>

                {/* Trust Signals */}
                <Stack 
                  direction="row" 
                  spacing={3} 
                  alignItems="center" 
                  flexWrap="wrap" 
                  justifyContent="center" 
                  sx={{ mt: 2 }}
                >
                  {trustSignals.map((signal, index) => (
                    <Stack 
                      key={index} 
                      direction="row" 
                      spacing={1} 
                      alignItems="center"
                      sx={{
                        // Add background for better visibility
                        background: 'rgba(0, 0, 0, 0.3)',
                        backdropFilter: 'blur(8px)',
                        px: 2,
                        py: 1,
                        borderRadius: 2,
                        border: '1px solid rgba(255, 255, 255, 0.1)',
                      }}
                    >
                      <Box sx={{ color: theme.palette.success.light }}>{signal.icon}</Box>
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          color: 'rgba(255, 255, 255, 0.95)', 
                          fontWeight: 600,
                          textShadow: '0 2px 4px rgba(0, 0, 0, 0.6)'
                        }}
                      >
                        {signal.label}
                      </Typography>
                    </Stack>
                  ))}
                </Stack>
              </Stack>
            </motion.div>

            {/* Glass CTA Panel */}
            <motion.div variants={fadeInUp}>
              <Box sx={{ ...glassPanelSx, px: { xs: 3, md: 5 }, py: { xs: 4, md: 6 }, maxWidth: 1000, width: '100%' }}>
                <Stack spacing={4} alignItems="center">
                  <Button 
                    onClick={() => openSignIn({ forceRedirectUrl: '/' })}
                    variant="contained" 
                    size="large"
                    startIcon={<Lightbulb />}
                    sx={{
                      py: 2.5,
                      px: 5,
                      fontSize: '1.2rem',
                      fontWeight: 700,
                      borderRadius: 3,
                      background: 'linear-gradient(45deg, #667eea 30%, #764ba2 90%)',
                      backgroundImage: `
                        linear-gradient(120deg, transparent 0%, rgba(255,255,255,0.3) 50%, transparent 100%),
                        linear-gradient(45deg, #667eea 30%, #764ba2 90%)
                      `,
                      backgroundSize: '200% 100%, 100% 100%',
                      backgroundPosition: '200% 0, 0 0',
                      boxShadow: '0 10px 40px rgba(102, 126, 234, 0.4)',
                      '&:hover': {
                        boxShadow: '0 15px 50px rgba(102, 126, 234, 0.5)',
                        transform: 'translateY(-3px)',
                        backgroundPosition: '0 0, 0 0'
                      },
                      transition: 'all 0.3s ease',
                      animation: 'shimmer 2.5s ease-in-out infinite',
                      '@keyframes shimmer': {
                        '0%': { backgroundPosition: '200% 0, 0 0' },
                        '100%': { backgroundPosition: '-200% 0, 0 0' }
                      }
                    }}
                  >
                    <ScramblingText 
                      phrases={['Start Free Trial', 'Get Started Now', 'Try AI Copilot', 'Boost ROI Now']}
                      interval={3000}
                    />
                  </Button>
                  
                  <Typography 
                    variant="body1" 
                    sx={{ 
                      color: 'rgba(255, 255, 255, 0.85)', 
                      fontWeight: 500,
                      textShadow: '0 2px 6px rgba(0, 0, 0, 0.7)'
                    }}
                  >
                    Bring Your Own Keys • No vendor lock-in • Enterprise security
                  </Typography>

                  {/* Stats Row with Mini Charts */}
                  <Grid container spacing={4} sx={{ mt: 1, mx: 'auto', maxWidth: '700px' }}>
                    {stats.map((stat, index) => (
                      <Grid item xs={6} md={3} key={index}>
                        <Stack alignItems="center" spacing={1.5}>
                          {/* Mini Progress Bar */}
                          <Box sx={{ width: '100%', maxWidth: 80 }}>
                            <Box
                              sx={{
                                height: 6,
                                borderRadius: 3,
                                background: 'rgba(255, 255, 255, 0.1)',
                                overflow: 'hidden',
                              }}
                            >
                              <Box
                                sx={{
                                  height: '100%',
                                  width: stat.value,
                                  background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
                                  borderRadius: 3,
                                  boxShadow: '0 0 10px rgba(102, 126, 234, 0.6)',
                                  animation: 'fillBar 1.5s ease-out',
                                  '@keyframes fillBar': {
                                    '0%': { width: '0%' },
                                    '100%': { width: stat.value },
                                  },
                                }}
                              />
                            </Box>
                          </Box>
                          
                          <Typography 
                            variant="h3" 
                            sx={{
                              fontWeight: 800,
                              color: '#fff',
                              textShadow: `
                                0 2px 8px rgba(0, 0, 0, 0.9),
                                0 0 20px rgba(102, 126, 234, 0.4)
                              `,
                            }}
                          >
                            {stat.value}
                          </Typography>
                          <Typography 
                            variant="body2" 
                            sx={{ 
                              color: 'rgba(255, 255, 255, 0.85)', 
                              fontWeight: 600,
                              textShadow: '0 2px 6px rgba(0, 0, 0, 0.8)',
                              fontSize: '0.85rem'
                            }}
                          >
                            {stat.label}
                          </Typography>
                        </Stack>
                      </Grid>
                    ))}
                  </Grid>
                </Stack>
              </Box>
            </motion.div>
          </Stack>
        </motion.div>
      </Container>

      {/* Bottom Fade Transition */}
      <Box 
        sx={{ 
          position: 'absolute', 
          left: 0, 
          right: 0, 
          bottom: -1, 
          height: 100, 
          background: `linear-gradient(180deg, rgba(0,0,0,0) 0%, ${alpha(theme.palette.background.default, 1)} 100%)`, 
          zIndex: 0 
        }} 
      />
    </Box>
  );
};

export default HeroSection;

