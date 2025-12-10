import React from "react";
import { Stack, Box, Typography, Divider, Chip, alpha } from "@mui/material";
import {
  EditNote as EditNoteIcon,
  CheckCircle as CheckCircleIcon,
  RadioButtonUnchecked as RadioButtonUncheckedIcon,
} from "@mui/icons-material";
import { Scene, Line } from "../types";
import { GlassyCard, glassyCardSx, PrimaryButton } from "../ui";
import { LineEditor } from "./LineEditor";

interface SceneEditorProps {
  scene: Scene;
  onUpdateScene: (s: Scene) => void;
  onApprove: (id: string) => Promise<void>;
  onPreviewLine: (text: string) => Promise<{ ok: boolean; message: string; audioUrl?: string }>;
  approvingSceneId?: string | null;
}

export const SceneEditor: React.FC<SceneEditorProps> = ({
  scene,
  onUpdateScene,
  onApprove,
  onPreviewLine,
  approvingSceneId,
}) => {
  const updateLine = (updatedLine: Line) => {
    const updated = { ...scene, lines: scene.lines.map((l) => (l.id === updatedLine.id ? updatedLine : l)) };
    onUpdateScene(updated);
  };
  const approving = approvingSceneId === scene.id;

  const handleApprove = async () => {
    await onApprove(scene.id);
    onUpdateScene({ ...scene, approved: true });
  };

  return (
    <GlassyCard sx={glassyCardSx}>
      <Stack spacing={2}>
        <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
          <Box>
            <Typography variant="h6" sx={{ display: "flex", alignItems: "center", gap: 1, mb: 0.5 }}>
              <EditNoteIcon fontSize="small" />
              {scene.title}
            </Typography>
            <Stack direction="row" spacing={1} alignItems="center">
              <Chip
                icon={scene.approved ? <CheckCircleIcon /> : <RadioButtonUncheckedIcon />}
                label={scene.approved ? "Approved" : "Pending Approval"}
                size="small"
                color={scene.approved ? "success" : "warning"}
                sx={{
                  background: scene.approved ? alpha("#10b981", 0.2) : alpha("#f59e0b", 0.2),
                  color: scene.approved ? "#6ee7b7" : "#fbbf24",
                  border: scene.approved ? "1px solid rgba(16,185,129,0.3)" : "1px solid rgba(245,158,11,0.3)",
                }}
              />
              <Typography variant="caption" color="text.secondary">
                Duration: {scene.duration}s
              </Typography>
            </Stack>
          </Box>
          <PrimaryButton
            onClick={handleApprove}
            disabled={scene.approved || approving}
            loading={approving}
            startIcon={scene.approved ? <CheckCircleIcon /> : undefined}
            tooltip={scene.approved ? "Scene is approved and ready for rendering" : "Approve this scene to enable rendering"}
          >
            {scene.approved ? "Approved" : approving ? "Approving..." : "Approve Scene"}
          </PrimaryButton>
        </Stack>

        <Divider sx={{ borderColor: "rgba(255,255,255,0.1)" }} />

        <Stack spacing={2}>
          {scene.lines.map((line) => (
            <LineEditor key={line.id} line={line} onChange={updateLine} onPreview={(text) => onPreviewLine(text)} />
          ))}
        </Stack>
      </Stack>
    </GlassyCard>
  );
};

