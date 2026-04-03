import React, { useState, useEffect, useMemo } from "react";
import {
  Box,
  Typography,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Stack,
  Button,
  Chip,
  CircularProgress,
  Tooltip,
  alpha,
  IconButton,
  ListItemIcon,
  ListItemText,
} from "@mui/material";
import {
  Mic,
  PlayArrow,
  Pause,
  CloudUpload,
  HelpOutline,
  AutoAwesome,
  CheckCircle,
} from "@mui/icons-material";
import { getLatestVoiceClone, VoiceCloneResponse } from "../../api/brandAssets";

export type VoiceOption = {
  id: string;
  name: string;
  personality?: string;
  isCustom?: boolean;
  previewUrl?: string;
};

interface VoiceSelectorProps {
  value: string;
  onChange: (voiceId: string) => void;
  disabled?: boolean;
  showVoiceClone?: boolean;
  compact?: boolean;
}

const PREDEFINED_VOICES: VoiceOption[] = [
  { id: "Wise_Woman", name: "Wise Woman", personality: "Authoritative, trustworthy female voice - perfect for educational content" },
  { id: "Friendly_Person", name: "Friendly Person", personality: "Warm, approachable voice - great for welcoming introductions" },
  { id: "Inspirational_girl", name: "Inspirational Girl", personality: "Motivational, uplifting female voice - ideal for inspiration" },
  { id: "Deep_Voice_Man", name: "Deep Voice Man", personality: "Powerful, commanding male voice - excellent for serious topics" },
  { id: "Calm_Woman", name: "Calm Woman", personality: "Soothing, composed female voice - perfect for meditation or sensitive topics" },
  { id: "Casual_Guy", name: "Casual Guy", personality: "Relaxed, conversational male voice - great for vlogs and tutorials" },
  { id: "Lively_Girl", name: "Lively Girl", personality: "Energetic, enthusiastic female voice - ideal for exciting announcements" },
  { id: "Patient_Man", name: "Patient Man", personality: "Gentle, understanding male voice - perfect for explanations" },
  { id: "Young_Knight", name: "Young Knight", personality: "Brave, confident male voice - great for adventure and gaming" },
  { id: "Determined_Man", name: "Determined Man", personality: "Strong, resolute male voice - excellent for motivational speeches" },
  { id: "Lovely_Girl", name: "Lovely Girl", personality: "Sweet, charming female voice - ideal for storytelling" },
  { id: "Decent_Boy", name: "Decent Boy", personality: "Honest, sincere male voice - perfect for testimonials" },
  { id: "Imposing_Manner", name: "Imposing Manner", personality: "Formal, dignified male voice - great for corporate content" },
  { id: "Elegant_Man", name: "Elegant Man", personality: "Refined, sophisticated male voice - ideal for luxury content" },
  { id: "Abbess", name: "Abbess", personality: "Spiritual, serene female voice - perfect for meditation" },
  { id: "Sweet_Girl_2", name: "Sweet Girl 2", personality: "Gentle, melodic female voice - excellent for children's content" },
  { id: "Exuberant_Girl", name: "Exuberant Girl", personality: "Joyful, expressive female voice - ideal for celebrations" },
];

const VOICE_CLONE_ID = "MY_VOICE_CLONE";

