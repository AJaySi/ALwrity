import React from "react";
import { Box, Stack, Typography, Chip, Paper, CircularProgress, alpha } from "@mui/material";
import { Input as InputIcon, Person as PersonIcon, AutoAwesome as AutoAwesomeIcon } from "@mui/icons-material";
import { AnalysisTabContent } from "../AnalysisTabNav";

interface InputsTabProps {
  idea?: string;
  duration?: number;
  speakers?: number;
  voiceName?: string;
  podcastMode?: "audio_only" | "video_only" | "audio_video";
  avatarUrl?: string | null;
  avatarPrompt?: string | null;
  avatarBlobUrl?: string | null;
  avatarLoading?: boolean;
  avatarError?: boolean;
}

export const InputsTab: React.FC<InputsTabProps> = ({ idea, duration, speakers, voiceName, podcastMode, avatarUrl, avatarPrompt, avatarBlobUrl, avatarLoading, avatarError }) => {
  if (!idea && !duration && !speakers && !voiceName && !podcastMode && !avatarUrl && !avatarPrompt) {
    return null;
  }

  return (
    <AnalysisTabContent title="Your Inputs" icon={<InputIcon />}>
      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: { xs: "1fr", md: avatarUrl && podcastMode !== "audio_only" ? "1fr 1fr" : "1fr" },
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
                  label={`${speakers} ${speakers === 1 ? "speaker" : "speakers"}`}
                  size="small"
                  sx={{ background: "#f1f5f9", color: "#0f172a", border: "1px solid rgba(0,0,0,0.08)" }}
                />
              </Box>
            )}
            {voiceName && (
              <Box>
                <Typography variant="caption" sx={{ color: "#64748b", fontWeight: 600, display: "block", mb: 0.5 }}>
                  Voice
                </Typography>
                <Chip
                  label={voiceName}
                  size="small"
                  sx={{ background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)", color: "#fff", fontWeight: 600 }}
                />
              </Box>
            )}
            {podcastMode && (
              <Box>
                <Typography variant="caption" sx={{ color: "#64748b", fontWeight: 600, display: "block", mb: 0.5 }}>
                  Podcast Mode
                </Typography>
                <Chip
                  label={podcastMode === "audio_only" ? "Audio Only" : podcastMode === "video_only" ? "Video" : "Audio + Video"}
                  size="small"
                  sx={{
                    background: podcastMode === "audio_only"
                      ? "#10b981"
                      : podcastMode === "video_only"
                      ? "#f97316"
                      : "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                    color: "#fff",
                    fontWeight: 600,
                  }}
                />
              </Box>
            )}
          </Stack>
          
          {avatarPrompt && (
            <Box>
              <Typography
                variant="caption"
                sx={{
                  color: "#64748b",
                  fontWeight: 600,
                  display: "flex",
                  alignItems: "center",
                  gap: 0.5,
                  mb: 0.75,
                }}
              >
                <AutoAwesomeIcon sx={{ fontSize: 14 }} />
                AI Generation Prompt
              </Typography>
              <Paper
                sx={{
                  p: 1.5,
                  background: "#f8fafc",
                  border: "1px solid rgba(0,0,0,0.08)",
                  borderRadius: 1.5,
                  maxHeight: 200,
                  overflow: "auto",
                }}
              >
                <Typography
                  variant="caption"
                  sx={{
                    color: "#475569",
                    fontFamily: "monospace",
                    fontSize: "0.75rem",
                    lineHeight: 1.6,
                    whiteSpace: "pre-wrap",
                    wordBreak: "break-word",
                    display: "block",
                  }}
                >
                  {avatarPrompt}
                </Typography>
              </Paper>
            </Box>
          )}
        </Stack>

        {podcastMode !== "audio_only" && avatarUrl && (
          <Box>
            <Typography
              variant="caption"
              sx={{
                color: "#64748b",
                fontWeight: 600,
                display: "flex",
                alignItems: "center",
                gap: 0.5,
                mb: 1,
              }}
            >
              <PersonIcon sx={{ fontSize: 16 }} />
              Presenter Avatar
            </Typography>
            <Box
              sx={{
                width: "100%",
                maxWidth: { xs: "100%", md: 300 },
                borderRadius: 2,
                overflow: "hidden",
                border: "1px solid rgba(102,126,234,0.2)",
                background: alpha("#667eea", 0.05),
                position: "relative",
                aspectRatio: "1",
                boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
              }}
            >
              {avatarLoading ? (
                <Box
                  sx={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    height: "100%",
                    background: "#f8fafc",
                  }}
                >
                  <CircularProgress size={40} />
                </Box>
              ) : avatarError ? (
                <Box
                  sx={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    height: "100%",
                    background: "#fef2f2",
                    color: "#dc2626",
                    p: 2,
                  }}
                >
                  <Typography variant="caption" sx={{ textAlign: "center" }}>
                    Failed to load avatar
                  </Typography>
                </Box>
              ) : avatarBlobUrl ? (
                <Box
                  component="img"
                  src={avatarBlobUrl}
                  alt="Podcast Presenter"
                  sx={{
                    width: "100%",
                    height: "100%",
                    objectFit: "cover",
                    display: "block",
                  }}
                />
              ) : null}
            </Box>
          </Box>
        )}
      </Box>
    </AnalysisTabContent>
  );
};
