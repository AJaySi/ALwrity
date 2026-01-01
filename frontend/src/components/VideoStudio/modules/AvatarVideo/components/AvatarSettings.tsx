import React, { useState } from 'react';
import { Box, Stack, Typography, FormControl, InputLabel, Select, MenuItem, TextField, Button, CircularProgress, Tooltip } from '@mui/material';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import type { AvatarResolution, AvatarModel } from '../hooks/useAvatarVideo';
import { optimizePrompt } from '../../../../../api/videoStudioApi';

interface AvatarSettingsProps {
  resolution: AvatarResolution;
  model: AvatarModel;
  prompt: string;
  seed: number | null;
  onResolutionChange: (value: AvatarResolution) => void;
  onModelChange: (value: AvatarModel) => void;
  onPromptChange: (value: string) => void;
  onSeedChange: (value: number | null) => void;
}

export const AvatarSettings: React.FC<AvatarSettingsProps> = ({
  resolution,
  model,
  prompt,
  seed,
  onResolutionChange,
  onModelChange,
  onPromptChange,
  onSeedChange,
}) => {
  const [enhancing, setEnhancing] = useState(false);

  const handleEnhancePrompt = async () => {
    if (!prompt.trim() || enhancing) return;

    setEnhancing(true);
    try {
      const result = await optimizePrompt({
        text: prompt,
        mode: 'video', // Use 'video' mode for avatar generation
        style: 'default',
      });

      if (result.success && result.optimized_prompt) {
        onPromptChange(result.optimized_prompt);
      }
    } catch (error) {
      console.error('Failed to enhance prompt:', error);
    } finally {
      setEnhancing(false);
    }
  };

  return (
    <Stack spacing={3}>
      <FormControl fullWidth>
        <InputLabel>AI Model</InputLabel>
        <Select
          value={model}
          label="AI Model"
          onChange={e => onModelChange(e.target.value as AvatarModel)}
          sx={{
            borderRadius: 2,
            backgroundColor: '#fff',
            '& fieldset': { borderColor: '#e2e8f0' },
          }}
        >
          <MenuItem value="infinitetalk">
            <Stack>
              <Typography variant="body2">InfiniteTalk - Long Form</Typography>
              <Typography variant="caption" color="text.secondary">
                Up to 10 minutes, $0.03-0.06/s
              </Typography>
            </Stack>
          </MenuItem>
          <MenuItem value="hunyuan-avatar">
            <Stack>
              <Typography variant="body2">Hunyuan Avatar - Fast & Affordable</Typography>
              <Typography variant="caption" color="text.secondary">
                Up to 2 minutes, $0.15-0.30 per 5s
              </Typography>
            </Stack>
          </MenuItem>
        </Select>
      </FormControl>

      <FormControl fullWidth>
        <InputLabel>Video Quality</InputLabel>
        <Select
          value={resolution}
          label="Video Quality"
          onChange={e => onResolutionChange(e.target.value as AvatarResolution)}
          sx={{
            borderRadius: 2,
            backgroundColor: '#fff',
            '& fieldset': { borderColor: '#e2e8f0' },
          }}
        >
          <MenuItem value="480p">
            <Stack>
              <Typography variant="body2">480p - Fast & Affordable</Typography>
              <Typography variant="caption" color="text.secondary">
                {model === 'hunyuan-avatar' ? '$0.15 per 5 seconds' : '$0.03 per second'}
              </Typography>
            </Stack>
          </MenuItem>
          <MenuItem value="720p">
            <Stack>
              <Typography variant="body2">720p - High Quality</Typography>
              <Typography variant="caption" color="text.secondary">
                {model === 'hunyuan-avatar' ? '$0.30 per 5 seconds' : '$0.06 per second'}
              </Typography>
            </Stack>
          </MenuItem>
        </Select>
      </FormControl>

      <Box>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="body2" sx={{ fontWeight: 600, color: '#0f172a' }}>
            Expression Prompt (Optional)
          </Typography>
          <Tooltip
            title={
              <Box sx={{ p: 0.5 }}>
                <Typography variant="caption" sx={{ display: 'block', fontWeight: 600, mb: 0.5 }}>
                  AI Prompt Optimizer
                </Typography>
                <Typography variant="caption" sx={{ display: 'block', fontSize: '0.7rem' }}>
                  Enhances your expression prompt for better avatar results by improving:
                </Typography>
                <Typography variant="caption" sx={{ display: 'block', fontSize: '0.7rem', mt: 0.5 }}>
                  • Visual clarity & composition
                </Typography>
                <Typography variant="caption" sx={{ display: 'block', fontSize: '0.7rem' }}>
                  • Expression details & style consistency
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
                borderColor: '#3b82f6',
                color: '#3b82f6',
                '&:hover': {
                  borderColor: '#3b82f6',
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
        <TextField
          fullWidth
          multiline
          rows={3}
          placeholder="e.g., 'Confident, friendly smile' or 'Professional, serious expression'"
          value={prompt}
          onChange={e => onPromptChange(e.target.value)}
          helperText="Describe the expression or style you want for your avatar"
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: 2,
              backgroundColor: '#fff',
              '& fieldset': { borderColor: '#e2e8f0' },
            },
          }}
        />
      </Box>

      <TextField
        fullWidth
        type="number"
        label="Seed (Optional)"
        placeholder="Leave empty for random"
        value={seed || ''}
        onChange={e => {
          const value = e.target.value;
          onSeedChange(value ? parseInt(value, 10) : null);
        }}
        helperText="Use the same seed to generate similar results"
        sx={{
          '& .MuiOutlinedInput-root': {
            borderRadius: 2,
            backgroundColor: '#fff',
            '& fieldset': { borderColor: '#e2e8f0' },
          },
        }}
      />
    </Stack>
  );
};
