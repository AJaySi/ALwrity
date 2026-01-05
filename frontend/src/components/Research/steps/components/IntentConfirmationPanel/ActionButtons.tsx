/**
 * ActionButtons Component
 * 
 * Action buttons section (More details toggle and Start Research).
 */

import React from 'react';
import {
  Box,
  Button,
  CircularProgress,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  PlayArrow as PlayIcon,
} from '@mui/icons-material';

interface ActionButtonsProps {
  showDetails: boolean;
  onToggleDetails: () => void;
  onExecute: () => void;
  isExecuting: boolean;
  canExecute: boolean;
}

export const ActionButtons: React.FC<ActionButtonsProps> = ({
  showDetails,
  onToggleDetails,
  onExecute,
  isExecuting,
  canExecute,
}) => {
  return (
    <Box
      display="flex"
      justifyContent="space-between"
      alignItems="center"
      mt={2}
      pt={2}
      borderTop="1px solid #e5e7eb"
    >
      <Button
        size="small"
        onClick={onToggleDetails}
        endIcon={showDetails ? <ExpandLessIcon /> : <ExpandMoreIcon />}
        sx={{
          color: '#666',
          '&:hover': { backgroundColor: '#f3f4f6' },
        }}
      >
        {showDetails ? 'Less details' : 'More details'}
      </Button>
      <Button
        variant="contained"
        color="primary"
        startIcon={isExecuting ? <CircularProgress size={16} color="inherit" /> : <PlayIcon />}
        onClick={onExecute}
        disabled={isExecuting || !canExecute}
        sx={{
          backgroundColor: '#0ea5e9',
          '&:hover': { backgroundColor: '#0284c7' },
          '&:disabled': { backgroundColor: '#d1d5db', color: '#9ca3af' },
        }}
      >
        {isExecuting ? 'Researching...' : 'Start Research'}
      </Button>
    </Box>
  );
};
