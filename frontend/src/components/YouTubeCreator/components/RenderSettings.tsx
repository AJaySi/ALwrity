/**
 * Render Settings Component
 * 
 * Configuration panel for video resolution and scene combination options.
 */

import React from 'react';
import {
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Box,
  Typography,
} from '@mui/material';
import { YT_BORDER, RESOLUTIONS, type Resolution } from '../constants';

interface RenderSettingsProps {
  resolution: Resolution;
  combineScenes: boolean;
  enabledScenesCount: number;
  onResolutionChange: (resolution: Resolution) => void;
  onCombineScenesChange: (combine: boolean) => void;
}

export const RenderSettings: React.FC<RenderSettingsProps> = React.memo(({
  resolution,
  combineScenes,
  enabledScenesCount,
  onResolutionChange,
  onCombineScenesChange,
}) => {
  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <FormControl fullWidth>
          <InputLabel>Video Resolution</InputLabel>
          <Select
            value={resolution}
            label="Video Resolution"
            onChange={(e) => onResolutionChange(e.target.value as Resolution)}
          >
            {RESOLUTIONS.map((res) => (
              <MenuItem key={res} value={res}>
                {res === '480p' && '480p (Lower cost, faster)'}
                {res === '720p' && '720p (Recommended)'}
                {res === '1080p' && '1080p (Highest quality)'}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>
      <Grid item xs={12} md={6}>
        <FormControlLabel
          control={
            <Switch
              checked={combineScenes}
              onChange={(e) => onCombineScenesChange(e.target.checked)}
            />
          }
          label="Combine scenes into single video"
        />
      </Grid>
    </Grid>
  );
});

RenderSettings.displayName = 'RenderSettings';

