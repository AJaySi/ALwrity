import React from 'react';
import { Grid, Paper, Stack, Typography, Divider } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { VideoStudioLayout } from './VideoStudioLayout';
import { videoStudioModules } from './dashboard/modules';
import { ModuleCard } from './dashboard/ModuleCard';

export const VideoStudioDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [hovered, setHovered] = React.useState<string>('');

  return (
    <VideoStudioLayout>
      <Paper
        elevation={0}
        sx={{
          maxWidth: 1400,
          mx: 'auto',
          borderRadius: 5,
          border: '1px solid rgba(255,255,255,0.12)',
          background: 'rgba(15,23,42,0.85)',
          p: { xs: 3, md: 5 },
          backdropFilter: 'blur(30px)',
          boxShadow: '0 20px 60px rgba(15,23,42,0.6), inset 0 1px 0 rgba(255,255,255,0.05)',
        }}
      >

        <Grid container spacing={3}>
          {videoStudioModules.map(module => (
            <Grid item xs={12} md={6} key={module.key}>
              <ModuleCard
                module={module}
                isHovered={hovered === module.key}
                onMouseEnter={() => setHovered(module.key)}
                onMouseLeave={() => setHovered('')}
                onNavigate={navigate}
              />
            </Grid>
          ))}
        </Grid>
      </Paper>
    </VideoStudioLayout>
  );
};

export default VideoStudioDashboard;
