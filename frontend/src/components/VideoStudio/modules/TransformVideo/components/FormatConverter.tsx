import React from 'react';
import { Box, Typography, FormControl, InputLabel, Select, MenuItem, Stack } from '@mui/material';
import type { OutputFormat, Quality } from '../hooks/useTransformVideo';

interface FormatConverterProps {
  outputFormat: OutputFormat;
  codec: string;
  quality: Quality;
  audioCodec: string;
  onOutputFormatChange: (format: OutputFormat) => void;
  onCodecChange: (codec: string) => void;
  onQualityChange: (quality: Quality) => void;
  onAudioCodecChange: (codec: string) => void;
}

export const FormatConverter: React.FC<FormatConverterProps> = ({
  outputFormat,
  codec,
  quality,
  audioCodec,
  onOutputFormatChange,
  onCodecChange,
  onQualityChange,
  onAudioCodecChange,
}) => {
  return (
    <Stack spacing={3}>
      <Typography
        variant="subtitle1"
        sx={{
          color: '#0f172a',
          fontWeight: 700,
        }}
      >
        Format Conversion Settings
      </Typography>

      <FormControl fullWidth>
        <InputLabel>Output Format</InputLabel>
        <Select
          value={outputFormat}
          label="Output Format"
          onChange={(e) => onOutputFormatChange(e.target.value as OutputFormat)}
        >
          <MenuItem value="mp4">MP4 (H.264)</MenuItem>
          <MenuItem value="mov">MOV (QuickTime)</MenuItem>
          <MenuItem value="webm">WebM (VP9)</MenuItem>
          <MenuItem value="gif">GIF (Animated)</MenuItem>
        </Select>
      </FormControl>

      {outputFormat !== 'gif' && (
        <>
          <FormControl fullWidth>
            <InputLabel>Video Codec</InputLabel>
            <Select
              value={codec}
              label="Video Codec"
              onChange={(e) => onCodecChange(e.target.value)}
              disabled={outputFormat === 'webm'} // Auto-selected for WebM
            >
              <MenuItem value="libx264">H.264 (MP4, MOV)</MenuItem>
              <MenuItem value="libvpx-vp9">VP9 (WebM)</MenuItem>
              <MenuItem value="libx265">H.265/HEVC</MenuItem>
            </Select>
          </FormControl>

          <FormControl fullWidth>
            <InputLabel>Audio Codec</InputLabel>
            <Select
              value={audioCodec}
              label="Audio Codec"
              onChange={(e) => onAudioCodecChange(e.target.value)}
              disabled={outputFormat === 'webm'} // Auto-selected for WebM
            >
              <MenuItem value="aac">AAC (MP4, MOV)</MenuItem>
              <MenuItem value="libopus">Opus (WebM)</MenuItem>
              <MenuItem value="mp3">MP3</MenuItem>
            </Select>
          </FormControl>
        </>
      )}

      {outputFormat !== 'gif' && (
        <FormControl fullWidth>
          <InputLabel>Quality</InputLabel>
          <Select
            value={quality}
            label="Quality"
            onChange={(e) => onQualityChange(e.target.value as Quality)}
          >
            <MenuItem value="high">High (Best Quality)</MenuItem>
            <MenuItem value="medium">Medium (Balanced)</MenuItem>
            <MenuItem value="low">Low (Smaller File)</MenuItem>
          </Select>
        </FormControl>
      )}

      {outputFormat === 'gif' && (
        <Box
          sx={{
            p: 2,
            borderRadius: 1,
            backgroundColor: '#f1f5f9',
            border: '1px solid #e2e8f0',
          }}
        >
          <Typography variant="body2" color="text.secondary">
            GIF format will be optimized for web with reduced frame rate (15fps) and no audio.
          </Typography>
        </Box>
      )}
    </Stack>
  );
};
