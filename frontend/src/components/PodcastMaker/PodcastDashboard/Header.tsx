import React, { useState } from "react";
import { Stack, Typography, Box, IconButton, Menu, MenuItem, Divider, ListItemIcon, ListItemText } from "@mui/material";
import {
  Mic as MicIcon,
  Menu as MenuIcon,
  Close as CloseIcon,
  AutoAwesome as AutoAwesomeIcon,
  LibraryMusic as LibraryMusicIcon,
  Folder as FolderIcon,
  Help as HelpIcon,
  Add as AddIcon,
  BarChart as BarChartIcon,
} from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import { PrimaryButton } from "../ui";
import HeaderControls from "../../shared/HeaderControls";

interface HeaderProps {
  onShowProjects: () => void;
  onNewEpisode: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onShowProjects, onNewEpisode }) => {
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const isMenuOpen = Boolean(anchorEl);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleHelp = () => {
    handleMenuClose();
    window.open("/docs", "_blank");
  };

  const handleMyEpisodes = () => {
    handleMenuClose();
    navigate("/asset-library?source_module=podcast_maker&asset_type=audio");
  };

  const handleMyProjects = () => {
    handleMenuClose();
    onShowProjects();
  };

  const handleNewEpisode = () => {
    handleMenuClose();
    onNewEpisode();
  };

  return (
    <Box
      sx={{
        width: "100%",
        minWidth: 0,
        background: "linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%)",
        borderRadius: 3,
        p: { xs: 1.5, md: 2.5 },
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
        gap={1}
      >
        {/* Logo and Title */}
        <Stack direction="row" alignItems="center" gap={1.5}>
          <Box
            sx={{
              width: { xs: 36, md: 44 },
              height: { xs: 36, md: 44 },
              borderRadius: 2,
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "0 4px 12px rgba(102, 126, 234, 0.3)",
            }}
          >
            <MicIcon sx={{ color: "#fff", fontSize: { xs: 20, md: 24 } }} />
          </Box>
          <Typography
            variant="h5"
            sx={{
              background: "linear-gradient(135deg, #1e293b 0%, #334155 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              fontWeight: 700,
              fontSize: { xs: "1.1rem", sm: "1.25rem", md: "1.5rem" },
              letterSpacing: "-0.02em",
            }}
          >
            ALwrity Podcast Maker
          </Typography>
        </Stack>

        {/* Right side - Hamburger Menu + HeaderControls + Create */}
        <Stack direction="row" spacing={1} alignItems="center">
          {/* Header Controls (alerts + user) */}
          <HeaderControls colorMode="light" showAlerts={true} showUser={true} />

          {/* Hamburger Menu Button */}
          <IconButton
            onClick={handleMenuOpen}
            sx={{
              background: isMenuOpen 
                ? "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
                : "rgba(102, 126, 234, 0.1)",
              border: "1px solid",
              borderColor: isMenuOpen ? "transparent" : "rgba(102, 126, 234, 0.3)",
              borderRadius: 2,
              p: 1,
              transition: "all 0.2s ease",
              "&:hover": {
                background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                borderColor: "transparent",
                transform: "scale(1.05)",
              },
            }}
          >
            {isMenuOpen ? (
              <CloseIcon sx={{ color: "#fff", fontSize: 20 }} />
            ) : (
              <MenuIcon sx={{ color: "#667eea", fontSize: 20 }} />
            )}
          </IconButton>

          {/* Dropdown Menu */}
          <Menu
            anchorEl={anchorEl}
            open={isMenuOpen}
            onClose={handleMenuClose}
            anchorOrigin={{
              vertical: "bottom",
              horizontal: "right",
            }}
            transformOrigin={{
              vertical: "top",
              horizontal: "right",
            }}
            PaperProps={{
              sx: {
                mt: 1,
                minWidth: 220,
                borderRadius: 2,
                background: "linear-gradient(135deg, #1e293b 0%, #0f172a 100%)",
                border: "1px solid rgba(102, 126, 234, 0.3)",
                boxShadow: "0 10px 40px rgba(102, 126, 234, 0.25)",
                "& .MuiMenuItem-root": {
                  color: "rgba(255, 255, 255, 0.85)",
                  px: 2,
                  py: 1.5,
                  transition: "all 0.15s ease",
                  "&:hover": {
                    background: "linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%)",
                    color: "#fff",
                  },
                },
                "& .MuiListItemIcon-root": {
                  color: "#a78bfa",
                  minWidth: 36,
                },
                "& .MuiDivider-root": {
                  borderColor: "rgba(102, 126, 234, 0.2)",
                  my: 0.5,
                },
              },
            }}
          >
            <MenuItem onClick={handleNewEpisode}>
              <ListItemIcon>
                <AddIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText 
                primary="New Episode" 
                primaryTypographyProps={{ fontWeight: 600 }}
              />
            </MenuItem>

            <MenuItem onClick={handleMyProjects}>
              <ListItemIcon>
                <FolderIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText 
                primary="My Projects"
                primaryTypographyProps={{ fontWeight: 500 }}
              />
            </MenuItem>

            <MenuItem onClick={handleMyEpisodes}>
              <ListItemIcon>
                <LibraryMusicIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText 
                primary="My Episodes"
                primaryTypographyProps={{ fontWeight: 500 }}
              />
            </MenuItem>

            <Divider />

            <MenuItem onClick={handleHelp}>
              <ListItemIcon>
                <HelpIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText 
                primary="Help & Docs"
                primaryTypographyProps={{ fontWeight: 500 }}
              />
            </MenuItem>
          </Menu>
        </Stack>
      </Stack>
    </Box>
  );
};