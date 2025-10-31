import React, { useState, useEffect, useRef, useCallback } from 'react';
import { debug } from '../../utils/debug';
import { CopilotSidebar } from '@copilotkit/react-ui';
import { useCopilotChatHeadless_c } from '@copilotkit/react-core';
import { useCopilotAction } from '@copilotkit/react-core';
import '@copilotkit/react-ui/styles.css';
import WriterCopilotSidebar from './BlogWriterUtils/WriterCopilotSidebar';
import { blogWriterApi, BlogSEOActionableRecommendation } from '../../services/blogWriterApi';
import { useOutlinePolling, useMediumGenerationPolling, useResearchPolling, useRewritePolling } from '../../hooks/usePolling';
import { useClaimFixer } from '../../hooks/useClaimFixer';
import { useMarkdownProcessor } from '../../hooks/useMarkdownProcessor';
import { useBlogWriterState } from '../../hooks/useBlogWriterState';
import { useSuggestions } from './SuggestionsGenerator';
import EnhancedOutlineEditor from './EnhancedOutlineEditor';
import ContinuityBadge from './ContinuityBadge';
import EnhancedTitleSelector from './EnhancedTitleSelector';
import SEOMiniPanel from './SEOMiniPanel';
import ResearchResults from './ResearchResults';
import KeywordInputForm from './KeywordInputForm';
import ResearchAction from './ResearchAction';
import { CustomOutlineForm } from './CustomOutlineForm';
import { ResearchDataActions } from './ResearchDataActions';
import { EnhancedOutlineActions } from './EnhancedOutlineActions';
import HallucinationChecker from './HallucinationChecker';
import { RewriteFeedbackForm } from './RewriteFeedbackForm';
import Publisher from './Publisher';
import OutlineGenerator from './OutlineGenerator';
import OutlineRefiner from './OutlineRefiner';
import { SEOProcessor } from './SEO';
import BlogWriterLanding from './BlogWriterLanding';
import { OutlineProgressModal } from './OutlineProgressModal';
import TaskProgressModals from './BlogWriterUtils/TaskProgressModals';
import OutlineFeedbackForm from './OutlineFeedbackForm';
import { BlogEditor } from './WYSIWYG';
import { SEOAnalysisModal } from './SEOAnalysisModal';
import { SEOMetadataModal } from './SEOMetadataModal';
import PhaseNavigation from './PhaseNavigation';
import { usePhaseNavigation } from '../../hooks/usePhaseNavigation';
import HeaderBar from './BlogWriterUtils/HeaderBar';
import PhaseContent from './BlogWriterUtils/PhaseContent';
import useBlogWriterCopilotActions from './BlogWriterUtils/useBlogWriterCopilotActions';

// Type assertion for CopilotKit action
const useCopilotActionTyped = useCopilotAction as any;

