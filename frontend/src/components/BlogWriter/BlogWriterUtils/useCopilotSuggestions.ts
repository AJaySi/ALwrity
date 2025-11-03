import React, { useRef, useEffect, useMemo } from 'react';
import { useCopilotChatHeadless_c } from '@copilotkit/react-core';
import { debug } from '../../../utils/debug';
import { useSuggestions } from '../SuggestionsGenerator';

interface UseCopilotSuggestionsProps {
  research: any;
  outline: any[];
  outlineConfirmed: boolean;
  researchPollingState: { isPolling: boolean; currentStatus: any };
  outlinePollingState: { isPolling: boolean; currentStatus: any };
  mediumPollingState: { isPolling: boolean; currentStatus: any };
  hasContent: boolean;
  flowAnalysisCompleted: boolean;
  contentConfirmed: boolean;
  seoAnalysis: any;
  seoMetadata: any;
  seoRecommendationsApplied: boolean;
}

export const useCopilotSuggestions = ({
  research,
  outline,
  outlineConfirmed,
  researchPollingState,
  outlinePollingState,
  mediumPollingState,
  hasContent,
  flowAnalysisCompleted,
  contentConfirmed,
  seoAnalysis,
  seoMetadata,
  seoRecommendationsApplied,
}: UseCopilotSuggestionsProps) => {
  const suggestions = useSuggestions({
    research,
    outline,
    outlineConfirmed,
    researchPolling: researchPollingState,
    outlinePolling: outlinePollingState,
    mediumPolling: mediumPollingState,
    hasContent,
    flowAnalysisCompleted,
    contentConfirmed,
    seoAnalysis,
    seoMetadata,
    seoRecommendationsApplied,
  });

  // Drive CopilotKit suggestions programmatically
  const copilotHeadless = (useCopilotChatHeadless_c as any)?.();
  const setSuggestionsRef = useRef<any>(null);
  useEffect(() => {
    setSuggestionsRef.current = copilotHeadless?.setSuggestions;
  }, [copilotHeadless]);

  const suggestionsPayload = useMemo(
    () => (Array.isArray(suggestions) ? suggestions.map((s: any) => ({ title: s.title, message: s.message })) : []),
    [suggestions]
  );
  const prevSuggestionsRef = useRef<string>("__init__");
  const suggestionsJson = useMemo(() => JSON.stringify(suggestionsPayload), [suggestionsPayload]);
  
  useEffect(() => {
    try {
      if (!setSuggestionsRef.current) return;
      if (suggestionsJson !== prevSuggestionsRef.current) {
        setSuggestionsRef.current(suggestionsPayload);
        debug.log('[BlogWriter] Copilot suggestions pushed', { count: suggestionsPayload.length });
        prevSuggestionsRef.current = suggestionsJson;
      }
    } catch {}
  }, [suggestionsJson, suggestionsPayload]);

  // Force-sync Copilot suggestions right after SEO recommendations applied
  useEffect(() => {
    if (!seoAnalysis || !seoRecommendationsApplied || !setSuggestionsRef.current) return;
    try {
      if (suggestionsJson !== prevSuggestionsRef.current) {
        setSuggestionsRef.current(suggestionsPayload);
        debug.log('[BlogWriter] Forced Copilot suggestions sync after SEO recommendations applied', { count: suggestionsPayload.length });
        prevSuggestionsRef.current = suggestionsJson;
      }
    } catch (e) {
      console.error('Failed to push Copilot suggestions after SEO apply:', e);
    }
  }, [seoAnalysis, seoRecommendationsApplied, suggestionsJson, suggestionsPayload]);

  return {
    suggestions,
    setSuggestionsRef,
  };
};

