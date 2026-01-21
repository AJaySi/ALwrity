/**
 * Quick Stats Grid Component
 *
 * Displays key performance metrics in a responsive grid
 */

import React from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Avatar,
  Box,
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import { People as PeopleIcon, Send as SendIcon, TrendingUp as TrendingUpIcon, Business as BusinessIcon } from '@mui/icons-material';
import { StatItem } from '../types/dashboard.types';

interface QuickStatsGridProps {
  stats?: StatItem[];
}

const defaultStats: StatItem[] = [
  { icon: PeopleIcon, label: 'Active Prospects', value: '1,247', color: '#60A5FA' },
  { icon: SendIcon, label: 'Emails This Week', value: '324', color: '#A855F7' },
  { icon: TrendingUpIcon, label: 'Success Rate', value: '24.8%', color: '#10B981' },
  { icon: BusinessIcon, label: 'Avg Domain DA', value: '68.5', color: '#F59E0B' },
];

export const QuickStatsGrid: React.FC<QuickStatsGridProps> = ({
  stats = defaultStats,
}) => {
  return (
    <Box sx={{ mb: 4 }}>
      <Grid container spacing={2}>
        {stats.map((stat, index) => (
          <Grid item xs={6} sm={3} key={stat.label}>
            <div
              className="fade-in-up"
              style={{
                opacity: 0,
                animationDelay: `${index * 0.1}s`
              }}
            >
              <Card sx={{
                background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(51, 65, 85, 0.8) 100%)',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: 2,
                textAlign: 'center',
                position: 'relative',
                overflow: 'hidden',
                '&::before': {
                  content: '""',
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  background: `radial-gradient(circle at 30% 30%, ${alpha(stat.color, 0.08)} 0%, transparent 70%)`,
                  pointerEvents: 'none',
                },
              }}>
                <CardContent sx={{ p: 2, position: 'relative', zIndex: 1 }}>
                  <Avatar sx={{
                    bgcolor: alpha(stat.color, 0.1),
                    border: `1px solid ${alpha(stat.color, 0.3)}`,
                    width: 40,
                    height: 40,
                    mx: 'auto',
                    mb: 1,
                  }}>
                    <stat.icon sx={{ color: stat.color, fontSize: 20 }} />
                  </Avatar>
                  <Typography variant="h5" sx={{ fontWeight: 700, color: '#F1F5F9', mb: 0.5 }}>
                    {stat.value}
                  </Typography>
                  <Typography variant="caption" sx={{ color: 'rgba(203, 213, 225, 0.7)', fontSize: '0.75rem' }}>
                    {stat.label}
                  </Typography>
                </CardContent>
              </Card>
            </div>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};