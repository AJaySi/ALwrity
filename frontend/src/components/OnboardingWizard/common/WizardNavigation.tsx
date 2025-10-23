import React from 'react';
import {
  Box,
  Button,
  Typography,
  Tooltip
} from '@mui/material';
import {
  ArrowBack,
  ArrowForward,
  CheckCircle
} from '@mui/icons-material';

interface WizardNavigationProps {
  activeStep: number;
  totalSteps: number;
  onBack: () => void;
  onNext: () => void;
  isLastStep: boolean;
  isCurrentStepValid?: boolean;
}

export const WizardNavigation: React.FC<WizardNavigationProps> = ({
  activeStep,
  totalSteps,
  onBack,
  onNext,
  isLastStep,
  isCurrentStepValid = true
}) => {
  return (
    <Box
      sx={{
        p: { xs: 2, md: 3 },
        pt: 2,
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        borderTop: '1px solid rgba(0,0,0,0.08)',
        background: 'rgba(0,0,0,0.02)',
      }}
    >
      <Button
        variant="outlined"
        onClick={onBack}
        disabled={activeStep === 0}
        startIcon={<ArrowBack />}
        sx={{
          borderRadius: 2,
          textTransform: 'none',
          fontWeight: 600,
          borderColor: 'rgba(0,0,0,0.2)',
          color: 'text.primary',
          '&:hover': {
            borderColor: 'rgba(0,0,0,0.4)',
            background: 'rgba(0,0,0,0.04)',
          },
          '&:disabled': {
            borderColor: 'rgba(0,0,0,0.1)',
            color: 'rgba(0,0,0,0.3)',
          }
        }}
      >
        Back
      </Button>

      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Typography variant="body2" sx={{ opacity: 0.7, fontWeight: 500 }}>
          Step {activeStep + 1} of {totalSteps}
        </Typography>
        {isLastStep && (
          <CheckCircle sx={{ color: 'success.main', fontSize: 20 }} />
        )}
      </Box>

      {!isLastStep && (
        <Tooltip 
          title={!isCurrentStepValid ? "Complete the current step requirements to continue" : ""}
          placement="top"
        >
          <span>
            <Button
              variant="contained"
              onClick={onNext}
              disabled={!isCurrentStepValid}
              endIcon={<ArrowForward />}
              sx={{
                borderRadius: 2,
                textTransform: 'none',
                fontWeight: 600,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                boxShadow: '0 4px 12px rgba(102, 126, 234, 0.3)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%)',
                  transform: 'translateY(-1px)',
                  boxShadow: '0 6px 16px rgba(102, 126, 234, 0.4)',
                },
                '&:disabled': {
                  background: 'rgba(0,0,0,0.1)',
                  color: 'rgba(0,0,0,0.4)',
                  boxShadow: 'none',
                  transform: 'none',
                }
              }}
            >
              Continue
            </Button>
          </span>
        </Tooltip>
      )}
    </Box>
  );
};
