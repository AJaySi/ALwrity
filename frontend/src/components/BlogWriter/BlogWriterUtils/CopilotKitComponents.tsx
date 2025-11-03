import React from 'react';
import KeywordInputForm from '../KeywordInputForm';
import ResearchAction from '../ResearchAction';
import { CustomOutlineForm } from '../CustomOutlineForm';
import { ResearchDataActions } from '../ResearchDataActions';
import { EnhancedOutlineActions } from '../EnhancedOutlineActions';
import OutlineFeedbackForm from '../OutlineFeedbackForm';
import { RewriteFeedbackForm } from '../RewriteFeedbackForm';

interface CopilotKitComponentsProps {
  research: any;
  outline: any[];
  outlineConfirmed: boolean;
  sections: Record<string, string>;
  selectedTitle: string | null;
  onResearchComplete: (research: any) => void;
  onOutlineCreated: (outline: any[]) => void;
  onOutlineUpdated: (outline: any[]) => void;
  onTitleOptionsSet: (titles: any[]) => void;
  onOutlineConfirmed: () => void;
  onOutlineRefined: (feedback?: string) => void;
  onMediumGenerationStarted: (taskId: string) => void;
  onMediumGenerationTriggered: () => void;
  onRewriteStarted: (taskId: string) => void;
  onRewriteTriggered: () => void;
  setFlowAnalysisCompleted: (completed: boolean) => void;
  setFlowAnalysisResults: (results: any) => void;
  setContinuityRefresh: (refresh: number | ((prev: number) => number)) => void;
  researchPolling: any;
}

export const CopilotKitComponents: React.FC<CopilotKitComponentsProps> = ({
  research,
  outline,
  outlineConfirmed,
  sections,
  selectedTitle,
  onResearchComplete,
  onOutlineCreated,
  onOutlineUpdated,
  onTitleOptionsSet,
  onOutlineConfirmed,
  onOutlineRefined,
  onMediumGenerationStarted,
  onMediumGenerationTriggered,
  onRewriteStarted,
  onRewriteTriggered,
  setFlowAnalysisCompleted,
  setFlowAnalysisResults,
  setContinuityRefresh,
  researchPolling,
}) => {
  return (
    <>
      <KeywordInputForm 
        onResearchComplete={onResearchComplete}
        onTaskStart={(taskId) => researchPolling.startPolling(taskId)}
      />
      <CustomOutlineForm onOutlineCreated={onOutlineCreated} />
      <ResearchAction onResearchComplete={onResearchComplete} />
      
      <ResearchDataActions 
        research={research} 
        onOutlineCreated={onOutlineCreated} 
        onTitleOptionsSet={onTitleOptionsSet} 
      />
      <EnhancedOutlineActions 
        outline={outline} 
        onOutlineUpdated={onOutlineUpdated} 
      />
      <OutlineFeedbackForm
        outline={outline} 
        research={research!} 
        onOutlineConfirmed={onOutlineConfirmed}
        onOutlineRefined={onOutlineRefined}
        onMediumGenerationStarted={onMediumGenerationStarted}
        onMediumGenerationTriggered={onMediumGenerationTriggered}
        sections={sections}
        blogTitle={selectedTitle ?? undefined}
        onFlowAnalysisComplete={(analysis) => {
          console.log('Flow analysis completed:', analysis);
          setFlowAnalysisCompleted(true);
          setFlowAnalysisResults(analysis);
          // Trigger a refresh of continuity badges
          setContinuityRefresh((prev: number) => (prev || 0) + 1);
        }}
      />
      
      {/* Rewrite Feedback Form - Only show when content exists */}
      {Object.keys(sections).length > 0 && (
        <RewriteFeedbackForm
          research={research!}
          outline={outline}
          sections={sections}
          blogTitle={selectedTitle || 'Untitled'}
          onRewriteStarted={onRewriteStarted}
          onRewriteTriggered={onRewriteTriggered}
        />
      )}
    </>
  );
};

