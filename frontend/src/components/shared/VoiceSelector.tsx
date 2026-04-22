import React, { useState, useEffect, useMemo, useCallback, useRef } from "react";
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
  Collapse,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Slider,
} from "@mui/material";
import {
  Mic,
  PlayArrow,
  Pause,
  HelpOutline,
  AutoAwesome,
  CheckCircle,
  ExpandLess,
  ExpandMore,
  RestartAlt,
  VolumeUp,
  Tune,
  Close,
  Male,
  Female,
  Category,
} from "@mui/icons-material";
import { getLatestVoiceClone, VoiceCloneResponse } from "../../api/brandAssets";
import { getAuthTokenGetter, getApiUrl } from "../../api/client";
import { VoiceAvatarPlaceholder } from "../OnboardingWizard/PersonalizationStep/components/VoiceAvatarPlaceholder";

export type VoiceOption = {
  id: string;
  name: string;
  personality?: string;
  isCustom?: boolean;
  previewUrl?: string;
  gender?: "male" | "female";
  category?: string;
};

export type VoiceAudioSettings = {
  speed: number;
  volume: number;
  pitch: number;
  emotion: string;
};

const DEFAULT_AUDIO_SETTINGS: VoiceAudioSettings = {
  speed: 1.0,
  volume: 1.0,
  pitch: 0,
  emotion: "neutral",
};

const EMOTION_OPTIONS = ["neutral", "happy", "sad", "angry", "fearful", "disgusted", "surprised"];

type GenderFilter = "all" | "male" | "female";
type CategoryFilter = string;

interface VoiceSelectorProps {
  value: string;
  onChange: (voiceId: string) => void;
  disabled?: boolean;
  showVoiceClone?: boolean;
  compact?: boolean;
  audioSettings?: VoiceAudioSettings;
  onAudioSettingsChange?: (settings: VoiceAudioSettings) => void;
}

const VOICE_SAMPLE_BASE = "/assets/voice-samples";

const VOICE_PREVIEW_MAP: Record<string, string> = {
  Wise_Woman: `${VOICE_SAMPLE_BASE}/wise_woman.mp3`,
  Friendly_Person: `${VOICE_SAMPLE_BASE}/friendly_person.mp3`,
  Inspirational_girl: `${VOICE_SAMPLE_BASE}/inspirational_girl.mp3`,
  Deep_Voice_Man: `${VOICE_SAMPLE_BASE}/deep_voice_man.mp3`,
  Calm_Woman: `${VOICE_SAMPLE_BASE}/calm_woman.mp3`,
  Casual_Guy: `${VOICE_SAMPLE_BASE}/casual_guy.mp3`,
  Lively_Girl: `${VOICE_SAMPLE_BASE}/lively_girl.mp3`,
  Patient_Man: `${VOICE_SAMPLE_BASE}/patient_man.mp3`,
  Young_Knight: `${VOICE_SAMPLE_BASE}/young_knight.mp3`,
  Determined_Man: `${VOICE_SAMPLE_BASE}/determined_man.mp3`,
  Lovely_Girl: `${VOICE_SAMPLE_BASE}/lovely_girl.mp3`,
  Decent_Boy: `${VOICE_SAMPLE_BASE}/decent_boy.mp3`,
  Imposing_Manner: `${VOICE_SAMPLE_BASE}/imposing_manner.mp3`,
  Elegant_Man: `${VOICE_SAMPLE_BASE}/elegant_man.mp3`,
  Abbess: `${VOICE_SAMPLE_BASE}/abbess.mp3`,
  Sweet_Girl_2: `${VOICE_SAMPLE_BASE}/sweet_girl.mp3`,
  Exuberant_Girl: `${VOICE_SAMPLE_BASE}/exuberant_girl.mp3`,
};

const CATEGORY_OPTIONS: { value: CategoryFilter; label: string }[] = [
  { value: "all", label: "All" },
  { value: "educational", label: "Educational" },
  { value: "marketing", label: "Marketing" },
  { value: "professional", label: "Professional" },
  { value: "creative", label: "Creative" },
  { value: "calming", label: "Calming" },
  { value: "motivational", label: "Motivational" },
];

