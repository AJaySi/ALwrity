import React, { useState, useEffect } from 'react';
import { useResearchPolling } from '../../hooks/usePolling';
import ResearchProgressModal from './ResearchProgressModal';
import { BlogResearchResponse } from '../../services/blogWriterApi';
import { researchCache } from '../../services/researchCache';
import { debug } from '../../utils/debug';

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
      debug.log('[ResearchPollingHandler] progress', { message });
      setCurrentMessage(message);
    },
    onComplete: (result) => {
      debug.log('[ResearchPollingHandler] complete');
      
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
      debug.error('[ResearchPollingHandler] error', error);
      onError?.(error);
      setCurrentMessage('');
    }
  });

  // Start polling when taskId is provided
  useEffect(() => {
    if (taskId) {
      polling.startPolling(taskId);
    } else {
      // Only stop if actually polling (not on every render when taskId is null)
      if (polling.isPolling) {
        polling.stopPolling();
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [taskId]); // Removed polling from dependencies - usePolling already handles cleanup

  // Only log on meaningful changes
  useEffect(() => {
    debug.log('[ResearchPollingHandler] state', {
      isPolling: polling.isPolling,
      status: polling.currentStatus,
      progressCount: polling.progressMessages?.length || 0
    });
  }, [polling.isPolling, polling.currentStatus, polling.progressMessages?.length]);

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
