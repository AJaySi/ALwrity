import React, { useEffect, useState } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stack,
  Box,
  Typography,
  Slider,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  FormControlLabel,
  Checkbox,
  Tooltip,
  IconButton,
  alpha,
  TextField,
} from "@mui/material";
import { HelpOutline as HelpOutlineIcon, Close as CloseIcon, VolumeUp } from "@mui/icons-material";
import { Button } from "@mui/material";

export type YouTubeAudioGenerationSettings = {
  voiceId: string;
  speed: number;
  volume: number;
  pitch: number;
  emotion: string;
  englishNormalization: boolean;
  sampleRate?: number;
  bitrate: number;
  channel: "1" | "2";
  format: "mp3" | "wav" | "pcm" | "flac";
  languageBoost?: string;
  enableSyncMode: boolean;
};

interface AudioSettingsModalProps {
  open: boolean;
  onClose: () => void;
  onApplySettings: (settings: YouTubeAudioGenerationSettings) => void;
  initialSettings: YouTubeAudioGenerationSettings;
  isGenerating?: boolean;
  sceneTitle?: string;
}

// Voice options from minimax/speech-02-hd
const VOICE_OPTIONS = [
  "Wise_Woman",
  "Friendly_Person",
  "Inspirational_girl",
  "Deep_Voice_Man",
  "Calm_Woman",
  "Casual_Guy",
  "Lively_Girl",
  "Patient_Man",
  "Young_Knight",
  "Determined_Man",
  "Lovely_Girl",
  "Decent_Boy",
  "Imposing_Manner",
  "Elegant_Man",
  "Abbess",
  "Sweet_Girl_2",
  "Exuberant_Girl",
];

const EMOTION_OPTIONS = ["happy", "sad", "angry", "fearful", "disgusted", "surprised", "neutral"];

const SAMPLE_RATE_OPTIONS = [8000, 16000, 22050, 24000, 32000, 44100];
const BITRATE_OPTIONS = [32000, 64000, 128000, 256000];
const LANGUAGE_BOOST_OPTIONS = [
  "auto",
  "English",
  "Chinese",
  "Chinese,Yue",
  "Arabic",
  "Russian",
  "Spanish",
  "French",
  "Portuguese",
  "German",
  "Turkish",
  "Dutch",
  "Ukrainian",
  "Vietnamese",
  "Indonesian",
  "Japanese",
  "Italian",
  "Korean",
  "Thai",
  "Polish",
  "Romanian",
  "Greek",
  "Czech",
  "Finnish",
  "Hindi",
];

