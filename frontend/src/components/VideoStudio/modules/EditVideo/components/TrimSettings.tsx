import React from 'react';
import { Box, Typography, Paper, Slider, TextField, Stack, ToggleButton, ToggleButtonGroup } from '@mui/material';
import ContentCutIcon from '@mui/icons-material/ContentCut';
import type { TrimMode } from '../hooks/useEditVideo';

interface TrimSettingsProps {
  videoDuration: number;
  startTime: number;
  endTime: number;
  maxDuration: number | null;
  trimMode: TrimMode;
  onStartTimeChange: (value: number) => void;
  onEndTimeChange: (value: number) => void;
  onMaxDurationChange: (value: number | null) => void;
  onTrimModeChange: (value: TrimMode) => void;
}

export const TrimSettings: React.FC<TrimSettingsProps> = ({
  videoDuration,
  startTime,
  endTime,
  maxDuration,
  trimMode,
  onStartTimeChange,
  onEndTimeChange,
  onMaxDurationChange,
  onTrimModeChange,
}) => {
  const handleRangeChange = (_event: Event, value: number | number[]) => {
    if (Array.isArray(value)) {
      onStartTimeChange(value[0]);
      onEndTimeChange(value[1]);
    }
  };

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
        <ContentCutIcon sx={{ color: '#3b82f6' }} />
        <Typography
          variant="subtitle2"
          sx={{
            color: '#0f172a',
            fontWeight: 700,
          }}
        >
          Trim Settings
        </Typography>
      </Stack>

      <Stack spacing={3}>
        {/* Time Range Slider */}
        <Box>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Select time range: {startTime.toFixed(1)}s - {endTime.toFixed(1)}s ({(endTime - startTime).toFixed(1)}s)
          </Typography>
          <Slider
            value={[startTime, endTime]}
            onChange={handleRangeChange}
            min={0}
            max={videoDuration}
            step={0.1}
            valueLabelDisplay="auto"
            valueLabelFormat={(value) => `${value.toFixed(1)}s`}
            sx={{
              color: '#3b82f6',
              '& .MuiSlider-thumb': {
                width: 16,
                height: 16,
              },
            }}
          />
        </Box>

        {/* Manual Time Input */}
        <Stack direction="row" spacing={2}>
          <TextField
            label="Start (s)"
            type="number"
            size="small"
            value={startTime}
            onChange={(e) => onStartTimeChange(parseFloat(e.target.value) || 0)}
            inputProps={{
              min: 0,
              max: endTime - 0.1,
              step: 0.1,
            }}
            sx={{ flex: 1 }}
          />
          <TextField
            label="End (s)"
            type="number"
            size="small"
            value={endTime}
            onChange={(e) => onEndTimeChange(parseFloat(e.target.value) || videoDuration)}
            inputProps={{
              min: startTime + 0.1,
              max: videoDuration,
              step: 0.1,
            }}
            sx={{ flex: 1 }}
          />
        </Stack>

        {/* Max Duration Mode */}
        <Box>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Or set max duration (optional):
          </Typography>
          <Stack direction="row" spacing={2} alignItems="center">
            <TextField
              label="Max Duration (s)"
              type="number"
              size="small"
              value={maxDuration ?? ''}
              onChange={(e) => {
                const val = e.target.value;
                onMaxDurationChange(val ? parseFloat(val) : null);
              }}
              inputProps={{
                min: 1,
                max: videoDuration,
                step: 0.1,
              }}
              sx={{ width: 150 }}
            />
            {maxDuration !== null && (
              <ToggleButtonGroup
                value={trimMode}
                exclusive
                onChange={(_, value) => value && onTrimModeChange(value)}
                size="small"
              >
                <ToggleButton value="beginning" sx={{ px: 2 }}>
                  Beginning
                </ToggleButton>
                <ToggleButton value="middle" sx={{ px: 2 }}>
                  Middle
                </ToggleButton>
                <ToggleButton value="end" sx={{ px: 2 }}>
                  End
                </ToggleButton>
              </ToggleButtonGroup>
            )}
          </Stack>
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            {maxDuration !== null
              ? `Will keep the ${trimMode} ${maxDuration}s of the video`
              : 'Leave empty to use start/end times'}
          </Typography>
        </Box>
      </Stack>
    </Paper>
  );
};
