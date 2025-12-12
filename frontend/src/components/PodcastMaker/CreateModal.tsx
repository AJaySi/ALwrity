import React, { useState, useEffect, useMemo } from "react";
import { Stack, Box, Typography, TextField, Divider, Button, Alert, alpha, Tooltip, Paper, Chip, IconButton } from "@mui/material";
import {
  AutoAwesome as AutoAwesomeIcon,
  Refresh as RefreshIcon,
  Info as InfoIcon,
  HelpOutline as HelpOutlineIcon,
  AttachMoney as AttachMoneyIcon,
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

  const submit = () => {
    if (!canSubmit || isSubmitting) return;
    onCreate({
      ideaOrUrl: idea || url,
      speakers,
      duration,
      knobs,
      budgetCap,
      files: { voiceFile, avatarFile },
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
            p: 3,
            borderRadius: 2,
            background: alpha("#f8fafc", 0.5),
            border: "1px solid rgba(15, 23, 42, 0.06)",
          }}
        >
          <Typography variant="subtitle2" sx={{ mb: 2, color: "#0f172a", fontWeight: 600, fontSize: "0.9375rem" }}>
            Podcast Settings
          </Typography>
          <Stack direction={{ xs: "column", sm: "row" }} spacing={2} alignItems="flex-start">
            <Stack direction={{ xs: "column", sm: "row" }} spacing={2} sx={{ flex: 1 }}>
            <TextField
              label="Duration (minutes)"
              type="number"
              value={duration}
              onChange={(e) => handleDurationChange(Number(e.target.value) || 1)}
              InputProps={{ inputProps: { min: 1, max: 10 } }}
              size="small"
            helperText={duration > 10 ? "Maximum duration is 10 minutes" : `Recommended: 1-3 minutes for quick tests (currently: ${duration} min)`}
              error={duration > 10}
              sx={{
                maxWidth: 220,
                "& .MuiOutlinedInput-root": {
                  backgroundColor: "#ffffff",
                  border: "1.5px solid rgba(15, 23, 42, 0.12)",
                  borderRadius: 2,
                  "&:hover": { 
                    backgroundColor: "#ffffff",
                    borderColor: "rgba(102, 126, 234, 0.4)",
                  },
                  "&.Mui-focused": {
                    borderColor: "#667eea",
                    borderWidth: 2,
                  },
                },
                "& .MuiInputLabel-root": {
                  color: "#64748b",
                  "&.Mui-focused": {
                    color: "#667eea",
                  },
                },
                "& .MuiFormHelperText-root": {
                  color: "#64748b",
                  fontSize: "0.8125rem",
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
              helperText={speakers > 2 ? "Maximum 2 speakers supported" : `Supports 1-2 speakers (currently: ${speakers})`}
              error={speakers > 2}
              sx={{
                maxWidth: 220,
                "& .MuiOutlinedInput-root": {
                  backgroundColor: "#ffffff",
                  border: "1.5px solid rgba(15, 23, 42, 0.12)",
                  borderRadius: 2,
                  "&:hover": { 
                    backgroundColor: "#ffffff",
                    borderColor: "rgba(102, 126, 234, 0.4)",
                  },
                  "&.Mui-focused": {
                    borderColor: "#667eea",
                    borderWidth: 2,
                  },
                },
                "& .MuiInputLabel-root": {
                  color: "#64748b",
                  "&.Mui-focused": {
                    color: "#667eea",
                  },
                },
                "& .MuiFormHelperText-root": {
                  color: "#64748b",
                  fontSize: "0.8125rem",
                },
              }}
            />
          </Stack>
          
            {/* Cost Breakdown Panel - positioned in empty space */}
            <Paper
              elevation={0}
              sx={{
                p: 2.5,
                background: "linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(5, 150, 105, 0.08) 100%)",
                border: "1.5px solid rgba(16, 185, 129, 0.2)",
                borderRadius: 2,
                minWidth: { xs: "100%", sm: 300 },
                flex: { xs: "none", sm: "0 0 auto" },
                boxShadow: "0 2px 8px rgba(16, 185, 129, 0.08)",
              }}
            >
              <Stack spacing={1.5}>
                <Stack direction="row" spacing={1} alignItems="center">
                  <Box
                    sx={{
                      width: 32,
                      height: 32,
                      borderRadius: 1.5,
                      background: "linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.15) 100%)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                    }}
                  >
                    <AttachMoneyIcon sx={{ fontSize: "1.125rem", color: "#059669" }} />
                  </Box>
                  <Typography variant="subtitle2" sx={{ color: "#0f172a", fontWeight: 600, fontSize: "0.875rem" }}>
                    Estimated Cost
                  </Typography>
                </Stack>
                <Typography 
                  variant="h5" 
                  sx={{ 
                    color: "#059669", 
                    fontWeight: 700,
                    fontSize: "1.75rem",
                    lineHeight: 1.2,
                  }}
                >
                  ${estimatedCost.total}
                </Typography>
                <Stack spacing={0.75} sx={{ mt: 0.5 }}>
                  <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <Typography variant="caption" sx={{ color: "#64748b", fontSize: "0.8125rem", fontWeight: 400 }}>
                      Audio Generation
                    </Typography>
                    <Typography variant="caption" sx={{ color: "#0f172a", fontSize: "0.8125rem", fontWeight: 600 }}>
                      ${estimatedCost.ttsCost}
                    </Typography>
                  </Box>
                  <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <Typography variant="caption" sx={{ color: "#64748b", fontSize: "0.8125rem", fontWeight: 400 }}>
                      Avatar Creation
                    </Typography>
                    <Typography variant="caption" sx={{ color: "#0f172a", fontSize: "0.8125rem", fontWeight: 600 }}>
                      ${estimatedCost.avatarCost}
                    </Typography>
                  </Box>
                  <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <Typography variant="caption" sx={{ color: "#64748b", fontSize: "0.8125rem", fontWeight: 400 }}>
                      Video Rendering
                    </Typography>
                    <Typography variant="caption" sx={{ color: "#0f172a", fontSize: "0.8125rem", fontWeight: 600 }}>
                      ${estimatedCost.videoCost}
                    </Typography>
                  </Box>
                  <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <Typography variant="caption" sx={{ color: "#64748b", fontSize: "0.8125rem", fontWeight: 400 }}>
                      Research
                    </Typography>
                    <Typography variant="caption" sx={{ color: "#0f172a", fontSize: "0.8125rem", fontWeight: 600 }}>
                      ${estimatedCost.researchCost}
                    </Typography>
                  </Box>
                </Stack>
                <Box
                  sx={{
                    mt: 1,
                    pt: 1.5,
                    borderTop: "1.5px solid rgba(16, 185, 129, 0.15)",
                  }}
                >
                  <Typography variant="caption" sx={{ color: "#64748b", fontSize: "0.75rem", fontWeight: 500 }}>
                    {duration} min • {speakers} speaker{speakers > 1 ? "s" : ""} • {knobs.bitrate === "hd" ? "HD" : "Standard"} quality
                  </Typography>
                </Box>
              </Stack>
            </Paper>
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

