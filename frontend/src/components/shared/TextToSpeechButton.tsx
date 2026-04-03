import React from 'react';
import { IconButton, Tooltip, CircularProgress, Box, Menu, MenuItem, ListItemIcon, ListItemText, FormControl, Select, Slider, Typography } from '@mui/material';
import { VolumeUp as VolumeUpIcon, Stop as StopIcon, PlayArrow as PlayArrowIcon, Settings as SettingsIcon } from '@mui/icons-material';
import { useTextToSpeech, SpeechSynthesisOptions } from '../../hooks/useTextToSpeech';

interface TextToSpeechButtonProps {
  text: string;
  textToSpeak?: string; // Optional different text to speak (e.g., shorter version)
  options?: SpeechSynthesisOptions;
  size?: 'small' | 'medium' | 'large';
  showSettings?: boolean;
  disabled?: boolean;
}

export const TextToSpeechButton: React.FC<TextToSpeechButtonProps> = ({
  text,
  textToSpeak,
  options,
  size = 'medium',
  showSettings = false,
  disabled = false,
}) => {
  const { speak, stop, isSpeaking, isSupported, voices, pause, resume, isPaused } = useTextToSpeech();
  
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const [selectedVoice, setSelectedVoice] = React.useState<SpeechSynthesisVoice | null>(null);
  const [rate, setRate] = React.useState(1);
  const [pitch, setPitch] = React.useState(1);
  const [volume, setVolume] = React.useState(1);

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    if (showSettings) {
      setAnchorEl(event.currentTarget);
    }
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleSpeak = () => {
    const textToUse = textToSpeak || text;
    if (!textToUse.trim()) return;
    
    if (isSpeaking) {
      stop();
    } else {
      speak(textToUse, {
        voice: selectedVoice || undefined,
        rate,
        pitch,
        volume,
        ...options,
      });
    }
  };

  if (!isSupported) {
    return null;
  }

  const iconSize = size === 'small' ? 18 : size === 'medium' ? 24 : 30;
  const buttonSize = size === 'small' ? 'small' : size === 'medium' ? 'medium' : 'large';

  return (
    <Box sx={{ display: 'inline-flex', alignItems: 'center' }}>
      <Tooltip title={isSpeaking ? "Stop" : "Read aloud"}>
        <IconButton
          onClick={handleSpeak}
          size={buttonSize}
          disabled={disabled || !text.trim()}
          sx={{
            color: isSpeaking ? '#ef4444' : '#667eea',
            backgroundColor: isSpeaking ? 'rgba(239, 68, 68, 0.1)' : 'rgba(102, 126, 234, 0.1)',
            '&:hover': {
              backgroundColor: isSpeaking ? 'rgba(239, 68, 68, 0.2)' : 'rgba(102, 126, 234, 0.2)',
            },
          }}
        >
          {isSpeaking ? <StopIcon sx={{ fontSize: iconSize }} /> : <VolumeUpIcon sx={{ fontSize: iconSize }} />}
        </IconButton>
      </Tooltip>

      {showSettings && (
        <>
          <Tooltip title="Voice settings">
            <IconButton
              onClick={handleClick}
              size={buttonSize}
              sx={{ ml: 0.5, color: 'rgba(0,0,0,0.5)' }}
            >
              <SettingsIcon sx={{ fontSize: iconSize * 0.75 }} />
            </IconButton>
          </Tooltip>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleClose}
            PaperProps={{ sx: { p: 2, minWidth: 280 } }}
          >
            <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
              Voice Settings
            </Typography>

            {/* Voice Selection */}
            <FormControl fullWidth size="small" sx={{ mb: 2 }}>
              <Typography variant="caption" sx={{ mb: 0.5, display: 'block' }}>Voice</Typography>
              <Select
                value={selectedVoice?.name || ''}
                onChange={(e) => {
                  const voice = voices.find(v => v.name === e.target.value);
                  setSelectedVoice(voice || null);
                }}
                displayEmpty
              >
                <MenuItem value="">
                  <em>Default</em>
                </MenuItem>
                {voices.map((voice) => (
                  <MenuItem key={voice.name} value={voice.name}>
                    {voice.name.split(' ')[0]}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {/* Speed */}
            <Typography variant="caption">Speed: {rate}x</Typography>
            <Slider
              value={rate}
              min={0.5}
              max={2}
              step={0.1}
              onChange={(_, value) => setRate(value as number)}
              size="small"
              sx={{ mb: 2 }}
            />

            {/* Pitch */}
            <Typography variant="caption">Pitch: {pitch}</Typography>
            <Slider
              value={pitch}
              min={0.5}
              max={2}
              step={0.1}
              onChange={(_, value) => setPitch(value as number)}
              size="small"
              sx={{ mb: 2 }}
            />

            {/* Volume */}
            <Typography variant="caption">Volume: {Math.round(volume * 100)}%</Typography>
            <Slider
              value={volume}
              min={0}
              max={1}
              step={0.1}
              onChange={(_, value) => setVolume(value as number)}
              size="small"
            />
          </Menu>
        </>
      )}
    </Box>
  );
};

export default TextToSpeechButton;
