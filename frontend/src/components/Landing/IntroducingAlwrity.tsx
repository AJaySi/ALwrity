import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Button, 
  Container, 
  Typography, 
  Stack, 
  Grid,
  Card,
  CardContent,
  useTheme,
  alpha,
  Skeleton
} from '@mui/material';
import { SignInButton, useClerk } from '@clerk/clerk-react';
import {
  RocketLaunch,
  Business,
  ContentCopy,
  TrendingUp,
  People,
  Code,
  Security,
  Speed
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { ScrambleText } from '../ScrambleText';

// Scrambling text component for multiple phrases
const ScramblingText: React.FC<{ phrases: string[]; interval?: number; duration?: number; delay?: number }> = ({ 
  phrases, 
  interval = 4000,
  duration = 600,
  delay = 0
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
    />
  );
};

const IntroducingAlwrity: React.FC = () => {
  const theme = useTheme();
  const [imageLoaded, setImageLoaded] = useState(false);
  const { openSignIn } = useClerk();

  // Preload the background image
  useEffect(() => {
    const img = new Image();
    img.onload = () => setImageLoaded(true);
    img.src = '/alwrity_landing_bg_vortex.png';
  }, []);

  // Framer Motion variants
  const fadeInUp = {
    hidden: { opacity: 0, y: 24 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" as const } },
  };

  const stagger = {
    hidden: {},
    visible: { transition: { staggerChildren: 0.12 } },
  };

  // Platform capabilities instead of fake testimonials
  const platformCapabilities = [
    {
      icon: <Code />,
      title: 'Open Source Foundation',
      description: 'Built with transparency and community in mind. Full source code available on GitHub for inspection and contribution.',
      highlight: '100% Open Source'
    },
    {
      icon: <Security />,
      title: 'Privacy First',
      description: 'Your data stays yours. No tracking, no data mining, no selling of user information. Complete privacy protection.',
      highlight: 'Zero Tracking'
    },
    {
      icon: <Speed />,
      title: 'Lightning Fast',
      description: 'Optimized for speed and efficiency. Generate high-quality content in seconds, not minutes.',
      highlight: 'Sub-second Response'
    }
  ];

  const socialProofStats = [
    { icon: <Business />, value: "1K+", label: "GitHub Stars" },
    { icon: <ContentCopy />, value: "10K+", label: "Content Pieces Generated" },
    { icon: <TrendingUp />, value: "95%", label: "User Satisfaction" },
    { icon: <People />, value: "500+", label: "Active Contributors" }
  ];

  // Glassmorphism styles
  const glassCardSx = {
    background: `linear-gradient(135deg, ${alpha(theme.palette.common.white, 0.08)} 0%, ${alpha(theme.palette.common.white, 0.03)} 100%)`,
    backdropFilter: 'blur(16px)',
    border: '1px solid rgba(255,255,255,0.15)',
    borderRadius: 3,
    boxShadow: '0 15px 35px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.08)'
  } as const;

  return (
    <Box
      sx={{
        position: 'relative',
        minHeight: '100vh',
        backgroundImage: imageLoaded ? 'url(/alwrity_landing_bg_vortex.png)' : 'none',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
        backgroundColor: '#0a0a0a', // Fallback color
        transition: 'background-image 0.3s ease',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'linear-gradient(135deg, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.5) 100%)',
          zIndex: 1
        }
      }}
    >
      {/* Loading skeleton for background image */}
      {!imageLoaded && (
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            zIndex: 0
          }}
        >
          <Skeleton 
            variant="rectangular" 
            width="100%" 
            height="100%" 
            sx={{ bgcolor: 'rgba(255,255,255,0.1)' }}
          />
        </Box>
      )}
      {/* Solution Bridge Section */}
      <Container maxWidth="lg" sx={{ py: 8, position: 'relative', zIndex: 2 }}>
        <motion.div variants={stagger} initial="hidden" whileInView="visible" viewport={{ once: true, amount: 0.2 }}>
          <Stack spacing={6} alignItems="center" textAlign="center">
            <motion.div variants={fadeInUp}>
              <Typography variant="h3" fontWeight={700} sx={{ color: 'white' }}>
                <ScramblingText 
                  phrases={['Introducing ALwrity', 'Welcome to ALwrity', 'Meet ALwrity', 'Discover ALwrity']}
                  duration={600}
                  delay={1000}
                  interval={5000}
                />
              </Typography>
            </motion.div>
            <motion.div variants={fadeInUp}>
              <Typography variant="h5" color="rgba(255,255,255,0.9)" maxWidth="800px">
                Transform from a manual implementer to a strategic director. 
                ALwrity automates the entire content strategy process with AI-powered intelligence.
              </Typography>
            </motion.div>
            
            <motion.div variants={fadeInUp}>
              <Box sx={{ mt: 4 }}>
                  <Button 
                    onClick={() => openSignIn({ forceRedirectUrl: '/' })}
                    variant="contained" 
                    size="large"
                    startIcon={<RocketLaunch />}
                    sx={{
                      py: 2,
                      px: 6,
                      fontSize: '1.2rem',
                      fontWeight: 600,
                      borderRadius: 2,
                      background: 'linear-gradient(45deg, #667eea 30%, #764ba2 90%)',
                      boxShadow: '0 8px 32px rgba(102, 126, 234, 0.3)',
                      '&:hover': {
                        boxShadow: '0 12px 40px rgba(102, 126, 234, 0.4)',
                        transform: 'translateY(-2px)'
                      },
                      transition: 'all 0.3s ease'
                    }}
                  >
                    <ScramblingText
                      phrases={['Start Your AI Journey', 'Begin AI Transformation', 'Launch AI Success', 'Start AI Revolution']}
                      duration={500}
                      delay={300}
                      interval={3500}
                    />
                  </Button>
              </Box>
            </motion.div>
          </Stack>
        </motion.div>
      </Container>

      {/* Platform Capabilities Section */}
      <Container maxWidth="lg" sx={{ py: 8, position: 'relative', zIndex: 2 }}>
        <motion.div variants={stagger} initial="hidden" whileInView="visible" viewport={{ once: true, amount: 0.2 }}>
          <Stack spacing={6} alignItems="center">
            <motion.div variants={fadeInUp}>
              <Stack spacing={2} alignItems="center" textAlign="center">
                <Typography variant="h3" fontWeight={700} sx={{ color: 'white' }}>
                  Why Choose ALwrity?
                </Typography>
                <Typography variant="h6" color="rgba(255,255,255,0.9)" maxWidth="700px">
                  Built for creators, by creators. Open-source, privacy-focused, and designed to scale with your ambitions.
                </Typography>
              </Stack>
            </motion.div>

            <Grid container spacing={4}>
              {platformCapabilities.map((capability, index) => (
                <Grid item xs={12} md={4} key={index}>
                  <motion.div variants={fadeInUp}>
                    <Card sx={{ ...glassCardSx, height: '100%', transition: 'all 0.3s ease', '&:hover': { transform: 'translateY(-8px)', boxShadow: `0 24px 48px ${alpha(theme.palette.primary.main, 0.18)}`, borderColor: alpha('#fff', 0.2) } }}>
                      <CardContent sx={{ p: 4 }}>
                        <Stack spacing={3}>
                          <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
                            <Box
                              sx={{
                                width: 56,
                                height: 56,
                                borderRadius: 2,
                                background: `linear-gradient(45deg, ${alpha(theme.palette.primary.main, 0.2)}, ${alpha(theme.palette.secondary.main, 0.2)})`,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                color: theme.palette.primary.main
                              }}
                            >
                              {capability.icon}
                            </Box>
                            <Typography 
                              variant="body2" 
                              sx={{ 
                                background: alpha(theme.palette.primary.main, 0.1),
                                color: theme.palette.primary.main,
                                fontWeight: 600,
                                px: 2,
                                py: 0.5,
                                borderRadius: 1
                              }}
                            >
                              {capability.highlight}
                            </Typography>
                          </Stack>
                          <Stack spacing={2}>
                            <Typography variant="h6" fontWeight={700} sx={{ fontSize: '1.1rem', color: 'white' }}>
                              {capability.title}
                            </Typography>
                            <Typography variant="body2" color="rgba(255,255,255,0.8)" lineHeight={1.6} sx={{ fontSize: '0.95rem' }}>
                              {capability.description}
                            </Typography>
                          </Stack>
                        </Stack>
                      </CardContent>
                    </Card>
                  </motion.div>
                </Grid>
              ))}
            </Grid>
          </Stack>
        </motion.div>
      </Container>

      {/* Social Proof Stats */}
      <Container maxWidth="lg" sx={{ py: 6, position: 'relative', zIndex: 2 }}>
        <motion.div variants={stagger} initial="hidden" whileInView="visible" viewport={{ once: true, amount: 0.2 }}>
          <Grid container spacing={4}>
            {socialProofStats.map((stat, index) => (
              <Grid item xs={6} md={3} key={index}>
                <motion.div variants={fadeInUp}>
                  <Stack alignItems="center" spacing={2}>
                    <Box
                      sx={{
                        width: 56,
                        height: 56,
                        borderRadius: 2,
                        background: `linear-gradient(45deg, ${alpha(theme.palette.primary.main, 0.2)}, ${alpha(theme.palette.secondary.main, 0.2)})`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: theme.palette.primary.main
                      }}
                    >
                      {stat.icon}
                    </Box>
                    <Stack alignItems="center" spacing={0.5}>
                      <Typography 
                        variant="h4" 
                        sx={{
                          fontWeight: 800,
                          background: 'linear-gradient(45deg, #667eea 30%, #764ba2 90%)',
                          WebkitBackgroundClip: 'text',
                          WebkitTextFillColor: 'transparent',
                          color: 'white'
                        }}
                      >
                        {stat.value}
                      </Typography>
                      <Typography variant="body2" color="rgba(255,255,255,0.8)" fontWeight={500} textAlign="center">
                        {stat.label}
                      </Typography>
                    </Stack>
                  </Stack>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        </motion.div>
      </Container>
    </Box>
  );
};

export default IntroducingAlwrity;
