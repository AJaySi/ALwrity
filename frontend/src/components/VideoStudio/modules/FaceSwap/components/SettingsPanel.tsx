import React from 'react';
import { Box, Typography, TextField, FormControl, InputLabel, Select, MenuItem, Paper, Stack } from '@mui/material';
import { Resolution, FaceSwapModel, TargetGender } from '../hooks/useFaceSwap';

interface SettingsPanelProps {
  model: FaceSwapModel;
  prompt: string;
  resolution: Resolution;
  seed: number | null;
  targetGender: TargetGender;
  targetIndex: number;
  onPromptChange: (value: string) => void;
  onResolutionChange: (value: Resolution) => void;
  onSeedChange: (value: number | null) => void;
  onTargetGenderChange: (value: TargetGender) => void;
  onTargetIndexChange: (value: number) => void;
}

export const SettingsPanel: React.FC<SettingsPanelProps> = ({
  model,
  prompt,
  resolution,
  seed,
  targetGender,
  targetIndex,
  onPromptChange,
  onResolutionChange,
  onSeedChange,
  onTargetGenderChange,
  onTargetIndexChange,
}) => {
  if (model === 'mocha') {
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
        <Typography
          variant="subtitle2"
          sx={{
            mb: 2,
            color: '#0f172a',
            fontWeight: 700,
          }}
        >
          MoCha Settings
        </Typography>
        <Stack spacing={2}>
          <TextField
            label="Prompt (Optional)"
            placeholder="e.g., preserve outfit; natural expressions; no background changes"
            value={prompt}
            onChange={(e) => onPromptChange(e.target.value)}
            multiline
            rows={3}
            fullWidth
            helperText="Optional prompt to guide the character replacement"
          />

          <FormControl fullWidth>
            <InputLabel>Resolution</InputLabel>
            <Select
              value={resolution}
              label="Resolution"
              onChange={(e) => onResolutionChange(e.target.value as Resolution)}
            >
              <MenuItem value="480p">480p ($0.04/second)</MenuItem>
              <MenuItem value="720p">720p ($0.08/second)</MenuItem>
            </Select>
          </FormControl>

          <TextField
            label="Seed (Optional)"
            type="number"
            value={seed || ''}
            onChange={(e) => {
              const value = e.target.value;
              onSeedChange(value === '' ? null : parseInt(value, 10));
            }}
            fullWidth
            helperText="Random seed for reproducibility (-1 for random, leave empty for random)"
            inputProps={{ min: -1 }}
          />
        </Stack>
      </Paper>
    );
  }

  // video-face-swap settings
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
      <Typography
        variant="subtitle2"
        sx={{
          mb: 2,
          color: '#0f172a',
          fontWeight: 700,
        }}
      >
        Video Face Swap Settings
      </Typography>
      <Stack spacing={2}>
        <FormControl fullWidth>
          <InputLabel>Target Gender</InputLabel>
          <Select
            value={targetGender}
            label="Target Gender"
            onChange={(e) => onTargetGenderChange(e.target.value as TargetGender)}
          >
            <MenuItem value="all">All (no filter)</MenuItem>
            <MenuItem value="female">Female only</MenuItem>
            <MenuItem value="male">Male only</MenuItem>
          </Select>
        </FormControl>

        <TextField
          label="Target Face Index"
          type="number"
          value={targetIndex}
          onChange={(e) => {
            const value = parseInt(e.target.value, 10);
            if (!isNaN(value) && value >= 0 && value <= 10) {
              onTargetIndexChange(value);
            }
          }}
          fullWidth
          helperText="0 = largest face, 1 = second largest, etc. (0-10)"
          inputProps={{ min: 0, max: 10 }}
        />
      </Stack>
    </Paper>
  );
};
