import React from 'react';
import { Box, Typography, Button, Avatar } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { AIInsightsPanel as StyledAIInsightsPanel } from '../../shared/styled';
import { AIInsight } from '../../../api/seoDashboard';

interface AIInsightsPanelProps {
  insights: AIInsight[];
}

const AIInsightsPanel: React.FC<AIInsightsPanelProps> = ({ insights }) => {
  return (
    <StyledAIInsightsPanel>
      <Box sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
          <Avatar sx={{ 
            background: 'linear-gradient(135deg, #667eea, #764ba2)',
            width: 48,
            height: 48
          }}>
            🤖
          </Avatar>
          <Box>
            <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
              AI SEO Assistant
            </Typography>
            <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
              Analyzing your data...
            </Typography>
          </Box>
        </Box>
        
        <Typography variant="body1" sx={{ 
          color: 'rgba(255, 255, 255, 0.9)',
          mb: 3,
          lineHeight: 1.6
        }}>
          💡 Based on your current performance, here are my recommendations:
        </Typography>
        
        <Box sx={{ mb: 3 }}>
          {insights.map((insight, index) => (
            <Box key={index} sx={{ 
              display: 'flex', 
              alignItems: 'flex-start', 
              gap: 2, 
              mb: 2,
              p: 2,
              background: 'rgba(255, 255, 255, 0.05)',
              borderRadius: 2,
              border: '1px solid rgba(255, 255, 255, 0.1)'
            }}>
              <CheckCircleIcon sx={{ 
                color: '#4CAF50', 
                fontSize: 20,
                mt: 0.5
              }} />
              <Typography variant="body2" sx={{ 
                color: 'rgba(255, 255, 255, 0.8)',
                flex: 1
              }}>
                {insight.insight}
              </Typography>
            </Box>
          ))}
        </Box>
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            size="small"
            sx={{
              background: 'linear-gradient(135deg, #667eea, #764ba2)',
              color: 'white',
              fontWeight: 600,
              '&:hover': {
                background: 'linear-gradient(135deg, #5a6fd8, #6a4190)',
              },
            }}
          >
            Optimize Now
          </Button>
          <Button
            variant="outlined"
            size="small"
            sx={{
              color: 'white',
              borderColor: 'rgba(255, 255, 255, 0.3)',
              '&:hover': {
                borderColor: 'rgba(255, 255, 255, 0.5)',
                background: 'rgba(255, 255, 255, 0.1)',
              },
            }}
          >
            Learn More
          </Button>
        </Box>
      </Box>
    </StyledAIInsightsPanel>
  );
};

export default AIInsightsPanel; 