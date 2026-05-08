import React from 'react';
import { Paper, Typography, Grid, Stack, Box } from '@mui/material';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import ContentPasteIcon from '@mui/icons-material/ContentPaste';

const BenefitsSummary: React.FC = () => {
  return (
    <Paper 
      sx={{ 
        p: 3, 
        backgroundColor: '#f8fafc',
        border: '1px solid #e2e8f0',
        borderRadius: 2
      }}
    >
      <Typography variant="h6" sx={{ fontWeight: 600, color: '#1e293b', mb: 2 }}>
        Why Connect Your Platforms?
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={12} md={4}>
          <Stack direction="row" spacing={2} alignItems="flex-start">
            <AutoAwesomeIcon sx={{ color: '#3b82f6', mt: 0.5 }} />
            <Box>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#1e293b' }}>
                Automated Publishing
              </Typography>
              <Typography variant="body2" sx={{ color: '#64748b' }}>
                AI automatically publishes optimized content to your connected platforms
              </Typography>
            </Box>
          </Stack>
        </Grid>
        <Grid item xs={12} md={4}>
          <Stack direction="row" spacing={2} alignItems="flex-start">
            <TrendingUpIcon sx={{ color: '#10b981', mt: 0.5 }} />
            <Box>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#1e293b' }}>
                Performance Analytics
              </Typography>
              <Typography variant="body2" sx={{ color: '#64748b' }}>
                Track content performance across all platforms with unified analytics
              </Typography>
            </Box>
          </Stack>
        </Grid>
        <Grid item xs={12} md={4}>
          <Stack direction="row" spacing={2} alignItems="flex-start">
            <ContentPasteIcon sx={{ color: '#8b5cf6', mt: 0.5 }} />
            <Box>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#1e293b' }}>
                Content Optimization
              </Typography>
              <Typography variant="body2" sx={{ color: '#64748b' }}>
                AI continuously optimizes content based on platform-specific performance data
              </Typography>
            </Box>
          </Stack>
        </Grid>
      </Grid>
    </Paper>
  );
};

export default BenefitsSummary;
