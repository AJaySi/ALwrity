import React from "react";
import { Stack } from "@mui/material";
import {
  VolumeUp as VolumeUpIcon,
  PlayArrow as PlayArrowIcon,
  Refresh as RefreshIcon,
  Image as ImageIcon,
  Videocam as VideocamIcon,
  Download as DownloadIcon,
  Share as ShareIcon,
} from "@mui/icons-material";
import { Scene, Job } from "../types";
import { PrimaryButton, SecondaryButton } from "../ui";

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

  // Failed - show retry
  if (job?.status === "failed") {
    return (
      <Stack direction="row" spacing={1} justifyContent="flex-end">
        <SecondaryButton
          onClick={() => onRender(scene.id, "full")}
          startIcon={<RefreshIcon />}
          tooltip="Retry audio generation"
        >
          Retry
        </SecondaryButton>
      </Stack>
    );
  }

  // Has audio - show all action buttons
  return (
    <Stack direction="row" spacing={1.5} justifyContent="flex-end" flexWrap="wrap" useFlexGap>
      {/* Generate Image */}
      <PrimaryButton
        onClick={() => onImageGenerate(scene.id)}
        disabled={isGeneratingImage || hasImage}
        loading={isGeneratingImage}
        startIcon={<ImageIcon />}
        tooltip={
          hasImage
            ? "Image already generated for this scene"
            : isGeneratingImage
            ? "Generating image..."
            : "Generate image for video (optional)"
        }
        sx={{ minWidth: 160 }}
      >
        {isGeneratingImage ? "Generating..." : hasImage ? "Image Ready" : "Generate Image"}
      </PrimaryButton>

      {/* Generate Video */}
      <PrimaryButton
        onClick={() => onVideoRender(scene.id)}
        disabled={isBusy || !hasImage || hasVideo}
        startIcon={<VideocamIcon />}
        tooltip={
          hasVideo
            ? "Video already generated"
            : !hasImage
            ? "Generate an image first to create video"
            : isBusy
            ? "Another operation in progress"
            : "Generate video for this scene"
        }
        sx={{ minWidth: 160 }}
      >
        {hasVideo ? "Video Ready" : "Generate Video"}
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
      <SecondaryButton
        onClick={() => {
          if (!audioUrl) {
            onError("Audio URL not found. Please regenerate audio.");
            return;
          }
          onDownloadAudio(audioUrl, scene.title);
        }}
        startIcon={<DownloadIcon />}
        tooltip={hasAudio ? "Download this scene's audio file" : "No audio available. Generate audio first."}
        disabled={!hasAudio}
      >
        Download Audio
      </SecondaryButton>

      {/* Share */}
      <SecondaryButton
        onClick={() => {
          if (!audioUrl) {
            onError("Audio URL not found. Please regenerate audio.");
            return;
          }
          onShare(audioUrl, scene.title);
        }}
        startIcon={<ShareIcon />}
        tooltip={hasAudio ? "Share this scene's audio" : "No audio available. Generate audio first."}
        disabled={!hasAudio}
      >
        Share
      </SecondaryButton>
    </Stack>
  );
};

