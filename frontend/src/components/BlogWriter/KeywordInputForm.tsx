import React, { useState } from 'react';
import { useCopilotAction } from '@copilotkit/react-core';
import { blogWriterApi, BlogResearchRequest, BlogResearchResponse } from '../../services/blogWriterApi';
import ResearchPollingHandler from './ResearchPollingHandler';
import { researchCache } from '../../services/researchCache';

const useCopilotActionTyped = useCopilotAction as any;

interface KeywordInputFormProps {
  onKeywordsReceived?: (data: { keywords: string; blogLength: string }) => void;
  onResearchComplete?: (researchData: BlogResearchResponse) => void;
  onTaskStart?: (taskId: string) => void;
}

export const KeywordInputForm: React.FC<KeywordInputFormProps> = ({ onKeywordsReceived, onResearchComplete, onTaskStart }) => {
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null);

  // This component now only provides polling functionality
  // The keyword input form is handled by ResearchAction component

  return (
    <>
      {/* Polling handler for research progress */}
      <ResearchPollingHandler
        taskId={currentTaskId}
        onResearchComplete={(result) => {
          onResearchComplete?.(result);
          setCurrentTaskId(null);
        }}
        onError={(error) => {
          console.error('Research error:', error);
          setCurrentTaskId(null);
        }}
      />
    </>
  );
};

export default KeywordInputForm;