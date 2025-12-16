import React, { useEffect, useState } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stack,
  Box,
  Typography,
  TextField,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Tooltip,
} from "@mui/material";
import { Info as InfoIcon } from "@mui/icons-material";
import { PrimaryButton, SecondaryButton } from "../ui";
import type { VideoGenerationSettings } from "../types";

interface VideoRegenerateModalProps {
  open: boolean;
  onClose: () => void;
  onGenerate: (settings: VideoGenerationSettings) => void;
  initialPrompt: string;
  initialResolution?: "480p" | "720p";
  initialSeed?: number | null;
}

export const VideoRegenerateModal: React.FC<VideoRegenerateModalProps> = ({
  open,
  onClose,
  onGenerate,
  initialPrompt,
  initialResolution = "480p",
  initialSeed = -1,
}) => {
  const [prompt, setPrompt] = useState(initialPrompt);
  const [resolution, setResolution] = useState<"480p" | "720p">(initialResolution);
  const [seed, setSeed] = useState<string>(initialSeed != null && initialSeed !== -1 ? String(initialSeed) : "");
  const [maskImageUrl, setMaskImageUrl] = useState<string>("");

  useEffect(() => {
    setPrompt(initialPrompt);
    setResolution(initialResolution);
  }, [initialResolution, initialPrompt]);

  const handleGenerate = () => {
    const parsedSeed = seed.trim() === "" ? undefined : Number.isNaN(Number(seed)) ? undefined : Number(seed);
    const settings: VideoGenerationSettings = {
      prompt: prompt.trim(),
      resolution,
      seed: parsedSeed,
      maskImageUrl: maskImageUrl.trim() || undefined,
    };
    onGenerate(settings);
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          background: "rgba(15, 23, 42, 0.96)",
          backdropFilter: "blur(18px)",
          borderRadius: 4,
          border: "1px solid rgba(148, 163, 184, 0.4)",
        },
      }}
    >
      <DialogTitle>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Typography variant="h6" sx={{ color: "white", fontWeight: 600 }}>
            Configure Video Generation
          </Typography>
          <Tooltip title="Adjust how your talking-head video is rendered. These settings control resolution, prompt, and animation seed.">
            <InfoIcon sx={{ color: "rgba(148,163,184,0.9)" }} />
          </Tooltip>
        </Stack>
        <Typography variant="body2" sx={{ color: "rgba(148,163,184,0.9)", mt: 1 }}>
          Fine-tune how this scene is animated. InfiniteTalk is audio-driven, so use the prompt to describe the visual
          look and feel you want while keeping it concise.
        </Typography>
      </DialogTitle>

      <DialogContent>
        <Stack spacing={3} sx={{ mt: 1 }}>
          {/* Prompt */}
          <Box>
            <FormLabel sx={{ color: "rgba(248,250,252,0.9)", mb: 0.5 }}>Visual prompt</FormLabel>
            <TextField
              multiline
              minRows={3}
              maxRows={6}
              fullWidth
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Short description of how the scene should look (lighting, mood, camera feel, etc.)"
              variant="outlined"
              InputProps={{
                sx: {
                  bgcolor: "rgba(15,23,42,0.9)",
                  color: "white",
                  "& .MuiOutlinedInput-notchedOutline": {
                    borderColor: "rgba(148,163,184,0.4)",
                  },
                  "&:hover .MuiOutlinedInput-notchedOutline": {
                    borderColor: "rgba(125,211,252,0.8)",
                  },
                },
              }}
              InputLabelProps={{
                sx: { color: "rgba(148,163,184,0.9)" },
              }}
            />
            <Typography variant="caption" sx={{ color: "rgba(148,163,184,0.9)", mt: 0.5, display: "block" }}>
              Example: &quot;Modern podcast studio with soft lighting, the host framed center, gentle camera movement.&quot;
            </Typography>
          </Box>

          {/* Resolution */}
          <Box>
            <FormLabel sx={{ color: "rgba(248,250,252,0.9)", mb: 1 }}>Resolution &amp; quality</FormLabel>
            <RadioGroup
              row
              value={resolution}
              onChange={(e) => setResolution(e.target.value as "480p" | "720p")}
            >
              <FormControlLabel
                value="480p"
                control={<Radio color="primary" />}
                label={
                  <Box>
                    <Typography variant="body2">480p (Recommended)</Typography>
                    <Typography variant="caption" color="text.secondary">
                      Faster render, lower cost, great for previews &amp; social
                    </Typography>
                  </Box>
                }
              />
              <FormControlLabel
                value="720p"
                control={<Radio color="primary" />}
                label={
                  <Box>
                    <Typography variant="body2">720p (Higher quality)</Typography>
                    <Typography variant="caption" color="text.secondary">
                      Sharper video, slightly higher cost and render time
                    </Typography>
                  </Box>
                }
              />
            </RadioGroup>
          </Box>

          {/* Seed & advanced options */}
          <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
            <FormControl fullWidth>
              <FormLabel sx={{ color: "rgba(248,250,252,0.9)", mb: 0.5 }}>Seed (optional)</FormLabel>
              <TextField
                type="number"
                value={seed}
                onChange={(e) => setSeed(e.target.value)}
                placeholder="Random each time if left empty"
                InputProps={{
                  sx: {
                    bgcolor: "rgba(15,23,42,0.9)",
                    color: "white",
                    "& .MuiOutlinedInput-notchedOutline": {
                      borderColor: "rgba(148,163,184,0.4)",
                    },
                    "&:hover .MuiOutlinedInput-notchedOutline": {
                      borderColor: "rgba(125,211,252,0.8)",
                    },
                  },
                }}
              />
              <Typography variant="caption" sx={{ color: "rgba(148,163,184,0.9)", mt: 0.5 }}>
                Use the same seed to get a similar animation style across multiple scenes.
              </Typography>
            </FormControl>

            <FormControl full-width="true">
              <FormLabel sx={{ color: "rgba(248,250,252,0.9)", mb: 0.5 }}>Mask image URL (optional)</FormLabel>
              <TextField
                value={maskImageUrl}
                onChange={(e) => setMaskImageUrl(e.target.value)}
                placeholder="e.g. /api/podcast/images/your_avatar_mask.png"
                InputProps={{
                  sx: {
                    bgcolor: "rgba(15,23,42,0.9)",
                    color: "white",
                    "& .MuiOutlinedInput-notchedOutline": {
                      borderColor: "rgba(148,163,184,0.4)",
                    },
                    "&:hover .MuiOutlinedInput-notchedOutline": {
                      borderColor: "rgba(125,211,252,0.8)",
                    },
                  },
                }}
              />
              <Typography variant="caption" sx={{ color: "rgba(148,163,184,0.9)", mt: 0.5 }}>
                Optional: limit animation to a specific region (e.g. face) by providing a mask image URL. Leave empty to
                animate the whole frame.
              </Typography>
            </FormControl>
          </Stack>
        </Stack>
      </DialogContent>

      <DialogActions sx={{ p: 2.5, pt: 0, justifyContent: "space-between" }}>
        <Typography variant="caption" sx={{ color: "rgba(148,163,184,0.9)" }}>
          Estimated cost at 480p is lower than 720p. You&apos;ll only be billed for successful renders.
        </Typography>
        <Stack direction="row" spacing={1}>
          <SecondaryButton onClick={onClose}>Cancel</SecondaryButton>
          <PrimaryButton onClick={handleGenerate}>Generate Video</PrimaryButton>
        </Stack>
      </DialogActions>
    </Dialog>
  );
}


