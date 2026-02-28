import React from "react";
import { Box, Typography, TextField, Tooltip, Button, alpha } from "@mui/material";
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
}

export const TopicUrlInput: React.FC<TopicUrlInputProps> = ({
  value,
  onChange,
  isUrl,
  showAIDetailsButton,
  onAIDetailsClick,
  placeholderIndex,
  loading = false,
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
        
        {/* Add details with AI button - appears when user types (and not a URL) */}
        {showAIDetailsButton && !isUrl && (
          <Box sx={{ display: "flex", justifyContent: "flex-end", mt: 1 }}>
            <Button
              size="small"
              variant="outlined"
              startIcon={<AutoAwesomeIcon />}
              onClick={onAIDetailsClick}
              disabled={loading}
              sx={{
                textTransform: "none",
                fontSize: "0.875rem",
                fontWeight: 600,
                borderColor: "#667eea",
                borderWidth: 1.5,
                color: "#667eea",
                borderRadius: 2,
                "&:hover": {
                  borderColor: "#5568d3",
                  backgroundColor: alpha("#667eea", 0.08),
                },
              }}
            >
              {loading ? "Enhancing..." : "Add details with AI"}
            </Button>
          </Box>
        )}
      </Box>
    </Box>
  );
};
