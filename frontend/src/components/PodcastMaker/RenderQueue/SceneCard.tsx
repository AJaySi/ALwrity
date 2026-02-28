import React, { useState, useEffect } from "react";
import { Box, Stack, Typography, Alert, Paper, Chip, Divider, LinearProgress, CircularProgress, alpha, Modal, IconButton } from "@mui/material";
import {
  CheckCircle as CheckCircleIcon,
  RadioButtonUnchecked as RadioButtonUncheckedIcon,
  Info as InfoIcon,
  OpenInNew as OpenInNewIcon,
  Videocam as VideocamIcon,
  Close as CloseIcon,
  ZoomIn as ZoomInIcon,
} from "@mui/icons-material";
import { Scene, Job, VideoGenerationSettings } from "../types";
import { GlassyCard, glassyCardSx } from "../ui";
import { InlineAudioPlayer } from "../InlineAudioPlayer";
import { SceneActionButtons } from "./SceneActionButtons";
import { aiApiClient } from "../../../api/client";
import { fetchMediaBlobUrl } from "../../../utils/fetchMediaBlobUrl";
import { VideoRegenerateModal } from "./VideoRegenerateModal";

interface SceneCardProps {
  scene: Scene;
  job?: Job;
  rendering: string | null;
  generatingImage: string | null;
  isBusy: boolean;
  avatarImageUrl?: string | null;
  bible?: any;
  analysis?: any;
  onRender: (sceneId: string, mode: "preview" | "full") => void;
  onImageGenerate: (sceneId: string) => void;
  onVideoGenerate: (sceneId: string, settings: VideoGenerationSettings) => void;
  onDownloadAudio: (audioUrl: string, title: string) => void;
  onDownloadVideo: (videoUrl: string, title: string) => void;
  onShare: (audioUrl: string, title: string) => void;
  onError: (message: string) => void;
}

