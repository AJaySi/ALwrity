import React from 'react';
import {
  Stack,
  TextField,
  Button,
  Box,
} from '@mui/material';
import { Check, Close } from '@mui/icons-material';
import { Scene } from '../../../../services/youtubeApi';
import { inputSx, labelSx } from '../../styles';

interface SceneEditFormProps {
  scene: Scene;
  editedScene: Partial<Scene>;
  onEditChange: (updates: Partial<Scene>) => void;
  onSave: () => void;
  onCancel: () => void;
  loading: boolean;
}

export const SceneEditForm: React.FC<SceneEditFormProps> = ({
  scene,
  editedScene,
  onEditChange,
  onSave,
  onCancel,
  loading,
}) => {
  return (
    <Stack spacing={2}>
      <TextField
        label="Narration"
        value={editedScene.narration ?? scene.narration}
        onChange={(e) => onEditChange({ narration: e.target.value })}
        multiline
        rows={3}
        fullWidth
        sx={inputSx}
        InputLabelProps={{ sx: labelSx }}
      />
      <TextField
        label="Visual Prompt"
        value={editedScene.visual_prompt ?? scene.visual_prompt}
        onChange={(e) => onEditChange({ visual_prompt: e.target.value })}
        multiline
        rows={2}
        fullWidth
        sx={inputSx}
        InputLabelProps={{ sx: labelSx }}
      />
      <TextField
        label="Duration (seconds)"
        type="number"
        value={editedScene.duration_estimate ?? scene.duration_estimate}
        onChange={(e) => onEditChange({ duration_estimate: parseFloat(e.target.value) || 5 })}
        inputProps={{ min: 1, max: 10, step: 0.5 }}
        fullWidth
        sx={inputSx}
        InputLabelProps={{ sx: labelSx }}
      />
      <Box sx={{ display: 'flex', gap: 1 }}>
        <Button
          size="small"
          variant="contained"
          startIcon={<Check />}
          onClick={onSave}
          disabled={loading}
        >
          Save
        </Button>
        <Button
          size="small"
          variant="outlined"
          startIcon={<Close />}
          onClick={onCancel}
        >
          Cancel
        </Button>
      </Box>
    </Stack>
  );
};
