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
  // Only show landing/initial content when no research exists
  // Phase navigation header is always visible, so this is just the initial content
  if (!research) {
    return (
      <>
        {/* Show manual research form when on research phase and CopilotKit unavailable */}
        {!copilotKitAvailable && currentPhase === 'research' && (
          <ManualResearchForm onResearchComplete={onResearchComplete} />
        )}
        {/* Show landing page for CopilotKit flow or when not on research phase */}
        {(!copilotKitAvailable && currentPhase !== 'research') || copilotKitAvailable ? (
          <BlogWriterLanding 
            onStartWriting={() => {
              // Navigate to research phase to start the workflow
              navigateToPhase('research');
            }}
          />
        ) : null}
      </>
    );
  }
  return null;
};

