import React from "react";
import { Box, Stack, Typography, Chip, Paper, alpha } from "@mui/material";
import { Input as InputIcon, Mic as MicIcon } from "@mui/icons-material";
import { useAnalysisPanel } from "../AnalysisPanelContext";

interface AnalysisTabContentProps {
  title: string;
  icon?: React.ReactNode;
  children: React.ReactNode;
}

const AnalysisTabContent: React.FC<AnalysisTabContentProps> = ({ title, icon, children }) => (
  <Box sx={{ p: 2 }}>
    <Stack direction="row" spacing={1.5} alignItems="center" mb={2}>
      {icon && <Box sx={{ color: "#6366f1" }}>{icon}</Box>}
      <Typography variant="h6" sx={{ fontWeight: 600, color: "#0f172a" }}>
        {title}
      </Typography>
    </Stack>
    {children}
  </Box>
);

export const AnalysisPanelInputsTab: React.FC = () => {
  const { idea, duration, speakers, avatarUrl, avatarPrompt, estimate } = useAnalysisPanel();

  if (!idea && !duration && !speakers && !avatarUrl && !avatarPrompt) {
    return (
      <Box sx={{ p: 3, textAlign: "center" }}>
        <Typography variant="body1" sx={{ color: "#64748b" }}>
          No analysis data available. Please generate analysis first.
        </Typography>
      </Box>
    );
  }

  return (
    <AnalysisTabContent title="Your Inputs" icon={<InputIcon />}>
      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: { xs: "1fr", md: avatarUrl ? "1fr 1fr" : "1fr" },
          gap: 3,
          alignItems: "flex-start",
        }}
      >
        <Stack spacing={1.5}>
          {idea && (
            <Box>
              <Typography variant="caption" sx={{ color: "#64748b", fontWeight: 600, display: "block", mb: 0.5 }}>
                Podcast Idea
              </Typography>
              <Typography variant="body2" sx={{ color: "#0f172a", wordBreak: "break-word" }}>
                {idea}
              </Typography>
            </Box>
          )}
          <Stack direction="row" spacing={2} flexWrap="wrap">
            {estimate?.voiceName && (
              <Box>
                <Typography variant="caption" sx={{ color: "#64748b", fontWeight: 600, display: "block", mb: 0.5 }}>
                  Voice
                </Typography>
                <Chip
                  icon={<MicIcon sx={{ fontSize: "14px !important" }} />}
                  label={estimate.voiceName}
                  size="small"
                  sx={{ 
                    background: estimate.isCustomVoice ? "rgba(16, 185, 129, 0.1)" : "rgba(99, 102, 241, 0.1)", 
                    color: estimate.isCustomVoice ? "#10b981" : "#6366f1", 
                    border: `1px solid ${estimate.isCustomVoice ? "rgba(16, 185, 129, 0.3)" : "rgba(99, 102, 241, 0.2)"}`,
                    '& .MuiChip-icon': { color: estimate.isCustomVoice ? "#10b981" : "#6366f1" }
                  }}
                />
              </Box>
            )}
            {duration !== undefined && (
              <Box>
                <Typography variant="caption" sx={{ color: "#64748b", fontWeight: 600, display: "block", mb: 0.5 }}>
                  Duration
                </Typography>
                <Chip
                  label={`${duration} minutes`}
                  size="small"
                  sx={{ background: "#f1f5f9", color: "#0f172a", border: "1px solid rgba(0,0,0,0.08)" }}
                />
              </Box>
            )}
            {speakers !== undefined && (
              <Box>
                <Typography variant="caption" sx={{ color: "#64748b", fontWeight: 600, display: "block", mb: 0.5 }}>
                  Speakers
                </Typography>
                <Chip
                  label={speakers === 1 ? "Solo" : `${speakers} speakers`}
                  size="small"
                  sx={{ background: "#f1f5f9", color: "#0f172a", border: "1px solid rgba(0,0,0,0.08)" }}
                />
              </Box>
            )}
          </Stack>
        </Stack>
        {avatarUrl && (
          <Paper sx={{ p: 2, background: "#f8fafc", border: "1px solid rgba(0,0,0,0.08)" }}>
            <Typography variant="caption" sx={{ color: "#64748b", fontWeight: 600, display: "block", mb: 1 }}>
              Avatar Preview
            </Typography>
            <Box
              component="img"
              src={avatarUrl}
              alt="Avatar"
              sx={{
                width: "100%",
                maxWidth: 120,
                height: "auto",
                borderRadius: 2,
                border: "1px solid rgba(0,0,0,0.1)",
              }}
            />
            {avatarPrompt && (
              <Typography variant="caption" sx={{ color: "#64748b", mt: 1, display: "block" }}>
                Prompt: {avatarPrompt}
              </Typography>
            )}
          </Paper>
        )}
      </Box>
    </AnalysisTabContent>
  );
};