const PREDEFINED_VOICES: VoiceOption[] = [
  { id: "Wise_Woman", name: "Wise Woman", personality: "Authoritative, trustworthy female voice - perfect for educational content", previewUrl: VOICE_PREVIEW_MAP.Wise_Woman, gender: "female", category: "educational" },
  { id: "Friendly_Person", name: "Friendly Person", personality: "Warm, approachable voice - great for welcoming introductions", previewUrl: VOICE_PREVIEW_MAP.Friendly_Person, category: "marketing" },
  { id: "Inspirational_girl", name: "Inspirational Girl", personality: "Motivational, uplifting female voice - ideal for inspiration", previewUrl: VOICE_PREVIEW_MAP.Inspirational_girl, gender: "female", category: "motivational" },
  { id: "Deep_Voice_Man", name: "Deep Voice Man", personality: "Powerful, commanding male voice - excellent for serious topics", previewUrl: VOICE_PREVIEW_MAP.Deep_Voice_Man, gender: "male", category: "professional" },
  { id: "Calm_Woman", name: "Calm Woman", personality: "Soothing, composed female voice - perfect for meditation or sensitive topics", previewUrl: VOICE_PREVIEW_MAP.Calm_Woman, gender: "female", category: "calming" },
  { id: "Casual_Guy", name: "Casual Guy", personality: "Relaxed, conversational male voice - great for vlogs and tutorials", previewUrl: VOICE_PREVIEW_MAP.Casual_Guy, gender: "male", category: "marketing" },
  { id: "Lively_Girl", name: "Lively Girl", personality: "Energetic, enthusiastic female voice - ideal for exciting announcements", previewUrl: VOICE_PREVIEW_MAP.Lively_Girl, gender: "female", category: "marketing" },
  { id: "Patient_Man", name: "Patient Man", personality: "Gentle, understanding male voice - perfect for explanations", previewUrl: VOICE_PREVIEW_MAP.Patient_Man, gender: "male", category: "educational" },
  { id: "Young_Knight", name: "Young Knight", personality: "Brave, confident male voice - great for adventure and gaming", previewUrl: VOICE_PREVIEW_MAP.Young_Knight, gender: "male", category: "creative" },
  { id: "Determined_Man", name: "Determined Man", personality: "Strong, resolute male voice - excellent for motivational speeches", previewUrl: VOICE_PREVIEW_MAP.Determined_Man, gender: "male", category: "motivational" },
  { id: "Lovely_Girl", name: "Lovely Girl", personality: "Sweet, charming female voice - ideal for storytelling", previewUrl: VOICE_PREVIEW_MAP.Lovely_Girl, gender: "female", category: "creative" },
  { id: "Decent_Boy", name: "Decent Boy", personality: "Honest, sincere male voice - perfect for testimonials", previewUrl: VOICE_PREVIEW_MAP.Decent_Boy, gender: "male", category: "marketing" },
  { id: "Imposing_Manner", name: "Imposing Manner", personality: "Formal, dignified male voice - great for corporate content", previewUrl: VOICE_PREVIEW_MAP.Imposing_Manner, gender: "male", category: "professional" },
  { id: "Elegant_Man", name: "Elegant Man", personality: "Refined, sophisticated male voice - ideal for luxury content", previewUrl: VOICE_PREVIEW_MAP.Elegant_Man, gender: "male", category: "professional" },
  { id: "Abbess", name: "Abbess", personality: "Spiritual, serene female voice - perfect for meditation", previewUrl: VOICE_PREVIEW_MAP.Abbess, gender: "female", category: "calming" },
  { id: "Sweet_Girl_2", name: "Sweet Girl 2", personality: "Gentle, melodic female voice - excellent for children's content", previewUrl: VOICE_PREVIEW_MAP.Sweet_Girl_2, gender: "female", category: "creative" },
  { id: "Exuberant_Girl", name: "Exuberant Girl", personality: "Joyful, expressive female voice - ideal for celebrations", previewUrl: VOICE_PREVIEW_MAP.Exuberant_Girl, gender: "female", category: "creative" },
];

export const VOICE_CLONE_ID = "MY_VOICE_CLONE";

