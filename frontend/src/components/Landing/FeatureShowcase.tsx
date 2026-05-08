import React, { useState } from 'react';
import { Box, Container, Typography, Stack, IconButton, useTheme, alpha } from '@mui/material';
import ArrowBack from '@mui/icons-material/ArrowBack';
import ArrowForward from '@mui/icons-material/ArrowForward';
import Psychology from '@mui/icons-material/Psychology';
import Search from '@mui/icons-material/Search';
import FactCheck from '@mui/icons-material/FactCheck';
import Edit from '@mui/icons-material/Edit';
import Assistant from '@mui/icons-material/Assistant';
import Verified from '@mui/icons-material/Verified';
import { motion, AnimatePresence } from 'framer-motion';

interface Feature {
  image: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  badge: string;
}

const features: Feature[] = [
  {
    image: '/Alwrity-copilot1.png',
    title: 'AI-First Copilot',
    description: 'Your personal LinkedIn writing assistant with persona-aware content generation. Create professional posts, articles, and carousels that match your unique voice.',
    icon: <Assistant />,
    badge: 'Persona-Aware'
  },
  {
    image: '/Alwrity-copilot2.png',
    title: 'Intelligent Writing Partner',
    description: 'Context-aware AI copilot that understands your content goals and audience. Get real-time suggestions and enhancements tailored to your strategy.',
    icon: <Psychology />,
    badge: 'Context-Aware'
  },
  {
    image: '/alwrty_research.png',
    title: 'Interactive Web Research',
    description: 'AI-powered research engine with 25+ source integration. Get SERP rankings, credibility scores, and real-time market insights for data-driven content.',
    icon: <Search />,
    badge: 'Live Research'
  },
  {
    image: '/ALwrity-assistive-writing.png',
    title: 'Assistive Writing Flow',
    description: 'Smart writing assistant that contextually continues your thoughts. Never face writer\'s block again with AI that understands your draft and goals.',
    icon: <Edit />,
    badge: 'Smart Assist'
  },
  {
    image: '/Fact-check1.png',
    title: 'Hallucination-Free Content',
    description: 'Advanced fact-checking with source verification and credibility scoring. Every claim is analyzed, validated, and cited with authority ratings.',
    icon: <FactCheck />,
    badge: 'Verified'
  },
  {
    image: '/Alwrity-fact-check.png',
    title: 'Claims Analysis Engine',
    description: 'Comprehensive fact-check results with supported, refuted, and insufficient claims. Ensure accuracy with AI-powered reasoning and source citations.',
    icon: <Verified />,
    badge: 'AI-Verified'
  },
];

