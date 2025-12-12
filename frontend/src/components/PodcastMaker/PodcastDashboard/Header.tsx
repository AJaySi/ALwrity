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
    <Stack direction="row" justifyContent="space-between" alignItems="flex-start" flexWrap="wrap" gap={2}>
      <Box>
        <Typography
          variant="h3"
          sx={{
            color: "#1e293b",
            fontWeight: 800,
            mb: 0.5,
            display: "flex",
            alignItems: "center",
            gap: 1.5,
          }}
        >
          <MicIcon fontSize="large" sx={{ color: "#667eea" }} />
          AI Podcast Maker
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Create professional podcast episodes with AI-powered research, smart scriptwriting, and natural voice narration
        </Typography>
      </Box>
      <Stack direction="row" spacing={1} alignItems="center">
        <HeaderControls colorMode="light" showAlerts={true} showUser={true} />
        <SecondaryButton onClick={() => window.open("/docs", "_blank")} startIcon={<InfoIcon />}>
          Help
        </SecondaryButton>
        <SecondaryButton
          onClick={() => navigate("/asset-library?source_module=podcast_maker&asset_type=audio")}
          startIcon={<LibraryMusicIcon />}
          tooltip="View all podcast episodes in Asset Library"
        >
          My Episodes
        </SecondaryButton>
        <SecondaryButton
          onClick={onShowProjects}
          startIcon={<MicIcon />}
          tooltip="View and resume saved projects"
        >
          My Projects
        </SecondaryButton>
        <PrimaryButton onClick={onNewEpisode} startIcon={<AutoAwesomeIcon />}>
          New Episode
        </PrimaryButton>
      </Stack>
    </Stack>
  );
};

