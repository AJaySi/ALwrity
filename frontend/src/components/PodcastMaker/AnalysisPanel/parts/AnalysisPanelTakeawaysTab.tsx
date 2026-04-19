import React from "react";
import { Stack, Box, Typography, Chip, Paper } from "@mui/material";
import { Lightbulb as TipsIcon } from "@mui/icons-material";
import { useAnalysisPanel } from "../AnalysisPanelContext";

export const AnalysisPanelTakeawaysTab: React.FC = () => {
  const { analysis: ctxAnalysis } = useAnalysisPanel();

  const keyTakeaways = ctxAnalysis?.key_takeaways;

  if (!keyTakeaways || keyTakeaways.length === 0) {
    return (
      <Box sx={{ p: 3, textAlign: "center" }}>
        <Typography variant="body1" sx={{ color: "#64748b" }}>
          No key takeaways generated yet.
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 2 }}>
      <Box sx={{ display: "flex", gap: 1.5, alignItems: "center", mb: 2 }}>
        <TipsIcon sx={{ color: "#6366f1" }} />
        <Typography variant="h6" sx={{ fontWeight: 600, color: "#0f172a" }}>
          Key Takeaways
        </Typography>
      </Box>
      <Stack spacing={2}>
        {keyTakeaways.map((takeaway: string, idx: number) => (
          <Paper key={idx} elevation={0} sx={{ p: 2, bgcolor: "#f0fdf4", border: "1px solid rgba(34,197,94,0.2)", borderRadius: 2, display: "flex", alignItems: "flex-start", gap: 1.5 }}>
            <Chip label={idx + 1} size="small" sx={{ minWidth: 24, bgcolor: "#22c55e", color: "#fff" }} />
            <Typography variant="body2" sx={{ color: "#166534" }}>
              {takeaway}
            </Typography>
          </Paper>
        ))}
      </Stack>
    </Box>
  );
};