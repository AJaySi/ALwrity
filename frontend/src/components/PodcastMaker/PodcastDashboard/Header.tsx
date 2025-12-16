import React from "react";
import { Box, Stack, Typography } from "@mui/material";
import {
  Mic as MicIcon,
  Info as InfoIcon,
  AutoAwesome as AutoAwesomeIcon,
  LibraryMusic as LibraryMusicIcon,
} from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import { PrimaryButton, SecondaryButton } from "../ui";
import HeaderControls from "../../shared/HeaderControls";

interface HeaderProps {
  onShowProjects: () => void;
  onNewEpisode: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onShowProjects, onNewEpisode }) => {
  const navigate = useNavigate();

  return (
    <Stack 
      direction="row" 
      justifyContent="space-between" 
      alignItems="flex-start" 
      flexWrap="wrap" 
      gap={2}
      sx={{ width: "100%", minWidth: 0 }} // Ensure full width and allow wrapping
    >
      <Box sx={{ minWidth: 0, flex: { xs: "1 1 100%", md: "0 1 auto" } }}>
        <Typography
          variant="h3"
          sx={{
            color: "#1e293b",
            fontWeight: 800,
            mb: 0.5,
            display: "flex",
            alignItems: "center",
            gap: 1.5,
            fontSize: { xs: "1.5rem", md: "2rem" },
          }}
        >
          <MicIcon fontSize="large" sx={{ color: "#667eea" }} />
          AI Podcast Maker
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ display: { xs: "none", sm: "block" } }}>
          Create professional podcast episodes with AI-powered research, smart scriptwriting, and natural voice narration
        </Typography>
      </Box>
      <Stack 
        direction="row" 
        spacing={1} 
        alignItems="center" 
        flexWrap="wrap"
        useFlexGap
        sx={{ 
          justifyContent: { xs: "flex-start", md: "flex-end" },
          gap: { xs: 0.5, md: 1 },
          minWidth: 0,
          width: { xs: "100%", md: "auto" }, // Full width on mobile to allow wrapping
          flex: { xs: "1 1 100%", md: "0 1 auto" }, // Take full width on mobile
        }}
      >
        <HeaderControls colorMode="light" showAlerts={true} showUser={true} />
        <SecondaryButton 
          onClick={() => window.open("/docs", "_blank")} 
          startIcon={<InfoIcon />}
          sx={{ 
            display: { xs: "none", lg: "flex" },
            // Override for light theme
            borderColor: "rgba(102, 126, 234, 0.3) !important",
            color: "#667eea !important",
            "&:hover": {
              borderColor: "rgba(102, 126, 234, 0.5) !important",
              background: "rgba(102, 126, 234, 0.1) !important",
            },
          }}
        >
          Help
        </SecondaryButton>
        <SecondaryButton
          onClick={() => navigate("/asset-library?source_module=podcast_maker&asset_type=audio")}
          startIcon={<LibraryMusicIcon />}
          tooltip="View all podcast episodes in Asset Library"
          sx={{ 
            display: { xs: "none", xl: "flex" },
            // Override for light theme
            borderColor: "rgba(102, 126, 234, 0.3) !important",
            color: "#667eea !important",
            "&:hover": {
              borderColor: "rgba(102, 126, 234, 0.5) !important",
              background: "rgba(102, 126, 234, 0.1) !important",
            },
          }}
        >
          My Episodes
        </SecondaryButton>
        <SecondaryButton
          onClick={onShowProjects}
          startIcon={<MicIcon />}
          tooltip="View and resume saved projects"
          sx={{ 
            flexShrink: 0,
            display: "flex !important", // Always show "My Projects" - force display
            order: { xs: 1, md: 0 }, // Show first on mobile
            // Override button colors for light theme
            borderColor: "rgba(102, 126, 234, 0.3) !important",
            color: "#667eea !important",
            "&:hover": {
              borderColor: "rgba(102, 126, 234, 0.5) !important",
              background: "rgba(102, 126, 234, 0.1) !important",
            },
          }}
        >
          My Projects
        </SecondaryButton>
        <PrimaryButton 
          onClick={onNewEpisode} 
          startIcon={<AutoAwesomeIcon />}
          sx={{ 
            flexShrink: 0,
            display: "flex", // Always show "New Episode"
            order: { xs: 0, md: 1 }, // Show first on mobile
          }}
        >
          New Episode
        </PrimaryButton>
      </Stack>
    </Stack>
  );
};

