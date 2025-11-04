import React from 'react';
import PhaseNavigation, { PhaseActionHandlers } from '../PhaseNavigation';

interface HeaderBarProps {
  phases: any[];
  currentPhase: string;
  onPhaseClick: (phaseId: string) => void;
  copilotKitAvailable?: boolean;
  actionHandlers?: PhaseActionHandlers;
  hasResearch?: boolean;
  hasOutline?: boolean;
  outlineConfirmed?: boolean;
  hasContent?: boolean;
  contentConfirmed?: boolean;
  hasSEOAnalysis?: boolean;
  seoRecommendationsApplied?: boolean;
  hasSEOMetadata?: boolean;
}

export const HeaderBar: React.FC<HeaderBarProps> = ({ 
  phases, 
  currentPhase, 
  onPhaseClick,
  copilotKitAvailable = true,
  actionHandlers,
  hasResearch = false,
  hasOutline = false,
  outlineConfirmed = false,
  hasContent = false,
  contentConfirmed = false,
  hasSEOAnalysis = false,
  seoRecommendationsApplied = false,
  hasSEOMetadata = false,
}) => {
  return (
    <div style={{ padding: 16, borderBottom: '1px solid #eee' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <h2 style={{ margin: 0 }}>AI Blog Writer</h2>
        <div style={{ 
          width: '40px', 
          height: '40px', 
          backgroundColor: '#f0f0f0', 
          borderRadius: '8px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '20px',
          fontWeight: 'bold',
          color: '#666'
        }}>
          A
        </div>
      </div>
      <PhaseNavigation
        phases={phases}
        currentPhase={currentPhase}
        onPhaseClick={onPhaseClick}
        copilotKitAvailable={copilotKitAvailable}
        actionHandlers={actionHandlers}
        hasResearch={hasResearch}
        hasOutline={hasOutline}
        outlineConfirmed={outlineConfirmed}
        hasContent={hasContent}
        contentConfirmed={contentConfirmed}
        hasSEOAnalysis={hasSEOAnalysis}
        seoRecommendationsApplied={seoRecommendationsApplied}
        hasSEOMetadata={hasSEOMetadata}
      />
    </div>
  );
};

export default HeaderBar;


