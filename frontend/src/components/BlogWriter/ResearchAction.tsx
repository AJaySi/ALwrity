import React, { useState } from 'react';
import { useCopilotAction } from '@copilotkit/react-core';
import { blogWriterApi, BlogResearchRequest, BlogResearchResponse } from '../../services/blogWriterApi';
import { useResearchPolling } from '../../hooks/usePolling';
import ResearchProgressModal from './ResearchProgressModal';
import { researchCache } from '../../services/researchCache';

const useCopilotActionTyped = useCopilotAction as any;

interface ResearchActionProps {
  onResearchComplete?: (research: BlogResearchResponse) => void;
}

export const ResearchAction: React.FC<ResearchActionProps> = ({ onResearchComplete }) => {
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null);
  const [currentMessage, setCurrentMessage] = useState<string>('');
  const [showProgressModal, setShowProgressModal] = useState<boolean>(false);

  const polling = useResearchPolling({
    onProgress: (message) => {
      setCurrentMessage(message);
    },
    onComplete: (result) => {
      // Cache the result for future use
      if (result && result.keywords) {
        researchCache.cacheResult(
          result.keywords,
          result.industry || 'General',
          result.target_audience || 'General',
          result
        );
      }
      
      onResearchComplete?.(result);
      setCurrentTaskId(null);
      setCurrentMessage('');
      setShowProgressModal(false);
    },
    onError: (error) => {
      console.error('Research polling error:', error);
      setCurrentTaskId(null);
      setCurrentMessage('');
      setShowProgressModal(false);
    }
  });

  useCopilotActionTyped({
    name: 'researchTopic',
    description: 'Research topic with keywords and persona context using Google Search grounding',
    parameters: [
      { name: 'keywords', type: 'string', description: 'Comma-separated keywords or topic description', required: true },
      { name: 'industry', type: 'string', description: 'Industry', required: false },
      { name: 'target_audience', type: 'string', description: 'Target audience', required: false },
      { name: 'blogLength', type: 'string', description: 'Target blog length in words', required: false }
    ],
    handler: async ({ keywords, industry, target_audience, blogLength }: { keywords: string; industry?: string; target_audience?: string; blogLength?: string }) => {
      try {
        // If keywords is a topic description, preserve as single phrase unless comma-separated
        const keywordList = keywords.includes(',') 
          ? keywords.split(',').map(k => k.trim())
          : [keywords.trim()]; // Preserve single phrases as-is
        
        const industryValue = industry || 'General';
        const audienceValue = target_audience || 'General';
        
        // Check frontend cache first
        const cachedResult = researchCache.getCachedResult(keywordList, industryValue, audienceValue);
        if (cachedResult) {
          console.log('Frontend cache hit - returning cached result instantly');
          onResearchComplete?.(cachedResult);
          return { 
            success: true, 
            message: `✅ Found cached research for "${keywords}"! Results loaded instantly.`,
            cached: true
          };
        }
        
        const payload: BlogResearchRequest = { 
          keywords: keywordList, 
          industry: industryValue, 
          target_audience: audienceValue,
          word_count_target: blogLength ? parseInt(blogLength) : 1000
        };
        
        // Start async research
        const { task_id } = await blogWriterApi.startResearch(payload);
        setCurrentTaskId(task_id);
        setShowProgressModal(true);
        polling.startPolling(task_id);
        
        return { 
          success: true, 
          message: `🔍 Research started for "${keywords}"! Task ID: ${task_id}. Progress will be shown below.`,
          task_id: task_id
        };
      } catch (error) {
        console.error(`Research failed: ${error}`);
        return { 
          success: false, 
          message: `❌ Research failed: ${error}. The AI research system encountered an issue. Please try again with different keywords or contact support if the problem persists.` 
        };
      }
    },
    render: () => null
  });

  return (
    <ResearchProgressModal
      open={showProgressModal}
      title="Research in progress"
      status={polling.currentStatus}
      messages={polling.progressMessages}
      error={polling.error}
      onClose={() => setShowProgressModal(false)}
    />
  );
};

export default ResearchAction;
