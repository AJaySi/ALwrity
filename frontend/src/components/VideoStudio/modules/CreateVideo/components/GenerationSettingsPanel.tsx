import React from 'react';
import {
  Box,
  Paper,
  Stack,
  Typography,
  ToggleButtonGroup,
  ToggleButton,
  Button,
  Alert,
} from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import type { Mode } from '../types';
import { PromptInput } from './PromptInput';
import { VideoSettings } from './VideoSettings';
import { ModelSelector } from './ModelSelector';
import type { Resolution, AspectPreset, MotionPreset, Duration } from '../types';

interface GenerationSettingsPanelProps {
  mode: Mode;
  prompt: string;
  negativePrompt: string;
  duration: Duration;
  resolution: Resolution;
  aspect: AspectPreset;
  motion: MotionPreset;
  audioAttached: boolean;
  costHint: string;
  canGenerate: boolean;
  promptFocused: boolean;
  negativeFocused: boolean;
  promptPlaceholderIndex: number;
  negativePlaceholderIndex: number;
  selectedModel: string;
  onModeChange: (mode: Mode) => void;
  onPromptChange: (value: string) => void;
  onNegativePromptChange: (value: string) => void;
  onDurationChange: (value: Duration) => void;
  onResolutionChange: (value: Resolution) => void;
  onAspectChange: (value: AspectPreset) => void;
  onMotionChange: (value: MotionPreset) => void;
  onModelChange: (modelId: string) => void;
  onFileSelect: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onPromptFocus: () => void;
  onPromptBlur: () => void;
  onNegativeFocus: () => void;
  onNegativeBlur: () => void;
  onPromptPlaceholderChange: (index: number) => void;
  onNegativePlaceholderChange: (index: number) => void;
  onGenerate: () => void;
}

export const GenerationSettingsPanel: React.FC<GenerationSettingsPanelProps> = ({
  mode,
  prompt,
  negativePrompt,
  duration,
  resolution,
  aspect,
  motion,
  costHint,
  canGenerate,
  promptFocused,
  negativeFocused,
  promptPlaceholderIndex,
  negativePlaceholderIndex,
  selectedModel,
  onModeChange,
  onPromptChange,
  onNegativePromptChange,
  onDurationChange,
  onResolutionChange,
  onAspectChange,
  onMotionChange,
  onModelChange,
  onFileSelect,
  onPromptFocus,
  onPromptBlur,
  onNegativeFocus,
  onNegativeBlur,
  onPromptPlaceholderChange,
  onNegativePlaceholderChange,
  onGenerate,
}) => {
  return (
    <Paper
      elevation={0}
      sx={{
        background: 'rgba(248, 250, 252, 0.96)',
        backdropFilter: 'blur(18px)',
        border: '1px solid rgba(148, 163, 184, 0.35)',
        borderRadius: 3,
        p: 3,
        height: '100%',
        color: '#0f172a',
      }}
    >
      <Typography
        variant="h6"
        sx={{
          fontWeight: 700,
          mb: 3,
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          color: '#0f172a',
        }}
      >
        <AutoAwesomeIcon sx={{ color: '#667eea' }} />
        Generation Settings
      </Typography>

      <Stack spacing={3}>
        {/* Mode Toggle */}
        <ToggleButtonGroup
          value={mode}
          exclusive
          onChange={(_, val) => val && onModeChange(val)}
          size="small"
          fullWidth
          sx={{
            background: 'rgba(255,255,255,0.8)',
            borderRadius: 2,
            '& .MuiToggleButton-root': {
              color: '#475569',
              '&.Mui-selected': {
                background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
                color: '#fff',
                fontWeight: 700,
              },
            },
          }}
        >
          <ToggleButton value="t2v">Text to Video</ToggleButton>
          <ToggleButton value="i2v">Image to Video</ToggleButton>
        </ToggleButtonGroup>

        {/* AI Model Selector (only for text-to-video) */}
        {mode === 't2v' && (
          <ModelSelector
            selectedModel={selectedModel}
            onModelChange={onModelChange}
            duration={duration}
            resolution={resolution}
          />
        )}

        {/* Prompt Input */}
        <PromptInput
          prompt={prompt}
          negativePrompt={negativePrompt}
          onPromptChange={onPromptChange}
          onNegativePromptChange={onNegativePromptChange}
          promptFocused={promptFocused}
          negativeFocused={negativeFocused}
          onPromptFocus={onPromptFocus}
          onPromptBlur={onPromptBlur}
          onNegativeFocus={onNegativeFocus}
          onNegativeBlur={onNegativeBlur}
          promptPlaceholderIndex={promptPlaceholderIndex}
          negativePlaceholderIndex={negativePlaceholderIndex}
          onPromptPlaceholderChange={onPromptPlaceholderChange}
          onNegativePlaceholderChange={onNegativePlaceholderChange}
        />

        {/* Image Upload for i2v */}
        {mode === 'i2v' && (
          <Button
            variant="outlined"
            component="label"
            startIcon={<UploadFileIcon />}
            fullWidth
            sx={{
              borderRadius: 2,
              borderColor: '#d2d9ee',
              color: '#0f172a',
              backgroundColor: 'rgba(255, 255, 255, 0.85)',
              '&:hover': {
                borderColor: '#7c3aed',
                background: 'rgba(124, 58, 237, 0.05)',
              },
            }}
          >
            Upload Image
            <input hidden accept="image/*" type="file" onChange={onFileSelect} />
          </Button>
        )}

        {/* Video Settings */}
        <VideoSettings
          resolution={resolution}
          aspect={aspect}
          motion={motion}
          duration={duration}
          onResolutionChange={onResolutionChange}
          onAspectChange={onAspectChange}
          onMotionChange={onMotionChange}
          onDurationChange={onDurationChange}
        />

        {/* Cost Estimate */}
        <Alert
          severity="info"
          icon={<InfoOutlinedIcon />}
          sx={{
            borderRadius: 2,
            background: 'rgba(99, 102, 241, 0.08)',
            color: '#0f172a',
            '& .MuiAlert-icon': { color: '#6366f1' },
          }}
        >
          <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
            Estimated Cost: {costHint}
          </Typography>
          <Typography variant="caption">
            Final cost is confirmed before generation. Lower cost = shorter duration + lower quality.
          </Typography>
        </Alert>

        {/* Generate Button */}
        <Button
          variant="contained"
          size="large"
          startIcon={<PlayArrowIcon />}
          disabled={!canGenerate}
          fullWidth
          onClick={onGenerate}
          sx={{
            py: 2,
            borderRadius: 2,
            background: canGenerate
              ? 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)'
              : '#e2e8f0',
            color: canGenerate ? '#fff' : '#94a3b8',
            fontWeight: 700,
            fontSize: 16,
            textTransform: 'none',
            boxShadow: canGenerate ? '0 8px 24px rgba(102, 126, 234, 0.4)' : 'none',
            '&:hover': {
              background: canGenerate
                ? 'linear-gradient(90deg, #5568d3 0%, #65408b 100%)'
                : '#e2e8f0',
              boxShadow: canGenerate ? '0 12px 32px rgba(102, 126, 234, 0.5)' : 'none',
            },
          }}
        >
          Create Video
        </Button>
      </Stack>
    </Paper>
  );
};
