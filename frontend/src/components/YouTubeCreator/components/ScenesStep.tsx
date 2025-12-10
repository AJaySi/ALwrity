/**
 * Scenes Step Component
 */

import React, { useMemo } from 'react';
import {
  Paper,
  Typography,
  Button,
  Stack,
  Box,
  CircularProgress,
} from '@mui/material';
import { PlayArrow, VideoLibrary } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { VideoPlan, Scene } from '../../../services/youtubeApi';
import { PlanDetails } from './PlanDetails';
import { SceneCard } from './SceneCard';
import { YT_BORDER } from '../constants';

interface ScenesStepProps {
  videoPlan: VideoPlan;
  scenes: Scene[];
  editingSceneId: number | null;
  editedScene: Partial<Scene> | null;
  loading: boolean;
  onBuildScenes: () => void;
  onEditScene: (scene: Scene) => void;
  onSaveScene: () => void;
  onCancelEdit: () => void;
  onEditChange: (updates: Partial<Scene>) => void;
  onToggleScene: (sceneNumber: number) => void;
  onBack: () => void;
  onNext: () => void;
}

export const ScenesStep: React.FC<ScenesStepProps> = React.memo(({
  videoPlan,
  scenes,
  editingSceneId,
  editedScene,
  loading,
  onBuildScenes,
  onEditScene,
  onSaveScene,
  onCancelEdit,
  onEditChange,
  onToggleScene,
  onBack,
  onNext,
}) => {
  const enabledScenesCount = useMemo(
    () => scenes.filter(s => s.enabled !== false).length,
    [scenes]
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <Paper
        sx={{
          p: 4,
          backgroundColor: 'white',
          border: `1px solid ${YT_BORDER}`,
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h5" sx={{ fontWeight: 600 }}>
            2️⃣ Review & Edit Scenes
          </Typography>
          {scenes.length === 0 && (
            <Button
              variant="contained"
              color="error"
              onClick={onBuildScenes}
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : <PlayArrow />}
            >
              {loading ? 'Building Scenes...' : 'Build Scenes from Plan'}
            </Button>
          )}
        </Box>

        <PlanDetails plan={videoPlan} />

        {scenes.length > 0 ? (
          <Stack spacing={2}>
            {scenes.map((scene) => (
              <SceneCard
                key={scene.scene_number}
                scene={scene}
                isEditing={editingSceneId === scene.scene_number}
                editedScene={editedScene}
                onToggle={onToggleScene}
                onEdit={onEditScene}
                onSave={onSaveScene}
                onCancel={onCancelEdit}
                onEditChange={onEditChange}
                loading={loading}
              />
            ))}
          </Stack>
        ) : (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <VideoLibrary sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
              Click "Build Scenes from Plan" to generate scene-by-scene breakdown
            </Typography>
          </Box>
        )}

        {scenes.length > 0 && (
          <Box sx={{ mt: 3, display: 'flex', gap: 2, justifyContent: 'space-between' }}>
            <Button variant="outlined" onClick={onBack}>
              Back to Plan
            </Button>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Typography variant="body2" sx={{ alignSelf: 'center', color: 'text.secondary' }}>
                {enabledScenesCount} of {scenes.length} scenes enabled
              </Typography>
              <Button
                variant="contained"
                color="error"
                onClick={onNext}
                disabled={enabledScenesCount === 0}
              >
                Proceed to Render ({enabledScenesCount} scenes)
              </Button>
            </Box>
          </Box>
        )}
      </Paper>
    </motion.div>
  );
});

ScenesStep.displayName = 'ScenesStep';

