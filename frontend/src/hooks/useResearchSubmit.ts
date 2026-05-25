import { useState, useCallback, useRef, useEffect } from 'react';
import { blogWriterApi, BlogResearchRequest, BlogResearchResponse } from '../services/blogWriterApi';
import { useBlogWriterResearchPolling } from './usePolling';
import { researchCache } from '../services/researchCache';

// Simulated progress messages shown while waiting for real backend updates.
// Research takes 40-60s; the backend sends 5-8 messages. These bridge the gaps
// so the user always sees something helpful.
const SIMULATED_MESSAGES: Array<{ delaySec: number; message: string }> = [
  { delaySec: 3,  message: '🔍 Validating keywords and preparing search queries…' },
  { delaySec: 8,  message: '🌐 Connecting to Exa deep-web search for authoritative sources…' },
  { delaySec: 14, message: '📊 Analyzing top-ranking pages and extracting structured data…' },
  { delaySec: 20, message: '🔍 Running Tavily real-time web search for current coverage…' },
  { delaySec: 26, message: '🧠 Cross-referencing results from multiple search engines…' },
  { delaySec: 32, message: '📋 Extracting key statistics, quotes, and content angles…' },
  { delaySec: 38, message: '🔬 Filtering and ranking sources by authority and relevance…' },
  { delaySec: 44, message: '📦 Assembling your research brief with source citations…' },
  { delaySec: 50, message: '💾 Caching results for future use — next up: Outline phase' },
];

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
  const simulatedTimersRef = useRef<NodeJS.Timeout[]>([]);
  const startedAtRef = useRef<number>(0);

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
      // Clear any pending simulated messages
      simulatedTimersRef.current.forEach(clearTimeout);
      simulatedTimersRef.current = [];
      onResearchComplete?.(result);
      setCurrentMessage('');
      setShowProgressModal(false);
      setIsSubmitting(false);
    },
    onError: (error) => {
      simulatedTimersRef.current.forEach(clearTimeout);
      simulatedTimersRef.current = [];
      setCurrentMessage('');
      setShowProgressModal(false);
      setIsSubmitting(false);
    },
  });

  // Schedule simulated progress messages when modal is open and polling is active
  useEffect(() => {
    if (!showProgressModal || !isSubmitting) {
      return;
    }
    const elapsed = Date.now() - startedAtRef.current;
    SIMULATED_MESSAGES.forEach(({ delaySec, message }) => {
      const msUntil = (delaySec * 1000) - elapsed;
      if (msUntil <= 0) return; // already past this point
      const timer = setTimeout(() => {
        setCurrentMessage(message);
      }, msUntil);
      simulatedTimersRef.current.push(timer);
    });
    return () => {
      simulatedTimersRef.current.forEach(clearTimeout);
      simulatedTimersRef.current = [];
    };
  }, [showProgressModal, isSubmitting]);

  const startResearch = useCallback(async (
    keywords: string,
    blogLength: string = '1000',
    industry: string = 'General',
    audience: string = 'General',
  ): Promise<BlogResearchResponse | null> => {
    const trimmed = keywords.trim();
    if (!trimmed) return null;

    setIsSubmitting(true);
    startedAtRef.current = Date.now();

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
      setCurrentMessage('🔍 Research pipeline initializing — validating your topic and preparing search queries…');

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
      simulatedTimersRef.current.forEach(clearTimeout);
      simulatedTimersRef.current = [];
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
