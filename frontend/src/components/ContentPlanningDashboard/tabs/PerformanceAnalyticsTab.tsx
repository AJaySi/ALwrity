import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography
} from '@mui/material';
import {
} from '@mui/icons-material';
import { useContentPlanningStore } from '../../../stores/contentPlanningStore';

const PerformanceAnalyticsTab: React.FC = () => {
  const { performanceMetrics } = useContentPlanningStore();

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Performance Analytics
      </Typography>

      {performanceMetrics ? (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Content Performance by Type
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  No content performance data available
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Growth Trends
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  No trend data available
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      ) : (
        <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', p: 3 }}>
          No performance analytics data available
        </Typography>
      )}
    </Box>
  );
};

export default PerformanceAnalyticsTab; 