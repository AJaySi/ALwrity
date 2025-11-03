import { useCallback } from 'react';
import { debug } from '../../../utils/debug';
import { mediumBlogApi } from '../../../services/blogWriterApi';
import { researchCache } from '../../../services/researchCache';
import { blogWriterCache } from '../../../services/blogWriterCache';

interface UsePhaseActionHandlersProps {
  research: any;
  outline: any[];
  selectedTitle: string | null;
  contentConfirmed: boolean;
  sections: Record<string, string>;
  navigateToPhase: (phase: string) => void;
  handleOutlineConfirmed: () => void;
  setIsMediumGenerationStarting: (starting: boolean) => void;
  mediumPolling: any;
  outlineGenRef: React.RefObject<any>;
  setOutline: (outline: any[]) => void;
  setContentConfirmed: (confirmed: boolean) => void;
  setIsSEOMetadataModalOpen: (open: boolean) => void;
  runSEOAnalysisDirect: () => string;
  onOutlineComplete?: (outline: any) => void;
  onContentComplete?: (sections: Record<string, string>) => void;
}

export const usePhaseActionHandlers = ({
  research,
  outline,
  selectedTitle,
  contentConfirmed,
  sections,
  navigateToPhase,
  handleOutlineConfirmed,
  setIsMediumGenerationStarting,
  mediumPolling,
  outlineGenRef,
  setOutline,
  setContentConfirmed,
  setIsSEOMetadataModalOpen,
  runSEOAnalysisDirect,
  onOutlineComplete,
  onContentComplete,
}: UsePhaseActionHandlersProps) => {
  const handleResearchAction = useCallback(() => {
    navigateToPhase('research');
    debug.log('[BlogWriter] Research action triggered - navigating to research phase');
    // Note: Research caching is handled by ManualResearchForm component
  }, [navigateToPhase]);

  const handleOutlineAction = useCallback(async () => {
    if (!research) {
      alert('Please complete research first before generating an outline.');
      return;
    }
    
    // Check cache first (shared utility)
    const researchKeywords = research.original_keywords || research.keyword_analysis?.primary || [];
    const cachedOutline = blogWriterCache.getCachedOutline(researchKeywords);
    
    if (cachedOutline) {
      debug.log('[BlogWriter] Using cached outline from localStorage', { sections: cachedOutline.outline.length });
      setOutline(cachedOutline.outline);
      if (onOutlineComplete) {
        onOutlineComplete({ outline: cachedOutline.outline, title_options: cachedOutline.title_options });
      }
      navigateToPhase('outline');
      return;
    }
    
    navigateToPhase('outline');
    if (outlineGenRef.current) {
      try {
        const result = await outlineGenRef.current.generateNow();
        if (!result.success) {
          alert(result.message || 'Failed to generate outline');
        }
      } catch (error) {
        console.error('Outline generation failed:', error);
        alert(`Outline generation failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }
    }
    debug.log('[BlogWriter] Outline action triggered');
  }, [research, navigateToPhase, outlineGenRef, setOutline, onOutlineComplete]);

  const handleContentAction = useCallback(async () => {
    if (!outline || outline.length === 0) {
      alert('Please generate and confirm an outline first.');
      return;
    }
    if (!research) {
      alert('Research data is required for content generation.');
      return;
    }
    navigateToPhase('content');
    
    // Confirm outline first
    handleOutlineConfirmed();
    
    // Check cache first (shared utility)
    const outlineIds = outline.map(s => String(s.id));
    const cachedContent = blogWriterCache.getCachedContent(outlineIds);
    
    if (cachedContent) {
      debug.log('[BlogWriter] Using cached content from localStorage', { sections: Object.keys(cachedContent).length });
      if (onContentComplete) {
        onContentComplete(cachedContent);
      }
      return;
    }
    
    // Also check if sections already exist in current state (shared utility)
    if (blogWriterCache.contentExistsInState(sections || {}, outlineIds)) {
      debug.log('[BlogWriter] Content already exists in state, skipping generation', { sections: Object.keys(sections || {}).length });
      return;
    }
    
    // If short/medium blog (<=1000 words), trigger content generation automatically
    const target = Number(
      research?.keyword_analysis?.blog_length || 
      (research as any)?.word_count_target || 
      localStorage.getItem('blog_length_target') || 
      0
    );
    
    if (target && target <= 1000) {
      try {
        setIsMediumGenerationStarting(true);
        const payload = {
          title: selectedTitle || (typeof window !== 'undefined' ? localStorage.getItem('blog_selected_title') : '') || outline[0]?.heading || 'Untitled',
          sections: outline.map(s => ({
            id: s.id,
            heading: s.heading,
            keyPoints: s.key_points,
            subheadings: s.subheadings,
            keywords: s.keywords,
            targetWords: s.target_words,
            references: s.references,
          })),
          globalTargetWords: target,
          researchKeywords: research.original_keywords || research.keyword_analysis?.primary || [],
        };

        const { task_id } = await mediumBlogApi.startMediumGeneration(payload as any);
        setIsMediumGenerationStarting(false);
        mediumPolling.startPolling(task_id);
        debug.log('[BlogWriter] Content action triggered - medium generation started', { task_id });
      } catch (error) {
        console.error('Content generation failed:', error);
        setIsMediumGenerationStarting(false);
        alert(`Content generation failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }
    } else {
      // For longer blogs, just confirm outline - user will use manual button
      debug.log('[BlogWriter] Content action triggered - outline confirmed (manual content generation required)');
    }
  }, [outline, research, selectedTitle, sections, navigateToPhase, handleOutlineConfirmed, setIsMediumGenerationStarting, mediumPolling, onContentComplete]);

  const handleSEOAction = useCallback(() => {
    if (!contentConfirmed) {
      // Mark content as confirmed when SEO action is clicked
      setContentConfirmed(true);
    }
    navigateToPhase('seo');
    runSEOAnalysisDirect();
    debug.log('[BlogWriter] SEO action triggered');
  }, [contentConfirmed, setContentConfirmed, navigateToPhase, runSEOAnalysisDirect]);

  const handlePublishAction = useCallback(() => {
    navigateToPhase('publish');
    setIsSEOMetadataModalOpen(true);
    debug.log('[BlogWriter] Publish action triggered - opening SEO metadata modal');
  }, [navigateToPhase, setIsSEOMetadataModalOpen]);

  return {
    handleResearchAction,
    handleOutlineAction,
    handleContentAction,
    handleSEOAction,
    handlePublishAction,
  };
};

