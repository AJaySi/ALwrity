import React, { useMemo, useState } from "react";
import { Stack, Typography, Divider, Chip, Tooltip, IconButton, alpha, Box } from "@mui/material";
import { OpenInNew as OpenInNewIcon, ContentCopy as ContentCopyIcon, ExpandMore as ExpandMoreIcon, ExpandLess as ExpandLessIcon } from "@mui/icons-material";
import { Fact } from "./types";
import { GlassyCard, glassyCardSx } from "./ui";

interface FactCardProps {
  fact: Fact;
}

const MAX_PREVIEW_LENGTH = 200; // Characters to show before truncation

export const FactCard: React.FC<FactCardProps> = ({ fact }) => {
  const [expanded, setExpanded] = useState(false);
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

  const shouldTruncate = fact.quote.length > MAX_PREVIEW_LENGTH;
  const previewText = shouldTruncate ? fact.quote.slice(0, MAX_PREVIEW_LENGTH).trim() + "..." : fact.quote;
  const fullText = fact.quote;

  return (
    <GlassyCard
      whileHover={{ y: -2 }}
      sx={{
        ...glassyCardSx,
        p: 1.5,
        cursor: "pointer",
        transition: "all 0.2s",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        "&:hover": {
          borderColor: "rgba(102,126,234,0.25)",
          boxShadow: "0 8px 20px rgba(15,23,42,0.08)",
        },
        background: "#ffffff",
        border: "1px solid rgba(0,0,0,0.06)",
      }}
    >
      <Stack spacing={1} sx={{ flex: 1, minHeight: 0 }}>
        {/* Source Image */}
        {fact.image && (
          <Box 
            component="img" 
            src={fact.image} 
            alt={fact.url} 
            sx={{ 
              width: "100%", 
              height: 120, 
              objectFit: "cover", 
              borderRadius: 1, 
              mb: 1,
              border: "1px solid rgba(0,0,0,0.04)" 
            }} 
          />
        )}

        {/* Quote Text - Truncated with expand option */}
        <Box sx={{ flex: 1, minHeight: 0 }}>
          <Typography 
            variant="body2" 
            sx={{ 
              lineHeight: 1.5, 
              color: "#0f172a",
              fontSize: "0.8125rem",
              display: "-webkit-box",
              WebkitLineClamp: expanded ? "none" : 4,
              WebkitBoxOrient: "vertical",
              overflow: "hidden",
              textOverflow: "ellipsis",
              mb: shouldTruncate ? 0.5 : 0,
            }}
          >
            {expanded ? fullText : previewText}
          </Typography>
          
          {/* Highlights */}
          {fact.highlights && fact.highlights.length > 0 && expanded && (
            <Box sx={{ mt: 1.5, pt: 1.5, borderTop: "1px dashed rgba(0,0,0,0.06)" }}>
              <Typography variant="caption" sx={{ fontWeight: 700, color: "#64748b", mb: 0.5, display: "block" }}>
                Highlights:
              </Typography>
              {fact.highlights.slice(0, 2).map((highlight, idx) => (
                <Typography key={idx} variant="caption" sx={{ display: "block", color: "#475569", mb: 0.5, fontStyle: "italic" }}>
                  "{highlight}"
                </Typography>
              ))}
            </Box>
          )}

          {shouldTruncate && (
            <IconButton
              size="small"
              onClick={(e) => {
                e.stopPropagation();
                setExpanded(!expanded);
              }}
              sx={{
                p: 0.25,
                mt: 0.25,
                color: "#4f46e5",
                "&:hover": { background: alpha("#4f46e5", 0.1) },
              }}
            >
              {expanded ? (
                <ExpandLessIcon fontSize="small" />
              ) : (
                <ExpandMoreIcon fontSize="small" />
              )}
            </IconButton>
          )}
        </Box>

        <Divider sx={{ borderColor: "rgba(0,0,0,0.06)", my: 0.5 }} />

        {/* Source and Actions */}
        <Stack direction="row" spacing={0.75} alignItems="center" justifyContent="space-between">
          <Stack direction="row" spacing={0.5} alignItems="center" flex={1} minWidth={0}>
            <OpenInNewIcon fontSize="small" sx={{ color: "rgba(15,23,42,0.5)", flexShrink: 0 }} />
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
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
                fontSize: "0.7rem",
              }}
            >
              {hostname || "source"}
            </Typography>
          </Stack>
          <Tooltip title="Copy citation">
            <IconButton 
              size="small" 
              onClick={(e) => {
                e.stopPropagation();
                handleCopy();
              }} 
              sx={{ 
                color: "rgba(15,23,42,0.6)",
                p: 0.5,
                "&:hover": { background: alpha("#4f46e5", 0.1) },
              }}
            >
              <ContentCopyIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Stack>

        {/* Confidence and Date */}
        <Stack direction="row" spacing={1} alignItems="center" justifyContent="space-between">
          <Chip
            label={`${(fact.confidence * 100).toFixed(0)}%`}
            size="small"
            sx={{
              height: 18,
              fontSize: "0.65rem",
              background: alpha("#22c55e", 0.15),
              color: "#15803d",
              border: "1px solid rgba(34,197,94,0.35)",
              fontWeight: 600,
            }}
          />
          <Typography variant="caption" sx={{ color: "#64748b", fontSize: "0.7rem" }}>
            {fact.date !== "Unknown" ? new Date(fact.date).toLocaleDateString("en-US", { month: "short", year: "numeric" }) : fact.date}
          </Typography>
        </Stack>
      </Stack>
    </GlassyCard>
  );
};

