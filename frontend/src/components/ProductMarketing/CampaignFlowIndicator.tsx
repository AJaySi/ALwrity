import React from 'react';
import { Box, Stepper, Step, StepLabel, Typography, Chip } from '@mui/material';
import { CheckCircle, RadioButtonUnchecked } from '@mui/icons-material';

interface CampaignFlowIndicatorProps {
  currentStep: 'blueprint' | 'proposals' | 'review' | 'generate' | 'complete';
}

const steps = [
  { id: 'blueprint', label: 'Create Blueprint' },
  { id: 'proposals', label: 'Generate Proposals' },
  { id: 'review', label: 'Review & Approve' },
  { id: 'generate', label: 'Generate Assets' },
  { id: 'complete', label: 'Complete' },
];

export const CampaignFlowIndicator: React.FC<CampaignFlowIndicatorProps> = ({ currentStep }) => {
  const currentStepIndex = steps.findIndex((s) => s.id === currentStep);

  return (
    <Box sx={{ mb: 4 }}>
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
        <Typography variant="h6" fontWeight={700}>
          Campaign Flow
        </Typography>
        <Chip
          label={`Step ${currentStepIndex + 1} of ${steps.length}`}
          size="small"
          color="primary"
        />
      </Box>
      <Stepper activeStep={currentStepIndex} alternativeLabel>
        {steps.map((step, index) => (
          <Step key={step.id} completed={index < currentStepIndex}>
            <StepLabel
              StepIconComponent={({ active, completed }) => (
                <Box
                  sx={{
                    width: 40,
                    height: 40,
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    background: completed
                      ? 'linear-gradient(135deg, #7c3aed, #a78bfa)'
                      : active
                      ? 'rgba(124, 58, 237, 0.2)'
                      : 'rgba(255,255,255,0.1)',
                    border: active ? '2px solid #7c3aed' : 'none',
                  }}
                >
                  {completed ? (
                    <CheckCircle sx={{ color: '#fff', fontSize: 24 }} />
                  ) : (
                    <RadioButtonUnchecked
                      sx={{
                        color: active ? '#7c3aed' : 'rgba(255,255,255,0.5)',
                        fontSize: 24,
                      }}
                    />
                  )}
                </Box>
              )}
            >
              {step.label}
            </StepLabel>
          </Step>
        ))}
      </Stepper>
    </Box>
  );
};

