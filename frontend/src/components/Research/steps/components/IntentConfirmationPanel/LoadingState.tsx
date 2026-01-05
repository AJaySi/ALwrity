/**
 * LoadingState Component
 * 
 * Displays loading indicator while intent is being analyzed.
 */

import React from 'react';
import { Box, Typography, Paper, CircularProgress } from '@mui/material';

interface LoadingStateProps {
  message?: string;
  subMessage?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = '🧠 Analyzing your research intent...',
  subMessage = 'AI is understanding what you want to accomplish',
}) => {
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
            {message}
          </Typography>
          <Typography variant="body2" color="#666">
            {subMessage}
          </Typography>
        </Box>
      </Box>
    </Paper>
  );
};