export const BlogWriter: React.FC = () => {
  // Use custom hook for all state management
  const {
    research,
    outline,
    titleOptions,
    selectedTitle,
    sections,
    seoAnalysis,
    genMode,
    seoMetadata,
    continuityRefresh,
    outlineTaskId,
    sourceMappingStats,
    groundingInsights,
    optimizationResults,
    researchCoverage,
    researchTitles,
    aiGeneratedTitles,
    outlineConfirmed,
    contentConfirmed,
    flowAnalysisCompleted,
    flowAnalysisResults,
    setOutline,
    setTitleOptions,
    setSelectedTitle,
    setSections,
    setSeoAnalysis,
    setGenMode,
    setSeoMetadata,
    setContinuityRefresh,
    setOutlineTaskId,
    setContentConfirmed,
    setFlowAnalysisCompleted,
    setFlowAnalysisResults,
    handleResearchComplete,
    handleOutlineComplete,
    handleOutlineError,
    handleTitleSelect,
    handleCustomTitle,
    handleOutlineConfirmed,
    handleOutlineRefined,
    handleContentUpdate,
    handleContentSave
  } = useBlogWriterState();

  const [isSEOAnalysisModalOpen, setIsSEOAnalysisModalOpen] = useState(false);
  const [isSEOMetadataModalOpen, setIsSEOMetadataModalOpen] = useState(false);
  const [seoRecommendationsApplied, setSeoRecommendationsApplied] = useState(false);
  const lastSEOModalOpenRef = useRef<number>(0);

  // Phase navigation hook
  const {
    phases,
    currentPhase,
    navigateToPhase,
    resetUserSelection
  } = usePhaseNavigation(
    research,
    outline,
    outlineConfirmed,
    Object.keys(sections).length > 0,
    contentConfirmed,
    seoAnalysis,
    seoMetadata,
    seoRecommendationsApplied
  );

  // Helper: run same checks as analyzeSEO and open modal
  const runSEOAnalysisDirect = (): string => {
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
  };

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
      setSeoAnalysis(prev => prev ? { ...prev, applied_recommendations: response.applied } : prev);
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
  }, [seoAnalysis, setSeoAnalysis, setIsSEOAnalysisModalOpen]);

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

  // Track when outlines/content become available for the first time
  const prevOutlineLenRef = useRef<number>(outline.length);
  const prevOutlineConfirmedRef = useRef<boolean>(outlineConfirmed);
  const prevContentConfirmedRef = useRef<boolean>(contentConfirmed);
  
  useEffect(() => {
    const prevLen = prevOutlineLenRef.current;
    if (research && prevLen === 0 && outline.length > 0) {
      resetUserSelection();
    }
    prevOutlineLenRef.current = outline.length;
  }, [research, outline.length, resetUserSelection]);

  // Only reset user selection when transitioning from not-confirmed to confirmed
  useEffect(() => {
    const wasConfirmed = prevOutlineConfirmedRef.current;
    if (!wasConfirmed && outlineConfirmed && Object.keys(sections).length > 0) {
      resetUserSelection(); // Allow auto-progression to content phase
    }
    prevOutlineConfirmedRef.current = outlineConfirmed;
  }, [outlineConfirmed, sections, resetUserSelection]);

  useEffect(() => {
    const wasConfirmed = prevContentConfirmedRef.current;
    if (!wasConfirmed && contentConfirmed && seoAnalysis) {
      resetUserSelection(); // Allow auto-progression to SEO phase
    }
    prevContentConfirmedRef.current = contentConfirmed;
  }, [contentConfirmed, seoAnalysis, resetUserSelection]);

  // Custom hooks for complex functionality
  const { buildFullMarkdown, buildUpdatedMarkdownForClaim, applyClaimFix } = useClaimFixer(
    outline,
    sections,
    setSections
  );
  
  const { convertMarkdownToHTML } = useMarkdownProcessor(
    outline,
    sections
  );

  // Research polling hook (for context awareness)
  const researchPolling = useResearchPolling({
    onComplete: handleResearchComplete,
    onError: (error) => console.error('Research polling error:', error)
  });

  // Outline polling hook
  const outlinePolling = useOutlinePolling({
    onComplete: handleOutlineComplete,
    onError: handleOutlineError
  });

  // Medium generation polling (used after confirm if short blog)
  const mediumPolling = useMediumGenerationPolling({
    onComplete: (result: any) => {
      try {
        if (result && result.sections) {
          const newSections: Record<string, string> = {};
          result.sections.forEach((s: any) => {
            newSections[String(s.id)] = s.content || '';
          });
          setSections(newSections);
        }
      } catch (e) {
        console.error('Failed to apply medium generation result:', e);
      }
    },
    onError: (err) => console.error('Medium generation failed:', err)
  });

  // Rewrite polling hook (used for blog rewrite operations)
  const rewritePolling = useRewritePolling({
    onComplete: (result: any) => {
      try {
        if (result && result.sections) {
          const newSections: Record<string, string> = {};
          result.sections.forEach((s: any) => {
            newSections[String(s.id)] = s.content || '';
          });
          setSections(newSections);
        }
      } catch (e) {
        console.error('Failed to apply rewrite result:', e);
      }
    },
    onError: (err) => console.error('Rewrite failed:', err)
  });

  // Add minimum display time for modal
  const [showModal, setShowModal] = useState(false);
  const [modalStartTime, setModalStartTime] = useState<number | null>(null);
  const [isMediumGenerationStarting, setIsMediumGenerationStarting] = useState(false);
  const [showOutlineModal, setShowOutlineModal] = useState(false);
  
  const suggestions = useSuggestions({
    research,
    outline,
    outlineConfirmed,
    researchPolling: { isPolling: researchPolling.isPolling, currentStatus: researchPolling.currentStatus },
    outlinePolling: { isPolling: outlinePolling.isPolling, currentStatus: outlinePolling.currentStatus },
    mediumPolling: { isPolling: mediumPolling.isPolling, currentStatus: mediumPolling.currentStatus },
    hasContent: Object.keys(sections).length > 0,
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

  const suggestionsPayload = React.useMemo(
    () => (Array.isArray(suggestions) ? suggestions.map((s: any) => ({ title: s.title, message: s.message })) : []),
    [suggestions]
  );
  const prevSuggestionsRef = useRef<string>("__init__");
  const suggestionsJson = React.useMemo(() => JSON.stringify(suggestionsPayload), [suggestionsPayload]);
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

  const handlePhaseClick = useCallback((phaseId: string) => {
    navigateToPhase(phaseId);
    if (phaseId === 'seo') {
      if (seoAnalysis) {
        setIsSEOAnalysisModalOpen(true);
        debug.log('[BlogWriter] SEO modal opened (phase navigation)');
      } else {
        runSEOAnalysisDirect();
      }
    }
  }, [navigateToPhase, seoAnalysis, runSEOAnalysisDirect]);
  const outlineGenRef = useRef<any>(null);

  useEffect(() => {
    if ((mediumPolling.isPolling || rewritePolling.isPolling || isMediumGenerationStarting) && !showModal) {
      setShowModal(true);
      setModalStartTime(Date.now());
    } else if (!mediumPolling.isPolling && !rewritePolling.isPolling && !isMediumGenerationStarting && showModal) {
      const elapsed = Date.now() - (modalStartTime || 0);
      const minDisplayTime = 2000; // 2 seconds minimum
      
      if (elapsed < minDisplayTime) {
        setTimeout(() => {
          setShowModal(false);
          setModalStartTime(null);
        }, minDisplayTime - elapsed);
      } else {
        setShowModal(false);
        setModalStartTime(null);
      }
    }
  }, [mediumPolling.isPolling, rewritePolling.isPolling, isMediumGenerationStarting, showModal, modalStartTime]);

  // Handle outline modal visibility
  useEffect(() => {
    if (outlinePolling.isPolling && !showOutlineModal) {
      setShowOutlineModal(true);
    } else if (!outlinePolling.isPolling && showOutlineModal) {
      // Add a small delay to ensure user sees completion message
      setTimeout(() => {
        setShowOutlineModal(false);
      }, 1000);
    }
  }, [outlinePolling.isPolling, showOutlineModal]);

  // Handle medium generation start from OutlineFeedbackForm
  const handleMediumGenerationStarted = (taskId: string) => {
    console.log('Starting medium generation polling for task:', taskId);
    setIsMediumGenerationStarting(false); // Clear the starting state
    mediumPolling.startPolling(taskId);
  };

  // Show modal immediately when copilot action is triggered
  const handleMediumGenerationTriggered = () => {
    console.log('Medium generation triggered - showing modal immediately');
    setIsMediumGenerationStarting(true);
  };

  // Debug medium polling state
  console.log('Medium polling state:', {
    isPolling: mediumPolling.isPolling,
    status: mediumPolling.currentStatus,
    progressCount: mediumPolling.progressMessages.length
  });

  // Log critical state changes only (reduce noise)
  const lastPhaseRef = useRef<string>('');
  const lastSeoOpenRef = useRef<boolean>(false);
  const lastSectionsLenRef = useRef<number>(0);

  useEffect(() => {
    if (currentPhase !== lastPhaseRef.current) {
      debug.log('[BlogWriter] Phase changed', { currentPhase });
      lastPhaseRef.current = currentPhase;
    }
  }, [currentPhase]);

  useEffect(() => {
    const open = isSEOAnalysisModalOpen;
    if (open !== lastSeoOpenRef.current) {
      debug.log('[BlogWriter] SEO modal', { isOpen: open });
      lastSeoOpenRef.current = open;
    }
  }, [isSEOAnalysisModalOpen]);

  useEffect(() => {
    const len = Object.keys(sections || {}).length;
    if (len !== lastSectionsLenRef.current) {
      debug.log('[BlogWriter] Sections updated', { count: len });
      lastSectionsLenRef.current = len;
    }
  }, [sections]);

  useEffect(() => {
    debug.log('[BlogWriter] Suggestions updated', { suggestions });
  }, [suggestions]);

  // Force-sync Copilot suggestions right after SEO recommendations applied (guarded by previous suggestions key)
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

  const confirmBlogContentCb = useCallback(() => {
    debug.log('[BlogWriter] Blog content confirmed by user');
    setContentConfirmed(true);
    resetUserSelection();
    setSeoRecommendationsApplied(false);
    navigateToPhase('seo');
    setTimeout(() => {
      setIsSEOAnalysisModalOpen(true);
      debug.log('[BlogWriter] SEO modal opened (confirm→direct)');
    }, 0);
    return "✅ Blog content has been confirmed! Running SEO analysis now.";
  }, [setContentConfirmed, resetUserSelection, navigateToPhase, setIsSEOAnalysisModalOpen]);

  useBlogWriterCopilotActions({
    isSEOAnalysisModalOpen,
    lastSEOModalOpenRef,
    runSEOAnalysisDirect,
    confirmBlogContent: confirmBlogContentCb,
    sections,
    research,
    openSEOMetadata: () => setIsSEOMetadataModalOpen(true),
  });





  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Extracted Components */}
      <KeywordInputForm 
        onResearchComplete={handleResearchComplete}
        onTaskStart={(taskId) => researchPolling.startPolling(taskId)}
      />
      <CustomOutlineForm onOutlineCreated={setOutline} />
      <ResearchAction onResearchComplete={handleResearchComplete} />
      <ResearchDataActions 
        research={research} 
        onOutlineCreated={setOutline} 
        onTitleOptionsSet={setTitleOptions} 
      />
      <EnhancedOutlineActions 
        outline={outline} 
        onOutlineUpdated={setOutline} 
      />
      <OutlineFeedbackForm 
        outline={outline} 
        research={research!} 
        onOutlineConfirmed={handleOutlineConfirmed}
        onOutlineRefined={handleOutlineRefined}
        onMediumGenerationStarted={handleMediumGenerationStarted}
        onMediumGenerationTriggered={handleMediumGenerationTriggered}
        sections={sections}
        blogTitle={selectedTitle}
        onFlowAnalysisComplete={(analysis) => {
          console.log('Flow analysis completed:', analysis);
          setFlowAnalysisCompleted(true);
          setFlowAnalysisResults(analysis);
          // Trigger a refresh of continuity badges
          setContinuityRefresh((prev: number) => (prev || 0) + 1);
        }}
      />
      
      {/* Rewrite Feedback Form - Only show when content exists */}
      {Object.keys(sections).length > 0 && (
        <RewriteFeedbackForm
          research={research!}
          outline={outline}
          sections={sections}
          blogTitle={selectedTitle}
          onRewriteStarted={(taskId) => {
            console.log('Starting rewrite polling for task:', taskId);
            rewritePolling.startPolling(taskId);
          }}
          onRewriteTriggered={() => {
            console.log('Rewrite triggered - showing modal immediately');
            setIsMediumGenerationStarting(true);
          }}
        />
      )}
      
      {/* New extracted functionality components */}
      <OutlineGenerator
        ref={outlineGenRef}
        research={research}
        onTaskStart={(taskId) => setOutlineTaskId(taskId)}
        onPollingStart={(taskId) => outlinePolling.startPolling(taskId)}
        onModalShow={() => setShowOutlineModal(true)}
      />
      <OutlineRefiner
        outline={outline}
        onOutlineUpdated={setOutline}
      />
      <SEOProcessor
        buildFullMarkdown={buildFullMarkdown}
        seoMetadata={seoMetadata}
        onSEOAnalysis={setSeoAnalysis}
        onSEOMetadata={setSeoMetadata}
      />
      <HallucinationChecker
        buildFullMarkdown={buildFullMarkdown}
        buildUpdatedMarkdownForClaim={buildUpdatedMarkdownForClaim}
        applyClaimFix={applyClaimFix}
      />
      <Publisher
        buildFullMarkdown={buildFullMarkdown}
        convertMarkdownToHTML={convertMarkdownToHTML}
        seoMetadata={seoMetadata}
      />
      
      {!research ? (
        <BlogWriterLanding 
          onStartWriting={() => {
            // Trigger the copilot to start the research process
          }}
        />
      ) : (
        <>
      <HeaderBar
        phases={phases}
        currentPhase={currentPhase}
        onPhaseClick={handlePhaseClick}
      />
      <PhaseContent
        currentPhase={currentPhase}
        research={research}
        outline={outline}
        outlineConfirmed={outlineConfirmed}
        titleOptions={titleOptions}
        selectedTitle={selectedTitle}
        researchTitles={researchTitles}
        aiGeneratedTitles={aiGeneratedTitles}
        sourceMappingStats={sourceMappingStats}
        groundingInsights={groundingInsights}
        optimizationResults={optimizationResults}
        researchCoverage={researchCoverage}
        setOutline={setOutline}
        sections={sections}
        handleContentUpdate={handleContentUpdate}
        handleContentSave={handleContentSave}
        continuityRefresh={continuityRefresh}
        flowAnalysisResults={flowAnalysisResults}
        outlineGenRef={outlineGenRef}
        blogWriterApi={blogWriterApi}
        contentConfirmed={contentConfirmed}
        seoAnalysis={seoAnalysis}
        seoMetadata={seoMetadata}
        onTitleSelect={handleTitleSelect}
        onCustomTitle={handleCustomTitle}
      />
        </>
      )}

      <WriterCopilotSidebar
        suggestions={suggestions}
        research={research}
        outline={outline}
        outlineConfirmed={outlineConfirmed}
      />
      
      <TaskProgressModals
        showOutlineModal={showOutlineModal}
        outlinePolling={outlinePolling}
        showModal={showModal}
        rewritePolling={rewritePolling}
        mediumPolling={mediumPolling}
      />

      {/* SEO Analysis Modal */}
      <SEOAnalysisModal
        isOpen={isSEOAnalysisModalOpen}
        onClose={handleSEOModalClose}
        blogContent={buildFullMarkdown()}
        blogTitle={selectedTitle}
        researchData={research}
        onApplyRecommendations={handleApplySeoRecommendations}
        onAnalysisComplete={handleSEOAnalysisComplete}
      />

      {/* SEO Metadata Modal */}
      <SEOMetadataModal
        isOpen={isSEOMetadataModalOpen}
        onClose={() => setIsSEOMetadataModalOpen(false)}
        blogContent={buildFullMarkdown()}
        blogTitle={selectedTitle}
        researchData={research}
        outline={outline}
        seoAnalysis={seoAnalysis}
        onMetadataGenerated={(metadata) => {
          console.log('SEO metadata generated:', metadata);
          setSeoMetadata(metadata);
          // Metadata is now saved and will be used when publishing to WordPress/Wix
          // The metadata includes all SEO fields (title, description, tags, Open Graph, etc.)
          // Publisher component will use this metadata when calling publish API
        }}
      />
    </div>
  );
};

export default BlogWriter;