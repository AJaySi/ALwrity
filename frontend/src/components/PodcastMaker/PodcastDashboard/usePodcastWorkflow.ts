import { useState, useEffect, useMemo, useCallback } from "react";
import { ResearchProvider, ResearchConfig } from "../../../services/blogWriterApi";
import { podcastApi } from "../../../services/podcastApi";
import { usePreflightCheck } from "../../../hooks/usePreflightCheck";
import { useBudgetTracking } from "../../../hooks/useBudgetTracking";
import { CreateProjectPayload, Query, Research, Script, Job } from "../types";
import { usePodcastProjectState } from "../../../hooks/usePodcastProjectState";
import { sanitizeExaConfig, announceError, getStepLabel } from "./utils";

type PodcastProjectStateReturn = ReturnType<typeof usePodcastProjectState>;

interface UsePodcastWorkflowProps {
  projectState: PodcastProjectStateReturn;
  onError: (message: string) => void;
}

export const usePodcastWorkflow = ({ projectState, onError }: UsePodcastWorkflowProps) => {
  const {
    project,
    analysis,
    queries,
    selectedQueries,
    research,
    rawResearch,
    researchProvider,
    showScriptEditor,
    showRenderQueue,
    currentStep,
    renderJobs,
    budgetCap,
    setProject,
    setAnalysis,
    setQueries,
    setSelectedQueries,
    setResearch,
    setRawResearch,
    setEstimate,
    setScriptData,
    setShowScriptEditor,
    setShowRenderQueue,
    setKnobs,
    setResearchProvider,
    setBudgetCap,
    updateRenderJob,
    initializeProject,
  } = projectState;

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isResearching, setIsResearching] = useState(false);
  const [announcement, setAnnouncement] = useState("");
  const [showResumeAlert, setShowResumeAlert] = useState(false);
  const [showPreflightDialog, setShowPreflightDialog] = useState(false);
  const [preflightResponse, setPreflightResponse] = useState<any>(null);
  const [preflightOperationName, setPreflightOperationName] = useState<string>("");

  const budgetTracking = useBudgetTracking(budgetCap || 50);
  const preflightCheck = usePreflightCheck({
    onBlocked: (response) => {
      setPreflightResponse(response);
      setShowPreflightDialog(true);
    },
  });

  // Update budget cap when project state changes
  useEffect(() => {
    if (budgetCap) {
      budgetTracking.setBudgetCap(budgetCap);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [budgetCap]);

  // Check if we have a saved project on mount
  useEffect(() => {
    if (project && currentStep && currentStep !== "create") {
      setShowResumeAlert(true);
      setTimeout(() => setShowResumeAlert(false), 5000);
    }
  }, []); // Only on mount

  useEffect(() => {
    if (announcement) {
      const t = setTimeout(() => setAnnouncement(""), 4000);
      return () => clearTimeout(t);
    }
    return undefined;
  }, [announcement]);

  const handleCreate = useCallback(async (payload: CreateProjectPayload) => {
    if (isAnalyzing) return;
    setResearch(null);
    setRawResearch(null);
    setScriptData(null);
    setShowScriptEditor(false);
    setShowRenderQueue(false);
    try {
      setIsAnalyzing(true);
      setAnnouncement("Analyzing your idea — AI suggestions incoming");
      const result = await podcastApi.createProject(payload);
      await initializeProject(payload, result.projectId);
      setProject({ id: result.projectId, idea: payload.ideaOrUrl, duration: payload.duration, speakers: payload.speakers });
      setAnalysis(result.analysis);
      setEstimate(result.estimate);
      setQueries(result.queries);
      setSelectedQueries(new Set(result.queries.map((q) => q.id)));
      setKnobs(payload.knobs);
      setBudgetCap(payload.budgetCap);
      setAnnouncement("Analysis complete");
    } catch (error: any) {
      if (error?.response?.status === 429 || error?.response?.data?.detail) {
        const errorDetail = error.response.data.detail;
        if (typeof errorDetail === 'object' && errorDetail.error && errorDetail.error.includes('limit')) {
          const usageInfo = errorDetail.usage_info || {};
          const blockedResponse = {
            can_proceed: false,
            estimated_cost: 0,
            operations: [{
              provider: errorDetail.provider || 'huggingface',
              operation_type: 'ai_text_generation',
              cost: 0,
              allowed: false,
              limit_info: usageInfo.limit_info || null,
              message: errorDetail.message || errorDetail.error || 'Subscription limit exceeded',
            }],
            total_cost: 0,
            usage_summary: usageInfo.usage_summary || null,
            cached: false,
          };
          setPreflightResponse(blockedResponse);
          setPreflightOperationName('Podcast Analysis');
          setShowPreflightDialog(true);
          setAnnouncement("Subscription limit reached. Please upgrade to continue.");
        } else {
          const message = typeof errorDetail === 'string' ? errorDetail : errorDetail.message || errorDetail.error || 'Request limit exceeded';
          announceError(setAnnouncement, new Error(message));
        }
      } else {
        announceError(setAnnouncement, error);
      }
    } finally {
      setIsAnalyzing(false);
    }
  }, [isAnalyzing, setResearch, setRawResearch, setScriptData, setShowScriptEditor, setShowRenderQueue, initializeProject, setProject, setAnalysis, setEstimate, setQueries, setSelectedQueries, setKnobs, setBudgetCap]);

  const handleRunResearch = useCallback(async () => {
    if (isResearching) return;
    if (!project) {
      setAnnouncement("Create a project first.");
      return;
    }
    if (selectedQueries.size === 0) {
      setAnnouncement("Select at least one query to research.");
      return;
    }

    setPreflightOperationName("Research");
    const approvedQueries = queries.filter((q) => selectedQueries.has(q.id));
    const preflightResult = await preflightCheck.check({
      provider: researchProvider === "exa" ? "exa" : "gemini",
      operation_type: researchProvider === "exa" ? "exa_neural_search" : "google_grounding",
      tokens_requested: researchProvider === "exa" ? 0 : 1200,
      actual_provider_name: researchProvider || "exa",
    });

    if (!preflightResult.can_proceed) {
      return;
    }

    try {
      setIsResearching(true);
      setAnnouncement(`Starting ${researchProvider === "exa" ? "deep" : "standard"} research — this may take a moment...`);
      setResearch(null);
      setRawResearch(null);
      setScriptData(null);
      setShowScriptEditor(false);
      setShowRenderQueue(false);

      try {
        const { research: mapped, raw } = await podcastApi.runResearch({
          projectId: project.id,
          topic: project.idea,
          approvedQueries,
          provider: researchProvider,
          exaConfig: sanitizeExaConfig(analysis?.exaSuggestedConfig),
          onProgress: (message) => {
            setAnnouncement(message);
          },
        });
        setResearch(mapped);
        setRawResearch(raw);
        setAnnouncement("Research complete — review fact cards below");
      } catch (researchError) {
        const errorMessage = researchError instanceof Error
          ? researchError.message
          : "Research failed. Please try again or switch to Standard Research.";

        if (errorMessage.includes("Exa") || errorMessage.includes("exa")) {
          setAnnouncement(`Deep research failed: ${errorMessage}. Try Standard Research instead.`);
        } else if (errorMessage.includes("timeout")) {
          setAnnouncement("Research timed out. Please try again with fewer queries.");
        } else {
          setAnnouncement(`Research failed: ${errorMessage}`);
        }

        console.error("Research error:", researchError);
        throw researchError;
      }
    } catch (error) {
      announceError(setAnnouncement, error);
    } finally {
      setIsResearching(false);
    }
  }, [isResearching, project, selectedQueries, queries, researchProvider, preflightCheck, analysis, setResearch, setRawResearch, setScriptData, setShowScriptEditor, setShowRenderQueue]);

  const handleGenerateScript = useCallback(async () => {
    if (showScriptEditor) return;
    if (!project || !research) {
      setAnnouncement("Project or research missing — cannot generate script");
      return;
    }

    setPreflightOperationName("Script Generation");
    const preflightResult = await preflightCheck.check({
      provider: "gemini",
      operation_type: "script_generation",
      tokens_requested: 2000,
      actual_provider_name: "gemini",
    });

    if (!preflightResult.can_proceed) {
      return;
    }

    setScriptData(null);
    setShowRenderQueue(false);
    setShowScriptEditor(true);
  }, [showScriptEditor, project, research, preflightCheck, setScriptData, setShowRenderQueue, setShowScriptEditor]);

  const handleProceedToRendering = useCallback((script: Script) => {
    setScriptData(script);
    if (renderJobs.length === 0) {
      script.scenes.forEach((scene) => {
        const hasExistingAudio = Boolean(scene.audioUrl);
        updateRenderJob(scene.id, {
          sceneId: scene.id,
          title: scene.title,
          status: hasExistingAudio ? ("completed" as const) : ("idle" as const),
          progress: hasExistingAudio ? 100 : 0,
          previewUrl: null,
          finalUrl: hasExistingAudio ? scene.audioUrl : null,
          jobId: null,
        });
      });
    }
    setShowRenderQueue(true);
    setShowScriptEditor(false);
  }, [renderJobs.length, setScriptData, updateRenderJob, setShowRenderQueue, setShowScriptEditor]);

  const toggleQuery = useCallback((id: string) => {
    if (isResearching) return;
    const current = selectedQueries;
    const next = new Set<string>(current);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setSelectedQueries(next);
  }, [isResearching, selectedQueries, setSelectedQueries]);

  const activeStep = useMemo(() => {
    if (showRenderQueue) return 3;
    if (showScriptEditor) return 2;
    if (research) return 1;
    if (analysis) return 0;
    return -1;
  }, [showRenderQueue, showScriptEditor, research, analysis]);

  const canGenerateScript = Boolean(project && research && rawResearch);

  return {
    // State
    isAnalyzing,
    isResearching,
    announcement,
    showResumeAlert,
    showPreflightDialog,
    preflightResponse,
    preflightOperationName,
    activeStep,
    canGenerateScript,
    // Handlers
    handleCreate,
    handleRunResearch,
    handleGenerateScript,
    handleProceedToRendering,
    toggleQuery,
    setAnnouncement,
    setShowResumeAlert,
    setShowPreflightDialog,
    setPreflightResponse,
    setResearchProvider,
    getStepLabel,
  };
};

