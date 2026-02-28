import React, { useState, useCallback } from "react";
import { Box, Paper, Stack, Alert, Divider, CircularProgress, alpha } from "@mui/material";
import { usePodcastProjectState } from "../../hooks/usePodcastProjectState";
import { CreateModal } from "./CreateModal";
import { AnalysisPanel } from "./AnalysisPanel";
import { ScriptEditor } from "./ScriptEditor";
import { RenderQueue } from "./RenderQueue";
import { RecentEpisodesPreview } from "./RecentEpisodesPreview";
import { ProjectList } from "./ProjectList";
import { PreflightBlockDialog } from "./PreflightBlockDialog";
import { PodcastBiblePanel } from "./PodcastBiblePanel";
import {
  Header,
  ProgressStepper,
  EstimateCard,
  QuerySelection,
  ResearchSummary,
  RegenerationFeedbackModal,
  usePodcastWorkflow,
  DEFAULT_KNOBS,
  getStepLabel,
} from "./PodcastDashboard/index";

const PodcastDashboard: React.FC = () => {
  const projectState = usePodcastProjectState();
  const [showProjectList, setShowProjectList] = useState(false);
  const {
    project,
    analysis,
    queries,
    selectedQueries,
    research,
    rawResearch,
    estimate,
    scriptData,
    renderJobs,
    knobs: knobsState,
    researchProvider,
    showScriptEditor,
    showRenderQueue,
    currentStep,
    bible,
    setScriptData,
    setBible,
    setShowScriptEditor,
    setShowRenderQueue,
    setResearchProvider,
    updateRenderJob,
    resetState,
    loadProjectFromDb,
    setCurrentStep,
  } = projectState;

  const workflow = usePodcastWorkflow({
    projectState,
    onError: (msg: string) => {
      // Error handling is done through workflow's own announcement system
      console.error("Workflow error:", msg);
    },
  });

  const [showRegenModal, setShowRegenModal] = useState(false);

  const handleSelectProject = useCallback(async (projectId: string) => {
    try {
      await loadProjectFromDb(projectId);
      setShowProjectList(false);
    } catch (error) {
      const errorMsg = `Failed to load project: ${error instanceof Error ? error.message : "Unknown error"}`;
      // Use workflow's setAnnouncement - workflow is stable from hook
      workflow.setAnnouncement(errorMsg);
    }
  }, [loadProjectFromDb, workflow]);

  const handleNewEpisode = useCallback(() => {
    resetState();
    setShowProjectList(false);
  }, [resetState]);

  if (showProjectList) {
    return <ProjectList onSelectProject={handleSelectProject} />;
  }

  return (
    <Box
      sx={{
        minHeight: "100vh",
        background: "#f8fafc",
        p: { xs: 2, md: 4 },
      }}
    >
      <Paper
        elevation={0}
        sx={{
          maxWidth: 1400,
          mx: "auto",
          borderRadius: 3,
          border: "1px solid rgba(0,0,0,0.08)",
          background: "#ffffff",
          boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
          p: { xs: 3, md: 4 },
        }}
      >
        <Stack spacing={3}>
          {/* Header */}
          <Header onShowProjects={() => setShowProjectList(true)} onNewEpisode={handleNewEpisode} />

          <Divider sx={{ borderColor: "rgba(0,0,0,0.08)" }} />

          {/* Progress Stepper */}
          {project && workflow.activeStep >= 0 && (
            <ProgressStepper
              activeStep={workflow.activeStep}
              completedSteps={[
                ...(analysis ? [0] : []), // Analysis step
                ...(research ? [1] : []), // Research step
                ...(scriptData ? [2] : []), // Script step
                ...(scriptData && renderJobs.length > 0 ? [3] : []), // Render step (if script exists and has jobs)
              ]}
              onStepClick={(stepIndex) => {
                // Navigate to the clicked step
                // Step indices: 0 = Analysis, 1 = Research, 2 = Script, 3 = Render
                if (stepIndex === 0) {
                  // Navigate to Analysis
                  setShowScriptEditor(false);
                  setShowRenderQueue(false);
                  setCurrentStep('analysis');
                } else if (stepIndex === 1) {
                  // Navigate to Research
                  if (!analysis) {
                    workflow.setAnnouncement("Complete Analysis first to access Research.");
                    return;
                  }
                  setShowScriptEditor(false);
                  setShowRenderQueue(false);
                  setCurrentStep('research');
                } else if (stepIndex === 2) {
                  // Navigate to Script
                  if (!research) {
                    workflow.setAnnouncement("Complete Research first to access Script Editor.");
                    return;
                  }
                  setShowRenderQueue(false);
                  setShowScriptEditor(true);
                  setCurrentStep('script');
                } else if (stepIndex === 3) {
                  // Navigate to Render
                  if (!scriptData) {
                    workflow.setAnnouncement("Generate and approve script first to access Render Queue.");
                    return;
                  }
                  setShowScriptEditor(false);
                  setShowRenderQueue(true);
                  setCurrentStep('render');
                }
              }}
            />
          )}

          {/* Resume Alert */}
          {workflow.showResumeAlert && project && (
            <Alert
              severity="success"
              onClose={() => workflow.setShowResumeAlert(false)}
              sx={{
                background: "#d1fae5",
                border: "1px solid #a7f3d0",
                "& .MuiAlert-icon": { color: "#10b981" },
              }}
            >
              <Box component="span" sx={{ fontSize: "0.875rem" }}>
                <strong>Project Restored:</strong> Resuming from {getStepLabel(currentStep)} step. Your progress has been saved.
              </Box>
            </Alert>
          )}

          {/* Announcements */}
          {workflow.announcement && (
            <Alert
              severity="info"
              onClose={() => workflow.setAnnouncement("")}
              sx={{
                background: "#dbeafe",
                border: "1px solid #bfdbfe",
                "& .MuiAlert-icon": { color: "#3b82f6" },
              }}
            >
              {workflow.announcement}
            </Alert>
          )}

          {/* Podcast Bible */}
          {project && bible && (currentStep === 'analysis' || (currentStep === 'research' && !research)) && !showScriptEditor && !showRenderQueue && (
            <PodcastBiblePanel 
              bible={bible} 
              onUpdate={(updated) => setBible(updated)} 
            />
          )}

          {(workflow.isAnalyzing || workflow.isResearching) && (
            <Alert
              severity="warning"
              icon={<CircularProgress size={20} />}
              sx={{
                background: "#fef3c7",
                border: "1px solid #fde68a",
              }}
            >
              <Box component="span" sx={{ fontSize: "0.875rem" }}>
                {workflow.isAnalyzing ? "Analyzing your idea with AI..." : "Running research... This may take a moment."}
              </Box>
            </Alert>
          )}

          {/* Create Modal */}
          {!project && (
            <>
              <CreateModal
                open
                onCreate={workflow.handleCreate}
                defaultKnobs={DEFAULT_KNOBS}
                isSubmitting={workflow.isAnalyzing}
              />
              <RecentEpisodesPreview onSelectEpisode={() => {}} />
            </>
          )}

          {/* Main Content */}
          <Stack spacing={3}>
            {analysis && (currentStep === 'analysis' || (currentStep === 'research' && !research)) && !showScriptEditor && !showRenderQueue && (
              <AnalysisPanel
                analysis={analysis}
                estimate={estimate}
                idea={project?.idea}
                duration={project?.duration}
                speakers={project?.speakers}
                avatarUrl={project?.avatarUrl}
                avatarPrompt={project?.avatarPrompt}
                onRegenerate={() => setShowRegenModal(true)}
                onUpdateAnalysis={(updated) => projectState.setAnalysis(updated)}
              />
            )}

            {/* Main content area */}
            {queries.length > 0 && currentStep === 'research' && !research && !showScriptEditor && !showRenderQueue && (
              <QuerySelection
                queries={queries}
                selectedQueries={selectedQueries}
                researchProvider={researchProvider}
                isResearching={workflow.isResearching}
                onToggleQuery={workflow.toggleQuery}
                onProviderChange={setResearchProvider}
                onRunResearch={workflow.handleRunResearch}
              />
            )}

            {research && (currentStep === 'research' || currentStep === 'script') && !showScriptEditor && !showRenderQueue && (
              <ResearchSummary
                research={research}
                canGenerateScript={workflow.canGenerateScript}
                onGenerateScript={workflow.handleGenerateScript}
              />
            )}

            {showScriptEditor && project && research && rawResearch && (
              <ScriptEditor
                projectId={project.id}
                idea={project.idea}
                research={research}
                rawResearch={rawResearch}
                knobs={knobsState}
                speakers={project.speakers}
                durationMinutes={project.duration}
                script={scriptData}
                analysis={analysis}
                outline={analysis?.suggestedOutlines?.[0]}
                onScriptChange={(s) => setScriptData(s)}
                onBackToResearch={() => setShowScriptEditor(false)}
                onProceedToRendering={(s) => workflow.handleProceedToRendering(s)}
                onError={(msg) => workflow.setAnnouncement(msg)}
                avatarUrl={project?.avatarUrl}
              />
            )}

            {showScriptEditor && (!research || !rawResearch) && (
              <Alert severity="warning" sx={{ background: alpha("#f59e0b", 0.1), border: "1px solid rgba(245,158,11,0.3)" }}>
                Complete a research run before opening the script editor.
              </Alert>
            )}

            {showRenderQueue && project && scriptData && (
              <RenderQueue
                projectId={project.id}
                script={scriptData}
                knobs={knobsState}
                jobs={renderJobs}
                bible={bible}
                budgetCap={projectState.budgetCap}
                avatarImageUrl={null}
                analysis={analysis} // Pass analysis context
                onUpdateJob={updateRenderJob}
                onUpdateScript={(updatedScript) => setScriptData(updatedScript)}
                onBack={() => {
                  setShowRenderQueue(false);
                  setShowScriptEditor(true);
                }}
                onError={(msg) => workflow.setAnnouncement(msg)}
              />
            )}
          </Stack>
        </Stack>
      </Paper>

      {/* Preflight Block Dialog */}
      <PreflightBlockDialog
        open={workflow.showPreflightDialog}
        onClose={() => {
          workflow.setShowPreflightDialog(false);
          workflow.setPreflightResponse(null);
        }}
        response={workflow.preflightResponse}
        operationName={workflow.preflightOperationName}
      />

      {/* Regeneration Feedback Modal */}
      <RegenerationFeedbackModal
        open={showRegenModal}
        onClose={() => setShowRegenModal(false)}
        onConfirm={async (feedback) => {
          setShowRegenModal(false);
          await workflow.handleRegenerate(feedback);
        }}
        isSubmitting={workflow.isAnalyzing}
      />
    </Box>
  );
};

export default PodcastDashboard;
