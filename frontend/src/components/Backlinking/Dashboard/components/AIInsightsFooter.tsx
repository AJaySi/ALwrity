/**
 * AI Insights Footer Component
 *
 * Displays AI-powered insights and recommendations
 */

import React from 'react';
import {
  Box,
  Typography,
  Grid,
  Avatar,
} from '@mui/material';
import {
  Psychology as BrainIcon,
  CheckCircle as CheckCircleIcon,
  Email as EmailIcon,
  TrendingUp as TrendingUpIcon,
} from '@mui/icons-material';

export const AIInsightsFooter: React.FC = () => {
  const insights = [
    {
      icon: CheckCircleIcon,
      title: 'Smart Prospect Scoring',
      description: 'AI analyzes domain authority, content relevance, and outreach potential',
      color: '#10B981',
    },
    {
      icon: EmailIcon,
      title: 'Personalized Outreach',
      description: 'Custom email templates crafted for each prospect\'s industry and content',
      color: '#A855F7',
    },
    {
      icon: TrendingUpIcon,
      title: 'Performance Analytics',
      description: 'Real-time tracking of response rates, conversions, and ROI metrics',
      color: '#F59E0B',
    },
  ];

  return (
    <Box sx={{
      mt: 4,
      p: 3,
      background: 'linear-gradient(135deg, rgba(96, 165, 250, 0.05) 0%, rgba(168, 85, 247, 0.05) 50%, rgba(6, 182, 212, 0.05) 100%)',
      border: '1px solid rgba(96, 165, 250, 0.2)',
      borderRadius: 3,
      backdropFilter: 'blur(10px)',
    }}>
      <Typography variant="h6" sx={{
        fontWeight: 700,
        color: '#60A5FA',
        mb: 2,
        display: 'flex',
        alignItems: 'center',
        gap: 1,
      }}>
        <BrainIcon />
        AI-Powered Backlinking Insights
      </Typography>

      <Grid container spacing={3}>
        {insights.map((insight, index) => (
          <Grid item xs={12} md={4} key={index}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Avatar sx={{
                bgcolor: `rgba(${insight.color === '#10B981' ? '16, 185, 129' :
                              insight.color === '#A855F7' ? '168, 85, 247' :
                              '245, 158, 11'}, 0.1)`,
                border: `1px solid rgba(${insight.color === '#10B981' ? '16, 185, 129' :
                                        insight.color === '#A855F7' ? '168, 85, 247' :
                                        '245, 158, 11'}, 0.3)`,
              }}>
                <insight.icon sx={{ color: insight.color }} />
              </Avatar>
              <Box>
                <Typography variant="subtitle2" sx={{ color: '#F1F5F9', fontWeight: 600 }}>
                  {insight.title}
                </Typography>
                <Typography variant="body2" sx={{ color: 'rgba(203, 213, 225, 0.8)', fontSize: '0.875rem' }}>
                  {insight.description}
                </Typography>
              </Box>
            </Box>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};