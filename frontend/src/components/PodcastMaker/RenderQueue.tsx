import React, { useEffect, useState, useRef } from "react";
import { Box, Stack, Typography, Alert, Paper, Chip, Divider, LinearProgress, Button, CircularProgress, alpha } from "@mui/material";
import {
  PlayArrow as PlayArrowIcon,
  ArrowBack as ArrowBackIcon,
  VolumeUp as VolumeUpIcon,
  CheckCircle as CheckCircleIcon,
  RadioButtonUnchecked as RadioButtonUncheckedIcon,
  Info as InfoIcon,
  OpenInNew as OpenInNewIcon,
  Download as DownloadIcon,
  Share as ShareIcon,
  Refresh as RefreshIcon,
  Videocam as VideocamIcon,
  Cancel as CancelIcon,
} from "@mui/icons-material";
import { Script, Knobs, Job, RenderJobResult, TaskStatus } from "./types";
import { podcastApi } from "../../services/podcastApi";
import { GlassyCard, glassyCardSx, PrimaryButton, SecondaryButton } from "./ui";
import { InlineAudioPlayer } from "./InlineAudioPlayer";

interface RenderQueueProps {
  projectId: string;
  script: Script;
  knobs: Knobs;
  jobs: Job[];
  budgetCap?: number;
  avatarImageUrl?: string | null;
  onUpdateJob: (sceneId: string, updates: Partial<Job>) => void;
  onBack: () => void;
  onError: (message: string) => void;
}

const getSceneVoiceEmotion = (knobs: Knobs) => knobs.voice_emotion || "neutral";

