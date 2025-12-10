/**
 * Scene Card Component
 */

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Stack,
  Chip,
  Box,
  FormControlLabel,
  Switch,
  IconButton,
  TextField,
  Button,
} from '@mui/material';
import { Edit, Check, Close } from '@mui/icons-material';
import { Scene } from '../../../services/youtubeApi';
import { inputSx, labelSx } from '../styles';

interface SceneCardProps {
  scene: Scene;
  isEditing: boolean;
  editedScene: Partial<Scene> | null;
  onToggle: (sceneNumber: number) => void;
  onEdit: (scene: Scene) => void;
  onSave: () => void;
  onCancel: () => void;
  onEditChange: (updates: Partial<Scene>) => void;
  loading: boolean;
}

export const SceneCard: React.FC<SceneCardProps> = React.memo(({
  scene,
  isEditing,
  editedScene,
  onToggle,
  onEdit,
  onSave,
  onCancel,
  onEditChange,
  loading,
}) => {
  const sceneData = isEditing && editedScene ? { ...scene, ...editedScene } : scene;

  return (
    <Card
      variant="outlined"
      sx={{
        opacity: sceneData.enabled === false ? 0.6 : 1,
        border: sceneData.enabled === false ? '1px dashed' : '1px solid',
      }}
    >
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h6" sx={{ mb: 1 }}>
              Scene {scene.scene_number}: {sceneData.title}
            </Typography>
            <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
              {sceneData.emphasis_tags?.map((tag) => (
                <Chip
                  key={tag}
                  label={tag}
                  size="small"
                  color={
                    tag === 'hook' ? 'primary' :
                    tag === 'cta' ? 'secondary' : 'default'
                  }
                />
              ))}
              <Chip
                label={`~${sceneData.duration_estimate}s`}
                size="small"
                variant="outlined"
              />
            </Stack>
          </Box>
          <Box>
            <FormControlLabel
              control={
                <Switch
                  checked={sceneData.enabled !== false}
                  onChange={() => onToggle(scene.scene_number)}
                  size="small"
                />
              }
              label="Enable"
              sx={{ mr: 1 }}
            />
            {!isEditing && (
              <IconButton
                size="small"
                onClick={() => onEdit(scene)}
                color="primary"
              >
                <Edit fontSize="small" />
              </IconButton>
            )}
          </Box>
        </Box>

        {isEditing ? (
          <Stack spacing={2}>
            <TextField
              label="Narration"
              value={sceneData.narration}
              onChange={(e) => onEditChange({ narration: e.target.value })}
              multiline
              rows={3}
              fullWidth
              sx={inputSx}
              InputLabelProps={{ sx: labelSx }}
            />
            <TextField
              label="Visual Prompt"
              value={sceneData.visual_prompt}
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
              value={sceneData.duration_estimate}
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
        ) : (
          <>
            <Typography variant="body2" sx={{ mb: 1, fontStyle: 'italic', color: 'text.secondary' }}>
              "{sceneData.narration}"
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Visual: {sceneData.visual_prompt}
            </Typography>
            {sceneData.visual_cues && sceneData.visual_cues.length > 0 && (
              <Box sx={{ mt: 1 }}>
                <Typography variant="caption" color="text.secondary">
                  Cues: {sceneData.visual_cues.join(', ')}
                </Typography>
              </Box>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
});

SceneCard.displayName = 'SceneCard';

