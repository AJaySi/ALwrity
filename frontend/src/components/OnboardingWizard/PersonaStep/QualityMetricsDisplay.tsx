import React from 'react';
import {
  Box,
  Grid,
  Typography,
  Stack
} from '@mui/material';

interface QualityMetrics {
  overall_score: number;
  style_consistency?: number;
  brand_alignment?: number;
  platform_optimization?: number;
  engagement_potential?: number;
  core_completeness?: number;
  platform_consistency?: number;
  linguistic_quality?: number;
  recommendations: string[];
}

interface QualityMetricsDisplayProps {
  metrics: QualityMetrics;
}

export const QualityMetricsDisplay: React.FC<QualityMetricsDisplayProps> = ({ metrics }) => {
  // Determine which metric set is being used (old vs new)
  const isNewMetrics = metrics.core_completeness !== undefined;
  
  const metricItems = isNewMetrics ? [
    { label: 'Overall Quality', value: metrics.overall_score },
    { label: 'Brand Voice Accuracy', value: metrics.core_completeness || 0 },
    { label: 'Platform Consistency', value: metrics.platform_consistency || 0 },
    { label: 'Platform Optimization', value: metrics.platform_optimization || 0 },
    { label: 'Linguistic Quality', value: metrics.linguistic_quality || 0 }
  ] : [
    { label: 'Overall Quality', value: metrics.overall_score },
    { label: 'Style Consistency', value: metrics.style_consistency || 0 },
    { label: 'Brand Voice Accuracy', value: metrics.brand_alignment || 0 },
    { label: 'Platform Optimization', value: metrics.platform_optimization || 0 },
    { label: 'Engagement Potential', value: metrics.engagement_potential || 0 }
  ];

  return (
    <Grid container spacing={4}>
      <Grid item xs={12} md={6}>
        <Box sx={{
          p: 3,
          background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
          border: '1px solid #e2e8f0',
          borderRadius: 3,
          height: '100%'
        }}>
          <Typography variant="h6" sx={{ fontWeight: 600, color: '#1e293b', mb: 3 }}>
            Performance Scores
          </Typography>
          <Stack spacing={3}>
            {metricItems.map((metric, index) => (
              <Box key={index}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5 }}>
                  <Typography variant="body2" sx={{ fontWeight: 500, color: '#334155' }}>
                    {metric.label}
                  </Typography>
                  <Typography variant="body2" sx={{
                    fontWeight: 700,
                    color: metric.value >= 85 ? '#059669' : metric.value >= 70 ? '#d97706' : '#dc2626'
                  }}>
                    {metric.value}%
                  </Typography>
                </Box>
                <Box sx={{
                  width: '100%',
                  height: 10,
                  backgroundColor: '#e2e8f0',
                  borderRadius: 5,
                  overflow: 'hidden',
                  position: 'relative'
                }}>
                  <Box
                    sx={{
                      width: `${metric.value}%`,
                      height: '100%',
                      background: metric.value >= 85
                        ? 'linear-gradient(90deg, #10b981 0%, #059669 100%)'
                        : metric.value >= 70
                        ? 'linear-gradient(90deg, #f59e0b 0%, #d97706 100%)'
                        : 'linear-gradient(90deg, #ef4444 0%, #dc2626 100%)',
                      borderRadius: 5,
                      transition: 'width 1s ease-in-out'
                    }}
                  />
                </Box>
              </Box>
            ))}
          </Stack>
        </Box>
      </Grid>
      <Grid item xs={12} md={6}>
        <Box sx={{
          p: 3,
          background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
          border: '1px solid #e2e8f0',
          borderRadius: 3,
          height: '100%'
        }}>
          <Typography variant="h6" sx={{ fontWeight: 600, color: '#1e293b', mb: 3 }}>
            Recommendations
          </Typography>
          <Stack spacing={2}>
            {metrics.recommendations && metrics.recommendations.length > 0 ? (
              metrics.recommendations.map((recommendation, index) => (
                <Box key={index} sx={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: 2,
                  p: 2,
                  background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
                  border: '1px solid #e2e8f0',
                  borderRadius: 2,
                  boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05)'
                }}>
                  <Box sx={{
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
                    mt: 0.5,
                    flexShrink: 0
                  }} />
                  <Typography variant="body2" sx={{ color: '#334155', lineHeight: 1.6 }}>
                    {recommendation}
                  </Typography>
                </Box>
              ))
            ) : (
              <Box sx={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: 2,
                p: 2,
                background: 'linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%)',
                border: '1px solid #10b981',
                borderRadius: 2
              }}>
                <Box sx={{
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                  mt: 0.5,
                  flexShrink: 0
                }} />
                <Typography variant="body2" sx={{ color: '#065f46', lineHeight: 1.6 }}>
                  Your personas demonstrate excellent quality across all assessment criteria!
                </Typography>
              </Box>
            )}
          </Stack>
        </Box>
      </Grid>
    </Grid>
  );
};

export default QualityMetricsDisplay;

