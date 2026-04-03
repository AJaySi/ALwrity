import React from "react";
import { Box, Typography, Paper } from "@mui/material";
import { Psychology as PsychologyIcon } from "@mui/icons-material";
import { PodcastAnalysis } from "../../types";
import { AnalysisTabContent } from "../AnalysisTabNav";

interface CTATabProps {
  analysis: PodcastAnalysis;
}

export const CTATab: React.FC<CTATabProps> = ({ analysis }) => {
  if (!analysis.listener_cta) {
    return (
      <AnalysisTabContent title="Listener CTA" icon={<PsychologyIcon />}>
        <Typography variant="body2" sx={{ color: "#64748b" }}>
          No listener call-to-action generated yet.
        </Typography>
      </AnalysisTabContent>
    );
  }

  return (
    <AnalysisTabContent title="Listener CTA" icon={<PsychologyIcon />}>
      <Paper elevation={0} sx={{ p: 3, bgcolor: "#fff7ed", border: "1px solid rgba(249,115,22,0.2)", borderRadius: 2 }}>
        <Typography variant="body1" sx={{ color: "#c2410c", fontWeight: 500, lineHeight: 1.6 }}>
          {analysis.listener_cta}
        </Typography>
      </Paper>
      <Typography variant="caption" sx={{ color: "#64748b", mt: 1, display: "block" }}>
        This is a call-to-action for listeners to take action after the episode.
      </Typography>
    </AnalysisTabContent>
  );
};
