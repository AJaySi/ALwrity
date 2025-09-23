import React, { useState, useEffect } from 'react';
import { useResearchPolling } from '../../hooks/usePolling';
import ResearchProgressModal from './ResearchProgressModal';
import { BlogResearchResponse } from '../../services/blogWriterApi';
import { researchCache } from '../../services/researchCache';

interface ResearchPollingHandlerProps {
  taskId: string | null;
  onResearchComplete: (result: BlogResearchResponse) => void;
  onError?: (error: string) => void;
}

export const ResearchPollingHandler: React.FC<ResearchPollingHandlerProps> = ({
  taskId,
  onResearchComplete,
  onError
}) => {
  const [currentMessage, setCurrentMessage] = useState<string>('');

  const polling = useResearchPolling({
    onProgress: (message) => {
      console.log('ResearchPollingHandler - Progress message received:', message);
      setCurrentMessage(message);
    },
    onComplete: (result) => {
      console.log('ResearchPollingHandler - Research completed:', result);
      
      // Cache the result for future use
      if (result && result.keywords) {
        researchCache.cacheResult(
          result.keywords,
          result.industry || 'General',
          result.target_audience || 'General',
          result
        );
      }
      
      onResearchComplete(result);
      setCurrentMessage('');
    },
    onError: (error) => {
      console.error('Research polling error:', error);
      onError?.(error);
      setCurrentMessage('');
    }
  });

  // Start polling when taskId is provided
  useEffect(() => {
    if (taskId) {
      polling.startPolling(taskId);
    } else {
      polling.stopPolling();
    }
  }, [taskId]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      polling.stopPolling();
    };
  }, []);

  console.log('ResearchPollingHandler render:', {
    taskId,
    isPolling: polling.isPolling,
    status: polling.currentStatus,
    progressMessages: polling.progressMessages?.length,
    currentMessage,
    error: polling.error
  });

  // Render the unified research progress modal when a task is present
  return (
    <ResearchProgressModal
      open={Boolean(taskId)}
      title="Research in progress"
      status={polling.currentStatus}
      messages={polling.progressMessages}
      error={polling.error}
      onClose={() => { /* modal is informational during processing; ignore manual close */ }}
    />
  );
};

export default ResearchPollingHandler;