export const RenderQueue: React.FC<RenderQueueProps> = ({ projectId, script, knobs, jobs, budgetCap, avatarImageUrl, onUpdateJob, onBack, onError }) => {
  const [rendering, setRendering] = useState<string | null>(null);
  const pollingIntervals = useRef<Map<string, NodeJS.Timeout>>(new Map());
  const isBusy = Boolean(rendering);

  // Cleanup polling intervals on unmount
  useEffect(() => {
    return () => {
      pollingIntervals.current.forEach((interval) => clearInterval(interval));
      pollingIntervals.current.clear();
    };
  }, []);

  // Initialize jobs if empty
  useEffect(() => {
    if (jobs.length === 0 && script.scenes.length > 0) {
      const initialJobs: Job[] = script.scenes.map((s) => ({
        sceneId: s.id,
        title: s.title,
        status: "idle" as const,
        progress: 0,
        previewUrl: null,
        finalUrl: null,
        jobId: null,
      }));
      // Update all jobs at once
      initialJobs.forEach((job) => {
        onUpdateJob(job.sceneId, job);
      });
    }
  }, [script.scenes.length, jobs.length, onUpdateJob]);

  const getScene = (sceneId: string) => script.scenes.find((s) => s.id === sceneId);

  const pollTaskStatus = async (taskId: string, sceneId: string) => {
    try {
      const status: TaskStatus = await podcastApi.pollTaskStatus(taskId);
      
      onUpdateJob(sceneId, {
        progress: status.progress ?? 0,
        status: status.status === "completed" ? "completed" : status.status === "failed" ? "failed" : "running",
      });

      if (status.status === "completed" && status.result) {
        const result = status.result;
        const updates: Partial<Job> = {
          status: "completed",
          progress: 100,
          videoUrl: result.video_url,
          cost: result.cost,
        };
        onUpdateJob(sceneId, updates);
        
        // Clear polling interval
        const interval = pollingIntervals.current.get(sceneId);
        if (interval) {
          clearInterval(interval);
          pollingIntervals.current.delete(sceneId);
        }
      } else if (status.status === "failed") {
        onUpdateJob(sceneId, { status: "failed", progress: 0 });
        
        // Clear polling interval
        const interval = pollingIntervals.current.get(sceneId);
        if (interval) {
          clearInterval(interval);
          pollingIntervals.current.delete(sceneId);
        }
        
        onError(status.error || "Video generation failed");
      }
      
      return status.status === "completed" || status.status === "failed";
    } catch (error) {
      console.error("Error polling task status:", error);
      return false;
    }
  };

  const startPolling = (taskId: string, sceneId: string) => {
    // Clear any existing interval for this scene
    const existingInterval = pollingIntervals.current.get(sceneId);
    if (existingInterval) {
      clearInterval(existingInterval);
    }

    // Poll every 3 seconds
    const interval = setInterval(async () => {
      const isComplete = await pollTaskStatus(taskId, sceneId);
      if (isComplete) {
        clearInterval(interval);
        pollingIntervals.current.delete(sceneId);
      }
    }, 3000);

    pollingIntervals.current.set(sceneId, interval);
  };

  const cancelRender = async (sceneId: string) => {
    const job = jobs.find((j) => j.sceneId === sceneId);
    if (job?.taskId) {
      try {
        await podcastApi.cancelTask(job.taskId);
        onUpdateJob(sceneId, { status: "cancelled", progress: 0 });
        
        // Clear polling interval
        const interval = pollingIntervals.current.get(sceneId);
        if (interval) {
          clearInterval(interval);
          pollingIntervals.current.delete(sceneId);
        }
      } catch (error) {
        console.error("Error cancelling task:", error);
        onError("Failed to cancel render job");
      }
    }
  };

  const runRender = async (sceneId: string, mode: "preview" | "full") => {
    // Prevent double-fire while another render is in-flight
    if (rendering && rendering !== sceneId) return;
    const job = jobs.find((j) => j.sceneId === sceneId);
    if (job && job.status !== "idle") return;
    const scene = getScene(sceneId);
    if (!scene) return;

    // Estimate cost (rough estimate: ~$0.05 per 1000 chars)
    const textLength = scene.lines.map((l) => l.text).join(" ").length;
    const estimatedCost = (textLength / 1000) * 0.05;

    // Check budget cap if provided
    if (budgetCap && budgetCap > 0) {
      const currentSpent = jobs
        .filter((j) => j.status === "completed" && j.cost)
        .reduce((sum, j) => sum + (j.cost || 0), 0);
      
      if (currentSpent + estimatedCost > budgetCap) {
        onError(`Budget cap exceeded. Estimated cost: $${estimatedCost.toFixed(4)}, Budget remaining: $${(budgetCap - currentSpent).toFixed(2)}`);
        return;
      }
    }

    setRendering(sceneId);
    onUpdateJob(sceneId, {
      status: mode === "preview" ? "previewing" : "running",
      progress: mode === "preview" ? 25 : 40,
    });
    try {
      const result: RenderJobResult = await podcastApi.renderSceneAudio({
        scene,
        voiceId: "Wise_Woman",
        emotion: getSceneVoiceEmotion(knobs),
        speed: knobs.voice_speed,
      });

      const updates: Partial<Job> = {
        status: "completed",
        progress: 100,
        cost: result.cost,
        provider: result.provider,
        voiceId: result.voiceId,
        fileSize: result.fileSize,
      };

      if (mode === "preview") {
        updates.previewUrl = result.audioUrl;
        window.open(result.audioUrl, "_blank");
      } else {
        updates.finalUrl = result.audioUrl;

        // Save to asset library when final render completes
        try {
          await podcastApi.saveAudioToAssetLibrary({
            audioUrl: result.audioUrl,
            filename: result.audioFilename,
            title: `${script.scenes.find((s) => s.id === sceneId)?.title || "Scene"} - ${projectId}`,
            description: `Podcast episode scene audio: ${scene.title}`,
            projectId,
            sceneId,
            cost: result.cost,
            provider: result.provider,
            model: result.model,
            fileSize: result.fileSize,
          });
        } catch (assetError) {
          console.error("Failed to save to asset library:", assetError);
          // Don't fail the render if asset save fails
        }
      }

      onUpdateJob(sceneId, updates);
    } catch (error) {
      onUpdateJob(sceneId, { status: "failed", progress: 0 });
      const message = error instanceof Error ? error.message : "Render failed";
      onError(message);
    } finally {
      setRendering(null);
    }
  };

  const runVideoRender = async (sceneId: string) => {
    // Prevent double-fire while another render is in-flight
    if (rendering && rendering !== sceneId) return;
    const scene = getScene(sceneId);
    if (!scene) return;

    if (!avatarImageUrl) {
      onError("Avatar image is required for video generation. Please upload an avatar image in project settings.");
      return;
    }

    const job = jobs.find((j) => j.sceneId === sceneId);
    if (!job?.finalUrl) {
      onError("Please generate audio first before creating video.");
      return;
    }

    // Estimate cost (video generation is ~$0.30 per 5 seconds at 720p)
    const estimatedCost = 0.30; // Base cost per video

    // Check budget cap if provided
    if (budgetCap && budgetCap > 0) {
      const currentSpent = jobs
        .filter((j) => j.status === "completed" && j.cost)
        .reduce((sum, j) => sum + (j.cost || 0), 0);
      
      if (currentSpent + estimatedCost > budgetCap) {
        onError(`Budget cap exceeded. Estimated cost: $${estimatedCost.toFixed(2)}, Budget remaining: $${(budgetCap - currentSpent).toFixed(2)}`);
        return;
      }
    }

    setRendering(sceneId);
    onUpdateJob(sceneId, {
      status: "running",
      progress: 5,
    });

    try {
      const result = await podcastApi.generateVideo({
        projectId,
        sceneId,
        sceneTitle: scene.title,
        audioUrl: job.finalUrl,
        avatarImageUrl: avatarImageUrl,
        resolution: knobs.resolution || "720p",
      });

      // Start polling for video generation status
      onUpdateJob(sceneId, {
        taskId: result.taskId,
        status: "running",
        progress: 5,
      });

      startPolling(result.taskId, sceneId);
    } catch (error) {
      onUpdateJob(sceneId, { status: "failed", progress: 0 });
      const message = error instanceof Error ? error.message : "Video generation failed";
      onError(message);
    } finally {
      setRendering(null);
    }
  };

  const getStatusColor = (status: Job["status"]) => {
    switch (status) {
      case "completed":
        return "success";
      case "failed":
        return "error";
      case "running":
      case "previewing":
        return "info";
      default:
        return "default";
    }
  };

  const getStatusIcon = (status: Job["status"]) => {
    switch (status) {
      case "completed":
        return <CheckCircleIcon />;
      case "failed":
        return <InfoIcon />;
      case "running":
      case "previewing":
        return <CircularProgress size={16} />;
      default:
        return <RadioButtonUncheckedIcon />;
    }
  };

  return (
    <Box sx={{ mt: 3 }}>
      <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 3 }}>
        <SecondaryButton onClick={onBack} startIcon={<ArrowBackIcon />}>
          Back to Script
        </SecondaryButton>
        <Typography
          variant="h4"
          sx={{
            background: "linear-gradient(135deg, #a78bfa 0%, #60a5fa 100%)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            fontWeight: 800,
            display: "flex",
            alignItems: "center",
            gap: 1,
          }}
        >
          <PlayArrowIcon />
          Render Queue
        </Typography>
      </Stack>

      <Alert severity="info" sx={{ mb: 3, background: alpha("#3b82f6", 0.1), border: "1px solid rgba(59,130,246,0.3)" }}>
        <Typography variant="body2">
          <strong>Audio Generation:</strong> Preview creates a quick sample to test voice and pacing. Full render generates the complete, production-ready audio file for your episode.
        </Typography>
      </Alert>

      <Stack spacing={2}>
        {jobs.map((job) => {
          const scene = getScene(job.sceneId);
          const initials = job.title
            .split(" ")
            .slice(0, 2)
            .map((s) => s[0])
            .join("")
            .toUpperCase();

          return (
            <GlassyCard key={job.sceneId} sx={glassyCardSx}>
              <Stack spacing={2}>
                <Stack direction="row" spacing={2} alignItems="flex-start">
                  <Paper
                    sx={{
                      width: 56,
                      height: 56,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      background: alpha("#667eea", 0.2),
                      border: "1px solid rgba(102,126,234,0.3)",
                      fontWeight: 700,
                      fontSize: "1.2rem",
                    }}
                  >
                    {initials}
                  </Paper>
                  <Box flex={1}>
                    <Typography variant="h6" sx={{ mb: 0.5 }}>
                      {job.title}
                    </Typography>
                    <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap" useFlexGap>
                      <Chip label={`Scene ${job.sceneId.slice(-4)}`} size="small" variant="outlined" />
                      {job.cost != null && (
                        <Chip
                          label={`$${job.cost.toFixed(2)}`}
                          size="small"
                          sx={{ background: alpha("#10b981", 0.2), color: "#6ee7b7" }}
                          title="Generation cost"
                        />
                      )}
                      {job.fileSize && (
                        <Typography variant="caption" color="text.secondary">
                          {(job.fileSize / 1024).toFixed(1)} KB
                        </Typography>
                      )}
                    </Stack>
                    {job.finalUrl && (
                      <Button
                        size="small"
                        startIcon={<OpenInNewIcon />}
                        href={job.finalUrl}
                        target="_blank"
                        sx={{ mt: 1, color: "#a78bfa" }}
                      >
                        Download Final Audio
                      </Button>
                    )}
                    {job.videoUrl && (
                      <Button
                        size="small"
                        startIcon={<VideocamIcon />}
                        href={job.videoUrl}
                        target="_blank"
                        sx={{ mt: 1, ml: 1, color: "#a78bfa" }}
                      >
                        Download Video
                      </Button>
                    )}
                  </Box>
                  <Chip
                    icon={getStatusIcon(job.status)}
                    label={job.status.charAt(0).toUpperCase() + job.status.slice(1)}
                    color={getStatusColor(job.status)}
                    size="small"
                    sx={{
                      textTransform: "capitalize",
                      minWidth: 100,
                    }}
                  />
                </Stack>

                {job.status !== "idle" && job.status !== "completed" && (
                  <Box>
                    <Stack direction="row" justifyContent="space-between" sx={{ mb: 0.5 }}>
                      <Typography variant="caption" color="text.secondary">
                        Progress
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {job.progress}%
                      </Typography>
                    </Stack>
                    <LinearProgress
                      variant="determinate"
                      value={job.progress}
                      sx={{
                        height: 8,
                        borderRadius: 4,
                        background: alpha("#fff", 0.1),
                        "& .MuiLinearProgress-bar": {
                          background: "linear-gradient(90deg, #667eea 0%, #764ba2 100%)",
                        },
                      }}
                    />
                  </Box>
                )}

                <Divider sx={{ borderColor: "rgba(255,255,255,0.1)" }} />

                <Stack direction="row" spacing={1} justifyContent="flex-end">
                  {job.status === "idle" && (
                    <>
                      <SecondaryButton
                        onClick={() => runRender(job.sceneId, "preview")}
                        disabled={isBusy}
                        startIcon={<VolumeUpIcon />}
                        tooltip="Preview a sample to test voice and pacing before generating the full episode"
                      >
                        Preview Sample
                      </SecondaryButton>
                      <PrimaryButton
                        onClick={() => runRender(job.sceneId, "full")}
                        disabled={isBusy}
                        startIcon={<PlayArrowIcon />}
                        tooltip="Generate the complete, production-ready audio for this scene"
                      >
                        Generate Audio
                      </PrimaryButton>
                    </>
                  )}
                  {job.status === "completed" && (job.previewUrl || job.finalUrl) && (
                    <Stack spacing={1} sx={{ width: "100%" }}>
                      <InlineAudioPlayer audioUrl={job.finalUrl || job.previewUrl || ""} title={job.title} />
                      <Stack direction="row" spacing={1} justifyContent="flex-end">
                        <Button
                          size="small"
                          variant="outlined"
                          startIcon={<DownloadIcon />}
                          onClick={() => {
                            const link = document.createElement("a");
                            link.href = job.finalUrl || job.previewUrl || "";
                            link.download = `${job.title.replace(/\s+/g, "-")}.mp3`;
                            link.click();
                          }}
                        >
                          Download
                        </Button>
                        <Button
                          size="small"
                          variant="outlined"
                          startIcon={<ShareIcon />}
                          onClick={async () => {
                            if (navigator.share && job.finalUrl) {
                              try {
                                await navigator.share({
                                  title: job.title,
                                  text: `Check out this podcast episode: ${job.title}`,
                                  url: job.finalUrl,
                                });
                              } catch (err) {
                                // User cancelled or error
                              }
                            } else {
                              // Fallback: copy to clipboard
                              await navigator.clipboard.writeText(job.finalUrl || job.previewUrl || "");
                              alert("Audio URL copied to clipboard!");
                            }
                          }}
                        >
                          Share
                        </Button>
                      </Stack>
                    </Stack>
                  )}
                  {job.status === "failed" && (
                    <Button variant="outlined" color="warning" onClick={() => runRender(job.sceneId, "full")} startIcon={<RefreshIcon />}>
                      Retry
                    </Button>
                  )}
                </Stack>
              </Stack>
            </GlassyCard>
          );
        })}
      </Stack>

      <Box sx={{ mt: 3, display: "flex", justifyContent: "flex-end" }}>
        <SecondaryButton onClick={onBack}>Done</SecondaryButton>
      </Box>
    </Box>
  );
};

