import React from 'react';
import { Box, Paper, Stepper, Step, StepLabel, StepButton, Typography, IconButton, Tooltip } from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import { StoryPhase } from '../../hooks/useStoryWriterPhaseNavigation';

interface PhaseNavigationProps {
  phases: StoryPhase[];
  currentPhase: string;
  onPhaseClick: (phaseId: string) => void;
  onReset?: () => void;
}

export const PhaseNavigation: React.FC<PhaseNavigationProps> = ({
  phases,
  currentPhase,
  onPhaseClick,
  onReset,
}) => {
  const activeStep = phases.findIndex((p) => p.id === currentPhase);

  const handleReset = () => {
    if (window.confirm('Are you sure you want to restart? This will clear all your story data and start from the beginning.')) {
      if (onReset) {
        onReset();
      }
    }
  };

  return (
    <Paper 
      sx={{ 
        p: 3,
        backgroundColor: '#F7F3E9', // Warm cream/parchment color
        color: '#2C2416', // Dark brown text for readability
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08)',
      }}
    >
      {onReset && (
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
        <Tooltip title="Restart Story (Clear all data and start from beginning)">
          <IconButton
            onClick={handleReset}
            sx={{
              color: '#5D4037',
              '&:hover': {
                backgroundColor: '#E8E5D3',
                color: '#1A1611',
              },
            }}
            size="small"
          >
            <RefreshIcon />
          </IconButton>
        </Tooltip>
        </Box>
      )}
      <Stepper activeStep={activeStep} alternativeLabel>
        {phases.map((phase) => (
          <Step key={phase.id} completed={phase.completed} disabled={phase.disabled}>
            <StepButton
              onClick={() => !phase.disabled && onPhaseClick(phase.id)}
              disabled={phase.disabled}
              sx={{
                '& .MuiStepLabel-root': {
                  cursor: phase.disabled ? 'not-allowed' : 'pointer',
                },
              }}
            >
              <StepLabel
                StepIconComponent={() => (
                  <Box
                    sx={{
                      width: 40,
                      height: 40,
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      backgroundColor: phase.current
                        ? 'primary.main'
                        : phase.completed
                        ? 'success.main'
                        : phase.disabled
                        ? 'grey.300'
                        : 'grey.200',
                      color: phase.current || phase.completed ? 'white' : 'text.secondary',
                      fontSize: '1.2rem',
                      fontWeight: phase.current ? 600 : 400,
                    }}
                  >
                    {phase.icon}
                  </Box>
                )}
              >
                <Typography
                  variant="body2"
                  sx={{
                    fontWeight: phase.current ? 600 : 400,
                    color: phase.disabled ? '#9E9E9E' : '#2C2416', // Dark brown text
                  }}
                >
                  {phase.name}
                </Typography>
                <Typography
                  variant="caption"
                  sx={{
                    color: phase.disabled ? '#9E9E9E' : '#5D4037', // Medium brown for secondary text
                    fontSize: '0.7rem',
                  }}
                >
                  {phase.description}
                </Typography>
              </StepLabel>
            </StepButton>
          </Step>
        ))}
      </Stepper>
    </Paper>
  );
};

export default PhaseNavigation;
