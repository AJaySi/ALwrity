import React from "react";
import { Box, Typography, TextField, Tooltip, Button, CircularProgress, alpha, Stack, Chip } from "@mui/material";
import { AutoAwesome as AutoAwesomeIcon, AttachMoney as AttachMoneyIcon } from "@mui/icons-material";
import { Knobs } from "../types";

export const TOPIC_PLACEHOLDERS = [
  "Industry insights: Latest trends in AI for Content Marketing",
  "Product deep-dive: How our new feature solves common pain points",
  "Educational: 5 ways to improve your workflow with automation",
  "Thought leadership: The future of decentralized finance (DeFi)",
  "Interview prep: Key questions for your next tech hiring round",
  "Podcast prep: Analyzing the impact of remote work on mental health",
];

interface TopicUrlInputProps {
  value: string;
  onChange: (value: string) => void;
  isUrl: boolean;
  showAIDetailsButton: boolean;
  onAIDetailsClick?: () => void;
  placeholderIndex: number;
  loading?: boolean;
  loadingMessage?: string;
  estimatedCost?: {
    ttsCost: number;
    avatarCost: number;
    videoCost: number;
    researchCost: number;
    total: number;
  };
  duration?: number;
  speakers?: number;
  knobs?: Knobs;
}

export const TopicUrlInput: React.FC<TopicUrlInputProps> = ({
  value,
  onChange,
  isUrl,
  showAIDetailsButton,
  onAIDetailsClick,
  placeholderIndex,
  loading = false,
  loadingMessage,
  estimatedCost,
  duration = 1,
  speakers = 1,
  knobs,
}) => {
  return (
    <Box
      sx={{
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
      <Box flex={1} display="flex" flexDirection="column">
        <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 2 }}>
          <Stack direction="row" alignItems="center" spacing={1}>
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
              <Typography sx={{ color: "#fff", fontSize: "0.75rem", fontWeight: 700 }}>1</Typography>
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
              <AutoAwesomeIcon sx={{ color: "#667eea", fontSize: "1rem" }} />
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
              Enter Podcast Topic or Blog URL
            </Typography>
          </Stack>
          
          {estimatedCost && (
            <Tooltip
              title={
                <Box>
                  <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                    Estimated Cost Breakdown:
                  </Typography>
                  <Typography variant="body2" component="div" sx={{ fontSize: "0.875rem", lineHeight: 1.6 }}>
                    • Audio Generation: ${estimatedCost.ttsCost}<br />
                    • Avatar Creation: ${estimatedCost.avatarCost}<br />
                    • Video Rendering: ${estimatedCost.videoCost}<br />
                    • Research: ${estimatedCost.researchCost}<br />
                    <Typography variant="body2" sx={{ fontWeight: 600, mt: 0.5, pt: 0.5, borderTop: "1px solid rgba(255,255,255,0.2)" }}>
                      Total: ${estimatedCost.total}
                    </Typography>
                    <Typography variant="caption" sx={{ fontSize: "0.75rem", opacity: 0.9, mt: 0.5, display: "block" }}>
                      Based on {duration} min, {speakers} speaker{speakers > 1 ? "s" : ""}, {knobs?.bitrate === "hd" ? "HD" : "standard"} quality
                    </Typography>
                  </Typography>
                </Box>
              }
              arrow
              placement="top"
              componentsProps={{
                tooltip: {
                  sx: {
                    bgcolor: "#0f172a",
                    color: "#ffffff",
                    maxWidth: 280,
                    fontSize: "0.875rem",
                    p: 1.5,
                    boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
                  },
                },
                arrow: {
                  sx: {
                    color: "#0f172a",
                  },
                },
              }}
            >
              <Chip 
                icon={<AttachMoneyIcon sx={{ fontSize: "0.875rem !important" }} />}
                label={`Est. $${estimatedCost.total}`} 
                size="small"
                sx={{
                  background: "linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(5, 150, 105, 0.12) 100%)",
                  color: "#059669",
                  fontWeight: 600,
                  border: "1px solid rgba(16, 185, 129, 0.2)",
                  fontSize: "0.75rem",
                  height: 26,
                  cursor: "help",
                }}
              />
            </Tooltip>
          )}
        </Stack>
        <Tooltip
          title={
            isUrl
              ? "We detected a URL. We'll fetch insights from this page."
              : "Enter a concise idea or paste a blog URL."
          }
          arrow
          placement="top"
        >
          <TextField
            fullWidth
            multiline
            rows={5}
            placeholder={!value ? `e.g., "${TOPIC_PLACEHOLDERS[placeholderIndex]}" or paste a URL` : ""}
            inputProps={{
              sx: {
                "&::placeholder": { color: "#94a3b8", opacity: 1 },
                color: "#1e293b",
              },
            }}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            size="small"
            helperText={
              isUrl
                ? "URL detected. We'll analyze this page content."
                : "Enter a clear, concise topic. We'll expand it into a full script after you click Analyze."
            }
            sx={{
              "& .MuiOutlinedInput-root": {
                backgroundColor: "#f8fafc",
                border: "2px solid rgba(102, 126, 234, 0.2)",
                borderRadius: 2,
                fontSize: "1rem",
                transition: "all 0.2s ease",
                "&:hover": {
                  backgroundColor: "#ffffff",
                  borderColor: "rgba(102, 126, 234, 0.4)",
                  boxShadow: "0 2px 8px rgba(102, 126, 234, 0.1)",
                },
                "&.Mui-focused": {
                  backgroundColor: "#ffffff",
                  borderColor: isUrl ? "#10b981" : "#667eea",
                  borderWidth: 2,
                  boxShadow: isUrl 
                    ? "0 0 0 4px rgba(16, 185, 129, 0.1)" 
                    : "0 0 0 4px rgba(102, 126, 234, 0.1)",
                },
              },
              "& .MuiOutlinedInput-input": {
                fontSize: "1rem",
                lineHeight: 1.7,
                color: "#1e293b",
                fontWeight: 500,
                "&::placeholder": {
                  color: "#64748b",
                  opacity: 1,
                  fontWeight: 400,
                },
              },
              "& .MuiFormHelperText-root": {
                color: isUrl ? "#059669" : "#64748b",
                fontSize: "0.8125rem",
                fontWeight: 500,
                mt: 1,
              },
            }}
          />
        </Tooltip>
        
        {/* Enhance topic with AI button - appears when user types (and not a URL) */}
        {showAIDetailsButton && !isUrl && (
          <Box sx={{ display: "flex", justifyContent: "flex-end", mt: 1.5, flexDirection: "column", alignItems: "flex-end", gap: 0.6 }}>
            <Button
              size="small"
              variant="contained"
              startIcon={
                loading ? (
                  <CircularProgress size={14} thickness={5} sx={{ color: "rgba(255,255,255,0.92)" }} />
                ) : (
                  <AutoAwesomeIcon />
                )
              }
              onClick={onAIDetailsClick}
              disabled={loading}
              sx={{
                textTransform: "none",
                fontSize: "0.875rem",
                fontWeight: 600,
                borderRadius: 2.5,
                color: "#f8fbff",
                px: 2,
                py: 0.75,
                border: "1px solid rgba(148, 211, 255, 0.6)",
                background: "linear-gradient(120deg, #0ea5e9 0%, #2563eb 55%, #1d4ed8 100%)",
                boxShadow: "0 8px 18px rgba(37, 99, 235, 0.28), inset 0 1px 0 rgba(255,255,255,0.22)",
                "&:hover": {
                  background: "linear-gradient(120deg, #38bdf8 0%, #2563eb 50%, #1e40af 100%)",
                  boxShadow: "0 12px 24px rgba(29, 78, 216, 0.35), inset 0 1px 0 rgba(255,255,255,0.26)",
                  transform: "translateY(-1px)",
                },
                "&.Mui-disabled": {
                  color: "#e2e8f0",
                  borderColor: "rgba(186, 230, 253, 0.7)",
                  background: "linear-gradient(120deg, #0ea5e9 0%, #2563eb 55%, #1d4ed8 100%)",
                  opacity: 0.78,
                },
              }}
            >
              {loading ? "Enhancing Topic With AI..." : "Enhance Topic With AI"}
            </Button>
            {loading && (
              <Typography sx={{ fontSize: "0.75rem", color: "#1d4ed8", fontWeight: 600 }}>
                {loadingMessage || "Analyzing your topic and improving clarity..."}
              </Typography>
            )}
          </Box>
        )}
      </Box>
    </Box>
  );
};