const FeatureShowcase: React.FC = () => {
  const theme = useTheme();
  const [currentPage, setCurrentPage] = useState(0);
  const itemsPerPage = 3;
  const totalPages = Math.ceil(features.length / itemsPerPage);

  const handleNext = () => {
    setCurrentPage((prev) => (prev + 1) % totalPages);
  };

  const handlePrev = () => {
    setCurrentPage((prev) => (prev - 1 + totalPages) % totalPages);
  };

  const currentFeatures = features.slice(
    currentPage * itemsPerPage,
    (currentPage + 1) * itemsPerPage
  );

  const slideVariants = {
    enter: (direction: number) => ({
      x: direction > 0 ? 1000 : -1000,
      opacity: 0,
      scale: 0.8,
    }),
    center: {
      x: 0,
      opacity: 1,
      scale: 1,
      transition: {
        duration: 0.5,
        ease: "easeOut" as const,
      },
    },
    exit: (direction: number) => ({
      x: direction > 0 ? -1000 : 1000,
      opacity: 0,
      scale: 0.8,
      transition: {
        duration: 0.5,
        ease: "easeOut" as const,
      },
    }),
  };

  const cardVariants = {
    hidden: { opacity: 0, y: 50 },
    visible: (i: number) => ({
      opacity: 1,
      y: 0,
      transition: {
        delay: i * 0.15,
        duration: 0.6,
        ease: "easeOut" as const,
      },
    }),
  };

  return (
    <Box
      sx={{
        position: 'relative',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundImage: 'url(/alwrity_platform_experience.png)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          zIndex: 0,
        },
        '&::after': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'linear-gradient(135deg, rgba(0, 0, 0, 0.3) 0%, rgba(25, 118, 210, 0.2) 50%, rgba(156, 39, 176, 0.2) 100%)',
          zIndex: 1,
        },
      }}
    >
      <Container maxWidth="xl" sx={{ py: 10, position: 'relative', zIndex: 2 }}>
        <Stack spacing={6} alignItems="center">
        {/* Section Header */}
        <Stack spacing={2} alignItems="center" textAlign="center">
          <Typography variant="h3" fontWeight={700} sx={{ fontSize: { xs: '2rem', md: '2.5rem' } }}>
            Experience the Platform
          </Typography>
          <Typography variant="h6" color="text.secondary" maxWidth="750px" sx={{ lineHeight: 1.6 }}>
            Explore ALwrity's powerful features designed to transform your content workflow. 
            From AI copilots to fact-checking, everything you need in one platform.
          </Typography>
        </Stack>

        {/* Carousel Container */}
        <Box sx={{ position: 'relative', width: '100%', overflow: 'hidden', px: { xs: 2, md: 4 } }}>
          <AnimatePresence mode="wait" custom={currentPage}>
            <motion.div
              key={currentPage}
              custom={currentPage}
              variants={slideVariants}
              initial="enter"
              animate="center"
              exit="exit"
              style={{ width: '100%' }}
            >
              <Box
                sx={{
                  display: 'grid',
                  gridTemplateColumns: { xs: '1fr', md: 'repeat(3, 1fr)' },
                  gap: 4,
                  px: { xs: 2, md: 4 },
                }}
              >
                {currentFeatures.map((feature, index) => (
                  <motion.div
                    key={feature.title}
                    custom={index}
                    variants={cardVariants}
                    initial="hidden"
                    animate="visible"
                  >
                    <Box
                      sx={{
                        position: 'relative',
                        borderRadius: 3,
                        overflow: 'hidden',
                        background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.08)} 0%, ${alpha(theme.palette.secondary.main, 0.08)} 100%)`,
                        border: `1px solid ${alpha(theme.palette.primary.main, 0.2)}`,
                        boxShadow: `0 12px 40px ${alpha(theme.palette.primary.main, 0.15)}`,
                        transition: 'all 0.4s cubic-bezier(0.32, 0.72, 0, 1)',
                        '&:hover': {
                          transform: 'translateY(-12px) scale(1.02)',
                          boxShadow: `0 20px 60px ${alpha(theme.palette.primary.main, 0.25)}`,
                          borderColor: alpha(theme.palette.primary.main, 0.4),
                        },
                      }}
                    >
                      {/* Badge */}
                      <Box
                        sx={{
                          position: 'absolute',
                          top: 16,
                          right: 16,
                          zIndex: 2,
                          background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 50%, ${theme.palette.primary.dark} 100%)`,
                          backdropFilter: 'blur(12px)',
                          px: 2.5,
                          py: 1,
                          borderRadius: 3,
                          border: '1px solid rgba(255, 255, 255, 0.3)',
                          boxShadow: `
                            0 8px 32px ${alpha(theme.palette.primary.main, 0.4)},
                            0 4px 16px ${alpha(theme.palette.secondary.main, 0.3)},
                            inset 0 1px 0 rgba(255, 255, 255, 0.2)
                          `,
                          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                          '&:hover': {
                            transform: 'translateY(-2px) scale(1.05)',
                            boxShadow: `
                              0 12px 40px ${alpha(theme.palette.primary.main, 0.5)},
                              0 6px 20px ${alpha(theme.palette.secondary.main, 0.4)},
                              inset 0 1px 0 rgba(255, 255, 255, 0.3)
                            `,
                          },
                        }}
                      >
                        <Typography 
                          variant="caption" 
                          fontWeight={700} 
                          color="white" 
                          sx={{ 
                            fontSize: '0.8rem',
                            textShadow: '0 1px 2px rgba(0, 0, 0, 0.3)',
                            letterSpacing: '0.5px',
                            textTransform: 'uppercase',
                          }}
                        >
                          {feature.badge}
                        </Typography>
                      </Box>

                      {/* Feature Image */}
                      <Box
                        sx={{
                          width: '100%',
                          height: 280,
                          backgroundImage: `url(${feature.image})`,
                          backgroundSize: 'cover',
                          backgroundPosition: 'center top',
                          position: 'relative',
                          '&::after': {
                            content: '""',
                            position: 'absolute',
                            bottom: 0,
                            left: 0,
                            right: 0,
                            height: '40%',
                            background: 'linear-gradient(to bottom, transparent, rgba(0,0,0,0.4))',
                          },
                        }}
                      />

                      {/* Feature Info */}
                      <Box
                        sx={{
                          p: 3,
                          background: `linear-gradient(135deg, ${alpha(theme.palette.common.white, 0.06)} 0%, ${alpha(theme.palette.common.white, 0.02)} 100%)`,
                          backdropFilter: 'blur(12px)',
                        }}
                      >
                        <Stack spacing={2}>
                          <Stack direction="row" spacing={1.5} alignItems="center">
                            <Box
                              sx={{
                                width: 40,
                                height: 40,
                                borderRadius: 2,
                                background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                color: 'white',
                                boxShadow: `0 4px 12px ${alpha(theme.palette.primary.main, 0.4)}`,
                              }}
                            >
                              {feature.icon}
                            </Box>
                            <Typography 
                              variant="h6" 
                              fontWeight={700} 
                              color="white"
                              sx={{ 
                                fontSize: '1.2rem',
                                textShadow: '0 1px 3px rgba(0, 0, 0, 0.7)',
                                letterSpacing: '0.5px',
                              }}
                            >
                              {feature.title}
                            </Typography>
                          </Stack>
                          <Typography 
                            variant="body2" 
                            color="white" 
                            sx={{ 
                              lineHeight: 1.6, 
                              fontSize: '1rem',
                              fontWeight: 500,
                              textShadow: '0 1px 3px rgba(0, 0, 0, 0.7)',
                              letterSpacing: '0.3px',
                            }}
                          >
                            {feature.description}
                          </Typography>
                        </Stack>
                      </Box>
                    </Box>
                  </motion.div>
                ))}
              </Box>
            </motion.div>
          </AnimatePresence>

          {/* Navigation Arrows */}
          {totalPages > 1 && (
            <>
              <IconButton
                onClick={handlePrev}
                sx={{
                  position: 'absolute',
                  left: { xs: 0, md: -10 },
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
                  color: 'white',
                  width: 50,
                  height: 50,
                  boxShadow: `0 8px 24px ${alpha(theme.palette.primary.main, 0.4)}`,
                  '&:hover': {
                    background: `linear-gradient(135deg, ${theme.palette.primary.dark} 0%, ${theme.palette.secondary.dark} 100%)`,
                    transform: 'translateY(-50%) scale(1.1)',
                    boxShadow: `0 12px 32px ${alpha(theme.palette.primary.main, 0.5)}`,
                  },
                  transition: 'all 0.3s ease',
                  zIndex: 10,
                }}
              >
                <ArrowBack />
              </IconButton>
              <IconButton
                onClick={handleNext}
                sx={{
                  position: 'absolute',
                  right: { xs: 0, md: -10 },
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
                  color: 'white',
                  width: 50,
                  height: 50,
                  boxShadow: `0 8px 24px ${alpha(theme.palette.primary.main, 0.4)}`,
                  '&:hover': {
                    background: `linear-gradient(135deg, ${theme.palette.primary.dark} 0%, ${theme.palette.secondary.dark} 100%)`,
                    transform: 'translateY(-50%) scale(1.1)',
                    boxShadow: `0 12px 32px ${alpha(theme.palette.primary.main, 0.5)}`,
                  },
                  transition: 'all 0.3s ease',
                  zIndex: 10,
                }}
              >
                <ArrowForward />
              </IconButton>
            </>
          )}
        </Box>

        {/* Page Indicators */}
        {totalPages > 1 && (
          <Stack direction="row" spacing={1.5} alignItems="center">
            {Array.from({ length: totalPages }).map((_, index) => (
              <Box
                key={index}
                onClick={() => setCurrentPage(index)}
                sx={{
                  width: index === currentPage ? 40 : 12,
                  height: 12,
                  borderRadius: 6,
                  background: index === currentPage
                    ? `linear-gradient(90deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`
                    : alpha(theme.palette.text.secondary, 0.2),
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  boxShadow: index === currentPage ? `0 4px 12px ${alpha(theme.palette.primary.main, 0.4)}` : 'none',
                  '&:hover': {
                    background: index === currentPage
                      ? `linear-gradient(90deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`
                      : alpha(theme.palette.text.secondary, 0.4),
                  },
                }}
              />
            ))}
          </Stack>
        )}

      </Stack>
    </Container>
    </Box>
  );
};

export default FeatureShowcase;

