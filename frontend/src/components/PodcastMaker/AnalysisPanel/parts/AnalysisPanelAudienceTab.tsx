import React from "react";
import { Stack, Box, Typography, Chip, TextField, Divider } from "@mui/material";
import { Groups as GroupsIcon, Search as SearchIcon } from "@mui/icons-material";
import { useAnalysisPanel } from "../AnalysisPanelContext";

const inputStyles = {
  '& .MuiInputBase-input': { color: '#111827 !important', fontWeight: 500 },
  '& .MuiInputLabel-root': { color: '#4b5563 !important' },
  '& .MuiOutlinedInput-root': {
    bgcolor: '#ffffff !important',
    '& fieldset': { borderColor: '#d1d5db !important' },
    '&:hover fieldset': { borderColor: '#4f46e5 !important' },
    '&.Mui-focused fieldset': { borderColor: '#4f46e5 !important' },
  },
};

const AnalysisTabContent: React.FC<{ title: string; icon?: React.ReactNode; children: React.ReactNode }> = ({ title, icon, children }) => (
  <Box sx={{ p: 2 }}>
    <Stack direction="row" spacing={1.5} alignItems="center" mb={2}>
      {icon && <Box sx={{ color: "#6366f1" }}>{icon}</Box>}
      <Typography variant="h6" sx={{ fontWeight: 600, color: "#0f172a" }}>
        {title}
      </Typography>
    </Stack>
    {children}
  </Box>
);

