import React from "react";
import { Stack, Typography, Chip, Divider } from "@mui/material";
import InsightsIcon from "@mui/icons-material/Insights";
import { PodcastEstimate } from "../types";
import { GlassyCard, glassyCardSx } from "../ui";

interface EstimateCardProps {
  estimate: PodcastEstimate;
}

export const EstimateCard: React.FC<EstimateCardProps> = ({ estimate }) => {
  return (
    <GlassyCard
      sx={{
        ...glassyCardSx,
        background: "#ffffff",
        border: "1px solid rgba(0,0,0,0.06)",
        boxShadow: "0 10px 28px rgba(15,23,42,0.06)",
        color: "#0f172a",
      }}
      aria-label="estimate"
    >
      <Stack spacing={2}>
        <Typography variant="h6" sx={{ display: "flex", alignItems: "center", gap: 1, color: "#0f172a", fontWeight: 700 }}>
          <InsightsIcon />
          Estimated Cost
        </Typography>
        <Typography variant="h4" sx={{ color: "#4f46e5", fontWeight: 800 }}>
          ${estimate.total.toFixed(2)}
        </Typography>
        <Divider sx={{ borderColor: "rgba(0,0,0,0.08)" }} />
        <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap>
          <Chip
            label={`Analysis: $${estimate.analysisCost.toFixed(2)}`}
            size="small"
            title="Topic analysis cost"
            sx={{ background: "#eef2ff", color: "#0f172a", border: "1px solid rgba(0,0,0,0.06)" }}
          />
          <Chip
            label={`Research: $${estimate.researchCost.toFixed(2)}`}
            size="small"
            title="Research and fact-checking cost"
            sx={{ background: "#eef2ff", color: "#0f172a", border: "1px solid rgba(0,0,0,0.06)" }}
          />
          <Chip
            label={`Script: $${estimate.scriptCost.toFixed(2)}`}
            size="small"
            title="Script generation cost"
            sx={{ background: "#eef2ff", color: "#0f172a", border: "1px solid rgba(0,0,0,0.06)" }}
          />
          <Chip
            label={`Voice: $${(estimate.ttsCost + estimate.voiceCloneCost).toFixed(2)}`}
            size="small"
            title={`Voice narration ($${estimate.ttsCost.toFixed(2)}) + cloning ($${estimate.voiceCloneCost.toFixed(2)})`}
            sx={{ background: "#eef2ff", color: "#0f172a", border: "1px solid rgba(0,0,0,0.06)" }}
          />
          <Chip
            label={`Visuals: $${(estimate.avatarCost + estimate.videoCost).toFixed(2)}`}
            size="small"
            title="Avatar and video cost"
            sx={{ background: "#eef2ff", color: "#0f172a", border: "1px solid rgba(0,0,0,0.06)" }}
          />
        </Stack>
      </Stack>
    </GlassyCard>
  );
};

