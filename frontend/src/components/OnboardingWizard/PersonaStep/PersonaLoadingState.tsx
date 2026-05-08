import React from 'react';
import {
  Box,
  Button,
  Typography,
  Alert,
  Card,
  CardContent,
  LinearProgress,
  Fade
} from '@mui/material';
import PsychologyIcon from '@mui/icons-material/Psychology';
import { PersonaGenerationProgress } from './PersonaGenerationProgress';
import { type GenerationStep } from './PersonaGenerationProgress';

interface PersonaLoadingStateProps {
  showPreview: boolean;
  isGenerating: boolean;
  corePersona: any;
  progress: number;
  generationStep: string;
  generationSteps: GenerationStep[];
  progressMessages: any[];
  error: string | null;
  pollingError: string | null;
  success: string | null;
  handleRegenerate: () => void;
  generatePersonas: () => void;
  setShowPreview: (show: boolean) => void;
  setSuccess: (message: string | null) => void;
}

export const PersonaLoadingState: React.FC<PersonaLoadingStateProps> = ({
  showPreview,
  isGenerating,
  corePersona,
  progress,
  generationStep,
  generationSteps,
  progressMessages,
  error,
  pollingError,
  success,
  handleRegenerate,
  generatePersonas,
  setShowPreview,
  setSuccess
}) => {
  return (
    <>
      {/* Safeguard: show loading instead of blank while initial checks run */}
      {!showPreview && !isGenerating && !corePersona && (
        <Fade in={true}>
          <Card sx={{
            mb: 4,
            background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
            border: '1px solid #e2e8f0',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)',
            borderRadius: 3
          }}>
            <CardContent sx={{ p: 4, textAlign: 'center' }}>
              <Box sx={{ mb: 3 }}>
                <Box
                  sx={{
                    width: 64,
                    height: 64,
                    borderRadius: '50%',
                    background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mx: 'auto',
                    mb: 2
                  }}
                >
                  <PsychologyIcon sx={{ fontSize: 32, color: 'white' }} />
                </Box>
                <Typography variant="h6" sx={{ fontWeight: 600, color: '#1e293b', mb: 1 }}>
                  Preparing Persona Workspace
                </Typography>
                <Typography variant="body2" sx={{ color: '#64748b' }}>
                  Checking cache and initializing generation...
                </Typography>
              </Box>
              <LinearProgress
                sx={{
                  height: 6,
                  borderRadius: 3,
                  backgroundColor: '#e2e8f0',
                  '& .MuiLinearProgress-bar': {
                    borderRadius: 3,
                    background: 'linear-gradient(90deg, #3b82f6 0%, #1d4ed8 100%)'
                  }
                }}
              />
            </CardContent>
          </Card>
        </Fade>
      )}

      {/* Generation Progress */}
      <PersonaGenerationProgress
        isGenerating={isGenerating}
        progress={progress}
        currentStep={generationStep}
        generationSteps={generationSteps}
        progressMessages={progressMessages}
      />

      {/* Error Display */}
      {(error || pollingError) && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error || pollingError}
          <Button 
            size="small" 
            onClick={handleRegenerate}
            sx={{ ml: 2 }}
          >
            Try Again
          </Button>
        </Alert>
      )}

      {/* Generate New Button (when cached data is loaded) */}
      {showPreview && success && success.includes('cached') && (
        <Alert severity="info" sx={{ mb: 3 }}>
          {success}
          <Button 
            size="small" 
            onClick={() => {
              setShowPreview(false);
              setSuccess(null);
              generatePersonas();
            }}
            sx={{ ml: 2 }}
          >
            Generate New
          </Button>
        </Alert>
      )}
    </>
  );
};
