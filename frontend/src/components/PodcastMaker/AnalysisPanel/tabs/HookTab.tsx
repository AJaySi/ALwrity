import React from "react";
import { Box, Typography, Paper } from "@mui/material";
import { AutoAwesome as AutoAwesomeIcon } from "@mui/icons-material";
import { PodcastAnalysis } from "../../types";
import { AnalysisTabContent } from "../AnalysisTabNav";

interface HookTabProps {
  analysis: PodcastAnalysis;
}

export const HookTab: React.FC<HookTabProps> = ({ analysis }) => {
  if (!analysis.episode_hook) {
    return (
      <AnalysisTabContent title="Episode Hook" icon={<AutoAwesomeIcon />}>
        <Typography variant="body2" sx={{ color: "#64748b" }}>
          No episode hook generated yet.
        </Typography>
      </AnalysisTabContent>
    );
  }

  return (
    <AnalysisTabContent title="Episode Hook" icon={<AutoAwesomeIcon />}>
      <Paper elevation={0} sx={{ p: 3, bgcolor: "#f0f9ff", border: "1px solid rgba(59,130,246,0.2)", borderRadius: 2 }}>
        <Typography variant="body1" sx={{ color: "#0369a1", fontStyle: "italic", fontSize: "1.1rem", lineHeight: 1.6 }}>
          "{analysis.episode_hook}"
        </Typography>
      </Paper>
      <Typography variant="caption" sx={{ color: "#64748b", mt: 1, display: "block" }}>
        This is a 15-30 second opening hook to grab listener attention.
      </Typography>
    </AnalysisTabContent>
  );
};
