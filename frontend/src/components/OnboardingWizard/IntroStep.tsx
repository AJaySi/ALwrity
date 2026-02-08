import React, { useEffect, useState } from 'react';
import { Box, Container, Typography, Grid, IconButton, Chip, Button } from '@mui/material';
import { ArrowBack, ArrowForward } from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import step1Img from '../../assets/onboarding/step1.png';
import step2Img from '../../assets/onboarding/step2.png';
import step3Img from '../../assets/onboarding/step3.png';
import step4Img from '../../assets/onboarding/step4.png';
import step5Img from '../../assets/onboarding/step5.png';
import step6Img from '../../assets/onboarding/step6.png';

interface IntroStepProps {
  updateHeaderContent: (content: { title: string; description: string }) => void;
}

interface IntroStepItem {
  id: number;
  title: string;
  subtitle: string;
  benefit: string;
  badge: string;
  imageSrc: string;
  imageAlt: string;
   details: string;
}

const formatDetails = (
  details: string
): {
  title: string;
  sections: { title: string; bullets: string[] }[];
} => {
  const lines = details
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => line.length > 0);

  const title = lines[0] || '';
  const sections: { title: string; bullets: string[] }[] = [];
  let currentSection: { title: string; bullets: string[] } | null = null;

  lines.slice(1).forEach((line) => {
    const isBullet = line.startsWith('- ') || line.startsWith('• ');
    if (!isBullet) {
      if (currentSection) {
        sections.push(currentSection);
      }
      currentSection = { title: line, bullets: [] };
      return;
    }
    const text = line.replace(/^[-•]\s*/, '');
    if (!currentSection) {
      currentSection = { title: '', bullets: [] };
    }
    currentSection.bullets.push(text);
  });

  if (currentSection) {
    sections.push(currentSection);
  }

  return { title, sections };
};

const items: IntroStepItem[] = [
  {
    id: 1,
    title: 'Getting started with ALwrity onboarding',
    subtitle: 'What this setup unlocks for your growth engine',
    benefit:
      'Design your AI growth engine in 6 focused steps. We will learn about your business, audience, and goals so ALwrity can plan, monitor, and optimize your content in the background. You can edit every step later.',
    badge: 'About 1 minute',
    imageSrc: step1Img,
    imageAlt: 'Overview of ALwrity onboarding steps',
    details: `Step 1 – Getting started with ALwrity

What you’ll see
- How the 6-step setup turns ALwrity into a co‑pilot for your marketing.

What you do
- Give ALwrity a quick overview of what you sell, who you serve, and where you publish.

What you get
- ALwrity does the heavy lifting (research, planning, suggestions) while you stay in control of what actually goes live and avoid blank‑page stress.`
  },
  {
    id: 2,
    title: 'Teach ALwrity your website and brand',
    subtitle: 'Website & brand',
    benefit:
      'We crawl your primary site, offers, and brand voice so every asset sounds like you and points to the right pages.',
    badge: 'Runs in the background',
    imageSrc: step2Img,
    imageAlt: 'Teach ALwrity your website and brand',
    details: `Step 2 – Teach ALwrity your website and brand

What you do
- Point ALwrity to your main website or a few key pages.

How it works
- ALwrity “reads” your site like a smart assistant, so you don’t need long briefs or technical setup.

What you get
- Suggestions that sound like you, use your real offers and proof, and know which pages to send people to.`
  },
  {
    id: 3,
    title: 'Map your market and opportunities',
    subtitle: 'Research & gaps',
    benefit:
      'ALwrity analyses your niche, competitors, and keywords to uncover content gaps that can drive compounding traffic.',
    badge: 'Research runs asynchronously',
    imageSrc: step3Img,
    imageAlt: 'Map your market and opportunities',
    details: `Step 3 – Map your market and opportunities

The usual problem
- “What should I create next?” often means bouncing between tools, tabs, and spreadsheets.

What ALwrity does
- Looks at your niche, similar players, and what people are searching for.

What you get
- A clearer set of content opportunities that can build momentum over time instead of random one‑off posts.`
  },
  {
    id: 4,
    title: 'Define personas and tone of voice',
    subtitle: 'Personas & tone',
    benefit:
      'We turn your ideal customers and brand personality into personas that guide every AI decision across channels.',
    badge: 'Takes a few minutes',
    imageSrc: step4Img,
    imageAlt: 'Define personas and tone of voice',
    details: `Step 4 – Define personas and tone of voice

What you do
- Describe your ideal readers or customers in plain language and how you like to talk to them.

How ALwrity uses it
- Turns that into clear personas and tone settings.

What you get
- Suggestions (headlines, outlines, emails, posts) that feel written for the right person, in your voice.`
  },
  {
    id: 5,
    title: 'Wire ALwrity into your channels',
    subtitle: 'Integrations',
    benefit:
      'Connect search, website, blog, and social platforms so insights and content can flow where your audience actually is.',
    badge: 'Optional but recommended',
    imageSrc: step5Img,
    imageAlt: 'Wire ALwrity into your channels',
    details: `Step 5 – Wire ALwrity into your channels (optional but powerful)

What you do
- Optionally connect ALwrity to where you already publish or track results (for example, your blog).

Why it helps
- Ideas, drafts, and insights appear alongside your existing workflow instead of in a separate tool.

What you get
- Less copy‑paste, less context switching, and more time to review, edit, and schedule. You stay in full control of what gets published.`
  },
  {
    id: 6,
    title: 'Launch your always-on growth system',
    subtitle: 'Review & launch',
    benefit:
      'Review the setup, confirm what matters, and let ALwrity monitor, plan, and suggest content in the background.',
    badge: 'You stay in control',
    imageSrc: step6Img,
    imageAlt: 'Launch your always-on growth system',
    details: `Step 6 – Launch your always‑on growth system

What you do
- Review the setup and confirm what matters most right now (traffic, leads, consistency, or something else).

What ALwrity does next
- Starts working in the background, watching what’s working and suggesting next moves and content ideas.

What you get
- A calm, central place to return to when planning your week and a system that keeps running even when you’re busy with clients, products, or the rest of the business.`
  }
];

