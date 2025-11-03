import { useState, useRef, useEffect, useCallback } from 'react';
import { debug } from '../../../utils/debug';
import { blogWriterApi, BlogSEOActionableRecommendation } from '../../../services/blogWriterApi';

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
    const hasResearch = !!research && !!(research as any).keyword_analysis;
    if (!hasSections) return "No blog content available for SEO analysis. Please generate content first.";
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
  }, [sections, research, isSEOAnalysisModalOpen, contentConfirmed, setContentConfirmed]);

  const handleApplySeoRecommendations = useCallback(async (
    recommendations: BlogSEOActionableRecommendation[]
  ) => {
    if (!outline || outline.length === 0) {
      throw new Error('An outline is required before applying recommendations.');
    }

    const sectionPayload = outline.map((section) => ({
      id: section.id,
      heading: section.heading,
      content: sections[section.id] ?? '',
    }));

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

    // Update sections - create new object reference to trigger React re-render
    const newSections: Record<string, string> = {};
    response.sections.forEach((section) => {
      if (section.id && section.content) {
        newSections[section.id] = section.content;
      }
    });
    
    // Validate we have sections before updating
    if (Object.keys(newSections).length === 0) {
      throw new Error('No valid sections received from SEO recommendations application.');
    }
    
    // Validate sections have actual content
    const sectionsWithContent = Object.values(newSections).filter(c => c && c.trim().length > 0);
    if (sectionsWithContent.length === 0) {
      throw new Error('SEO recommendations resulted in empty sections. Please try again.');
    }
    
    // Log detailed section info for debugging
    const sectionIds = Object.keys(newSections);
    const sectionSizes = sectionIds.map(id => ({ id, length: newSections[id]?.length || 0 }));
    debug.log('[BlogWriter] Applied SEO recommendations: sections updated', { 
      sectionCount: sectionIds.length,
      sectionsWithContent: sectionsWithContent.length,
      sectionIds: sectionIds,
      sectionSizes: sectionSizes,
      totalContentLength: Object.values(newSections).reduce((sum, c) => sum + (c?.length || 0), 0)
    });
    
    // Update sections state
    setSections(newSections);
    
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
  }, [outline, sections, selectedTitle, research, setSections, setSelectedTitle, setContinuityRefresh, setFlowAnalysisCompleted, setFlowAnalysisResults, setSeoAnalysis, currentPhase, navigateToPhase]);

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

