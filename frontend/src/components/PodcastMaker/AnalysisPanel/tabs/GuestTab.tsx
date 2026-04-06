import React from "react";
import { Stack, Box, Typography, Chip, Paper } from "@mui/material";
import { Quiz as TalkIcon } from "@mui/icons-material";
import { PodcastAnalysis } from "../../types";
import { AnalysisTabContent } from "../AnalysisTabNav";
import { TextToSpeechButton } from "../../../shared/TextToSpeechButton";

interface GuestTabProps {
  analysis: PodcastAnalysis;
}

export const GuestTab: React.FC<GuestTabProps> = ({ analysis }) => {
  const talkingPointsText = analysis.guest_talking_points?.map((p, idx) => `Question ${idx + 1}: ${p}`).join(" ") || "";

  if (!analysis.guest_talking_points || analysis.guest_talking_points.length === 0) {
    return (
      <AnalysisTabContent title="Guest Talking Points" icon={<TalkIcon />}>
        <Typography variant="body2" sx={{ color: "#64748b" }}>
          No guest talking points generated yet. Add a guest speaker to get interview questions.
        </Typography>
      </AnalysisTabContent>
    );
  }

  return (
    <AnalysisTabContent title="Guest Talking Points" icon={<TalkIcon />}>
      <Stack spacing={2}>
        <Box sx={{ display: "flex", justifyContent: "flex-end", mb: 1 }}>
          <TextToSpeechButton text={talkingPointsText} size="small" showSettings />
        </Box>
        {analysis.guest_talking_points.map((point: string, idx: number) => (
          <Paper key={idx} elevation={0} sx={{ p: 2, bgcolor: "#faf5ff", border: "1px solid rgba(168,85,247,0.2)", borderRadius: 2, display: "flex", alignItems: "flex-start", gap: 1.5 }}>
            <Chip label="Q" size="small" sx={{ minWidth: 24, bgcolor: "#a855f7", color: "#fff" }} />
            <Typography variant="body2" sx={{ color: "#6b21a8" }}>
              {point}
            </Typography>
          </Paper>
        ))}
      </Stack>
    </AnalysisTabContent>
  );
};
