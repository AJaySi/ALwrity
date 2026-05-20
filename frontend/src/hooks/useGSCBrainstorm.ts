import { useState, useCallback } from 'react';
import { useAuth } from '@clerk/clerk-react';
import {
  gscBrainstormAPI,
  BrainstormResult,
  ContentOpportunity,
  KeywordGap,
  AIRecommendations,
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
  aiRecommendations: AIRecommendations | null;
  summary: BrainstormSummary | null;
  connectGSC: () => Promise<void>;
  brainstorm: (keywords: string, siteUrl?: string) => Promise<BrainstormResult | null>;
  reset: () => void;
}

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

  const brainstorm = useCallback(
    async (keywords: string, siteUrl?: string): Promise<BrainstormResult | null> => {
      setIsBrainstorming(true);
      setBrainstormError(null);

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
      } catch (error) {
        const message =
          error instanceof Error ? error.message : 'Failed to brainstorm topics. Please try again.';
        setBrainstormError(message);
        return null;
      } finally {
        setIsBrainstorming(false);
      }
    },
    [getToken],
  );

  const reset = useCallback(() => {
    setBrainstormResult(null);
    setBrainstormError(null);
    setIsBrainstorming(false);
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
    aiRecommendations: brainstormResult?.ai_recommendations
      && Object.keys(brainstormResult.ai_recommendations).length > 0
      ? (brainstormResult.ai_recommendations as AIRecommendations)
      : null,
    summary: brainstormResult?.summary
      && Object.keys(brainstormResult.summary).length > 0
      ? (brainstormResult.summary as BrainstormSummary)
      : null,
    connectGSC,
    brainstorm,
    reset,
  };
};