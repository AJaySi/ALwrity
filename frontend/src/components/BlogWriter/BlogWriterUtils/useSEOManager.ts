import { useState, useRef, useEffect, useCallback } from 'react';
import { debug } from '../../../utils/debug';
import { blogWriterApi, BlogSEOActionableRecommendation } from '../../../services/blogWriterApi';
import { blogWriterCache } from '../../../services/blogWriterCache';

const registerContentKey = (map: Map<string, string>, key: any, content?: string) => {
  if (key === undefined || key === null) {
    return;
  }
  const trimmed = String(key).trim();
  if (!trimmed) {
    return;
  }
  const safeContent = content !== undefined && content !== null ? String(content) : '';
  map.set(trimmed, safeContent);
  map.set(trimmed.toLowerCase(), safeContent);
};

const getIdCandidatesForSection = (section: any, index: number): string[] => {
  const rawCandidates = [
    section?.id,
    section?.section_id,
    section?.sectionId,
    section?.sectionID,
    section?.heading_id,
    `section_${index + 1}`,
    `Section ${index + 1}`,
    `section${index + 1}`,
    `s${index + 1}`,
    `S${index + 1}`,
    `${index + 1}`,
  ];

  const normalized = rawCandidates
    .map((value) => (value === undefined || value === null ? '' : String(value).trim()))
    .filter(Boolean);

  return Array.from(new Set(normalized));
};

const buildExistingContentMap = (sectionsRecord: Record<string, string>): Map<string, string> => {
  const map = new Map<string, string>();
  if (!sectionsRecord) {
    return map;
  }
  Object.entries(sectionsRecord).forEach(([key, value]) => {
    registerContentKey(map, key, value ?? '');
  });
  return map;
};

const buildResponseContentMaps = (responseSections: any[]): { byId: Map<string, string>; byHeading: Map<string, string> } => {
  const byId = new Map<string, string>();
  const byHeading = new Map<string, string>();

  if (!responseSections) {
    return { byId, byHeading };
  }

  responseSections.forEach((section, index) => {
    if (!section) {
      return;
    }
    const content = section?.content;
    const normalizedContent = content !== undefined && content !== null ? String(content).trim() : '';
    if (!normalizedContent) {
      return;
    }

    registerContentKey(byId, section?.id, normalizedContent);
    registerContentKey(byId, section?.section_id, normalizedContent);
    registerContentKey(byId, section?.sectionId, normalizedContent);
    registerContentKey(byId, section?.sectionID, normalizedContent);
    registerContentKey(byId, `section_${index + 1}`, normalizedContent);
    registerContentKey(byId, `Section ${index + 1}`, normalizedContent);
    registerContentKey(byId, `section${index + 1}`, normalizedContent);
    registerContentKey(byId, `s${index + 1}`, normalizedContent);
    registerContentKey(byId, `S${index + 1}`, normalizedContent);
    registerContentKey(byId, `${index + 1}`, normalizedContent);

    const heading = section?.heading || section?.title;
    if (heading) {
      registerContentKey(byHeading, heading, normalizedContent);
    }
  });

  return { byId, byHeading };
};

const getPrimaryKeyForOutlineSection = (outlineSection: any, index: number): string => {
  const candidates = getIdCandidatesForSection(outlineSection, index);
  if (candidates.length > 0) {
    return candidates[0];
  }
  const fallbackHeading = outlineSection?.heading || outlineSection?.title;
  if (fallbackHeading) {
    const trimmed = String(fallbackHeading).trim();
    if (trimmed) {
      return trimmed;
    }
  }
  return `section_${index + 1}`;
};

