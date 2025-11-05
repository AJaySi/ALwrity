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
  // This component is now a lightweight wrapper
  // The actual keyword input form is handled by ResearchAction component
  // Polling is handled by ResearchPollingHandler in ResearchAction
  // This component exists for backward compatibility but doesn't create unnecessary polling hooks
  
  // Note: If onTaskStart is called, it should use the researchPolling from parent
  // (passed via CopilotKitComponents), not create a new polling instance here
  
  return null; // No UI needed - ResearchAction handles everything
};

export default KeywordInputForm;