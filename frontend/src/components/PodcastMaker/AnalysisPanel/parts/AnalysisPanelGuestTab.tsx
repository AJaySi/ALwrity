import React from "react";
import { Stack, Box, Typography, Chip, Paper } from "@mui/material";
import { Quiz as TalkIcon } from "@mui/icons-material";
import { useAnalysisPanel } from "../AnalysisPanelContext";

export const AnalysisPanelGuestTab: React.FC = () => {
  const { analysis: ctxAnalysis } = useAnalysisPanel();

  const guestTalkingPoints = ctxAnalysis?.guest_talking_points;

  if (!guestTalkingPoints || guestTalkingPoints.length === 0) {
    return (
      <Box sx={{ p: 3, textAlign: "center" }}>
        <Typography variant="body1" sx={{ color: "#64748b" }}>
          No guest talking points generated yet. Add a guest speaker to get interview questions.
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 2 }}>
      <Box sx={{ display: "flex", gap: 1.5, alignItems: "center", mb: 2 }}>
        <TalkIcon sx={{ color: "#6366f1" }} />
        <Typography variant="h6" sx={{ fontWeight: 600, color: "#0f172a" }}>
          Guest Talking Points
        </Typography>
      </Box>
      <Stack spacing={2}>
        {guestTalkingPoints.map((point: string, idx: number) => (
          <Paper key={idx} elevation={0} sx={{ p: 2, bgcolor: "#faf5ff", border: "1px solid rgba(168,85,247,0.2)", borderRadius: 2, display: "flex", alignItems: "flex-start", gap: 1.5 }}>
            <Chip label="Q" size="small" sx={{ minWidth: 24, bgcolor: "#a855f7", color: "#fff" }} />
            <Typography variant="body2" sx={{ color: "#6b21a8" }}>
              {point}
            </Typography>
          </Paper>
        ))}
      </Stack>
    </Box>
  );
};