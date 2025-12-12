import React from "react";
import { Box, Paper, Stepper, Step, StepLabel, Typography, alpha } from "@mui/material";
import {
  Psychology as PsychologyIcon,
  Search as SearchIcon,
  EditNote as EditNoteIcon,
  PlayArrow as PlayArrowIcon,
  CheckCircle as CheckCircleIcon,
} from "@mui/icons-material";

interface ProgressStepperProps {
  activeStep: number;
  completedSteps?: number[]; // Steps that have been completed (have data)
  onStepClick?: (stepIndex: number) => void;
}

const steps = [
  { label: "Analysis", icon: <PsychologyIcon />, description: "AI analyzes your idea" },
  { label: "Research", icon: <SearchIcon />, description: "Gather facts and citations" },
  { label: "Script", icon: <EditNoteIcon />, description: "Edit and approve scenes" },
  { label: "Render", icon: <PlayArrowIcon />, description: "Generate audio files" },
];

export const ProgressStepper: React.FC<ProgressStepperProps> = ({ activeStep, completedSteps = [], onStepClick }) => {
  if (activeStep < 0) return null;

  const handleStepClick = (stepIndex: number) => {
    // Allow navigation to any completed step (has data), not just steps before active step
    const isCompleted = completedSteps.includes(stepIndex);
    if (isCompleted && onStepClick) {
      onStepClick(stepIndex);
    }
  };

  return (
    <Paper
      sx={{
        p: 2.5,
        background: "#f8fafc",
        border: "1px solid rgba(0,0,0,0.08)",
        borderRadius: 2,
      }}
    >
      <Stepper activeStep={activeStep} orientation="horizontal">
        {steps.map((step, index) => {
          const isCompleted = completedSteps.includes(index);
          const isClickable = isCompleted && onStepClick !== undefined;
          
          return (
            <Step key={step.label} completed={isCompleted}>
              <StepLabel
                onClick={() => handleStepClick(index)}
                sx={{
                  cursor: isClickable ? "pointer" : "default",
                  "&:hover": isClickable
                    ? {
                        "& .MuiStepLabel-label": {
                          color: "#667eea",
                        },
                      }
                    : {},
                }}
                StepIconComponent={({ active, completed }) => (
                  <Box
                    sx={{
                      width: 40,
                      height: 40,
                      borderRadius: "50%",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      background: completed
                        ? "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
                        : active
                        ? alpha("#667eea", 0.15)
                        : "#e2e8f0",
                      border: active ? "2px solid #667eea" : "1px solid rgba(0,0,0,0.1)",
                      color: completed || active ? "#fff" : "#64748b",
                      transition: "all 0.2s ease",
                      ...(isClickable && {
                        cursor: "pointer",
                        "&:hover": {
                          transform: "scale(1.05)",
                          boxShadow: "0 2px 8px rgba(102, 126, 234, 0.3)",
                        },
                      }),
                    }}
                  >
                    {completed ? <CheckCircleIcon /> : step.icon}
                  </Box>
                )}
              >
                <Typography variant="subtitle2">{step.label}</Typography>
                <Typography variant="caption" color="text.secondary">
                  {step.description}
                </Typography>
              </StepLabel>
            </Step>
          );
        })}
      </Stepper>
    </Paper>
  );
};