const getInitials = (title: string): string => {
  return title
    .split(" ")
    .slice(0, 2)
    .map((s) => s[0])
    .join("")
    .toUpperCase();
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

export const SceneCard: React.FC<SceneCardProps> = ({
  scene,
  job,
  rendering,
  generatingImage,
  isBusy,
  avatarImageUrl,
  bible,
  analysis,
  onRender,
  onImageGenerate,
  onVideoGenerate,
  onDownloadAudio,
  onDownloadVideo,
  onShare,
  onError,
}) => {
  const hasAudio = Boolean(scene.audioUrl || job?.finalUrl || job?.previewUrl);
  const hasImage = Boolean(scene.imageUrl || job?.imageUrl);
  const hasVideo = Boolean(job?.videoUrl);
  const audioUrl = job?.finalUrl || job?.previewUrl || scene.audioUrl || "";
  const imageUrl = job?.imageUrl || scene.imageUrl || "";
  const status = job?.status || (hasAudio ? "completed" : "idle");
  const initials = getInitials(scene.title);


  // Load image as blob if it's an authenticated endpoint
  const [imageBlobUrl, setImageBlobUrl] = useState<string | null>(null);
  const [videoBlobUrl, setVideoBlobUrl] = useState<string | null>(null);
  const [showVideoModal, setShowVideoModal] = useState(false);
  const [showImageModal, setShowImageModal] = useState(false);
  const [initialVideoPrompt, setInitialVideoPrompt] = useState<string>("");

  // Prepare a simple default prompt based on the scene title/description
  useEffect(() => {
    const baseTitle = (scene.title || "").trim();
    const description = (scene as any).description as string | undefined;
    const descSnippet = (description || "").split(".")[0]?.trim();
    let prompt = baseTitle;
    if (!prompt && descSnippet) {
      prompt = descSnippet;
    }
    if (!prompt) {
      prompt = "Professional podcast scene with subtle movement";
    }
    setInitialVideoPrompt(prompt);
  }, [scene]);
  
  useEffect(() => {
    if (!imageUrl) {
      setImageBlobUrl(null);
      return;
    }

    // Check if this is a podcast image endpoint that requires authentication
    const isPodcastImage = imageUrl.includes('/api/podcast/images/') || imageUrl.includes('/api/story/images/');
    
    if (!isPodcastImage) {
      // Regular URL (external), use directly
      setImageBlobUrl(imageUrl);
      return;
    }

    // Fetch as blob for authenticated endpoints
    let isMounted = true;
    const currentImageUrl = imageUrl;

    const loadImageBlob = async () => {
      try {
        // Normalize path
        let imagePath = currentImageUrl.startsWith('/') ? currentImageUrl : `/${currentImageUrl}`;
        
        // Convert /api/story/images/ to /api/podcast/images/ if needed
        if (imagePath.includes('/api/story/images/')) {
          const filename = imagePath.split('/api/story/images/').pop() || '';
          imagePath = `/api/podcast/images/${filename}`;
        }
        
        // Ensure it's a podcast image endpoint
        if (!imagePath.includes('/api/podcast/images/')) {
          const filename = imagePath.split('/').pop() || currentImageUrl;
          imagePath = `/api/podcast/images/${filename}`;
        }

        // Remove query parameters if present
        imagePath = imagePath.split('?')[0];

        const response = await aiApiClient.get(imagePath, {
          responseType: 'blob',
        });
        
        if (!isMounted || imageUrl !== currentImageUrl) {
          return;
        }
        
        const blob = response.data;
        const newBlobUrl = URL.createObjectURL(blob);
        
        setImageBlobUrl((prevBlobUrl) => {
          // Clean up previous blob URL if exists
          if (prevBlobUrl && prevBlobUrl !== newBlobUrl && prevBlobUrl.startsWith('blob:')) {
            URL.revokeObjectURL(prevBlobUrl);
          }
          return newBlobUrl;
        });
      } catch (err) {
        console.error('[SceneCard] Failed to load image blob:', err);
        if (isMounted && imageUrl === currentImageUrl) {
          // Try adding query token as fallback
          try {
            // Normalize path again for fallback
            let fallbackPath = currentImageUrl.startsWith('/') ? currentImageUrl : `/${currentImageUrl}`;
            
            // Convert /api/story/images/ to /api/podcast/images/ if needed
            if (fallbackPath.includes('/api/story/images/')) {
              const filename = fallbackPath.split('/api/story/images/').pop() || '';
              fallbackPath = `/api/podcast/images/${filename}`;
            }
            
            // Ensure it's a podcast image endpoint
            if (!fallbackPath.includes('/api/podcast/images/')) {
              const filename = fallbackPath.split('/').pop() || currentImageUrl;
              fallbackPath = `/api/podcast/images/${filename}`;
            }

            // Remove query parameters if present
            fallbackPath = fallbackPath.split('?')[0];

            // Get auth token from localStorage or use aiApiClient's default token
            const token = localStorage.getItem('clerk_dashboard_token') || '';
            if (token) {
              const urlWithToken = `${fallbackPath}?token=${encodeURIComponent(token)}`;
              setImageBlobUrl(urlWithToken);
            } else {
              // Fallback to original URL
              setImageBlobUrl(imageUrl);
            }
          } catch (fallbackErr) {
            console.error('[SceneCard] Fallback also failed:', fallbackErr);
            setImageBlobUrl(imageUrl);
          }
        }
      }
    };

    loadImageBlob();

    return () => {
      isMounted = false;
      // Cleanup blob URL when component unmounts or URL changes
      setImageBlobUrl((prevBlobUrl) => {
        if (prevBlobUrl && prevBlobUrl.startsWith('blob:')) {
          URL.revokeObjectURL(prevBlobUrl);
        }
        return null;
      });
    };
  }, [imageUrl, hasImage, scene.id]);

  // Load video as blob when videoUrl changes (using Story Writer's utility)
  useEffect(() => {
    if (!job?.videoUrl) {
      setVideoBlobUrl(null);
      return;
    }

    let currentBlobUrl: string | null = null;

    fetchMediaBlobUrl(job.videoUrl)
      .then((blobUrl) => {
        if (blobUrl) {
          currentBlobUrl = blobUrl;
          setVideoBlobUrl(blobUrl);
        } else {
          // File not found (404) - clear the blob URL
          console.warn('[SceneCard] Video file not found (404):', job.videoUrl);
          setVideoBlobUrl(null);
        }
      })
      .catch((err) => {
        console.error('[SceneCard] Failed to load video blob:', err);
        setVideoBlobUrl(null);
      });

    return () => {
      // Cleanup blob URL when component unmounts or URL changes
      if (currentBlobUrl) {
        URL.revokeObjectURL(currentBlobUrl);
      }
    };
  }, [job?.videoUrl]);

  return (
    <GlassyCard sx={glassyCardSx}>
      <Stack spacing={2}>
        {/* Header */}
        <Stack direction="row" spacing={2} alignItems="center">
          {/* Visual Avatar */}
          <Paper
            sx={{
              width: 48,
              height: 48,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              color: "#ffffff",
              fontWeight: 700,
              fontSize: "1.1rem",
              borderRadius: 2,
              boxShadow: "0 2px 8px rgba(102, 126, 234, 0.25)",
            }}
          >
            {initials}
          </Paper>

          {/* Title and Metadata */}
          <Box flex={1}>
            <Stack direction="row" alignItems="center" justifyContent="space-between" flexWrap="wrap" gap={1}>
              <Typography variant="h6" sx={{ color: "#0f172a", fontWeight: 700, fontSize: "1.05rem" }}>
                {scene.title}
              </Typography>
              
              {/* Quick Downloads */}
              <Stack direction="row" spacing={1.5} alignItems="center">
                {job?.finalUrl && (
                  <Box
                    component="a"
                    href={job.finalUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    sx={{ 
                      color: "#64748b", 
                      textDecoration: "none", 
                      display: "flex", 
                      alignItems: "center", 
                      gap: 0.5,
                      fontSize: "0.75rem",
                      fontWeight: 600,
                      "&:hover": { color: "#6366f1" }
                    }}
                  >
                    <OpenInNewIcon sx={{ fontSize: 14 }} />
                    Audio
                  </Box>
                )}
                {hasVideo && videoBlobUrl && (
                  <Box
                    component="a"
                    href={videoBlobUrl}
                    download={`${scene.title.replace(/[^a-z0-9]/gi, '_')}_video.mp4`}
                    sx={{ 
                      color: "#64748b", 
                      textDecoration: "none", 
                      display: "flex", 
                      alignItems: "center", 
                      gap: 0.5,
                      fontSize: "0.75rem",
                      fontWeight: 600,
                      "&:hover": { color: "#6366f1" }
                    }}
                  >
                    <VideocamIcon sx={{ fontSize: 14 }} />
                    Video
                  </Box>
                )}
              </Stack>
            </Stack>

            {/* Compact Metadata Row */}
            <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap" sx={{ mt: 0.5 }} useFlexGap>
              {/* Scene ID */}
              <Chip 
                label={`Scene ${scene.id.slice(-4)}`} 
                size="small" 
                sx={{ 
                  height: 20, 
                  fontSize: "0.7rem", 
                  background: alpha("#64748b", 0.08), 
                  color: "#64748b",
                  fontWeight: 600 
                }} 
              />
              
              {/* Audio Status */}
              <Chip
                label={hasAudio ? "Audio Ready" : "Needs Audio"}
                size="small"
                sx={{
                  height: 20,
                  fontSize: "0.7rem",
                  background: hasAudio ? alpha("#10b981", 0.1) : alpha("#f59e0b", 0.1),
                  color: hasAudio ? "#059669" : "#d97706",
                  fontWeight: 700,
                  border: "1px solid",
                  borderColor: hasAudio ? alpha("#10b981", 0.2) : alpha("#f59e0b", 0.2),
                }}
              />

              {/* Cost */}
              {job?.cost != null && (
                <Chip
                  label={`$${job.cost.toFixed(2)}`}
                  size="small"
                  sx={{ 
                    height: 20,
                    fontSize: "0.7rem",
                    background: alpha("#6366f1", 0.08), 
                    color: "#6366f1",
                    fontWeight: 600
                  }}
                />
              )}

              {/* Job Status (if active/failed) */}
              {job && job.status !== "idle" && (
                <Chip
                  icon={getStatusIcon(status)}
                  label={status.charAt(0).toUpperCase() + status.slice(1)}
                  size="small"
                  sx={{
                    height: 20,
                    fontSize: "0.7rem",
                    background: status === "completed" ? alpha("#10b981", 0.1) : status === "failed" ? alpha("#ef4444", 0.1) : alpha("#3b82f6", 0.1),
                    color: status === "completed" ? "#059669" : status === "failed" ? "#dc2626" : "#2563eb",
                    fontWeight: 700,
                    "& .MuiChip-icon": { fontSize: 14, color: "inherit" }
                  }}
                />
              )}
            </Stack>
          </Box>
        </Stack>

        {/* Audio Player - Now directly in header section (visual integration) */}
        {hasAudio && audioUrl && (
          <Box sx={{ width: "100%", mt: 1 }}>
            <InlineAudioPlayer audioUrl={audioUrl} title={scene.title} />
          </Box>
        )}

        {/* Progress Bar */}
        {job && job.status !== "idle" && job.status !== "completed" && (
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

        <Divider sx={{ borderColor: "rgba(15, 23, 42, 0.08)" }} />

        {/* Video Preview - Show video if available, otherwise show image */}
        {hasVideo && videoBlobUrl ? (
          <Box
            sx={{
              width: "100%",
              borderRadius: 2,
              overflow: "hidden",
              border: "2px solid rgba(56,189,248,0.5)",
              background: alpha("#0f172a", 0.85),
              position: "relative",
            }}
          >
            <Box
              component="video"
              src={videoBlobUrl}
              controls
              preload="metadata"
              sx={{
                width: "100%",
                height: "auto",
                display: "block",
                maxHeight: 420,
                objectFit: "contain",
                backgroundColor: "black",
              }}
              onError={(e) => {
                const videoElement = e.currentTarget as HTMLVideoElement;
                console.error("[SceneCard] Video failed to load:", {
                  originalUrl: job?.videoUrl,
                  networkState: videoElement.networkState,
                });
              }}
            />
            <Box
              sx={{
                position: "absolute",
                top: 8,
                right: 8,
                bgcolor: "rgba(56,189,248,0.9)",
                color: "white",
                px: 1,
                py: 0.5,
                borderRadius: 1,
                fontSize: "0.75rem",
                fontWeight: 600,
              }}
            >
              VIDEO
            </Box>
          </Box>
        ) : hasImage && (imageBlobUrl || (imageUrl && !imageUrl.includes('/api/'))) ? (
          <Box sx={{ position: "relative", width: "100%" }}>
            <Box
              sx={{
                width: "100%",
                borderRadius: 2,
                overflow: "hidden",
                border: "1px solid rgba(102,126,234,0.2)",
                background: alpha("#667eea", 0.05),
                cursor: "pointer",
                "&:hover .zoom-icon": {
                  opacity: 1,
                }
              }}
              onClick={() => setShowImageModal(true)}
            >
              <Box
                component="img"
                src={imageBlobUrl || imageUrl}
                alt={scene.title}
                sx={{
                  width: "100%",
                  height: "auto",
                  display: "block",
                  maxHeight: 400,
                  objectFit: "contain",
                  background: "#000",
                }}
                onError={(e) => {
                  console.error("[SceneCard] Image failed to load:", {
                    src: e.currentTarget.src,
                    imageUrl,
                  });
                }}
              />
              <Box
                className="zoom-icon"
                sx={{
                  position: "absolute",
                  top: "50%",
                  left: "50%",
                  transform: "translate(-50%, -50%)",
                  bgcolor: "rgba(0,0,0,0.6)",
                  color: "white",
                  borderRadius: "50%",
                  p: 1.5,
                  opacity: 0,
                  transition: "opacity 0.2s",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <ZoomInIcon sx={{ fontSize: 32 }} />
              </Box>
            </Box>
          </Box>
        ) : null}

        {/* Action Buttons */}
        <SceneActionButtons
          scene={scene}
          job={job}
          hasAudio={hasAudio}
          hasImage={hasImage}
          hasVideo={hasVideo}
          audioUrl={audioUrl}
          rendering={rendering}
          generatingImage={generatingImage}
          isBusy={isBusy}
          onRender={onRender}
          onImageGenerate={onImageGenerate}
          onVideoRender={() => setShowVideoModal(true)}
          onDownloadAudio={onDownloadAudio}
          onDownloadVideo={onDownloadVideo}
          onShare={onShare}
          onError={onError}
        />

        {/* Video Generation Settings Modal */}
        <VideoRegenerateModal
          open={showVideoModal}
          onClose={() => setShowVideoModal(false)}
          onGenerate={(settings: VideoGenerationSettings) => {
            setShowVideoModal(false);
            onVideoGenerate(scene.id, settings);
          }}
          initialPrompt={initialVideoPrompt}
          initialResolution="480p"
          initialSeed={-1}
          sceneTitle={scene.title}
          bible={bible}
          analysis={analysis}
        />
      </Stack>
    </GlassyCard>
  );
};

