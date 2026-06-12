import { useState, useRef, useEffect, useCallback } from 'react';
import { debug } from '../../../utils/debug';
import { hashContent, getSeoCacheKey } from '../../../utils/contentHash';
import { blogWriterApi, BlogSEOActionableRecommendation } from '../../../services/blogWriterApi';
import { blogWriterCache } from '../../../services/blogWriterCache';
import { getSectionDiffs, DiffPreviewData } from '../../../utils/getSectionDiffs';

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
  introduction?: string;
  research: any;
  outline: any[];
  selectedTitle: string | null;
  selectedCompetitiveAdvantage?: string;
  contentConfirmed: boolean;
  seoAnalysis: any;
  currentPhase: string;
  navigateToPhase: (phase: string) => void;
  setContentConfirmed: (confirmed: boolean) => void;
  setSeoAnalysis: (analysis: any) => void;
  setSeoMetadata: (metadata: any) => void;
  setSections: (sections: Record<string, string>) => void;
  setSelectedTitle: (title: string | null) => void;
  setIntroduction: (intro: string) => void;
  setContinuityRefresh: (timestamp: number) => void;
  setFlowAnalysisCompleted: (completed: boolean) => void;
  setFlowAnalysisResults: (results: any) => void;
}

export const useSEOManager = ({
  sections,
  introduction,
  research,
  outline,
  selectedTitle,
  selectedCompetitiveAdvantage,
  contentConfirmed,
  seoAnalysis,
  currentPhase,
  navigateToPhase,
  setContentConfirmed,
  setSeoAnalysis,
  setSeoMetadata,
  setSections,
  setSelectedTitle,
  setIntroduction,
  setContinuityRefresh,
  setFlowAnalysisCompleted,
  setFlowAnalysisResults,
}: UseSEOManagerProps) => {
  const [isSEOAnalysisModalOpen, setIsSEOAnalysisModalOpen] = useState(false);
  const [isSEOMetadataModalOpen, setIsSEOMetadataModalOpen] = useState(false);
  const [seoRecommendationsApplied, setSeoRecommendationsApplied] = useState(false);
  const lastSEOModalOpenRef = useRef<number>(0);

  // Diff preview state
  const [isDiffModalOpen, setIsDiffModalOpen] = useState(false);
  const [diffPreviewData, setDiffPreviewData] = useState<DiffPreviewData | null>(null);
  const pendingSectionsRef = useRef<Record<string, string> | null>(null);
  const pendingSectionsKeysRef = useRef<string[] | null>(null);
  const pendingIntroductionRef = useRef<string | null>(null);
  const pendingTitleRef = useRef<string | null>(null);
  const pendingAppliedRef = useRef<any>(null);
  const originalSectionsRef = useRef<Record<string, string> | null>(null);
  const originalIntroductionRef = useRef<string | null>(null);

  // Restore cached SEO analysis only when user is on/past the SEO phase
  useEffect(() => {
    // Don't run SEO cache lookups on research or outline phases
    if (currentPhase !== 'seo' && currentPhase !== 'publish') return;

    const restoreCachedSEO = async () => {
      if (seoAnalysis) return;

      const title = selectedTitle || '';
      if (!title && (!outline || outline.length === 0)) return;

      const fullMarkdown = (outline || []).map(s => `## ${s.heading}\n\n${(sections || {})[s.id] || ''}`).join('\n\n');
      if (!fullMarkdown && !title) return;

      try {
        const hash = await hashContent(`${title}\n${fullMarkdown}`);
        const cacheKey = getSeoCacheKey(hash, title);
        const cached = window.localStorage.getItem(cacheKey);
        if (cached) {
          const parsed = JSON.parse(cached);
          if (parsed && typeof parsed.overall_score === 'number' && parsed.category_scores) {
            debug.log('[SEOManager] Restored cached SEO analysis', { score: parsed.overall_score });
            setSeoAnalysis(parsed);
          }
        }
      } catch (e) {
        debug.log('[SEOManager] Failed to restore cached SEO analysis', e);
      }
    };

    restoreCachedSEO();

    try {
      const wasApplied = localStorage.getItem('blog_seo_recommendations_applied') === 'true';
      if (wasApplied) {
        setSeoRecommendationsApplied(true);
      }
    } catch {}
  }, [currentPhase, selectedTitle, sections, outline, seoAnalysis, setSeoAnalysis, setSeoRecommendationsApplied]);

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
    
    console.debug('[SEODirect] runSEOAnalysisDirect', { hasSections, hasValidContent, hasResearch, sectionKeys: Object.keys(sections), outlineLen: outline?.length, isModalOpen: isSEOAnalysisModalOpen, contentConfirmed });
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

    // Capture originals before API call for diff preview
    originalSectionsRef.current = { ...(sections || {}) };
    originalIntroductionRef.current = introduction || '';

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
      introduction: introduction || undefined,
      sections: sectionPayload,
      outline,
      research: (research as any) || {},
      recommendations,
      competitive_advantage: selectedCompetitiveAdvantage || undefined,
    });

    if (!response.success) {
      throw new Error(response.error || 'Failed to apply recommendations.');
    }

    if (!response.sections || !Array.isArray(response.sections)) {
      throw new Error('Recommendation response did not include updated sections.');
    }

    if (response.sections.length !== outline.length) {
      debug.log('[BlogWriter] WARNING: API returned different section count', {
        apiCount: response.sections.length,
        outlineCount: outline.length,
      });
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

    debug.log('[BlogWriter] handleApplySeoRecommendations: computed diffs, showing preview', {
      keys: Object.keys(normalizedSections),
    });

    // Store pending changes (don't apply yet)
    pendingSectionsRef.current = normalizedSections;
    pendingSectionsKeysRef.current = uniqueSectionKeys;
    pendingIntroductionRef.current = response.introduction ?? null;
    pendingTitleRef.current = response.title ?? null;
    pendingAppliedRef.current = response.applied ?? null;

    // Build diff data from originals vs pending
    const outlineHeadings = outline.map((s: any) => ({ id: getPrimaryKeyForOutlineSection(s, outline.indexOf(s)), heading: s.heading || s.title || `Section ${outline.indexOf(s) + 1}` }));
    const diffData = getSectionDiffs(
      outlineHeadings,
      originalSectionsRef.current,
      normalizedSections,
      originalIntroductionRef.current || undefined,
      response.introduction || undefined
    );
    setDiffPreviewData(diffData);
    setIsDiffModalOpen(true);

    // Cache the pending content
    try {
      blogWriterCache.cacheContent(normalizedSections, uniqueSectionKeys);
    } catch (cacheError) {
      debug.log('[BlogWriter] Failed to cache SEO-applied content', cacheError);
    }
  }, [outline, research, sections, introduction, selectedTitle, selectedCompetitiveAdvantage, setSections]);

  const acceptDiffChanges = useCallback(() => {
    const normalizedSections = pendingSectionsRef.current;
    const uniqueSectionKeys = pendingSectionsKeysRef.current;
    if (!normalizedSections || !uniqueSectionKeys) {
      debug.log('[BlogWriter] acceptDiffChanges: no pending changes to apply');
      return;
    }

    debug.log('[BlogWriter] Accepting diff changes, applying sections', {
      keys: Object.keys(normalizedSections),
    });

    setSections(normalizedSections);
    setContinuityRefresh(Date.now());
    setFlowAnalysisCompleted(false);
    setFlowAnalysisResults(null);

    const pendingIntro = pendingIntroductionRef.current;
    if (pendingIntro !== null && pendingIntro !== introduction) {
      setIntroduction(pendingIntro);
      debug.log('[BlogWriter] Introduction updated from SEO response', {
        length: pendingIntro.length,
        preview: pendingIntro.substring(0, 80),
      });
    }

    const pendingTitle = pendingTitleRef.current;
    if (pendingTitle && pendingTitle !== selectedTitle) {
      setSelectedTitle(pendingTitle);
    }

    if (pendingAppliedRef.current) {
      setSeoAnalysis((prev: any) => prev ? { ...prev, applied_recommendations: pendingAppliedRef.current } : prev);
      debug.log('[BlogWriter] SEO analysis state updated with applied recommendations');
    }

    setSeoRecommendationsApplied(true);
    try {
      localStorage.setItem('blog_seo_recommendations_applied', 'true');
    } catch {}
    debug.log('[BlogWriter] seoRecommendationsApplied set to true');

    if (currentPhase !== 'seo') {
      navigateToPhase('seo');
      debug.log('[BlogWriter] Forced navigation to SEO phase after accepting changes');
    } else {
      debug.log('[BlogWriter] Already in SEO phase, staying to show updated content');
    }

    // Clean up pending and close
    pendingSectionsRef.current = null;
    pendingSectionsKeysRef.current = null;
    pendingIntroductionRef.current = null;
    pendingTitleRef.current = null;
    pendingAppliedRef.current = null;
    originalSectionsRef.current = null;
    originalIntroductionRef.current = null;
    setIsDiffModalOpen(false);
    setDiffPreviewData(null);
  }, [setSections, setContinuityRefresh, setFlowAnalysisCompleted, setFlowAnalysisResults, setIntroduction, introduction, setSelectedTitle, selectedTitle, setSeoAnalysis, setSeoRecommendationsApplied, currentPhase, navigateToPhase]);

  const rejectDiffChanges = useCallback(() => {
    debug.log('[BlogWriter] Rejecting diff changes, discarding pending content');

    // Clean up pending without applying
    pendingSectionsRef.current = null;
    pendingSectionsKeysRef.current = null;
    pendingIntroductionRef.current = null;
    pendingTitleRef.current = null;
    pendingAppliedRef.current = null;
    originalSectionsRef.current = null;
    originalIntroductionRef.current = null;
    setIsDiffModalOpen(false);
    setDiffPreviewData(null);
  }, []);

  const acceptSelectedDiffChanges = useCallback((
    selectedIds: Record<string, boolean>,
    acceptIntro: boolean
  ) => {
    const pendingSections = pendingSectionsRef.current;
    const originalSections = originalSectionsRef.current;
    const uniqueSectionKeys = pendingSectionsKeysRef.current;

    if (!pendingSections || !originalSections || !uniqueSectionKeys) {
      debug.log('[BlogWriter] acceptSelectedDiffChanges: no pending changes to apply');
      return;
    }

    // Merge: selected sections use pending content, unselected use original
    const mergedSections: Record<string, string> = {};
    const allKeys = new Set([...Object.keys(pendingSections), ...Object.keys(originalSections)]);
    allKeys.forEach(key => {
      if (selectedIds[key]) {
        mergedSections[key] = pendingSections[key] || originalSections[key] || '';
      } else {
        mergedSections[key] = originalSections[key] || pendingSections[key] || '';
      }
    });

    const mergedKeys = Object.keys(mergedSections);
    debug.log('[BlogWriter] Accepting selected diff changes', {
      selected: Object.entries(selectedIds).filter(([, v]) => v).length,
      totalSections: mergedKeys.length,
    });

    setSections(mergedSections);
    setContinuityRefresh(Date.now());
    setFlowAnalysisCompleted(false);
    setFlowAnalysisResults(null);

    // Introduction: only apply if acceptIntro is true
    const pendingIntro = pendingIntroductionRef.current;
    if (acceptIntro && pendingIntro !== null && pendingIntro !== introduction) {
      setIntroduction(pendingIntro);
      debug.log('[BlogWriter] Introduction updated from selected SEO response', {
        length: pendingIntro.length,
      });
    }

    // Title: always apply if changed (not per-section granularity)
    const pendingTitle = pendingTitleRef.current;
    if (pendingTitle && pendingTitle !== selectedTitle) {
      setSelectedTitle(pendingTitle);
    }

    if (pendingAppliedRef.current) {
      setSeoAnalysis((prev: any) => prev ? { ...prev, applied_recommendations: pendingAppliedRef.current } : prev);
    }

    setSeoRecommendationsApplied(true);
    try {
      localStorage.setItem('blog_seo_recommendations_applied', 'true');
    } catch {}

    if (currentPhase !== 'seo') {
      navigateToPhase('seo');
    }

    // Clean up pending and close
    pendingSectionsRef.current = null;
    pendingSectionsKeysRef.current = null;
    pendingIntroductionRef.current = null;
    pendingTitleRef.current = null;
    pendingAppliedRef.current = null;
    originalSectionsRef.current = null;
    originalIntroductionRef.current = null;
    setIsDiffModalOpen(false);
    setDiffPreviewData(null);

    try {
      blogWriterCache.cacheContent(mergedSections, mergedKeys);
    } catch (cacheError) {
      debug.log('[BlogWriter] Failed to cache selected SEO content', cacheError);
    }
  }, [setSections, setContinuityRefresh, setFlowAnalysisCompleted, setFlowAnalysisResults, setIntroduction, introduction, setSelectedTitle, selectedTitle, setSeoAnalysis, setSeoRecommendationsApplied, currentPhase, navigateToPhase]);

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
    // Only auto-navigate to SEO if user is already on/past the SEO phase
    if (seoRecommendationsApplied && seoAnalysis && (currentPhase === 'seo' || currentPhase === 'publish')) {
      debug.log('[BlogWriter] SEO recommendations applied, SEO phase marked as complete');
    }
  }, [seoRecommendationsApplied, seoAnalysis, currentPhase]);

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
    isDiffModalOpen,
    diffPreviewData,
    acceptDiffChanges,
    rejectDiffChanges,
    acceptSelectedDiffChanges,
  };
};

export type SEOManagerReturn = ReturnType<typeof useSEOManager>;

