import React from 'react';
import { Box, Typography, Chip, LinearProgress } from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import { EnhancedGlassCard } from '../../shared/styled';
import { SEOHealthScore } from '../../../api/seoDashboard';

interface HealthScoreProps {
  score: SEOHealthScore;
}

const HealthScore: React.FC<HealthScoreProps> = ({ score }) => {
  return (
    <EnhancedGlassCard>
      <Box sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
            🎯 SEO Health Score
          </Typography>
          <Chip
            label={score.label}
            size="small"
            sx={{
              background: `${score.color}20`,
              color: score.color,
              border: `1px solid ${score.color}40`,
              fontWeight: 600,
            }}
          />
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <Typography variant="h2" sx={{ 
            color: 'white', 
            fontWeight: 800,
            fontSize: { xs: '2.5rem', md: '3.5rem' }
          }}>
            {score.score}/100
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {score.trend === 'up' ? (
              <TrendingUpIcon sx={{ color: '#4CAF50', fontSize: 24 }} />
            ) : (
              <TrendingDownIcon sx={{ color: '#F44336', fontSize: 24 }} />
            )}
            <Typography variant="h6" sx={{ 
              color: score.trend === 'up' ? '#4CAF50' : '#F44336',
              fontWeight: 600
            }}>
              {score.trend === 'up' ? '+' : ''}{score.change} this month
            </Typography>
          </Box>
        </Box>
        
        <LinearProgress
          variant="determinate"
          value={score.score}
          sx={{
            height: 8,
            borderRadius: 4,
            backgroundColor: 'rgba(255, 255, 255, 0.2)',
            '& .MuiLinearProgress-bar': {
              background: `linear-gradient(90deg, ${score.color}, ${score.color}80)`,
              borderRadius: 4,
            },
          }}
        />
      </Box>
    </EnhancedGlassCard>
  );
};

export default HealthScore; 