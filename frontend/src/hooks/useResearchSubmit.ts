import { useState, useCallback, useRef } from 'react';
import { blogWriterApi, BlogResearchRequest, BlogResearchResponse } from '../services/blogWriterApi';
import { useBlogWriterResearchPolling } from './usePolling';
import { researchCache } from '../services/researchCache';

export interface UseResearchSubmitOptions {
  onResearchComplete?: (research: BlogResearchResponse) => void;
  navigateToPhase?: (phase: string) => void;
}

export interface UseResearchSubmitReturn {
  startResearch: (keywords: string, blogLength?: string, industry?: string, audience?: string) => Promise<BlogResearchResponse | null>;
  isSubmitting: boolean;
  showProgressModal: boolean;
  setShowProgressModal: (show: boolean) => void;
  currentMessage: string;
  currentStatus: string;
  progressMessages: Array<{ timestamp: string; message: string }>;
  error: string | null;
  result: BlogResearchResponse | null;
  isPolling: boolean;
}

export const useResearchSubmit = ({
  onResearchComplete,
  navigateToPhase,
}: UseResearchSubmitOptions): UseResearchSubmitReturn => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showProgressModal, setShowProgressModal] = useState(false);
  const [currentMessage, setCurrentMessage] = useState('');
  const keywordListRef = useRef<string[]>([]);

  const polling = useBlogWriterResearchPolling({
    onProgress: (message) => {
      setCurrentMessage(message);
    },
    onComplete: (result) => {
      if (result) {
        researchCache.cacheResult(
          keywordListRef.current,
          result.industry || 'General',
          result.target_audience || 'General',
          result
        );
      }
      onResearchComplete?.(result);
      setCurrentMessage('');
      setShowProgressModal(false);
      setIsSubmitting(false);
    },
    onError: (error) => {
      setCurrentMessage('');
      setShowProgressModal(false);
      setIsSubmitting(false);
    },
  });

  const startResearch = useCallback(async (
    keywords: string,
    blogLength: string = '1000',
    industry: string = 'General',
    audience: string = 'General',
  ): Promise<BlogResearchResponse | null> => {
    const trimmed = keywords.trim();
    if (!trimmed) return null;

    setIsSubmitting(true);

    try {
      const keywordList = trimmed.includes(',')
        ? trimmed.split(',').map(k => k.trim()).filter(Boolean)
        : [trimmed];

      keywordListRef.current = keywordList;

      const cachedResult = researchCache.getCachedResult(keywordList, industry, audience);
      if (cachedResult) {
        onResearchComplete?.(cachedResult);
        setIsSubmitting(false);
        return cachedResult;
      }

      navigateToPhase?.('research');

      setShowProgressModal(true);
      setCurrentMessage('Starting research...');

      const payload: BlogResearchRequest = {
        keywords: keywordList,
        industry,
        target_audience: audience,
        word_count_target: parseInt(blogLength),
      };

      const { task_id } = await blogWriterApi.startResearch(payload);
      polling.startPolling(task_id);
      return null;
    } catch (error) {
      setCurrentMessage('');
      setShowProgressModal(false);
      setIsSubmitting(false);
      throw error;
    }
  }, [onResearchComplete, navigateToPhase, polling]);

  return {
    startResearch,
    isSubmitting,
    showProgressModal,
    setShowProgressModal,
    currentMessage,
    currentStatus: polling.currentStatus,
    progressMessages: polling.progressMessages,
    error: polling.error,
    result: polling.result,
    isPolling: polling.isPolling,
  };
};

export default useResearchSubmit;
