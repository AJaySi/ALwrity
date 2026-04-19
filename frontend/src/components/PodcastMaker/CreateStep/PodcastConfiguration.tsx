import React, { useState } from "react";
import { Stack, Box, Typography, TextField, ToggleButton, ToggleButtonGroup, alpha, IconButton, Tooltip } from "@mui/material";
import { Person as PersonIcon, Group as GroupIcon, Settings as SettingsIcon, HelpOutline as HelpOutlineIcon, Headphones as HeadphonesIcon, Videocam as VideocamIcon } from "@mui/icons-material";
import { PodcastMode } from "../types";
import { PodcastModeInfoModal } from "./PodcastModeInfoModal";

interface PodcastConfigurationProps {
  duration: number;
  setDuration: (value: number) => void;
  speakers: number;
  setSpeakers: (value: number) => void;
  podcastMode: PodcastMode;
  setPodcastMode: (mode: PodcastMode) => void;
}

export const PodcastConfiguration: React.FC<PodcastConfigurationProps> = ({
  duration,
  setDuration,
  speakers,
  setSpeakers,
  podcastMode,
  setPodcastMode,
}) => {
  const [modeInfoOpen, setModeInfoOpen] = useState(false);

  const handleDurationChange = (value: number) => {
    const clamped = Math.min(10, Math.max(1, value));
    setDuration(clamped);
  };

  const handleSpeakersChange = (
    event: React.MouseEvent<HTMLElement>,
    newValue: number | null
  ) => {
    if (newValue !== null) {
      setSpeakers(newValue);
    }
  };

  const handleModeChange = (
    event: React.MouseEvent<HTMLElement>,
    newValue: PodcastMode | null
  ) => {
    if (newValue !== null) {
      setPodcastMode(newValue);
    }
  };

  const podcastModes: { value: PodcastMode; label: string; icon: React.ReactNode; color: string; desc: string }[] = [
    { value: "audio_only", label: "Audio", icon: <HeadphonesIcon fontSize="small" />, color: "#10b981", desc: "Audio podcast only" },
    { value: "video_only", label: "Video", icon: <VideocamIcon fontSize="small" />, color: "#f97316", desc: "AI avatar video" },
    { value: "audio_video", label: "Both", icon: <><HeadphonesIcon fontSize="small" /><VideocamIcon fontSize="small" /></>, color: "#8b5cf6", desc: "Audio + Video" },
  ];

  return (
    <Box
      sx={{
        flex: { xs: "1 1 auto", lg: "0 0 320px" },
        width: { xs: "100%", lg: "320px" },
        p: 3,
        borderRadius: 3,
        background: "#ffffff",
        border: "1px solid rgba(102, 126, 234, 0.15)",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        boxShadow: "0 4px 20px rgba(102, 126, 234, 0.08)",
        position: "relative",
        overflow: "hidden",
        "&::before": {
          content: '""',
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          height: "3px",
          background: "linear-gradient(90deg, #667eea 0%, #764ba2 100%)",
        },
      }}
    >
      <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2.5 }}>
        <Box
          sx={{
            width: 24,
            height: 24,
            borderRadius: "50%",
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            boxShadow: "0 2px 8px rgba(102, 126, 234, 0.25)",
          }}
        >
          <Typography sx={{ color: "#fff", fontSize: "0.75rem", fontWeight: 700 }}>2</Typography>
        </Box>
        <Box
          sx={{
            width: 32,
            height: 32,
            borderRadius: 1.5,
            background: "linear-gradient(135deg, rgba(102, 126, 234, 0.12) 0%, rgba(118, 75, 162, 0.12) 100%)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            boxShadow: "0 2px 8px rgba(102, 126, 234, 0.15)",
          }}
        >
          <SettingsIcon sx={{ color: "#667eea", fontSize: "1rem" }} />
        </Box>
        <Typography 
          variant="subtitle1" 
          sx={{ 
            color: "#0f172a", 
            fontWeight: 700, 
            fontSize: "1rem",
            letterSpacing: "-0.01em",
          }}
        >
          Basic Configuration
        </Typography>
      </Stack>
      
      <Stack spacing={3}>
        {/* Podcast Mode */}
        <Box>
          <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
            <Typography variant="caption" sx={{ display: "block", color: "#64748b", fontWeight: 600, fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.05em" }}>
              Podcast Mode
            </Typography>
            <Tooltip title="Learn about podcast modes">
              <IconButton size="small" onClick={() => setModeInfoOpen(true)} sx={{ color: "#94a3b8", p: 0.25, "&:hover": { color: "#667eea" } }}>
                <HelpOutlineIcon sx={{ fontSize: "0.9rem" }} />
              </IconButton>
            </Tooltip>
          </Stack>
          <ToggleButtonGroup
            value={podcastMode}
            exclusive
            onChange={handleModeChange}
            fullWidth
            size="small"
            sx={{
              backgroundColor: "#f8fafc",
              border: "2px solid rgba(102, 126, 234, 0.2)",
              borderRadius: 2,
              p: 0.5,
              "& .MuiToggleButton-root": {
                border: "none",
                borderRadius: 1.5,
                color: "#64748b",
                textTransform: "none",
                fontWeight: 500,
                fontSize: "0.875rem",
                py: 1,
                transition: "all 0.2s ease",
                "&:hover": {
                  backgroundColor: alpha("#667eea", 0.08),
                },
                "&.Mui-selected": {
                  background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                  color: "#ffffff",
                  fontWeight: 600,
                  boxShadow: "0 4px 12px rgba(102, 126, 234, 0.3)",
                  "&:hover": {
                    background: "linear-gradient(135deg, #764ba2 0%, #667eea 100%)",
                  },
                },
              },
            }}
          >
            {podcastModes.map((mode) => (
              <ToggleButton key={mode.value} value={mode.value} aria-label={mode.label}>
                <Stack direction="row" spacing={0.5} alignItems="center">
                  {mode.icon}
                  <Typography variant="body2">{mode.label}</Typography>
                </Stack>
              </ToggleButton>
            ))}
          </ToggleButtonGroup>
          <Typography variant="caption" sx={{ display: "block", mt: 1, color: podcastModes.find(m => m.value === podcastMode)?.color || "#64748b", fontSize: "0.75rem", fontWeight: 500 }}>
            {podcastModes.find(m => m.value === podcastMode)?.desc}
            {podcastMode === "audio_only" && " • No avatar needed • Lowest cost"}
            {podcastMode === "video_only" && " • Requires avatar • Medium cost"}
            {podcastMode === "audio_video" && " • Both formats • Highest cost"}
          </Typography>
        </Box>

        {/* Duration Input */}
        <Box>
          <Typography variant="caption" sx={{ display: "block", mb: 1, color: "#64748b", fontWeight: 600, fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.05em" }}>
            Duration (minutes)
          </Typography>
          <TextField
            type="number"
            value={duration}
            onChange={(e) => handleDurationChange(Number(e.target.value) || 1)}
            InputProps={{ inputProps: { min: 1, max: 10 } }}
            size="small"
            helperText={duration > 10 ? "Maximum duration is 10 minutes" : "Recommended: 1-3 mins"}
            error={duration > 10}
            fullWidth
            sx={{
              "& .MuiOutlinedInput-root": {
                backgroundColor: "#f8fafc",
                border: "2px solid rgba(102, 126, 234, 0.2)",
                borderRadius: 2,
                transition: "all 0.2s",
                "&:hover": { 
                  borderColor: "rgba(102, 126, 234, 0.4)",
                  boxShadow: "0 2px 8px rgba(102, 126, 234, 0.1)",
                },
                "&.Mui-focused": {
                  borderColor: "#667eea",
                  boxShadow: "0 0 0 4px rgba(102, 126, 234, 0.1)",
                  backgroundColor: "#ffffff",
                },
              },
              "& .MuiOutlinedInput-input": {
                color: "#1e293b",
                fontWeight: 600,
                fontSize: "1rem",
              },
              "& .MuiFormHelperText-root": {
                color: duration > 10 ? "#dc2626" : "#64748b",
                fontSize: "0.75rem",
                mt: 1,
                fontWeight: 500,
              },
            }}
          />
        </Box>

        {/* Speakers Toggle */}
        <Box>
          <Typography variant="caption" sx={{ display: "block", mb: 1, color: "#64748b", fontWeight: 600, fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.05em" }}>
            Number of Speakers
          </Typography>
          <ToggleButtonGroup
            value={speakers}
            exclusive
            onChange={handleSpeakersChange}
            fullWidth
            size="small"
            sx={{
              backgroundColor: "#f8fafc",
              border: "2px solid rgba(102, 126, 234, 0.2)",
              borderRadius: 2,
              p: 0.5,
              "& .MuiToggleButton-root": {
                border: "none",
                borderRadius: 1.5,
                color: "#64748b",
                textTransform: "none",
                fontWeight: 500,
                fontSize: "0.875rem",
                py: 1,
                transition: "all 0.2s ease",
                "&:hover": {
                  backgroundColor: alpha("#667eea", 0.08),
                },
                "&.Mui-selected": {
                  background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                  color: "#ffffff",
                  fontWeight: 600,
                  boxShadow: "0 4px 12px rgba(102, 126, 234, 0.3)",
                  "&:hover": {
                    background: "linear-gradient(135deg, #764ba2 0%, #667eea 100%)",
                  },
                },
              },
            }}
          >
            <ToggleButton value={1} aria-label="1 speaker">
              <Stack direction="row" spacing={1} alignItems="center">
                <PersonIcon fontSize="small" />
                <Typography variant="body2">1 Speaker</Typography>
              </Stack>
            </ToggleButton>
            <ToggleButton value={2} aria-label="2 speakers">
              <Stack direction="row" spacing={1} alignItems="center">
                <GroupIcon fontSize="small" />
                <Typography variant="body2">2 Speakers</Typography>
              </Stack>
            </ToggleButton>
          </ToggleButtonGroup>
          <Typography variant="caption" sx={{ display: "block", mt: 1, color: "#64748b", fontSize: "0.75rem", fontWeight: 500 }}>
            {speakers === 1 ? "Single host format" : "Host and guest conversation"}
          </Typography>
        </Box>
      </Stack>

      <PodcastModeInfoModal open={modeInfoOpen} onClose={() => setModeInfoOpen(false)} />
    </Box>
  );
};
