import React from "react";
import { Stack, Box, Typography, Chip, TextField, IconButton } from "@mui/material";
import { EditNote as EditNoteIcon, Add as AddIcon } from "@mui/icons-material";
import { PodcastAnalysis } from "../../types";
import { AnalysisTabContent } from "../AnalysisTabNav";

interface TitlesTabProps {
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

export const TitlesTab: React.FC<TitlesTabProps> = ({ analysis, isEditing, handleRemoveTitle, handleAddTitle }) => {
  return (
    <AnalysisTabContent title="Episode Titles" icon={<EditNoteIcon />}>
      <Stack spacing={2}>
        <Stack direction="row" flexWrap="wrap" useFlexGap sx={{ mb: isEditing ? 1.5 : 0 }}>
          {analysis.titleSuggestions?.map((title: string, idx: number) => (
            <Chip
              key={idx}
              label={title}
              size="small"
              onDelete={isEditing ? () => handleRemoveTitle?.(title) : undefined}
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
      </Stack>
    </AnalysisTabContent>
  );
};
