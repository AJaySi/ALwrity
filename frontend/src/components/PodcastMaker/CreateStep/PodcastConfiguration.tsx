import React from "react";
import { Stack, Box, Typography, TextField, ToggleButton, ToggleButtonGroup, alpha } from "@mui/material";
import { Person as PersonIcon, Group as GroupIcon } from "@mui/icons-material";

interface PodcastConfigurationProps {
  duration: number;
  setDuration: (value: number) => void;
  speakers: number;
  setSpeakers: (value: number) => void;
}

export const PodcastConfiguration: React.FC<PodcastConfigurationProps> = ({
  duration,
  setDuration,
  speakers,
  setSpeakers,
}) => {
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

  return (
    <Box
      sx={{
        flex: { xs: "1 1 auto", lg: "0 0 320px" },
        width: { xs: "100%", lg: "320px" },
        p: 3,
        borderRadius: 2,
        background: alpha("#f8fafc", 0.5),
        border: "1px solid rgba(15, 23, 42, 0.06)",
        height: "100%",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <Typography variant="subtitle2" sx={{ mb: 2.5, color: "#0f172a", fontWeight: 600, fontSize: "0.9375rem" }}>
        Basic Configuration
      </Typography>
      
      <Stack spacing={3}>
        {/* Duration Input */}
        <Box>
          <Typography variant="caption" sx={{ display: "block", mb: 1, color: "#64748b", fontWeight: 500 }}>
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
                backgroundColor: "#ffffff",
                border: "1px solid rgba(15, 23, 42, 0.12)",
                borderRadius: 2,
                transition: "all 0.2s",
                "&:hover": { 
                  borderColor: "rgba(102, 126, 234, 0.6)",
                },
                "&.Mui-focused": {
                  borderColor: "#667eea",
                  boxShadow: "0 0 0 3px rgba(102, 126, 234, 0.1)",
                },
              },
              "& .MuiOutlinedInput-input": {
                color: "#0f172a",
                fontWeight: 600,
                fontSize: "0.9375rem",
              },
              "& .MuiFormHelperText-root": {
                color: duration > 10 ? "#dc2626" : "#64748b",
                fontSize: "0.75rem",
                mt: 0.75,
              },
            }}
          />
        </Box>

        {/* Speakers Toggle */}
        <Box>
          <Typography variant="caption" sx={{ display: "block", mb: 1, color: "#64748b", fontWeight: 500 }}>
            Number of Speakers
          </Typography>
          <ToggleButtonGroup
            value={speakers}
            exclusive
            onChange={handleSpeakersChange}
            fullWidth
            size="small"
            sx={{
              backgroundColor: "#ffffff",
              border: "1px solid rgba(15, 23, 42, 0.12)",
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
                  backgroundColor: alpha("#64748b", 0.05),
                },
                "&.Mui-selected": {
                  backgroundColor: alpha("#667eea", 0.1),
                  color: "#667eea",
                  fontWeight: 600,
                  "&:hover": {
                    backgroundColor: alpha("#667eea", 0.15),
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
          <Typography variant="caption" sx={{ display: "block", mt: 0.75, color: "#64748b", fontSize: "0.75rem" }}>
            {speakers === 1 ? "Single host format" : "Host and guest conversation"}
          </Typography>
        </Box>
      </Stack>
    </Box>
  );
};
