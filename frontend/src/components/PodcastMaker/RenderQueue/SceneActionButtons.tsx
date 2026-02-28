import React from "react";
import { Stack, alpha } from "@mui/material";
import {
  VolumeUp as VolumeUpIcon,
  Image as ImageIcon,
  Videocam as VideocamIcon,
  Download as DownloadIcon,
  Share as ShareIcon,
  PlayArrow as PlayArrowIcon,
  Refresh as RefreshIcon,
} from "@mui/icons-material";
import { Scene, Job } from "../types";
import { PrimaryButton, SecondaryButton } from "../ui";
import { Typography } from "@mui/material"; // Import Typography

interface SceneActionButtonsProps {
  scene: Scene;
  job?: Job;
  hasAudio: boolean;
  hasImage: boolean;
  hasVideo: boolean;
  audioUrl: string;
  rendering: string | null;
  generatingImage: string | null;
  isBusy: boolean;
  onRender: (sceneId: string, mode: "preview" | "full") => void;
  onImageGenerate: (sceneId: string) => void;
  onVideoRender: (sceneId: string) => void;
  onDownloadAudio: (audioUrl: string, title: string) => void;
  onDownloadVideo: (videoUrl: string, title: string) => void;
  onShare: (audioUrl: string, title: string) => void;
  onError: (message: string) => void;
}

export const SceneActionButtons: React.FC<SceneActionButtonsProps> = ({
  scene,
  job,
  hasAudio,
  hasImage,
  hasVideo,
  audioUrl,
  rendering,
  generatingImage,
  isBusy,
  onRender,
  onImageGenerate,
  onVideoRender,
  onDownloadAudio,
  onDownloadVideo,
  onShare,
  onError,
}) => {
  const isGeneratingImage = generatingImage === scene.id;
  const needsAudio = !hasAudio && (!job || job.status === "idle");

  // No audio - show generate buttons
  if (needsAudio) {
    return (
      <Stack direction="row" spacing={1} justifyContent="flex-end">
        <SecondaryButton
          onClick={() => onRender(scene.id, "preview")}
          disabled={isBusy}
          startIcon={<VolumeUpIcon />}
          tooltip="Preview a sample to test voice and pacing"
        >
          Preview Sample
        </SecondaryButton>
        <PrimaryButton
          onClick={() => onRender(scene.id, "full")}
          disabled={isBusy}
          startIcon={<PlayArrowIcon />}
          tooltip="Generate the complete, production-ready audio for this scene"
        >
          Generate Audio
        </PrimaryButton>
      </Stack>
    );
  }

  // Video generation failed - show specific retry for video
  if (job?.status === "failed" && !needsAudio && hasAudio) {
    return (
      <Stack direction="row" spacing={1} justifyContent="flex-end">
        <Typography variant="caption" color="error" sx={{ alignSelf: "center", mr: 1 }}>
          Video Generation Failed
        </Typography>
        <SecondaryButton
          onClick={() => onVideoRender(scene.id)}
          startIcon={<RefreshIcon />}
          tooltip="Retry video generation"
          sx={{ borderColor: "error.main", color: "error.main" }}
        >
          Retry Video
        </SecondaryButton>
      </Stack>
    );
  }

  // Failed (Audio) - show retry
  if (job?.status === "failed") {
    return (
      <Stack direction="row" spacing={1} justifyContent="flex-end">
        <SecondaryButton
          onClick={() => onRender(scene.id, "full")}
          startIcon={<RefreshIcon />}
          tooltip="Retry audio generation"
        >
          Retry Audio
        </SecondaryButton>
      </Stack>
    );
  }

  // Has audio - show all action buttons
  const videoInProgress = rendering !== null;
  const isCurrentVideo = rendering === scene.id;

  return (
    <Stack direction="row" spacing={1.5} justifyContent="flex-end" flexWrap="wrap" useFlexGap>
      {/* Generate/Regenerate Image - ALWAYS visible if we have audio */}
      <PrimaryButton
        onClick={() => onImageGenerate(scene.id)}
        disabled={isGeneratingImage}
        loading={isGeneratingImage}
        startIcon={<ImageIcon />}
        tooltip={
          isGeneratingImage
            ? "Generating image..."
            : hasImage
            ? "Regenerate image for this scene"
            : "Generate image for video (optional)"
        }
        sx={{ 
          minWidth: 160,
          // Use secondary style if image exists (to de-emphasize), primary if needed
          background: hasImage ? alpha("#667eea", 0.1) : undefined,
          color: hasImage ? "#667eea" : undefined,
          border: hasImage ? "1px solid rgba(102,126,234,0.3)" : undefined,
          "&:hover": {
             background: hasImage ? alpha("#667eea", 0.2) : undefined,
          }
        }}
      >
        {isGeneratingImage ? "Generating..." : hasImage ? "Regenerate Image" : "Generate Image"}
      </PrimaryButton>

      {/* Generate Video - ALWAYS visible if we have audio */}
      <PrimaryButton
        onClick={() => {
          onVideoRender(scene.id);
        }}
        disabled={isBusy || videoInProgress || !hasImage}
        startIcon={<VideocamIcon />}
        tooltip={
          !hasImage
            ? "Generate an image first to create video"
            : videoInProgress
            ? "A video generation is already running. Please wait..."
            : isBusy
            ? "Another operation in progress"
            : hasVideo 
            ? "Regenerate video"
            : "Generate video for this scene"
        }
        sx={{ minWidth: 180 }}
      >
        {videoInProgress && isCurrentVideo
          ? "Generating Video..."
          : hasVideo
          ? "Regenerate Video"
          : "Generate Video"}
      </PrimaryButton>

      {/* Download Video */}
      {hasVideo && job?.videoUrl && (
        <SecondaryButton
          onClick={() => onDownloadVideo(job.videoUrl!, scene.title)}
          startIcon={<VideocamIcon />}
          tooltip="Download video file"
        >
          Download Video
        </SecondaryButton>
      )}

      {/* Download Audio */}
      {hasAudio && audioUrl && (
        <PrimaryButton
          onClick={() => onDownloadAudio(audioUrl, scene.title)}
          startIcon={<DownloadIcon />}
          tooltip="Download audio file"
          sx={{
            minWidth: 40,
            width: 40,
            padding: 0,
            background: alpha("#64748b", 0.1),
            color: "#64748b",
            border: "1px solid rgba(100, 116, 139, 0.2)",
            "&:hover": {
              background: alpha("#64748b", 0.2),
            },
          }}
        >
          {/* Icon only */}
        </PrimaryButton>
      )}

      {/* Share */}
      {hasAudio && audioUrl && (
        <PrimaryButton
          onClick={() => onShare(audioUrl, scene.title)}
          startIcon={<ShareIcon />}
          tooltip="Share audio link"
          sx={{
            minWidth: 40,
            width: 40,
            padding: 0,
            background: alpha("#64748b", 0.1),
            color: "#64748b",
            border: "1px solid rgba(100, 116, 139, 0.2)",
            "&:hover": {
              background: alpha("#64748b", 0.2),
            },
          }}
        >
          {/* Icon only */}
        </PrimaryButton>
      )}
    </Stack>
  );
};

