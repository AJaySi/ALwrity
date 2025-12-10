import React from "react";
import { Stack, Box, Typography, Paper, Chip, alpha } from "@mui/material";
import { LibraryMusic as LibraryMusicIcon, OpenInNew as OpenInNewIcon, VolumeUp as VolumeUpIcon } from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import { useContentAssets } from "../../hooks/useContentAssets";
import { GlassyCard, glassyCardSx, SecondaryButton } from "./ui";

interface RecentEpisodesPreviewProps {
  onSelectEpisode: (assetId: number) => void;
}

export const RecentEpisodesPreview: React.FC<RecentEpisodesPreviewProps> = ({ onSelectEpisode }) => {
  const navigate = useNavigate();
  const { assets, loading } = useContentAssets({
    asset_type: "audio",
    source_module: "podcast_maker",
    limit: 6,
  });

  if (loading || assets.length === 0) {
    return null;
  }

  return (
    <GlassyCard sx={glassyCardSx}>
      <Stack spacing={2}>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Typography variant="h6" sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <LibraryMusicIcon />
            Recent Episodes
          </Typography>
          <SecondaryButton
            onClick={() => navigate("/asset-library?source_module=podcast_maker&asset_type=audio")}
            startIcon={<OpenInNewIcon />}
          >
            View All
          </SecondaryButton>
        </Stack>
        <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", sm: "1fr 1fr", md: "1fr 1fr 1fr" }, gap: 2 }}>
          {assets.slice(0, 6).map((asset) => (
            <Paper
              key={asset.id}
              sx={{
                p: 2,
                background: alpha("#1e293b", 0.5),
                border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: 2,
                cursor: "pointer",
                "&:hover": {
                  borderColor: "rgba(102,126,234,0.4)",
                  background: alpha("#1e293b", 0.7),
                },
              }}
              onClick={() => onSelectEpisode(asset.id)}
            >
              <Stack spacing={1}>
                <Typography variant="subtitle2" sx={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {asset.title || "Untitled Episode"}
                </Typography>
                <Stack direction="row" spacing={1} alignItems="center">
                  <VolumeUpIcon fontSize="small" sx={{ color: "rgba(255,255,255,0.5)" }} />
                  <Typography variant="caption" color="text.secondary">
                    {new Date(asset.created_at).toLocaleDateString()}
                  </Typography>
                </Stack>
                {asset.cost > 0 && (
                  <Chip label={`$${asset.cost.toFixed(2)}`} size="small" sx={{ width: "fit-content", fontSize: "0.65rem", height: 20 }} />
                )}
              </Stack>
            </Paper>
          ))}
        </Box>
      </Stack>
    </GlassyCard>
  );
};

