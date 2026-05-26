import { useState, useCallback, useRef, useEffect } from 'react';
import { useAuth } from '@clerk/clerk-react';
import {
  gscBrainstormAPI,
  BrainstormResult,
  ContentOpportunity,
  KeywordGap,
  QuickWin,
  PageOpportunity,
  AIRecommendations,
  AIRecommendation,
  BrainstormSummary,
} from '../api/gscBrainstorm';
import { useGSCBrainstormConnection } from './useGSCBrainstormConnection';

interface UseGSCBrainstormReturn {
  gscConnected: boolean;
  gscSites: { siteUrl: string; permissionLevel: string }[] | null;
  isConnecting: boolean;
  connectError: string | null;
  isBrainstorming: boolean;
  brainstormError: string | null;
  brainstormResult: BrainstormResult | null;
  contentOpportunities: ContentOpportunity[];
  keywordGaps: KeywordGap[];
  quickWins: QuickWin[];
  pageOpportunities: PageOpportunity[];
  aiRecommendations: AIRecommendations | null;
  summary: BrainstormSummary | null;
  connectGSC: () => Promise<void>;
  brainstorm: (keywords: string, siteUrl?: string) => Promise<BrainstormResult | null>;
  reset: () => void;
  progressMessage: string;
}

const PROGRESS_MESSAGES = [
  'Fetching your Google Search Console data for the last 30 days...',
  'Analyzing which keywords bring traffic to your site and which ones need work...',
  'Scanning for quick wins — keywords already on page 1 that just need a boost...',
  'Identifying keyword gaps where better content could move you to page 1...',
  'Reviewing your pages for optimization opportunities...',
  'Computing your SEO health score and benchmark metrics...',
  'Generating AI-powered blog post recommendations tailored to your GSC data...',
  'Formatting insights into actionable topic suggestions you can use today...',
];

export const useGSCBrainstorm = (): UseGSCBrainstormReturn => {
  const { getToken } = useAuth();
  const {
    gscConnected,
    gscSites,
    isConnecting,
    connectError,
    checkConnection,
    connectGSC,
  } = useGSCBrainstormConnection();

  const [isBrainstorming, setIsBrainstorming] = useState(false);
  const [brainstormError, setBrainstormError] = useState<string | null>(null);
  const [brainstormResult, setBrainstormResult] = useState<BrainstormResult | null>(null);
  const [progressMessage, setProgressMessage] = useState('');
  const progressIndexRef = useRef(0);
  const progressTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    return () => {
      if (progressTimerRef.current) {
        clearInterval(progressTimerRef.current);
      }
    };
  }, []);

  const startProgressMessages = () => {
    progressIndexRef.current = 0;
    setProgressMessage(PROGRESS_MESSAGES[0]);
    progressTimerRef.current = setInterval(() => {
      progressIndexRef.current += 1;
      if (progressIndexRef.current < PROGRESS_MESSAGES.length) {
        setProgressMessage(PROGRESS_MESSAGES[progressIndexRef.current]);
      } else if (progressTimerRef.current) {
        clearInterval(progressTimerRef.current);
        progressTimerRef.current = null;
      }
    }, 3000);
  };

  const stopProgressMessages = () => {
    if (progressTimerRef.current) {
      clearInterval(progressTimerRef.current);
      progressTimerRef.current = null;
    }
    setProgressMessage('');
  };

  const brainstorm = useCallback(
    async (keywords: string, siteUrl?: string): Promise<BrainstormResult | null> => {
      setIsBrainstorming(true);
      setBrainstormError(null);
      startProgressMessages();

      try {
        gscBrainstormAPI.setAuthTokenGetter(async () => {
          try {
            return await getToken();
          } catch {
            return null;
          }
        });

        const result = await gscBrainstormAPI.brainstorm(keywords, siteUrl);
        setBrainstormResult(result);
        return result;
      } catch (error: any) {
        let message = 'Failed to brainstorm topics. Please try again.';
        if (error?.response?.data?.detail) {
          message = error.response.data.detail;
        } else if (error instanceof Error) {
          message = error.message;
        }
        setBrainstormError(message);
        return null;
      } finally {
        setIsBrainstorming(false);
        stopProgressMessages();
      }
    },
    [getToken],
  );

  const reset = useCallback(() => {
    setBrainstormResult(null);
    setBrainstormError(null);
    setIsBrainstorming(false);
    stopProgressMessages();
  }, []);

  return {
    gscConnected,
    gscSites,
    isConnecting,
    connectError,
    isBrainstorming,
    brainstormError,
    brainstormResult,
    contentOpportunities: brainstormResult?.content_opportunities ?? [],
    keywordGaps: brainstormResult?.keyword_gaps ?? [],
    quickWins: brainstormResult?.quick_wins ?? [],
    pageOpportunities: brainstormResult?.page_opportunities ?? [],
    aiRecommendations: brainstormResult?.ai_recommendations
      && Array.isArray(brainstormResult.ai_recommendations?.immediate_opportunities)
      ? (brainstormResult.ai_recommendations as AIRecommendations)
      : null,
    summary: brainstormResult?.summary
      && brainstormResult.summary.site_url
      ? (brainstormResult.summary as BrainstormSummary)
      : null,
    connectGSC,
    brainstorm,
    reset,
    progressMessage,
  };
};
