import React from "react";
import { Box, Divider, Stack, Typography, CircularProgress } from "@mui/material";
import { VolumeUp as VolumeUpIcon } from "@mui/icons-material";

interface SceneEditorMediaPanelProps {
  hasAudio: boolean;
  audioBlobUrl?: string | null;
  isGenerating?: boolean;
}

// Minimal media panel wrapper extracted for refactor hygiene
export const SceneEditorMediaPanel: React.FC<SceneEditorMediaPanelProps> = ({ hasAudio, audioBlobUrl, isGenerating }) => {
  return (
    <Box sx={{ mt: 1, p: 2, borderRadius: 2, border: "1px solid rgba(0,0,0,0.08)", background: "#fff" }}>
      <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1 }}>
        <VolumeUpIcon sx={{ color: hasAudio ? "#059669" : "#d97706" }} />
        <Typography variant="subtitle2" sx={{ fontWeight: 700, color: hasAudio ? "#059669" : "#d97706" }}>
          {hasAudio ? "Audio Generated" : "Loading Audio..."}
        </Typography>
      </Stack>
      {audioBlobUrl ? (
        <audio controls src={audioBlobUrl} style={{ width: "100%" }} />
      ) : isGenerating ? (
        <CircularProgress size={20} />
      ) : null}
      <Divider sx={{ mt: 2 }} />
    </Box>
  );
};
