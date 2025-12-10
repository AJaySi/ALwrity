import React, { useMemo } from "react";
import { Stack, Typography, Divider, Chip, Tooltip, IconButton, alpha } from "@mui/material";
import { OpenInNew as OpenInNewIcon, ContentCopy as ContentCopyIcon } from "@mui/icons-material";
import { Fact } from "./types";
import { GlassyCard, glassyCardSx } from "./ui";

interface FactCardProps {
  fact: Fact;
}

export const FactCard: React.FC<FactCardProps> = ({ fact }) => {
  const hostname = useMemo(() => {
    try {
      return new URL(fact.url).hostname;
    } catch {
      return fact.url;
    }
  }, [fact.url]);

  const handleCopy = () => {
    navigator.clipboard.writeText(fact.quote);
  };

  return (
    <GlassyCard
      whileHover={{ y: -4 }}
      sx={{
        ...glassyCardSx,
        p: 2,
        cursor: "pointer",
        transition: "all 0.2s",
        "&:hover": {
          borderColor: "rgba(102,126,234,0.25)",
          boxShadow: "0 12px 28px rgba(15,23,42,0.08)",
        },
        background: "#ffffff",
        border: "1px solid rgba(0,0,0,0.06)",
      }}
    >
      <Stack spacing={1.5}>
        <Typography variant="body2" sx={{ lineHeight: 1.6, color: "#0f172a" }}>
          {fact.quote}
        </Typography>
        <Divider sx={{ borderColor: "rgba(0,0,0,0.06)" }} />
        <Stack direction="row" spacing={1} alignItems="center" justifyContent="space-between">
          <Stack direction="row" spacing={1} alignItems="center" flex={1}>
            <OpenInNewIcon fontSize="small" sx={{ color: "rgba(15,23,42,0.6)" }} />
            <Typography
              variant="caption"
              component="a"
              href={fact.url}
              target="_blank"
              rel="noreferrer"
              sx={{
                color: "#4f46e5",
                textDecoration: "none",
                "&:hover": { textDecoration: "underline" },
                flex: 1,
                overflow: "hidden",
                textOverflow: "ellipsis",
              }}
            >
              {hostname || "source"}
            </Typography>
          </Stack>
          <Tooltip title="Copy citation">
            <IconButton size="small" onClick={handleCopy} sx={{ color: "rgba(15,23,42,0.65)" }}>
              <ContentCopyIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Stack>
        <Stack direction="row" spacing={2}>
          <Chip
            label={`${(fact.confidence * 100).toFixed(0)}% confidence`}
            size="small"
            sx={{
              height: 20,
              fontSize: "0.65rem",
              background: alpha("#22c55e", 0.15),
              color: "#15803d",
              border: "1px solid rgba(34,197,94,0.35)",
            }}
          />
          <Typography variant="caption" sx={{ color: "#475569" }}>
            {fact.date}
          </Typography>
        </Stack>
      </Stack>
    </GlassyCard>
  );
};

