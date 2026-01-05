/**
 * LoadingState Component
 * 
 * Loading indicator for intent analysis.
 */

import React from 'react';
import {
  Box,
  Typography,
  Paper,
  CircularProgress,
} from '@mui/material';

export const LoadingState: React.FC = () => {
  return (
    <Paper
      elevation={0}
      sx={{
        p: 3,
        mt: 2,
        borderRadius: 2,
        border: '1px solid #e0e0e0',
        backgroundColor: '#ffffff',
      }}
    >
      <Box display="flex" alignItems="center" gap={2}>
        <CircularProgress size={24} />
        <Box>
          <Typography variant="subtitle1" fontWeight={600} color="#333">
            🧠 Analyzing your research intent...
          </Typography>
          <Typography variant="body2" color="#666">
            AI is understanding what you want to accomplish
          </Typography>
        </Box>
      </Box>
    </Paper>
  );
};
