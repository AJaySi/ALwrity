import React from 'react';
import { Box, Stepper, Step, StepLabel, StepButton, Typography, IconButton, Tooltip } from '@mui/material';
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
    <Box sx={{ position: 'relative' }}>
      {onReset && (
        <Box sx={{ position: 'absolute', top: -8, right: -8, zIndex: 10 }}>
        <Tooltip title="Restart Story (Clear all data and start from beginning)">
          <IconButton
            onClick={handleReset}
            sx={{
                color: 'rgba(255, 255, 255, 0.9)',
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
              '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.2)',
                  color: 'white',
              },
            }}
            size="small"
          >
              <RefreshIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        </Box>
      )}
      <Stepper 
        activeStep={activeStep} 
        alternativeLabel
        sx={{
          backgroundColor: 'transparent',
          '& .MuiStepLabel-label': {
            color: 'rgba(255, 255, 255, 0.9)',
            '&.Mui-active': {
              color: 'white',
            },
            '&.Mui-completed': {
              color: 'rgba(255, 255, 255, 0.7)',
            },
            '&.Mui-disabled': {
              color: 'rgba(255, 255, 255, 0.4)',
            },
          },
          '& .MuiStepLabel-iconContainer': {
            '& .MuiSvgIcon-root': {
              color: 'rgba(255, 255, 255, 0.3)',
              '&.Mui-active': {
                color: 'rgba(255, 255, 255, 0.6)',
              },
              '&.Mui-completed': {
                color: 'rgba(255, 255, 255, 0.5)',
              },
            },
          },
        }}
      >
        {phases.map((phase) => (
          <Step key={phase.id} completed={phase.completed} disabled={phase.disabled}>
            <StepButton
              onClick={() => !phase.disabled && onPhaseClick(phase.id)}
              disabled={phase.disabled}
              sx={{
                padding: '8px 4px',
                '& .MuiStepLabel-root': {
                  cursor: phase.disabled ? 'not-allowed' : 'pointer',
                },
              }}
            >
              <StepLabel
                StepIconComponent={() => (
                  <Box
                    sx={{
                      width: 32,
                      height: 32,
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      backgroundColor: phase.current
                        ? 'rgba(255, 255, 255, 0.9)'
                        : phase.completed
                        ? 'rgba(76, 175, 80, 0.9)'
                        : phase.disabled
                        ? 'rgba(255, 255, 255, 0.2)'
                        : 'rgba(255, 255, 255, 0.3)',
                      color: phase.current 
                        ? '#667eea'
                        : phase.completed 
                        ? 'white' 
                        : 'rgba(255, 255, 255, 0.7)',
                      fontSize: '1rem',
                      fontWeight: phase.current ? 600 : 400,
                      transition: 'all 0.2s ease',
                      '&:hover': !phase.disabled ? {
                        backgroundColor: phase.current
                          ? 'rgba(255, 255, 255, 1)'
                          : 'rgba(255, 255, 255, 0.4)',
                        transform: 'scale(1.05)',
                      } : {},
                    }}
                  >
                    {phase.icon}
                  </Box>
                )}
              >
                <Typography
                  variant="caption"
                  sx={{
                    fontWeight: phase.current ? 600 : 400,
                    fontSize: '0.75rem',
                    color: phase.disabled 
                      ? 'rgba(255, 255, 255, 0.4)' 
                      : phase.current 
                      ? 'white' 
                      : 'rgba(255, 255, 255, 0.8)',
                    mt: 0.5,
                  }}
                >
                  {phase.name}
                </Typography>
              </StepLabel>
            </StepButton>
          </Step>
        ))}
      </Stepper>
    </Box>
  );
};

export default PhaseNavigation;
