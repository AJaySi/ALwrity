import React from 'react';
import { Box, Container, Typography, useTheme } from '@mui/material';
import { useStoryWriterState } from '../../hooks/useStoryWriterState';
import { useStoryWriterPhaseNavigation } from '../../hooks/useStoryWriterPhaseNavigation';
import StorySetup from './Phases/StorySetup';
import StoryOutline from './Phases/StoryOutline';
import StoryWriting from './Phases/StoryWriting';
import StoryExport from './Phases/StoryExport';
import PhaseNavigation from './PhaseNavigation';

export const StoryWriter: React.FC = () => {
  const theme = useTheme();

  // State management
  const state = useStoryWriterState();

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
    // Simplest approach: reload the page to ensure a clean slate
    if (typeof window !== 'undefined') {
      window.location.reload();
    }
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
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h3" component="h1" gutterBottom>
            Story Writer
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Create compelling stories with AI assistance
          </Typography>
        </Box>

        {/* Phase Navigation */}
        <PhaseNavigation
          phases={phases}
          currentPhase={currentPhase}
          onPhaseClick={navigateToPhase}
          onReset={handleReset}
        />

        {/* Phase Content */}
        <Box sx={{ mt: 4 }}>
          {renderPhaseContent()}
        </Box>
      </Container>
    </Box>
  );
};

export default StoryWriter;
