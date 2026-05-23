import React, { useRef, useCallback, useState } from 'react';
import { useNavigate, useSearchParams, useLocation } from 'react-router-dom';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogActions from '@mui/material/DialogActions';
import Button from '@mui/material/Button';
import { debug } from '../../utils/debug';
import WriterCopilotSidebar from './BlogWriterUtils/WriterCopilotSidebar';
import { blogWriterApi } from '../../services/blogWriterApi';
import { researchCache } from '../../services/researchCache';
import { useClaimFixer } from '../../hooks/useClaimFixer';
import { useMarkdownProcessor } from '../../hooks/useMarkdownProcessor';
import { useBlogWriterState } from '../../hooks/useBlogWriterState';
import HallucinationChecker from './HallucinationChecker';
import Publisher from './Publisher';
import OutlineGenerator from './OutlineGenerator';
import OutlineRefiner from './OutlineRefiner';
import { SEOProcessor } from './SEO';
import TaskProgressModals from './BlogWriterUtils/TaskProgressModals';
import { SEOAnalysisModal } from './SEOAnalysisModal';
import { SEOMetadataModal } from './SEOMetadataModal';
import { usePhaseNavigation } from '../../hooks/usePhaseNavigation';
import HeaderBar from './BlogWriterUtils/HeaderBar';
import PhaseContent from './BlogWriterUtils/PhaseContent';
import useBlogWriterCopilotActions from './BlogWriterUtils/useBlogWriterCopilotActions';
import { useCopilotKitHealth } from '../../hooks/useCopilotKitHealth';
import { useSEOManager } from './BlogWriterUtils/useSEOManager';
import { usePhaseActionHandlers } from './BlogWriterUtils/usePhaseActionHandlers';
import { useBlogWriterPolling } from './BlogWriterUtils/useBlogWriterPolling';
import { useCopilotSuggestions } from './BlogWriterUtils/useCopilotSuggestions';
import { usePhaseRestoration } from './BlogWriterUtils/usePhaseRestoration';
import { useModalVisibility } from './BlogWriterUtils/useModalVisibility';
import { useBlogWriterRefs } from './BlogWriterUtils/useBlogWriterRefs';
import { BlogWriterLandingSection } from './BlogWriterUtils/BlogWriterLandingSection';
import { CopilotKitComponents } from './BlogWriterUtils/CopilotKitComponents';
import { useBlogAsset } from '../../hooks/useBlogAsset';

