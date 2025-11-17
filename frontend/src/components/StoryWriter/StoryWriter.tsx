import React, { useState } from 'react';
import { Box, Container, Typography, useTheme, Dialog, DialogTitle, DialogContent, IconButton } from '@mui/material';
import { useStoryWriterState } from '../../hooks/useStoryWriterState';
import { useStoryWriterPhaseNavigation } from '../../hooks/useStoryWriterPhaseNavigation';
import StorySetup from './Phases/StorySetup';
import StoryOutline from './Phases/StoryOutline';
import StoryWriting from './Phases/StoryWriting';
import StoryExport from './Phases/StoryExport';
import PhaseNavigation from './PhaseNavigation';
import { MultimediaToolbar } from './components/MultimediaToolbar';
import { storyWriterApi } from '../../services/storyWriterApi';
import { triggerSubscriptionError } from '../../api/client';
import CloseIcon from '@mui/icons-material/Close';
import { MultimediaSection } from './components/MultimediaSection';
import StoryWriterLanding from './StoryWriterLanding';

export const StoryWriter: React.FC = () => {
  const theme = useTheme();

  // State management
  const state = useStoryWriterState();

  // Multimedia generation state
  const [isGeneratingAudio, setIsGeneratingAudio] = useState(false);
  const [isGeneratingVideo, setIsGeneratingVideo] = useState(false);
  const [isMultimediaDialogOpen, setIsMultimediaDialogOpen] = useState(false);
  const [landingDismissed, setLandingDismissed] = useState(() => {
    if (typeof window === 'undefined') return false;
    return window.localStorage.getItem('storywriter:landingDismissed') === 'true';
  });

  // Phase navigation
  const {
    phases,
    currentPhase,
    navigateToPhase,
  } = useStoryWriterPhaseNavigation({
    hasPremise: !!state.premise,
    hasOutline: !!state.outline,
    hasStoryContent: !!state.storyContent,
    isComplete: state.isComplete,
  });
  
  // Reset handler
  const handleReset = () => {
    // Reset story state (this also clears localStorage)
    state.resetState();
    if (typeof window !== 'undefined') {
      window.localStorage.removeItem('storywriter:landingDismissed');
    }
    // Simplest approach: reload the page to ensure a clean slate
    if (typeof window !== 'undefined') {
      window.location.reload();
    }
  };

  const handleOpenMultimediaDialog = () => {
    setIsMultimediaDialogOpen(true);
  };

  const handleCloseMultimediaDialog = () => {
    setIsMultimediaDialogOpen(false);
  };

  // Audio generation handler
  const handleGenerateAudio = async () => {
    if (!state.enableNarration) {
      return;
    }
    if (!state.outlineScenes || state.outlineScenes.length === 0) {
      return;
    }

    setIsGeneratingAudio(true);

    try {
      const response = await storyWriterApi.generateSceneAudio({
        scenes: state.outlineScenes,
        provider: state.audioProvider,
        lang: state.audioLang,
        slow: state.audioSlow,
        rate: state.audioRate,
      });

      if (response.success && response.audio_files) {
        const audioMap = new Map<number, string>();
        response.audio_files.forEach((audio) => {
          if (audio.audio_url && !audio.error) {
            audioMap.set(audio.scene_number, audio.audio_url);
          }
        });
        state.setSceneAudio(audioMap);
        state.setError(null);
      }
    } catch (err: any) {
      const status = err?.response?.status;
      if (status === 429 || status === 402) {
        await triggerSubscriptionError(err);
      }
      console.error('Audio generation failed:', err);
    } finally {
      setIsGeneratingAudio(false);
    }
  };

  // Video generation handler
  const handleGenerateVideo = async () => {
    if (!state.enableVideoNarration) {
      return;
    }
    if (!state.outlineScenes || state.outlineScenes.length === 0) {
      return;
    }

    if (!state.sceneImages || state.sceneImages.size === 0) {
      return;
    }

    if (!state.sceneAudio || state.sceneAudio.size === 0) {
      return;
    }

    setIsGeneratingVideo(true);

    try {
      const imageUrls: string[] = [];
      const audioUrls: string[] = [];
      const scenes = state.outlineScenes;

      for (const scene of scenes) {
        const sceneNumber = scene.scene_number || scenes.indexOf(scene) + 1;
        const imageUrl = state.sceneImages?.get(sceneNumber);
        const audioUrl = state.sceneAudio?.get(sceneNumber);

        if (imageUrl && audioUrl) {
          imageUrls.push(imageUrl);
          audioUrls.push(audioUrl);
        }
      }

      if (imageUrls.length !== scenes.length || audioUrls.length !== scenes.length) {
        throw new Error('Number of images and audio files must match number of scenes');
      }

      // Switch to async flow so UI can poll progress messages
      const start = await storyWriterApi.generateStoryVideoAsync({
        scenes: scenes,
        image_urls: imageUrls,
        audio_urls: audioUrls,
        story_title: state.storySetting || 'Story',
        fps: state.videoFps,
        transition_duration: state.videoTransitionDuration,
      });

      // Optional: set a lightweight spinner; export page shows detailed progress
      let done = false;
      while (!done) {
        await new Promise((r) => setTimeout(r, 1200));
        const status = await storyWriterApi.getTaskStatus(start.task_id);
        if (status.status === 'completed') {
          const result = await storyWriterApi.getTaskResult(start.task_id);
          // @ts-ignore: async result includes video dict
          const video = (result as any).video || (result as any)?.result?.video;
          const finalUrl: string | undefined = video?.video_url;
          if (finalUrl) state.setStoryVideo(finalUrl);
          state.setError(null);
          done = true;
        } else if (status.status === 'failed') {
          throw new Error(status.error || 'Video generation failed');
        }
      }
    } catch (err: any) {
      const status = err?.response?.status;
      if (status === 429 || status === 402) {
        await triggerSubscriptionError(err);
      }
      console.error('Video generation failed:', err);
    } finally {
      setIsGeneratingVideo(false);
    }
  };

  const hasStoryProgress = Boolean(state.premise || state.outline || state.storyContent);
  const showLanding = !landingDismissed && !hasStoryProgress;

  const handleLandingStart = () => {
    setLandingDismissed(true);
    if (typeof window !== 'undefined') {
      window.localStorage.setItem('storywriter:landingDismissed', 'true');
    }
    navigateToPhase('setup');
  };

  // Render phase content
  const renderPhaseContent = () => {
    switch (currentPhase) {
      case 'setup':
        return <StorySetup state={state} onNext={() => navigateToPhase('outline')} />;
      case 'outline':
        return <StoryOutline state={state} onNext={() => navigateToPhase('writing')} />;
      case 'writing':
        return <StoryWriting state={state} onNext={() => navigateToPhase('export')} />;
      case 'export':
        return <StoryExport state={state} />;
      default:
        return <StorySetup state={state} onNext={() => navigateToPhase('outline')} />;
    }
  };

  if (showLanding) {
    return (
      <Box
        sx={{
          minHeight: '100vh',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)',
          padding: theme.spacing(4),
        }}
      >
        <Container maxWidth="xl">
          <StoryWriterLanding onStart={handleLandingStart} />
        </Container>
      </Box>
    );
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)',
        padding: theme.spacing(4),
        position: 'relative',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'url("data:image/svg+xml,%3Csvg width="80" height="80" viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="none" fill-rule="evenodd"%3E%3Cg fill="%23ffffff" fill-opacity="0.03"%3E%3Ccircle cx="40" cy="40" r="3"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")',
          pointerEvents: 'none',
        },
        '&::after': {
          content: '""',
          position: 'absolute',
          top: '50%',
          left: '50%',
          width: '600px',
          height: '600px',
          background: 'radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%)',
          transform: 'translate(-50%, -50%)',
          pointerEvents: 'none',
          zIndex: 0,
        },
      }}
    >
      <Container
        maxWidth="xl"
        sx={{
          position: 'relative',
          zIndex: 1,
        }}
      >
        {/* Header with Phase Navigation and Multimedia Toolbar */}
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 2 }}>
            <Box>
              <Typography variant="h3" component="h1" gutterBottom sx={{ color: 'white' }}>
            Story Writer
          </Typography>
              <Typography variant="body1" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
            Create compelling stories with AI assistance
          </Typography>
        </Box>
            {/* Compact Phase Navigation */}
            <Box sx={{ flex: '1 1 auto', minWidth: { xs: '100%', md: '600px' }, display: 'flex', alignItems: 'center', gap: 2 }}>
              <Box sx={{ flex: 1 }}>
        <PhaseNavigation
          phases={phases}
          currentPhase={currentPhase}
          onPhaseClick={navigateToPhase}
          onReset={handleReset}
        />
              </Box>
              {/* Multimedia Toolbar */}
              <MultimediaToolbar
                state={state}
                onGenerateAudio={handleGenerateAudio}
                onGenerateVideo={handleGenerateVideo}
                isGeneratingAudio={isGeneratingAudio}
                isGeneratingVideo={isGeneratingVideo}
                onOpenPanel={(_section) => handleOpenMultimediaDialog()}
              />
            </Box>
          </Box>
        </Box>

        {/* Phase Content */}
        <Box sx={{ mt: 4 }}>
          {renderPhaseContent()}
        </Box>
      </Container>

      <Dialog
        open={isMultimediaDialogOpen}
        onClose={handleCloseMultimediaDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          Multimedia Controls
          <IconButton size="small" onClick={handleCloseMultimediaDialog}>
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent dividers>
          <MultimediaSection state={state} />
        </DialogContent>
      </Dialog>
    </Box>
  );
};

export default StoryWriter;
