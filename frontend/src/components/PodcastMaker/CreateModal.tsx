import React, { useState, useEffect, useMemo } from "react";
import { Stack, Box, Typography, TextField, Divider, Button, Alert, alpha, Tooltip, Paper, Chip, IconButton } from "@mui/material";
import {
  AutoAwesome as AutoAwesomeIcon,
  Refresh as RefreshIcon,
  Info as InfoIcon,
  HelpOutline as HelpOutlineIcon,
  AttachMoney as AttachMoneyIcon,
  CloudUpload as CloudUploadIcon,
  Person as PersonIcon,
  Delete as DeleteIcon,
} from "@mui/icons-material";
import { CreateProjectPayload, Knobs } from "./types";
import { PrimaryButton, SecondaryButton } from "./ui";
import { useSubscription } from "../../contexts/SubscriptionContext";

interface CreateModalProps {
  onCreate: (payload: CreateProjectPayload) => void;
  open: boolean;
  defaultKnobs: Knobs;
  isSubmitting?: boolean;
}

// Rotating placeholder examples for topic ideas
const TOPIC_PLACEHOLDERS = [
  "How AI is transforming content marketing in 2024",
  "The future of remote work: trends and predictions",
  "Sustainable business practices for modern companies",
];

export const CreateModal: React.FC<CreateModalProps> = ({ onCreate, open, defaultKnobs, isSubmitting = false }) => {
  const { subscription } = useSubscription();
  const [idea, setIdea] = useState("");
  const [url, setUrl] = useState("");
  const [showAIDetailsButton, setShowAIDetailsButton] = useState(false);
  const [speakers, setSpeakers] = useState<number>(1);
  const [duration, setDuration] = useState<number>(1);
  const [budgetCap, setBudgetCap] = useState<number>(50);
  const [voiceFile, setVoiceFile] = useState<File | null>(null);
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null);
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null); // Store uploaded avatar URL
  const [makingPresentable, setMakingPresentable] = useState(false);
  const [knobs, setKnobs] = useState<Knobs>({ ...defaultKnobs });
  const [placeholderIndex, setPlaceholderIndex] = useState(0);

  // Determine subscription tier restrictions
  const tier = subscription?.tier || 'free';
  const isFreeTier = tier === 'free';
  const isBasicTier = tier === 'basic';
  const canUseHD = !isFreeTier && !isBasicTier; // HD only for pro/enterprise
  const canUseMultiSpeaker = !isFreeTier; // Multi-speaker for basic+ tiers

  // Rotate placeholder every 3 seconds
  useEffect(() => {
    if (!idea && !url) {
      const interval = setInterval(() => {
        setPlaceholderIndex((prev) => (prev + 1) % TOPIC_PLACEHOLDERS.length);
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [idea, url]);

  // Reset HD quality if user downgrades
  useEffect(() => {
    if (!canUseHD && knobs.bitrate === 'hd') {
      setKnobs({ ...knobs, bitrate: 'standard' });
    }
  }, [canUseHD]);

  // Reset multi-speaker if user downgrades
  useEffect(() => {
    if (!canUseMultiSpeaker && speakers > 1) {
      setSpeakers(1);
    }
  }, [canUseMultiSpeaker]);

  // Ensure duration and speakers are within limits
  useEffect(() => {
    if (duration > 10) {
      setDuration(10);
    }
    if (speakers > 2) {
      setSpeakers(2);
    }
  }, [duration, speakers]);

  // Show AI details button when user starts typing
  useEffect(() => {
    setShowAIDetailsButton(idea.trim().length > 0);
  }, [idea]);

  // Calculate estimated cost
  const estimatedCost = useMemo(() => {
    const chars = Math.max(1000, duration * 900); // ~900 chars per minute
    const scenes = Math.ceil((duration * 60) / (knobs.scene_length_target || 45));
    const secs = duration * 60;
    
    const ttsCost = (chars / 1000) * 0.05;
    const avatarCost = speakers * 0.15;
    const videoRate = knobs.bitrate === 'hd' ? 0.06 : 0.03;
    const videoCost = secs * videoRate;
    const researchCost = 0.3; // Fixed research cost
    
    return {
      ttsCost: +ttsCost.toFixed(2),
      avatarCost: +avatarCost.toFixed(2),
      videoCost: +videoCost.toFixed(2),
      researchCost: +researchCost.toFixed(2),
      total: +(ttsCost + avatarCost + videoCost + researchCost).toFixed(2),
    };
  }, [duration, speakers, knobs.bitrate, knobs.scene_length_target]);

  const canSubmit = Boolean(idea || url);

  const submit = async () => {
    if (!canSubmit || isSubmitting) return;
    
    // If avatar was uploaded but not yet uploaded to server, upload it now
    let finalAvatarUrl: string | null = avatarUrl;
    if (avatarFile && !avatarUrl) {
      try {
        const { podcastApi } = await import("../../services/podcastApi");
        const uploadResult = await podcastApi.uploadAvatar(avatarFile);
        finalAvatarUrl = uploadResult.avatar_url;
      } catch (error) {
        console.error('Avatar upload failed:', error);
        // Continue without avatar
      }
    }
    
    onCreate({
      ideaOrUrl: idea || url,
      speakers,
      duration,
      knobs,
      budgetCap,
      files: { voiceFile, avatarFile },
      avatarUrl: finalAvatarUrl,
    });
  };

  const reset = () => {
    setIdea("");
    setUrl("");
    setSpeakers(1);
    setDuration(1);
    setBudgetCap(50);
    setVoiceFile(null);
    setAvatarFile(null);
    setAvatarPreview(null);
    setAvatarUrl(null);
    setMakingPresentable(false);
    setKnobs({ ...defaultKnobs });
    setPlaceholderIndex(0);
  };

  const handleDurationChange = (value: number) => {
    const clamped = Math.min(10, Math.max(1, value));
    setDuration(clamped);
  };

  const handleSpeakersChange = (value: number) => {
    const clamped = Math.min(2, Math.max(1, value));
    setSpeakers(clamped);
  };

  const handleAvatarChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        console.error('Please select an image file');
        return;
      }
      // Validate file size (e.g., max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        console.error('Image file size must be less than 5MB');
        return;
      }
      setAvatarFile(file);
      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setAvatarPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
      
      // Upload image immediately to get URL (for "Make Presentable" feature)
      try {
        const { podcastApi } = await import("../../services/podcastApi");
        const uploadResult = await podcastApi.uploadAvatar(file);
        setAvatarUrl(uploadResult.avatar_url);
      } catch (error) {
        console.error('Avatar upload failed:', error);
        // Continue with local preview - upload will happen on submit
      }
    }
  };

  const handleRemoveAvatar = () => {
    setAvatarFile(null);
    setAvatarPreview(null);
    setAvatarUrl(null);
    setMakingPresentable(false);
  };

  const handleMakePresentable = async () => {
    if (!avatarUrl || makingPresentable) return;
    
    try {
      setMakingPresentable(true);
      const { podcastApi } = await import("../../services/podcastApi");
      const result = await podcastApi.makeAvatarPresentable(avatarUrl);
      
      // Fetch the transformed image as blob to display
      const { aiApiClient } = await import("../../api/client");
      const response = await aiApiClient.get(result.avatar_url, { responseType: 'blob' });
      const blobUrl = URL.createObjectURL(response.data);
      setAvatarPreview(blobUrl);
      setAvatarUrl(result.avatar_url);
    } catch (error) {
      console.error('Failed to make avatar presentable:', error);
      // Could show error message to user
    } finally {
      setMakingPresentable(false);
    }
  };

  return (
    <Paper
      elevation={0}
      sx={{
        borderRadius: 3,
        border: "1px solid rgba(15, 23, 42, 0.08)",
        background: "#ffffff",
        boxShadow: "0 1px 3px rgba(15, 23, 42, 0.06), 0 8px 24px rgba(15, 23, 42, 0.08)",
        p: { xs: 3, md: 4.5 },
      }}
    >
      <Stack spacing={3.5}>
        {/* Header Section */}
        <Stack direction="row" spacing={2} alignItems="flex-start" justifyContent="space-between" flexWrap="wrap" gap={2}>
          <Stack direction="row" spacing={2} alignItems="flex-start" sx={{ flex: 1, minWidth: { xs: "100%", md: "60%" } }}>
            <Box
              sx={{
                width: 48,
                height: 48,
                borderRadius: 2,
                background: "linear-gradient(135deg, rgba(102, 126, 234, 0.12) 0%, rgba(118, 75, 162, 0.12) 100%)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
              }}
            >
              <AutoAwesomeIcon sx={{ color: "#667eea", fontSize: "1.75rem" }} />
            </Box>
            <Box sx={{ flex: 1 }}>
              <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 0.5 }}>
                <Typography 
                  variant="h5" 
                  sx={{ 
                    color: "#0f172a", 
                    fontWeight: 700,
                    fontSize: { xs: "1.5rem", md: "1.75rem" },
                    letterSpacing: "-0.02em",
                    lineHeight: 1.2,
                  }}
                >
                  Create New Podcast Episode
                </Typography>
                <Tooltip
                  title={
                    <Box>
                      <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                        Tips for best results:
                      </Typography>
                      <Typography variant="body2" component="div" sx={{ fontSize: "0.875rem" }}>
                        • Provide one clear topic OR a single blog URL (we won't auto-run anything).<br />
                        • Keep it concise—one sentence topic works best.<br />
                        • We start analysis only after you confirm, so you stay in control.
                      </Typography>
                    </Box>
                  }
                  arrow
                  placement="top"
                  componentsProps={{
                    tooltip: {
                      sx: {
                        bgcolor: "#0f172a",
                        color: "#ffffff",
                        maxWidth: 300,
                        fontSize: "0.875rem",
                        p: 1.5,
                        boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
                      },
                    },
                    arrow: {
                      sx: {
                        color: "#0f172a",
                      },
                    },
                  }}
                >
                  <IconButton 
                    size="small" 
                    sx={{ 
                      color: "#64748b", 
                      "&:hover": { 
                        color: "#667eea",
                        backgroundColor: alpha("#667eea", 0.08),
                      } 
                    }}
                  >
                    <HelpOutlineIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Stack>
            </Box>
          </Stack>
          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap sx={{ alignItems: "center" }}>
            <Tooltip
              title={`Your current subscription plan: ${subscription?.tier || "free"}. Upgrade for more features.`}
              arrow
              placement="top"
            >
              <Chip 
                label={`Plan: ${subscription?.tier || "free"}`} 
                size="small" 
                sx={{
                  background: "linear-gradient(135deg, rgba(102, 126, 234, 0.12) 0%, rgba(118, 75, 162, 0.12) 100%)",
                  color: "#667eea",
                  fontWeight: 600,
                  border: "1px solid rgba(102, 126, 234, 0.2)",
                  fontSize: "0.75rem",
                  height: 26,
                  cursor: "help",
                }}
              />
            </Tooltip>
            <Tooltip
              title={`Podcast duration: ${duration} minutes. Maximum duration is 10 minutes. Recommended: 5-10 minutes for best results.`}
              arrow
              placement="top"
            >
              <Chip 
                label={`Duration: ${duration} min`} 
                size="small"
                sx={{
                  background: alpha("#0f172a", 0.06),
                  color: "#0f172a",
                  fontWeight: 600,
                  border: "1px solid rgba(15, 23, 42, 0.12)",
                  fontSize: "0.75rem",
                  height: 26,
                  cursor: "help",
                }}
              />
            </Tooltip>
            <Tooltip
              title={`Number of speakers: ${speakers}. Supports 1-2 speakers. Each additional speaker adds avatar generation cost.`}
              arrow
              placement="top"
            >
              <Chip 
                label={`${speakers} speaker${speakers > 1 ? "s" : ""}`} 
                size="small"
                sx={{
                  background: alpha("#0f172a", 0.06),
                  color: "#0f172a",
                  fontWeight: 600,
                  border: "1px solid rgba(15, 23, 42, 0.12)",
                  fontSize: "0.75rem",
                  height: 26,
                  cursor: "help",
                }}
              />
            </Tooltip>
            <Tooltip
              title={
                <Box>
                  <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                    Estimated Cost Breakdown:
                  </Typography>
                  <Typography variant="body2" component="div" sx={{ fontSize: "0.875rem", lineHeight: 1.6 }}>
                    • Audio Generation: ${estimatedCost.ttsCost}<br />
                    • Avatar Creation: ${estimatedCost.avatarCost}<br />
                    • Video Rendering: ${estimatedCost.videoCost}<br />
                    • Research: ${estimatedCost.researchCost}<br />
                    <Typography variant="body2" sx={{ fontWeight: 600, mt: 0.5, pt: 0.5, borderTop: "1px solid rgba(255,255,255,0.2)" }}>
                      Total: ${estimatedCost.total}
                    </Typography>
                    <Typography variant="caption" sx={{ fontSize: "0.75rem", opacity: 0.9, mt: 0.5, display: "block" }}>
                      Based on {duration} min, {speakers} speaker{speakers > 1 ? "s" : ""}, {knobs.bitrate === "hd" ? "HD" : "standard"} quality
                    </Typography>
                  </Typography>
                </Box>
              }
              arrow
              placement="top"
              componentsProps={{
                tooltip: {
                  sx: {
                    bgcolor: "#0f172a",
                    color: "#ffffff",
                    maxWidth: 280,
                    fontSize: "0.875rem",
                    p: 1.5,
                    boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
                  },
                },
                arrow: {
                  sx: {
                    color: "#0f172a",
                  },
                },
              }}
            >
              <Chip 
                icon={<AttachMoneyIcon sx={{ fontSize: "0.875rem !important" }} />}
                label={`Est. $${estimatedCost.total}`} 
                size="small"
                sx={{
                  background: "linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(5, 150, 105, 0.12) 100%)",
                  color: "#059669",
                  fontWeight: 600,
                  border: "1px solid rgba(16, 185, 129, 0.2)",
                  fontSize: "0.75rem",
                  height: 26,
                  cursor: "help",
                }}
              />
            </Tooltip>
          </Stack>
        </Stack>


        {/* Input Section */}
        <Box
          sx={{
            p: 3,
            borderRadius: 2,
            background: alpha("#f8fafc", 0.5),
            border: "1px solid rgba(15, 23, 42, 0.06)",
          }}
        >
          <Stack direction={{ xs: "column", md: "row" }} spacing={3} alignItems="stretch">
            {/* Topic Idea Section */}
            <Box flex={1}>
              <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1.5 }}>
                <Typography variant="subtitle2" sx={{ color: "#0f172a", fontWeight: 600, fontSize: "0.9375rem" }}>
                  Topic Idea
                </Typography>
              </Stack>
            <Tooltip
              title="Enter a concise idea. We will expand it into an outline only after you click Analyze."
              arrow
              placement="top"
            >
              <TextField
                fullWidth
                multiline
                rows={5}
                placeholder={!idea && !url ? `e.g., "${TOPIC_PLACEHOLDERS[placeholderIndex]}"` : ""}
                inputProps={{
                  sx: {
                    "&::placeholder": { color: "#94a3b8", opacity: 1 },
                    color: "#0f172a",
                  },
                }}
                value={idea}
                onChange={(e) => {
                  setIdea(e.target.value);
                  // Clear URL when typing idea
                  if (e.target.value.trim().length > 0) {
                    setUrl("");
                  }
                }}
                size="small"
                helperText="Enter a clear, concise topic. We'll expand it into a full script after you click Analyze."
                sx={{
                  "& .MuiOutlinedInput-root": {
                    backgroundColor: "#ffffff",
                    border: "1.5px solid rgba(15, 23, 42, 0.12)",
                    borderRadius: 2,
                    "&:hover": {
                      backgroundColor: "#ffffff",
                      borderColor: "rgba(102, 126, 234, 0.4)",
                    },
                    "&.Mui-focused": {
                      backgroundColor: "#ffffff",
                      borderColor: "#667eea",
                      borderWidth: 2,
                    },
                  "& .MuiOutlinedInput-input": {
                    fontSize: "0.9375rem",
                    lineHeight: 1.6,
                    color: "#0f172a",
                    fontWeight: 400,
                  },
                  },
                  "& .MuiInputBase-input::placeholder": {
                    color: "#94a3b8",
                    opacity: 1,
                    fontWeight: 400,
                  },
                  "& .MuiFormHelperText-root": {
                    color: "#64748b",
                    fontSize: "0.8125rem",
                    fontWeight: 400,
                    mt: 0.75,
                  },
                }}
              />
            </Tooltip>
            {/* Add details with AI button - appears when user types */}
            {showAIDetailsButton && (
              <Box sx={{ display: "flex", justifyContent: "flex-end", mt: 1 }}>
                <Button
                  size="small"
                  variant="outlined"
                  startIcon={<AutoAwesomeIcon />}
                  onClick={() => {
                    // TODO: Implement AI details functionality
                    console.log("Add details with AI clicked");
                  }}
                  sx={{
                    textTransform: "none",
                    fontSize: "0.875rem",
                    fontWeight: 600,
                    borderColor: "#667eea",
                    borderWidth: 1.5,
                    color: "#667eea",
                    borderRadius: 2,
                    "&:hover": {
                      borderColor: "#5568d3",
                      backgroundColor: alpha("#667eea", 0.08),
                    },
                  }}
                >
                  Add details with AI
                </Button>
              </Box>
            )}
          </Box>

            {/* Center OR divider */}
            <Stack alignItems="center" justifyContent="center" sx={{ px: { xs: 0, md: 2 } }}>
              <Divider 
                orientation="vertical" 
                flexItem 
                sx={{ 
                  display: { xs: "none", md: "block" }, 
                  borderColor: "rgba(15, 23, 42, 0.1)",
                  borderWidth: 1,
                }} 
              />
              <Box
                sx={{
                  display: { xs: "flex", md: "none" },
                  alignItems: "center",
                  width: "100%",
                  my: 2,
                }}
              >
                <Divider sx={{ flex: 1, borderColor: "rgba(15, 23, 42, 0.1)" }} />
                <Box
                  sx={{
                    px: 2,
                    py: 0.5,
                    borderRadius: 2,
                    background: alpha("#ffffff", 0.8),
                    border: "1px solid rgba(15, 23, 42, 0.1)",
                  }}
                >
                  <Typography variant="caption" sx={{ color: "#64748b", fontWeight: 700, fontSize: "0.75rem" }}>
                    OR
                  </Typography>
                </Box>
                <Divider sx={{ flex: 1, borderColor: "rgba(15, 23, 42, 0.1)" }} />
              </Box>
              <Box
                sx={{
                  display: { xs: "none", md: "flex" },
                  alignItems: "center",
                  justifyContent: "center",
                  width: 40,
                  height: 40,
                  borderRadius: "50%",
                  background: alpha("#ffffff", 0.9),
                  border: "1px solid rgba(15, 23, 42, 0.1)",
                  boxShadow: "0 1px 2px rgba(0,0,0,0.05)",
                }}
              >
                <Typography variant="caption" sx={{ color: "#64748b", fontWeight: 700, fontSize: "0.75rem" }}>
                  OR
                </Typography>
              </Box>
            </Stack>

            {/* Blog URL Section */}
            <Box flex={1}>
              <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1.5 }}>
                <Typography variant="subtitle2" sx={{ color: "#0f172a", fontWeight: 600, fontSize: "0.9375rem" }}>
                  Blog Post URL
                </Typography>
              </Stack>
            <Tooltip
              title="Paste a single article URL. We’ll fetch insights only after you click Analyze."
              arrow
              placement="top"
            >
              <TextField
                fullWidth
                label="Paste blog post URL"
                placeholder="https://yourblog.com/article"
              inputProps={{
                sx: {
                  "&::placeholder": { color: "#94a3b8", opacity: 1 },
                  color: "#0f172a",
                },
              }}
                value={url}
                onChange={(e) => {
                  setUrl(e.target.value);
                  // Clear idea when entering URL
                  if (e.target.value.trim().length > 0) {
                    setIdea("");
                    setShowAIDetailsButton(false);
                  }
                }}
                size="small"
                helperText="We won’t trigger analysis until you confirm."
                InputProps={{
                  endAdornment: (
                    <Tooltip title="One URL is enough—keep it focused to reduce retries." arrow>
                      <InfoIcon sx={{ color: "action.disabled", fontSize: 18, ml: 1 }} />
                    </Tooltip>
                  ),
                }}
                sx={{
                  "& .MuiOutlinedInput-root": {
                    backgroundColor: "#ffffff",
                    border: "1.5px solid rgba(15, 23, 42, 0.12)",
                    borderRadius: 2,
                    "&:hover": {
                      backgroundColor: "#ffffff",
                      borderColor: "rgba(102, 126, 234, 0.4)",
                    },
                    "&.Mui-focused": {
                      backgroundColor: "#ffffff",
                      borderColor: "#667eea",
                      borderWidth: 2,
                    },
                  },
                  "& .MuiInputBase-input": {
                    color: "#0f172a",
                    fontSize: "0.9375rem",
                    fontWeight: 400,
                  },
                  "& .MuiInputLabel-root": {
                    color: "#64748b",
                    fontSize: "0.9375rem",
                    "&.Mui-focused": {
                      color: "#667eea",
                    },
                  },
                  "& .MuiInputBase-input::placeholder": {
                    color: "#94a3b8",
                    opacity: 1,
                    fontWeight: 400,
                  },
                  "& .MuiFormHelperText-root": {
                    color: "#64748b",
                    fontSize: "0.8125rem",
                    fontWeight: 400,
                    mt: 0.75,
                  },
                }}
              />
            </Tooltip>
          </Box>
          </Stack>
        </Box>

        {/* Settings Section */}
        <Box
          sx={{
            p: 3.5,
            borderRadius: 2.5,
            background: "linear-gradient(135deg, rgba(248, 250, 252, 0.8) 0%, rgba(241, 245, 249, 0.8) 100%)",
            border: "1.5px solid rgba(15, 23, 42, 0.08)",
            boxShadow: "0 1px 3px rgba(15, 23, 42, 0.04), 0 4px 12px rgba(15, 23, 42, 0.06)",
          }}
        >
          <Stack direction="row" spacing={1.5} alignItems="center" sx={{ mb: 3 }}>
            <Box
              sx={{
                width: 40,
                height: 40,
                borderRadius: 2,
                background: "linear-gradient(135deg, rgba(102, 126, 234, 0.12) 0%, rgba(118, 75, 162, 0.12) 100%)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <AutoAwesomeIcon sx={{ color: "#667eea", fontSize: "1.25rem" }} />
            </Box>
            <Typography variant="h6" sx={{ color: "#0f172a", fontWeight: 700, fontSize: "1.125rem", letterSpacing: "-0.01em" }}>
              Podcast Settings
            </Typography>
          </Stack>
          
          <Stack direction={{ xs: "column", lg: "row" }} spacing={3} alignItems="flex-start">
            {/* Duration and Speakers in vertical column */}
            <Box
              sx={{
                flex: { xs: "1 1 auto", lg: "0 0 280px" },
                width: { xs: "100%", lg: "280px" },
                p: 2.5,
                borderRadius: 2,
                background: "#ffffff",
                border: "1px solid rgba(15, 23, 42, 0.08)",
                boxShadow: "0 1px 2px rgba(15, 23, 42, 0.04)",
              }}
            >
              <Typography variant="subtitle2" sx={{ mb: 2, color: "#0f172a", fontWeight: 600, fontSize: "0.875rem" }}>
                Basic Configuration
              </Typography>
              <Stack spacing={2.5}>
                <TextField
                  label="Duration (minutes)"
                  type="number"
                  value={duration}
                  onChange={(e) => handleDurationChange(Number(e.target.value) || 1)}
                  InputProps={{ inputProps: { min: 1, max: 10 } }}
                  size="small"
                  helperText={duration > 10 ? "Maximum duration is 10 minutes" : `Recommended: 1-3 minutes for quick tests`}
                  error={duration > 10}
                  fullWidth
                  sx={{
                    "& .MuiOutlinedInput-root": {
                      backgroundColor: "#f8fafc",
                      border: "1.5px solid rgba(15, 23, 42, 0.12)",
                      borderRadius: 2,
                      transition: "all 0.2s",
                      "&:hover": { 
                        backgroundColor: "#ffffff",
                        borderColor: "rgba(102, 126, 234, 0.4)",
                        boxShadow: "0 0 0 3px rgba(102, 126, 234, 0.08)",
                      },
                      "&.Mui-focused": {
                        backgroundColor: "#ffffff",
                        borderColor: "#667eea",
                        borderWidth: 2,
                        boxShadow: "0 0 0 3px rgba(102, 126, 234, 0.12)",
                      },
                    },
                    "& .MuiInputLabel-root": {
                      color: "#64748b",
                      fontWeight: 500,
                      "&.Mui-focused": {
                        color: "#667eea",
                        fontWeight: 600,
                      },
                    },
                    "& .MuiFormHelperText-root": {
                      color: duration > 10 ? "#dc2626" : "#64748b",
                      fontSize: "0.8125rem",
                      mt: 0.75,
                    },
                  }}
                />
                <TextField
                  label="Number of speakers"
                  type="number"
                  value={speakers}
                  onChange={(e) => handleSpeakersChange(Number(e.target.value) || 1)}
                  InputProps={{ inputProps: { min: 1, max: 2 } }}
                  size="small"
                  helperText={speakers > 2 ? "Maximum 2 speakers supported" : `Supports 1-2 speakers`}
                  error={speakers > 2}
                  fullWidth
                  sx={{
                    "& .MuiOutlinedInput-root": {
                      backgroundColor: "#f8fafc",
                      border: "1.5px solid rgba(15, 23, 42, 0.12)",
                      borderRadius: 2,
                      transition: "all 0.2s",
                      "&:hover": { 
                        backgroundColor: "#ffffff",
                        borderColor: "rgba(102, 126, 234, 0.4)",
                        boxShadow: "0 0 0 3px rgba(102, 126, 234, 0.08)",
                      },
                      "&.Mui-focused": {
                        backgroundColor: "#ffffff",
                        borderColor: "#667eea",
                        borderWidth: 2,
                        boxShadow: "0 0 0 3px rgba(102, 126, 234, 0.12)",
                      },
                    },
                    "& .MuiInputLabel-root": {
                      color: "#64748b",
                      fontWeight: 500,
                      "&.Mui-focused": {
                        color: "#667eea",
                        fontWeight: 600,
                      },
                    },
                    "& .MuiFormHelperText-root": {
                      color: speakers > 2 ? "#dc2626" : "#64748b",
                      fontSize: "0.8125rem",
                      mt: 0.75,
                    },
                  }}
                />
              </Stack>
            </Box>
            
            {/* Avatar Upload Section - replacing Estimated Cost */}
            <Box
              sx={{
                flex: 1,
                minWidth: 0,
                p: 2.5,
                borderRadius: 2,
                background: "#ffffff",
                border: "1px solid rgba(15, 23, 42, 0.08)",
                boxShadow: "0 1px 2px rgba(15, 23, 42, 0.04)",
              }}
            >
              <Stack direction="row" spacing={1.5} alignItems="center" sx={{ mb: 2.5 }}>
                <Box
                  sx={{
                    width: 36,
                    height: 36,
                    borderRadius: 1.5,
                    background: "linear-gradient(135deg, rgba(102, 126, 234, 0.12) 0%, rgba(118, 75, 162, 0.12) 100%)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  <PersonIcon fontSize="small" sx={{ color: "#667eea" }} />
                </Box>
                <Typography variant="subtitle2" sx={{ color: "#0f172a", fontWeight: 600, fontSize: "0.9375rem" }}>
                  Podcast Presenter Avatar
                </Typography>
                <Tooltip
                  title={
                    <Box>
                      <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                        Avatar Options:
                      </Typography>
                      <Typography variant="body2" component="div" sx={{ fontSize: "0.875rem", lineHeight: 1.6 }}>
                        <strong>Upload your photo:</strong> We'll enhance it into a professional podcast presenter using AI. Click "Make Presentable" after upload.<br/><br/>
                        <strong>Skip upload:</strong> After analysis completes, we'll generate professional presenter images based on your podcast topic, audience, and speaker count.
                      </Typography>
                    </Box>
                  }
                  arrow
                  placement="top"
                  componentsProps={{
                    tooltip: {
                      sx: {
                        bgcolor: "#0f172a",
                        color: "#ffffff",
                        maxWidth: 320,
                        fontSize: "0.875rem",
                        p: 1.5,
                        boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
                      },
                    },
                    arrow: {
                      sx: {
                        color: "#0f172a",
                      },
                    },
                  }}
                >
                  <InfoIcon fontSize="small" sx={{ color: "#94a3b8", cursor: "help" }} />
                </Tooltip>
              </Stack>
              
              <Stack direction={{ xs: "column", sm: "row" }} spacing={2.5} alignItems="flex-start">
                {avatarPreview ? (
                  <Stack spacing={1.5} sx={{ flexShrink: 0 }}>
                    <Box sx={{ position: "relative", display: "inline-block" }}>
                      <Box
                        component="img"
                        src={avatarPreview}
                        alt="Avatar preview"
                        sx={{
                          width: 140,
                          height: 140,
                          objectFit: "cover",
                          borderRadius: 2.5,
                          border: "2px solid #e2e8f0",
                          boxShadow: "0 2px 8px rgba(15, 23, 42, 0.08)",
                        }}
                      />
                      <IconButton
                        size="small"
                        onClick={handleRemoveAvatar}
                        sx={{
                          position: "absolute",
                          top: -8,
                          right: -8,
                          bgcolor: "white",
                          border: "1.5px solid #e2e8f0",
                          boxShadow: "0 2px 4px rgba(15, 23, 42, 0.1)",
                          "&:hover": { 
                            bgcolor: "#f8fafc",
                            borderColor: "#dc2626",
                            color: "#dc2626",
                          },
                        }}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Box>
                    {avatarUrl && (
                      <Tooltip
                        title="Transform your uploaded photo into a professional podcast presenter. This AI enhancement optimizes your photo for video generation while maintaining your appearance and identity."
                        arrow
                        placement="top"
                      >
                        <Box>
                          <SecondaryButton
                            onClick={handleMakePresentable}
                            disabled={makingPresentable}
                            loading={makingPresentable}
                            startIcon={!makingPresentable ? <AutoAwesomeIcon fontSize="small" /> : undefined}
                            sx={{
                              fontSize: "0.8125rem",
                              py: 0.75,
                              width: "100%",
                              background: makingPresentable ? undefined : "linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%)",
                              border: makingPresentable ? undefined : "1px solid rgba(102, 126, 234, 0.2)",
                              color: makingPresentable ? undefined : "#667eea",
                              fontWeight: 600,
                              "&:hover": {
                                background: makingPresentable ? undefined : "linear-gradient(135deg, rgba(102, 126, 234, 0.12) 0%, rgba(118, 75, 162, 0.12) 100%)",
                              },
                            }}
                          >
                            {makingPresentable ? "Transforming..." : "Make Presentable"}
                          </SecondaryButton>
                        </Box>
                      </Tooltip>
                    )}
                  </Stack>
                ) : (
                  <Box
                    component="label"
                    sx={{
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "center",
                      justifyContent: "center",
                      width: { xs: "100%", sm: 200 },
                      minHeight: 140,
                      border: "2px dashed #cbd5e1",
                      borderRadius: 2.5,
                      bgcolor: "#f8fafc",
                      cursor: "pointer",
                      transition: "all 0.2s",
                      flexShrink: 0,
                      "&:hover": {
                        borderColor: "#667eea",
                        bgcolor: "#f1f5f9",
                        borderWidth: "2.5px",
                        boxShadow: "0 0 0 3px rgba(102, 126, 234, 0.08)",
                      },
                    }}
                  >
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleAvatarChange}
                      style={{ display: "none" }}
                    />
                    <CloudUploadIcon sx={{ color: "#94a3b8", fontSize: 36, mb: 1.5 }} />
                    <Typography variant="body2" sx={{ color: "#64748b", fontWeight: 600, mb: 0.5 }}>
                      Upload Your Photo
                    </Typography>
                    <Typography variant="caption" sx={{ color: "#94a3b8", textAlign: "center", px: 2, lineHeight: 1.5 }}>
                      Optional - We'll enhance it with AI or generate one after analysis
                    </Typography>
                  </Box>
                )}
                
                <Box sx={{ flex: 1, minWidth: 0 }}>
                  <Stack spacing={1.5}>
                    <Box>
                      <Typography variant="body2" sx={{ color: "#0f172a", fontSize: "0.9375rem", lineHeight: 1.7, fontWeight: 500, mb: 1 }}>
                        Choose Your Avatar Option:
                      </Typography>
                      
                      <Stack spacing={1.5}>
                        <Box
                          sx={{
                            p: 1.5,
                            borderRadius: 1.5,
                            background: alpha("#f0f4ff", 0.6),
                            border: "1px solid rgba(99, 102, 241, 0.2)",
                          }}
                        >
                          <Typography variant="body2" sx={{ color: "#0f172a", fontSize: "0.875rem", fontWeight: 600, mb: 0.5, display: "flex", alignItems: "center", gap: 0.5 }}>
                            <AutoAwesomeIcon fontSize="small" sx={{ color: "#667eea" }} />
                            Upload Your Photo (Recommended)
                          </Typography>
                          <Typography variant="body2" sx={{ color: "#475569", fontSize: "0.8125rem", lineHeight: 1.6 }}>
                            Upload your photo and we'll enhance it into a professional podcast presenter using AI. After upload, click <strong>"Make Presentable"</strong> to transform your photo into a podcast-ready avatar that maintains your appearance while optimizing it for video generation.
                          </Typography>
                        </Box>
                        
                        <Box
                          sx={{
                            p: 1.5,
                            borderRadius: 1.5,
                            background: alpha("#f8fafc", 0.8),
                            border: "1px solid rgba(15, 23, 42, 0.1)",
                          }}
                        >
                          <Typography variant="body2" sx={{ color: "#0f172a", fontSize: "0.875rem", fontWeight: 600, mb: 0.5, display: "flex", alignItems: "center", gap: 0.5 }}>
                            <PersonIcon fontSize="small" sx={{ color: "#64748b" }} />
                            Let ALwrity Generate (Alternative)
                          </Typography>
                          <Typography variant="body2" sx={{ color: "#475569", fontSize: "0.8125rem", lineHeight: 1.6 }}>
                            If you skip upload, we'll automatically generate professional presenter images <strong>after the AI analysis completes</strong>. The generated presenters will be tailored to your podcast topic, target audience, content type, and speaker count for the best fit.
                          </Typography>
                        </Box>
                      </Stack>
                    </Box>
                    
                    <Box
                      sx={{
                        p: 1.5,
                        borderRadius: 1.5,
                        background: alpha("#f0f4ff", 0.5),
                        border: "1px solid rgba(99, 102, 241, 0.15)",
                      }}
                    >
                      <Typography variant="caption" sx={{ color: "#6366f1", fontSize: "0.8125rem", fontWeight: 500, display: "flex", alignItems: "center", gap: 0.5 }}>
                        <InfoIcon fontSize="inherit" />
                        Supported formats: JPG, PNG, WebP (max 5MB)
                      </Typography>
                    </Box>
                  </Stack>
                </Box>
              </Stack>
            </Box>
          </Stack>
        </Box>

        {/* Info Banner */}
        <Alert 
          severity="info" 
          icon={<InfoIcon sx={{ color: "#6366f1", fontSize: "1.125rem" }} />}
          sx={{ 
            background: alpha("#f0f4ff", 0.6),
            border: "1px solid rgba(99, 102, 241, 0.15)",
            borderRadius: 2,
            boxShadow: "0 1px 3px rgba(99, 102, 241, 0.08)",
            "& .MuiAlert-message": {
              width: "100%",
            },
          }}
        >
          <Typography variant="body2" sx={{ fontSize: "0.875rem", color: "#475569", lineHeight: 1.6, fontWeight: 400 }}>
            You can provide either a topic idea or a blog post URL. We won't make any external AI calls until you click "Analyze & Continue".
          </Typography>
        </Alert>

        <Stack direction="row" justifyContent="flex-end" spacing={1}>
          <SecondaryButton onClick={reset} startIcon={<RefreshIcon />}>
            Reset
          </SecondaryButton>
          <PrimaryButton
            onClick={submit}
            disabled={!canSubmit || isSubmitting}
            loading={isSubmitting}
            startIcon={<AutoAwesomeIcon />}
            tooltip={!canSubmit ? "Enter an idea or URL to continue" : "We’ll start AI analysis after this click"}
          >
            {isSubmitting ? "Analyzing..." : "Analyze & Continue"}
          </PrimaryButton>
        </Stack>
      </Stack>
    </Paper>
  );
};

