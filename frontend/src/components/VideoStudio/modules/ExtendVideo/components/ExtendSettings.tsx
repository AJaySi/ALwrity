import React, { useState } from 'react';
import { Box, Stack, Typography, FormControl, InputLabel, Select, MenuItem, TextField, FormControlLabel, Switch, Chip, Button, CircularProgress, Tooltip, Paper } from '@mui/material';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import type { ExtendResolution, ExtendModel } from '../hooks/useExtendVideo';
import { optimizePrompt } from '../../../../../api/videoStudioApi';

interface ExtendSettingsProps {
  model: ExtendModel;
  prompt: string;
  negativePrompt: string;
  resolution: ExtendResolution;
  duration: number;
  enablePromptExpansion: boolean;
  generateAudio: boolean;
  cameraFixed: boolean;
  seed: number | null;
  costHint: string;
  onModelChange: (model: ExtendModel) => void;
  onPromptChange: (value: string) => void;
  onNegativePromptChange: (value: string) => void;
  onResolutionChange: (resolution: ExtendResolution) => void;
  onDurationChange: (duration: number) => void;
  onEnablePromptExpansionChange: (enabled: boolean) => void;
  onGenerateAudioChange: (enabled: boolean) => void;
  onCameraFixedChange: (enabled: boolean) => void;
  onSeedChange: (seed: number | null) => void;
}

