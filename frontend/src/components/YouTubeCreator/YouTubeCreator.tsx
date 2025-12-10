/**
 * YouTube Creator Studio Component
 * 
 * AI-first YouTube video creation tool with persona integration.
 * Three-phase workflow: Plan → Scenes → Render
 */

import React, { useState, useMemo, useCallback } from 'react';
import {
  Box,
  Container,
  Typography,
  Stepper,
  Step,
  StepLabel,
  Paper,
  Button,
  Alert,
} from '@mui/material';
import { ArrowBack } from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { youtubeApi, type VideoPlan, type Scene } from '../../services/youtubeApi';
import { STEPS, YT_RED, YT_BG, YT_BORDER, YT_TEXT, type Resolution, type DurationType } from './constants';
import { PlanStep } from './components/PlanStep';
import { ScenesStep } from './components/ScenesStep';
import { RenderStep } from './components/RenderStep';
import { useRenderPolling } from './hooks/useRenderPolling';
import { useCostEstimate } from './hooks/useCostEstimate';
import HeaderControls from '../shared/HeaderControls';

const YouTubeCreator: React.FC = () => {
  const navigate = useNavigate();
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Step 1: Plan
  const [userIdea, setUserIdea] = useState('');
  const [durationType, setDurationType] = useState<DurationType>('medium');
  const [referenceImage, setReferenceImage] = useState('');
  const [videoPlan, setVideoPlan] = useState<VideoPlan | null>(null);

  // Step 2: Scenes
  const [scenes, setScenes] = useState<Scene[]>([]);
  const [editingSceneId, setEditingSceneId] = useState<number | null>(null);
  const [editedScene, setEditedScene] = useState<Partial<Scene> | null>(null);

  // Step 3: Render
  const [renderTaskId, setRenderTaskId] = useState<string | null>(null);
  const [renderStatus, setRenderStatus] = useState<any>(null);
  const [renderProgress, setRenderProgress] = useState(0);
  const [resolution, setResolution] = useState<Resolution>('720p');
  const [combineScenes, setCombineScenes] = useState(true);

  // Custom hooks
  const { renderStatus: polledStatus, renderProgress: polledProgress, error: pollingError } = useRenderPolling(
    renderTaskId,
    () => setSuccess('Video rendered successfully!'),
    (err) => setError(err)
  );

  // Update local state from polling hook
  React.useEffect(() => {
    if (polledStatus) {
      setRenderStatus(polledStatus);
    }
    if (polledProgress !== undefined) {
      setRenderProgress(polledProgress);
    }
    if (pollingError) {
      setError(pollingError);
    }
  }, [polledStatus, polledProgress, pollingError]);

  const { costEstimate, loadingCostEstimate } = useCostEstimate({
    activeStep,
    scenes,
    resolution,
    renderTaskId,
  });

  // Memoized computed values
  const enabledScenesCount = useMemo(
    () => scenes.filter(s => s.enabled !== false).length,
    [scenes]
  );

  // Handlers
  const handleGeneratePlan = useCallback(async () => {
    if (!userIdea.trim()) {
      setError('Please enter your video idea');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await youtubeApi.createPlan({
        user_idea: userIdea,
        duration_type: durationType,
        reference_image_description: referenceImage || undefined,
      });

      if (response.success && response.plan) {
        setVideoPlan(response.plan);
        setSuccess('Video plan generated successfully!');
        setTimeout(() => {
          setActiveStep(1);
          setSuccess(null);
        }, 1000);
      } else {
        setError(response.message || 'Failed to generate plan');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to generate video plan');
    } finally {
      setLoading(false);
    }
  }, [userIdea, durationType, referenceImage]);

  const handleBuildScenes = useCallback(async () => {
    if (!videoPlan) {
      setError('Please generate a plan first');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await youtubeApi.buildScenes(videoPlan);

      if (response.success && response.scenes) {
        setScenes(response.scenes.map(s => ({ ...s, enabled: s.enabled !== false })));
        setSuccess(`Built ${response.scenes.length} scenes successfully!`);
        setTimeout(() => {
          setActiveStep(2);
          setSuccess(null);
        }, 1000);
      } else {
        setError(response.message || 'Failed to build scenes');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to build scenes');
    } finally {
      setLoading(false);
    }
  }, [videoPlan]);

  const handleEditScene = useCallback((scene: Scene) => {
    setEditingSceneId(scene.scene_number);
    setEditedScene({
      narration: scene.narration,
      visual_prompt: scene.visual_prompt,
      duration_estimate: scene.duration_estimate,
      enabled: scene.enabled !== false,
    });
  }, []);

  const handleSaveScene = useCallback(async () => {
    if (!editingSceneId || !editedScene) return;

    setLoading(true);
    setError(null);

    try {
      const response = await youtubeApi.updateScene(editingSceneId, {
        narration: editedScene.narration,
        visual_description: editedScene.visual_prompt,
        duration_estimate: editedScene.duration_estimate,
        enabled: editedScene.enabled,
      });

      if (response.success && response.scene) {
        setScenes(scenes.map(s =>
          s.scene_number === editingSceneId ? { ...s, ...response.scene } : s
        ));
        setEditingSceneId(null);
        setEditedScene(null);
        setSuccess('Scene updated successfully!');
      } else {
        setError(response.message || 'Failed to update scene');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to update scene');
    } finally {
      setLoading(false);
    }
  }, [editingSceneId, editedScene, scenes]);

  const handleCancelEdit = useCallback(() => {
    setEditingSceneId(null);
    setEditedScene(null);
  }, []);

  const handleToggleScene = useCallback((sceneNumber: number) => {
    setScenes(scenes.map(s =>
      s.scene_number === sceneNumber ? { ...s, enabled: !s.enabled } : s
    ));
  }, [scenes]);

  const handleStartRender = useCallback(async () => {
    if (scenes.length === 0) {
      setError('Please build scenes first');
      return;
    }

    const enabledScenes = scenes.filter(s => s.enabled !== false);
    if (enabledScenes.length === 0) {
      setError('Please enable at least one scene to render');
      return;
    }

    if (!videoPlan) {
      setError('Video plan is missing');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await youtubeApi.startRender({
        scenes: enabledScenes,
        video_plan: videoPlan,
        resolution,
        combine_scenes: combineScenes,
      });

      if (response.success && response.task_id) {
        setRenderTaskId(response.task_id);
        setRenderProgress(0);
        setSuccess('Video rendering started!');
      } else {
        setError(response.message || 'Failed to start render');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to start render');
    } finally {
      setLoading(false);
    }
  }, [scenes, videoPlan, resolution, combineScenes]);

  const getVideoUrl = useCallback(() => {
    if (renderStatus?.result?.final_video_url) {
      return renderStatus.result.final_video_url;
    }
    if (renderStatus?.result?.scene_results?.[0]?.video_url) {
      return renderStatus.result.scene_results[0].video_url;
    }
    return null;
  }, [renderStatus]);

  const handleStepNavigation = useCallback((targetStep: number) => {
    if (targetStep === activeStep) return;

    // Always allow going back
    if (targetStep < activeStep) {
      setActiveStep(targetStep);
      return;
    }

    // Forward navigation with guards
    if (targetStep === 1) {
      if (!videoPlan) {
        setError('Please generate a plan first.');
        return;
      }
      setActiveStep(1);
      return;
    }

    if (targetStep === 2) {
      if (!videoPlan) {
        setError('Please generate a plan first.');
        return;
      }
      if (scenes.length === 0) {
        setError('Please build scenes before rendering.');
        return;
      }
      if (enabledScenesCount === 0) {
        setError('Enable at least one scene to render.');
        return;
      }
      setActiveStep(2);
      return;
    }
  }, [activeStep, videoPlan, scenes.length, enabledScenesCount]);

  const handleResetRender = useCallback(() => {
    setRenderTaskId(null);
    setRenderStatus(null);
    setRenderProgress(0);
    setError(null);
  }, []);

  const handleRetryFailedScenes = useCallback((failedScenes: any[]) => {
    if (failedScenes.length > 0) {
      const sceneNumbers = failedScenes.map((f: any) => f.scene_number);
      const updatedScenes = scenes.map(s =>
        sceneNumbers.includes(s.scene_number)
          ? { ...s, enabled: true }
          : s
      );
      setScenes(updatedScenes);
      handleResetRender();
    }
  }, [scenes, handleResetRender]);

  return (
    <Container
      maxWidth="lg"
      sx={{
        py: 4,
        backgroundColor: YT_BG,
        color: YT_TEXT,
        minHeight: '100vh',
        borderRadius: 2,
        border: `1px solid ${YT_BORDER}`,
        boxShadow: '0 8px 24px rgba(0,0,0,0.06)',
      }}
    >
      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', gap: 2 }}>
        <Button
          startIcon={<ArrowBack />}
          onClick={() => navigate('/dashboard')}
          variant="outlined"
          sx={{ borderColor: YT_BORDER, color: YT_TEXT, backgroundColor: 'white' }}
        >
          Back to Dashboard
        </Button>
        <Typography variant="h4" sx={{ flexGrow: 1, fontWeight: 700 }}>
          🎥 YouTube Creator Studio
        </Typography>
        <HeaderControls colorMode="light" showAlerts={true} showUser={true} />
      </Box>

      {/* Stepper */}
      <Paper
        sx={{
          p: 3,
          mb: 4,
          backgroundColor: 'white',
          border: `1px solid ${YT_BORDER}`,
        }}
      >
        <Stepper
          activeStep={activeStep}
          sx={{
            '& .MuiStepIcon-root.Mui-active': { color: YT_RED },
            '& .MuiStepIcon-root.Mui-completed': { color: YT_RED },
          }}
        >
          {STEPS.map((label, idx) => (
            <Step key={label} completed={idx < activeStep}>
              <StepLabel
                onClick={() => handleStepNavigation(idx)}
                sx={{ cursor: 'pointer', userSelect: 'none' }}
              >
                {label}
              </StepLabel>
            </Step>
          ))}
        </Stepper>
      </Paper>

      {/* Success Alert */}
      <AnimatePresence>
        {success && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccess(null)}>
              {success}
            </Alert>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Step Components */}
      {activeStep === 0 && (
        <PlanStep
          userIdea={userIdea}
          durationType={durationType}
          referenceImage={referenceImage}
          loading={loading}
          onIdeaChange={setUserIdea}
          onDurationChange={setDurationType}
          onReferenceImageChange={setReferenceImage}
          onGeneratePlan={handleGeneratePlan}
        />
      )}

      {activeStep === 1 && videoPlan && (
        <ScenesStep
          videoPlan={videoPlan}
          scenes={scenes}
          editingSceneId={editingSceneId}
          editedScene={editedScene}
          loading={loading}
          onBuildScenes={handleBuildScenes}
          onEditScene={handleEditScene}
          onSaveScene={handleSaveScene}
          onCancelEdit={handleCancelEdit}
          onEditChange={setEditedScene}
          onToggleScene={handleToggleScene}
          onBack={() => setActiveStep(0)}
          onNext={() => setActiveStep(2)}
        />
      )}

      {activeStep === 2 && (
        <RenderStep
          renderTaskId={renderTaskId}
          renderStatus={renderStatus}
          renderProgress={renderProgress}
          resolution={resolution}
          combineScenes={combineScenes}
          enabledScenesCount={enabledScenesCount}
          costEstimate={costEstimate}
          loadingCostEstimate={loadingCostEstimate}
          loading={loading}
          onResolutionChange={setResolution}
          onCombineScenesChange={setCombineScenes}
          onStartRender={handleStartRender}
          onBack={() => setActiveStep(1)}
          onReset={handleResetRender}
          onRetryFailedScenes={handleRetryFailedScenes}
          getVideoUrl={getVideoUrl}
        />
      )}
    </Container>
  );
};

export default YouTubeCreator;