export const VoiceSelector: React.FC<VoiceSelectorProps> = ({
  value,
  onChange,
  disabled = false,
  showVoiceClone = true,
  compact = false,
  audioSettings: externalAudioSettings,
  onAudioSettingsChange,
}) => {
  const [voiceClone, setVoiceClone] = useState<VoiceCloneResponse | null>(null);
  const [loadingVoiceClone, setLoadingVoiceClone] = useState(false);
  const [playingPreview, setPlayingPreview] = useState<string | null>(null);
  const [showVoiceClonePanel, setShowVoiceClonePanel] = useState(false);
  const [voiceCreated, setVoiceCreated] = useState(false);
  const [redoingClone, setRedoingClone] = useState(false);
  const [selectOpen, setSelectOpen] = useState(false);
  const [tuneModalOpen, setTuneModalOpen] = useState(false);
  const [tuneForVoice, setTuneForVoice] = useState<string | null>(null);
  const [localAudioSettings, setLocalAudioSettings] = useState<VoiceAudioSettings>(
    externalAudioSettings || { ...DEFAULT_AUDIO_SETTINGS }
  );
  const [genderFilter, setGenderFilter] = useState<GenderFilter>("all");
  const [categoryFilter, setCategoryFilter] = useState<CategoryFilter>("all");
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const prevVoiceCloneIdRef = useRef<string | null>(null);

  const fetchVoiceClone = async () => {
    try {
      setLoadingVoiceClone(true);
      const result = await getLatestVoiceClone();
      setVoiceClone(result);
      return result;
    } catch (error) {
      console.error("Failed to fetch voice clone:", error);
      return null;
    } finally {
      setLoadingVoiceClone(false);
    }
  };

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

  const filteredVoices = useMemo(() => {
    const filtered = PREDEFINED_VOICES.filter(v => {
      if (genderFilter !== "all" && v.gender !== genderFilter) return false;
      if (categoryFilter !== "all" && v.category !== categoryFilter) return false;
      return true;
    });
    if (value && value !== VOICE_CLONE_ID && !filtered.some(v => v.id === value)) {
      const selected = PREDEFINED_VOICES.find(v => v.id === value);
      if (selected) filtered.unshift(selected);
    }
    return filtered;
  }, [genderFilter, categoryFilter, value]);

  useEffect(() => {
    if (!showVoiceClone) return;
    fetchVoiceClone();
  }, [showVoiceClone]);

  useEffect(() => {
    if (voiceClone?.success && voiceClone.custom_voice_id) {
      const cloneId = voiceClone.custom_voice_id;
      if (prevVoiceCloneIdRef.current !== cloneId) {
        prevVoiceCloneIdRef.current = cloneId;
        if (!value || value === "Wise_Woman") {
          onChange(cloneId);
        }
      }
    }
  }, [voiceClone]);

  const stopCurrentAudio = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current.onended = null;
      audioRef.current.onerror = null;
      audioRef.current = null;
    }
  }, []);

  const handlePreview = useCallback(async (voice: VoiceOption) => {
    if (!voice.previewUrl) return;

    if (playingPreview === voice.id) {
      stopCurrentAudio();
      setPlayingPreview(null);
      return;
    }

    stopCurrentAudio();
    setPlayingPreview(voice.id);

    // Append auth token for endpoints that require it (e.g. /api/assets/)
    let previewUrl = voice.previewUrl;
    // Convert relative URLs to absolute (pointing to backend, not Vercel)
    if (previewUrl.startsWith('/')) {
      previewUrl = `${getApiUrl()}${previewUrl}`;
    }
    try {
      const tokenGetter = getAuthTokenGetter();
      if (tokenGetter) {
        const token = await tokenGetter();
        if (token && previewUrl.includes('/api/')) {
          const separator = previewUrl.includes('?') ? '&' : '?';
          previewUrl = `${previewUrl}${separator}token=${encodeURIComponent(token)}`;
        }
      }
    } catch (e) {
      // Token retrieval failed — try URL without token
    }

    const audio = new Audio(previewUrl);
    audioRef.current = audio;

    audio.onerror = () => {
      console.error("Failed to load voice preview audio:", voice.previewUrl);
      if (audioRef.current === audio) {
        audioRef.current = null;
      }
      setPlayingPreview(null);
    };

    audio.onended = () => {
      if (audioRef.current === audio) {
        audioRef.current = null;
      }
      setPlayingPreview(null);
    };

    audio.play().catch((err) => {
      console.error("Failed to play voice preview:", err);
      if (audioRef.current === audio) {
        audioRef.current = null;
      }
      setPlayingPreview(null);
    });
  }, [playingPreview, stopCurrentAudio]);

  useEffect(() => {
    return () => {
      stopCurrentAudio();
    };
  }, [stopCurrentAudio]);

  const handleChange = (newValue: string) => {
    if (newValue === VOICE_CLONE_ID && voiceClone?.success) {
      onChange(voiceClone.custom_voice_id || VOICE_CLONE_ID);
    } else {
      onChange(newValue);
    }
  };

  const isVoiceCloneSelected = value === VOICE_CLONE_ID || 
    (voiceClone?.success && voiceClone.custom_voice_id && value === voiceClone.custom_voice_id);

  const selectValue = useMemo(() => {
    if (isVoiceCloneSelected) return VOICE_CLONE_ID;
    if (value && voiceOptions.some(v => v.id === value)) return value;
    return voiceOptions.length > 0 ? voiceOptions[0].id : "";
  }, [value, isVoiceCloneSelected, voiceOptions]);

  const selectedVoice = useMemo(() => {
    if (isVoiceCloneSelected) {
      return voiceOptions.find(v => v.id === VOICE_CLONE_ID);
    }
    return voiceOptions.find(v => v.id === value) || voiceOptions[0];
  }, [value, isVoiceCloneSelected, voiceOptions]);

  const handleVoiceSet = useCallback(() => {
    setVoiceCreated(true);
  }, []);

  const handleRedoClone = useCallback(() => {
    setSelectOpen(false);
    setTimeout(() => {
      setRedoingClone(true);
      setShowVoiceClonePanel(true);
      setVoiceCreated(false);
    }, 150);
  }, []);

  const handleDoneWithVoice = useCallback(() => {
    fetchVoiceClone();
    setShowVoiceClonePanel(false);
    setVoiceCreated(false);
    setRedoingClone(false);
  }, []);

  const handleCancelRedo = useCallback(() => {
    setShowVoiceClonePanel(false);
    setRedoingClone(false);
    setVoiceCreated(false);
  }, []);

  const handleTogglePanel = useCallback(() => {
    if (showVoiceClonePanel) {
      setShowVoiceClonePanel(false);
      setVoiceCreated(false);
      setRedoingClone(false);
    } else {
      setShowVoiceClonePanel(true);
      setVoiceCreated(false);
      setRedoingClone(false);
    }
  }, [showVoiceClonePanel]);

  const isPreviewing = playingPreview !== null;

  useEffect(() => {
    if (externalAudioSettings) {
      setLocalAudioSettings(externalAudioSettings);
    }
  }, [externalAudioSettings]);

  const hasCustomSettings = externalAudioSettings && (
    externalAudioSettings.speed !== 1.0 ||
    externalAudioSettings.volume !== 1.0 ||
    externalAudioSettings.pitch !== 0 ||
    externalAudioSettings.emotion !== "neutral"
  );

  const handleApplyTune = useCallback(() => {
    if (onAudioSettingsChange) {
      onAudioSettingsChange(localAudioSettings);
    }
    setTuneModalOpen(false);
  }, [localAudioSettings, onAudioSettingsChange]);

  const handleOpenTune = useCallback((voiceId: string) => {
    setTuneForVoice(voiceId);
    setLocalAudioSettings(externalAudioSettings || { ...DEFAULT_AUDIO_SETTINGS });
    setTuneModalOpen(true);
  }, [externalAudioSettings]);

  // Gradient style for Tune icon button
  const tuneButtonSx = useMemo(() => ({
    textTransform: 'none' as const,
    fontSize: "0.68rem",
    fontWeight: 600,
    minWidth: 60,
    py: 0.3,
    borderRadius: 1.5,
    background: "linear-gradient(135deg, rgba(249, 115, 22, 0.08) 0%, rgba(236, 72, 153, 0.08) 100%)",
    color: "#e17055",
    borderColor: "rgba(249, 115, 22, 0.3)",
    "&:hover": {
      background: "linear-gradient(135deg, rgba(249, 115, 22, 0.18) 0%, rgba(236, 72, 153, 0.18) 100%)",
      borderColor: "#f97316",
    },
  }), []);

  if (compact) {
    return (
      <FormControl fullWidth size="small">
        <InputLabel>Voice</InputLabel>
        <Select
          value={selectValue}
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
    <Box
      sx={{
        p: 3,
        borderRadius: 3,
        background: "#ffffff",
        border: "1px solid rgba(102, 126, 234, 0.15)",
        boxShadow: "0 4px 20px rgba(102, 126, 234, 0.08)",
        position: "relative",
        overflow: "hidden",
        "&::before": {
          content: '""',
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          height: "3px",
          background: "linear-gradient(90deg, #667eea 0%, #764ba2 100%)",
        },
      }}
    >
      <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
        <Box
          sx={{
            width: 24,
            height: 24,
            borderRadius: "50%",
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            boxShadow: "0 2px 8px rgba(102, 126, 234, 0.25)",
          }}
        >
          <Typography sx={{ color: "#fff", fontSize: "0.75rem", fontWeight: 700 }}>4</Typography>
        </Box>
        <Box
          sx={{
            width: 32,
            height: 32,
            borderRadius: 1.5,
            background: "linear-gradient(135deg, rgba(102, 126, 234, 0.12) 0%, rgba(118, 75, 162, 0.12) 100%)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            boxShadow: "0 2px 8px rgba(102, 126, 234, 0.15)",
          }}
        >
          <Mic fontSize="small" sx={{ color: "#667eea" }} />
        </Box>
        <Typography variant="subtitle1" sx={{ fontWeight: 700, color: "#0f172a", fontSize: "1rem" }}>
          Voice Selection
        </Typography>
        {selectedVoice && (
          <Chip
            icon={<Mic sx={{ fontSize: "12px !important" }} />}
            label={`Active: ${selectedVoice.isCustom ? "My Voice Clone" : selectedVoice.name}`}
            size="small"
            sx={{
              background: selectedVoice.isCustom
                ? "linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(5, 150, 105, 0.12) 100%)"
                : "linear-gradient(135deg, rgba(102, 126, 234, 0.12) 0%, rgba(118, 75, 162, 0.12) 100%)",
              color: selectedVoice.isCustom ? "#10b981" : "#6366f1",
              border: `1px solid ${selectedVoice.isCustom ? "rgba(16, 185, 129, 0.25)" : "rgba(99, 102, 241, 0.2)"}`,
              fontWeight: 600,
              fontSize: "0.7rem",
              height: 22,
              "& .MuiChip-icon": { color: selectedVoice.isCustom ? "#10b981" : "#6366f1" },
            }}
          />
        )}
        <Tooltip title="Fine-tune voice speed, pitch, volume & emotion" arrow>
          <IconButton
            size="small"
            onClick={() => {
              setLocalAudioSettings(externalAudioSettings || { ...DEFAULT_AUDIO_SETTINGS });
              setTuneForVoice(null);
              setTuneModalOpen(true);
            }}
            sx={{
              color: hasCustomSettings ? "#667eea" : "#94a3b8",
              background: hasCustomSettings ? "rgba(102, 126, 234, 0.1)" : "transparent",
              "&:hover": { color: "#667eea", background: "rgba(102, 126, 234, 0.08)" },
            }}
          >
            <Tune fontSize="small" />
          </IconButton>
        </Tooltip>
        <Tooltip title="Choose a system voice or your custom cloned voice. Click the play button to hear a preview." arrow>
          <IconButton size="small" sx={{ color: "#94a3b8", "&:hover": { color: "#667eea" } }}>
            <HelpOutline fontSize="small" />
          </IconButton>
        </Tooltip>
        {showVoiceClone && loadingVoiceClone && (
          <CircularProgress size={16} sx={{ ml: 1, color: "#667eea" }} />
        )}
      </Stack>

      <FormControl fullWidth>
        <Select
          open={selectOpen}
          onOpen={() => setSelectOpen(true)}
          onClose={() => setSelectOpen(false)}
          value={selectValue}
          onChange={(e) => {
            handleChange(e.target.value);
            setSelectOpen(false);
          }}
          disabled={disabled}
          renderValue={(selected) => {
            const voice = voiceOptions.find(v => 
              v.id === selected || 
              (selected === VOICE_CLONE_ID && v.isCustom)
            );
            return (
              <Stack direction="row" spacing={1} alignItems="center">
                <VolumeUp fontSize="small" sx={{ color: voice?.isCustom ? "#667eea" : "#64748b" }} />
                <Typography sx={{ fontWeight: 600, color: "#1e293b" }}>{voice?.name}</Typography>
                {voice?.isCustom && (
                  <Chip 
                    label="Cloned" 
                    size="small" 
                    sx={{ 
                      bgcolor: alpha("#667eea", 0.1), 
                      color: "#667eea",
                      height: 20,
                      fontSize: "0.7rem",
                      fontWeight: 600,
                    }} 
                  />
                )}
              </Stack>
            );
          }}
          sx={{
            color: "#1e293b",
            "& .MuiOutlinedInput-notchedOutline": {
              border: "2px solid rgba(102, 126, 234, 0.2)",
            },
            "&:hover .MuiOutlinedInput-notchedOutline": {
              borderColor: "rgba(102, 126, 234, 0.4)",
            },
            "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
              borderColor: "#667eea",
            },
          }}
          MenuProps={{
            PaperProps: {
              sx: {
                maxHeight: 500,
                bgcolor: "#ffffff",
                boxShadow: "0 8px 32px rgba(15, 23, 42, 0.12)",
                border: "2px solid rgba(102, 126, 234, 0.35)",
                borderRadius: 2.5,
                "& .MuiMenuItem-root": {
                  bgcolor: "#ffffff",
                  color: "#1e293b",
                  "&:hover": {
                    bgcolor: "rgba(102, 126, 234, 0.06)",
                  },
                  "&.Mui-selected": {
                    bgcolor: "rgba(102, 126, 234, 0.1)",
                    "&:hover": {
                      bgcolor: "rgba(102, 126, 234, 0.16)",
                    },
                  },
                },
              },
            },
            MenuListProps: {
              sx: {
                bgcolor: "#ffffff",
              },
            },
          }}
        >
          {showVoiceClone && voiceClone?.success && voiceClone.custom_voice_id && (
            <MenuItem value={VOICE_CLONE_ID} sx={{ 
              borderBottom: '1px solid rgba(102, 126, 234, 0.1)', 
              py: 1.5,
              bgcolor: isVoiceCloneSelected ? "rgba(102, 126, 234, 0.06)" : "#ffffff",
            }}>
              <ListItemIcon sx={{ minWidth: 40 }}>
                <AutoAwesome sx={{ color: "#667eea", fontSize: "1.1rem" }} />
              </ListItemIcon>
              <ListItemText 
                primary={
                  <Stack direction="row" spacing={1} alignItems="center" justifyContent="space-between" sx={{ width: "100%" }}>
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
                          fontWeight: 600,
                          '& .MuiChip-icon': { color: "#10b981" }
                        }} 
                      />
                    </Stack>
                    <Stack direction="row" spacing={0.75}>
                      {voiceClone.preview_audio_url && (
                        <Button
                          size="small"
                          variant={playingPreview === VOICE_CLONE_ID ? "contained" : "outlined"}
                          startIcon={playingPreview === VOICE_CLONE_ID ? <Pause /> : <PlayArrow />}
                          onClick={(e) => {
                            e.stopPropagation();
                            handlePreview({ 
                              id: VOICE_CLONE_ID, 
                              name: voiceClone.voice_name || "My Voice Clone",
                              previewUrl: voiceClone.preview_audio_url 
                            });
                          }}
                          disabled={isPreviewing && playingPreview !== VOICE_CLONE_ID}
                          sx={{ 
                            textTransform: 'none',
                            fontSize: "0.7rem",
                            fontWeight: 600,
                            minWidth: 82,
                            py: 0.3,
                            borderRadius: 1.5,
                            ...(playingPreview === VOICE_CLONE_ID ? {
                              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                              color: "#fff",
                              boxShadow: "0 2px 8px rgba(102, 126, 234, 0.35)",
                              "&:hover": {
                                background: "linear-gradient(135deg, #5a6fd6 0%, #6a4195 100%)",
                              },
                            } : {
                              background: "linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%)",
                              color: "#667eea",
                              borderColor: "rgba(102, 126, 234, 0.35)",
                              "&:hover": {
                                background: "linear-gradient(135deg, rgba(102, 126, 234, 0.16) 0%, rgba(118, 75, 162, 0.16) 100%)",
                                borderColor: "#667eea",
                              },
                            }),
                          }}
                        >
                          {playingPreview === VOICE_CLONE_ID ? "Stop" : "Preview"}
                        </Button>
                      )}
                      <Button
                        size="small"
                        variant="outlined"
                        startIcon={<RestartAlt sx={{ fontSize: "0.85rem" }} />}
                        onClick={handleRedoClone}
                        sx={{
                          textTransform: 'none',
                          fontSize: "0.68rem",
                          fontWeight: 600,
                          minWidth: 70,
                          py: 0.3,
                          borderRadius: 1.5,
                          background: "linear-gradient(135deg, rgba(249, 115, 22, 0.06) 0%, rgba(234, 88, 12, 0.06) 100%)",
                          color: "#f97316",
                          borderColor: "rgba(249, 115, 22, 0.3)",
                          "&:hover": {
                            background: "linear-gradient(135deg, rgba(249, 115, 22, 0.14) 0%, rgba(234, 88, 12, 0.14) 100%)",
                            borderColor: "#f97316",
                          },
                        }}
                      >
                        Redo
                      </Button>
                    </Stack>
                  </Stack>
                }
                secondary={
                  <Typography variant="caption" sx={{ color: "#64748b", fontSize: "0.72rem", lineHeight: 1.4 }}>
                    Your own voice - cloned from audio sample
                  </Typography>
                }
              />
            </MenuItem>
          )}

          {/* Filter row inside dropdown */}
          <Box
            onClick={(e) => e.stopPropagation()}
            sx={{
              px: 1.5,
              pt: 1.5,
              pb: 0.5,
              borderBottom: "1px solid rgba(102, 126, 234, 0.1)",
              position: "sticky",
              top: 0,
              bgcolor: "#ffffff",
              zIndex: 2,
            }}
          >
            <Stack direction="row" spacing={0.5} alignItems="center" useFlexGap flexWrap="wrap" sx={{ mb: 0.75 }}>
              <Typography variant="caption" sx={{ fontWeight: 700, color: "#94a3b8", fontSize: "0.6rem", textTransform: "uppercase", letterSpacing: "0.08em", mr: 0.25 }}>
                Gender
              </Typography>
              {([["all", "All"], ["male", "♂ M"], ["female", "♀ F"]] as const).map(([val, label]) => (
                <Chip
                  key={val}
                  label={label}
                  size="small"
                  onClick={() => setGenderFilter(val as GenderFilter)}
                  variant={genderFilter === val ? "filled" : "outlined"}
                  sx={{
                    height: 22,
                    fontSize: "0.65rem",
                    fontWeight: genderFilter === val ? 700 : 500,
                    background: genderFilter === val
                      ? "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
                      : "rgba(248, 250, 252, 1)",
                    color: genderFilter === val ? "#ffffff" : "#64748b",
                    border: genderFilter === val
                      ? "1px solid rgba(102, 126, 234, 0.5)"
                      : "1px solid rgba(148, 163, 184, 0.3)",
                    boxShadow: genderFilter === val ? "0 2px 8px rgba(102, 126, 234, 0.3)" : "none",
                    cursor: "pointer",
                    "& .MuiChip-label": {
                      color: "inherit",
                    },
                    "&:hover": {
                      background: genderFilter === val
                        ? "linear-gradient(135deg, #5a6fd6 0%, #6a4195 100%)"
                        : "rgba(102, 126, 234, 0.08)",
                      border: genderFilter === val ? "1px solid rgba(102, 126, 234, 0.6)" : "1px solid rgba(102, 126, 234, 0.3)",
                    },
                    transition: "all 0.15s ease",
                  }}
                />
              ))}
            </Stack>
            <Stack direction="row" spacing={0.5} alignItems="center" useFlexGap flexWrap="wrap">
              <Typography variant="caption" sx={{ fontWeight: 700, color: "#94a3b8", fontSize: "0.6rem", textTransform: "uppercase", letterSpacing: "0.08em", mr: 0.25 }}>
                Use Case
              </Typography>
              {CATEGORY_OPTIONS.map((cat) => (
                <Chip
                  key={cat.value}
                  label={cat.label}
                  size="small"
                  onClick={() => setCategoryFilter(cat.value)}
                  variant={categoryFilter === cat.value ? "filled" : "outlined"}
                  sx={{
                    height: 22,
                    fontSize: "0.65rem",
                    fontWeight: categoryFilter === cat.value ? 700 : 500,
                    background: categoryFilter === cat.value
                      ? "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
                      : "rgba(248, 250, 252, 1)",
                    color: categoryFilter === cat.value ? "#ffffff" : "#64748b",
                    border: categoryFilter === cat.value
                      ? "1px solid rgba(102, 126, 234, 0.5)"
                      : "1px solid rgba(148, 163, 184, 0.3)",
                    boxShadow: categoryFilter === cat.value ? "0 2px 8px rgba(102, 126, 234, 0.3)" : "none",
                    cursor: "pointer",
                    "& .MuiChip-label": {
                      color: "inherit",
                    },
                    "&:hover": {
                      background: categoryFilter === cat.value
                        ? "linear-gradient(135deg, #5a6fd6 0%, #6a4195 100%)"
                        : "rgba(102, 126, 234, 0.08)",
                      border: categoryFilter === cat.value ? "1px solid rgba(102, 126, 234, 0.6)" : "1px solid rgba(102, 126, 234, 0.3)",
                    },
                    transition: "all 0.15s ease",
                  }}
                />
              ))}
            </Stack>
          </Box>

          <MenuItem disabled sx={{ 
            py: 0.25,
            bgcolor: "#f8fafc !important",
            "&.MuiMenuItem-root": { bgcolor: "#f8fafc !important" },
          }}>
            <Typography variant="caption" sx={{ fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em", color: "#94a3b8", fontSize: "0.65rem" }}>
              {filteredVoices.length} voice{filteredVoices.length !== 1 ? "s" : ""}
            </Typography>
          </MenuItem>

          {filteredVoices.map((voice) => {
            const isPlaying = playingPreview === voice.id;
            const isDisabled = isPreviewing && !isPlaying;
            const personalityShort = voice.personality?.split(' - ')[0] || '';
            const personalityBest = voice.personality?.split(' - ')[1] || '';

            return (
              <MenuItem 
                key={voice.id} 
                value={voice.id} 
                sx={{ 
                  py: 1,
                  opacity: isDisabled ? 0.45 : 1,
                  transition: "opacity 0.2s ease",
                  pointerEvents: isDisabled ? "none" : "auto",
                }}
              >
                <ListItemText 
                  primary={
                    <Box sx={{ width: "100%" }}>
                      <Stack direction="row" spacing={0.5} alignItems="center" sx={{ mb: 0.25 }}>
                        <Typography sx={{ fontWeight: 500, fontSize: "0.85rem", lineHeight: 1.3 }}>{voice.name}</Typography>
                        {voice.gender && (
                          <Box
                            component="span"
                            sx={{
                              display: "inline-flex",
                              alignItems: "center",
                              justifyContent: "center",
                              minWidth: 16,
                              height: 16,
                              px: 0.5,
                              borderRadius: "3px",
                              fontSize: "0.55rem",
                              fontWeight: 700,
                              lineHeight: 1,
                              bgcolor: voice.gender === "male" ? "rgba(59, 130, 246, 0.12)" : "rgba(236, 72, 153, 0.12)",
                              color: voice.gender === "male" ? "#3b82f6" : "#ec4899",
                              border: `1px solid ${voice.gender === "male" ? "rgba(59, 130, 246, 0.25)" : "rgba(236, 72, 153, 0.25)"}`,
                            }}
                          >
                            {voice.gender === "male" ? "M" : "F"}
                          </Box>
                        )}
                        {voice.category && (
                          <Typography component="span" variant="caption" sx={{ color: "#94a3b8", fontSize: "0.6rem" }}>
                            · {voice.category}
                          </Typography>
                        )}
                      </Stack>
                      {personalityBest ? (
                        <Typography variant="caption" sx={{ color: "#667eea", fontSize: "0.65rem", fontWeight: 500, lineHeight: 1.3, display: "block" }}>
                          {personalityBest.toLowerCase()}
                        </Typography>
                      ) : personalityShort ? (
                        <Typography variant="caption" sx={{ color: "#94a3b8", fontSize: "0.65rem", lineHeight: 1.3, display: "block" }}>
                          {personalityShort}
                        </Typography>
                      ) : null}
                    </Box>
                  }
                />
                <Stack direction="row" spacing={0.5} sx={{ ml: 1, flexShrink: 0 }}>
                  {voice.previewUrl && (
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        handlePreview(voice);
                      }}
                      disabled={isDisabled}
                      sx={{
                        width: 28,
                        height: 28,
                        borderRadius: "6px",
                        ...(isPlaying ? {
                          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                          color: "#fff",
                          boxShadow: "0 2px 6px rgba(102, 126, 234, 0.35)",
                        } : {
                          background: "linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%)",
                          color: "#667eea",
                          border: "1px solid rgba(102, 126, 234, 0.25)",
                        }),
                      }}
                    >
                      {isPlaying ? <Pause sx={{ fontSize: "0.85rem" }} /> : <PlayArrow sx={{ fontSize: "0.85rem" }} />}
                    </IconButton>
                  )}
                  <IconButton
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleOpenTune(voice.id);
                    }}
                    sx={{
                      width: 28,
                      height: 28,
                      borderRadius: "6px",
                      background: "linear-gradient(135deg, rgba(249, 115, 22, 0.08) 0%, rgba(236, 72, 153, 0.08) 100%)",
                      color: "#e17055",
                      border: "1px solid rgba(249, 115, 22, 0.2)",
                      "&:hover": {
                        background: "linear-gradient(135deg, rgba(249, 115, 22, 0.18) 0%, rgba(236, 72, 153, 0.18) 100%)",
                        borderColor: "rgba(249, 115, 22, 0.5)",
                      },
                    }}
                  >
                    <Tune sx={{ fontSize: "0.85rem" }} />
                  </IconButton>
                </Stack>
              </MenuItem>
            );
          })}

          {filteredVoices.length === 0 && (
            <MenuItem disabled sx={{ py: 2 }}>
              <ListItemText>
                <Typography variant="body2" sx={{ color: "#94a3b8", textAlign: "center" }}>
                  No voices match the selected filters
                </Typography>
              </ListItemText>
            </MenuItem>
          )}
        </Select>
      </FormControl>

      {selectedVoice?.personality && (
        <Box sx={{ 
          mt: 1.5, 
          p: 1.5, 
          borderRadius: 2,
          background: playingPreview 
            ? "linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%)"
            : "rgba(248, 250, 252, 0.8)",
          border: playingPreview 
            ? "1px solid rgba(102, 126, 234, 0.2)" 
            : "1px solid rgba(102, 126, 234, 0.1)",
          transition: "all 0.3s ease",
        }}>
          <Stack direction="row" spacing={1} alignItems="center">
            {playingPreview && (
              <Box sx={{ 
                width: 8, height: 8, borderRadius: "50%", bgcolor: "#667eea",
                animation: "pulse 1.5s ease-in-out infinite",
                "@keyframes pulse": {
                  "0%": { opacity: 1, transform: "scale(1)" },
                  "50%": { opacity: 0.5, transform: "scale(1.2)" },
                  "100%": { opacity: 1, transform: "scale(1)" },
                },
              }} />
            )}
            <Box sx={{ flex: 1 }}>
              <Typography variant="body2" sx={{ color: "#0f172a", fontSize: "0.8125rem", fontWeight: 600, lineHeight: 1.4 }}>
                {selectedVoice.isCustom ? "My Voice Clone" : selectedVoice.name}
              </Typography>
              <Typography variant="caption" sx={{ color: playingPreview ? "#4f46e5" : "#64748b", fontSize: "0.75rem", lineHeight: 1.4, fontWeight: playingPreview ? 500 : 400, display: "block" }}>
                {selectedVoice.personality}
              </Typography>
            </Box>
            {playingPreview && (
              <Typography variant="caption" sx={{ color: "#667eea", fontWeight: 600, fontSize: "0.7rem", whiteSpace: "nowrap" }}>
                Playing...
              </Typography>
            )}
          </Stack>
        </Box>
      )}

      {(showVoiceClone && !voiceClone?.success) || redoingClone ? (
        <Box sx={{ mt: 2 }}>
          <Button
            onClick={handleTogglePanel}
            startIcon={showVoiceClonePanel ? <ExpandLess /> : redoingClone ? <RestartAlt /> : <AutoAwesome />}
            endIcon={showVoiceClonePanel ? <ExpandLess /> : <ExpandMore />}
            sx={{
              py: 2,
              px: 3,
              width: "100%",
              background: showVoiceClonePanel 
                ? "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
                : "linear-gradient(135deg, #8B5CF6 0%, #EC4899 50%, #F59E0B 100%)",
              border: showVoiceClonePanel 
                ? "1px solid rgba(102, 126, 234, 0.5)"
                : "none",
              borderRadius: 2.5,
              color: "#fff",
              fontWeight: 700,
              textTransform: "none",
              fontSize: "0.95rem",
              boxShadow: showVoiceClonePanel 
                ? "0 4px 15px rgba(102, 126, 234, 0.35)"
                : "0 4px 20px rgba(139, 92, 246, 0.4), 0 0 30px rgba(236, 72, 153, 0.2)",
              "&:hover": {
                background: "linear-gradient(135deg, #7C3AED 0%, #9333EA 50%, #D97706 100%)",
                boxShadow: "0 6px 25px rgba(139, 92, 246, 0.5)",
                transform: "translateY(-1px)",
              },
              transition: "all 0.3s ease",
            }}
          >
            {redoingClone ? "Redo Voice Clone" : showVoiceClonePanel ? "Hide Voice Cloning" : "Create Your Voice Clone ✨"}
          </Button>

          <Collapse in={showVoiceClonePanel}>
            <Box
              sx={{
                mt: 2,
                p: 2,
                borderRadius: 2,
                background: "linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)",
                border: "1px solid rgba(102, 126, 234, 0.2)",
                boxShadow: "inset 0 1px 3px rgba(0,0,0,0.05)",
              }}
            >
              <VoiceAvatarPlaceholder
                domainName="Podcast"
                onVoiceSet={handleVoiceSet}
              />

              {voiceCreated && (
                <Box
                  sx={{
                    mt: 2,
                    p: 2,
                    borderRadius: 2,
                    background: "linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%)",
                    border: "1px solid rgba(16, 185, 129, 0.3)",
                  }}
                >
                  <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1 }}>
                    <CheckCircle sx={{ color: "#10b981", fontSize: "1.25rem" }} />
                    <Typography variant="subtitle2" sx={{ color: "#10b981", fontWeight: 700 }}>
                      {redoingClone ? "Voice Clone Updated!" : "Voice Clone Created Successfully!"}
                    </Typography>
                  </Stack>

                  <Typography variant="body2" sx={{ color: "#475569", mb: 1.5, fontSize: "0.875rem" }}>
                    {redoingClone ? "Your voice clone has been updated and will be used for your podcast." : "Your custom voice clone is ready and will be used for your podcast."}
                  </Typography>

                  <Stack direction="row" spacing={1.5} justifyContent="flex-end">
                    <Button
                      onClick={handleCancelRedo}
                      sx={{
                        color: "#64748b",
                        "&:hover": { color: "#1e293b", background: "rgba(0,0,0,0.04)" },
                      }}
                    >
                      Cancel
                    </Button>
                    <Button
                      variant="contained"
                      onClick={handleDoneWithVoice}
                      sx={{
                        background: "linear-gradient(135deg, #10b981 0%, #059669 100%)",
                        color: "#fff",
                        fontWeight: 600,
                        textTransform: "none",
                        px: 3,
                        boxShadow: "0 4px 12px rgba(16, 185, 129, 0.3)",
                        "&:hover": {
                          background: "linear-gradient(135deg, #059669 0%, #047857 100%)",
                        },
                      }}
                    >
                      Done
                    </Button>
                  </Stack>
                </Box>
              )}
            </Box>
          </Collapse>
        </Box>
      ) : null}

      {/* Voice Fine-tune Modal */}
      <Dialog
        open={tuneModalOpen}
        onClose={() => setTuneModalOpen(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 3,
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            color: "white",
          },
        }}
      >
        <DialogTitle>
          <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Stack direction="row" spacing={1} alignItems="center">
              <Tune sx={{ fontSize: "1.25rem" }} />
              <Typography variant="h6" sx={{ fontWeight: 700 }}>
                Fine-tune Voice
              </Typography>
            </Stack>
            <IconButton onClick={() => setTuneModalOpen(false)} size="small" sx={{ color: "rgba(255,255,255,0.7)" }}>
              <Close />
            </IconButton>
          </Stack>
          {tuneForVoice && (
            <Typography variant="body2" sx={{ opacity: 0.8, mt: 0.5 }}>
              Adjusting settings for: <strong>{voiceOptions.find(v => v.id === tuneForVoice)?.name || "selected voice"}</strong>
            </Typography>
          )}
          {!tuneForVoice && (
            <Typography variant="body2" sx={{ opacity: 0.7, mt: 0.5 }}>
              Adjust speed, pitch, volume and emotion for your selected voice.
            </Typography>
          )}
        </DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 1 }}>
            <Box>
              <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>Speaking Speed</Typography>
                <Chip label={localAudioSettings.speed.toFixed(2)} size="small" sx={{ bgcolor: "rgba(255,255,255,0.15)", color: "white", fontWeight: 600, fontSize: "0.7rem", height: 20 }} />
              </Stack>
              <Slider
                value={localAudioSettings.speed}
                min={0.5}
                max={2.0}
                step={0.05}
                onChange={(_, v) => setLocalAudioSettings(s => ({ ...s, speed: v as number }))}
                sx={{ color: "#4ade80" }}
              />
              <Typography variant="caption" sx={{ opacity: 0.7 }}>0.5 = Slow &bull; 1.0 = Normal &bull; 2.0 = Fast</Typography>
            </Box>
            <Box>
              <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>Volume</Typography>
                <Chip label={localAudioSettings.volume.toFixed(1)} size="small" sx={{ bgcolor: "rgba(255,255,255,0.15)", color: "white", fontWeight: 600, fontSize: "0.7rem", height: 20 }} />
              </Stack>
              <Slider
                value={localAudioSettings.volume}
                min={0.1}
                max={10.0}
                step={0.1}
                onChange={(_, v) => setLocalAudioSettings(s => ({ ...s, volume: v as number }))}
                sx={{ color: "#fbbf24" }}
              />
              <Typography variant="caption" sx={{ opacity: 0.7 }}>0.1 = Very soft &bull; 1.0 = Normal &bull; 10.0 = Very loud</Typography>
            </Box>
            <Box>
              <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>Pitch</Typography>
                <Chip label={localAudioSettings.pitch > 0 ? `+${localAudioSettings.pitch}` : localAudioSettings.pitch} size="small" sx={{ bgcolor: "rgba(255,255,255,0.15)", color: "white", fontWeight: 600, fontSize: "0.7rem", height: 20 }} />
              </Stack>
              <Slider
                value={localAudioSettings.pitch}
                min={-12}
                max={12}
                step={0.5}
                onChange={(_, v) => setLocalAudioSettings(s => ({ ...s, pitch: v as number }))}
                sx={{ color: "#f87171" }}
              />
              <Typography variant="caption" sx={{ opacity: 0.7 }}>-12 = Very deep &bull; 0 = Normal &bull; +12 = Very high</Typography>
            </Box>
            <Box>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>Emotion</Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                {EMOTION_OPTIONS.map((em) => (
                  <Chip
                    key={em}
                    label={em.charAt(0).toUpperCase() + em.slice(1)}
                    size="small"
                    onClick={() => setLocalAudioSettings(s => ({ ...s, emotion: em }))}
                    sx={{
                      bgcolor: localAudioSettings.emotion === em ? "rgba(255,255,255,0.25)" : "rgba(255,255,255,0.08)",
                      color: "white",
                      fontWeight: localAudioSettings.emotion === em ? 700 : 400,
                      border: localAudioSettings.emotion === em ? "1px solid rgba(255,255,255,0.5)" : "1px solid rgba(255,255,255,0.1)",
                      cursor: "pointer",
                      "&:hover": { bgcolor: "rgba(255,255,255,0.2)" },
                    }}
                  />
                ))}
              </Stack>
            </Box>
          </Stack>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button
            onClick={() => {
              setLocalAudioSettings({ ...DEFAULT_AUDIO_SETTINGS });
              if (onAudioSettingsChange) onAudioSettingsChange({ ...DEFAULT_AUDIO_SETTINGS });
              setTuneModalOpen(false);
            }}
            sx={{ color: "rgba(255,255,255,0.7)" }}
          >
            Reset to Defaults
          </Button>
          <Button
            onClick={() => setTuneModalOpen(false)}
            sx={{ color: "rgba(255,255,255,0.7)" }}
          >
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleApplyTune}
            startIcon={<Tune sx={{ fontSize: "1rem" }} />}
            sx={{
              bgcolor: "#4ade80",
              color: "#0f172a",
              fontWeight: 700,
              "&:hover": { bgcolor: "#22c55e" },
            }}
          >
            Apply Settings
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default VoiceSelector;