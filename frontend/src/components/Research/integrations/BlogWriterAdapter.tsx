/**
 * Blog Writer Integration Adapter for Research Component
 * 
 * This adapter provides a simple way to integrate the ResearchWizard
 * into the BlogWriter's research phase.
 */

import React from 'react';
import { ResearchWizard } from '../ResearchWizard';
import { BlogResearchResponse } from '../../../services/blogWriterApi';

interface BlogWriterResearchAdapterProps {
  onResearchComplete: (research: BlogResearchResponse) => void;
  onCancel?: () => void;
  initialKeywords?: string[];
  initialIndustry?: string;
}

/**
 * Adapter component that wraps ResearchWizard for BlogWriter integration.
 * Provides a clean interface for switching between CopilotKit and wizard-based research.
 */
export const BlogWriterResearchAdapter: React.FC<BlogWriterResearchAdapterProps> = ({
  onResearchComplete,
  onCancel,
  initialKeywords,
  initialIndustry,
}) => {
  return (
    <div style={{ 
      height: '100%', 
      display: 'flex', 
      flexDirection: 'column',
      backgroundColor: 'white',
    }}>
      <ResearchWizard
        onComplete={onResearchComplete}
        onCancel={onCancel}
        initialKeywords={initialKeywords}
        initialIndustry={initialIndustry}
      />
    </div>
  );
};

export default BlogWriterResearchAdapter;

/**
 * USAGE EXAMPLE:
 * 
 * In BlogWriter.tsx, replace the research phase content with:
 * 
 * {currentPhase === 'research' && !research && (
 *   <BlogWriterResearchAdapter
 *     onResearchComplete={(res) => {
 *       handleResearchComplete(res);
 *       // Optionally auto-advance to outline phase
 *       navigateToPhase('outline');
 *     }}
 *     onCancel={() => {
 *       // Navigate back to dashboard
 *       navigateToPhase('research');
 *     }}
 *     initialKeywords={[]}
 *     initialIndustry="General"
 *   />
 * )}
 * 
 * Note: This maintains backward compatibility. The existing CopilotKit/manual
 * research flow continues to work. This provides an alternative UI option.
 */

