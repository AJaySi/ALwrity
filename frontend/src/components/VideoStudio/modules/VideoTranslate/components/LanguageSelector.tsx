import React from 'react';
import { Paper, Stack, Typography, Autocomplete, TextField } from '@mui/material';
import TranslateIcon from '@mui/icons-material/Translate';

interface LanguageSelectorProps {
  outputLanguage: string;
  supportedLanguages: string[];
  onLanguageChange: (language: string) => void;
}

export const LanguageSelector: React.FC<LanguageSelectorProps> = ({
  outputLanguage,
  supportedLanguages,
  onLanguageChange,
}) => {
  return (
    <Paper
      elevation={0}
      sx={{
        p: 3,
        borderRadius: 2,
        border: '1px solid #e2e8f0',
        backgroundColor: '#ffffff',
      }}
    >
      <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
        <TranslateIcon sx={{ color: '#3b82f6' }} />
        <Typography
          variant="subtitle2"
          sx={{
            color: '#0f172a',
            fontWeight: 700,
          }}
        >
          Target Language
        </Typography>
      </Stack>

      <Autocomplete
        value={outputLanguage}
        onChange={(event, newValue) => {
          if (newValue) {
            onLanguageChange(newValue);
          }
        }}
        options={supportedLanguages}
        renderInput={(params) => (
          <TextField
            {...params}
            label="Select Language"
            placeholder="Search for a language..."
            fullWidth
          />
        )}
        sx={{
          '& .MuiAutocomplete-input': {
            py: 1.5,
          },
        }}
      />

      <Typography
        variant="caption"
        color="text.secondary"
        sx={{ display: 'block', mt: 1.5 }}
      >
        Supports 70+ languages and 175+ dialects. The video will be translated with
        lip-sync preservation.
      </Typography>
    </Paper>
  );
};
