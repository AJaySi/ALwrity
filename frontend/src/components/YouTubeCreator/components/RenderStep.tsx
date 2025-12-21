/**
 * Render Step Component
 * 
 * Main component for the render step in YouTube Creator workflow.
 * Orchestrates scene overview, settings, cost estimation, and render status.
 */

import React from 'react';
import {
  Paper,
  Typography,
  Stack,
  Button,
  Box,
  Alert,
  CircularProgress,
} from '@mui/material';
import { PlayArrow } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { TaskStatus, CostEstimate, VideoPlan, Scene } from '../../../services/youtubeApi';
import { YT_BORDER, type Resolution } from '../constants';
import { SceneCard } from './SceneCard';
import { CombinedSceneOverview } from './CombinedSceneOverview';
import { CostEstimateCard } from './CostEstimateCard';
import { RenderSettings } from './RenderSettings';
import { RenderStatusDisplay } from './RenderStatusDisplay';

interface RenderStepProps {
  renderTaskId: string | null;
  renderStatus: TaskStatus | null;
  renderProgress: number;
  resolution: Resolution;
  combineScenes: boolean;
  enabledScenesCount: number;
  costEstimate: CostEstimate | null;
  loadingCostEstimate: boolean;
  loading: boolean;
  scenes: Scene[];
  videoPlan: VideoPlan | null;
  editingSceneId: number | null;
  editedScene: Partial<Scene> | null;
  onResolutionChange: (resolution: Resolution) => void;
  onCombineScenesChange: (combine: boolean) => void;
  onStartRender: () => void;
  onBack: () => void;
  onReset: () => void;
  onRetryFailedScenes: (failedScenes: any[]) => void;
  onEditScene: (scene: Scene) => void;
  onSaveScene: () => void;
  onCancelEdit: () => void;
  onEditChange: (updates: Partial<Scene>) => void;
  onToggleScene: (sceneNumber: number) => void;
  getVideoUrl: () => string | null;
}

export const RenderStep: React.FC<RenderStepProps> = React.memo(({
  renderTaskId,
  renderStatus,
  renderProgress,
  resolution,
  combineScenes,
  enabledScenesCount,
  costEstimate,
  loadingCostEstimate,
  loading,
  scenes,
  editingSceneId,
  editedScene,
  onResolutionChange,
  onCombineScenesChange,
  onStartRender,
  onBack,
  onReset,
  onRetryFailedScenes,
  onEditScene,
  onSaveScene,
  onCancelEdit,
  onEditChange,
  onToggleScene,
  getVideoUrl,
}) => {
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
        <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
          3️⃣ Render Video
        </Typography>

        {!renderTaskId ? (
          <Stack spacing={3}>
            <Alert severity="info">
              Review your scenes, configure render settings, and start generating your video. This may take several minutes.
            </Alert>

            {/* Combined Scene Statistics & Timeline */}
            {scenes.length > 0 && (
              <CombinedSceneOverview scenes={scenes} />
            )}

            {/* Scene Details - Full descriptions */}
            {scenes.length > 0 && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, color: '#111827' }}>
                  Scene Details
                </Typography>
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
              </Box>
            )}

            {/* Render Settings */}
            <RenderSettings
              resolution={resolution}
              combineScenes={combineScenes}
              enabledScenesCount={enabledScenesCount}
              onResolutionChange={onResolutionChange}
              onCombineScenesChange={onCombineScenesChange}
            />

            {/* Render Summary and Cost Estimate */}
            <Box sx={{ p: 2, bgcolor: '#f4f4f4', borderRadius: 1, border: `1px solid ${YT_BORDER}` }}>
              <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                Render Summary
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                • {enabledScenesCount} scenes will be rendered
                <br />
                • Resolution: {resolution}
                <br />
                • {combineScenes ? 'Scenes will be combined into one video' : 'Each scene will be a separate video'}
                <br />
              </Typography>

              <CostEstimateCard
                costEstimate={costEstimate}
                loadingCostEstimate={loadingCostEstimate}
              />
            </Box>

            {/* Action Buttons */}
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button variant="outlined" onClick={onBack}>
                Back to Scenes
              </Button>
              <Button
                variant="contained"
                color="error"
                size="large"
                onClick={onStartRender}
                disabled={loading || enabledScenesCount === 0}
                startIcon={loading ? <CircularProgress size={20} /> : <PlayArrow />}
                sx={{ px: 4 }}
              >
                {loading ? 'Starting Render...' : 'Start Video Render'}
              </Button>
            </Box>
          </Stack>
        ) : (
          <RenderStatusDisplay
            renderStatus={renderStatus}
            renderProgress={renderProgress}
            getVideoUrl={getVideoUrl}
            onReset={onReset}
            onRetryFailedScenes={onRetryFailedScenes}
          />
        )}
      </Paper>
    </motion.div>
  );
});

RenderStep.displayName = 'RenderStep';
