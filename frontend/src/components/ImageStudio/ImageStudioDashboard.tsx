import React from 'react';
import { Paper, Grid, Stack, Typography, Divider } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { ImageStudioLayout } from './ImageStudioLayout';
import { studioModules } from './dashboard/modules';
import { ModuleCard } from './dashboard/ModuleCard';

export const ImageStudioDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [hoveredModule, setHoveredModule] = React.useState<string>('');

  return (
    <ImageStudioLayout>
      <Paper
        elevation={0}
        sx={{
          maxWidth: 1400,
          mx: 'auto',
          borderRadius: 4,
          border: '1px solid rgba(255,255,255,0.08)',
          background: 'rgba(15,23,42,0.72)',
          p: { xs: 3, md: 5 },
          backdropFilter: 'blur(25px)',
        }}
      >
        <Stack spacing={1}>
          <Typography
            variant="h3"
            fontWeight={800}
            sx={{
              background: 'linear-gradient(120deg,#ede9fe,#c7d2fe)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            AI Image Studio
          </Typography>
          <Typography variant="body1" color="text.secondary">
            One hub for every visual workflow: generate, edit, upscale, transform, optimize, and manage
            assets built for content and marketing teams.
          </Typography>
        </Stack>

        <Divider sx={{ my: 3, borderColor: 'rgba(255,255,255,0.08)' }} />

        <Grid container spacing={3}>
          {studioModules.map(module => (
            <Grid item xs={12} md={6} key={module.key}>
              <ModuleCard
                module={module}
                isHovered={hoveredModule === module.key}
                onMouseEnter={() => setHoveredModule(module.key)}
                onMouseLeave={() => setHoveredModule('')}
                onNavigate={navigate}
              />
            </Grid>
          ))}
        </Grid>
      </Paper>
    </ImageStudioLayout>
  );
};
