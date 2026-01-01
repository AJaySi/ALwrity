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
          borderRadius: 4,
          border: '1px solid rgba(255,255,255,0.08)',
          background: 'rgba(15,23,42,0.78)',
          p: { xs: 3, md: 5 },
          backdropFilter: 'blur(25px)',
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
