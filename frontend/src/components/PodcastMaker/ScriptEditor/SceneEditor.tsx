import React, { useState, useEffect } from "react";
import { Stack, Box, Typography, Divider, Chip, alpha, CircularProgress, LinearProgress } from "@mui/material";
import {
  EditNote as EditNoteIcon,
  CheckCircle as CheckCircleIcon,
  RadioButtonUnchecked as RadioButtonUncheckedIcon,
  VolumeUp as VolumeUpIcon,
  PlayArrow as PlayArrowIcon,
  Image as ImageIcon,
} from "@mui/icons-material";
import { Scene, Line, Knobs } from "../types";
import { GlassyCard, glassyCardSx, PrimaryButton } from "../ui";
import { LineEditor } from "./LineEditor";
import { ImageRegenerateModal, ImageGenerationSettings } from "./ImageRegenerateModal";
import { AudioRegenerateModal, AudioGenerationSettings } from "./AudioRegenerateModal";
import { podcastApi } from "../../../services/podcastApi";
import { aiApiClient } from "../../../api/client";

interface SceneEditorProps {
  scene: Scene;
  onUpdateScene: (s: Scene) => void;
  onApprove: (id: string) => Promise<void>;
  knobs: Knobs;
  approvingSceneId?: string | null;
  generatingAudioId?: string | null;
  onAudioGenerationStart?: (sceneId: string) => void;
  onAudioGenerated?: (sceneId: string, audioUrl: string) => void;
  idea?: string; // Podcast idea for image generation context
  avatarUrl?: string | null; // Base avatar URL for consistent scene image generation
}

