import { useState, useCallback } from 'react';
import { aiVisibilityApi, AIVisibilityResponse, AIOThresholdInput } from '../api/aiVisibility';

const DEFAULT_THRESHOLDS: AIOThresholdInput = {
  impacted_min_impressions: 500,
  impacted_max_position: 4.0,
  impacted_max_ctr: 2.0,
  opportunity_min_impressions: 300,
  opportunity_min_position: 4.0,
  opportunity_max_position: 10.0,
  opportunity_min_ctr: 5.0,
};

interface UseAIVisibilityInsightsState {
  loading: boolean;
  error: string | null;
  result: AIVisibilityResponse | null;
  thresholds: AIOThresholdInput;
}

export function useAIVisibilityInsights() {
  const [state, setState] = useState<UseAIVisibilityInsightsState>({
    loading: false,
    error: null,
    result: null,
    thresholds: { ...DEFAULT_THRESHOLDS },
  });

  const runAnalysis = useCallback(
    async (
      siteUrl: string,
      startDate?: string,
      endDate?: string,
      thresholds?: AIOThresholdInput,
    ) => {
      setState((prev) => ({ ...prev, loading: true, error: null }));
      try {
        const result = await aiVisibilityApi.getOverviewInsights(
          siteUrl,
          startDate,
          endDate,
          thresholds || state.thresholds,
        );
        setState((prev) => ({
          ...prev,
          loading: false,
          result,
          error: result.error || null,
          thresholds: thresholds || prev.thresholds,
        }));
      } catch (e: any) {
        setState((prev) => ({
          ...prev,
          loading: false,
          error: e?.message || 'Analysis failed',
        }));
      }
    },
    [state.thresholds],
  );

  const setThreshold = useCallback(
    <K extends keyof AIOThresholdInput>(key: K, value: AIOThresholdInput[K]) => {
      setState((prev) => ({
        ...prev,
        thresholds: { ...prev.thresholds, [key]: value },
      }));
    },
    [],
  );

  const resetThresholds = useCallback(() => {
    setState((prev) => ({
      ...prev,
      thresholds: { ...DEFAULT_THRESHOLDS },
    }));
  }, []);

  const reset = useCallback(() => {
    setState({
      loading: false,
      error: null,
      result: null,
      thresholds: { ...DEFAULT_THRESHOLDS },
    });
  }, []);

  return {
    ...state,
    runAnalysis,
    setThreshold,
    resetThresholds,
    reset,
    defaultThresholds: DEFAULT_THRESHOLDS,
  };
}