export const AudioSettingsModal: React.FC<AudioSettingsModalProps> = ({
  open,
  onClose,
  onApplySettings,
  initialSettings,
  isGenerating = false,
  sceneTitle,
}) => {
  const [settings, setSettings] = useState<YouTubeAudioGenerationSettings>(initialSettings);

  useEffect(() => {
    setSettings(initialSettings);
  }, [initialSettings]);

  const handleApply = () => {
    onApplySettings(settings);
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
          color: "white",
        },
      }}
    >
      <DialogTitle>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 0.5 }}>
              Audio Generation Settings
            </Typography>
            {sceneTitle && (
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                Configure voice settings for "{sceneTitle}"
              </Typography>
            )}
          </Box>
          <IconButton onClick={onClose} size="small" sx={{ color: "rgba(255,255,255,0.7)" }}>
            <CloseIcon />
          </IconButton>
        </Stack>
        <Typography variant="body2" sx={{ opacity: 0.7, mt: 1 }}>
          Customize voice, tone, and quality for better audio results. Changes apply only to this scene.
        </Typography>
      </DialogTitle>

      <DialogContent>
        <Stack spacing={3} sx={{ mt: 1 }}>
          {/* Voice Selection */}
          <Box>
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                Voice
              </Typography>
              <Tooltip title="Choose from professional voice options. Each voice has unique characteristics for different content types." arrow>
                <IconButton size="small" sx={{ color: "rgba(255,255,255,0.5)" }}>
                  <HelpOutlineIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Stack>
            <FormControl fullWidth>
              <Select
                value={settings.voiceId}
                onChange={(e) => setSettings({ ...settings, voiceId: e.target.value })}
                sx={{
                  backgroundColor: alpha("#ffffff", 0.1),
                  color: "white",
                  "& .MuiOutlinedInput-notchedOutline": { borderColor: "rgba(255,255,255,0.3)" },
                  "&:hover .MuiOutlinedInput-notchedOutline": { borderColor: "rgba(255,255,255,0.4)" },
                  "&.Mui-focused .MuiOutlinedInput-notchedOutline": { borderColor: "#ffffff" },
                  "& .MuiSvgIcon-root": { color: "rgba(255,255,255,0.7)" },
                }}
              >
                {VOICE_OPTIONS.map((voice) => (
                  <MenuItem key={voice} value={voice}>
                    {voice.replace('_', ' ')}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>

          {/* Speed / Volume / Pitch */}
          <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
            <Box sx={{ flex: 1 }}>
              <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 0.5 }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                  Speed ({settings.speed.toFixed(2)})
                </Typography>
                <Tooltip title="How fast the voice speaks. 1.0 = normal speed. Lower for narration, higher for conversational." arrow>
                  <HelpOutlineIcon fontSize="small" sx={{ color: "rgba(255,255,255,0.5)" }} />
                </Tooltip>
              </Stack>
              <Slider
                value={settings.speed}
                min={0.5}
                max={2.0}
                step={0.05}
                onChange={(_, v) => setSettings({ ...settings, speed: v as number })}
                sx={{ color: "#4ade80" }}
              />
              <Typography variant="caption" sx={{ opacity: 0.7 }}>
                0.5 = Slower (narrative) • 1.0 = Normal • 2.0 = Faster (energetic)
              </Typography>
            </Box>

            <Box sx={{ flex: 1 }}>
              <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 0.5 }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                  Volume ({settings.volume.toFixed(1)})
                </Typography>
                <Tooltip title="Loudness of the voice. 1.0 = normal volume." arrow>
                  <HelpOutlineIcon fontSize="small" sx={{ color: "rgba(255,255,255,0.5)" }} />
                </Tooltip>
              </Stack>
              <Slider
                value={settings.volume}
                min={0.1}
                max={10.0}
                step={0.1}
                onChange={(_, v) => setSettings({ ...settings, volume: v as number })}
                sx={{ color: "#fbbf24" }}
              />
              <Typography variant="caption" sx={{ opacity: 0.7 }}>
                0.1 = Very soft • 1.0 = Normal • 10.0 = Very loud
              </Typography>
            </Box>

            <Box sx={{ flex: 1 }}>
              <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 0.5 }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                  Pitch ({settings.pitch})
                </Typography>
                <Tooltip title="Tone of the voice. 0 = neutral. Negative = deeper, positive = higher pitched." arrow>
                  <HelpOutlineIcon fontSize="small" sx={{ color: "rgba(255,255,255,0.5)" }} />
                </Tooltip>
              </Stack>
              <Slider
                value={settings.pitch}
                min={-12}
                max={12}
                step={0.5}
                onChange={(_, v) => setSettings({ ...settings, pitch: v as number })}
                sx={{ color: "#f87171" }}
              />
              <Typography variant="caption" sx={{ opacity: 0.7 }}>
                -12 = Very deep • 0 = Normal • +12 = Very high
              </Typography>
            </Box>
          </Stack>

          {/* Emotion */}
          <Box>
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                Emotion
              </Typography>
              <Tooltip title="Sets the vocal mood and emotional delivery style." arrow>
                <IconButton size="small" sx={{ color: "rgba(255,255,255,0.5)" }}>
                  <HelpOutlineIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Stack>
            <FormControl fullWidth>
              <Select
                value={settings.emotion}
                onChange={(e) => setSettings({ ...settings, emotion: e.target.value })}
                sx={{
                  backgroundColor: alpha("#ffffff", 0.1),
                  color: "white",
                  "& .MuiOutlinedInput-notchedOutline": { borderColor: "rgba(255,255,255,0.3)" },
                  "&:hover .MuiOutlinedInput-notchedOutline": { borderColor: "rgba(255,255,255,0.4)" },
                  "&.Mui-focused .MuiOutlinedInput-notchedOutline": { borderColor: "#ffffff" },
                  "& .MuiSvgIcon-root": { color: "rgba(255,255,255,0.7)" },
                }}
              >
                {EMOTION_OPTIONS.map((emotion) => (
                  <MenuItem key={emotion} value={emotion}>
                    {emotion.charAt(0).toUpperCase() + emotion.slice(1)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <Typography variant="caption" sx={{ opacity: 0.7, mt: 0.5, display: "block" }}>
              Choose emotion that matches your content: happy for upbeat, neutral for professional, sad for serious topics.
            </Typography>
          </Box>

          {/* Language & Normalization */}
          <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
            <Box sx={{ flex: 1 }}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={settings.englishNormalization}
                    onChange={(e) => setSettings({ ...settings, englishNormalization: e.target.checked })}
                    sx={{ color: "rgba(255,255,255,0.7)" }}
                  />
                }
                label={
                  <Typography variant="body2" sx={{ color: "white" }}>
                    English normalization
                  </Typography>
                }
              />
              <Typography variant="caption" sx={{ opacity: 0.7 }}>
                Improves pronunciation of numbers, dates, and technical terms.
              </Typography>
            </Box>

            <Box sx={{ flex: 1 }}>
              <TextField
                select
                fullWidth
                label="Language boost"
                value={settings.languageBoost || "auto"}
                onChange={(e) => setSettings({ ...settings, languageBoost: e.target.value })}
                InputLabelProps={{ sx: { color: "rgba(255,255,255,0.7)" } }}
                sx={{
                  "& .MuiOutlinedInput-root": {
                    backgroundColor: alpha("#ffffff", 0.1),
                    color: "white",
                    "& fieldset": { borderColor: "rgba(255,255,255,0.3)" },
                    "&:hover fieldset": { borderColor: "rgba(255,255,255,0.4)" },
                    "&.Mui-focused fieldset": { borderColor: "#ffffff" },
                    "& .MuiSvgIcon-root": { color: "rgba(255,255,255,0.7)" },
                  },
                }}
              >
                {LANGUAGE_BOOST_OPTIONS.map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </TextField>
              <Typography variant="caption" sx={{ opacity: 0.7, mt: 0.5, display: "block" }}>
                Enhances pronunciation for specific languages.
              </Typography>
            </Box>
          </Stack>

          {/* Quality Settings */}
          <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
            <Box sx={{ flex: 1 }}>
              <TextField
                select
                fullWidth
                label="Sample rate"
                value={settings.sampleRate || 24000}
                onChange={(e) => setSettings({ ...settings, sampleRate: Number(e.target.value) })}
                InputLabelProps={{ sx: { color: "rgba(255,255,255,0.7)" } }}
                sx={{
                  "& .MuiOutlinedInput-root": {
                    backgroundColor: alpha("#ffffff", 0.1),
                    color: "white",
                    "& fieldset": { borderColor: "rgba(255,255,255,0.3)" },
                    "&:hover fieldset": { borderColor: "rgba(255,255,255,0.4)" },
                    "&.Mui-focused fieldset": { borderColor: "#ffffff" },
                    "& .MuiSvgIcon-root": { color: "rgba(255,255,255,0.7)" },
                  },
                }}
              >
                {SAMPLE_RATE_OPTIONS.map((rate) => (
                  <MenuItem key={rate} value={rate}>
                    {rate} Hz
                  </MenuItem>
                ))}
              </TextField>
              <Typography variant="caption" sx={{ opacity: 0.7, mt: 0.5, display: "block" }}>
                Higher = better quality, larger files. 24kHz recommended for voice.
              </Typography>
            </Box>

            <Box sx={{ flex: 1 }}>
              <TextField
                select
                fullWidth
                label="Bitrate"
                value={settings.bitrate}
                onChange={(e) => setSettings({ ...settings, bitrate: Number(e.target.value) })}
                InputLabelProps={{ sx: { color: "rgba(255,255,255,0.7)" } }}
                sx={{
                  "& .MuiOutlinedInput-root": {
                    backgroundColor: alpha("#ffffff", 0.1),
                    color: "white",
                    "& fieldset": { borderColor: "rgba(255,255,255,0.3)" },
                    "&:hover fieldset": { borderColor: "rgba(255,255,255,0.4)" },
                    "&.Mui-focused fieldset": { borderColor: "#ffffff" },
                    "& .MuiSvgIcon-root": { color: "rgba(255,255,255,0.7)" },
                  },
                }}
              >
                {BITRATE_OPTIONS.map((bitrate) => (
                  <MenuItem key={bitrate} value={bitrate}>
                    {bitrate / 1000} kbps
                  </MenuItem>
                ))}
              </TextField>
              <Typography variant="caption" sx={{ opacity: 0.7, mt: 0.5, display: "block" }}>
                Higher = clearer audio, larger files. 128kbps recommended.
              </Typography>
            </Box>
          </Stack>

          {/* Format & Channel */}
          <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
            <Box sx={{ flex: 1 }}>
              <TextField
                select
                fullWidth
                label="Channel"
                value={settings.channel}
                onChange={(e) => setSettings({ ...settings, channel: e.target.value as "1" | "2" })}
                InputLabelProps={{ sx: { color: "rgba(255,255,255,0.7)" } }}
                sx={{
                  "& .MuiOutlinedInput-root": {
                    backgroundColor: alpha("#ffffff", 0.1),
                    color: "white",
                    "& fieldset": { borderColor: "rgba(255,255,255,0.3)" },
                    "&:hover fieldset": { borderColor: "rgba(255,255,255,0.4)" },
                    "&.Mui-focused fieldset": { borderColor: "#ffffff" },
                    "& .MuiSvgIcon-root": { color: "rgba(255,255,255,0.7)" },
                  },
                }}
              >
                <MenuItem value="1">Mono (smaller files, voice-focused)</MenuItem>
                <MenuItem value="2">Stereo (better spatial audio)</MenuItem>
              </TextField>
            </Box>

            <Box sx={{ flex: 1 }}>
              <TextField
                select
                fullWidth
                label="Format"
                value={settings.format}
                onChange={(e) => setSettings({ ...settings, format: e.target.value as "mp3" | "wav" | "pcm" | "flac" })}
                InputLabelProps={{ sx: { color: "rgba(255,255,255,0.7)" } }}
                sx={{
                  "& .MuiOutlinedInput-root": {
                    backgroundColor: alpha("#ffffff", 0.1),
                    color: "white",
                    "& fieldset": { borderColor: "rgba(255,255,255,0.3)" },
                    "&:hover fieldset": { borderColor: "rgba(255,255,255,0.4)" },
                    "&.Mui-focused fieldset": { borderColor: "#ffffff" },
                    "& .MuiSvgIcon-root": { color: "rgba(255,255,255,0.7)" },
                  },
                }}
              >
                <MenuItem value="mp3">MP3 (compressed, universal)</MenuItem>
                <MenuItem value="wav">WAV (uncompressed, high quality)</MenuItem>
                <MenuItem value="pcm">PCM (raw audio data)</MenuItem>
                <MenuItem value="flac">FLAC (lossless compression)</MenuItem>
              </TextField>
            </Box>
          </Stack>

          {/* Sync Mode */}
          <Box>
            <FormControlLabel
              control={
                <Checkbox
                  checked={settings.enableSyncMode}
                  onChange={(e) => setSettings({ ...settings, enableSyncMode: e.target.checked })}
                  sx={{ color: "rgba(255,255,255,0.7)" }}
                />
              }
              label={
                <Typography variant="body2" sx={{ color: "white" }}>
                  Enable sync mode (faster, recommended)
                </Typography>
              }
            />
            <Typography variant="caption" sx={{ opacity: 0.7 }}>
              Waits for audio completion before returning. Recommended for most use cases.
            </Typography>
          </Box>
        </Stack>
      </DialogContent>

      <DialogActions sx={{ p: 3, pt: 2 }}>
        <Button
          onClick={onClose}
          disabled={isGenerating}
          sx={{ color: "rgba(255,255,255,0.7)" }}
        >
          Cancel
        </Button>
        <Button
          onClick={handleApply}
          variant="contained"
          disabled={isGenerating}
          startIcon={isGenerating ? undefined : <VolumeUp />}
          sx={{
            backgroundColor: "#4ade80",
            "&:hover": { backgroundColor: "#22c55e" },
            "&:disabled": { backgroundColor: "rgba(255,255,255,0.2)" },
          }}
        >
          {isGenerating ? "Generating..." : "Apply Settings & Generate"}
        </Button>
      </DialogActions>
    </Dialog>
  );
};
