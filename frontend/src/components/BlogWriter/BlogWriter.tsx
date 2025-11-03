import React, { useRef, useCallback } from 'react';
import { debug } from '../../utils/debug';
import WriterCopilotSidebar from './BlogWriterUtils/WriterCopilotSidebar';
import { blogWriterApi } from '../../services/blogWriterApi';
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

export const BlogWriter: React.FC = () => {
  // Check CopilotKit health status
  const { isAvailable: copilotKitAvailable } = useCopilotKitHealth({
    enabled: true, // Enable health checking
  });

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
    onResearchComplete: handleResearchComplete,
    onOutlineComplete: handleOutlineComplete,
    onOutlineError: handleOutlineError,
    onSectionsUpdate: setSections,
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
  const hasContent = React.useMemo(() => Object.keys(sections).length > 0, [sections]);
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
    if (phaseId === 'seo') {
      if (seoAnalysis) {
        setIsSEOAnalysisModalOpen(true);
        debug.log('[BlogWriter] SEO modal opened (phase navigation)');
      } else {
        runSEOAnalysisDirect();
      }
    }
  }, [navigateToPhase, seoAnalysis, runSEOAnalysisDirect, setIsSEOAnalysisModalOpen]);

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
    handlePublishAction,
  } = usePhaseActionHandlers({
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
    confirmBlogContent,
    sections,
    research,
    openSEOMetadata: () => setIsSEOMetadataModalOpen(true),
  });





  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* CopilotKit-dependent components - extracted to CopilotKitComponents */}
      {copilotKitAvailable && (
        <CopilotKitComponents
          research={research}
          outline={outline}
          outlineConfirmed={outlineConfirmed}
          sections={sections}
          selectedTitle={selectedTitle}
          onResearchComplete={handleResearchComplete}
          onOutlineCreated={setOutline}
          onOutlineUpdated={setOutline}
          onTitleOptionsSet={setTitleOptions}
          onOutlineConfirmed={handleOutlineConfirmed}
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
      
      {/* Always show HeaderBar when CopilotKit is unavailable, or when research exists */}
      {(!copilotKitAvailable || research) && (
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
            onPublishAction: handlePublishAction,
          }}
          hasResearch={!!research}
          hasOutline={outline.length > 0}
          outlineConfirmed={outlineConfirmed}
          hasContent={Object.keys(sections).length > 0}
          contentConfirmed={contentConfirmed}
          hasSEOAnalysis={!!seoAnalysis}
          hasSEOMetadata={!!seoMetadata}
        />
      )}

      {/* Landing section - extracted to BlogWriterLandingSection */}
      <BlogWriterLandingSection
        research={research}
        copilotKitAvailable={copilotKitAvailable}
        currentPhase={currentPhase}
        navigateToPhase={navigateToPhase}
        onResearchComplete={handleResearchComplete}
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
        onResearchComplete={handleResearchComplete}
        onOutlineGenerationStart={(taskId) => {
          setOutlineTaskId(taskId);
          outlinePolling.startPolling(taskId);
          setShowOutlineModal(true);
        }}
        onContentGenerationStart={handleMediumGenerationStarted}
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