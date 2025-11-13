import React from 'react';
import { Grid, Typography, Box, FormControlLabel, Checkbox } from '@mui/material';
import { SectionProps } from './types';

export const FeatureCheckboxesSection: React.FC<SectionProps> = ({ state }) => {
  return (
    <Grid item xs={12}>
      <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
        Story Features
      </Typography>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
        <FormControlLabel
          control={
            <Checkbox
              checked={state.enableExplainer}
              onChange={(e) => state.setEnableExplainer(e.target.checked)}
            />
          }
          label="Explainer"
        />
        <FormControlLabel
          control={
            <Checkbox
              checked={state.enableIllustration}
              onChange={(e) => state.setEnableIllustration(e.target.checked)}
            />
          }
          label="Illustration"
        />
        <FormControlLabel
          control={
            <Checkbox
              checked={state.enableVideoNarration}
              onChange={(e) => state.setEnableVideoNarration(e.target.checked)}
            />
          }
          label="Story Video & Narration"
        />
      </Box>
    </Grid>
  );
};

