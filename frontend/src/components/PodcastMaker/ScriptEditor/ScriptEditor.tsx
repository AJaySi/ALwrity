import React, { useEffect, useState } from "react";
import { Box, Stack, Typography, Alert, Paper, LinearProgress, CircularProgress, alpha } from "@mui/material";
import { EditNote as EditNoteIcon, CheckCircle as CheckCircleIcon, PlayArrow as PlayArrowIcon, ArrowBack as ArrowBackIcon } from "@mui/icons-material";
import { Script, Knobs, Scene } from "../types";
import { BlogResearchResponse } from "../../../services/blogWriterApi";
import { podcastApi } from "../../../services/podcastApi";
import { GlassyCard, PrimaryButton, SecondaryButton } from "../ui";
import { SceneEditor } from "./SceneEditor";

interface ScriptEditorProps {
  projectId: string;
  idea: string;
  research: any; // Research type
  rawResearch: BlogResearchResponse | null;
  knobs: Knobs;
  speakers: number;
  durationMinutes: number;
  script: Script | null;
  onScriptChange: (script: Script) => void;
  onBackToResearch: () => void;
  onProceedToRendering: (script: Script) => void;
  onError: (message: string) => void;
}

export const ScriptEditor: React.FC<ScriptEditorProps> = ({
  projectId,
  idea,
  research,
  rawResearch,
  knobs,
  speakers,
  durationMinutes,
  script: initialScript,
  onScriptChange,
  onBackToResearch,
  onProceedToRendering,
  onError,
}) => {
  const [script, setScript] = useState<Script | null>(initialScript);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [approvingSceneId, setApprovingSceneId] = useState<string | null>(null);

  // Sync with parent state
  useEffect(() => {
    if (initialScript) {
      setScript(initialScript);
    }
  }, [initialScript]);

  useEffect(() => {
    // If script already exists, don't regenerate
    if (script) {
      return;
    }

    // Only generate if we have research data
    if (!rawResearch) {
      return;
    }

    let mounted = true;
    setLoading(true);
    setError(null);
    podcastApi
      .generateScript({
        projectId,
        idea,
        research: rawResearch,
        knobs,
        speakers,
        durationMinutes,
      })
      .then((res) => {
        if (mounted) {
          setScript(res);
          onScriptChange(res);
          setError(null);
        }
      })
      .catch((err) => {
        const message = err instanceof Error ? err.message : "Failed to generate script";
        setError(message);
        onError(message);
      })
      .finally(() => mounted && setLoading(false));
    return () => {
      mounted = false;
    };
  }, [projectId, rawResearch, idea, knobs, speakers, durationMinutes]);

  const updateScene = (updated: Scene) => {
    if (!script) return;
    const updatedScript = { ...script, scenes: script.scenes.map((s) => (s.id === updated.id ? updated : s)) };
    setScript(updatedScript);
    onScriptChange(updatedScript);
  };

  const approveScene = async (sceneId: string) => {
    try {
      setApprovingSceneId(sceneId);
      await podcastApi.approveScene({ projectId, sceneId });
      const updatedScript = script
        ? {
            ...script,
            scenes: script.scenes.map((s) => (s.id === sceneId ? { ...s, approved: true } : s)),
          }
        : null;
      if (updatedScript) {
        setScript(updatedScript);
        onScriptChange(updatedScript);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to approve scene";
      setError(message);
      onError(message);
      throw err;
    } finally {
      setApprovingSceneId((current) => (current === sceneId ? null : current));
    }
  };

  const allApproved = script && script.scenes.every((s) => s.approved);
  const approvedCount = script ? script.scenes.filter((s) => s.approved).length : 0;
  const totalScenes = script ? script.scenes.length : 0;

  return (
    <Box sx={{ mt: 3 }}>
      <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 3 }}>
        <SecondaryButton onClick={onBackToResearch} startIcon={<ArrowBackIcon />}>
          Back to Research
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
          <EditNoteIcon />
          Script Editor
        </Typography>
      </Stack>

      {loading && (
        <Alert severity="info" icon={<CircularProgress size={20} />} sx={{ mb: 3 }}>
          <Typography variant="body2">Generating script with AI... This may take a moment.</Typography>
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {script && (
        <Stack spacing={3}>
          <Alert severity="info" sx={{ background: alpha("#3b82f6", 0.1), border: "1px solid rgba(59,130,246,0.3)" }}>
            <Typography variant="body2">
              <strong>Approval Required:</strong> Each scene must be approved before rendering. Review and edit lines as needed, then approve each scene.
            </Typography>
          </Alert>

          <Stack spacing={2}>
            {script.scenes.map((scene, idx) => (
              <GlassyCard
                key={scene.id}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: idx * 0.1 }}
              >
                <SceneEditor
                  scene={scene}
                  onUpdateScene={updateScene}
                  onApprove={approveScene}
                  onPreviewLine={(text) => podcastApi.previewLine(text)}
                  approvingSceneId={approvingSceneId}
                />
              </GlassyCard>
            ))}
          </Stack>

          <Paper
            sx={{
              p: 3,
              background: alpha("#1e293b", 0.6),
              border: allApproved ? "2px solid rgba(16,185,129,0.4)" : "1px solid rgba(255,255,255,0.1)",
            }}
          >
            <Stack direction="row" justifyContent="space-between" alignItems="center">
              <Box>
                <Typography variant="subtitle1" sx={{ mb: 0.5, display: "flex", alignItems: "center", gap: 1 }}>
                  <CheckCircleIcon fontSize="small" color={allApproved ? "success" : "disabled"} />
                  Approval Status
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {approvedCount} of {totalScenes} scenes approved
                  {!allApproved && " — Approve all scenes to enable rendering"}
                </Typography>
                {!allApproved && (
                  <LinearProgress
                    variant="determinate"
                    value={(approvedCount / totalScenes) * 100}
                    sx={{ mt: 1, height: 6, borderRadius: 3 }}
                  />
                )}
              </Box>
              <PrimaryButton
                onClick={() => script && onProceedToRendering(script)}
                disabled={!allApproved}
                startIcon={<PlayArrowIcon />}
                tooltip={!allApproved ? "Approve all scenes to proceed to rendering" : "Start rendering all approved scenes"}
              >
                Proceed to Rendering
              </PrimaryButton>
            </Stack>
          </Paper>
        </Stack>
      )}
    </Box>
  );
};

