import React, { useState, useEffect, useMemo, useCallback } from "react";
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
  FormControlLabel,
  Checkbox,
  Divider,
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
} from "@mui/icons-material";
import { getLatestVoiceClone, VoiceCloneResponse } from "../../api/brandAssets";
import { VoiceAvatarPlaceholder } from "../OnboardingWizard/PersonalizationStep/components/VoiceAvatarPlaceholder";

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
  const [showVoiceClonePanel, setShowVoiceClonePanel] = useState(false);
  const [voiceCreated, setVoiceCreated] = useState(false);
  const [useCreatedVoice, setUseCreatedVoice] = useState(true);

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

  const selectedVoice = useMemo(() => {
    if (value === VOICE_CLONE_ID && voiceClone?.success) {
      return voiceOptions.find(v => v.id === VOICE_CLONE_ID);
    }
    return voiceOptions.find(v => v.id === value) || voiceOptions[0];
  }, [value, voiceOptions, voiceClone]);

  useEffect(() => {
    if (!showVoiceClone) return;
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

  const handleVoiceSet = useCallback(() => {
    setVoiceCreated(true);
    setUseCreatedVoice(true);
  }, []);

  const handleDoneWithVoice = useCallback(() => {
    if (useCreatedVoice) {
      fetchVoiceClone();
    }
    setShowVoiceClonePanel(false);
    setVoiceCreated(false);
  }, [useCreatedVoice]);

  const handleTogglePanel = useCallback(() => {
    if (showVoiceClonePanel) {
      setShowVoiceClonePanel(false);
      setVoiceCreated(false);
    } else {
      setShowVoiceClonePanel(true);
      setVoiceCreated(false);
      setUseCreatedVoice(true);
    }
  }, [showVoiceClonePanel]);

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
        <Tooltip title="Choose a system voice or your custom cloned voice" arrow>
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
                <Mic fontSize="small" sx={{ color: voice?.isCustom ? "#667eea" : "#64748b" }} />
                <Typography sx={{ fontWeight: 500 }}>{voice?.name}</Typography>
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
            "& .MuiOutlinedInput-root": {
              backgroundColor: "#f8fafc",
              border: "2px solid rgba(102, 126, 234, 0.2)",
              borderRadius: 2,
              transition: "all 0.2s ease",
              "&:hover": {
                backgroundColor: "#ffffff",
                borderColor: "rgba(102, 126, 234, 0.4)",
                boxShadow: "0 2px 8px rgba(102, 126, 234, 0.1)",
              },
              "&.Mui-focused": {
                backgroundColor: "#ffffff",
                borderColor: "#667eea",
                boxShadow: "0 0 0 4px rgba(102, 126, 234, 0.1)",
              },
            },
          }}
          MenuProps={{
            PaperProps: {
              sx: {
                maxHeight: 400,
                boxShadow: "0 8px 24px rgba(0,0,0,0.12)",
                border: "1px solid rgba(102, 126, 234, 0.15)",
                borderRadius: 2,
              },
            },
          }}
        >
          {showVoiceClone && voiceClone?.success && voiceClone.custom_voice_id && (
            <MenuItem value={VOICE_CLONE_ID} sx={{ borderBottom: '1px solid rgba(0,0,0,0.1)', py: 1.5 }}>
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
                        fontWeight: 600,
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
                      sx={{ mt: 0.5, textTransform: 'none', color: "#667eea" }}
                    >
                      {playingPreview === VOICE_CLONE_ID ? "Stop" : "Preview"}
                    </Button>
                  )
                }
              />
            </MenuItem>
          )}
          
          <MenuItem disabled sx={{ opacity: 0.6, py: 1 }}>
            <Typography variant="caption" sx={{ fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em" }}>System Voices</Typography>
          </MenuItem>
          
          {voiceOptions.filter(v => !v.isCustom).map((voice) => (
            <MenuItem key={voice.id} value={voice.id} sx={{ py: 1.5 }}>
              <ListItemIcon>
                <Mic fontSize="small" sx={{ color: "#64748b" }} />
              </ListItemIcon>
              <ListItemText 
                primary={<Typography sx={{ fontWeight: 500 }}>{voice.name}</Typography>} 
                secondary={voice.personality?.split(' - ')[0]}
              />
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      {selectedVoice?.personality && (
        <Box sx={{ mt: 1.5, p: 1.5, bgcolor: alpha("#f0f4ff", 0.6), borderRadius: 1.5, border: "1px solid rgba(99, 102, 241, 0.15)" }}>
          <Typography variant="body2" sx={{ color: "#475569", fontSize: "0.8125rem", lineHeight: 1.5 }}>
            <strong style={{ color: "#0f172a" }}>Voice Personality:</strong> {selectedVoice.personality}
          </Typography>
        </Box>
      )}

      {showVoiceClone && !voiceClone?.success && (
        <Box sx={{ mt: 2 }}>
          <Button
            onClick={handleTogglePanel}
            startIcon={showVoiceClonePanel ? <ExpandLess /> : <AutoAwesome />}
            endIcon={showVoiceClonePanel ? <ExpandLess /> : <ExpandMore />}
            sx={{
              py: 1.5,
              px: 2,
              width: "100%",
              background: showVoiceClonePanel 
                ? "linear-gradient(135deg, rgba(102, 126, 234, 0.12) 0%, rgba(118, 75, 162, 0.12) 100%)"
                : "linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%)",
              border: showVoiceClonePanel 
                ? "1px solid rgba(102, 126, 234, 0.3)"
                : "1px dashed rgba(102, 126, 234, 0.4)",
              borderRadius: 2,
              color: "#667eea",
              fontWeight: 600,
              textTransform: "none",
              fontSize: "0.875rem",
              "&:hover": {
                background: "linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%)",
                borderColor: "#667eea",
                boxShadow: "0 2px 8px rgba(102, 126, 234, 0.15)",
              },
            }}
          >
            {showVoiceClonePanel ? "Hide Voice Cloning" : "Create Your Voice Clone"}
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
                  <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1.5 }}>
                    <CheckCircle sx={{ color: "#10b981", fontSize: "1.25rem" }} />
                    <Typography variant="subtitle2" sx={{ color: "#10b981", fontWeight: 700 }}>
                      Voice Clone Created Successfully!
                    </Typography>
                  </Stack>

                  <Typography variant="body2" sx={{ color: "#475569", mb: 1.5, fontSize: "0.875rem" }}>
                    Your custom voice clone is ready. Would you like to use this voice for your podcast?
                  </Typography>

                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={useCreatedVoice}
                        onChange={(e) => setUseCreatedVoice(e.target.checked)}
                        sx={{
                          color: "#10b981",
                          "&.Mui-checked": { color: "#10b981" },
                        }}
                      />
                    }
                    label={
                      <Typography sx={{ color: "#1e293b", fontWeight: 500, fontSize: "0.9375rem" }}>
                        Use this voice for my podcast
                      </Typography>
                    }
                  />

                  <Divider sx={{ my: 2, borderColor: "rgba(0,0,0,0.08)" }} />

                  <Stack direction="row" spacing={1.5} justifyContent="flex-end">
                    <Button
                      onClick={() => {
                        setShowVoiceClonePanel(false);
                        setVoiceCreated(false);
                      }}
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
                        background: useCreatedVoice
                          ? "linear-gradient(135deg, #10b981 0%, #059669 100%)"
                          : "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                        color: "#fff",
                        fontWeight: 600,
                        textTransform: "none",
                        px: 3,
                        boxShadow: useCreatedVoice
                          ? "0 4px 12px rgba(16, 185, 129, 0.3)"
                          : "0 4px 12px rgba(102, 126, 234, 0.3)",
                        "&:hover": {
                          background: useCreatedVoice
                            ? "linear-gradient(135deg, #059669 0%, #047857 100%)"
                            : "linear-gradient(135deg, #764ba2 0%, #667eea 100%)",
                        },
                      }}
                    >
                      {useCreatedVoice ? "Use This Voice" : "Done"}
                    </Button>
                  </Stack>
                </Box>
              )}
            </Box>
          </Collapse>
        </Box>
      )}
    </Box>
  );
};

export default VoiceSelector;