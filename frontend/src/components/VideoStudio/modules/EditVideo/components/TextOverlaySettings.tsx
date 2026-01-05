import React from 'react';
import { Box, Typography, Paper, TextField, Slider, Stack, Select, MenuItem, FormControl, InputLabel } from '@mui/material';
import TextFieldsIcon from '@mui/icons-material/TextFields';

interface TextOverlaySettingsProps {
  text: string;
  position: string;
  fontSize: number;
  fontColor: string;
  backgroundColor: string;
  startTime: number;
  endTime: number | null;
  videoDuration: number;
  onTextChange: (value: string) => void;
  onPositionChange: (value: string) => void;
  onFontSizeChange: (value: number) => void;
  onFontColorChange: (value: string) => void;
  onBackgroundColorChange: (value: string) => void;
  onStartTimeChange: (value: number) => void;
  onEndTimeChange: (value: number | null) => void;
}

const positions = [
  { value: 'top', label: 'Top Center' },
  { value: 'center', label: 'Center' },
  { value: 'bottom', label: 'Bottom Center' },
  { value: 'top-left', label: 'Top Left' },
  { value: 'top-right', label: 'Top Right' },
  { value: 'bottom-left', label: 'Bottom Left' },
  { value: 'bottom-right', label: 'Bottom Right' },
];

const colors = [
  { value: 'white', label: 'White' },
  { value: 'black', label: 'Black' },
  { value: 'yellow', label: 'Yellow' },
  { value: 'red', label: 'Red' },
  { value: 'blue', label: 'Blue' },
  { value: 'green', label: 'Green' },
];

export const TextOverlaySettings: React.FC<TextOverlaySettingsProps> = ({
  text,
  position,
  fontSize,
  fontColor,
  backgroundColor,
  startTime,
  endTime,
  videoDuration,
  onTextChange,
  onPositionChange,
  onFontSizeChange,
  onFontColorChange,
  onBackgroundColorChange,
  onStartTimeChange,
  onEndTimeChange,
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
        <TextFieldsIcon sx={{ color: '#3b82f6' }} />
        <Typography variant="subtitle2" sx={{ color: '#0f172a', fontWeight: 700 }}>
          Text Overlay Settings
        </Typography>
      </Stack>

      <Stack spacing={3}>
        {/* Text Input */}
        <TextField
          label="Text to Display"
          value={text}
          onChange={(e) => onTextChange(e.target.value)}
          multiline
          rows={2}
          fullWidth
          placeholder="Enter your text here..."
        />

        {/* Position */}
        <FormControl fullWidth size="small">
          <InputLabel>Position</InputLabel>
          <Select
            value={position}
            label="Position"
            onChange={(e) => onPositionChange(e.target.value)}
          >
            {positions.map((pos) => (
              <MenuItem key={pos.value} value={pos.value}>
                {pos.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {/* Font Size */}
        <Box>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Font Size: {fontSize}px
          </Typography>
          <Slider
            value={fontSize}
            onChange={(_, value) => onFontSizeChange(value as number)}
            min={12}
            max={120}
            step={4}
            marks={[
              { value: 24, label: '24' },
              { value: 48, label: '48' },
              { value: 72, label: '72' },
              { value: 96, label: '96' },
            ]}
            sx={{ color: '#3b82f6' }}
          />
        </Box>

        {/* Colors */}
        <Stack direction="row" spacing={2}>
          <FormControl fullWidth size="small">
            <InputLabel>Font Color</InputLabel>
            <Select
              value={fontColor}
              label="Font Color"
              onChange={(e) => onFontColorChange(e.target.value)}
            >
              {colors.map((color) => (
                <MenuItem key={color.value} value={color.value}>
                  <Stack direction="row" spacing={1} alignItems="center">
                    <Box
                      sx={{
                        width: 16,
                        height: 16,
                        borderRadius: 1,
                        backgroundColor: color.value,
                        border: '1px solid #e2e8f0',
                      }}
                    />
                    <span>{color.label}</span>
                  </Stack>
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl fullWidth size="small">
            <InputLabel>Background</InputLabel>
            <Select
              value={backgroundColor.split('@')[0]}
              label="Background"
              onChange={(e) => onBackgroundColorChange(`${e.target.value}@0.5`)}
            >
              {colors.map((color) => (
                <MenuItem key={color.value} value={color.value}>
                  <Stack direction="row" spacing={1} alignItems="center">
                    <Box
                      sx={{
                        width: 16,
                        height: 16,
                        borderRadius: 1,
                        backgroundColor: color.value,
                        border: '1px solid #e2e8f0',
                        opacity: 0.5,
                      }}
                    />
                    <span>{color.label}</span>
                  </Stack>
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Stack>

        {/* Time Range */}
        <Box>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Display Time: {startTime.toFixed(1)}s - {endTime !== null ? `${endTime.toFixed(1)}s` : 'end'}
          </Typography>
          <Slider
            value={[startTime, endTime ?? videoDuration]}
            onChange={(_, value) => {
              if (Array.isArray(value)) {
                onStartTimeChange(value[0]);
                onEndTimeChange(value[1] >= videoDuration ? null : value[1]);
              }
            }}
            min={0}
            max={videoDuration}
            step={0.1}
            valueLabelDisplay="auto"
            valueLabelFormat={(value) => `${value.toFixed(1)}s`}
            sx={{ color: '#3b82f6' }}
          />
        </Box>
      </Stack>
    </Paper>
  );
};
