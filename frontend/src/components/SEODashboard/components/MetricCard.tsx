import React from 'react';
import { Box, Typography } from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import { GlassCard } from '../../shared/styled';
import { SEOMetric } from '../../../api/seoDashboard';

interface MetricCardProps {
  title: string;
  metric: SEOMetric;
  icon: React.ReactNode;
  color?: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ 
  title, 
  metric, 
  icon, 
  color = '#2196F3'
}) => {
  return (
    <GlassCard>
      <Box sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box
            sx={{
              width: 48,
              height: 48,
              borderRadius: 3,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              background: `${color}20`,
              border: `1px solid ${color}40`,
            }}
          >
            {icon}
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {metric.trend === 'up' ? (
              <TrendingUpIcon sx={{ color: '#4CAF50', fontSize: 20 }} />
            ) : (
              <TrendingDownIcon sx={{ color: '#F44336', fontSize: 20 }} />
            )}
            <Typography variant="body2" sx={{ 
              color: metric.trend === 'up' ? '#4CAF50' : '#F44336',
              fontWeight: 600
            }}>
              {metric.change > 0 ? '+' : ''}{metric.change}%
            </Typography>
          </Box>
        </Box>
        
        <Typography variant="h4" sx={{ 
          color: 'white', 
          fontWeight: 700,
          mb: 1
        }}>
          {metric.value.toLocaleString()}
        </Typography>
        
        <Typography variant="body2" sx={{ 
          color: 'rgba(255, 255, 255, 0.8)',
          mb: 2
        }}>
          {title}
        </Typography>
        
        <Typography variant="caption" sx={{ 
          color: 'rgba(255, 255, 255, 0.6)',
          fontStyle: 'italic'
        }}>
          {metric.description}
        </Typography>
      </Box>
    </GlassCard>
  );
};

export default MetricCard; 