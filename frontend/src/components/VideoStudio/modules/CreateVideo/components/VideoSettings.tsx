import React from 'react';
import { Box, Stack, Typography, FormControl, InputLabel, Select, MenuItem, Slider } from '@mui/material';
import type { Resolution, AspectPreset, MotionPreset, Duration } from '../types';
import { motionPresets, aspectPresets, inputStyles } from '../constants';

interface VideoSettingsProps {
  resolution: Resolution;
  aspect: AspectPreset;
  motion: MotionPreset;
  duration: Duration;
  onResolutionChange: (value: Resolution) => void;
  onAspectChange: (value: AspectPreset) => void;
  onMotionChange: (value: MotionPreset) => void;
  onDurationChange: (value: Duration) => void;
}

export const VideoSettings: React.FC<VideoSettingsProps> = ({
  resolution,
  aspect,
  motion,
  duration,
  onResolutionChange,
  onAspectChange,
  onMotionChange,
  onDurationChange,
}) => {
  return (
    <>
      {/* Resolution, Aspect, Motion */}
      <Stack direction="row" spacing={2}>
        <FormControl fullWidth>
          <InputLabel sx={inputStyles.inputLabel}>Video Quality</InputLabel>
          <Select
            value={resolution}
            label="Video Quality"
            onChange={e => onResolutionChange(e.target.value as Resolution)}
            sx={{
              borderRadius: 2,
              backgroundColor: '#fff',
              '& fieldset': { borderColor: '#e2e8f0' },
            }}
          >
            <MenuItem value="480p">
              <Stack>
                <Typography variant="body2">480p - Fast & Affordable</Typography>
                <Typography variant="caption" color="text.secondary">
                  Perfect for quick social media tests
                </Typography>
              </Stack>
            </MenuItem>
            <MenuItem value="720p">
              <Stack>
                <Typography variant="body2">720p - Balanced</Typography>
                <Typography variant="caption" color="text.secondary">
                  Great for most platforms
                </Typography>
              </Stack>
            </MenuItem>
            <MenuItem value="1080p">
              <Stack>
                <Typography variant="body2">1080p - Premium</Typography>
                <Typography variant="caption" color="text.secondary">
                  Ideal for YouTube and professional content
                </Typography>
              </Stack>
            </MenuItem>
          </Select>
        </FormControl>

        <FormControl fullWidth>
          <InputLabel sx={inputStyles.inputLabel}>Video Format</InputLabel>
          <Select
            value={aspect}
            label="Video Format"
            onChange={e => onAspectChange(e.target.value as AspectPreset)}
            sx={{
              borderRadius: 2,
              backgroundColor: '#fff',
              '& fieldset': { borderColor: '#e2e8f0' },
            }}
          >
            <MenuItem value="9:16">
              <Stack>
                <Typography variant="body2">9:16 - Vertical</Typography>
                <Typography variant="caption" color="text.secondary">
                  Instagram Reels, TikTok, YouTube Shorts
                </Typography>
              </Stack>
            </MenuItem>
            <MenuItem value="1:1">
              <Stack>
                <Typography variant="body2">1:1 - Square</Typography>
                <Typography variant="caption" color="text.secondary">
                  Instagram posts, Facebook feed
                </Typography>
              </Stack>
            </MenuItem>
            <MenuItem value="16:9">
              <Stack>
                <Typography variant="body2">16:9 - Landscape</Typography>
                <Typography variant="caption" color="text.secondary">
                  YouTube, LinkedIn, landscape content
                </Typography>
              </Stack>
            </MenuItem>
          </Select>
        </FormControl>
      </Stack>

      <FormControl fullWidth>
        <InputLabel sx={inputStyles.inputLabel}>Movement Style</InputLabel>
        <Select
          value={motion}
          label="Movement Style"
          onChange={e => onMotionChange(e.target.value as MotionPreset)}
          sx={{
            borderRadius: 2,
            backgroundColor: '#fff',
            '& fieldset': { borderColor: '#e2e8f0' },
          }}
        >
          {motionPresets.map(preset => (
            <MenuItem key={preset} value={preset}>
              <Stack>
                <Typography variant="body2">{preset}</Typography>
                <Typography variant="caption" color="text.secondary">
                  {preset === 'Subtle'
                    ? 'Gentle movement, professional content'
                    : preset === 'Medium'
                    ? 'Balanced motion, most social media'
                    : 'Energetic movement, attention-grabbing'}
                </Typography>
              </Stack>
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      {/* Duration Slider */}
      <Box>
        <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: '#0f172a' }}>
          Duration: {duration} seconds
        </Typography>
        <Slider
          value={duration}
          min={5}
          max={10}
          step={3}
          marks={[
            { value: 5, label: '5s' },
            { value: 8, label: '8s' },
            { value: 10, label: '10s' },
          ]}
          onChange={(_, val) => onDurationChange(val as Duration)}
          sx={{
            color: '#667eea',
            '& .MuiSlider-markLabel': { color: '#475569' },
          }}
        />
        <Typography variant="caption" sx={{ color: '#475569', mt: 0.5 }}>
          Shorter videos cost less. Perfect for testing ideas before investing in longer content.
        </Typography>
      </Box>
    </>
  );
};
