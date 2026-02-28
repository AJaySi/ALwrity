import React from "react";
import { Stack, Typography } from "@mui/material";
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
    <Stack sx={{ width: "100%", minWidth: 0 }} spacing={1.5}>
      <Stack
        direction="row"
        justifyContent="space-between"
        alignItems="center"
        flexWrap="wrap"
        gap={2}
      >
        <Typography
          variant="h3"
          sx={{
            color: "#1e293b",
            fontWeight: 800,
            display: "flex",
            alignItems: "center",
            gap: 1.5,
            fontSize: { xs: "1.5rem", md: "2rem" },
          }}
        >
          <MicIcon fontSize="large" sx={{ color: "#667eea" }} />
          AI Podcast Maker
        </Typography>
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
          }}
        >
          <HeaderControls colorMode="light" showAlerts={true} showUser={true} />
          <SecondaryButton
            onClick={() => window.open("/docs", "_blank")}
            startIcon={<InfoIcon />}
            sx={{
              display: { xs: "none", lg: "flex" },
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
              display: "flex !important",
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
              display: "flex",
            }}
          >
            New Episode
          </PrimaryButton>
        </Stack>
      </Stack>
      <Typography
        variant="body2"
        color="text.secondary"
        sx={{ display: { xs: "none", sm: "block" } }}
      >
        Create professional podcast episodes with AI-powered research, smart scriptwriting, and natural voice narration
      </Typography>
    </Stack>
  );
};

