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
import { HelpOutline as HelpOutlineIcon, Close as CloseIcon } from "@mui/icons-material";
import { PrimaryButton, SecondaryButton } from "../ui";

export type AudioGenerationSettings = {
  voiceId: string;
  speed: number;
  volume: number;
  pitch: number;
  emotion: string;
  englishNormalization: boolean;
  sampleRate?: number;
  bitrate?: number;
  channel?: "1" | "2";
  format?: "mp3" | "wav" | "pcm" | "flac";
  languageBoost?: string;
};

interface AudioRegenerateModalProps {
  open: boolean;
  onClose: () => void;
  onRegenerate: (settings: AudioGenerationSettings) => void;
  initialSettings: AudioGenerationSettings;
  isGenerating?: boolean;
}

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

export const AudioRegenerateModal: React.FC<AudioRegenerateModalProps> = ({
  open,
  onClose,
  onRegenerate,
  initialSettings,
  isGenerating = false,
}) => {
  const [settings, setSettings] = useState<AudioGenerationSettings>(initialSettings);

  useEffect(() => {
    setSettings(initialSettings);
  }, [initialSettings]);

  const handleRegenerate = () => {
    onRegenerate(settings);
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          background: alpha("#0f172a", 0.95),
          backdropFilter: "blur(20px)",
          border: "1px solid rgba(255,255,255,0.1)",
          borderRadius: 4,
        },
      }}
    >
      <DialogTitle>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Typography variant="h6" sx={{ color: "white", fontWeight: 600 }}>
            Regenerate Audio with Custom Settings
          </Typography>
          <IconButton onClick={onClose} size="small" sx={{ color: "rgba(255,255,255,0.7)" }}>
            <CloseIcon />
          </IconButton>
        </Stack>
        <Typography variant="body2" sx={{ color: "rgba(255,255,255,0.6)", mt: 1 }}>
          Adjust voice, speed, tone, and quality. Changes apply only to this scene.
        </Typography>
      </DialogTitle>

      <DialogContent>
        <Stack spacing={3} sx={{ mt: 1 }}>
          {/* Voice */}
          <Box>
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
              <Typography variant="subtitle1" sx={{ color: "white", fontWeight: 600 }}>
                Voice
              </Typography>
              <Tooltip title="Choose a system voice or your custom trained voice ID." arrow>
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
                  backgroundColor: alpha("#ffffff", 0.05),
                  color: "white",
                  "& .MuiOutlinedInput-notchedOutline": { borderColor: "rgba(255,255,255,0.2)" },
                  "&:hover .MuiOutlinedInput-notchedOutline": { borderColor: "rgba(255,255,255,0.3)" },
                  "&.Mui-focused .MuiOutlinedInput-notchedOutline": { borderColor: "#667eea" },
                  "& .MuiSvgIcon-root": { color: "rgba(255,255,255,0.7)" },
                }}
              >
                {VOICE_OPTIONS.map((v) => (
                  <MenuItem key={v} value={v}>
                    {v}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>

          {/* Speed / Volume / Pitch */}
          <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
            <Box sx={{ flex: 1 }}>
              <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 0.5 }}>
                <Typography variant="subtitle2" sx={{ color: "white", fontWeight: 600 }}>
                  Speed (0.5-2.0)
                </Typography>
                <Tooltip title="Control how fast the voice speaks. 1.0 is normal." arrow>
                  <HelpOutlineIcon fontSize="small" sx={{ color: "rgba(255,255,255,0.5)" }} />
                </Tooltip>
              </Stack>
              <Slider
                value={settings.speed}
                min={0.5}
                max={2.0}
                step={0.05}
                onChange={(_, v) => setSettings({ ...settings, speed: v as number })}
                sx={{ color: "#6366f1" }}
              />
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.6)" }}>
                Slower (narrative) ↔ Faster (conversational). Impacts duration.
              </Typography>
            </Box>
            <Box sx={{ flex: 1 }}>
              <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 0.5 }}>
                <Typography variant="subtitle2" sx={{ color: "white", fontWeight: 600 }}>
                  Volume (0.1-10)
                </Typography>
                <Tooltip title="Loudness of the voice. 1.0 is normal loudness." arrow>
                  <HelpOutlineIcon fontSize="small" sx={{ color: "rgba(255,255,255,0.5)" }} />
                </Tooltip>
              </Stack>
              <Slider
                value={settings.volume}
                min={0.1}
                max={10}
                step={0.1}
                onChange={(_, v) => setSettings({ ...settings, volume: v as number })}
                sx={{ color: "#10b981" }}
              />
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.6)" }}>
                Lower for soft tone; higher for punchier delivery.
              </Typography>
            </Box>
            <Box sx={{ flex: 1 }}>
              <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 0.5 }}>
                <Typography variant="subtitle2" sx={{ color: "white", fontWeight: 600 }}>
                  Pitch (-12 to 12)
                </Typography>
                <Tooltip title="Tone of the voice. 0 is neutral. Negative is deeper; positive is brighter." arrow>
                  <HelpOutlineIcon fontSize="small" sx={{ color: "rgba(255,255,255,0.5)" }} />
                </Tooltip>
              </Stack>
              <Slider
                value={settings.pitch}
                min={-12}
                max={12}
                step={0.5}
                onChange={(_, v) => setSettings({ ...settings, pitch: v as number })}
                sx={{ color: "#f97316" }}
              />
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.6)" }}>
                Use small adjustments (±2) for natural results.
              </Typography>
            </Box>
          </Stack>

          {/* Emotion */}
          <Box>
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
              <Typography variant="subtitle1" sx={{ color: "white", fontWeight: 600 }}>
                Emotion
              </Typography>
              <Tooltip title="Sets the vocal mood: happy, neutral, sad, etc." arrow>
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
                  backgroundColor: alpha("#ffffff", 0.05),
                  color: "white",
                  "& .MuiOutlinedInput-notchedOutline": { borderColor: "rgba(255,255,255,0.2)" },
                  "&:hover .MuiOutlinedInput-notchedOutline": { borderColor: "rgba(255,255,255,0.3)" },
                  "&.Mui-focused .MuiOutlinedInput-notchedOutline": { borderColor: "#667eea" },
                  "& .MuiSvgIcon-root": { color: "rgba(255,255,255,0.7)" },
                }}
              >
                {EMOTION_OPTIONS.map((e) => (
                  <MenuItem key={e} value={e}>
                    {e}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.6)", mt: 0.5, display: "block" }}>
              Tip: happy/neutral for most podcasts; sad/angry for dramatic or critical segments.
            </Typography>
          </Box>

          {/* Normalization & Language */}
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
                    English normalization (better numbers/dates)
                  </Typography>
                }
              />
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.6)" }}>
                Improves pronunciation of numbers/dates (recommended for stats-heavy scenes).
              </Typography>
            </Box>
            <Box sx={{ flex: 1 }}>
              <TextField
                select
                fullWidth
                label="Language boost"
                value={settings.languageBoost || "auto"}
                onChange={(e) => setSettings({ ...settings, languageBoost: e.target.value })}
                SelectProps={{ native: false }}
                InputLabelProps={{ sx: { color: "rgba(255,255,255,0.7)" } }}
                sx={{
                  "& .MuiOutlinedInput-root": {
                    backgroundColor: alpha("#ffffff", 0.05),
                    color: "white",
                    "& fieldset": { borderColor: "rgba(255,255,255,0.2)" },
                    "&:hover fieldset": { borderColor: "rgba(255,255,255,0.3)" },
                    "&.Mui-focused fieldset": { borderColor: "#667eea" },
                    "& .MuiSvgIcon-root": { color: "rgba(255,255,255,0.7)" },
                  },
                }}
              >
                {LANGUAGE_BOOST_OPTIONS.map((opt) => (
                  <MenuItem key={opt} value={opt}>
                    {opt}
                  </MenuItem>
                ))}
              </TextField>
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.6)", mt: 0.5, display: "block" }}>
                Helps with language-specific pronunciation and accent.
              </Typography>
            </Box>
          </Stack>

          {/* Quality & Format */}
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
                    backgroundColor: alpha("#ffffff", 0.05),
                    color: "white",
                    "& fieldset": { borderColor: "rgba(255,255,255,0.2)" },
                    "&:hover fieldset": { borderColor: "rgba(255,255,255,0.3)" },
                    "&.Mui-focused fieldset": { borderColor: "#667eea" },
                    "& .MuiSvgIcon-root": { color: "rgba(255,255,255,0.7)" },
                  },
                }}
              >
                {SAMPLE_RATE_OPTIONS.map((opt) => (
                  <MenuItem key={opt} value={opt}>
                    {opt} Hz
                  </MenuItem>
                ))}
              </TextField>
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.6)", mt: 0.5, display: "block" }}>
                Higher sample rate = higher fidelity (24k+ recommended for podcast voice).
              </Typography>
            </Box>
            <Box sx={{ flex: 1 }}>
              <TextField
                select
                fullWidth
                label="Bitrate"
                value={settings.bitrate || 64000}
                onChange={(e) => setSettings({ ...settings, bitrate: Number(e.target.value) })}
                InputLabelProps={{ sx: { color: "rgba(255,255,255,0.7)" } }}
                sx={{
                  "& .MuiOutlinedInput-root": {
                    backgroundColor: alpha("#ffffff", 0.05),
                    color: "white",
                    "& fieldset": { borderColor: "rgba(255,255,255,0.2)" },
                    "&:hover fieldset": { borderColor: "rgba(255,255,255,0.3)" },
                    "&.Mui-focused fieldset": { borderColor: "#667eea" },
                    "& .MuiSvgIcon-root": { color: "rgba(255,255,255,0.7)" },
                  },
                }}
              >
                {BITRATE_OPTIONS.map((opt) => (
                  <MenuItem key={opt} value={opt}>
                    {opt / 1000} kbps
                  </MenuItem>
                ))}
              </TextField>
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.6)", mt: 0.5, display: "block" }}>
                Higher bitrate = larger file but clearer audio. 64–128 kbps is great for voice.
              </Typography>
            </Box>
          </Stack>

          <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
            <Box sx={{ flex: 1 }}>
              <TextField
                select
                fullWidth
                label="Channel"
                value={settings.channel || "1"}
                onChange={(e) => setSettings({ ...settings, channel: e.target.value as "1" | "2" })}
                InputLabelProps={{ sx: { color: "rgba(255,255,255,0.7)" } }}
                sx={{
                  "& .MuiOutlinedInput-root": {
                    backgroundColor: alpha("#ffffff", 0.05),
                    color: "white",
                    "& fieldset": { borderColor: "rgba(255,255,255,0.2)" },
                    "&:hover fieldset": { borderColor: "rgba(255,255,255,0.3)" },
                    "&.Mui-focused fieldset": { borderColor: "#667eea" },
                    "& .MuiSvgIcon-root": { color: "rgba(255,255,255,0.7)" },
                  },
                }}
              >
                <MenuItem value="1">Mono (smaller, voice-focused)</MenuItem>
                <MenuItem value="2">Stereo (wider, more presence)</MenuItem>
              </TextField>
            </Box>
            <Box sx={{ flex: 1 }}>
              <TextField
                select
                fullWidth
                label="Format"
                value={settings.format || "mp3"}
                onChange={(e) => setSettings({ ...settings, format: e.target.value as "mp3" | "wav" | "pcm" | "flac" })}
                InputLabelProps={{ sx: { color: "rgba(255,255,255,0.7)" } }}
                sx={{
                  "& .MuiOutlinedInput-root": {
                    backgroundColor: alpha("#ffffff", 0.05),
                    color: "white",
                    "& fieldset": { borderColor: "rgba(255,255,255,0.2)" },
                    "&:hover fieldset": { borderColor: "rgba(255,255,255,0.3)" },
                    "&.Mui-focused fieldset": { borderColor: "#667eea" },
                    "& .MuiSvgIcon-root": { color: "rgba(255,255,255,0.7)" },
                  },
                }}
              >
                <MenuItem value="mp3">mp3 (small, universal)</MenuItem>
                <MenuItem value="wav">wav (uncompressed)</MenuItem>
                <MenuItem value="pcm">pcm (raw)</MenuItem>
                <MenuItem value="flac">flac (lossless)</MenuItem>
              </TextField>
            </Box>
          </Stack>
        </Stack>
      </DialogContent>

      <DialogActions sx={{ p: 3, pt: 2 }}>
        <SecondaryButton onClick={onClose} disabled={isGenerating}>
          Cancel
        </SecondaryButton>
        <PrimaryButton onClick={handleRegenerate} loading={isGenerating} disabled={isGenerating}>
          {isGenerating ? "Generating..." : "Apply & Regenerate"}
        </PrimaryButton>
      </DialogActions>
    </Dialog>
  );
};

