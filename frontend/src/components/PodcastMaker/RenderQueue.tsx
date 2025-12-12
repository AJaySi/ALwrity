import React, { useCallback } from "react";
import { Box, Stack, Typography, Alert, Paper, alpha } from "@mui/material";
import {
  PlayArrow as PlayArrowIcon,
  ArrowBack as ArrowBackIcon,
} from "@mui/icons-material";
import { Script, Knobs, Job } from "./types";
import { SecondaryButton } from "./ui";
import { SceneCard } from "./RenderQueue/SceneCard";
import { SummaryStats } from "./RenderQueue/SummaryStats";
import { GuidancePanel } from "./RenderQueue/GuidancePanel";
import { useRenderQueue } from "./RenderQueue/useRenderQueue";

interface RenderQueueProps {
  projectId: string;
  script: Script;
  knobs: Knobs;
  jobs: Job[];
  budgetCap?: number;
  avatarImageUrl?: string | null;
  onUpdateJob: (sceneId: string, updates: Partial<Job>) => void;
  onUpdateScript?: (script: Script) => void;
  onBack: () => void;
  onError: (message: string) => void;
}

export const RenderQueue: React.FC<RenderQueueProps> = ({
  projectId,
  script,
  knobs,
  jobs,
  budgetCap,
  avatarImageUrl,
  onUpdateJob,
  onUpdateScript,
  onBack,
  onError,
}) => {
  const {
    rendering,
    generatingImage,
    isBusy,
    runRender,
    runImageGeneration,
    runVideoRender,
  } = useRenderQueue({
    script,
    jobs,
    knobs,
    projectId,
    budgetCap,
    avatarImageUrl,
    onUpdateJob,
    onUpdateScript,
    onError,
  });

  const handleDownloadAudio = useCallback((audioUrl: string, title: string) => {
    const link = document.createElement("a");
    link.href = audioUrl;
    link.download = `${title.replace(/\s+/g, "-")}.mp3`;
    link.click();
  }, []);

  const handleDownloadVideo = useCallback((videoUrl: string, title: string) => {
    const link = document.createElement("a");
    link.href = videoUrl;
    link.download = `${title.replace(/\s+/g, "-")}.mp4`;
    link.click();
  }, []);

  const handleShare = useCallback(async (audioUrl: string, title: string) => {
    if (navigator.share && audioUrl) {
      try {
        await navigator.share({
          title,
          text: `Check out this podcast episode: ${title}`,
          url: audioUrl,
        });
      } catch (err) {
        // User cancelled or error
      }
    } else {
      // Fallback: copy to clipboard
      await navigator.clipboard.writeText(audioUrl);
      alert("Audio URL copied to clipboard!");
    }
  }, []);

  const allScenesCompleted =
    (jobs.length > 0 && jobs.every((j) => j.status === "completed" && j.imageUrl)) ||
    (script.scenes.length > 0 && script.scenes.every((s) => s.audioUrl && s.imageUrl));

  return (
    <Box sx={{ mt: 3 }}>
      {/* Header */}
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

      {/* Info Alert */}
      <Alert severity="info" sx={{ mb: 3, background: alpha("#3b82f6", 0.1), border: "1px solid rgba(59,130,246,0.3)" }}>
        <Typography variant="body2">
          <strong>Audio Generation:</strong> Preview creates a quick sample to test voice and pacing. Full render generates the complete, production-ready audio file for your episode.
        </Typography>
      </Alert>

      {/* Summary Stats */}
      <SummaryStats jobs={jobs} scenes={script.scenes} />

      {/* Empty State */}
      {jobs.length === 0 && script.scenes.length === 0 && (
        <Paper
          sx={{
            p: 4,
            textAlign: "center",
            background: "linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%)",
            border: "2px dashed rgba(102, 126, 234, 0.3)",
            borderRadius: 2,
          }}
        >
          <Typography variant="h6" sx={{ color: "#0f172a", fontWeight: 600, mb: 1 }}>
            No scenes to render
          </Typography>
          <Typography variant="body2" sx={{ color: "#64748b", mb: 3 }}>
            Go back to the script editor to generate and approve scenes first.
          </Typography>
          <SecondaryButton onClick={onBack} startIcon={<ArrowBackIcon />}>
            Back to Script Editor
          </SecondaryButton>
        </Paper>
      )}

      {/* Guidance Panel */}
      {script.scenes.length > 0 && <GuidancePanel scenes={script.scenes} />}

      {/* Scene Cards */}
      <Stack spacing={2}>
        {script.scenes.map((scene) => {
          const job = jobs.find((j) => j.sceneId === scene.id);
          return (
            <SceneCard
              key={scene.id}
              scene={scene}
              job={job}
              rendering={rendering}
              generatingImage={generatingImage}
              isBusy={isBusy}
              avatarImageUrl={avatarImageUrl}
              onRender={runRender}
              onImageGenerate={runImageGeneration}
              onVideoRender={runVideoRender}
              onDownloadAudio={handleDownloadAudio}
              onDownloadVideo={handleDownloadVideo}
              onShare={handleShare}
              onError={onError}
            />
          );
        })}
      </Stack>

      {/* Footer - Video Generation Focus */}
      <Paper
        sx={{
          mt: 4,
          p: 3,
          background: "linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%)",
          border: "1px solid rgba(102, 126, 234, 0.15)",
          borderRadius: 2,
        }}
      >
        <Stack spacing={2}>
          <Stack direction="row" justifyContent="space-between" alignItems="center" flexWrap="wrap" spacing={2}>
            <SecondaryButton onClick={onBack} startIcon={<ArrowBackIcon />}>
              Back to Script
            </SecondaryButton>
            {allScenesCompleted ? (
              <Stack spacing={1} alignItems="flex-end">
                <Typography variant="body1" sx={{ color: "#10b981", fontWeight: 700, fontSize: "1rem" }}>
                  🎉 All scenes ready for video generation!
                </Typography>
                <Typography variant="body2" sx={{ color: "#64748b" }}>
                  Generate videos for individual scenes or download them.
                </Typography>
              </Stack>
            ) : (
              <Typography variant="body2" sx={{ color: "#64748b" }}>
                Complete audio and image generation for all scenes to enable video generation.
              </Typography>
            )}
          </Stack>
        </Stack>
      </Paper>
    </Box>
  );
};
