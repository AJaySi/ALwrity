import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  Alert,
  CircularProgress,
} from '@mui/material';
import { useStoryWriterState } from '../../../hooks/useStoryWriterState';
import { storyWriterApi } from '../../../services/storyWriterApi';

interface StoryPremiseProps {
  state: ReturnType<typeof useStoryWriterState>;
  onNext: () => void;
}

const StoryPremise: React.FC<StoryPremiseProps> = ({ state, onNext }) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRegenerate = async () => {
    setIsGenerating(true);
    setError(null);

    try {
      const request = state.getRequest();
      const response = await storyWriterApi.generatePremise(request);
      
      if (response.success && response.premise) {
        state.setPremise(response.premise);
        state.setError(null);
      } else {
        throw new Error(response.premise || 'Failed to generate premise');
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to generate premise';
      setError(errorMessage);
      state.setError(errorMessage);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleContinue = () => {
    if (state.premise) {
      onNext();
    }
  };

  return (
    <Paper sx={{ p: 4, mt: 2 }}>
      <Typography variant="h5" gutterBottom sx={{ mb: 3, fontWeight: 600 }}>
        Story Premise
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
        Review and refine your story premise. You can regenerate it or proceed to create the outline.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {state.premise ? (
        <>
          <TextField
            fullWidth
            multiline
            rows={8}
            value={state.premise}
            onChange={(e) => state.setPremise(e.target.value)}
            label="Story Premise"
            sx={{ mb: 3 }}
          />
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
            <Button
              variant="outlined"
              onClick={handleRegenerate}
              disabled={isGenerating}
            >
              {isGenerating ? (
                <>
                  <CircularProgress size={20} sx={{ mr: 1 }} />
                  Regenerating...
                </>
              ) : (
                'Regenerate Premise'
              )}
            </Button>
            <Button
              variant="contained"
              onClick={handleContinue}
              disabled={!state.premise || isGenerating}
            >
              Continue to Outline
            </Button>
          </Box>
        </>
      ) : (
        <Alert severity="info" sx={{ mb: 3 }}>
          No premise generated yet. Please go back to Setup and generate a premise first.
        </Alert>
      )}
    </Paper>
  );
};

export default StoryPremise;
