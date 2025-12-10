import React, { useEffect, useMemo, useState } from "react";
import {
  Box,
  Paper,
  Stack,
  Typography,
  Alert,
  Chip,
  Tooltip,
  LinearProgress,
  Stepper,
  Step,
  StepLabel,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Checkbox,
  CircularProgress,
  alpha,
} from "@mui/material";
import {
  Mic as MicIcon,
  Psychology as PsychologyIcon,
  Search as SearchIcon,
  EditNote as EditNoteIcon,
  PlayArrow as PlayArrowIcon,
  CheckCircle as CheckCircleIcon,
  Info as InfoIcon,
  AutoAwesome as AutoAwesomeIcon,
  Insights as InsightsIcon,
  LibraryMusic as LibraryMusicIcon,
} from "@mui/icons-material";
import { ResearchProvider } from "../../services/blogWriterApi";
import { podcastApi } from "../../services/podcastApi";
import { usePodcastProjectState } from "../../hooks/usePodcastProjectState";
import { useNavigate } from "react-router-dom";
import { CreateProjectPayload, Job, Knobs, Query, Research, Script } from "./types";
import { GlassyCard, glassyCardSx, PrimaryButton, SecondaryButton } from "./ui";
import { CreateModal } from "./CreateModal";
import { AnalysisPanel } from "./AnalysisPanel";
import { FactCard } from "./FactCard";
import { ScriptEditor } from "./ScriptEditor";
import { RenderQueue } from "./RenderQueue";
import { RecentEpisodesPreview } from "./RecentEpisodesPreview";
import { ProjectList } from "./ProjectList";
import { usePreflightCheck } from "../../hooks/usePreflightCheck";
import { useBudgetTracking } from "../../hooks/useBudgetTracking";
import { PreflightBlockDialog } from "./PreflightBlockDialog";
import HeaderControls from "../shared/HeaderControls";

/* ================= Helpers ================= */

const DEFAULT_KNOBS: Knobs = {
  voice_emotion: "neutral",
  voice_speed: 1,
  resolution: "720p",
  scene_length_target: 45,
  sample_rate: 24000,
  bitrate: "standard",
};

const announceError = (setAnnouncement: (msg: string) => void, error: unknown) => {
  const message = error instanceof Error ? error.message : "Unexpected error";
  setAnnouncement(message);
};

/* ================= Dashboard ================= */

