import React from "react";
import { Stack, Typography, Box } from "@mui/material";
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
    <Box
      sx={{
        width: "100%",
        minWidth: 0,
        background: "linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%)",
        borderRadius: 3,
        p: { xs: 2, md: 2.5 },
        border: "1px solid rgba(102, 126, 234, 0.15)",
        position: "relative",
        overflow: "hidden",
        "&::before": {
          content: '""',
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          height: "3px",
          background: "linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%)",
        },
      }}
    >
      <Stack
        direction="row"
        justifyContent="space-between"
        alignItems="center"
        flexWrap="wrap"
        gap={2}
      >
        <Stack direction="row" alignItems="center" gap={1.5}>
          <Box
            sx={{
              width: 44,
              height: 44,
              borderRadius: 2,
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "0 4px 12px rgba(102, 126, 234, 0.3)",
            }}
          >
            <MicIcon sx={{ color: "#fff", fontSize: 24 }} />
          </Box>
          <Typography
            variant="h5"
            sx={{
              background: "linear-gradient(135deg, #1e293b 0%, #334155 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              fontWeight: 700,
              fontSize: { xs: "1.25rem", md: "1.5rem" },
              letterSpacing: "-0.02em",
            }}
          >
            ALwrity Podcast Maker
          </Typography>
        </Stack>
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
    </Box>
  );
};

