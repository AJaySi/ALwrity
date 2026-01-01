import React from 'react';
import { Box, Stack, Typography, FormControl, InputLabel, Select, MenuItem, TextField, Paper, Chip } from '@mui/material';
import MusicNoteIcon from '@mui/icons-material/MusicNote';
import type { AudioModel } from '../hooks/useAddAudioToVideo';

interface AudioSettingsProps {
  model: AudioModel;
  prompt: string;
  seed: number | null;
  costHint: string;
  onModelChange: (model: AudioModel) => void;
  onPromptChange: (prompt: string) => void;
  onSeedChange: (seed: number | null) => void;
}

export const AudioSettings: React.FC<AudioSettingsProps> = ({
  model,
  prompt,
  seed,
  costHint,
  onModelChange,
  onPromptChange,
  onSeedChange,
}) => {
  return (
    <Paper
      elevation={0}
      sx={{
        p: 3,
        borderRadius: 2,
        border: '1px solid #e2e8f0',
        backgroundColor: '#ffffff',
      }}
    >
      <Stack spacing={3}>
        <Box>
          <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
            <MusicNoteIcon sx={{ color: '#3b82f6' }} />
            <Typography
              variant="subtitle2"
              sx={{
                color: '#0f172a',
                fontWeight: 700,
              }}
            >
              Audio Settings
            </Typography>
          </Stack>
        </Box>

        <Box>
          <Typography
            variant="subtitle2"
            sx={{
              mb: 1,
              color: '#0f172a',
              fontWeight: 600,
            }}
          >
            Audio Model
          </Typography>
          <FormControl fullWidth>
            <Select
              value={model}
              onChange={(e) => onModelChange(e.target.value as AudioModel)}
              sx={{
                backgroundColor: '#fff',
                '& .MuiOutlinedInput-notchedOutline': {
                  borderColor: '#e2e8f0',
                },
              }}
            >
              <MenuItem value="hunyuan-video-foley">Hunyuan Video Foley ($0.02/s)</MenuItem>
              <MenuItem value="think-sound">Think Sound ($0.05/video)</MenuItem>
            </Select>
          </FormControl>
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            {model === 'hunyuan-video-foley' 
              ? 'Tencent Hunyuan\'s video-to-audio model: Multi-scene synchronization, 48 kHz hi-fi output, SOTA performance'
              : model === 'think-sound'
              ? 'Context-aware video-to-audio generation: Analyzes visual elements to generate matching audio. Features built-in Prompt Enhancer for AI-assisted optimization.'
              : 'Generate audio from video'}
          </Typography>
        </Box>

        <Box>
          <Typography
            variant="subtitle2"
            sx={{
              mb: 1,
              color: '#0f172a',
              fontWeight: 600,
            }}
          >
            Audio Prompt (Optional)
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={3}
            value={prompt}
            onChange={(e) => onPromptChange(e.target.value)}
            placeholder={
              model === 'hunyuan-video-foley'
                ? "Briefly describe the mood or key sounds (e.g., 'Rainy street ambience, soft footsteps, distant cars' or 'Kitchen ASMR: chopping vegetables, sizzling pan')"
                : "Describe the type of sound you want (e.g., 'engine roaring', 'footsteps on gravel', 'ocean waves crashing'). The built-in Prompt Enhancer will optimize your prompt for better results."
            }
            sx={{
              backgroundColor: '#fff',
              '& .MuiOutlinedInput-notchedOutline': {
                borderColor: '#e2e8f0',
              },
            }}
          />
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            {model === 'hunyuan-video-foley'
              ? 'Optional: Leave empty to let AI automatically generate appropriate sounds based on visual cues'
              : 'Optional: Add text descriptions to guide the style and type of audio generated. The built-in Prompt Enhancer will optimize your prompt for better results. Use clear, descriptive prompts for best quality.'}
          </Typography>
        </Box>

        <Box>
          <Typography
            variant="subtitle2"
            sx={{
              mb: 1,
              color: '#0f172a',
              fontWeight: 600,
            }}
          >
            Seed (Optional)
          </Typography>
          <TextField
            fullWidth
            type="number"
            value={seed === null ? '' : seed}
            onChange={(e) => {
              const value = e.target.value;
              onSeedChange(value === '' ? null : parseInt(value, 10));
            }}
            placeholder="-1 for random"
            sx={{
              backgroundColor: '#fff',
              '& .MuiOutlinedInput-notchedOutline': {
                borderColor: '#e2e8f0',
              },
            }}
          />
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            Use -1 for random seed, or specify a number for reproducible results. Fix the seed when iterating to compare different prompt variations.
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
          <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
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
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
            {model === 'think-sound'
              ? 'Pricing: $0.05 per video (flat rate)'
              : 'Pricing: $0.02/second (estimated)'}
          </Typography>
          {model === 'hunyuan-video-foley' && (
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
              Minimum charge: 5 seconds | Maximum: 10 minutes (600 seconds)
            </Typography>
          )}
        </Box>
      </Stack>
    </Paper>
  );
};