const PodcastDashboard: React.FC = () => {
  const navigate = useNavigate();
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
    setProject,
    setAnalysis,
    setQueries,
    setSelectedQueries,
    setResearch,
    setRawResearch,
    setEstimate,
    setScriptData,
    updateRenderJob,
    setKnobs,
    setResearchProvider,
    setBudgetCap,
    setShowScriptEditor,
    setShowRenderQueue,
    initializeProject,
    resetState,
    loadProjectFromDb,
  } = projectState;

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isResearching, setIsResearching] = useState(false);
  const [announcement, setAnnouncement] = useState("");
  const [showResumeAlert, setShowResumeAlert] = useState(false);
  const [showPreflightDialog, setShowPreflightDialog] = useState(false);
  const [preflightResponse, setPreflightResponse] = useState<any>(null);
  const [preflightOperationName, setPreflightOperationName] = useState<string>("");

  // Budget tracking
  const budgetTracking = useBudgetTracking(projectState.budgetCap || 50);
  
  // Preflight check hook
  const preflightCheck = usePreflightCheck({
    onBlocked: (response) => {
      setPreflightResponse(response);
      setShowPreflightDialog(true);
    },
  });

  // Update budget cap when project state changes
  useEffect(() => {
    if (projectState.budgetCap) {
      budgetTracking.setBudgetCap(projectState.budgetCap);
    }
  }, [projectState.budgetCap, budgetTracking]);

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

  const handleCreate = async (payload: CreateProjectPayload) => {
    // Prevent duplicate submits that can spam story setup API
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
    } catch (error) {
      announceError(setAnnouncement, error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleRunResearch = async () => {
    // Prevent duplicate research calls
    if (isResearching) return;
    if (!project) {
      setAnnouncement("Create a project first.");
      return;
    }
    if (selectedQueries.size === 0) {
      setAnnouncement("Select at least one query to research.");
      return;
    }
    
    // Preflight check before research
    setPreflightOperationName("Research");
    const approvedQueries = queries.filter((q) => selectedQueries.has(q.id));
    const preflightResult = await preflightCheck.check({
      provider: researchProvider === "exa" ? "exa" : "gemini",
      operation_type: researchProvider === "exa" ? "exa_neural_search" : "google_grounding",
      tokens_requested: researchProvider === "exa" ? 0 : 1200,
      actual_provider_name: researchProvider || "google",
    });

    if (!preflightResult.can_proceed) {
      return; // Dialog will be shown by onBlocked callback
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
          onProgress: (message) => {
            // Update announcement with progress messages
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
        
        // Provide helpful error messages
        if (errorMessage.includes("Exa") || errorMessage.includes("exa")) {
          setAnnouncement(`Deep research failed: ${errorMessage}. Try Standard Research instead.`);
        } else if (errorMessage.includes("timeout")) {
          setAnnouncement("Research timed out. Please try again with fewer queries.");
        } else {
          setAnnouncement(`Research failed: ${errorMessage}`);
        }
        
        // Log full error for debugging
        console.error("Research error:", researchError);
        throw researchError;
      }
    } catch (error) {
      announceError(setAnnouncement, error);
    } finally {
      setIsResearching(false);
    }
  };

  const handleGenerateScript = async () => {
    // Avoid re-triggering script generation preflight
    if (showScriptEditor) return;
    if (!project || !research) {
      setAnnouncement("Project or research missing — cannot generate script");
      return;
    }

    // Preflight check before script generation
    setPreflightOperationName("Script Generation");
    const preflightResult = await preflightCheck.check({
      provider: "gemini",
      operation_type: "script_generation",
      tokens_requested: 2000,
      actual_provider_name: "gemini",
    });

    if (!preflightResult.can_proceed) {
      return; // Dialog will be shown by onBlocked callback
    }

    setScriptData(null);
    setShowRenderQueue(false);
    setShowScriptEditor(true);
  };

  const handleProceedToRendering = (script: Script) => {
    setScriptData(script);
    // Initialize render jobs if empty
    if (renderJobs.length === 0) {
      script.scenes.forEach((scene) => {
        updateRenderJob(scene.id, {
          sceneId: scene.id,
          title: scene.title,
          status: "idle" as const,
          progress: 0,
          previewUrl: null,
          finalUrl: null,
          jobId: null,
        });
      });
    }
    setShowRenderQueue(true);
    setShowScriptEditor(false);
  };

  const selectedCount = selectedQueries.size;
  const canGenerateScript = Boolean(project && research && rawResearch);

  const toggleQuery = (id: string) => {
    if (isResearching) return;
    const current = selectedQueries;
    const next = new Set<string>(current);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setSelectedQueries(next);
  };

  const activeStep = useMemo(() => {
    if (showRenderQueue) return 3;
    if (showScriptEditor) return 2;
    if (research) return 1;
    if (analysis) return 0;
    return -1;
  }, [showRenderQueue, showScriptEditor, research, analysis]);

  const steps = [
    { label: "Analysis", icon: <PsychologyIcon />, description: "AI analyzes your idea" },
    { label: "Research", icon: <SearchIcon />, description: "Gather facts and citations" },
    { label: "Script", icon: <EditNoteIcon />, description: "Edit and approve scenes" },
    { label: "Render", icon: <PlayArrowIcon />, description: "Generate audio files" },
  ];

  const handleSelectProject = async (projectId: string) => {
    try {
      await loadProjectFromDb(projectId);
      setShowProjectList(false);
    } catch (error) {
      setAnnouncement(`Failed to load project: ${error instanceof Error ? error.message : "Unknown error"}`);
    }
  };

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
          <Stack direction="row" justifyContent="space-between" alignItems="flex-start" flexWrap="wrap" gap={2}>
            <Box>
              <Typography
                variant="h3"
                sx={{
                  color: "#1e293b",
                  fontWeight: 800,
                  mb: 0.5,
                  display: "flex",
                  alignItems: "center",
                  gap: 1.5,
                }}
              >
                <MicIcon fontSize="large" sx={{ color: "#667eea" }} />
                AI Podcast Maker
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Create professional podcast episodes with AI-powered research, smart scriptwriting, and natural voice narration
              </Typography>
            </Box>
            <Stack direction="row" spacing={1} alignItems="center">
              <HeaderControls colorMode="light" showAlerts={true} showUser={true} />
              <SecondaryButton onClick={() => window.open("/docs", "_blank")} startIcon={<InfoIcon />}>
                Help
              </SecondaryButton>
              <SecondaryButton
                onClick={() => navigate("/asset-library?source_module=podcast_maker&asset_type=audio")}
                startIcon={<LibraryMusicIcon />}
                tooltip="View all podcast episodes in Asset Library"
              >
                My Episodes
              </SecondaryButton>
              <SecondaryButton
                onClick={() => setShowProjectList(true)}
                startIcon={<MicIcon />}
                tooltip="View and resume saved projects"
              >
                My Projects
              </SecondaryButton>
              <PrimaryButton
                onClick={() => {
                  resetState();
                  setShowProjectList(false);
                }}
                startIcon={<AutoAwesomeIcon />}
              >
                New Episode
              </PrimaryButton>
            </Stack>
          </Stack>

          <Divider sx={{ borderColor: "rgba(0,0,0,0.08)" }} />

          {/* Progress Stepper */}
          {project && activeStep >= 0 && (
            <Paper
              sx={{
                p: 2.5,
                background: "#f8fafc",
                border: "1px solid rgba(0,0,0,0.08)",
                borderRadius: 2,
              }}
            >
              <Stepper activeStep={activeStep} orientation="horizontal" sx={{ "& .MuiStepLabel-root": { cursor: "pointer" } }}>
                {steps.map((step, index) => (
                  <Step key={step.label} completed={index < activeStep}>
                    <StepLabel
                      StepIconComponent={({ active, completed }) => (
                        <Box
                          sx={{
                            width: 40,
                            height: 40,
                            borderRadius: "50%",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            background: completed
                              ? "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
                              : active
                              ? alpha("#667eea", 0.15)
                              : "#e2e8f0",
                            border: active ? "2px solid #667eea" : "1px solid rgba(0,0,0,0.1)",
                            color: completed || active ? "#fff" : "#64748b",
                          }}
                        >
                          {completed ? <CheckCircleIcon /> : step.icon}
                        </Box>
                      )}
                    >
                      <Typography variant="subtitle2">{step.label}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {step.description}
                      </Typography>
                    </StepLabel>
                  </Step>
                ))}
              </Stepper>
            </Paper>
          )}

          {/* Resume Alert */}
          {showResumeAlert && project && (
            <Alert
              severity="success"
              onClose={() => setShowResumeAlert(false)}
              sx={{
                background: "#d1fae5",
                border: "1px solid #a7f3d0",
                "& .MuiAlert-icon": { color: "#10b981" },
              }}
            >
              <Typography variant="body2">
                <strong>Project Restored:</strong> Resuming from{" "}
                {currentStep === "analysis"
                  ? "Analysis"
                  : currentStep === "research"
                  ? "Research"
                  : currentStep === "script"
                  ? "Script Editing"
                  : "Rendering"}{" "}
                step. Your progress has been saved.
              </Typography>
            </Alert>
          )}

          {/* Announcements */}
          {announcement && (
            <Alert
              severity="info"
              onClose={() => setAnnouncement("")}
              sx={{
                background: "#dbeafe",
                border: "1px solid #bfdbfe",
                "& .MuiAlert-icon": { color: "#3b82f6" },
              }}
            >
              {announcement}
            </Alert>
          )}

          {(isAnalyzing || isResearching) && (
            <Alert
              severity="warning"
              icon={<CircularProgress size={20} />}
              sx={{
                background: "#fef3c7",
                border: "1px solid #fde68a",
              }}
            >
              <Typography variant="body2">
                {isAnalyzing ? "Analyzing your idea with AI..." : "Running research... This may take a moment."}
              </Typography>
            </Alert>
          )}

          {/* Create Modal */}
          {!project && (
            <>
              <CreateModal open onCreate={handleCreate} defaultKnobs={DEFAULT_KNOBS} isSubmitting={isAnalyzing} />
              {/* Recent Episodes Preview */}
              <RecentEpisodesPreview onSelectEpisode={() => {}} />
            </>
          )}

          {/* Main Content */}
          <Stack spacing={3}>
            {analysis && !showScriptEditor && !showRenderQueue && (
              <AnalysisPanel
                analysis={analysis}
                onRegenerate={() => setAnalysis({ ...analysis })}
              />
            )}

            {estimate && !showScriptEditor && !showRenderQueue && (
              <GlassyCard
                sx={{
                  ...glassyCardSx,
                  background: "#ffffff",
                  border: "1px solid rgba(0,0,0,0.06)",
                  boxShadow: "0 10px 28px rgba(15,23,42,0.06)",
                  color: "#0f172a",
                }}
                aria-label="estimate"
              >
                <Stack spacing={2}>
                  <Typography variant="h6" sx={{ display: "flex", alignItems: "center", gap: 1, color: "#0f172a", fontWeight: 700 }}>
                    <InsightsIcon />
                    Estimated Cost
                  </Typography>
                  <Typography variant="h4" sx={{ color: "#4f46e5", fontWeight: 800 }}>
                    ${estimate.total.toFixed(2)}
                  </Typography>
                  <Divider sx={{ borderColor: "rgba(0,0,0,0.08)" }} />
                  <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap>
                    <Chip
                      label={`Voice: $${estimate.ttsCost.toFixed(2)}`}
                      size="small"
                      title="Voice narration cost"
                      sx={{ background: "#eef2ff", color: "#0f172a", border: "1px solid rgba(0,0,0,0.06)" }}
                    />
                    <Chip
                      label={`Visuals: $${estimate.avatarCost.toFixed(2)}`}
                      size="small"
                      title="Avatar/video cost"
                      sx={{ background: "#eef2ff", color: "#0f172a", border: "1px solid rgba(0,0,0,0.06)" }}
                    />
                    <Chip
                      label={`Research: $${estimate.researchCost.toFixed(2)}`}
                      size="small"
                      title="Research and fact-checking cost"
                      sx={{ background: "#eef2ff", color: "#0f172a", border: "1px solid rgba(0,0,0,0.06)" }}
                    />
                  </Stack>
                </Stack>
              </GlassyCard>
            )}

            {queries.length > 0 && !showScriptEditor && !showRenderQueue && (
              <GlassyCard
                sx={{
                  ...glassyCardSx,
                  background: "#ffffff",
                  border: "1px solid rgba(0,0,0,0.06)",
                  boxShadow: "0 10px 28px rgba(15,23,42,0.06)",
                  color: "#0f172a",
                }}
              >
                <Stack spacing={3}>
                  <Stack direction="row" justifyContent="space-between" alignItems="center" flexWrap="wrap" gap={2}>
                    <Typography variant="h6" sx={{ display: "flex", alignItems: "center", gap: 1, color: "#0f172a", fontWeight: 700 }}>
                      <SearchIcon />
                      Research Queries
                    </Typography>
                    <Stack direction="row" spacing={2} alignItems="center">
                      <FormControl size="small" sx={{ minWidth: 180 }}>
                        <InputLabel>Provider</InputLabel>
                        <Select
                          value={researchProvider}
                          onChange={(e) => setResearchProvider(e.target.value as ResearchProvider)}
                          label="Provider"
                          disabled={isResearching}
                          size="small"
                          sx={{
                            backgroundColor: "#f8fafc",
                            "&:hover": {
                              backgroundColor: "#f1f5f9",
                            },
                          }}
                        >
                          <MenuItem value="google">
                            <Stack direction="row" spacing={1} alignItems="center">
                              <SearchIcon fontSize="small" />
                              <span>Standard Research</span>
                            </Stack>
                          </MenuItem>
                          <MenuItem value="exa">
                            <Stack direction="row" spacing={1} alignItems="center">
                              <AutoAwesomeIcon fontSize="small" />
                              <span>Deep Research</span>
                            </Stack>
                          </MenuItem>
                        </Select>
                      </FormControl>
                      <Chip
                        label={`${selectedCount} / ${queries.length} selected`}
                        size="small"
                        color={selectedCount > 0 ? "primary" : "default"}
                      />
                    </Stack>
                  </Stack>

                  <Divider sx={{ borderColor: "rgba(0,0,0,0.08)" }} />

                  <Tooltip
                    title={
                      researchProvider === "google"
                        ? "Standard Research: Fast, fact-checked results with source citations"
                        : "Deep Research: Comprehensive analysis with competitor insights and trending topics"
                    }
                    arrow
                  >
                    <Alert
                      severity="info"
                      sx={{
                        background: "#e0f2fe",
                        border: "1px solid #bae6fd",
                        color: "#0f172a",
                      }}
                    >
                      <Typography variant="caption" sx={{ color: "#0f172a" }}>
                        {researchProvider === "google"
                          ? "Select at least one query (recommended: 3+ for balanced coverage). Standard research provides fact-checked results with source citations."
                          : "Select queries for deep research. This mode provides comprehensive analysis with competitor insights and trending topics."}
                      </Typography>
                    </Alert>
                  </Tooltip>

                  <List>
                    {queries.map((q) => (
                      <ListItem key={q.id} disablePadding>
                        <ListItemButton
                          onClick={() => toggleQuery(q.id)}
                          disabled={isResearching}
                          sx={{
                            borderRadius: 2,
                            mb: 1,
                            border: "1px solid rgba(0,0,0,0.08)",
                            background: "#f8fafc",
                            "&:hover": { background: alpha("#667eea", 0.08) },
                          }}
                        >
                          <Checkbox checked={selectedQueries.has(q.id)} edge="start" />
                          <ListItemText
                            primary={q.query}
                            secondary={q.rationale}
                            primaryTypographyProps={{ variant: "body2", fontWeight: 600, color: "#0f172a" }}
                            secondaryTypographyProps={{ variant: "caption", sx: { color: "#475569" } }}
                          />
                        </ListItemButton>
                      </ListItem>
                    ))}
                  </List>

                  <Box sx={{ display: "flex", justifyContent: "flex-end" }}>
                    <PrimaryButton
                      onClick={handleRunResearch}
                      disabled={!project || selectedCount === 0 || isResearching}
                      loading={isResearching}
                      startIcon={<SearchIcon />}
                      tooltip={
                        selectedCount === 0
                          ? "Select at least one query to run research"
                          : `Run research with ${selectedCount} selected ${selectedCount === 1 ? "query" : "queries"}`
                      }
                    >
                      {isResearching ? "Running Research..." : "Run Research"}
                    </PrimaryButton>
                  </Box>
                </Stack>
              </GlassyCard>
            )}

            {research && !showScriptEditor && !showRenderQueue && (
              <GlassyCard sx={glassyCardSx}>
                <Stack spacing={3}>
                  <Stack direction="row" justifyContent="space-between" alignItems="flex-start" flexWrap="wrap" gap={2}>
                    <Box>
                      <Typography variant="h6" sx={{ display: "flex", alignItems: "center", gap: 1, mb: 0.5 }}>
                        <InsightsIcon />
                        Research Summary
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {research.summary}
                      </Typography>
                    </Box>
                    <PrimaryButton
                      onClick={handleGenerateScript}
                      disabled={!canGenerateScript}
                      startIcon={<EditNoteIcon />}
                      tooltip={!canGenerateScript ? "Complete research to generate script" : "Generate AI-powered script from research"}
                    >
                      Generate Script
                    </PrimaryButton>
                  </Stack>

                  {research.factCards.length > 0 && (
                    <>
                      <Divider sx={{ borderColor: "rgba(0,0,0,0.08)" }} />
                      <Typography variant="subtitle2" sx={{ mb: 1 }}>
                        Fact Cards ({research.factCards.length})
                      </Typography>
                      <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", sm: "1fr 1fr", lg: "1fr 1fr 1fr" }, gap: 2 }}>
                        {research.factCards.map((fact) => (
                          <FactCard key={fact.id} fact={fact} />
                        ))}
                      </Box>
                    </>
                  )}
                </Stack>
              </GlassyCard>
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
                onScriptChange={(s) => setScriptData(s)}
                onBackToResearch={() => setShowScriptEditor(false)}
                onProceedToRendering={(s) => handleProceedToRendering(s)}
                onError={(msg) => setAnnouncement(msg)}
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
                budgetCap={projectState.budgetCap}
                avatarImageUrl={null}
                onUpdateJob={updateRenderJob}
                onBack={() => {
                  setShowRenderQueue(false);
                  setShowScriptEditor(true);
                }}
                onError={(msg) => setAnnouncement(msg)}
              />
            )}
          </Stack>
        </Stack>
      </Paper>

      {/* Preflight Block Dialog */}
      <PreflightBlockDialog
        open={showPreflightDialog}
        onClose={() => {
          setShowPreflightDialog(false);
          setPreflightResponse(null);
        }}
        response={preflightResponse}
        operationName={preflightOperationName}
      />
    </Box>
  );
};

export default PodcastDashboard;
