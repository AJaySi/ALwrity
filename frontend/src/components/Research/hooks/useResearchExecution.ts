import { useState, useCallback } from 'react';
import { blogWriterApi, BlogResearchRequest, BlogResearchResponse } from '../../../services/blogWriterApi';
import { useResearchPolling } from '../../../hooks/usePolling';
import { researchCache } from '../../../services/researchCache';
import { WizardState } from '../types/research.types';

export const useResearchExecution = () => {
  const [isExecuting, setIsExecuting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const polling = useResearchPolling({
    onComplete: (result) => {
      if (result && result.keywords) {
        researchCache.cacheResult(
          result.keywords,
          'General',
          'General',
          result
        );
      }
      setIsExecuting(false);
    },
    onError: (error) => {
      console.error('Research polling error:', error);
      setError(error);
      setIsExecuting(false);
    }
  });

  const executeResearch = useCallback(async (state: WizardState): Promise<string | null> => {
    setIsExecuting(true);
    setError(null);

    try {
      // Check cache first
      const cachedResult = researchCache.getCachedResult(
        state.keywords,
        state.industry,
        state.targetAudience
      );
      
      if (cachedResult) {
        setIsExecuting(false);
        return 'cached';
      }

      const payload: BlogResearchRequest = {
        keywords: state.keywords,
        industry: state.industry,
        target_audience: state.targetAudience,
        research_mode: state.researchMode,
        config: state.config,
      };

      const { task_id } = await blogWriterApi.startResearch(payload);
      polling.startPolling(task_id);
      return task_id;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      setIsExecuting(false);
      return null;
    }
  }, [polling]);

  const stopExecution = useCallback(() => {
    polling.stopPolling();
    setIsExecuting(false);
    setError(null);
  }, [polling]);

  return {
    executeResearch,
    stopExecution,
    isExecuting,
    error,
    progressMessages: polling.progressMessages,
    currentStatus: polling.currentStatus,
    result: polling.result,
  };
};

