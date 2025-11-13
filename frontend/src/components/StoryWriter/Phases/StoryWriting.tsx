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
import { triggerSubscriptionError } from '../../../api/client';

interface StoryWritingProps {
  state: ReturnType<typeof useStoryWriterState>;
  onNext: () => void;
}

// Helper function to check if story is short
const isShortStory = (storyLength: string | null | undefined): boolean => {
  if (!storyLength) return false;
  const storyLengthLower = storyLength.toLowerCase();
  return storyLengthLower.includes('short') || storyLengthLower.includes('1000');
};

const StoryWriting: React.FC<StoryWritingProps> = ({ state, onNext }) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [isContinuing, setIsContinuing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerateStart = async () => {
    if (!state.premise || (!state.outline && !state.outlineScenes)) {
      setError('Please generate a premise and outline first');
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      const request = state.getRequest();
      // Use structured scenes if available, otherwise use text outline
      const outline = state.isOutlineStructured && state.outlineScenes 
        ? state.outlineScenes 
        : (state.outline || '');
      
      const response = await storyWriterApi.generateStoryStart(
        state.premise,
        outline,
        request
      );
      
      if (response.success && response.story) {
        state.setStoryContent(response.story);
        state.setIsComplete(response.is_complete);
        state.setError(null);
      } else {
        throw new Error(response.story || 'Failed to generate story');
      }
    } catch (err: any) {
      console.error('Story start generation failed:', err);
      
      // Check if this is a subscription error (429/402) and trigger global subscription modal
      const status = err?.response?.status;
      if (status === 429 || status === 402) {
        console.log('StoryWriting: Detected subscription error, triggering global handler', {
          status,
          data: err?.response?.data
        });
        const handled = await triggerSubscriptionError(err);
        if (handled) {
          console.log('StoryWriting: Global subscription error handler triggered successfully');
          // Don't set local error - let the global modal handle it
          setIsGenerating(false);
          return;
        } else {
          console.warn('StoryWriting: Global subscription error handler did not handle the error');
        }
      }
      
      // For non-subscription errors, show local error message
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to generate story';
      setError(errorMessage);
      state.setError(errorMessage);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleContinue = async () => {
    if (!state.premise || (!state.outline && !state.outlineScenes) || !state.storyContent) {
      setError('Please generate story content first');
      return;
    }

    setIsContinuing(true);
    setError(null);

    try {
      const request = state.getRequest();
      // Use structured scenes if available, otherwise use text outline
      const outline = state.isOutlineStructured && state.outlineScenes 
        ? state.outlineScenes 
        : (state.outline || '');
      
      const continueRequest = {
        ...request,
        premise: state.premise,
        outline: outline,
        story_text: state.storyContent,
      };
      
      const response = await storyWriterApi.continueStory(continueRequest);
      
      if (response.success && response.continuation) {
        // Check if continuation is IAMDONE marker
        const isDone = response.is_complete || /IAMDONE/i.test(response.continuation);
        
        // Strip IAMDONE marker if present for cleaner display
        const cleanContinuation = response.continuation.replace(/IAMDONE/gi, '').trim();
        
        // Only append continuation if it's not just IAMDONE or empty
        if (cleanContinuation) {
          state.setStoryContent((state.storyContent || '') + '\n\n' + cleanContinuation);
        }
        
        // Set completion status
        state.setIsComplete(isDone);
        
        // If story is complete, show success message
        if (isDone) {
          console.log('Story is complete. Word count target reached.');
        }
        
        state.setError(null);
      } else {
        throw new Error(response.continuation || 'Failed to continue story');
      }
    } catch (err: any) {
      console.error('Story continuation failed:', err);
      
      // Check if this is a subscription error (429/402) and trigger global subscription modal
      const status = err?.response?.status;
      if (status === 429 || status === 402) {
        console.log('StoryWriting: Detected subscription error in continuation, triggering global handler', {
          status,
          data: err?.response?.data
        });
        const handled = await triggerSubscriptionError(err);
        if (handled) {
          console.log('StoryWriting: Global subscription error handler triggered successfully');
          // Don't set local error - let the global modal handle it
          setIsContinuing(false);
          return;
        } else {
          console.warn('StoryWriting: Global subscription error handler did not handle the error');
        }
      }
      
      // For non-subscription errors, show local error message
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to continue story';
      setError(errorMessage);
      state.setError(errorMessage);
    } finally {
      setIsContinuing(false);
    }
  };

  const handleContinueToExport = () => {
    if (state.storyContent && state.isComplete) {
      onNext();
    }
  };

  return (
    <Paper 
      sx={{ 
        p: 4, 
        mt: 2,
        backgroundColor: '#F7F3E9', // Warm cream/parchment color
        color: '#2C2416', // Dark brown text for readability
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08)',
      }}
    >
      <Typography variant="h5" gutterBottom sx={{ mb: 3, fontWeight: 600, color: '#1A1611' }}>
        Story Writing
      </Typography>
      <Typography variant="body2" sx={{ mb: 2, color: '#5D4037' }}>
        Generate your story content. You can generate the starting section and continue writing until the story is complete.
      </Typography>
      {state.storyContent && (
        <Typography variant="body2" sx={{ mb: 4, color: '#5D4037', fontStyle: 'italic' }}>
          Current word count: {state.storyContent.split(/\s+/).filter(word => word.length > 0).length} words
          {state.storyLength && (
            <> (Target: {state.storyLength.includes('1000') ? '>1000' : state.storyLength.includes('5000') ? '>5000' : '>10000'} words)</>
          )}
        </Typography>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {(!state.premise || (!state.outline && !state.outlineScenes)) && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          Please generate a premise and outline first.
        </Alert>
      )}

      {state.storyContent ? (
        <>
          <TextField
            fullWidth
            multiline
            rows={20}
            value={state.storyContent}
            onChange={(e) => state.setStoryContent(e.target.value)}
            label="Story Content"
            sx={{ mb: 3 }}
          />
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', flexWrap: 'wrap', alignItems: 'center' }}>
            {/* Only show Continue Writing button for medium/long stories that are not complete */}
            {!state.isComplete && !isShortStory(state.storyLength) && (
              <Button
                variant="outlined"
                onClick={handleContinue}
                disabled={isContinuing || !state.storyContent}
              >
                {isContinuing ? (
                  <>
                    <CircularProgress size={20} sx={{ mr: 1 }} />
                    Continuing...
                  </>
                ) : (
                  'Continue Writing'
                )}
              </Button>
            )}
            {/* Show completion message if story is complete */}
            {state.isComplete && (
              <Alert severity="success" sx={{ flex: 1, minWidth: '200px' }}>
                Story is complete! You can proceed to export.
              </Alert>
            )}
            {/* Show info message for short stories that are not complete yet */}
            {!state.isComplete && isShortStory(state.storyLength) && (
              <Alert severity="info" sx={{ flex: 1, minWidth: '200px' }}>
                Short stories are generated in one call. If the story is incomplete, please regenerate it.
              </Alert>
            )}
            <Button
              variant="contained"
              onClick={handleContinueToExport}
              disabled={!state.storyContent || !state.isComplete}
            >
              Continue to Export
            </Button>
          </Box>
        </>
      ) : (
        <Box>
          <Alert severity="info" sx={{ mb: 3 }}>
            {state.premise && (state.outline || state.outlineScenes)
              ? 'Click "Generate Story" to start writing your story.'
              : 'Please generate a premise and outline first.'}
          </Alert>
          <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              variant="contained"
              onClick={handleGenerateStart}
              disabled={isGenerating || !state.premise || (!state.outline && !state.outlineScenes)}
            >
              {isGenerating ? (
                <>
                  <CircularProgress size={20} sx={{ mr: 1 }} />
                  Generating...
                </>
              ) : (
                'Generate Story'
              )}
            </Button>
          </Box>
        </Box>
      )}
    </Paper>
  );
};

export default StoryWriting;
