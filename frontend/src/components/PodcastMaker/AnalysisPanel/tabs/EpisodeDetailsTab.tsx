import React from "react";
import { Stack, Box, Typography, Chip, TextField, IconButton, Paper, Divider } from "@mui/material";
import { EditNote as EditNoteIcon, Add as AddIcon, AutoAwesome as AutoAwesomeIcon, CallToAction as CTAIcon, Edit as EditIcon } from "@mui/icons-material";
import { PodcastAnalysis } from "../../types";
import { AnalysisTabContent } from "../AnalysisTabNav";

interface EpisodeDetailsTabProps {
  analysis: PodcastAnalysis;
  isEditing?: boolean;
  handleRemoveTitle?: (title: string) => void;
  handleAddTitle?: (title: string) => void;
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

export const EpisodeDetailsTab: React.FC<EpisodeDetailsTabProps> = ({ 
  analysis, 
  isEditing, 
  handleRemoveTitle, 
  handleAddTitle 
}) => {
  return (
    <AnalysisTabContent title="Episode Details" icon={<EditIcon />}>
      <Stack spacing={4}>
        {/* Titles Section */}
        <Box>
          <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1.5 }}>
            <EditNoteIcon sx={{ color: "#4f46e5", fontSize: 20 }} />
            <Typography variant="subtitle2" sx={{ color: "#1e293b", fontWeight: 700 }}>
              Episode Titles
            </Typography>
          </Stack>
          <Stack direction="row" flexWrap="wrap" useFlexGap sx={{ gap: 1 }}>
            {analysis.titleSuggestions?.map((title: string, idx: number) => (
              <Chip
                key={idx}
                label={title}
                size="small"
                onDelete={isEditing ? () => handleRemoveTitle?.(title) : undefined}
                sx={{
                  color: "#0f172a",
                  background: "linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)",
                  border: "1px solid #e2e8f0",
                  maxWidth: "100%",
                  whiteSpace: "normal",
                  height: "auto",
                  py: 0.5,
                  "&:hover": { background: "#e2e8f0" },
                }}
              />
            ))}
          </Stack>
          {isEditing && (
            <TextField
              fullWidth
              size="small"
              placeholder="Add title suggestion..."
              sx={{ ...inputStyles, mt: 2 }}
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

        <Divider sx={{ borderColor: "rgba(0,0,0,0.08)" }} />

        {/* Hook Section */}
        <Box>
          <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1.5 }}>
            <AutoAwesomeIcon sx={{ color: "#4f46e5", fontSize: 20 }} />
            <Typography variant="subtitle2" sx={{ color: "#1e293b", fontWeight: 700 }}>
              Episode Hook
            </Typography>
          </Stack>
          {analysis.episode_hook ? (
            <Paper elevation={0} sx={{ p: 2.5, bgcolor: "#f0f9ff", border: "1px solid rgba(59,130,246,0.2)", borderRadius: 2 }}>
              <Typography variant="body2" sx={{ color: "#0369a1", fontStyle: "italic", lineHeight: 1.6 }}>
                "{analysis.episode_hook}"
              </Typography>
            </Paper>
          ) : (
            <Typography variant="body2" sx={{ color: "#94a3b8", fontStyle: "italic" }}>
              No episode hook generated yet.
            </Typography>
          )}
          <Typography variant="caption" sx={{ color: "#94a3b8", mt: 1, display: "block" }}>
            A 15-30 second opening hook to grab listener attention.
          </Typography>
        </Box>

        <Divider sx={{ borderColor: "rgba(0,0,0,0.08)" }} />

        {/* CTA Section */}
        <Box>
          <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1.5 }}>
            <CTAIcon sx={{ color: "#4f46e5", fontSize: 20 }} />
            <Typography variant="subtitle2" sx={{ color: "#1e293b", fontWeight: 700 }}>
              Listener CTA
            </Typography>
          </Stack>
          {analysis.listener_cta ? (
            <Paper elevation={0} sx={{ p: 2.5, bgcolor: "#fff7ed", border: "1px solid rgba(249,115,22,0.2)", borderRadius: 2 }}>
              <Typography variant="body2" sx={{ color: "#c2410c", fontWeight: 500, lineHeight: 1.6 }}>
                {analysis.listener_cta}
              </Typography>
            </Paper>
          ) : (
            <Typography variant="body2" sx={{ color: "#94a3b8", fontStyle: "italic" }}>
              No listener call-to-action generated yet.
            </Typography>
          )}
          <Typography variant="caption" sx={{ color: "#94a3b8", mt: 1, display: "block" }}>
            A call-to-action for listeners after the episode.
          </Typography>
        </Box>
      </Stack>
    </AnalysisTabContent>
  );
};