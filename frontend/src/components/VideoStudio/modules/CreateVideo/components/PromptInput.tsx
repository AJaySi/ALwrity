import React, { useState } from 'react';
import { Box, TextField, Typography, Stack, Button, CircularProgress, Tooltip } from '@mui/material';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import { CarouselPlaceholder } from '../../CarouselPlaceholder';
import { examplePrompts, exampleNegativePrompts, inputStyles, colors } from '../constants';
import { optimizePrompt } from '../../../../../api/videoStudioApi';

interface PromptInputProps {
  prompt: string;
  negativePrompt: string;
  promptFocused: boolean;
  negativeFocused: boolean;
  promptPlaceholderIndex: number;
  negativePlaceholderIndex: number;
  onPromptChange: (value: string) => void;
  onNegativePromptChange: (value: string) => void;
  onPromptFocus: () => void;
  onPromptBlur: () => void;
  onNegativeFocus: () => void;
  onNegativeBlur: () => void;
  onPromptPlaceholderChange: (index: number) => void;
  onNegativePlaceholderChange: (index: number) => void;
}

export const PromptInput: React.FC<PromptInputProps> = ({
  prompt,
  negativePrompt,
  promptFocused,
  negativeFocused,
  promptPlaceholderIndex,
  negativePlaceholderIndex,
  onPromptChange,
  onNegativePromptChange,
  onPromptFocus,
  onPromptBlur,
  onNegativeFocus,
  onNegativeBlur,
  onPromptPlaceholderChange,
  onNegativePlaceholderChange,
}) => {
  const [enhancing, setEnhancing] = useState(false);

  const handleEnhancePrompt = async () => {
    if (!prompt.trim() || enhancing) return;

    setEnhancing(true);
    try {
      const result = await optimizePrompt({
        text: prompt,
        mode: 'video', // Always use 'video' mode for Video Studio
        style: 'default',
      });

      if (result.success && result.optimized_prompt) {
        onPromptChange(result.optimized_prompt);
      }
    } catch (error) {
      console.error('Failed to enhance prompt:', error);
      // Optionally show error toast/notification
    } finally {
      setEnhancing(false);
    }
  };

  return (
    <Stack spacing={3}>
      <Box>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
          <Typography
            variant="subtitle2"
            sx={{
              color: colors.primary,
              fontWeight: 700,
            }}
          >
            Describe Your Video
          </Typography>
          <Tooltip
            title={
              <Box sx={{ p: 0.5 }}>
                <Typography variant="caption" sx={{ display: 'block', fontWeight: 600, mb: 0.5 }}>
                  AI Prompt Optimizer
                </Typography>
                <Typography variant="caption" sx={{ display: 'block', fontSize: '0.7rem' }}>
                  Enhances your prompt for better video generation by improving:
                </Typography>
                <Typography variant="caption" sx={{ display: 'block', fontSize: '0.7rem', mt: 0.5 }}>
                  • Visual clarity & composition
                </Typography>
                <Typography variant="caption" sx={{ display: 'block', fontSize: '0.7rem' }}>
                  • Cinematic framing & lighting
                </Typography>
                <Typography variant="caption" sx={{ display: 'block', fontSize: '0.7rem' }}>
                  • Camera movement & style consistency
                </Typography>
              </Box>
            }
            arrow
            placement="top"
          >
            <Button
              size="small"
              variant="outlined"
              startIcon={enhancing ? <CircularProgress size={16} /> : <AutoAwesomeIcon />}
              onClick={handleEnhancePrompt}
              disabled={!prompt.trim() || enhancing}
              sx={{
                textTransform: 'none',
                fontSize: '0.75rem',
                py: 0.5,
                px: 1.5,
                borderColor: colors.primary,
                color: colors.primary,
                '&:hover': {
                  borderColor: colors.primary,
                  backgroundColor: 'rgba(59, 130, 246, 0.1)',
                },
                '&:disabled': {
                  borderColor: '#cbd5e1',
                  color: '#94a3b8',
                },
              }}
            >
              {enhancing ? 'Enhancing...' : 'Enhance Instructions'}
            </Button>
          </Tooltip>
        </Box>
        <Box sx={{ position: 'relative' }}>
          <TextField
            fullWidth
            multiline
            rows={4}
            placeholder="Enter your video description..."
            value={prompt}
            onChange={e => onPromptChange(e.target.value)}
            onFocus={onPromptFocus}
            onBlur={onPromptBlur}
            sx={{
              '& .MuiOutlinedInput-root': {
                ...inputStyles.outlinedInputBase,
                minHeight: 140,
              },
              '& .MuiInputBase-input': {
                color: '#0f172a',
                '&::placeholder': {
                  color: '#64748b',
                  opacity: 1,
                },
              },
            }}
          />
          {!prompt && (
            <Box
              sx={{
                position: 'absolute',
                top: 56,
                left: 14,
                right: 14,
                pointerEvents: 'none',
                zIndex: 1,
                opacity: promptFocused ? 0 : 1,
                transition: 'opacity 0.2s ease',
              }}
            >
              <CarouselPlaceholder
                examples={examplePrompts}
                interval={4000}
                paused={promptFocused}
                onExampleChange={(_: string, idx: number) => onPromptPlaceholderChange(idx)}
              />
            </Box>
          )}
        </Box>
      </Box>

      <Box>
        <Typography
          variant="subtitle2"
          sx={{
            mb: 1,
            color: colors.primary,
            fontWeight: 700,
          }}
        >
          What to Avoid (Optional)
        </Typography>
        <Box sx={{ position: 'relative' }}>
          <TextField
            label="What to avoid (optional)"
            value={negativePrompt}
            onChange={e => onNegativePromptChange(e.target.value)}
            onFocus={onNegativeFocus}
            onBlur={onNegativeBlur}
            fullWidth
            sx={{
              '& .MuiOutlinedInput-root': inputStyles.outlinedInputBase,
              '& .MuiInputBase-input': {
                color: '#0f172a',
                '&::placeholder': {
                  color: '#64748b',
                  opacity: 1,
                },
              },
            }}
          />
          {!negativePrompt && (
            <Box
              sx={{
                position: 'absolute',
                top: 40,
                left: 14,
                right: 14,
                pointerEvents: 'none',
                zIndex: 1,
                opacity: negativeFocused ? 0 : 1,
                transition: 'opacity 0.2s ease',
              }}
            >
              <CarouselPlaceholder
                examples={exampleNegativePrompts}
                interval={4000}
                paused={negativeFocused}
                onExampleChange={(_: string, idx: number) => onNegativePlaceholderChange(idx)}
              />
            </Box>
          )}
        </Box>
        <Typography
          variant="caption"
          sx={{
            mt: 1,
            display: 'block',
            color: colors.muted,
          }}
        >
          Use this to specify what you don't want in your video (e.g., "blurry, low quality, distorted faces")
        </Typography>
      </Box>
    </Stack>
  );
};