const resolveContentForOutlineSection = (
  outlineSection: any,
  index: number,
  responseSections: any[],
  responseById: Map<string, string>,
  responseByHeading: Map<string, string>,
  existingContentMap: Map<string, string>
): { content: string; matchedKey: string } => {
  const idCandidates = getIdCandidatesForSection(outlineSection, index);

  for (const candidate of idCandidates) {
    if (responseById.has(candidate)) {
      return { content: responseById.get(candidate) || '', matchedKey: candidate };
    }
    const lower = candidate.toLowerCase();
    if (responseById.has(lower)) {
      return { content: responseById.get(lower) || '', matchedKey: candidate };
    }
  }

  const heading = outlineSection?.heading || outlineSection?.title;
  if (heading) {
    const headingKey = String(heading).trim();
    if (headingKey) {
      const lowerHeading = headingKey.toLowerCase();
      if (responseByHeading.has(lowerHeading)) {
        return { content: responseByHeading.get(lowerHeading) || '', matchedKey: headingKey };
      }
      if (responseByHeading.has(headingKey)) {
        return { content: responseByHeading.get(headingKey) || '', matchedKey: headingKey };
      }
    }
  }

  const responseSection = responseSections?.[index];
  if (responseSection?.content) {
    const normalizedContent = String(responseSection.content).trim();
    if (normalizedContent) {
      return {
        content: normalizedContent,
        matchedKey: idCandidates[0] || getPrimaryKeyForOutlineSection(outlineSection, index),
      };
    }
  }

  for (const candidate of idCandidates) {
    if (existingContentMap.has(candidate)) {
      return { content: existingContentMap.get(candidate) || '', matchedKey: candidate };
    }
    const lower = candidate.toLowerCase();
    if (existingContentMap.has(lower)) {
      return { content: existingContentMap.get(lower) || '', matchedKey: candidate };
    }
  }

  if (heading) {
    const headingKey = String(heading).trim();
    if (headingKey) {
      const lowerHeading = headingKey.toLowerCase();
      if (existingContentMap.has(lowerHeading)) {
        return { content: existingContentMap.get(lowerHeading) || '', matchedKey: headingKey };
      }
      if (existingContentMap.has(headingKey)) {
        return { content: existingContentMap.get(headingKey) || '', matchedKey: headingKey };
      }
    }
  }

  return {
    content: '',
    matchedKey: idCandidates[0] || getPrimaryKeyForOutlineSection(outlineSection, index),
  };
};

interface UseSEOManagerProps {
  sections: Record<string, string>;
  research: any;
  outline: any[];
  selectedTitle: string | null;
  contentConfirmed: boolean;
  seoAnalysis: any;
  currentPhase: string;
  navigateToPhase: (phase: string) => void;
  setContentConfirmed: (confirmed: boolean) => void;
  setSeoAnalysis: (analysis: any) => void;
  setSeoMetadata: (metadata: any) => void;
  setSections: (sections: Record<string, string>) => void;
  setSelectedTitle: (title: string | null) => void;
  setContinuityRefresh: (timestamp: number) => void;
  setFlowAnalysisCompleted: (completed: boolean) => void;
  setFlowAnalysisResults: (results: any) => void;
}

