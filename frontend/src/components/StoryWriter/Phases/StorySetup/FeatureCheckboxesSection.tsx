import React from 'react';
import { Grid, Typography, Box, FormControlLabel, Checkbox } from '@mui/material';
import { SectionProps } from './types';

interface FeatureCheckboxesProps {
  state: SectionProps['state'];
  layout?: 'stack' | 'inline';
}

export const FeatureCheckboxesSection: React.FC<FeatureCheckboxesProps> = ({ state, layout = 'stack' }) => {
  const options = [
    {
      label: 'Explainer',
      checked: state.enableExplainer,
      onChange: (checked: boolean) => state.setEnableExplainer(checked),
    },
    {
      label: 'Illustration',
      checked: state.enableIllustration,
      onChange: (checked: boolean) => state.setEnableIllustration(checked),
    },
    {
      label: 'Narration',
      checked: state.enableNarration,
      onChange: (checked: boolean) => state.setEnableNarration(checked),
    },
    {
      label: 'Story Video',
      checked: state.enableVideoNarration,
      onChange: (checked: boolean) => state.setEnableVideoNarration(checked),
    },
  ];

  const renderCheckboxes = (direction: 'row' | 'column') => (
    <Box
      sx={{
        display: 'flex',
        flexWrap: direction === 'row' ? 'wrap' : 'nowrap',
        flexDirection: direction === 'row' ? 'row' : 'column',
        gap: 1.5,
      }}
    >
      {options.map((option) => (
        <FormControlLabel
          key={option.label}
          control={
            <Checkbox
              checked={option.checked}
              onChange={(e) => option.onChange(e.target.checked)}
              size="small"
            />
          }
          label={option.label}
          sx={{
            m: 0,
            '& .MuiFormControlLabel-label': {
              fontWeight: 600,
            },
          }}
        />
      ))}
    </Box>
  );

  if (layout === 'inline') {
    return renderCheckboxes('row');
  }

  return (
    <Grid item xs={12}>
      <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
        Story Features
      </Typography>
      {renderCheckboxes('column')}
    </Grid>
  );
};

