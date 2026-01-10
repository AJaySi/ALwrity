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
    // Show research form only when user explicitly navigated to research phase (clicked "Start Research")
    if (currentPhase === 'research') {
      return <ManualResearchForm onResearchComplete={onResearchComplete} />;
    }
    
    // Default: Always show landing page when no research exists
    // This ensures landing page is shown on initial load
    return (
      <BlogWriterLanding 
        onStartWriting={() => {
          // Navigate to research phase to show the research form
          navigateToPhase('research');
        }}
      />
    );
  }
  
  // If research exists, don't show landing section (phase content will be shown instead)
  return null;
};

