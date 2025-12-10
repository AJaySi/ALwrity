import React, { useState, useEffect } from "react";
import { Stack, Box, Typography, TextField, Divider, Button, Alert, alpha, Tooltip, Paper, Chip } from "@mui/material";
import {
  AutoAwesome as AutoAwesomeIcon,
  Refresh as RefreshIcon,
  Info as InfoIcon,
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

export const CreateModal: React.FC<CreateModalProps> = ({ onCreate, open, defaultKnobs, isSubmitting = false }) => {
  const { subscription } = useSubscription();
  const [idea, setIdea] = useState("");
  const [url, setUrl] = useState("");
  const [showAIDetailsButton, setShowAIDetailsButton] = useState(false);
  const [speakers, setSpeakers] = useState<number>(1);
  const [duration, setDuration] = useState<number>(10);
  const [budgetCap, setBudgetCap] = useState<number>(50);
  const [voiceFile, setVoiceFile] = useState<File | null>(null);
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [knobs, setKnobs] = useState<Knobs>({ ...defaultKnobs });

  // Determine subscription tier restrictions
  const tier = subscription?.tier || 'free';
  const isFreeTier = tier === 'free';
  const isBasicTier = tier === 'basic';
  const canUseHD = !isFreeTier && !isBasicTier; // HD only for pro/enterprise
  const canUseMultiSpeaker = !isFreeTier; // Multi-speaker for basic+ tiers

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

  // Show AI details button when user starts typing
  useEffect(() => {
    setShowAIDetailsButton(idea.trim().length > 0);
  }, [idea]);

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
    setDuration(10);
    setBudgetCap(50);
    setVoiceFile(null);
    setAvatarFile(null);
    setKnobs({ ...defaultKnobs });
  };

  return (
    <Paper
      elevation={0}
      sx={{
        borderRadius: 3,
        border: "1px solid rgba(0,0,0,0.08)",
        background: "#ffffff",
        boxShadow: "0 6px 20px rgba(15, 23, 42, 0.08)",
        p: { xs: 3, md: 4 },
      }}
    >
      <Stack spacing={2}>
        <Stack direction="row" spacing={2} alignItems="center" justifyContent="space-between" flexWrap="wrap">
          <Stack direction="row" spacing={2} alignItems="center">
            <AutoAwesomeIcon sx={{ color: "#667eea" }} />
            <Box>
              <Typography variant="h5" sx={{ color: "#0f172a", fontWeight: 800 }}>
                Create New Podcast Episode
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Provide either a topic idea or a blog post URL. We start AI analysis only after you click “Analyze & Continue”.
              </Typography>
            </Box>
          </Stack>
          <Stack direction="row" spacing={1}>
            <Chip label={`Plan: ${subscription?.tier || "free"}`} size="small" color="default" />
            <Chip label={`Duration: ${duration} min`} size="small" color="default" />
            <Chip label={`${speakers} speaker${speakers > 1 ? "s" : ""}`} size="small" color="default" />
          </Stack>
        </Stack>

        <Alert severity="info" sx={{ background: "#eef2ff", border: "1px solid #e0e7ff" }}>
          <Typography variant="body2" sx={{ color: "#4338ca" }}>
            Tips for best results:
          </Typography>
          <Typography variant="body2" sx={{ color: "#4338ca" }}>
            • Provide one clear topic OR a single blog URL (we won’t auto-run anything).<br />
            • Keep it concise—one sentence topic works best.<br />
            • We start analysis only after you confirm, so you stay in control.
          </Typography>
        </Alert>

        <Stack direction={{ xs: "column", md: "row" }} spacing={3} alignItems="stretch">
          {/* Topic Idea Section */}
          <Box flex={1}>
            <Typography variant="subtitle2" sx={{ mb: 1, color: "#0f172a", fontWeight: 700 }}>
              Topic Idea
            </Typography>
            <Tooltip
              title="Enter a concise idea. We will expand it into an outline only after you click Analyze."
              arrow
              placement="top"
            >
              <TextField
                fullWidth
                multiline
                rows={5}
                placeholder="e.g., 'How AI is transforming content marketing in 2024'"
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
                helperText="We will not start analysis until you click Analyze."
                sx={{
                  "& .MuiOutlinedInput-root": {
                    backgroundColor: "#f8fafc",
                    "&:hover": {
                      backgroundColor: "#f1f5f9",
                    },
                  "& .MuiOutlinedInput-input": {
                    fontSize: "0.95rem",
                    lineHeight: 1.5,
                    color: "#0f172a",
                  },
                  },
                  "& .MuiInputBase-input::placeholder": {
                    color: "#94a3b8",
                    opacity: 1,
                  },
                  "& .MuiFormHelperText-root": {
                    color: "#475569",
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
                    borderColor: "#667eea",
                    color: "#667eea",
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
          <Stack alignItems="center" justifyContent="center" sx={{ px: { xs: 0, md: 1 } }}>
            <Divider orientation="vertical" flexItem sx={{ display: { xs: "none", md: "block" }, borderColor: "rgba(0,0,0,0.08)" }} />
            <Divider sx={{ display: { xs: "block", md: "none" }, borderColor: "rgba(0,0,0,0.08)", my: 1 }} />
            <Typography variant="caption" sx={{ color: "#64748b", fontWeight: 700, fontSize: "0.75rem" }}>
              OR
            </Typography>
          </Stack>

          {/* Blog URL Section */}
          <Box flex={1}>
            <Typography variant="subtitle2" sx={{ mb: 1, color: "#0f172a", fontWeight: 700 }}>
              Blog Post URL
            </Typography>
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
                    backgroundColor: "#f8fafc",
                    "&:hover": {
                      backgroundColor: "#f1f5f9",
                    },
                  },
                  "& .MuiInputBase-input::placeholder": {
                    color: "#94a3b8",
                    opacity: 1,
                  },
                  "& .MuiFormHelperText-root": {
                    color: "#475569",
                  },
                }}
              />
            </Tooltip>
          </Box>
        </Stack>

        {/* Quick settings for duration and speakers */}
        <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
          <TextField
            label="Duration (minutes)"
            type="number"
            value={duration}
            onChange={(e) => setDuration(Math.max(1, Number(e.target.value) || 0))}
            InputProps={{ inputProps: { min: 1, max: 60 } }}
            size="small"
            helperText="Typical podcasts: 5-20 minutes"
            sx={{
              maxWidth: 220,
              "& .MuiOutlinedInput-root": {
                backgroundColor: "#f8fafc",
                "&:hover": { backgroundColor: "#f1f5f9" },
              },
            }}
          />
          <TextField
            label="Number of speakers"
            type="number"
            value={speakers}
            onChange={(e) => setSpeakers(Math.min(4, Math.max(1, Number(e.target.value) || 1)))}
            InputProps={{ inputProps: { min: 1, max: 4 } }}
            size="small"
            helperText="Supports single or panel style"
            sx={{
              maxWidth: 220,
              "& .MuiOutlinedInput-root": {
                backgroundColor: "#f8fafc",
                "&:hover": { backgroundColor: "#f1f5f9" },
              },
            }}
          />
        </Stack>

        <Alert severity="info" sx={{ background: "#ecfeff", border: "1px solid #bae6fd", borderRadius: 1 }}>
          <Typography variant="body2" sx={{ fontSize: "0.9rem", color: "#0ea5e9" }}>
            You can provide either a topic idea or a blog post URL. We won’t make any external AI calls until you click “Analyze & Continue”.
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

