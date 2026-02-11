import React from 'react';
import { Paper, Grid, Stack, Typography, Divider } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { aiApiClient } from '../../api/client';
import { ImageStudioLayout } from './ImageStudioLayout';
import { studioModules } from './dashboard/modules';
import { ModuleCard } from './dashboard/ModuleCard';

export const ImageStudioDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [hoveredModule, setHoveredModule] = React.useState<string>('');
  const [costCatalog, setCostCatalog] = React.useState<Record<string, any>>({});

  React.useEffect(() => {
    const loadCostCatalog = async () => {
      try {
        const response = await aiApiClient.get('/api/image-studio/cost-catalog');
        const payload = response?.data || {};
        const modules = payload.modules || {};
        const confidence = payload.confidence || 'estimated';
        const updatedAt = payload.updated_at || '';
        const mapped: Record<string, any> = {};

        Object.entries(modules).forEach(([key, value]: [string, any]) => {
          mapped[key] = {
            estimate: value.estimate,
            notes: value.notes,
            confidence,
            updatedAt,
          };
        });

        setCostCatalog(mapped);
      } catch (error) {
        // fallback to static pricing already embedded in module configs
      }
    };

    loadCostCatalog();
  }, []);

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
          {studioModules.map(module => {
            const catalogPrice = costCatalog[module.key];
            const resolvedModule = catalogPrice
              ? { ...module, pricing: { ...module.pricing, ...catalogPrice } }
              : module;

            return (
              <Grid item xs={12} md={6} key={module.key}>
                <ModuleCard
                  module={resolvedModule}
                  isHovered={hoveredModule === module.key}
                  onMouseEnter={() => setHoveredModule(module.key)}
                  onMouseLeave={() => setHoveredModule('')}
                  onNavigate={navigate}
                />
              </Grid>
            );
          })}
        </Grid>
      </Paper>
    </ImageStudioLayout>
  );
};
