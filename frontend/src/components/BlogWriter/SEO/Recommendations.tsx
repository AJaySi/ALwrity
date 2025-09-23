/**
 * Recommendations Component
 * 
 * Displays actionable SEO recommendations with priority indicators,
 * category tags, and impact descriptions.
 */

import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Chip
} from '@mui/material';
import { 
  Lightbulb,
  CheckCircle,
  Cancel,
  Warning
} from '@mui/icons-material';

interface Recommendation {
  category: string;
  priority: 'High' | 'Medium' | 'Low';
  recommendation: string;
  impact: string;
}

interface RecommendationsProps {
  recommendations: Recommendation[];
}

export const Recommendations: React.FC<RecommendationsProps> = ({ recommendations }) => {
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'High': return 'error.main';
      case 'Medium': return 'warning.main';
      case 'Low': return 'success.main';
      default: return 'text.secondary';
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'High': return <Cancel sx={{ fontSize: 16 }} />;
      case 'Medium': return <Warning sx={{ fontSize: 16 }} />;
      case 'Low': return <CheckCircle sx={{ fontSize: 16 }} />;
      default: return <Warning sx={{ fontSize: 16 }} />;
    }
  };

  const getScoreBadgeVariant = (score: number) => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'error';
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
        <Lightbulb sx={{ color: 'primary.main' }} />
        <Typography variant="h6" component="h3" sx={{ fontWeight: 600 }}>
          Actionable Recommendations
        </Typography>
      </Box>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {recommendations.map((rec, index) => (
          <Paper 
            key={index} 
            sx={{ 
              p: 3, 
              border: '1px solid rgba(255,255,255,0.1)',
              background: 'rgba(255,255,255,0.03)',
              borderRadius: 2
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
              <Box sx={{ color: getPriorityColor(rec.priority), mt: 0.5 }}>
                {getPriorityIcon(rec.priority)}
              </Box>
              <Box sx={{ flex: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <Chip 
                    label={rec.category} 
                    variant="outlined" 
                    size="small"
                    sx={{ borderColor: 'rgba(255,255,255,0.3)' }}
                  />
                  <Chip 
                    label={rec.priority}
                    color={getScoreBadgeVariant(rec.priority === 'High' ? 30 : 70)}
                    size="small"
                  />
                </Box>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  {rec.recommendation}
                </Typography>
                <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                  {rec.impact}
                </Typography>
              </Box>
            </Box>
          </Paper>
        ))}
      </Box>
    </Box>
  );
};
