import React from 'react';
import { Box, Button, Grid, Paper, Typography } from '@mui/material';
import GlobalStyles from '@mui/material/GlobalStyles';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import ImageIcon from '@mui/icons-material/Image';
import VolumeUpIcon from '@mui/icons-material/VolumeUp';
import VideoLibraryIcon from '@mui/icons-material/VideoLibrary';

interface StoryWriterLandingProps {
  onStart: () => void;
}

const featureHighlights = [
  {
    title: 'AI Story Blueprint',
    description: 'Persona, setting, tone, and premise woven together automatically.',
    detail: 'Start with cohesive outlines tailored to your audience and genre.',
    icon: <MenuBookIcon sx={{ fontSize: 32, color: '#8D5524' }} />,
  },
  {
    title: 'Cinematic Illustrations',
    description: 'Scene-by-scene image prompts and gallery-ready renders.',
    detail: 'Control aspect ratios, providers, and models for every chapter.',
    icon: <ImageIcon sx={{ fontSize: 32, color: '#B25D3E' }} />,
  },
  {
    title: 'Voice-Ready Narration',
    description: 'Generate lifelike audio in multiple languages and speeds.',
    detail: 'Perfect for bedtime stories, podcasts, or accessibility-ready scripts.',
    icon: <VolumeUpIcon sx={{ fontSize: 32, color: '#7A4C9F' }} />,
  },
  {
    title: 'Story Video Composer',
    description: 'Blend scenes, audio, and transitions into immersive videos.',
    detail: 'Fine-tune FPS, transitions, and pacing for a studio polish.',
    icon: <VideoLibraryIcon sx={{ fontSize: 32, color: '#2E7D83' }} />,
  },
];

export const StoryWriterLanding: React.FC<StoryWriterLandingProps> = ({ onStart }) => {
  return (
    <Box sx={{ py: 6 }}>
      <GlobalStyles
        styles={{
          '.storywriter-landing-shadow': {
            boxShadow: '0 36px 80px rgba(45, 30, 15, 0.25)',
          },
        }}
      />

      <Box sx={{ mb: 5, display: 'flex', justifyContent: 'center' }}>
        <Box
          className="storywriter-landing-shadow"
          sx={{
            position: 'relative',
            width: { xs: '100%', lg: '90vw' },
            maxWidth: 1400,
            display: 'flex',
            flexDirection: { xs: 'column', md: 'row' },
            borderRadius: '24px',
            overflow: 'hidden',
            background: 'linear-gradient(120deg, #fff9ef 0%, #f5e1c7 45%, #fff9ef 100%)',
            border: '1px solid rgba(120, 90, 60, 0.28)',
          }}
        >
          <Box
            sx={{
              flex: 1,
              p: { xs: 4, md: 6 },
              borderRight: { md: '1px solid rgba(120, 90, 60, 0.18)' },
              background: 'linear-gradient(100deg, rgba(255,255,255,0.85) 0%, rgba(242,226,204,0.95) 100%)',
            }}
          >
            <Typography variant="overline" sx={{ letterSpacing: 6, color: '#7a5335', fontWeight: 600 }}>
              Story Text & Blueprint
            </Typography>
            <Typography variant="h4" sx={{ fontFamily: `'Playfair Display', serif`, color: '#2C2416', mb: 2 }}>
              Watch Alwrity AI open your storybook
            </Typography>
            <Typography variant="body1" sx={{ color: '#3f3224', lineHeight: 1.8, mb: 3 }}>
              Begin with a book-inspired canvas. Alwrity assembles personas, settings, tones, and story beats so you can
              focus on imagination, not forms.
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
              {[
                'AI-curated personas, stakes, and endings',
                'Guided tone, POV, rating, and length controls',
                'Scene-by-scene descriptions ready for writing',
              ].map((item) => (
                <Typography key={item} variant="body2" sx={{ color: '#5D4037' }}>
                  • {item}
                </Typography>
              ))}
            </Box>
          </Box>

          <Box
            sx={{
              flex: 1,
              p: { xs: 4, md: 6 },
              background: 'linear-gradient(260deg, rgba(255,255,255,0.9) 0%, rgba(243,226,206,0.95) 100%)',
            }}
          >
            <Typography variant="overline" sx={{ letterSpacing: 6, color: '#7a5335', fontWeight: 600 }}>
              Multimedia Magic
            </Typography>
            <Typography variant="h4" sx={{ fontFamily: `'Playfair Display', serif`, color: '#2C2416', mb: 2 }}>
              Illustrations, narration, and video on tap
            </Typography>
            <Typography variant="body1" sx={{ color: '#3f3224', lineHeight: 1.8, mb: 3 }}>
              Every scene can bloom into art, audio, and cinematic video. Toggle features that matter and let AI stitch
              them together.
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
              {[
                'High-fidelity prompts for image generators',
                'Narration in multiple languages and speeds',
                'Video assembly with scene transitions and audio sync',
              ].map((item) => (
                <Typography key={item} variant="body2" sx={{ color: '#5D4037' }}>
                  • {item}
                </Typography>
              ))}
            </Box>
          </Box>
        </Box>
      </Box>

      <Box sx={{ textAlign: 'center', mb: 5 }}>
        <Button
          variant="contained"
          size="large"
          startIcon={<AutoAwesomeIcon />}
          onClick={onStart}
          sx={{
            mb: 1,
            px: 5,
            py: 1.8,
            borderRadius: '999px',
            textTransform: 'none',
            fontWeight: 600,
            background: 'linear-gradient(135deg, #7F5AF0 0%, #2CB67D 100%)',
            boxShadow: '0 16px 32px rgba(127, 90, 240, 0.35)',
            '&:hover': {
              background: 'linear-gradient(135deg, #6c4cd4 0%, #24a26f 100%)',
              boxShadow: '0 18px 36px rgba(127, 90, 240, 0.4)',
            },
          }}
        >
          Let’s ALwrity Your Story Journey
        </Button>
        <Typography variant="body2" sx={{ color: '#5D4037' }}>
          Tap once to open the book. Inputs appear after AI drafts your foundation.
        </Typography>
      </Box>

      <Typography variant="h5" sx={{ fontWeight: 600, color: '#1A1611', mb: 2 }}>
        Everything Story Writer helps you create
      </Typography>
      <Grid container spacing={2}>
        {featureHighlights.map((feature) => (
          <Grid item xs={12} sm={6} md={3} key={feature.title}>
            <Paper
              elevation={0}
              sx={{
                height: '100%',
                p: 3,
                background: 'linear-gradient(180deg, #fff8ef 0%, #f8efe2 100%)',
                borderRadius: 3,
                border: '1px solid rgba(138, 85, 36, 0.18)',
                display: 'flex',
                flexDirection: 'column',
                gap: 1,
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                {feature.icon}
                <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#2C2416' }}>
                  {feature.title}
                </Typography>
              </Box>
              <Typography variant="body2" sx={{ color: '#5D4037' }}>
                {feature.description}
              </Typography>
              <Typography variant="caption" sx={{ color: '#7A5A3C' }}>
                {feature.detail}
              </Typography>
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default StoryWriterLanding;

