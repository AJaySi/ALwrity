import React, { useCallback, useState, useEffect } from "react";
import { Box, Stack, Typography, Alert, Paper, alpha, Button, CircularProgress, LinearProgress } from "@mui/material";
import {
  PlayArrow as PlayArrowIcon,
  ArrowBack as ArrowBackIcon,
  VideoLibrary as VideoLibraryIcon,
  Download as DownloadIcon,
  CheckCircle as CheckCircleIcon,
} from "@mui/icons-material";
import { Script, Knobs, Job } from "./types";
import { SecondaryButton } from "./ui";
import { SceneCard } from "./RenderQueue/SceneCard";
import { SummaryStats } from "./RenderQueue/SummaryStats";
import { GuidancePanel } from "./RenderQueue/GuidancePanel";
import { useRenderQueue } from "./RenderQueue/useRenderQueue";
import { fetchMediaBlobUrl } from "../../utils/fetchMediaBlobUrl";

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
  const [localError, setLocalError] = useState<string>("");
  const {
    rendering,
    generatingImage,
    isBusy,
    runRender,
    runImageGeneration,
    runVideoRender,
    combiningVideos,
    combiningProgress,
    finalVideoUrl,
    combineFinalVideo,
  } = useRenderQueue({
    script,
    jobs,
    knobs,
    projectId,
    budgetCap,
    avatarImageUrl,
    onUpdateJob,
    onUpdateScript,
    onError: (msg) => {
      setLocalError(msg);
      onError(msg);
    },
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

  const allVideosReady = jobs.length > 0 && jobs.every((j) => j.videoUrl);
  
  // State for final video blob URL
  const [finalVideoBlobUrl, setFinalVideoBlobUrl] = useState<string | null>(null);
  
  // Load final video as blob when URL changes
  useEffect(() => {
    if (finalVideoUrl) {
      fetchMediaBlobUrl(finalVideoUrl)
        .then((blobUrl) => {
          if (blobUrl) {
            setFinalVideoBlobUrl(blobUrl);
          }
        })
        .catch((err) => {
          console.error("Failed to load final video blob:", err);
        });
    } else {
      setFinalVideoBlobUrl(null);
    }
  }, [finalVideoUrl]);

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

      {/* Error Display */}
      {localError && (
        <Alert 
          severity="error" 
          onClose={() => setLocalError("")}
          sx={{
            mb: 3,
            background: alpha("#ef4444", 0.1),
            border: "1px solid",
            borderColor: alpha("#ef4444", 0.3),
          }}
        >
          <Typography variant="body2" sx={{ fontWeight: 600 }}>
            ❌ {localError}
          </Typography>
        </Alert>
      )}

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
              onVideoGenerate={(sceneId, settings) => runVideoRender(sceneId, settings)}
              onDownloadAudio={handleDownloadAudio}
              onDownloadVideo={handleDownloadVideo}
              onShare={handleShare}
              onError={onError}
            />
          );
        })}
      </Stack>

      {/* Final Export Section - Show when all scene videos are ready */}
      {allVideosReady && (
        <Paper
          elevation={3}
          sx={{
            mt: 4,
            p: 4,
            background: "linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, rgba(6, 182, 212, 0.05) 100%)",
            border: "2px solid",
            borderColor: finalVideoUrl ? "success.main" : "info.light",
            borderRadius: 3,
            position: "relative",
            overflow: "hidden",
            "&::before": {
              content: '""',
              position: "absolute",
              top: 0,
              left: 0,
              right: 0,
              height: "4px",
              background: finalVideoUrl 
                ? "linear-gradient(90deg, #10b981 0%, #06b6d4 100%)"
                : "linear-gradient(90deg, #667eea 0%, #764ba2 100%)",
            },
          }}
        >
          <Stack spacing={3}>
            {/* Header */}
            <Stack direction="row" alignItems="center" spacing={2}>
              <Box
                sx={{
                  p: 1.5,
                  borderRadius: 2,
                  background: finalVideoUrl 
                    ? "linear-gradient(135deg, #10b981 0%, #059669 100%)"
                    : "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  boxShadow: "0 4px 12px rgba(102, 126, 234, 0.3)",
                }}
              >
                {finalVideoUrl ? (
                  <CheckCircleIcon sx={{ color: "white", fontSize: 32 }} />
                ) : (
                  <VideoLibraryIcon sx={{ color: "white", fontSize: 32 }} />
                )}
              </Box>
              <Box>
                <Typography 
                  variant="h5" 
                  sx={{ 
                    fontWeight: 700, 
                    color: "#0f172a",
                    mb: 0.5,
                  }}
                >
                  {finalVideoUrl ? "🎉 Final Podcast Ready!" : "🎬 Final Podcast Export"}
                </Typography>
                <Typography variant="body2" sx={{ color: "#64748b" }}>
                  {finalVideoUrl 
                    ? "Your complete podcast video is ready to download"
                    : `Combine ${script.scenes.length} scene videos into one final podcast`}
                </Typography>
              </Box>
            </Stack>

            {finalVideoUrl ? (
              <Stack spacing={3}>
                <Alert 
                  severity="success"
                  icon={<CheckCircleIcon />}
                  sx={{ 
                    background: alpha("#10b981", 0.1),
                    border: "1px solid",
                    borderColor: alpha("#10b981", 0.3),
                  }}
                >
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    ✅ Your final podcast video has been created successfully!
                  </Typography>
                </Alert>
                
                {/* Video Preview */}
                <Box
                  sx={{
                    width: "100%",
                    maxWidth: 900,
                    mx: "auto",
                    borderRadius: 2,
                    overflow: "hidden",
                    boxShadow: "0 8px 24px rgba(0, 0, 0, 0.12)",
                    border: "1px solid",
                    borderColor: alpha("#10b981", 0.2),
                  }}
                >
                  <video
                    controls
                    src={finalVideoBlobUrl || finalVideoUrl}
                    style={{
                      width: "100%",
                      display: "block",
                      backgroundColor: "#000",
                    }}
                  >
                    Your browser does not support video playback.
                  </video>
                </Box>

                {/* Download Button */}
                <Stack direction="row" spacing={2} justifyContent="center" sx={{ pt: 2 }}>
                  <Button
                    variant="contained"
                    size="large"
                    startIcon={<DownloadIcon />}
                    onClick={async () => {
                      if (finalVideoBlobUrl) {
                        const link = document.createElement("a");
                        link.href = finalVideoBlobUrl;
                        link.download = `podcast-final-${Date.now()}.mp4`;
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                      }
                    }}
                    sx={{
                      px: 4,
                      py: 1.5,
                      background: "linear-gradient(135deg, #10b981 0%, #059669 100%)",
                      boxShadow: "0 4px 12px rgba(16, 185, 129, 0.4)",
                      "&:hover": {
                        background: "linear-gradient(135deg, #059669 0%, #047857 100%)",
                        boxShadow: "0 6px 16px rgba(16, 185, 129, 0.5)",
                      },
                    }}
                  >
                    Download Final Podcast
                  </Button>
                </Stack>
              </Stack>
            ) : (
              <Stack spacing={3}>
                <Alert 
                  severity="info"
                  sx={{ 
                    background: alpha("#3b82f6", 0.08),
                    border: "1px solid",
                    borderColor: alpha("#3b82f6", 0.2),
                  }}
                >
                  <Typography variant="body2">
                    <strong>Ready to export!</strong> Click below to combine all {script.scenes.length} scene videos into your final podcast video.
                  </Typography>
                </Alert>

                {combiningVideos && (
                  <Box sx={{ width: "100%" }}>
                    <Stack direction="row" justifyContent="space-between" sx={{ mb: 1 }}>
                      <Typography variant="body2" sx={{ fontWeight: 600, color: "#0f172a" }}>
                        {combiningProgress?.message || "Combining videos..."}
                      </Typography>
                      {combiningProgress && (
                        <Typography variant="body2" sx={{ color: "#64748b", fontWeight: 600 }}>
                          {combiningProgress.progress.toFixed(0)}%
                      </Typography>
                      )}
                    </Stack>
                    <LinearProgress 
                      variant={combiningProgress ? "determinate" : "indeterminate"}
                      value={combiningProgress?.progress || 0}
                      sx={{
                        height: 8,
                        borderRadius: 4,
                        background: alpha("#667eea", 0.1),
                        "& .MuiLinearProgress-bar": {
                          background: "linear-gradient(90deg, #667eea 0%, #764ba2 100%)",
                          borderRadius: 4,
                        },
                      }}
                    />
                    {combiningProgress && combiningProgress.progress < 100 && (
                      <Typography variant="caption" sx={{ color: "#64748b", mt: 0.5, display: "block" }}>
                        Video encoding in progress. This may take a few minutes...
                      </Typography>
                    )}
                  </Box>
                )}

                <Button
                  variant="contained"
                  size="large"
                  fullWidth
                  startIcon={combiningVideos ? <CircularProgress size={20} sx={{ color: "white" }} /> : <VideoLibraryIcon />}
                  onClick={combineFinalVideo}
                  disabled={combiningVideos}
                  sx={{
                    py: 2,
                    fontSize: "1.1rem",
                    fontWeight: 700,
                    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                    boxShadow: "0 4px 12px rgba(102, 126, 234, 0.4)",
                    "&:hover": {
                      background: "linear-gradient(135deg, #5568d3 0%, #6a3f8f 100%)",
                      boxShadow: "0 6px 16px rgba(102, 126, 234, 0.5)",
                    },
                    "&:disabled": {
                      background: alpha("#667eea", 0.5),
                    },
                  }}
                >
                  {combiningVideos ? "Combining Videos..." : "Combine Scenes into Final Video"}
                </Button>
              </Stack>
            )}
          </Stack>
        </Paper>
      )}

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
            {allVideosReady ? (
              <Stack spacing={1} alignItems="flex-end">
                <Typography variant="body1" sx={{ color: "#10b981", fontWeight: 700, fontSize: "1rem" }}>
                  🎉 All scene videos ready!
                </Typography>
                <Typography variant="body2" sx={{ color: "#64748b" }}>
                  Scroll up to combine them into your final podcast video.
                </Typography>
              </Stack>
            ) : allScenesCompleted ? (
              <Stack spacing={1} alignItems="flex-end">
                <Typography variant="body1" sx={{ color: "#10b981", fontWeight: 700, fontSize: "1rem" }}>
                  🎉 All scenes ready for video generation!
                </Typography>
                <Typography variant="body2" sx={{ color: "#64748b" }}>
                  Generate videos for individual scenes above.
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
