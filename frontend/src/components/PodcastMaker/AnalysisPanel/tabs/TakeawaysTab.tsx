import React from "react";
import { Stack, Box, Typography, Chip, Paper } from "@mui/material";
import { Lightbulb as TipsIcon } from "@mui/icons-material";
import { PodcastAnalysis } from "../../types";
import { AnalysisTabContent } from "../AnalysisTabNav";

interface TakeawaysTabProps {
  analysis: PodcastAnalysis;
}

export const TakeawaysTab: React.FC<TakeawaysTabProps> = ({ analysis }) => {
  if (!analysis.key_takeaways || analysis.key_takeaways.length === 0) {
    return (
      <AnalysisTabContent title="Key Takeaways" icon={<TipsIcon />}>
        <Typography variant="body2" sx={{ color: "#64748b" }}>
          No key takeaways generated yet.
        </Typography>
      </AnalysisTabContent>
    );
  }

  return (
    <AnalysisTabContent title="Key Takeaways" icon={<TipsIcon />}>
      <Stack spacing={2}>
        {analysis.key_takeaways.map((takeaway: string, idx: number) => (
          <Paper key={idx} elevation={0} sx={{ p: 2, bgcolor: "#f0fdf4", border: "1px solid rgba(34,197,94,0.2)", borderRadius: 2, display: "flex", alignItems: "flex-start", gap: 1.5 }}>
            <Chip label={idx + 1} size="small" sx={{ minWidth: 24, bgcolor: "#22c55e", color: "#fff" }} />
            <Typography variant="body2" sx={{ color: "#166534" }}>
              {takeaway}
            </Typography>
          </Paper>
        ))}
      </Stack>
    </AnalysisTabContent>
  );
};
