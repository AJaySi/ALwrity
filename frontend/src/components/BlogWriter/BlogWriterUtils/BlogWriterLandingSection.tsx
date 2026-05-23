import React from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';
import BlogWriterLanding from '../BlogWriterLanding';
import ManualResearchForm from '../ManualResearchForm';

interface BlogWriterLandingSectionProps {
  research: any;
  copilotKitAvailable: boolean;
  currentPhase: string;
  navigateToPhase: (phase: string) => void;
  onResearchComplete: (research: any) => void;
  onBeforeResearchSubmit?: (keywords: string, blogLength: string) => Promise<void>;
  restoreAttempted?: boolean;
}

const VALID_PHASES = ['research', 'outline', 'content', 'seo', 'publish'];

export const BlogWriterLandingSection: React.FC<BlogWriterLandingSectionProps> = ({
  research,
  copilotKitAvailable,
  currentPhase,
  navigateToPhase,
  onResearchComplete,
  onBeforeResearchSubmit,
  restoreAttempted = false,
}) => {
  if (!research) {
    if (currentPhase === 'research') {
      return <ManualResearchForm onResearchComplete={onResearchComplete} onBeforeResearchSubmit={onBeforeResearchSubmit} />;
    }

    if (currentPhase === '' || !VALID_PHASES.includes(currentPhase)) {
      return (
        <BlogWriterLanding 
          onStartWriting={() => {
            navigateToPhase('research');
          }}
        />
      );
    }

    if (restoreAttempted) {
      return (
        <BlogWriterLanding 
          onStartWriting={() => {
            navigateToPhase('research');
          }}
        />
      );
    }

    return (
      <Box 
        display="flex" 
        flexDirection="column" 
        alignItems="center" 
        justifyContent="center" 
        minHeight="300px"
        gap={2}
      >
        <CircularProgress size={32} />
        <Typography variant="body2" color="text.secondary">
          Restoring your work...
        </Typography>
      </Box>
    );
  }
  
  return null;
};