export const ExtendSettings: React.FC<ExtendSettingsProps> = ({
  model,
  prompt,
  negativePrompt,
  resolution,
  duration,
  enablePromptExpansion,
  generateAudio,
  cameraFixed,
  seed,
  costHint,
  onModelChange,
  onPromptChange,
  onNegativePromptChange,
  onResolutionChange,
  onDurationChange,
  onEnablePromptExpansionChange,
  onGenerateAudioChange,
  onCameraFixedChange,
  onSeedChange,
}) => {
  const [enhancing, setEnhancing] = useState(false);

  const handleEnhancePrompt = async () => {
    if (!prompt.trim() || enhancing) return;

    setEnhancing(true);
    try {
      const result = await optimizePrompt({
        text: prompt,
        mode: 'video',
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

  // Model-specific options
  const isWan22Spicy = model === 'wan-2.2-spicy';
  const isSeedance = model === 'seedance-1.5-pro';
  const isWan25 = model === 'wan-2.5';
  
  const availableResolutions: ExtendResolution[] = (isWan22Spicy || isSeedance)
    ? ['480p', '720p'] 
    : ['480p', '720p', '1080p'];
  
  const availableDurations = isWan22Spicy
    ? [5, 8]
    : isSeedance
    ? [4, 5, 6, 7, 8, 9, 10, 11, 12]
    : [3, 4, 5, 6, 7, 8, 9, 10];

  return (
    <Stack spacing={3}>
      <Box>
        <Typography
          variant="subtitle2"
          sx={{
            mb: 1,
            color: '#0f172a',
            fontWeight: 700,
          }}
        >
          AI Model
        </Typography>
        <FormControl fullWidth>
          <Select
            value={model}
            onChange={(e) => onModelChange(e.target.value as ExtendModel)}
            sx={{
              backgroundColor: '#fff',
              '& .MuiOutlinedInput-notchedOutline': {
                borderColor: '#e2e8f0',
              },
            }}
          >
            <MenuItem value="wan-2.5">WAN 2.5 (Full Featured)</MenuItem>
            <MenuItem value="wan-2.2-spicy">WAN 2.2 Spicy (Fast & Affordable)</MenuItem>
            <MenuItem value="seedance-1.5-pro">Seedance 1.5 Pro (Advanced)</MenuItem>
          </Select>
        </FormControl>
        <Paper
          elevation={0}
          sx={{
            mt: 1,
            p: 1.5,
            backgroundColor: isWan22Spicy ? '#fef3c7' : isSeedance ? '#f3e8ff' : '#eff6ff',
            borderRadius: 1,
          }}
        >
          <Typography variant="caption" sx={{ display: 'block', fontWeight: 600, color: '#0f172a', mb: 0.5 }}>
            {isWan22Spicy ? 'WAN 2.2 Spicy' : isSeedance ? 'Seedance 1.5 Pro' : 'WAN 2.5'}
          </Typography>
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
            {isWan22Spicy 
              ? 'Fast and affordable: 480p/720p, 5 or 8 seconds. $0.03-0.06/s pricing. Perfect for quick extensions with expressive visuals.'
              : isSeedance
              ? `Advanced features: 480p/720p, 4-12 seconds, auto audio generation, camera control. ${generateAudio ? '$0.024-0.052' : '$0.012-0.026'}/s pricing. Ideal for ad creatives and short dramas.`
              : 'Full featured: 480p/720p/1080p, 3-10 seconds, audio upload, negative prompts, and prompt expansion. $0.05-0.15/s pricing.'}
          </Typography>
        </Paper>
      </Box>

      <Box>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
          <Typography
            variant="subtitle2"
            sx={{
              color: '#0f172a',
              fontWeight: 700,
            }}
          >
            Extension Prompt *
          </Typography>
          <Tooltip title="AI will optimize your prompt for better video extension results, improving visual clarity, composition, and motion continuity.">
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
          rows={4}
          placeholder="Describe how you want to extend the video. For example: 'Continue the motion smoothly', 'Add a zoom out effect', 'Extend the scene with the character walking forward'"
          value={prompt}
          onChange={e => onPromptChange(e.target.value)}
          required
          sx={{
            '& .MuiOutlinedInput-root': {
              backgroundColor: '#fff',
              '& fieldset': { borderColor: '#e2e8f0' },
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
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
          Describe the motion, scene, or effect you want for the extended portion. Supports Chinese and English prompts.
        </Typography>
      </Box>

      {isWan25 && (
        <Box>
          <Typography
            variant="subtitle2"
            sx={{
              mb: 1,
              color: '#0f172a',
              fontWeight: 700,
            }}
          >
            Negative Prompt (Optional)
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={2}
            placeholder="What to avoid in the extended video..."
            value={negativePrompt}
            onChange={e => onNegativePromptChange(e.target.value)}
            sx={{
              '& .MuiOutlinedInput-root': {
                backgroundColor: '#fff',
                '& fieldset': { borderColor: '#e2e8f0' },
              },
            }}
          />
        </Box>
      )}

      {isSeedance && (
        <>
          <Box>
            <FormControlLabel
              control={
                <Switch
                  checked={generateAudio}
                  onChange={(e) => onGenerateAudioChange(e.target.checked)}
                  color="primary"
                />
              }
              label="Generate Audio"
            />
            <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
              Automatically generate audio for the extended video
              {generateAudio 
                ? ' (Adds ~$0.012-0.026/s to cost)'
                : ' (Saves ~$0.012-0.026/s)'}
            </Typography>
          </Box>

          <Box>
            <FormControlLabel
              control={
                <Switch
                  checked={cameraFixed}
                  onChange={(e) => onCameraFixedChange(e.target.checked)}
                  color="primary"
                />
              }
              label="Fix Camera Position"
            />
            <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
              Keep camera position fixed for stable shots
            </Typography>
          </Box>
        </>
      )}

      <Box>
        <Typography
          variant="subtitle2"
          sx={{
            mb: 1,
            color: '#0f172a',
            fontWeight: 700,
          }}
        >
          Resolution
        </Typography>
        <FormControl fullWidth>
          <Select
            value={resolution}
            onChange={(e) => onResolutionChange(e.target.value as ExtendResolution)}
            sx={{
              backgroundColor: '#fff',
              '& .MuiOutlinedInput-notchedOutline': {
                borderColor: '#e2e8f0',
              },
            }}
          >
            {availableResolutions.map((res) => {
              // Model-specific pricing
              let price: string;
              if (isWan22Spicy) {
                price = res === '480p' ? '$0.03' : '$0.06';
              } else if (isSeedance) {
                // Seedance pricing varies by audio generation
                if (generateAudio) {
                  price = res === '480p' ? '$0.024' : '$0.052';
                } else {
                  price = res === '480p' ? '$0.012' : '$0.026';
                }
              } else {
                price = res === '480p' ? '$0.05' : res === '720p' ? '$0.10' : '$0.15';
              }
              return (
                <MenuItem key={res} value={res}>
                  {res} ({price}/s)
                </MenuItem>
              );
            })}
          </Select>
        </FormControl>
      </Box>

      <Box>
        <Typography
          variant="subtitle2"
          sx={{
            mb: 1,
            color: '#0f172a',
            fontWeight: 700,
          }}
        >
          Extension Duration
        </Typography>
        <FormControl fullWidth>
          <Select
            value={duration}
            onChange={(e) => onDurationChange(Number(e.target.value))}
            sx={{
              backgroundColor: '#fff',
              '& .MuiOutlinedInput-notchedOutline': {
                borderColor: '#e2e8f0',
              },
            }}
          >
            {availableDurations.map((d) => (
              <MenuItem key={d} value={d}>
                {d} seconds
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
          How long should the extended portion be?
        </Typography>
      </Box>

      {isWan25 && (
        <Box>
          <FormControlLabel
            control={
              <Switch
                checked={enablePromptExpansion}
                onChange={(e) => onEnablePromptExpansionChange(e.target.checked)}
                color="primary"
              />
            }
            label="Enable Prompt Expansion"
          />
          <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
            Automatically enhance your prompt for better results
          </Typography>
        </Box>
      )}

      <Box>
        <Typography
          variant="subtitle2"
          sx={{
            mb: 1,
            color: '#0f172a',
            fontWeight: 700,
          }}
        >
          Seed (Optional)
        </Typography>
        <TextField
          fullWidth
          type="number"
          placeholder="Leave empty for random"
          value={seed ?? ''}
          onChange={(e) => {
            const value = e.target.value;
            onSeedChange(value === '' ? null : Number(value));
          }}
          sx={{
            backgroundColor: '#fff',
            '& .MuiOutlinedInput-root': {
              '& fieldset': { borderColor: '#e2e8f0' },
            },
          }}
        />
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
          Use the same seed to reproduce similar results
        </Typography>
      </Box>

      <Box
        sx={{
          p: 2,
          borderRadius: 2,
          backgroundColor: '#f1f5f9',
          border: '1px solid #e2e8f0',
        }}
      >
        <Stack direction="row" spacing={1} alignItems="center">
          <Typography variant="body2" sx={{ fontWeight: 600, color: '#0f172a' }}>
            Estimated Cost:
          </Typography>
          <Chip
            label={costHint}
            size="small"
            sx={{
              backgroundColor: '#3b82f6',
              color: '#fff',
              fontWeight: 600,
            }}
          />
        </Stack>
      </Box>
    </Stack>
  );
};