export const AnalysisPanelAudienceTab: React.FC = () => {
  const { currentAnalysis, isEditing, setEditedAnalysis, editedAnalysis, handleRemoveKeyword, handleAddKeyword, handleRemoveTitle, handleAddTitle } = useAnalysisPanel();

  if (!currentAnalysis) {
    return (
      <Box sx={{ p: 3, textAlign: "center" }}>
        <Typography variant="body1" sx={{ color: "#64748b" }}>
          No analysis data available. Please generate analysis first.
        </Typography>
      </Box>
    );
  }

  const analysis = currentAnalysis;

  const handleAudienceChange = (value: string) => {
    if (editedAnalysis) {
      setEditedAnalysis({ ...editedAnalysis, audience: value });
    }
  };

  const handleContentTypeChange = (value: string) => {
    if (editedAnalysis) {
      setEditedAnalysis({ ...editedAnalysis, contentType: value });
    }
  };

  return (
    <AnalysisTabContent title="Target Audience" icon={<GroupsIcon />}>
      <Stack spacing={3}>
        <Box>
          <Typography variant="caption" sx={{ color: "#64748b", fontWeight: 600, display: "block", mb: 0.5 }}>
            Audience Description
          </Typography>
          {isEditing ? (
            <TextField
              fullWidth
              multiline
              rows={2}
              size="small"
              value={analysis.audience || ""}
              onChange={(e) => handleAudienceChange(e.target.value)}
              placeholder="Describe your target audience..."
              sx={inputStyles}
            />
          ) : (
            <Typography variant="body2" sx={{ color: "#0f172a" }}>
              {analysis.audience}
            </Typography>
          )}
        </Box>

        <Box>
          <Typography variant="caption" sx={{ color: "#64748b", fontWeight: 600, display: "block", mb: 1 }}>
            Content Type
          </Typography>
          {isEditing ? (
            <TextField
              fullWidth
              size="small"
              value={analysis.contentType || ""}
              onChange={(e) => handleContentTypeChange(e.target.value)}
              placeholder="e.g. Interview, Narrative, Solo..."
              sx={inputStyles}
            />
          ) : (
            <Chip label={analysis.contentType} size="small" sx={{ background: "#eef2ff", color: "#4f46e5", border: "1px solid rgba(79,70,229,0.2)" }} />
          )}
        </Box>

        <Box>
          <Typography variant="caption" sx={{ color: "#64748b", fontWeight: 600, display: "block", mb: 1 }}>
            Top Keywords
          </Typography>
          <Stack direction="row" flexWrap="wrap" useFlexGap sx={{ mb: isEditing ? 1.5 : 0 }}>
            {analysis.topKeywords?.map((k: string) => (
              <Chip
                key={k}
                label={k}
                size="small"
                variant="outlined"
                onDelete={isEditing ? () => handleRemoveKeyword?.(k) : undefined}
                sx={{
                  borderColor: isEditing ? "#ef4444" : "rgba(0,0,0,0.15)",
                  color: isEditing ? "#dc2626" : "#0f172a",
                  background: isEditing ? "#fef2f2" : "#f8fafc",
                  fontWeight: 500,
                  "& .MuiChip-deleteIcon": {
                    color: "#ef4444",
                    "&:hover": {
                      color: "#dc2626",
                      backgroundColor: "#fee2e2",
                    },
                  },
                }}
              />
            ))}
          </Stack>
          {isEditing && (
            <TextField
              fullWidth
              size="small"
              placeholder="Add keyword and press Enter..."
              sx={inputStyles}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  const input = e.target as HTMLInputElement;
                  handleAddKeyword?.(input.value);
                  input.value = '';
                }
              }}
            />
          )}
        </Box>

        {analysis.exaSuggestedConfig && (
          <Box>
            <Divider sx={{ mb: 2 }} />
            <Typography variant="subtitle2" sx={{ mb: 1, color: "#0f172a", display: "flex", alignItems: "center", gap: 0.5 }}>
              <SearchIcon fontSize="small" sx={{ color: "#4f46e5" }} />
              Exa Research Config
            </Typography>
            <Stack direction="row" flexWrap="wrap" useFlexGap>
              {analysis.exaSuggestedConfig.exa_search_type && (
                <Chip label={`Search: ${analysis.exaSuggestedConfig.exa_search_type}`} size="small" sx={{ background: "#eef2ff", color: "#0f172a" }} />
              )}
              {analysis.exaSuggestedConfig.exa_category && (
                <Chip label={`Category: ${analysis.exaSuggestedConfig.exa_category}`} size="small" sx={{ background: "#eef2ff", color: "#0f172a" }} />
              )}
              {analysis.exaSuggestedConfig.date_range && (
                <Chip label={`Date: ${analysis.exaSuggestedConfig.date_range}`} size="small" sx={{ background: "#eef2ff", color: "#0f172a" }} />
              )}
              {analysis.exaSuggestedConfig.max_sources && (
                <Chip label={`Max: ${analysis.exaSuggestedConfig.max_sources}`} size="small" sx={{ background: "#eef2ff", color: "#0f172a" }} />
              )}
            </Stack>
          </Box>
        )}

        <Box>
          <Typography variant="caption" sx={{ color: "#64748b", fontWeight: 600, display: "block", mb: 1 }}>
            Title Suggestions
          </Typography>
          <Stack direction="row" flexWrap="wrap" useFlexGap sx={{ mb: isEditing ? 1.5 : 0 }}>
            {analysis.titleSuggestions?.map((t: string) => (
              <Chip
                key={t}
                label={t}
                size="small"
                onDelete={isEditing ? () => handleRemoveTitle?.(t) : undefined}
                sx={{
                  color: isEditing ? "#dc2626" : "#0f172a",
                  background: isEditing ? "#fef2f2" : "#f8fafc",
                  border: isEditing ? "1px solid #ef4444" : "1px solid #e2e8f0",
                  maxWidth: "100%",
                  whiteSpace: "normal",
                  fontWeight: 500,
                  "& .MuiChip-deleteIcon": {
                    color: "#ef4444",
                    "&:hover": {
                      color: "#dc2626",
                      backgroundColor: "#fee2e2",
                    },
                  },
                  height: "auto",
                }}
              />
            ))}
          </Stack>
          {isEditing && (
            <TextField
              fullWidth
              size="small"
              placeholder="Add title suggestion..."
              sx={inputStyles}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  const input = e.target as HTMLInputElement;
                  handleAddTitle?.(input.value);
                  input.value = '';
                }
              }}
            />
          )}
        </Box>
      </Stack>
    </AnalysisTabContent>
  );
};