import React from "react";
import { Box, Stack, Typography, Paper } from "@mui/material";
import { Script, Job } from "../types";

interface SummaryStatsProps {
  jobs: Job[];
  scenes: Script["scenes"];
}

export const SummaryStats: React.FC<SummaryStatsProps> = ({ jobs, scenes }) => {
  const totalScenes = jobs.length > 0 ? jobs.length : scenes.length;
  const readyToRender = jobs.length > 0
    ? jobs.filter((j) => j.status === "idle").length
    : scenes.filter((s) => !s.audioUrl).length;
  const completed = jobs.length > 0
    ? jobs.filter((j) => j.status === "completed").length
    : scenes.filter((s) => s.audioUrl).length;
  const inProgress = jobs.length > 0
    ? jobs.filter((j) => j.status === "running" || j.status === "previewing").length
    : 0;

  if (totalScenes === 0) return null;

  return (
    <Paper
      sx={{
        p: 2.5,
        mb: 3,
        background: "linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%)",
        border: "1px solid rgba(102, 126, 234, 0.15)",
        borderRadius: 2,
      }}
    >
      <Stack direction="row" spacing={3} flexWrap="wrap" useFlexGap>
        <Box>
          <Typography variant="caption" sx={{ color: "#64748b", fontWeight: 500, display: "block", mb: 0.5 }}>
            Total Scenes
          </Typography>
          <Typography variant="h6" sx={{ color: "#0f172a", fontWeight: 700 }}>
            {totalScenes}
          </Typography>
        </Box>
        <Box>
          <Typography variant="caption" sx={{ color: "#64748b", fontWeight: 500, display: "block", mb: 0.5 }}>
            Ready to Render
          </Typography>
          <Typography variant="h6" sx={{ color: "#667eea", fontWeight: 700 }}>
            {readyToRender}
          </Typography>
        </Box>
        <Box>
          <Typography variant="caption" sx={{ color: "#64748b", fontWeight: 500, display: "block", mb: 0.5 }}>
            Completed
          </Typography>
          <Typography variant="h6" sx={{ color: "#10b981", fontWeight: 700 }}>
            {completed}
          </Typography>
        </Box>
        <Box>
          <Typography variant="caption" sx={{ color: "#64748b", fontWeight: 500, display: "block", mb: 0.5 }}>
            In Progress
          </Typography>
          <Typography variant="h6" sx={{ color: "#3b82f6", fontWeight: 700 }}>
            {inProgress}
          </Typography>
        </Box>
      </Stack>
    </Paper>
  );
};