export const SceneEditor: React.FC<SceneEditorProps> = ({
  scene,
  onUpdateScene,
  onApprove,
  knobs,
  approvingSceneId,
  generatingAudioId,
  onAudioGenerationStart,
  onAudioGenerated,
  idea,
  avatarUrl,
}) => {
  const [localGenerating, setLocalGenerating] = useState(false);
  const [generatingImage, setGeneratingImage] = useState(false);
  const [imageGenerationStatus, setImageGenerationStatus] = useState<string>("");
  const [imageGenerationProgress, setImageGenerationProgress] = useState<number>(0);
  const [audioBlobUrl, setAudioBlobUrl] = useState<string | null>(null);
  const [imageBlobUrl, setImageBlobUrl] = useState<string | null>(null);
  const [imageLoading, setImageLoading] = useState(false);
  const [showRegenerateModal, setShowRegenerateModal] = useState(false);
  const [showAudioModal, setShowAudioModal] = useState(false);
  const [audioSettings, setAudioSettings] = useState<AudioGenerationSettings>({
    voiceId: "Wise_Woman",
    speed: 1.0,
    volume: 1.0,
    pitch: 0.0,
    emotion: scene.emotion || "neutral",
    englishNormalization: true,
    sampleRate: 24000,
    bitrate: 64000,
    channel: "1",
    format: "mp3",
    languageBoost: "auto",
  });

  // Load audio as blob when audioUrl is available
  useEffect(() => {
    if (!scene.audioUrl) {
      // Clean up blob URL if audioUrl is removed
      setAudioBlobUrl((currentBlobUrl) => {
        if (currentBlobUrl) {
          URL.revokeObjectURL(currentBlobUrl);
        }
        return null;
      });
      return;
    }

    let isMounted = true;
    const currentAudioUrl = scene.audioUrl; // Capture current value

    const loadAudioBlob = async () => {
      try {
        // Normalize path
        let audioPath = currentAudioUrl.startsWith('/') ? currentAudioUrl : `/${currentAudioUrl}`;
        
        // Convert /api/story/audio/ to /api/podcast/audio/ if needed
        if (audioPath.includes('/api/story/audio/')) {
          const filename = audioPath.split('/api/story/audio/').pop() || '';
          audioPath = `/api/podcast/audio/${filename}`;
        }
        
        // Ensure it's a podcast audio endpoint
        if (!audioPath.includes('/api/podcast/audio/')) {
          const filename = audioPath.split('/').pop() || currentAudioUrl;
          audioPath = `/api/podcast/audio/${filename}`;
        }

        // Remove query parameters if present
        audioPath = audioPath.split('?')[0];

        const response = await aiApiClient.get(audioPath, {
          responseType: 'blob',
        });
        
        if (!isMounted) {
          // Component unmounted or audioUrl changed, don't set blob URL
          return;
        }
        
        // Double-check that audioUrl hasn't changed
        if (scene.audioUrl !== currentAudioUrl) {
          return;
        }
        
        const blob = response.data;
        const blobUrl = URL.createObjectURL(blob);
        
        setAudioBlobUrl((prevBlobUrl) => {
          // Clean up previous blob URL if exists
          if (prevBlobUrl && prevBlobUrl !== blobUrl) {
            URL.revokeObjectURL(prevBlobUrl);
          }
          return blobUrl;
        });
      } catch (error) {
        console.error(`Failed to load audio blob for scene ${scene.id}:`, error);
        // Don't set blob URL on error - will show error state
      }
    };

    loadAudioBlob();

    // Cleanup: only mark as unmounted, don't revoke blob URL here
    // The blob URL will be cleaned up when audioUrl changes (new effect) or component unmounts
    return () => {
      isMounted = false;
    };
  }, [scene.audioUrl, scene.id]);

  // Load image as blob when imageUrl is available
  useEffect(() => {
    if (!scene.imageUrl) {
      // Clean up blob URL if imageUrl is removed
      setImageBlobUrl((currentBlobUrl) => {
        if (currentBlobUrl && currentBlobUrl.startsWith('blob:')) {
          URL.revokeObjectURL(currentBlobUrl);
        }
        return null;
      });
      return;
    }

    let isMounted = true;
    const currentImageUrl = scene.imageUrl; // Capture current value

    const loadImageBlob = async () => {
      try {
        setImageLoading(true);
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
        
        if (!isMounted) {
          return;
        }
        
        // Double-check that imageUrl hasn't changed
        if (scene.imageUrl !== currentImageUrl) {
          return;
        }
        
        const blob = response.data;
        const blobUrl = URL.createObjectURL(blob);
        
        setImageBlobUrl((prevBlobUrl) => {
          // Clean up previous blob URL if exists
          if (prevBlobUrl && prevBlobUrl !== blobUrl && prevBlobUrl.startsWith('blob:')) {
            URL.revokeObjectURL(prevBlobUrl);
          }
          return blobUrl;
        });
      } catch (error) {
        console.error('[SceneEditor] Failed to load image blob:', error);
        // Fallback: try with query token
        try {
          const token = localStorage.getItem('clerk_dashboard_token') || '';
          if (token) {
            const urlWithToken = `${currentImageUrl}?token=${encodeURIComponent(token)}`;
            setImageBlobUrl(urlWithToken);
          }
        } catch (fallbackError) {
          console.error('[SceneEditor] Fallback image loading failed:', fallbackError);
        }
      } finally {
        if (isMounted) {
          setImageLoading(false);
        }
      }
    };

    loadImageBlob();

    return () => {
      isMounted = false;
      // Cleanup blob URL on unmount or when imageUrl changes
      setImageBlobUrl((prevBlobUrl) => {
        if (prevBlobUrl && prevBlobUrl.startsWith('blob:')) {
          URL.revokeObjectURL(prevBlobUrl);
        }
        return null;
      });
    };
  }, [scene.imageUrl]);

  const updateLine = (updatedLine: Line) => {
    const updated = { ...scene, lines: scene.lines.map((l) => (l.id === updatedLine.id ? updatedLine : l)) };
    onUpdateScene(updated);
  };
  
  const approving = approvingSceneId === scene.id;
  const generating = generatingAudioId === scene.id || localGenerating;
  const hasAudio = Boolean(scene.audioUrl && audioBlobUrl);
  const hasImage = Boolean(scene.imageUrl);

  const handleApproveAndGenerate = async (settings?: AudioGenerationSettings) => {
    const wasAlreadyApproved = scene.approved;
    const sceneId = scene.id;
    
    try {
      // Set generating state
      setLocalGenerating(true);
      if (onAudioGenerationStart) {
        onAudioGenerationStart(sceneId);
      }

      // If scene is not approved yet, approve it first
      // This will update the parent script state
      if (!scene.approved) {
        await onApprove(sceneId);
        // The parent's approveScene already updated the script state
        // We need to wait for React to propagate the updated scene prop
        // For now, we'll update it locally too to ensure UI updates immediately
        onUpdateScene({ ...scene, approved: true });
      }

      // Use the current scene (which should now be approved)
      // If scene prop hasn't updated yet, use the local update we just made
      const currentScene = { ...scene, approved: true };
      
      // Generate audio
      const effectiveSettings = settings || audioSettings;
      const result = await podcastApi.renderSceneAudio({
        scene: currentScene,
        voiceId: effectiveSettings.voiceId || "Wise_Woman",
        emotion: effectiveSettings.emotion || scene.emotion || knobs.voice_emotion || "neutral",
        speed: effectiveSettings.speed ?? knobs.voice_speed ?? 1.0,
        volume: effectiveSettings.volume ?? 1.0,
        pitch: effectiveSettings.pitch ?? 0.0,
        englishNormalization: effectiveSettings.englishNormalization ?? true,
        sampleRate: effectiveSettings.sampleRate,
        bitrate: effectiveSettings.bitrate,
        channel: effectiveSettings.channel,
        format: effectiveSettings.format,
        languageBoost: effectiveSettings.languageBoost,
      });

      // Update scene with audio URL and ensure approved state
      // This will sync with parent script state
      const updatedScene = { ...currentScene, audioUrl: result.audioUrl, approved: true };
      onUpdateScene(updatedScene);
      
      if (onAudioGenerated) {
        onAudioGenerated(sceneId, result.audioUrl);
      }
    } catch (error) {
      console.error("Failed to approve and generate audio:", error);
      // On error, revert approval only if we just approved it in this call
      if (!wasAlreadyApproved) {
        onUpdateScene({ ...scene, approved: false, audioUrl: undefined });
      }
      throw error;
    } finally {
      setLocalGenerating(false);
    }
  };

  const handleGenerateImage = async (settings?: ImageGenerationSettings) => {
    const sceneId = scene.id;
    const startTime = Date.now();
    let progressInterval: NodeJS.Timeout | null = null;
    
    try {
      setGeneratingImage(true);
      setShowRegenerateModal(false);
      setImageGenerationStatus("Submitting image generation request...");
      setImageGenerationProgress(10);
      
      // Build scene content from lines for context
      const sceneContent = scene.lines.map((line) => line.text).join(" ");
      
      // Log avatar URL for debugging
      console.log("[SceneEditor] Generating image with avatarUrl:", avatarUrl);
      console.log("[SceneEditor] Custom settings:", settings);
      
      // Simulate progress updates during API call
      progressInterval = setInterval(() => {
        const elapsed = Date.now() - startTime;
        const seconds = Math.floor(elapsed / 1000);
        
        // Update status based on elapsed time
        if (seconds < 5) {
          setImageGenerationStatus("Submitting request to AI service...");
          setImageGenerationProgress(15);
        } else if (seconds < 15) {
          setImageGenerationStatus("AI is generating your image...");
          setImageGenerationProgress(30);
        } else if (seconds < 30) {
          setImageGenerationStatus("Creating character-consistent scene image...");
          setImageGenerationProgress(50);
        } else if (seconds < 60) {
          setImageGenerationStatus("Rendering image details...");
          setImageGenerationProgress(70);
        } else {
          setImageGenerationStatus(`Processing... (${seconds}s elapsed)`);
          setImageGenerationProgress(Math.min(90, 50 + (seconds - 30) / 2));
        }
      }, 1000);
      
      const result = await podcastApi.generateSceneImage({
        sceneId: scene.id,
        sceneTitle: scene.title,
        sceneContent: sceneContent,
        baseAvatarUrl: avatarUrl || undefined, // Pass base avatar URL for character consistency
        idea: idea,
        width: 1024,
        height: 1024,
        // Pass custom settings if provided
        customPrompt: settings?.prompt,
        style: settings?.style,
        renderingSpeed: settings?.renderingSpeed,
        aspectRatio: settings?.aspectRatio,
      });
      
      if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
      }
      
      setImageGenerationStatus("Finalizing image...");
      setImageGenerationProgress(95);
      
      // Update scene with image URL
      const updatedScene = { ...scene, imageUrl: result.image_url };
      onUpdateScene(updatedScene);
      
      const elapsed = Math.floor((Date.now() - startTime) / 1000);
      setImageGenerationStatus(`Image generated successfully in ${elapsed}s`);
      setImageGenerationProgress(100);
      
      // Clear status after a moment
      setTimeout(() => {
        setImageGenerationStatus("");
        setImageGenerationProgress(0);
      }, 2000);
    } catch (error: any) {
      // Clear interval on error
      if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
      }
      
      console.error("Failed to generate image:", error);
      // Extract error message from response if available
      const errorMessage = error?.response?.data?.detail?.message 
        || error?.response?.data?.detail?.error 
        || error?.response?.data?.detail 
        || error?.message 
        || "Failed to generate image. Please try again.";
      console.error("Error details:", {
        status: error?.response?.status,
        statusText: error?.response?.statusText,
        data: error?.response?.data,
        message: errorMessage,
      });
      
      setImageGenerationStatus(`Error: ${errorMessage}`);
      setImageGenerationProgress(0);
      
      // Show user-friendly error message
      alert(`Image generation failed: ${errorMessage}`);
      throw error;
    } finally {
      // Ensure interval is cleared
      if (progressInterval) {
        clearInterval(progressInterval);
      }
      setGeneratingImage(false);
    }
  };

  const handleRegenerateClick = () => {
    setShowRegenerateModal(true);
  };

  const handleAudioRegenerateClick = () => {
    if (hasAudio) {
      setShowAudioModal(true);
    } else {
      handleApproveAndGenerate(audioSettings);
    }
  };

  const handleAudioRegenerate = (settings: AudioGenerationSettings) => {
    setAudioSettings(settings);
    setShowAudioModal(false);
    handleApproveAndGenerate(settings);
  };

  return (
    <GlassyCard sx={glassyCardSx}>
      <Stack spacing={2.5}>
        <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
          <Box sx={{ flex: 1 }}>
            <Typography 
              variant="h6" 
              sx={{ 
                display: "flex", 
                alignItems: "center", 
                gap: 1.5, 
                mb: 1, 
                color: "#0f172a", 
                fontWeight: 600,
                fontSize: "1.25rem",
                letterSpacing: "-0.01em",
              }}
            >
              <EditNoteIcon fontSize="small" sx={{ color: "#667eea", fontSize: "1.5rem" }} />
              {scene.title}
            </Typography>
            <Stack direction="row" spacing={1.5} alignItems="center" flexWrap="wrap">
              <Chip
                icon={scene.approved ? <CheckCircleIcon /> : <RadioButtonUncheckedIcon />}
                label={scene.approved ? "Approved" : "Pending Approval"}
                size="small"
                color={scene.approved ? "success" : "warning"}
                sx={{
                  background: scene.approved 
                    ? "linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(5, 150, 105, 0.12) 100%)"
                    : "linear-gradient(135deg, rgba(245, 158, 11, 0.12) 0%, rgba(217, 119, 6, 0.12) 100%)",
                  color: scene.approved ? "#059669" : "#d97706",
                  border: scene.approved 
                    ? "1px solid rgba(16, 185, 129, 0.25)" 
                    : "1px solid rgba(245, 158, 11, 0.25)",
                  fontWeight: 600,
                  fontSize: "0.75rem",
                  height: 26,
                  boxShadow: "0 1px 2px rgba(0, 0, 0, 0.05)",
                }}
              />
              <Typography variant="caption" sx={{ color: "#64748b", fontWeight: 500, fontSize: "0.8125rem" }}>
                Duration: {scene.duration}s
              </Typography>
            </Stack>
          </Box>
          <Stack direction="row" spacing={1.5} flexWrap="wrap" useFlexGap>
            <PrimaryButton
              onClick={handleAudioRegenerateClick}
              disabled={approving || generating}
              loading={approving || generating}
              startIcon={
                hasAudio && !generating ? (
                  <VolumeUpIcon />
                ) : generating ? (
                  <CircularProgress size={16} sx={{ color: "white" }} />
                ) : (
                  <PlayArrowIcon />
                )
              }
              tooltip={
                hasAudio && !generating
                  ? "Regenerate audio for this scene with custom settings"
                  : generating
                  ? "Generating audio..."
                  : scene.approved
                  ? "Generate audio for this scene"
                  : "Approve scene and generate audio"
              }
              sx={{
                minWidth: 200,
              }}
            >
              {hasAudio && !generating
                ? "Regenerate Audio"
                : generating
                ? "Generating Audio..."
                : scene.approved
                ? "Generate Audio"
                : "Approve & Generate Audio"}
            </PrimaryButton>
            <PrimaryButton
              onClick={hasImage ? handleRegenerateClick : () => handleGenerateImage()}
              disabled={generatingImage}
              loading={generatingImage}
              startIcon={
                hasImage && !generatingImage ? (
                  <ImageIcon />
                ) : generatingImage ? (
                  <CircularProgress size={16} sx={{ color: "white" }} />
                ) : (
                  <ImageIcon />
                )
              }
              tooltip={
                hasImage
                  ? "Regenerate image for this scene"
                  : generatingImage
                  ? "Generating image..."
                  : "Generate image for video (optional)"
              }
              sx={{
                minWidth: 180,
                background: hasImage 
                  ? "linear-gradient(135deg, #10b981 0%, #059669 100%)"
                  : "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                "&:hover": {
                  background: hasImage
                    ? "linear-gradient(135deg, #059669 0%, #047857 100%)"
                    : "linear-gradient(135deg, #764ba2 0%, #667eea 100%)",
                },
              }}
            >
              {hasImage && !generatingImage
                ? "Regenerate Image"
                : generatingImage
                ? "Generating Image..."
                : "Generate Image"}
            </PrimaryButton>
          </Stack>
        </Stack>

        <Divider sx={{ borderColor: "rgba(15, 23, 42, 0.08)", borderWidth: 1 }} />

        <Stack spacing={2}>
          {scene.lines.map((line) => (
            <LineEditor key={line.id} line={line} onChange={updateLine} />
          ))}
        </Stack>

        {scene.audioUrl && (
          <>
            <Divider sx={{ borderColor: "rgba(15, 23, 42, 0.08)", borderWidth: 1, mt: 1 }} />
            <Box
              sx={{
                p: 2,
                background: hasAudio
                  ? "linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(5, 150, 105, 0.08) 100%)"
                  : "linear-gradient(135deg, rgba(245, 158, 11, 0.08) 0%, rgba(217, 119, 6, 0.08) 100%)",
                borderRadius: 2,
                border: hasAudio
                  ? "1px solid rgba(16, 185, 129, 0.2)"
                  : "1px solid rgba(245, 158, 11, 0.2)",
              }}
            >
              <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 1.5 }}>
                <VolumeUpIcon sx={{ color: hasAudio ? "#059669" : "#d97706", fontSize: "1.25rem" }} />
                <Typography variant="subtitle2" sx={{ color: hasAudio ? "#059669" : "#d97706", fontWeight: 600 }}>
                  {hasAudio ? "Audio Generated" : "Loading Audio..."}
                </Typography>
              </Stack>
              {hasAudio && audioBlobUrl ? (
                <audio controls style={{ width: "100%", borderRadius: 8 }}>
                  <source src={audioBlobUrl} type="audio/mpeg" />
                  Your browser does not support the audio element.
                </audio>
              ) : (
                <Box sx={{ display: "flex", alignItems: "center", justifyContent: "center", py: 2 }}>
                  <CircularProgress size={24} sx={{ color: "#d97706" }} />
                </Box>
              )}
            </Box>
          </>
        )}

        {/* Image Generation Progress - Show when generating */}
        {generatingImage && (
          <>
            <Divider sx={{ borderColor: "rgba(15, 23, 42, 0.08)", borderWidth: 1, mt: 1 }} />
            <Box
              sx={{
                p: 2,
                background: "linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%)",
                borderRadius: 2,
                border: "1px solid rgba(102, 126, 234, 0.2)",
              }}
            >
              <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 1.5 }}>
                <ImageIcon sx={{ color: "#667eea", fontSize: "1.25rem" }} />
                <Typography variant="subtitle2" sx={{ color: "#667eea", fontWeight: 600 }}>
                  Generating Image...
                </Typography>
              </Stack>
              
              {/* Progress Bar */}
              <Box sx={{ mb: 1.5 }}>
                <LinearProgress 
                  variant="determinate" 
                  value={imageGenerationProgress} 
                  sx={{ 
                    height: 8, 
                    borderRadius: 4,
                    backgroundColor: alpha("#667eea", 0.1),
                    "& .MuiLinearProgress-bar": {
                      backgroundColor: "#667eea",
                      borderRadius: 4,
                    }
                  }} 
                />
                <Typography variant="caption" sx={{ color: "#667eea", mt: 0.5, display: "block", textAlign: "right" }}>
                  {imageGenerationProgress}%
                </Typography>
              </Box>
              
              {/* Status Message */}
              {imageGenerationStatus && (
                <Typography variant="body2" sx={{ color: "#667eea", fontSize: "0.875rem", lineHeight: 1.6, mb: 1 }}>
                  {imageGenerationStatus}
                </Typography>
              )}
              
              {/* Spinner */}
              <Box sx={{ display: "flex", alignItems: "center", justifyContent: "center", mt: 1 }}>
                <CircularProgress size={32} sx={{ color: "#667eea" }} />
              </Box>
            </Box>
          </>
        )}

        {/* Generated Image Display - Show when image exists and not generating */}
        {scene.imageUrl && !generatingImage && (
          <>
            <Divider sx={{ borderColor: "rgba(15, 23, 42, 0.08)", borderWidth: 1, mt: 1 }} />
            <Box
              sx={{
                p: 2,
                background: imageBlobUrl && !imageLoading
                  ? "linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%)"
                  : "linear-gradient(135deg, rgba(245, 158, 11, 0.08) 0%, rgba(217, 119, 6, 0.08) 100%)",
                borderRadius: 2,
                border: imageBlobUrl && !imageLoading
                  ? "1px solid rgba(102, 126, 234, 0.2)"
                  : "1px solid rgba(245, 158, 11, 0.2)",
              }}
            >
              <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 1.5 }}>
                <ImageIcon sx={{ color: imageBlobUrl && !imageLoading ? "#667eea" : "#d97706", fontSize: "1.25rem" }} />
                <Typography variant="subtitle2" sx={{ color: imageBlobUrl && !imageLoading ? "#667eea" : "#d97706", fontWeight: 600 }}>
                  {imageBlobUrl && !imageLoading ? "Image Generated" : "Loading Image..."}
                </Typography>
              </Stack>
              {imageBlobUrl && !imageLoading ? (
                <Box
                  sx={{
                    width: "100%",
                    borderRadius: 2,
                    overflow: "hidden",
                    border: "1px solid rgba(102,126,234,0.2)",
                    background: alpha("#667eea", 0.05),
                  }}
                >
                  <Box
                    component="img"
                    src={imageBlobUrl}
                    alt={scene.title}
                    sx={{
                      width: "100%",
                      height: "auto",
                      display: "block",
                      maxHeight: 400,
                      objectFit: "cover",
                    }}
                    onError={(e) => {
                      console.error('[SceneEditor] Image failed to load:', {
                        src: e.currentTarget.src,
                        imageUrl: scene.imageUrl,
                        imageBlobUrl,
                      });
                    }}
                    onLoad={() => {
                      console.log('[SceneEditor] Image loaded successfully');
                    }}
                  />
                </Box>
              ) : (
                <Box sx={{ display: "flex", alignItems: "center", justifyContent: "center", py: 2 }}>
                  <CircularProgress size={24} sx={{ color: "#d97706" }} />
                </Box>
              )}
            </Box>
          </>
        )}
      </Stack>

      {/* Image Regeneration Modal */}
      <ImageRegenerateModal
        open={showRegenerateModal}
        onClose={() => setShowRegenerateModal(false)}
        onRegenerate={handleGenerateImage}
        initialPrompt={(() => {
          const promptParts = [
            `Scene: ${scene.title}`,
            "Professional podcast recording studio",
            "Modern microphone setup",
            "Clean background, professional lighting",
            "16:9 aspect ratio, video-optimized composition"
          ];
          if (idea) {
            promptParts.push(`Topic: ${idea.substring(0, 60)}`);
          }
          return promptParts.join(", ");
        })()}
        initialStyle="Realistic"
        initialRenderingSpeed="Quality"
        initialAspectRatio="16:9"
        isGenerating={generatingImage}
      />

      <AudioRegenerateModal
        open={showAudioModal}
        onClose={() => setShowAudioModal(false)}
        onRegenerate={handleAudioRegenerate}
        initialSettings={audioSettings}
        isGenerating={generating}
      />
    </GlassyCard>
  );
};