export const VoiceSelector: React.FC<VoiceSelectorProps> = ({
  value,
  onChange,
  disabled = false,
  showVoiceClone = true,
  compact = false,
}) => {
  const [voiceClone, setVoiceClone] = useState<VoiceCloneResponse | null>(null);
  const [loadingVoiceClone, setLoadingVoiceClone] = useState(false);
  const [playingPreview, setPlayingPreview] = useState<string | null>(null);

  const voiceOptions = useMemo(() => {
    const options: VoiceOption[] = [...PREDEFINED_VOICES];
    
    if (showVoiceClone && voiceClone?.success && voiceClone.custom_voice_id) {
      options.unshift({
        id: VOICE_CLONE_ID,
        name: voiceClone.voice_name || voiceClone.custom_voice_id || "My Voice Clone",
        personality: "Your own voice - cloned from audio sample",
        isCustom: true,
        previewUrl: voiceClone.preview_audio_url,
      });
    }
    
    return options;
  }, [showVoiceClone, voiceClone]);

  const selectedVoice = useMemo(() => {
    if (value === VOICE_CLONE_ID && voiceClone?.success) {
      return voiceOptions.find(v => v.id === VOICE_CLONE_ID);
    }
    return voiceOptions.find(v => v.id === value) || voiceOptions[0];
  }, [value, voiceOptions, voiceClone]);

  useEffect(() => {
    if (!showVoiceClone) return;
    
    const fetchVoiceClone = async () => {
      try {
        setLoadingVoiceClone(true);
        const result = await getLatestVoiceClone();
        setVoiceClone(result);
      } catch (error) {
        console.error("Failed to fetch voice clone:", error);
      } finally {
        setLoadingVoiceClone(false);
      }
    };
    
    fetchVoiceClone();
  }, [showVoiceClone]);

  const handlePreview = (voice: VoiceOption) => {
    if (!voice.previewUrl) return;
    
    if (playingPreview === voice.id) {
      const audio = document.getElementById(`voice-preview-${voice.id}`) as HTMLAudioElement;
      if (audio) {
        audio.pause();
        audio.currentTime = 0;
      }
      setPlayingPreview(null);
    } else {
      setPlayingPreview(voice.id);
      const audio = new Audio(voice.previewUrl);
      audio.id = `voice-preview-${voice.id}`;
      audio.onerror = () => {
        console.error("Failed to load voice preview audio");
        setPlayingPreview(null);
      };
      audio.onended = () => setPlayingPreview(null);
      audio.play().catch((err) => {
        console.error("Failed to play voice preview:", err);
        setPlayingPreview(null);
      });
    }
  };

  const handleChange = (newValue: string) => {
    if (newValue === VOICE_CLONE_ID && voiceClone?.success) {
      onChange(voiceClone.custom_voice_id || VOICE_CLONE_ID);
    } else {
      onChange(newValue);
    }
  };

  const isVoiceCloneSelected = value === VOICE_CLONE_ID || 
    (voiceClone?.success && voiceClone.custom_voice_id && value === voiceClone.custom_voice_id);

  if (compact) {
    return (
      <FormControl fullWidth size="small">
        <InputLabel>Voice</InputLabel>
        <Select
          value={isVoiceCloneSelected ? VOICE_CLONE_ID : value}
          onChange={(e) => handleChange(e.target.value)}
          label="Voice"
          disabled={disabled}
          startAdornment={
            <ListItemIcon sx={{ minWidth: 32 }}>
              <Mic fontSize="small" sx={{ color: isVoiceCloneSelected ? "#667eea" : "inherit" }} />
            </ListItemIcon>
          }
        >
          {voiceOptions.map((voice) => (
            <MenuItem key={voice.id} value={voice.id}>
              <ListItemText 
                primary={voice.name} 
                secondary={voice.isCustom ? "Custom voice clone" : voice.personality?.split(' - ')[0]} 
              />
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    );
  }

  return (
    <Box>
      <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
        <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
          Voice
        </Typography>
        <Tooltip title="Choose a system voice or your custom cloned voice" arrow>
          <IconButton size="small" sx={{ color: "rgba(0,0,0,0.5)" }}>
            <HelpOutline fontSize="small" />
          </IconButton>
        </Tooltip>
        {showVoiceClone && loadingVoiceClone && (
          <CircularProgress size={16} sx={{ ml: 1 }} />
        )}
      </Stack>

      <FormControl fullWidth>
        <Select
          value={isVoiceCloneSelected ? VOICE_CLONE_ID : value}
          onChange={(e) => handleChange(e.target.value)}
          disabled={disabled}
          renderValue={(selected) => {
            const voice = voiceOptions.find(v => 
              v.id === selected || 
              (selected === VOICE_CLONE_ID && v.isCustom)
            );
            return (
              <Stack direction="row" spacing={1} alignItems="center">
                <Mic fontSize="small" sx={{ color: voice?.isCustom ? "#667eea" : "inherit" }} />
                <Typography>{voice?.name}</Typography>
                {voice?.isCustom && (
                  <Chip 
                    label="Cloned" 
                    size="small" 
                    sx={{ 
                      bgcolor: alpha("#667eea", 0.1), 
                      color: "#667eea",
                      height: 20,
                      fontSize: "0.7rem",
                    }} 
                  />
                )}
              </Stack>
            );
          }}
          MenuProps={{
            PaperProps: {
              sx: {
                maxHeight: 400,
              },
            },
          }}
        >
          {showVoiceClone && voiceClone?.success && voiceClone.custom_voice_id && (
            <MenuItem value={VOICE_CLONE_ID} sx={{ borderBottom: '1px solid rgba(0,0,0,0.1)' }}>
              <ListItemIcon>
                <AutoAwesome sx={{ color: "#667eea" }} />
              </ListItemIcon>
              <ListItemText 
                primary={
                  <Stack direction="row" spacing={1} alignItems="center">
                    <Typography fontWeight={600} sx={{ color: "#667eea" }}>
                      My Voice Clone
                    </Typography>
                    <Chip 
                      icon={<CheckCircle sx={{ fontSize: "14px !important" }} />}
                      label="Active" 
                      size="small" 
                      sx={{ 
                        bgcolor: alpha("#10b981", 0.1), 
                        color: "#10b981",
                        height: 20,
                        fontSize: "0.65rem",
                        '& .MuiChip-icon': { color: "#10b981" }
                      }} 
                    />
                  </Stack>
                }
                secondary={
                  voiceClone.preview_audio_url && (
                    <Button
                      size="small"
                      startIcon={playingPreview === VOICE_CLONE_ID ? <Pause /> : <PlayArrow />}
                      onClick={(e) => {
                        e.stopPropagation();
                        handlePreview({ 
                          id: VOICE_CLONE_ID, 
                          name: voiceClone.voice_name || "My Voice Clone",
                          previewUrl: voiceClone.preview_audio_url 
                        });
                      }}
                      sx={{ mt: 0.5, textTransform: 'none' }}
                    >
                      {playingPreview === VOICE_CLONE_ID ? "Stop" : "Preview"}
                    </Button>
                  )
                }
              />
            </MenuItem>
          )}
          
          <MenuItem disabled sx={{ opacity: 0.6 }}>
            <Typography variant="caption">System Voices</Typography>
          </MenuItem>
          
          {voiceOptions.filter(v => !v.isCustom).map((voice) => (
            <MenuItem key={voice.id} value={voice.id}>
              <ListItemText 
                primary={voice.name} 
                secondary={voice.personality?.split(' - ')[0]}
              />
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      {selectedVoice?.personality && (
        <Typography variant="caption" sx={{ color: "text.secondary", mt: 0.5, display: 'block' }}>
          {selectedVoice.personality}
        </Typography>
      )}

      {showVoiceClone && !voiceClone?.success && (
        <Box sx={{ mt: 2, p: 2, bgcolor: alpha("#f8fafc", 0.5), borderRadius: 2, border: '1px dashed rgba(0,0,0,0.1)' }}>
          <Stack direction="row" spacing={1} alignItems="center">
            <CloudUpload sx={{ color: "#64748b" }} />
            <Typography variant="body2" sx={{ color: "#64748b" }}>
              Don't see your voice? Go to Onboarding → Voice Cloning to create your custom voice clone.
            </Typography>
          </Stack>
        </Box>
      )}
    </Box>
  );
};

export default VoiceSelector;