const IntroStep: React.FC<IntroStepProps> = ({ updateHeaderContent }) => {
  const [activeIndex, setActiveIndex] = useState(0);
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    updateHeaderContent({
      title: 'ALwrity Onboarding',
      description: 'A guided 6-step setup to configure your AI-powered marketing system.'
    });
  }, [updateHeaderContent]);

  const handleNext = () => {
    setActiveIndex((prev) => (prev + 1) % items.length);
  };

  const handlePrev = () => {
    setActiveIndex((prev) => (prev - 1 + items.length) % items.length);
  };

  useEffect(() => {
    setShowDetails(false);
  }, [activeIndex]);

  const current = items[activeIndex];
  const { title: detailsTitle, sections } = formatDetails(current.details);

  return (
    <Container
      maxWidth="lg"
      sx={{
        py: { xs: 3, md: 4 },
        position: 'relative'
      }}
    >
      <Box
        sx={{
          position: 'absolute',
          inset: 0,
          pointerEvents: 'none',
          background:
            'radial-gradient(circle at 0% 0%, rgba(102,126,234,0.12) 0%, transparent 55%), radial-gradient(circle at 100% 100%, rgba(129,140,248,0.16) 0%, transparent 55%)'
        }}
      />
      <Grid container spacing={4} alignItems="center" sx={{ position: 'relative' }}>
        <Grid item xs={12}>
          <Box
            sx={{
              borderRadius: 4,
              p: { xs: 2, md: 3 },
              background:
                'linear-gradient(135deg, rgba(15,23,42,0.9), rgba(30,64,175,0.9))',
              border: '1px solid rgba(148, 163, 184, 0.45)',
              boxShadow:
                '0 24px 60px rgba(15, 23, 42, 0.75), 0 0 0 1px rgba(148, 163, 184, 0.15)',
              minHeight: 320,
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              position: 'relative',
              overflow: 'hidden'
            }}
          >
            <Box
              sx={{
                position: 'absolute',
                inset: 0,
                pointerEvents: 'none',
                background:
                  'radial-gradient(circle at 0% 0%, rgba(59,130,246,0.22) 0%, transparent 55%), radial-gradient(circle at 100% 100%, rgba(56,189,248,0.16) 0%, transparent 60%)',
                opacity: 0.9
              }}
            />
            <Box
              sx={{
                mb: 2,
                display: 'flex',
                alignItems: 'flex-end',
                justifyContent: 'space-between',
                gap: 2,
                flexWrap: { xs: 'wrap', md: 'nowrap' }
              }}
            >
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'baseline',
                  gap: 1,
                  flexWrap: 'wrap',
                  minWidth: 0
                }}
              >
                <Typography
                  variant="h6"
                  sx={{
                    fontWeight: 700,
                    color: 'white',
                    whiteSpace: 'nowrap',
                    letterSpacing: 0.2,
                    fontSize: 18.5
                  }}
                >
                  {current.title}
                </Typography>
                <Typography
                  variant="body2"
                  sx={{
                    color: 'rgba(226, 232, 240, 0.85)',
                    opacity: 0.95
                  }}
                >
                  {current.subtitle}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.2 }}>
                <Chip
                  label={`Step ${current.id} of ${items.length}`}
                  size="small"
                  sx={{
                    backgroundColor: 'rgba(15, 23, 42, 0.9)',
                    color: 'rgba(226, 232, 240, 0.95)',
                    borderRadius: 999,
                    fontWeight: 600,
                    fontSize: 11,
                    '& .MuiChip-label': {
                      px: 1.5
                    }
                  }}
                />
                <Chip
                  label={current.badge}
                  size="small"
                  sx={{
                    backgroundColor: 'rgba(45, 212, 191, 0.18)',
                    color: 'rgb(45, 212, 191)',
                    borderRadius: 999,
                    fontWeight: 600,
                    fontSize: 11,
                    '& .MuiChip-label': {
                      px: 1.5
                    }
                  }}
                />
              </Box>
            </Box>
            <AnimatePresence mode="wait">
              <Box
                key={current.id}
                component={motion.div}
                initial={{ opacity: 0, y: 16, scale: 0.97 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -16, scale: 0.97 }}
                transition={{ duration: 0.3, ease: 'easeOut' }}
                sx={{
                  borderRadius: 3,
                  background:
                    'linear-gradient(135deg, rgba(15,23,42,0.6), rgba(30,64,175,0.9))',
                  border: '1px dashed rgba(129, 140, 248, 0.8)',
                  mb: 3,
                  minHeight: 320,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  position: 'relative',
                  overflow: 'hidden'
                }}
              >
                <Box
                  sx={{
                    position: 'absolute',
                    inset: '-20%',
                    background:
                      'radial-gradient(circle at 0% 0%, rgba(59,130,246,0.25) 0%, transparent 55%), radial-gradient(circle at 100% 100%, rgba(56,189,248,0.2) 0%, transparent 60%)',
                    opacity: 0.9
                  }}
                />
                <Box
                  sx={{
                    position: 'relative',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 1,
                    width: '100%',
                    height: { xs: 220, md: 260 }
                  }}
                >
                  {!showDetails ? (
                    <Box
                      component={motion.img}
                      src={current.imageSrc}
                      alt={current.imageAlt}
                      initial={{ opacity: 0.9, y: 4 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.4, ease: 'easeOut' }}
                      sx={{
                        width: '100%',
                        height: '100%',
                        borderRadius: 2,
                        objectFit: 'cover',
                        boxShadow: '0 18px 45px rgba(15,23,42,0.85)',
                        border: '1px solid rgba(148, 163, 184, 0.45)',
                        mx: 'auto'
                      }}
                    />
                  ) : (
                    <Box
                      component={motion.div}
                      initial={{ opacity: 0.9, y: 4 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.4, ease: 'easeOut' }}
                      sx={{
                        width: '100%',
                        height: '100%',
                        borderRadius: 2,
                        border: '1px solid rgba(148, 163, 184, 0.45)',
                        mx: 'auto',
                        display: 'flex',
                        alignItems: 'flex-start',
                        justifyContent: 'flex-start',
                        px: 3,
                        py: 2.5
                      }}
                    >
                      <Box
                        sx={{
                          width: '100%',
                          maxHeight: '100%',
                          overflowY: 'auto',
                          pr: 1
                        }}
                      >
                        <Typography
                          variant="subtitle2"
                          sx={{
                            color: 'rgba(226, 232, 240, 0.98)',
                            fontWeight: 600,
                            fontSize: 13,
                            mb: 1.5
                          }}
                        >
                          {detailsTitle}
                        </Typography>
                        <Box
                          sx={{
                            display: 'flex',
                            flexDirection: { xs: 'column', sm: 'row' },
                            gap: 1.5,
                            mt: 0.5,
                            flexWrap: 'wrap'
                          }}
                        >
                          {sections.map((section, index) => (
                            <Box
                              key={index}
                              sx={{
                                flex: { xs: '1 1 100%', sm: '1 1 0' },
                                minWidth: 0,
                                background:
                                  'linear-gradient(135deg, rgba(15,23,42,0.9), rgba(30,64,175,0.7))',
                                borderRadius: 1.5,
                                border: '1px solid rgba(148,163,184,0.6)',
                                boxShadow: '0 10px 25px rgba(15,23,42,0.55)',
                                px: 1.4,
                                py: 1.25
                              }}
                            >
                              {section.title && (
                                <Typography
                                  variant="body2"
                                  sx={{
                                    color: 'rgba(226, 232, 240, 0.95)',
                                    fontWeight: 600,
                                    fontSize: 12,
                                    mb: section.bullets.length ? 0.8 : 0
                                  }}
                                >
                                  {section.title}
                                </Typography>
                              )}
                              {section.bullets.map((bullet, bulletIndex) => (
                                <Box
                                  key={bulletIndex}
                                  sx={{
                                    display: 'flex',
                                    alignItems: 'flex-start',
                                    gap: 1,
                                    mt: bulletIndex === 0 ? 0.2 : 0.5
                                  }}
                                >
                                  <Box
                                    sx={{
                                      width: 4,
                                      height: 4,
                                      borderRadius: '50%',
                                      mt: 0.7,
                                      backgroundColor:
                                        'rgba(148, 163, 184, 0.95)'
                                    }}
                                  />
                                  <Typography
                                    variant="body2"
                                    sx={{
                                      color: 'rgba(226, 232, 240, 0.95)',
                                      fontSize: 12.5,
                                      lineHeight: 1.6
                                    }}
                                  >
                                    {bullet}
                                  </Typography>
                                </Box>
                              ))}
                            </Box>
                          ))}
                        </Box>
                      </Box>
                    </Box>
                  )}
                </Box>
                <IconButton
                  onClick={handlePrev}
                  size="small"
                  sx={{
                    position: 'absolute',
                    left: 10,
                    top: '50%',
                    transform: 'translateY(-50%)',
                    color: 'rgba(226, 232, 240, 0.92)',
                    backgroundColor: 'rgba(15,23,42,0.9)',
                    boxShadow: '0 8px 18px rgba(15,23,42,0.7)',
                    '&:hover': {
                      backgroundColor: 'rgba(15,23,42,1)'
                    }
                  }}
                >
                  <ArrowBack fontSize="small" />
                </IconButton>
                <IconButton
                  onClick={handleNext}
                  size="small"
                  sx={{
                    position: 'absolute',
                    right: 10,
                    top: '50%',
                    transform: 'translateY(-50%)',
                    color: 'rgba(226, 232, 240, 0.92)',
                    backgroundColor: 'rgba(15,23,42,0.9)',
                    boxShadow: '0 8px 18px rgba(15,23,42,0.7)',
                    '&:hover': {
                      backgroundColor: 'rgba(15,23,42,1)'
                    }
                  }}
                >
                  <ArrowForward fontSize="small" />
                </IconButton>
              </Box>
            </AnimatePresence>
            <Box>
              <Typography
                variant="body2"
                sx={{
                  color: 'rgba(241, 245, 249, 0.95)',
                  mb: 1.5,
                  maxWidth: 760,
                  mx: 'auto',
                  textAlign: 'center'
                }}
              >
                {current.benefit}
              </Typography>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Button
                  size="small"
                  variant="text"
                  onClick={() => setShowDetails((prev) => !prev)}
                  sx={{
                    color: 'rgba(96, 165, 250, 0.95)',
                    textTransform: 'none',
                    fontWeight: 600,
                    px: 0,
                    '&:hover': {
                      backgroundColor: 'transparent',
                      textDecoration: 'underline'
                    }
                  }}
                >
                  {showDetails ? 'Hide details' : 'Know more'}
                </Button>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mt: 0.5 }}>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  {items.map((item, index) => (
                    <Box
                      key={item.id}
                      sx={{
                        width: index === activeIndex ? 18 : 8,
                        height: 8,
                        borderRadius: 999,
                        backgroundColor:
                          index === activeIndex
                            ? 'rgba(129, 140, 248, 0.95)'
                            : 'rgba(148, 163, 184, 0.6)',
                        boxShadow:
                          index === activeIndex
                            ? '0 0 0 1px rgba(191, 219, 254, 0.7)'
                            : 'none',
                        transition: 'all 0.2s ease'
                      }}
                    />
                  ))}
                </Box>
              </Box>
            </Box>
          </Box>
        </Grid>
      </Grid>
    </Container>
  );
};

export default IntroStep;

