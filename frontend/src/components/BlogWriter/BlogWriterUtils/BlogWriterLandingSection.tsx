import React from 'react';
import BlogWriterLanding from '../BlogWriterLanding';
import ManualResearchForm from '../ManualResearchForm';

interface BlogWriterLandingSectionProps {
  research: any;
  copilotKitAvailable: boolean;
  currentPhase: string;
  navigateToPhase: (phase: string) => void;
  onResearchComplete: (research: any) => void;
}

export const BlogWriterLandingSection: React.FC<BlogWriterLandingSectionProps> = ({
  research,
  copilotKitAvailable,
  currentPhase,
  navigateToPhase,
  onResearchComplete,
}) => {
  if (!research) {
    return (
      <>
        {!copilotKitAvailable && currentPhase === 'research' && (
          <ManualResearchForm onResearchComplete={onResearchComplete} />
        )}
        {copilotKitAvailable && (
          <BlogWriterLanding 
            onStartWriting={() => {
              // Trigger the copilot to start the research process
            }}
          />
        )}
        {!copilotKitAvailable && currentPhase !== 'research' && (
          <BlogWriterLanding 
            onStartWriting={() => {
              // Navigate to research phase when CopilotKit unavailable
              navigateToPhase('research');
            }}
          />
        )}
      </>
    );
  }
  return null;
};

