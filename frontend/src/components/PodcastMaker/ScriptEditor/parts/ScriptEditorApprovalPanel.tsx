import React from "react";
import { Stack, Box, Typography, Paper, LinearProgress } from "@mui/material";
import { CheckCircle as CheckCircleIcon, PlayArrow as PlayArrowIcon } from "@mui/icons-material";
import { Script } from "../../types";
import { useScriptEditor } from "../ScriptEditorContext";
import { PrimaryButton } from "../../ui";

interface ScriptEditorApprovalPanelProps {
  onProceedToRendering: (script: Script) => void;
}

export const ScriptEditorApprovalPanel: React.FC<ScriptEditorApprovalPanelProps> = ({ onProceedToRendering }) => {
  const { activeScript, allApproved, approvedCount, totalScenes, allScenesHaveAudioAndImages } = useScriptEditor();
  const approved = allApproved ?? false;
  const ready = allScenesHaveAudioAndImages ?? false;

  return (
    <Paper sx={{ p: 3.5, background: approved ? "linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, rgba(5, 150, 105, 0.05) 100%)" : "#ffffff", border: approved ? "2px solid rgba(16, 185, 129, 0.25)" : "1px solid rgba(15, 23, 42, 0.08)", borderRadius: 3 }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center">
        <Box>
          <Typography variant="subtitle1" sx={{ mb: 1, display: "flex", alignItems: "center", gap: 1.5, color: "#0f172a", fontWeight: 600, fontSize: "1.1rem" }}>
            <CheckCircleIcon fontSize="small" sx={{ color: approved ? "#10b981" : "#94a3b8", fontSize: "1.25rem" }} />Approval Status
          </Typography>
          <Typography variant="body2" sx={{ color: "#64748b", fontWeight: 400, lineHeight: 1.6 }}>
            {approvedCount} of {totalScenes} scenes approved{!approved && " — Approve all scenes first"}
          </Typography>
          {!ready && <LinearProgress variant="determinate" value={ready ? 100 : (activeScript ? (activeScript.scenes.filter((s) => s.audioUrl && s.imageUrl).length / totalScenes) * 100 : 0)} sx={{ mt: 1, height: 6, borderRadius: 3 }} />}
        </Box>
        <PrimaryButton onClick={() => activeScript && onProceedToRendering(activeScript)} disabled={!ready} startIcon={<PlayArrowIcon />}>
          Proceed to Rendering
        </PrimaryButton>
      </Stack>
    </Paper>
  );
};