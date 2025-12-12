import React from "react";
import { Box, Stack, Typography, Alert, Paper, alpha } from "@mui/material";
import { PlayArrow as PlayArrowIcon } from "@mui/icons-material";
import { Script } from "../types";

interface GuidancePanelProps {
  scenes: Script["scenes"];
}

export const GuidancePanel: React.FC<GuidancePanelProps> = ({ scenes }) => {
  const scenesNeedingAudio = scenes.filter((s) => !s.audioUrl).length;
  const allScenesHaveAudio = scenes.length > 0 && scenesNeedingAudio === 0;

  return (
    <Paper
      sx={{
        p: 3,
        mb: 3,
        background: "linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)",
        border: "2px solid rgba(102, 126, 234, 0.3)",
        borderRadius: 2,
        boxShadow: "0 2px 8px rgba(102, 126, 234, 0.15)",
      }}
    >
      <Stack spacing={2}>
        <Typography variant="h6" sx={{ color: "#0f172a", fontWeight: 700, display: "flex", alignItems: "center", gap: 1.5, fontSize: "1.125rem" }}>
          <PlayArrowIcon sx={{ color: "#667eea", fontSize: "1.5rem" }} />
          What's Next? Generate Audio for Your Scenes
        </Typography>
        <Stack spacing={1.5}>
          <Typography variant="body2" sx={{ color: "#475569", lineHeight: 1.7, fontSize: "0.9375rem" }}>
            <strong>For each scene below:</strong>
          </Typography>
          <Box component="ul" sx={{ m: 0, pl: 2.5, color: "#475569" }}>
            <Typography component="li" variant="body2" sx={{ mb: 1, lineHeight: 1.7 }}>
              <strong>If audio is missing:</strong> Click <strong style={{ color: "#667eea" }}>"Generate Audio"</strong> to create the audio file for that scene
            </Typography>
            <Typography component="li" variant="body2" sx={{ mb: 1, lineHeight: 1.7 }}>
              <strong>If audio exists:</strong> The scene is ready! You can download it or proceed to video generation
            </Typography>
            <Typography component="li" variant="body2" sx={{ lineHeight: 1.7 }}>
              <strong>Optional:</strong> Use <strong>"Preview Sample"</strong> to test voice and pacing before full generation
            </Typography>
          </Box>
          {scenesNeedingAudio > 0 && (
            <Alert
              severity="info"
              sx={{
                mt: 1,
                background: alpha("#3b82f6", 0.1),
                border: "1px solid rgba(59,130,246,0.3)",
                "& .MuiAlert-icon": {
                  color: "#3b82f6",
                },
              }}
            >
              <Typography variant="body2" sx={{ color: "#1e40af", fontWeight: 600 }}>
                📢 {scenesNeedingAudio} scene{scenesNeedingAudio !== 1 ? "s" : ""} need{scenesNeedingAudio === 1 ? "s" : ""} audio generation. Scroll down and click the <strong>"Generate Audio"</strong> buttons below!
              </Typography>
            </Alert>
          )}
          {allScenesHaveAudio && (
            <Alert
              severity="success"
              sx={{
                mt: 1,
                background: alpha("#10b981", 0.1),
                border: "1px solid rgba(16,185,129,0.3)",
                "& .MuiAlert-icon": {
                  color: "#10b981",
                },
              }}
            >
              <Typography variant="body2" sx={{ color: "#059669", fontWeight: 600 }}>
                ✅ All scenes have audio! Your podcast is ready. You can download individual scenes or proceed to video generation.
              </Typography>
            </Alert>
          )}
        </Stack>
      </Stack>
    </Paper>
  );
};