const BlogWriter: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  // Add light theme class to body/html on mount, remove on unmount
  React.useEffect(() => {
    document.body.classList.add('blog-writer-page');
    document.documentElement.classList.add('blog-writer-page');
    return () => {
      document.body.classList.remove('blog-writer-page');
      document.documentElement.classList.remove('blog-writer-page');
    };
  }, []);

  // Check CopilotKit health status
  const { isAvailable: copilotKitAvailable } = useCopilotKitHealth({
    enabled: true, // Enable health checking
  });

  const navigate = useNavigate();

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
    sectionImages,
    restoreAttempted,
    setResearch,
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
    setOutlineConfirmed,
    setFlowAnalysisCompleted,
    setFlowAnalysisResults,
    setSectionImages,
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

  // SEO Manager - handles all SEO-related logic
  // Initialize phase navigation with temporary false value for seoRecommendationsApplied
  const [tempSeoRecommendationsApplied] = React.useState(false);
  const {
    phases: tempPhases,
    currentPhase: tempCurrentPhase,
    navigateToPhase: tempNavigateToPhase,
    setCurrentPhase: tempSetCurrentPhase,
    resetUserSelection
  } = usePhaseNavigation(
    research,
    outline,
    outlineConfirmed,
    Object.keys(sections).length > 0,
    contentConfirmed,
    seoAnalysis,
    seoMetadata,
    tempSeoRecommendationsApplied
  );

  const {
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
  } = useSEOManager({
    sections,
    research,
    outline,
    selectedTitle,
    contentConfirmed,
    seoAnalysis,
    currentPhase: tempCurrentPhase,
    navigateToPhase: tempNavigateToPhase,
    setContentConfirmed,
    setSeoAnalysis,
    setSeoMetadata,
    setSections,
    setSelectedTitle: setSelectedTitle as (title: string | null) => void,
    setContinuityRefresh,
    setFlowAnalysisCompleted,
    setFlowAnalysisResults,
  });

  // Phase navigation hook with correct seoRecommendationsApplied
  const {
    phases,
    currentPhase,
    navigateToPhase,
    setCurrentPhase,
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

  // Update ref when navigateToPhase changes
  React.useEffect(() => {
    navigateToPhaseRef.current = navigateToPhase;
  }, [navigateToPhase]);

  // Phase restoration logic
  usePhaseRestoration({
    copilotKitAvailable,
    research,
    phases,
    currentPhase,
    navigateToPhase,
    setCurrentPhase,
  });

  // All SEO management logic is now in useSEOManager hook above

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

  // Store navigateToPhase in a ref for use in polling callbacks
  const navigateToPhaseRef = React.useRef<((phase: string) => void) | null>(null);
  // When true (Re-Content), polling callback skips auto-confirm and SEO navigation
  const skipContentAutoConfirmRef = React.useRef<boolean>(false);

  // Normalize section keys to match outline IDs when updating from API responses
  const handleSectionsUpdate = useCallback((newSections: Record<string, string>) => {
    if (outline && outline.length > 0 && Object.keys(newSections).length > 0) {
      const normalized: Record<string, string> = {};
      const values = Object.values(newSections);
      outline.forEach((s, idx) => {
        const id = String(s.id);
        normalized[id] = newSections[id] ?? values[idx] ?? '';
      });
      setSections(normalized);
    } else {
      setSections(newSections);
    }
  }, [outline, setSections]);

  // Blog asset persistence (phase-by-phase saving via ContentAsset)
  const {
    assetId,
    createAsset,
    updatePhase,
    loadAsset,
    resetAsset,
  } = useBlogAsset();
  // Load blog asset passed via React Router state (from Asset Library)
  const location = useLocation();
  const locationState = location.state as { restoreBlogAssetId?: number } | null;

  // Persist last active asset_id across refreshes
  const saveLastAssetId = useCallback((id: number) => {
    try { localStorage.setItem('blog_last_asset_id', id.toString()); } catch { /* noop */ }
  }, []);

  React.useEffect(() => {
    const assetIdFromState = locationState?.restoreBlogAssetId;
    if (assetIdFromState) {
      // Coming from Asset Library — load that specific asset
      loadAsset(assetIdFromState).then(loaded => {
        if (!loaded) return;
        saveLastAssetId(assetIdFromState);
        debug.log('[BlogWriter] Loaded blog asset from navigation state', { asset_id: assetIdFromState, phase: loaded.phase });
      });
    } else {
      // No navigation state — try restoring last active asset from localStorage
      const savedId = (() => { try { return localStorage.getItem('blog_last_asset_id'); } catch { return null; } })();
      if (savedId) {
        const id = parseInt(savedId, 10);
        if (!isNaN(id)) {
          loadAsset(id).then(loaded => {
            if (loaded) {
              debug.log('[BlogWriter] Restored last active blog', { asset_id: id, phase: loaded.phase });
            } else {
              // Asset was deleted or inaccessible — clear stale localStorage key
              try { localStorage.removeItem('blog_last_asset_id'); } catch { /* noop */ }
            }
          });
        }
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Create/get blog asset before research starts (saves to Asset Library immediately)
  const handleBeforeResearchSubmit = useCallback(async (keywords: string, blogLength: string) => {
    const id = await createAsset(keywords, keywords, parseInt(blogLength));
    if (id) saveLastAssetId(id);
  }, [createAsset, saveLastAssetId]);

  // Wrap handlers to also update the blog ContentAsset
  const wrappedHandleResearchComplete = useCallback((researchData: any) => {
    handleResearchComplete(researchData);
    if (assetId) { updatePhase('research', researchData); saveLastAssetId(assetId); }
  }, [handleResearchComplete, assetId, updatePhase, saveLastAssetId]);

  const wrappedHandleSEOAnalysisComplete = useCallback((analysis: any) => {
    handleSEOAnalysisComplete(analysis);
    if (assetId) { updatePhase('seo', analysis); saveLastAssetId(assetId); }
  }, [handleSEOAnalysisComplete, assetId, updatePhase, saveLastAssetId]);

  const wrappedHandleOutlineConfirmed = useCallback(() => {
    handleOutlineConfirmed();
    if (assetId) {
      updatePhase('outline', { outline, selected_title: selectedTitle, title_options: titleOptions });
      saveLastAssetId(assetId);
    }
  }, [handleOutlineConfirmed, assetId, updatePhase, outline, selectedTitle, titleOptions, saveLastAssetId]);

  const wrappedConfirmBlogContent = useCallback(() => {
    const result = confirmBlogContent();
    if (assetId) { updatePhase('content', sections); saveLastAssetId(assetId); }
    return result;
  }, [confirmBlogContent, assetId, updatePhase, sections, saveLastAssetId]);

  // Polling hooks - extracted to useBlogWriterPolling
  const {
    researchPolling,
    outlinePolling,
    mediumPolling,
    rewritePolling,
    researchPollingState,
    outlinePollingState,
    mediumPollingState,
  } = useBlogWriterPolling({
    onResearchComplete: wrappedHandleResearchComplete,
    onOutlineComplete: handleOutlineComplete,
    onOutlineError: handleOutlineError,
    onSectionsUpdate: handleSectionsUpdate,
    onContentConfirmed: () => {
      debug.log('[BlogWriter] Content generation completed - auto-confirming content');
      setContentConfirmed(true);
    },
    onContentError: () => {
      debug.log('[BlogWriter] Content generation failed - reverting outline confirmation');
      setOutlineConfirmed(false);
    },
    navigateToPhase: (phase) => {
      debug.log('[BlogWriter] Navigating to phase after content generation', { phase });
      // Use ref to access navigateToPhase (defined later in component)
      if (navigateToPhaseRef.current) {
        setTimeout(() => {
          navigateToPhaseRef.current?.(phase);
        }, 0);
      }
    },
    skipContentAutoConfirmRef,
  });

  // Modal visibility management - extracted to useModalVisibility
  const {
    showModal,
    showOutlineModal,
    setShowOutlineModal,
    isMediumGenerationStarting,
    setIsMediumGenerationStarting,
  } = useModalVisibility({
    mediumPolling,
    rewritePolling,
    outlinePolling,
  });

  // CopilotKit suggestions management - extracted to useCopilotSuggestions
  // Check if sections exist AND have actual content (not just empty strings)
  const hasContent = React.useMemo(() => {
    const sectionKeys = Object.keys(sections);
    if (sectionKeys.length === 0) return false;
    // Check if at least one section has actual content
    const sectionsWithContent = Object.values(sections).filter(c => c && c.trim().length > 0);
    return sectionsWithContent.length > 0;
  }, [sections]);
  const {
    suggestions,
    setSuggestionsRef,
  } = useCopilotSuggestions({
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
  });

  // Refs and tracking logic - extracted to useBlogWriterRefs
  useBlogWriterRefs({
    research,
    outline,
    outlineConfirmed,
    contentConfirmed,
    sections,
    currentPhase,
    isSEOAnalysisModalOpen,
    resetUserSelection,
  });

  const handlePhaseClick = useCallback((phaseId: string) => {
    navigateToPhase(phaseId);
    if (phaseId === 'research') {
      if (!currentPhase) {
        setResearch(null);
        debug.log('[BlogWriter] Research phase clicked from landing - cleared research to show form');
      } else {
        debug.log('[BlogWriter] Research phase clicked - showing existing research data');
      }
    }
    if (phaseId === 'seo') {
      if (seoAnalysis) {
        setIsSEOAnalysisModalOpen(true);
        debug.log('[BlogWriter] SEO modal opened (phase navigation)');
      } else {
        runSEOAnalysisDirect();
      }
    }
  }, [navigateToPhase, currentPhase, seoAnalysis, research, setResearch, runSEOAnalysisDirect, setIsSEOAnalysisModalOpen]);

  const handleNewBlog = useCallback(() => {
    setResearch(null);
    setOutline([]);
    setSections({});
    setSeoAnalysis(null);
    setSeoMetadata(null);
    setContentConfirmed(false);
    setOutlineConfirmed(false);
    setSelectedTitle('');
    setTitleOptions([]);
    setCurrentPhase('');
    try {
      localStorage.removeItem('blog_outline');
      localStorage.removeItem('blog_title_options');
      localStorage.removeItem('blog_selected_title');
      localStorage.removeItem('blogwriter_current_phase');
      localStorage.removeItem('blogwriter_user_selected_phase');
      localStorage.removeItem('blog_content_confirmed');
      localStorage.removeItem('blog_seo_recommendations_applied');
      localStorage.removeItem('blog_last_asset_id');
    } catch {
      // ignore localStorage errors
    }
    researchCache.clearCache();
    resetAsset();
    setSearchParams({}, { replace: true });
  }, [setResearch, setOutline, setSections, setSeoAnalysis, setSeoMetadata,
      setContentConfirmed, setOutlineConfirmed, setSelectedTitle, setTitleOptions,
      setCurrentPhase, resetAsset, setSearchParams]);

  // Handle ?new=true query param from "New Blog" button in Asset Library
  React.useEffect(() => {
    if (searchParams.get('new') === 'true') {
      handleNewBlog();
      setSearchParams({}, { replace: true });
    }
  }, [searchParams, handleNewBlog, setSearchParams]);

  const [newBlogDialogOpen, setNewBlogDialogOpen] = useState(false);

  const handleMyBlogs = useCallback(() => {
    navigate('/asset-library?source_module=blog_writer&asset_type=text');
  }, [navigate]);

  const hasExistingWork = !!(research || outline.length > 0 || Object.keys(sections).length > 0);

  const confirmNewBlog = useCallback(() => {
    if (hasExistingWork) {
      setNewBlogDialogOpen(true);
    } else {
      handleNewBlog();
    }
  }, [hasExistingWork, handleNewBlog]);

  const outlineGenRef = useRef<any>(null);

  // Callback to handle cached outline completion
  const handleCachedOutlineComplete = useCallback((result: { outline: any[], title_options?: string[] }) => {
    if (result.outline && Array.isArray(result.outline)) {
      handleOutlineComplete(result);
    }
  }, [handleOutlineComplete]);

  // Callback to handle cached content completion
  const handleCachedContentComplete = useCallback((cachedSections: Record<string, string>) => {
    if (cachedSections && Object.keys(cachedSections).length > 0) {
      setSections(cachedSections);
      debug.log('[BlogWriter] Cached content loaded into state', { sections: Object.keys(cachedSections).length });
    }
  }, [setSections]);

  // Phase action handlers for when CopilotKit is unavailable - extracted to usePhaseActionHandlers
  const {
    handleResearchAction,
    handleOutlineAction,
    handleContentAction,
    handleSEOAction,
    handleApplySEORecommendations,
    handlePublishAction,
  } = usePhaseActionHandlers({
    research,
    outline,
    selectedTitle,
    contentConfirmed,
    sections,
    seoAnalysis,
    navigateToPhase,
    handleOutlineConfirmed,
    setIsMediumGenerationStarting,
    mediumPolling,
    outlineGenRef,
    setOutline,
    setContentConfirmed,
    setIsSEOAnalysisModalOpen,
    setIsSEOMetadataModalOpen,
    runSEOAnalysisDirect,
    skipContentAutoConfirmRef,
    onResearchComplete: wrappedHandleResearchComplete,
    onOutlineComplete: handleCachedOutlineComplete,
    onContentComplete: handleCachedContentComplete,
  });

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

  useBlogWriterCopilotActions({
    isSEOAnalysisModalOpen,
    lastSEOModalOpenRef,
    runSEOAnalysisDirect,
    confirmBlogContent: wrappedConfirmBlogContent,
    sections,
    research,
    openSEOMetadata: () => setIsSEOMetadataModalOpen(true),
    navigateToPhase,
  });





  return (
    <div style={{ 
      height: '100vh', 
      display: 'flex', 
      flexDirection: 'column',
      backgroundColor: '#ffffff',
      color: '#1a1a1a',
      overflow: 'auto'
    }} className="blog-writer-container">
      {/* CopilotKit-dependent components - extracted to CopilotKitComponents */}
      {copilotKitAvailable && (
        <CopilotKitComponents
          research={research}
          outline={outline}
          outlineConfirmed={outlineConfirmed}
          sections={sections}
          selectedTitle={selectedTitle}
           onResearchComplete={wrappedHandleResearchComplete}
          onOutlineCreated={setOutline}
          onOutlineUpdated={setOutline}
          onTitleOptionsSet={setTitleOptions}
          onOutlineConfirmed={wrappedHandleOutlineConfirmed}
          onOutlineRefined={(feedback?: string) => handleOutlineRefined(feedback || '')}
          onMediumGenerationStarted={handleMediumGenerationStarted}
          onMediumGenerationTriggered={handleMediumGenerationTriggered}
          onRewriteStarted={(taskId) => {
            console.log('Starting rewrite polling for task:', taskId);
            rewritePolling.startPolling(taskId);
          }}
          onRewriteTriggered={() => {
            console.log('Rewrite triggered - showing modal immediately');
            setIsMediumGenerationStarting(true);
          }}
          setFlowAnalysisCompleted={setFlowAnalysisCompleted}
          setFlowAnalysisResults={setFlowAnalysisResults}
          setContinuityRefresh={setContinuityRefresh}
          researchPolling={researchPolling}
          navigateToPhase={navigateToPhase}
        />
      )}
      
      {/* New extracted functionality components */}
      <OutlineGenerator
        ref={outlineGenRef}
        research={research}
        onTaskStart={(taskId) => setOutlineTaskId(taskId)}
        onPollingStart={(taskId) => outlinePolling.startPolling(taskId)}
        onModalShow={() => setShowOutlineModal(true)}
        navigateToPhase={navigateToPhase}
        onOutlineCreated={(outline, titleOptions) => {
          // Handle cached outline from CopilotKit action (same as header button)
          setOutline(outline);
          if (titleOptions) {
            setTitleOptions(titleOptions);
          }
        }}
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
        onPublishComplete={() => {
          if (assetId) {
            const fullContent = buildFullMarkdown();
            updatePhase('publish', {
              published_at: new Date().toISOString(),
              content_preview: fullContent.substring(0, 500),
              title: selectedTitle || seoMetadata?.seo_title || '',
            });
            saveLastAssetId(assetId);
          }
        }}
      />
      
      {/* Phase navigation header - always visible as default interface */}
      <div style={{ flexShrink: 0 }}>
      <HeaderBar
        phases={phases}
        currentPhase={currentPhase}
        onPhaseClick={handlePhaseClick}
        copilotKitAvailable={copilotKitAvailable}
        actionHandlers={{
          onResearchAction: handleResearchAction,
          onOutlineAction: handleOutlineAction,
          onContentAction: handleContentAction,
          onSEOAction: handleSEOAction,
          onApplySEORecommendations: handleApplySEORecommendations,
          onPublishAction: handlePublishAction,
        }}
        hasResearch={!!research}
        hasOutline={outline.length > 0}
        outlineConfirmed={outlineConfirmed}
        hasContent={hasContent}
        contentConfirmed={contentConfirmed}
        hasSEOAnalysis={!!seoAnalysis}
        seoRecommendationsApplied={seoRecommendationsApplied}
        hasSEOMetadata={!!seoMetadata}
        onNewBlog={confirmNewBlog}
        onMyBlogs={handleMyBlogs}
        onHelp={() => window.open('/docs', '_blank')}
      />
      </div>

      {/* Landing section - extracted to BlogWriterLandingSection */}
      <BlogWriterLandingSection
        research={research}
        copilotKitAvailable={copilotKitAvailable}
        currentPhase={currentPhase}
        navigateToPhase={navigateToPhase}
        onResearchComplete={wrappedHandleResearchComplete}
        onBeforeResearchSubmit={handleBeforeResearchSubmit}
        restoreAttempted={restoreAttempted}
      />

      {research && (
        <>
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
        sectionImages={sectionImages}
        setSectionImages={setSectionImages}
        contentConfirmed={contentConfirmed}
        seoAnalysis={seoAnalysis}
        seoMetadata={seoMetadata}
        onTitleSelect={handleTitleSelect}
        onCustomTitle={handleCustomTitle}
        copilotKitAvailable={copilotKitAvailable}
        onResearchComplete={wrappedHandleResearchComplete}
        onOutlineGenerationStart={(taskId) => {
          setOutlineTaskId(taskId);
          outlinePolling.startPolling(taskId);
          setShowOutlineModal(true);
        }}
        onContentGenerationStart={handleMediumGenerationStarted}
        buildFullMarkdown={buildFullMarkdown}
        convertMarkdownToHTML={convertMarkdownToHTML}
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
        onAnalysisComplete={wrappedHandleSEOAnalysisComplete}
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

      {/* New Blog confirmation dialog */}
      <Dialog
        open={newBlogDialogOpen}
        onClose={() => setNewBlogDialogOpen(false)}
        aria-labelledby="new-blog-dialog-title"
      >
        <DialogTitle id="new-blog-dialog-title">Start New Blog?</DialogTitle>
        <DialogContent>
          <DialogContentText>
            This will clear all your current work and start a new blog. This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setNewBlogDialogOpen(false)}>Cancel</Button>
          <Button onClick={() => { handleNewBlog(); setNewBlogDialogOpen(false); }} color="primary" variant="contained">
            Start New
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};

export default BlogWriter;