export const useSEOManager = ({
  sections,
  research,
  outline,
  selectedTitle,
  contentConfirmed,
  seoAnalysis,
  currentPhase,
  navigateToPhase,
  setContentConfirmed,
  setSeoAnalysis,
  setSeoMetadata,
  setSections,
  setSelectedTitle,
  setContinuityRefresh,
  setFlowAnalysisCompleted,
  setFlowAnalysisResults,
}: UseSEOManagerProps) => {
  const [isSEOAnalysisModalOpen, setIsSEOAnalysisModalOpen] = useState(false);
  const [isSEOMetadataModalOpen, setIsSEOMetadataModalOpen] = useState(false);
  const [seoRecommendationsApplied, setSeoRecommendationsApplied] = useState(false);
  const lastSEOModalOpenRef = useRef<number>(0);

  // Helper: run same checks as analyzeSEO and open modal
  const runSEOAnalysisDirect = useCallback((): string => {
    const hasSections = !!sections && Object.keys(sections).length > 0;
    // Check if sections have actual content (not just empty strings)
    let sectionsWithContent = hasSections ? Object.values(sections).filter(c => c && c.trim().length > 0) : [];
    let hasValidContent = sectionsWithContent.length > 0;
    
    // If sections don't exist in state, check cache (similar to how content generation checks cache)
    if (!hasValidContent && outline && outline.length > 0) {
      try {
        const outlineIds = outline.map(s => String(s.id));
        const cachedContent = blogWriterCache.getCachedContent(outlineIds);
        if (cachedContent && Object.keys(cachedContent).length > 0) {
          sectionsWithContent = Object.values(cachedContent).filter(c => c && c.trim().length > 0);
          hasValidContent = sectionsWithContent.length > 0;
          if (hasValidContent) {
            debug.log('[BlogWriter] Using cached content for SEO analysis', { sections: Object.keys(cachedContent).length });
            // Update sections state with cached content
            setSections(cachedContent);
          }
        }
      } catch (e) {
        debug.log('[BlogWriter] Error checking cache for SEO analysis', e);
      }
    }
    
    const hasResearch = !!research && !!(research as any).keyword_analysis;
    
    if (!hasValidContent) {
      return "No blog content available for SEO analysis. Please generate content first. Content generation may still be in progress - please wait for it to complete.";
    }
    if (!hasResearch) return "Research data is required for SEO analysis. Please run research first.";
    // Prevent rapid re-opens
    const now = Date.now();
    if (isSEOAnalysisModalOpen && now - lastSEOModalOpenRef.current < 1000) {
      return "SEO analysis is already open.";
    }
    
    // Mark content phase as done when user clicks "Next: Run SEO Analysis"
    if (!contentConfirmed) {
      setContentConfirmed(true);
      debug.log('[BlogWriter] Content phase marked as done (SEO analysis triggered)');
    }
    
    setSeoRecommendationsApplied(false);
    if (!isSEOAnalysisModalOpen) {
      setIsSEOAnalysisModalOpen(true);
      lastSEOModalOpenRef.current = now;
      debug.log('[BlogWriter] SEO modal opened (direct)');
    }
    return "Running SEO analysis of your blog content. This will analyze content structure, keyword optimization, readability, and provide actionable recommendations.";
  }, [sections, research, outline, isSEOAnalysisModalOpen, contentConfirmed, setContentConfirmed, setSections]);

  const handleApplySeoRecommendations = useCallback(async (
    recommendations: BlogSEOActionableRecommendation[]
  ) => {
    if (!outline || outline.length === 0) {
      throw new Error('An outline is required before applying recommendations.');
    }

    const existingContentMap = buildExistingContentMap(sections || {});
    const emptyMap = new Map<string, string>();

    const sectionPayload = outline.map((section, index) => {
      const existingMatch = resolveContentForOutlineSection(
        section,
        index,
        [],
        emptyMap,
        emptyMap,
        existingContentMap
      );
      const payloadContentRaw = existingMatch.content ?? sections?.[section?.id] ?? '';
      const payloadContent = payloadContentRaw !== undefined && payloadContentRaw !== null ? String(payloadContentRaw) : '';
      const rawIdentifier = section?.id || section?.section_id || section?.sectionId || section?.sectionID || `section_${index + 1}`;
      const identifier = String(rawIdentifier).trim();

      return {
        id: identifier,
        heading: section.heading,
        content: payloadContent,
      };
    });

    const response = await blogWriterApi.applySeoRecommendations({
      title: selectedTitle || outline[0]?.heading || 'Untitled Blog',
      sections: sectionPayload,
      outline,
      research: (research as any) || {},
      recommendations,
    });

    if (!response.success) {
      throw new Error(response.error || 'Failed to apply recommendations.');
    }

    if (!response.sections || !Array.isArray(response.sections)) {
      throw new Error('Recommendation response did not include updated sections.');
    }

    const { byId: responseById, byHeading: responseByHeading } = buildResponseContentMaps(response.sections);

    const normalizedSections: Record<string, string> = {};
    const sectionKeysForCache: string[] = [];

    outline.forEach((section, index) => {
      const { content: resolvedContent, matchedKey } = resolveContentForOutlineSection(
        section,
        index,
        response.sections,
        responseById,
        responseByHeading,
        existingContentMap
      );

      const finalContent = (resolvedContent ?? '').trim();
      const contentToUse = finalContent || '';
      const primaryKey = getPrimaryKeyForOutlineSection(section, index);

      normalizedSections[primaryKey] = contentToUse;
      sectionKeysForCache.push(primaryKey);
    });

    const uniqueSectionKeys = Array.from(new Set(sectionKeysForCache));

    if (uniqueSectionKeys.length === 0) {
      throw new Error('No valid sections received from SEO recommendations application.');
    }

    const sectionsWithContent = Object.values(normalizedSections).filter(c => c && c.trim().length > 0);
    if (sectionsWithContent.length === 0) {
      throw new Error('SEO recommendations resulted in empty sections. Please try again.');
    }

    debug.log('[BlogWriter] Applied SEO recommendations: sections normalized', {
      sectionCount: uniqueSectionKeys.length,
      sectionsWithContent: sectionsWithContent.length,
      sectionKeys: uniqueSectionKeys,
      totalContentLength: Object.values(normalizedSections).reduce((sum, c) => sum + (c?.length || 0), 0)
    });

    setSections(normalizedSections);

    try {
      blogWriterCache.cacheContent(normalizedSections, uniqueSectionKeys);
    } catch (cacheError) {
      debug.log('[BlogWriter] Failed to cache SEO-applied content', cacheError);
    }

    // Force a delay to ensure React processes the state update before proceeding
    // This gives React time to re-render with new sections before phase navigation checks
    await new Promise(resolve => setTimeout(resolve, 200));

    setContinuityRefresh(Date.now());
    setFlowAnalysisCompleted(false);
    setFlowAnalysisResults(null);

    if (response.title && response.title !== selectedTitle) {
      setSelectedTitle(response.title);
    }

    if (response.applied) {
      setSeoAnalysis((prev: any) => prev ? { ...prev, applied_recommendations: response.applied } : prev);
      debug.log('[BlogWriter] SEO analysis state updated with applied recommendations');
    }

    // Mark recommendations as applied (this will trigger phase navigation check)
    // But we'll stay in SEO phase to show updated content
    setSeoRecommendationsApplied(true);
    debug.log('[BlogWriter] seoRecommendationsApplied set to true');

    // Ensure we stay in SEO phase to show updated content
    // Force navigation to SEO phase if we're not already there (safeguard)
    if (currentPhase !== 'seo') {
      navigateToPhase('seo');
      debug.log('[BlogWriter] Forced navigation to SEO phase after applying recommendations');
    } else {
      debug.log('[BlogWriter] Already in SEO phase, staying to show updated content');
    }
  }, [outline, research, sections, selectedTitle, setSections, setContinuityRefresh, setFlowAnalysisCompleted, setFlowAnalysisResults, setSelectedTitle, setSeoAnalysis, setSeoRecommendationsApplied, currentPhase, navigateToPhase]);

  // Handle SEO analysis completion
  const handleSEOAnalysisComplete = useCallback((analysis: any) => {
    setSeoAnalysis(analysis);
    debug.log('[BlogWriter] SEO analysis completed', { hasAnalysis: !!analysis });
  }, [setSeoAnalysis]);

  // Handle SEO modal close - mark SEO phase as done if not already marked
  const handleSEOModalClose = useCallback(() => {
    // Mark SEO phase as done when modal closes (even without applying recommendations)
    if (!seoAnalysis) {
      // Set a minimal valid seoAnalysis object to mark phase as complete
      setSeoAnalysis({
        success: true,
        overall_score: 0,
        category_scores: {},
        analysis_summary: {
          overall_grade: 'N/A',
          status: 'Skipped',
          strongest_category: 'N/A',
          weakest_category: 'N/A',
          key_strengths: [],
          key_weaknesses: [],
          ai_summary: 'SEO analysis was skipped by user'
        },
        actionable_recommendations: [],
        generated_at: new Date().toISOString()
      });
      debug.log('[BlogWriter] SEO phase marked as done (modal closed without analysis)');
    }
    setIsSEOAnalysisModalOpen(false);
    debug.log('[BlogWriter] SEO modal closed');
  }, [seoAnalysis, setSeoAnalysis]);

  // Mark SEO phase as completed when recommendations are applied
  useEffect(() => {
    if (seoRecommendationsApplied && seoAnalysis) {
      // SEO phase is considered complete when recommendations are applied
      // But stay in SEO phase to show updated content
      debug.log('[BlogWriter] SEO recommendations applied, SEO phase marked as complete');
      
      // Ensure we stay in SEO phase to show updated content (override auto-progression)
      if (currentPhase !== 'seo' && Object.keys(sections).length > 0) {
        navigateToPhase('seo');
        debug.log('[BlogWriter] Forced stay in SEO phase to show updated content');
      }
    }
  }, [seoRecommendationsApplied, seoAnalysis, currentPhase, sections, navigateToPhase]);

  const confirmBlogContent = useCallback(() => {
    debug.log('[BlogWriter] Blog content confirmed by user');
    setContentConfirmed(true);
    setSeoRecommendationsApplied(false);
    navigateToPhase('seo');
    setTimeout(() => {
      setIsSEOAnalysisModalOpen(true);
      debug.log('[BlogWriter] SEO modal opened (confirm→direct)');
    }, 0);
    return "✅ Blog content has been confirmed! Running SEO analysis now.";
  }, [setContentConfirmed, navigateToPhase]);

  return {
    isSEOAnalysisModalOpen,
    setIsSEOAnalysisModalOpen,
    isSEOMetadataModalOpen,
    setIsSEOMetadataModalOpen,
    seoRecommendationsApplied,
    setSeoRecommendationsApplied,
    lastSEOModalOpenRef,
    runSEOAnalysisDirect,
    handleApplySeoRecommendations,
    handleSEOAnalysisComplete,
    handleSEOModalClose,
    confirmBlogContent,
  };
};

export type SEOManagerReturn = ReturnType<typeof useSEOManager>;

