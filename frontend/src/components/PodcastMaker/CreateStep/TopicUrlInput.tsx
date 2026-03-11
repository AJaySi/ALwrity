import React from "react";
import { Box, Typography, TextField, Tooltip, Button, CircularProgress, alpha } from "@mui/material";
import { AutoAwesome as AutoAwesomeIcon } from "@mui/icons-material";

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
}) => {
  return (
    <Box
      sx={{
        p: 3,
        borderRadius: 2,
        background: alpha("#f8fafc", 0.5),
        border: "1px solid rgba(15, 23, 42, 0.06)",
        height: "100%", // Fill height of parent
        display: "flex",
        flexDirection: "column",
      }}
    >
      <Box flex={1} display="flex" flexDirection="column">
        <Typography variant="subtitle2" sx={{ mb: 1.5, color: "#0f172a", fontWeight: 600, fontSize: "0.9375rem" }}>
          Topic Idea or Blog URL
        </Typography>
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
                color: "#0f172a",
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
                backgroundColor: "#ffffff",
                border: "1.5px solid rgba(15, 23, 42, 0.12)",
                borderRadius: 2,
                "&:hover": {
                  backgroundColor: "#ffffff",
                  borderColor: "rgba(102, 126, 234, 0.4)",
                },
                "&.Mui-focused": {
                  backgroundColor: "#ffffff",
                  borderColor: isUrl ? "#10b981" : "#667eea", // Green for URL, Blue for Topic
                  borderWidth: 2,
                },
              },
              "& .MuiOutlinedInput-input": {
                fontSize: "0.9375rem",
                lineHeight: 1.6,
                color: "#0f172a",
                fontWeight: 400,
              },
              "& .MuiInputBase-input::placeholder": {
                color: "#94a3b8",
                opacity: 1,
                fontWeight: 400,
              },
              "& .MuiFormHelperText-root": {
                color: isUrl ? "#059669" : "#64748b",
                fontSize: "0.8125rem",
                fontWeight: 400,
                mt: 0.75,
              },
            }}
          />
        </Tooltip>
        
        {/* Enhance topic with AI button - appears when user types (and not a URL) */}
        {showAIDetailsButton && !isUrl && (
          <Box sx={{ display: "flex", justifyContent: "flex-end", mt: 1, flexDirection: "column", alignItems: "flex-end", gap: 0.6 }}>
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
                px: 1.8,
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
