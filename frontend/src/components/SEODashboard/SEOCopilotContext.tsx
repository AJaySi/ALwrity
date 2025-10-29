// SEO CopilotKit Context Component
// Provides real-time context and instructions to CopilotKit

import React, { useEffect, useRef, useMemo } from 'react';
import { useCopilotReadable } from '@copilotkit/react-core';
import { useSEOCopilotStore } from '../../stores/seoCopilotStore';

const SEOCopilotContext: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { 
    analysisData, 
    personalizationData, 
    dashboardLayout, 
    suggestions,
    isLoading,
    isAnalyzing,
    isGenerating,
    error
  } = useSEOCopilotStore();

  const hasLoadedPersonalization = useRef(false);

  // Load personalization data on mount
  useEffect(() => {
    if (!hasLoadedPersonalization.current && !personalizationData) {
      useSEOCopilotStore.getState().loadPersonalizationData();
      hasLoadedPersonalization.current = true;
    }
  }, [personalizationData]);

  // Memoize values to prevent unnecessary re-renders
  const websiteUrl = useMemo(() => analysisData?.url || '', [analysisData?.url]);
  const statusData = useMemo(() => ({
    isLoading,
    isAnalyzing,
    isGenerating,
    error
  }), [isLoading, isAnalyzing, isGenerating, error]);
  const suggestionsCount = useMemo(() => Array.isArray(suggestions) ? suggestions.length : 0, [suggestions]);

  // Register SEO analysis data with CopilotKit
  useCopilotReadable({
    description: "Current SEO analysis data and insights",
    value: analysisData,
    categories: ["seo", "analysis"]
  });

  // Provide a flat, explicit website URL for the LLM
  useCopilotReadable({
    description: "Current website URL the user is working on",
    value: websiteUrl,
    categories: ["seo", "context"]
  });

  // Register personalization data with CopilotKit
  useCopilotReadable({
    description: "User personalization preferences and settings",
    value: personalizationData,
    categories: ["user", "preferences"]
  });

  // Register dashboard layout with CopilotKit
  useCopilotReadable({
    description: "Current dashboard layout and configuration",
    value: dashboardLayout,
    categories: ["ui", "layout"]
  });

  // Register suggestions with CopilotKit
  useCopilotReadable({
    description: "Available SEO actions and suggestions",
    value: suggestions,
    categories: ["actions", "suggestions"]
  });

  // Register loading states with CopilotKit
  useCopilotReadable({
    description: "Current loading and processing states",
    value: statusData,
    categories: ["status", "loading"]
  });

  // Debug logging only in development and only when values actually change
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      console.log('[CopilotContext] Registered analysis data', !!analysisData);
      console.log('[CopilotContext] Registered website URL', websiteUrl);
      console.log('[CopilotContext] Registered personalization', !!personalizationData);
      console.log('[CopilotContext] Registered layout', !!dashboardLayout);
      console.log('[CopilotContext] Registered suggestions', suggestionsCount);
      console.log('[CopilotContext] Registered status', { isLoading, isAnalyzing, isGenerating, hasError: !!error });
    }
  }, [analysisData, websiteUrl, personalizationData, dashboardLayout, suggestionsCount, statusData]);

  return <>{children}</>;
};

export default SEOCopilotContext;
