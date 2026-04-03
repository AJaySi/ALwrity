import React from "react";
import { Stack, Box, Typography, Chip, TextField, IconButton, Paper, Divider } from "@mui/material";
import { Groups as GroupsIcon, Insights as InsightsIcon, Search as SearchIcon, EditNote as EditNoteIcon, Add as AddIcon } from "@mui/icons-material";
import { PodcastAnalysis } from "../../types";
import { AnalysisTabContent } from "../AnalysisTabNav";

interface AudienceTabProps {
  analysis: PodcastAnalysis;
  isEditing?: boolean;
  editedAnalysis?: PodcastAnalysis | null;
  setEditedAnalysis?: (analysis: PodcastAnalysis) => void;
  handleRemoveKeyword?: (keyword: string) => void;
  handleAddKeyword?: (keyword: string) => void;
  handleRemoveTitle?: (title: string) => void;
  handleAddTitle?: (title: string) => void;
  handleUpdateOutline?: (id: string | number, field: 'title' | 'segments', value: any) => void;
  updateExaConfig?: (field: string, value: any) => void;
}

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

export const AudienceTab: React.FC<AudienceTabProps> = ({ 
  analysis, 
  isEditing, 
  editedAnalysis, 
  setEditedAnalysis,
  handleRemoveKeyword,
  handleAddKeyword,
  handleRemoveTitle,
  handleAddTitle,
  handleUpdateOutline,
  updateExaConfig
}) => {
  const currentAnalysis = editedAnalysis || analysis;

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
              value={currentAnalysis.audience}
              onChange={(e) => setEditedAnalysis?.({ ...currentAnalysis, audience: e.target.value })}
              placeholder="Describe your target audience..."
              sx={inputStyles}
            />
          ) : (
            <Typography variant="body2" sx={{ color: "#0f172a" }}>
              {currentAnalysis.audience}
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
              value={currentAnalysis.contentType}
              onChange={(e) => setEditedAnalysis?.({ ...currentAnalysis, contentType: e.target.value })}
              placeholder="e.g. Interview, Narrative, Solo..."
              sx={inputStyles}
            />
          ) : (
            <Chip label={currentAnalysis.contentType} size="small" sx={{ background: "#eef2ff", color: "#4f46e5", border: "1px solid rgba(79,70,229,0.2)" }} />
          )}
        </Box>

        <Box>
          <Typography variant="caption" sx={{ color: "#64748b", fontWeight: 600, display: "block", mb: 1 }}>
            Top Keywords
          </Typography>
          <Stack direction="row" flexWrap="wrap" useFlexGap sx={{ mb: isEditing ? 1.5 : 0 }}>
            {currentAnalysis.topKeywords.map((k: string) => (
              <Chip
                key={k}
                label={k}
                size="small"
                variant="outlined"
                onDelete={isEditing ? () => handleRemoveKeyword?.(k) : undefined}
                sx={{
                  borderColor: "rgba(0,0,0,0.1)",
                  color: "#0f172a",
                  background: "#f8fafc",
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
                  handleAddKeyword?.((e.target as HTMLInputElement).value);
                  (e.target as HTMLInputElement).value = '';
                }
              }}
              InputProps={{
                endAdornment: (
                  <IconButton size="small" onClick={(e) => {
                    const input = (e.currentTarget.parentElement?.parentElement?.querySelector('input') as HTMLInputElement);
                    handleAddKeyword?.(input.value);
                    input.value = '';
                  }}>
                    <AddIcon fontSize="small" sx={{ color: '#4f46e5' }} />
                  </IconButton>
                )
              }}
            />
          )}
        </Box>

        {currentAnalysis.exaSuggestedConfig && (
          <Box>
            <Divider sx={{ mb: 2 }} />
            <Typography variant="subtitle2" sx={{ mb: 1, color: "#0f172a", display: "flex", alignItems: "center", gap: 0.5 }}>
              <SearchIcon fontSize="small" sx={{ color: "#4f46e5" }} />
              Exa Research Config
            </Typography>
            <Stack direction="row" flexWrap="wrap" useFlexGap>
              {currentAnalysis.exaSuggestedConfig.exa_search_type && (
                <Chip label={`Search: ${currentAnalysis.exaSuggestedConfig.exa_search_type}`} size="small" sx={{ background: "#eef2ff", color: "#0f172a" }} />
              )}
              {currentAnalysis.exaSuggestedConfig.exa_category && (
                <Chip label={`Category: ${currentAnalysis.exaSuggestedConfig.exa_category}`} size="small" sx={{ background: "#eef2ff", color: "#0f172a" }} />
              )}
              {currentAnalysis.exaSuggestedConfig.date_range && (
                <Chip label={`Date: ${currentAnalysis.exaSuggestedConfig.date_range}`} size="small" sx={{ background: "#eef2ff", color: "#0f172a" }} />
              )}
              {currentAnalysis.exaSuggestedConfig.max_sources && (
                <Chip label={`Max: ${currentAnalysis.exaSuggestedConfig.max_sources}`} size="small" sx={{ background: "#eef2ff", color: "#0f172a" }} />
              )}
            </Stack>
          </Box>
        )}

        <Box>
          <Typography variant="caption" sx={{ color: "#64748b", fontWeight: 600, display: "block", mb: 1 }}>
            Title Suggestions
          </Typography>
          <Stack direction="row" flexWrap="wrap" useFlexGap sx={{ mb: isEditing ? 1.5 : 0 }}>
            {currentAnalysis.titleSuggestions.map((t: string) => (
              <Chip
                key={t}
                label={t}
                size="small"
                onDelete={isEditing ? () => handleRemoveTitle?.(t) : undefined}
                sx={{
                  color: "#0f172a",
                  background: "#f8fafc",
                  maxWidth: "100%",
                  whiteSpace: "normal",
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
                  handleAddTitle?.((e.target as HTMLInputElement).value);
                  (e.target as HTMLInputElement).value = '';
                }
              }}
              InputProps={{
                endAdornment: (
                  <IconButton size="small" onClick={(e) => {
                    const input = (e.currentTarget.parentElement?.parentElement?.querySelector('input') as HTMLInputElement);
                    handleAddTitle?.(input.value);
                    input.value = '';
                  }}>
                    <AddIcon fontSize="small" sx={{ color: '#4f46e5' }} />
                  </IconButton>
                )
              }}
            />
          )}
        </Box>
      </Stack>
    </AnalysisTabContent>
  );
};
