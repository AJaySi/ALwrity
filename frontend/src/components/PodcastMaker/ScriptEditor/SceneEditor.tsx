import React, { useState, useEffect } from "react";
import { Stack, Box, Typography, Divider, Chip, alpha, CircularProgress } from "@mui/material";
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
}) => {
  const [localGenerating, setLocalGenerating] = useState(false);
  const [generatingImage, setGeneratingImage] = useState(false);
  const [audioBlobUrl, setAudioBlobUrl] = useState<string | null>(null);

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

  const updateLine = (updatedLine: Line) => {
    const updated = { ...scene, lines: scene.lines.map((l) => (l.id === updatedLine.id ? updatedLine : l)) };
    onUpdateScene(updated);
  };
  
  const approving = approvingSceneId === scene.id;
  const generating = generatingAudioId === scene.id || localGenerating;
  const hasAudio = Boolean(scene.audioUrl && audioBlobUrl);
  const hasImage = Boolean(scene.imageUrl);

  const handleApproveAndGenerate = async () => {
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
      const result = await podcastApi.renderSceneAudio({
        scene: currentScene,
        voiceId: "Wise_Woman",
        emotion: scene.emotion || knobs.voice_emotion || "neutral",
        speed: knobs.voice_speed || 1.0,
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

  const handleGenerateImage = async () => {
    const sceneId = scene.id;
    
    try {
      setGeneratingImage(true);
      
      // Build scene content from lines for context
      const sceneContent = scene.lines.map((line) => line.text).join(" ");
      
      const result = await podcastApi.generateSceneImage({
        sceneId: scene.id,
        sceneTitle: scene.title,
        sceneContent: sceneContent,
        idea: idea,
        width: 1024,
        height: 1024,
      });
      
      // Update scene with image URL
      const updatedScene = { ...scene, imageUrl: result.image_url };
      onUpdateScene(updatedScene);
    } catch (error) {
      console.error("Failed to generate image:", error);
      throw error;
    } finally {
      setGeneratingImage(false);
    }
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
              onClick={handleApproveAndGenerate}
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
                  ? "Regenerate audio for this scene"
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
              onClick={handleGenerateImage}
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
      </Stack>
    </GlassyCard>
  );
};

